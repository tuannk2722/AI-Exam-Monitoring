"""Manual study observations; ranges compress notes, not automated label inference."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
notes = {}


def put(ids, labels, reason):
    for i in ids:
        notes[f"CB-{i:04}"] = {"draft_labels": labels, "reason": reason}


def span(a, b, labels, reason):
    put(range(a, b + 1), labels, reason)


span(
    1,
    25,
    "U/N",
    (
        "Anchor nữ đeo kính hàng sau; vật cầm nhỏ, không đồng nhất calculator với "
        "phone. Hướng đầu về vùng bài riêng."
    ),
)
put(
    [2, 3, 8, 9, 10, 11, 12, 15, 16],
    "P/N",
    (
        "Thấy thiết bị đen dạng mobile của anchor; hướng đầu về vùng bài riêng, "
        "không lấy calculator trắng làm phone."
    ),
)
put([6, 17], "U/P", "Đầu quay sang người/vùng bên cạnh; thiết bị chưa đủ rõ để kết luận phone.")
span(
    18,
    25,
    "U/U",
    "Khung cố định lệch so với nữ đeo kính bên phải; cần crop mới để tách khỏi nữ bên trái.",
)
span(
    26,
    62,
    "N/N",
    (
        "Calculator có bàn phím; quan sát bàn và tư thế hướng bài riêng. Không lấy "
        "người hàng sau làm anchor."
    ),
)
put(
    [30, 55],
    "N/U",
    (
        "Crop cắt phần đầu khi anchor ngồi thẳng/đứng; không chuyển nhãn hướng nhìn "
        "từ frame rộng sang crop mất bằng chứng."
    ),
)
span(
    63,
    87,
    "P/N",
    "Mobile trên bàn riêng; calculator là vật khác. Đầu cúi về bài riêng đủ diễn giải dù mắt nhỏ.",
)
put(
    [68, 69, 70, 74, 75, 76, 78, 79, 80, 82],
    "P/P",
    "Ngoại lệ trong nhóm P/N: đầu quay rõ ra bên trái, ngoài vùng bài riêng; mobile trên bàn.",
)
put(
    [65, 66, 81, 87],
    "P/U",
    (
        "Mobile trên bàn; mặt/tay che hoặc tư thế nghiêng khiến vùng nhìn chưa chắc,"
        " không suy từ tư thế đơn lẻ."
    ),
)
span(
    88,
    105,
    "U/N",
    (
        "Nữ áo trắng hàng giữa bên trái nhìn bài; cần phân biệt calculator màu hồng "
        "với mobile, bàn bị người trước che một phần."
    ),
)
put(
    [98, 102, 103, 104, 105],
    "P/N",
    "Mobile trên vùng bàn của anchor, calculator riêng; đầu hướng bài.",
)
put(
    [90, 97],
    "U/U",
    "Thiết bị và hướng nhìn chưa đủ rõ tại kích thước crop, không nội suy từ frame lân cận.",
)
put(
    [100, 101],
    "U/P",
    "Đầu quay rõ sang bên; tay che không xóa bằng chứng hướng đầu. Vùng thiết bị bị che.",
)
span(
    106,
    112,
    "U/U",
    (
        "Anchor nữ hàng giữa đã dịch sang phải ngoài tâm crop; cần recrop, không gán"
        " nhãn của người áo xanh/nam ngồi trái."
    ),
)
span(
    113,
    149,
    "P/N",
    (
        "Mobile đặt trên bàn riêng; vật trắng cầm tay là calculator. Đầu nhìn bài "
        "riêng, kể cả khi đứng cúi làm bài."
    ),
)
span(
    150,
    174,
    "P/N",
    (
        "Mobile trên bàn của nữ ở giữa/phải, calculator trắng đen riêng; người khác "
        "trong context không đổi anchor."
    ),
)
span(175, 199, "P/N", "Mobile trên bàn riêng; calculator xanh trắng riêng; hướng đầu về bàn/bài.")
span(
    200,
    223,
    "P/N",
    "Mobile trên bài riêng, calculator trắng đen riêng; người phía trước chỉ là vật che/context.",
)
put(
    [210, 219],
    "P/U",
    (
        "Mobile còn evidence trên bàn nhưng đầu bị cắt/che nhiều; không chốt looking"
        " N từ các frame khác."
    ),
)
span(
    224,
    252,
    "P/N",
    (
        "Đề xuất anchor là nam áo trắng ở giữa, đúng vùng tâm metadata, mobile trong"
        " tay; cần recrop để owner xác nhận attribution có điều kiện."
    ),
)
span(
    253,
    281,
    "P/N",
    "Mobile màn hình sáng trên bàn, calculator đen riêng; nhìn bài/thiết bị trong vùng bài riêng.",
)
span(
    282,
    368,
    "P/N",
    (
        "Nữ áo trắng phía trước; mobile riêng rõ cạnh/cùng calculator; nhìn bài hoặc"
        " thiết bị trong vùng riêng."
    ),
)
put(
    [294, 295, 303, 332, 337],
    "P/P",
    "Ngoại lệ nhóm P/N: đầu quay sang bên ngoài vùng bài riêng; mobile vẫn rõ.",
)
put(
    [338, 356, 357],
    "P/U",
    "Mobile rõ; hướng nhìn bị tay che hoặc ở ranh giới giữa bài riêng và phía bên cạnh.",
)
span(
    369,
    397,
    "P/N",
    "Nữ áo xanh số 10: mobile trên bàn hoặc cầm tay, calculator riêng; nhìn bài riêng.",
)
span(
    398,
    484,
    "P/N",
    (
        "Nữ áo khoác sọc trắng: mobile trên bàn/đang dùng, calculator riêng; hướng "
        "bài riêng. Dòng owner chỉ có nhận xét, không có cột nhãn hợp lệ."
    ),
)
put(
    [398, 399, 400, 473],
    "P/U",
    "Mobile rõ; tay che phần lớn mặt hoặc hướng nhìn trái chưa phân biệt chắc với bài riêng.",
)
span(
    485,
    513,
    "P/N",
    "Nữ kính áo trắng: calculator xanh nhạt cầm tay, mobile nằm riêng trên bàn; hướng bài riêng.",
)
span(
    514,
    542,
    "P/N",
    (
        "Đề xuất nam áo be ở giữa cầm mobile, calculator trên bàn; hướng bài riêng. "
        "Cần crop mới cho attribution rõ."
    ),
)
span(
    543,
    571,
    "U/N",
    (
        "Nữ áo vàng bên phải là anchor; bàn/tay bị cắt hoặc che. Không lấy mobile "
        "của nam áo trắng hàng sau/nữ số 10 làm phone của anchor."
    ),
)
span(
    572,
    597,
    "P/N",
    (
        "Nam áo xám: mobile trên bài hoặc trong tay; hướng bài riêng, cần crop rộng "
        "hơn giữ đầu và vùng bàn."
    ),
)
put(
    [582, 592, 593, 594],
    "P/U",
    "Crop cắt đầu khi anchor ngồi thẳng/đứng; cần đánh giá looking trên crop mới.",
)
span(
    598,
    603,
    "P/U",
    (
        "Mobile cầm tay rõ, nhưng crop mất đầu; một số frame gốc cũng mất đầu ở mép "
        "phải, không thể phục hồi bằng recrop."
    ),
)
span(
    604,
    610,
    "N/U",
    (
        "Nam áo sọc đen trắng: calculator riêng trên bàn, crop cắt đầu; cần recrop "
        "trước kết luận hướng nhìn."
    ),
)
put(
    [605, 606],
    "N/N",
    "Calculator có bàn phím, đầu nhìn bài riêng; đồng thuận owner cho crop hiện tại.",
)
span(
    611,
    617,
    "U/U",
    (
        "Nam áo đen hàng giữa; người phía trước che tay/bàn hoặc mất đầu khi đứng. "
        "Cần crop mới, không dùng phone của người khác."
    ),
)
put([612], "P/U", "Mobile trên bàn, đầu bị tay che; hướng nhìn chưa chắc.")
put([614], "U/P", "Đầu quay rõ sang bên; tay/bàn không đủ cho phone N hay P.")
put([616], "P/N", "Mobile trên bài riêng, đầu cúi về bài dù người trước chen vào crop.")
put([617], "P/U", "Mobile trong hai tay; đầu nằm ngoài crop cũ khi đứng.")
span(
    618,
    633,
    "P/N",
    (
        "Nam áo jersey: mobile trên bàn riêng/đang dùng, calculator trắng đen riêng;"
        " phần lớn hướng bài riêng."
    ),
)
put(
    [626, 627],
    "P/U",
    "Owner ghi looking P nhưng đầu ở ranh giới nhìn trước/bài; đề xuất U thay vì nhận nguyên nhóm.",
)
put([631], "P/P", "Frame 86: đầu quay rõ sang trái ngoài bài riêng, mobile trên bàn.")
put([632], "P/U", "Frame 90: chuyển động mờ khi quay/cúi; không lấy P từ frame 86.")
span(
    634,
    643,
    "P/U",
    (
        "Khung cố định mất đầu hoặc lệch khi người đứng/ngồi thẳng; mobile trên bàn "
        "còn rõ, looking cần crop mới."
    ),
)
put(
    [643],
    "U/U",
    "Người áo đen phía trước chiếm phần lớn crop; không gán thiết bị của người này cho jersey.",
)
span(
    644,
    646,
    "P/N",
    "Nam áo navy: mobile trên bàn riêng, calculator xanh lá riêng, hướng bài riêng.",
)
put([647], "P/P", "Nam áo navy nghiêng đầu sang bài/người jersey bên trái; mobile riêng trên bàn.")
put(
    [648],
    "U/U",
    (
        "Metadata nói redshirt nhưng crop chứa nữ áo trắng và nam áo đen. Quyết định"
        " N/N của owner có điều kiện cho nữ áo trắng, không áp cho redshirt."
    ),
)
span(
    649,
    652,
    "P/N",
    (
        "Nam áo đỏ kính: mobile trên giấy, đầu hướng bài riêng; không lấy nam áo đen"
        " phía trước làm anchor."
    ),
)
span(
    653,
    656,
    "P/N",
    "Nữ áo trắng kính: calculator xanh nhạt cầm tay, mobile trên sách/bàn riêng, nhìn bài riêng.",
)
span(
    657,
    672,
    "P/N",
    "Nữ áo xám phía trước: mobile đen nằm trên bàn/sách riêng; xét hướng đầu từng ảnh.",
)
put(
    [657, 658, 663, 670, 671],
    "P/P",
    "Đầu hướng ra phía trước/bên cạnh ngoài bài riêng; mobile trên bàn.",
)
put(
    [660, 661, 664, 665],
    "P/U",
    "Mobile trên bàn; hướng nhìn chưa đủ rõ giữa bài riêng và phía trước/tay che.",
)
span(673, 702, "P/P", "Nữ áo hồng: mobile trên bàn/cầm tay; đầu hướng ra bên ngoài vùng bài riêng.")
put(
    [673, 674],
    "P/N",
    "Ngoại lệ owner P/P: đầu đang cúi về trang giấy riêng, không thấy hướng sang người khác.",
)
span(
    684,
    693,
    "P/N",
    (
        "Nữ áo hồng nhìn sách hoặc mobile đặt ngay vùng bài riêng; không dùng quy "
        "tắc ZIP nhìn phone là looking P."
    ),
)
put(
    [694, 696, 697, 702],
    "P/U",
    (
        "Mobile rõ nhưng xoay thân/nhìn phone hoặc đứng chỉnh tóc không đủ xác định "
        "hướng nhìn ngoài bài riêng."
    ),
)
span(
    703,
    717,
    "U/P",
    (
        "Nam vest xanh phía trước nhìn ra ngoài bài; tay dưới bàn hoặc vùng tay "
        "thiếu evidence, không tự gán phone N."
    ),
)
put(
    [704, 705, 707, 709, 715, 716, 717],
    "N/N",
    "Nam vest xanh: hai tay và vùng bài đủ quan sát, đọc/viết bài riêng; không thấy mobile.",
)
put([710, 711, 714], "N/P", "Hai tay/vùng bàn rõ không mobile; đầu nhìn ra ngoài bài riêng.")
span(
    718,
    733,
    "U/U",
    (
        "Nam vest xám bên trái là anchor; crop có nhiều người. Cần recrop và xem "
        "riêng tay/bàn/hướng đầu."
    ),
)
put(
    [734],
    "U/U",
    (
        "Nữ áo đỏ không có trong vùng crop/frame tại vị trí này; không retarget sang"
        " nam/nữ khác để cứu nhãn."
    ),
)
span(
    735,
    748,
    "U/U",
    (
        "Nữ áo đỏ hàng giữa là anchor, không phải nam vest xám tiền cảnh; cần recrop"
        " và xem tay/bàn riêng."
    ),
)
put([749, 761], "U/N", "Vùng tay bị che hoặc mờ; đầu về bài riêng, phone giữ U đúng owner.")
put(
    [750, 753, 756, 757],
    "N/P",
    (
        "Đầu quay rõ khỏi bài riêng; vật/tài liệu/case trong vùng tay không phải "
        "mobile theo owner và đối chiếu crop."
    ),
)
put(
    [751, 752, 754, 755, 758, 759, 760, 763, 764, 765],
    "N/N",
    (
        "Đầu về vùng bài riêng, vật trên bàn là sách/case/bút; đồng thuận owner về "
        "absence mobile ở crop này."
    ),
)
put(
    [762],
    "U/N",
    "Vật đang cầm quá nhỏ/mờ để xác nhận không phải phone; khác owner N/N, đề xuất phone U.",
)
put(
    [592, 593, 594],
    "U/U",
    (
        "Đầu bị crop cắt và mobile không còn thấy tại frame này; không truyền phone "
        "P từ frame trước/sau."
    ),
)
put(
    [519, 523, 524, 540, 541],
    "P/U",
    (
        "Mobile rõ, tay che phần lớn mặt; chưa đủ kết luận hướng nhìn dù các ảnh "
        "cùng nhóm đang nhìn bài."
    ),
)

assert len(notes) == 765
(HERE / "manual-observations.json").write_text(
    json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)

# Explicit study context boxes, XYXY in source pixels. No runtime padding policy.
geometry = {}


def box(a, b, xyxy, labels=None):
    for i in range(a, b + 1):
        geometry[f"CB-{i:04}-R1"] = {
            "original_id": f"CB-{i:04}",
            "context_xyxy": xyxy,
            "draft_labels": labels,
        }


box(18, 25, [1090, 100, 1320, 335], "U/N")
box(30, 30, [1000, 290, 1410, 900], "N/P")
box(55, 55, [1080, 310, 1510, 900], "N/U")
box(106, 112, [620, 285, 915, 570], "U/N")
box(224, 252, [795, 135, 970, 310], "P/N")
box(514, 542, [440, 225, 705, 470], "P/N")
box(543, 571, [1600, 590, 1920, 1010], "U/N")
box(572, 581, [0, 470, 610, 1080], "P/N")
box(582, 582, [100, 350, 650, 1080], "P/P")
box(583, 591, [80, 430, 650, 1080], "P/N")
box(592, 597, [50, 320, 630, 1080], "U/U")
box(598, 600, [1580, 450, 1920, 1010], "P/N")
box(601, 603, [1630, 350, 1920, 980], "P/U")
box(604, 604, [1000, 250, 1490, 920], "N/N")
box(607, 610, [980, 250, 1560, 920], "N/U")
box(611, 616, [1330, 100, 1680, 630], "U/U")
box(617, 617, [1300, 0, 1690, 640], "P/N")
box(634, 642, [540, 70, 840, 480], "P/U")
box(643, 643, [570, 0, 840, 490], "P/U")
box(648, 648, [110, 190, 390, 510], "P/N")
box(715, 717, [990, 300, 1230, 570], "N/N")
box(718, 733, [790, 300, 1040, 600], "U/U")
box(735, 735, [875, 140, 1010, 390], "U/P")
box(736, 748, [750, 245, 940, 425], "U/U")
new = [
    (
        "CB-NEW-01",
        543,
        [390, 330, 750, 630],
        "P/P",
        "g2_new_striped_green",
        "Nữ áo sọc xanh, mobile trong tay, đầu quay trái sang người bên cạnh.",
    ),
    (
        "CB-NEW-02",
        514,
        [390, 330, 750, 630],
        "P/N",
        "g2_new_striped_green",
        (
            "Cùng anchor sọc xanh, mobile trong tay, đầu cúi trong vùng riêng; cặp tương"
            " phản với NEW-01."
        ),
    ),
    (
        "CB-NEW-03",
        30,
        [240, 250, 480, 550],
        "P/N",
        "g1_new_olive",
        "Nam áo xanh olive: mobile riêng trên bàn cạnh calculator, hướng giấy riêng.",
    ),
    (
        "CB-NEW-04",
        648,
        [430, 100, 700, 460],
        "U/N",
        "g5_new_white_left",
        (
            "Nữ áo trắng thực sự xuất hiện trong crop lỗi CB-0648; tạo anchor mới, không"
            " đổi danh tính redshirt."
        ),
    ),
    (
        "CB-NEW-05",
        718,
        [280, 350, 435, 550],
        "P/P",
        "g4_new_blue_jacket",
        "Nữ áo khoác xanh nhạt phía sau: mobile trên sách riêng, đầu nhìn ra ngoài vùng bài.",
    ),
]
for cid, source, xyxy, labels, anchor, reason in new:
    geometry[cid] = {
        "source_crop_id": f"CB-{source:04}",
        "context_xyxy": xyxy,
        "draft_labels": labels,
        "new_anchor_id": anchor,
        "reason": reason,
    }


# Second visual pass: every derivative viewed at 224 and against its native source.
def revise(ids, labels, reason):
    for i in ids:
        row = geometry[f"CB-{i:04}-R1"]
        row["draft_labels"] = labels
        row["reason"] = reason


revise(
    range(18, 26),
    "P/N",
    (
        "Recrop tách nữ kính bên phải: mobile trên bàn/đang cầm rõ, calculator trắng"
        " riêng, nhìn bài riêng."
    ),
)
revise([519, 523, 524, 540, 541], "P/U", "Mobile rõ nhưng tay che phần lớn mặt; giữ looking U.")
revise(
    range(543, 571),
    "P/N",
    (
        "Recrop phục hồi vùng bàn nữ áo vàng: mobile tối màu nằm cạnh calculator, "
        "đầu hướng bài riêng. Không dùng phone của hàng sau."
    ),
)
revise([571], "U/N", "Đang lật giấy che vùng thiết bị, không nội suy phone từ các frame trước.")
revise(
    [592, 593, 594], "U/N", "Đã phục hồi đầu nhìn bài riêng; phone không thấy ở frame này, giữ U."
)
revise([595, 596, 597], "P/N", "Recrop giữ đầu và phone trong tay/trên giấy; hướng bài riêng.")
revise(
    [607, 608, 610],
    "N/N",
    "Recrop giữ đầu nhìn giấy riêng, bàn và calculator quan sát đủ, không thấy mobile.",
)
revise([609], "U/P", "Đầu quay rõ sang phải; một tay vươn ra ngoài context nên phone không chốt N.")
revise([611], "P/N", "Mobile trên bàn riêng đã được giữ trọn hơn, đầu hướng bài.")
revise([612], "P/U", "Mobile riêng thấy rõ; tay che mặt, looking U.")
revise(
    [613],
    "U/N",
    "Đầu hướng thiết bị/bài riêng; vật cầm chưa chắc mobile hay calculator tại 224, phone U.",
)
revise([614], "U/P", "Đầu quay trái rõ; bàn/tay bị người trước che, phone U.")
revise(
    [615],
    "U/U",
    (
        "Anchor cúi lệch và bị người trước che phần lớn; bản recrop không giải quyết"
        " được attribution/visibility."
    ),
)
revise([616], "P/N", "Mobile trên bàn riêng, đầu cúi nhìn bài; người trước che một phần context.")
revise(
    [634, 635, 636, 637, 641, 642],
    "P/N",
    "Recrop phục hồi đầu hướng bài/thiết bị riêng, mobile trên bàn hoặc trong tay.",
)
revise([638, 639], "P/P", "Recrop phục hồi đầu quay rõ trái ngoài bài riêng; mobile trên bàn.")
revise(
    [640, 643],
    "P/U",
    "Mobile riêng thấy được; nét mặt/chuyển động hoặc người trước che khiến hướng nhìn chưa chắc.",
)
revise([718, 720, 721, 723], "U/P", "Nam vest xám nhìn ra ngoài bài; tay dưới bàn nên phone U.")
revise(
    [719, 722], "U/N", "Nam vest xám nhìn xuống sách/tay; vùng tay không đủ rõ để loại trừ phone."
)
revise(
    [724, 725, 728, 729, 730, 731, 732, 733],
    "N/N",
    "Nam vest xám: recrop giữ vùng tay và bài, đang đọc/viết riêng, không thấy mobile.",
)
revise([726, 727], "N/P", "Nam vest xám: tay/bàn đủ quan sát, đầu hướng ra ngoài bài riêng.")
revise(
    [736, 737, 738, 740, 741, 743, 745],
    "U/P",
    "Nữ áo đỏ: đầu hướng ra trước/bên ngoài bài riêng; bàn bị tiền cảnh che một phần, phone U.",
)
revise(
    [739, 742, 744, 746, 747, 748],
    "U/N",
    "Nữ áo đỏ: đầu nhìn xuống bài riêng; thiết bị/vùng tay nhỏ và che, phone U.",
)
geometry["CB-NEW-03"]["draft_labels"] = "U/N"
geometry["CB-NEW-03"]["reason"] = (
    "Nam áo olive nhìn bài riêng; vật tối cạnh tay quá nhỏ tại 224 để phân biệt "
    "chắc mobile, giữ U. Có ích cho looking N với phone masked."
)
(HERE / "geometry-proposals.json").write_text(
    json.dumps(geometry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
