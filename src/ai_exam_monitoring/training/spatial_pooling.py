"""Continuous area-weighted token pooling over reviewed letterbox rectangles."""

from __future__ import annotations

import torch

from ai_exam_monitoring.common.errors import DataContractError
from ai_exam_monitoring.data.pilot_schema import PixelBox


def letterbox_regions(
    person: PixelBox, context: PixelBox, image_size: tuple[int, int], size: int,
) -> torch.Tensor:
    """Content/person XYXY in actual rounded letterbox pixels, before any flip.

    Imported crop dimensions can differ from native context dimensions. Map the
    accepted person rectangle proportionally through the full crop, without
    rounding its continuous coordinates or inventing additional padding.
    """
    if min(*image_size, size) <= 0 or not context.contains(person):
        raise DataContractError("Invalid spatial crop geometry")
    scale = size / max(image_size)
    w, h = (max(1, min(size, round(v * scale))) for v in image_size)
    left, top = (size - w) // 2, (size - h) // 2
    sx, sy = w / (context.xmax-context.xmin), h / (context.ymax-context.ymin)
    return torch.tensor([
        [left, top, left+w, top+h],
        [left+(person.xmin-context.xmin)*sx, top+(person.ymin-context.ymin)*sy,
         left+(person.xmax-context.xmin)*sx, top+(person.ymax-context.ymin)*sy],
    ], dtype=torch.float32)


def mirror_regions(boxes: torch.Tensor, size: int) -> torch.Tensor:
    result = boxes.clone()
    result[..., 0], result[..., 2] = size-boxes[..., 2], size-boxes[..., 0]
    return result


def spatial_features(
    tokens: torch.Tensor, boxes: torch.Tensor, *, image_size: int, patch_size: int = 14,
) -> torch.Tensor:
    """CLS followed by TL, TR, BL, BR area-weighted patch means; never fallback."""
    grid = image_size // patch_size
    if (image_size % patch_size or tokens.ndim != 3
            or tokens.shape[1] != 1 + grid * grid
            or boxes.shape != (tokens.shape[0], 4)):
        raise DataContractError("Spatial token grid/rectangle shape mismatch")
    boxes = boxes.to(device=tokens.device, dtype=tokens.dtype)
    if (not torch.isfinite(boxes).all() or not torch.isfinite(tokens).all()
            or (boxes < 0).any() or (boxes > image_size).any()
            or (boxes[:, 2:] <= boxes[:, :2]).any()):
        raise DataContractError("Invalid/nonfinite spatial tokens or rectangle")
    lo, hi = boxes[:, :2], boxes[:, 2:]
    mid = (lo+hi)/2
    x1, y1 = lo.unbind(1)
    x2, y2 = hi.unbind(1)
    xm, ym = mid.unbind(1)
    bins = torch.stack([
        torch.stack([x1,y1,xm,ym],1), torch.stack([xm,y1,x2,ym],1),
        torch.stack([x1,ym,xm,y2],1), torch.stack([xm,ym,x2,y2],1),
    ],1)
    edge = torch.arange(grid, device=tokens.device, dtype=tokens.dtype)*patch_size
    xs, ys = edge.repeat(grid), edge.repeat_interleave(grid)
    dx = (torch.minimum(xs+patch_size, bins[..., 2,None])
          - torch.maximum(xs, bins[..., 0,None])).clamp_min(0)
    dy = (torch.minimum(ys+patch_size, bins[..., 3,None])
          - torch.maximum(ys, bins[..., 1,None])).clamp_min(0)
    area = dx*dy
    total = area.sum(-1, keepdim=True)
    if not torch.isfinite(total).all() or (total <= 0).any():
        raise DataContractError("Empty/nonfinite spatial bin")
    means = torch.bmm(area/total, tokens[:, 1:])
    return torch.cat([tokens[:, 0], means.flatten(1)],1)
