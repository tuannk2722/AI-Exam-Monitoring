import hashlib
import json
from pathlib import Path

ROOT = Path("D:/ai-exam-monitoring-final")
REPORT = ROOT / "artifacts/reports/E004-new-bundle-audit-20261015"
inventory = json.loads((REPORT / "crop-inventory.json").read_text(encoding="utf-8"))
frames = [
    r
    for r in json.loads((REPORT / "frame-inventory.json").read_text(encoding="utf-8"))
    if r["source_group"] == "A"
]
derivatives = {
    r["id"]: r
    for r in json.loads((REPORT / "source-A-derivatives.json").read_text(encoding="utf-8"))
}
decisions = [
    (
        "U/N",
        "Người áo xanh tóc mái phía trước, cầm vật đen",
        "Vật cầm chỉ lộ cạnh và mặt lưng, không thấy mặt kính lớn hoặc camera; động tác bấm không đủ phân biệt calculator.",
        "Mặt hướng trực tiếp vào vật trên vùng sách riêng.",
    ),
    (
        "N/N",
        "Người áo xanh giữa hình, tay gần miệng",
        "Hai bàn tay thấy rõ: một tay cầm bút gần miệng, một tay đặt trên giấy; vùng bàn không có thiết bị chưa phân loại của anchor.",
        "Đầu và mặt hướng xuống tờ giấy riêng.",
    ),
    (
        "U/N",
        "Người tóc dài tết hai bên, cầm vật trắng trước mặt",
        "Mặt trắng trơn hướng máy ảnh, không có đặc trưng phân biệt phone/calculator.",
        "Đầu hướng vào vật cầm sát vùng bài riêng; không phải nhìn người bên trái.",
    ),
    (
        "N/P",
        "Người tóc bob đeo kính bên trái",
        "Calculator có màn hình nhỏ và nhiều hàng phím rõ trên bàn; hai tay đang cầm bút và giấy, không có phone riêng rõ hoặc vật mơ hồ khác.",
        "Mặt và mắt hướng lên bên trái, ra khỏi giấy/bàn riêng.",
    ),
    (
        "N/N",
        "Người tóc dài buộc sau đang bấm calculator",
        "Cụm phím calculator rõ dưới hai bàn tay; vùng giấy còn lại không có vật chưa phân loại.",
        "Mặt hướng xuống calculator và giấy riêng.",
    ),
    (
        "N/N",
        "Người tóc buộc hai bên phía trước, cầm calculator đen",
        "Vật cầm có màn hình nhỏ và hàng phím rõ ngay trong input; tay kia cầm bút viết, không lấy vật hồng của người bên trái làm phone của anchor.",
        "Mặt hướng xuống vùng giấy/calculator riêng.",
    ),
    (
        "U/N",
        "Người kính trong, dây đeo xanh nhạt, cầm vật hồng",
        "Chỉ thấy lưng/cạnh vỏ hồng trơn; không xác định mobile từ màu và dáng cầm.",
        "Mặt hướng trực tiếp vào vật trên giấy riêng.",
    ),
    (
        "N/N",
        "Người áo xanh tóc mái cúi viết ở giữa",
        "Tay viết và tay đặt giấy đều thấy; túi bút che một phần bàn nhưng không có thiết bị mơ hồ còn lộ của anchor. Vật hồng bên phải thuộc người khác.",
        "Mặt hướng xuống chỗ bút viết trên giấy riêng.",
    ),
    (
        "N/N",
        "Người áo xanh tóc buộc sát tường trái",
        "Hai tay trên giấy, calculator có phím rõ ở bàn; không thấy vật chưa phân loại trong phần làm việc của anchor.",
        "Mặt hướng xuống tờ giấy riêng.",
    ),
    (
        "N/N",
        "Người tóc dài phía trước, đồng hồ trắng",
        "Calculator hồng ép vào ngực vẫn lộ bàn phím; vật hồng trên bàn có cấu trúc nắp rỗng, không lấy thiết bị người phía sau làm của anchor.",
        "Mắt/mặt hướng xuống trang đang viết.",
    ),
    (
        "N/N",
        "Người áo xanh bên phải, hai tay khoanh trước ngực",
        "Hai bàn tay khoanh thấy rõ, một tay cầm bút; không có phone hoặc vật mơ hồ trong vùng bài crop.",
        "Mặt cúi về tờ giấy ngay trước hai tay.",
    ),
    (
        "U/N",
        "Người áo xanh dây hồng ở trước",
        "Crop cũ cắt hẳn bàn tay phía phải; không kết luận absence từ crop cũ. Bản R1 mở sang phải để phục hồi tay.",
        "Hướng mặt rõ về trang đang đọc.",
    ),
    (
        "U/N",
        "Người áo khoác trắng xanh phía sau",
        "Tay cầm bút rõ và calculator có phím rõ, nhưng bàn tay còn lại bị tay áo/đầu che; calculator không đủ tự kết luận absence.",
        "Đầu và bút cùng hướng vào giấy riêng.",
    ),
    (
        "N/N",
        "Người kính lớn, áo xanh, dây đeo trắng",
        "Hai bàn tay viết/giữ giấy thấy rõ; calculator hồng nằm ngoài crop này nên không viện dẫn calculator làm evidence cho crop cũ.",
        "Mặt hướng xuống giấy đang viết.",
    ),
    (
        "U/N",
        "Người áo khoác trắng xanh cúi sát giấy",
        "Calculator có phím rõ nhưng một bàn tay hoàn toàn khuất dưới phần tay áo/đầu; phone vẫn U.",
        "Hướng đầu xuống giấy và tay bút đủ rõ dù không thấy mắt.",
    ),
    (
        "N/N",
        "Người áo khoác trắng xanh, tay chống má",
        "Một tay đặt/di trên giấy, tay kia chống má đều rõ; các calculator trên bàn có phím, vật xanh mỏng là bút/thước, không có mobile rõ.",
        "Mặt và tay chỉ cùng hướng vào trang giấy riêng.",
    ),
    (
        "U/N",
        "Người áo xanh tóc búi với dây buộc trắng",
        "Tay bút rõ nhưng bàn tay còn lại đi khỏi mép trái và bị đồ/vùng crop che; chưa xác nhận absence.",
        "Mặt hướng xuống giấy nơi đang viết.",
    ),
    (
        "U/N",
        "Người áo xanh tóc ngắn phía trước",
        "Crop cũ cắt bàn tay ở mép phải; đề xuất mở crop R1 để thấy đầy đủ hai tay.",
        "Mặt hướng xuống trang giấy riêng.",
    ),
    (
        "N/N",
        "Người áo xanh đeo kính phía sau bên phải",
        "Hai bàn tay viết/giữ giấy rõ; calculator bàn phím rõ ở mép phải, không có vật mơ hồ của anchor.",
        "Mặt hướng vào điểm đang viết trên giấy riêng.",
    ),
    (
        "N/N",
        "Người áo xanh nghiêng người viết ở dãy phải",
        "Hai tay viết/giữ giấy nhìn rõ; phần calculator còn lộ dưới giấy vẫn có hàng phím, không chỉ một cạnh đen.",
        "Đầu nghiêng nhưng hướng vào giấy riêng, không tự gán looking P từ dáng nghiêng.",
    ),
    (
        "N/N",
        "Người áo xanh tóc mái đeo dây chuyền phía trước",
        "Hai tay và calculator bàn phím rõ trên bàn riêng; vật trắng do người phía sau cầm không thuộc anchor.",
        "Đầu/mặt hướng vào điểm bút đang viết.",
    ),
    (
        "U/N",
        "Người áo xanh kính trong ở giữa, cầm vật trắng",
        "Vật trắng chỉ lộ lưng/cạnh trong tay trái; không dùng chữ metadata writing để bỏ qua vật.",
        "Mặt hướng vào vật/giấy trong vùng bài riêng.",
    ),
]
rows = []
for base, (labels, desc, phone, looking) in zip(
    [r for r in inventory if r["source_group"] == "A"], decisions, strict=True
):
    row = {
        k: base[k]
        for k in (
            "id",
            "source",
            "source_sha256",
            "crop",
            "crop_sha256",
            "input",
            "context_xyxy",
            "frame_num",
            "anchor_id",
        )
    }
    row.update(
        draft_labels=labels,
        anchor_description=desc,
        phone_reason=phone,
        looking_reason=looking,
        disposition="keep",
        visual_evidence=["supplied_224", "same_frame_native_context", "frame_overview"],
        training_ready=False,
        assigned_split=None,
    )
    if base["id"] in ("NB-0012", "NB-0018"):
        row.update(
            disposition="recrop",
            replacement_id=base["id"] + "-R1",
            proposedbox=derivatives[base["id"] + "-R1"]["context_xyxy"],
        )
    rows.append(row)
extra_notes = {
    "NB-0012-R1": (
        "N/N",
        "Người áo xanh dây hồng ở trước",
        "Crop rộng hơn thấy hai bàn tay trên giấy, không có thiết bị mơ hồ riêng; calculator phía sau thuộc người áo trắng xanh.",
        "Mặt hướng vào sách/giấy riêng.",
    ),
    "NB-0018-R1": (
        "N/N",
        "Người áo xanh tóc ngắn phía trước",
        "Hai tay nay nằm trong crop; một tay viết một tay giữ giấy, không có vật chưa phân loại của anchor.",
        "Mặt hướng vào giấy đang viết.",
    ),
    "NA-001": (
        "U/P",
        "Người áo khoác trắng xanh ở hàng sau, nhìn về máy ảnh",
        "Một bàn tay/vùng bàn bị đầu người trước che; vật xanh trên bàn chỉ lộ mặt trơn không phân loại.",
        "Mặt và mắt nhìn thẳng ra phía máy ảnh, ngoài vùng giấy riêng.",
    ),
    "NA-002": (
        "U/N",
        "Người áo sơ mi trắng phía trái, cầm vật trắng",
        "Vật trắng chỉ lộ lưng trơn, không đủ phân biệt phone và calculator.",
        "Đầu/mặt hướng xuống vật trong hai tay trên bàn riêng.",
    ),
    "NA-003": (
        "U/N",
        "Người áo xanh kẹp tóc bạc phía trước bên phải",
        "Vật đen dưới mép giấy bên trái chỉ lộ một phần bề mặt; không đủ nhận dạng hoặc attribution chắc giữa hai chỗ ngồi.",
        "Mặt hướng xuống vùng đang viết của mình; người bên trái không là anchor.",
    ),
    "NA-004": (
        "N/N",
        "Người áo xanh phía trước bên phải, tóc rẽ giữa",
        "Hai tay viết và giữ giấy rõ, calculator có phím trên bàn bên trái; không có vật chưa phân loại trong phần làm việc riêng.",
        "Đầu/mặt hướng xuống trang đang viết.",
    ),
    "NA-005": (
        "U/N",
        "Người áo xanh kính trong phía trước bên trái",
        "Vật trắng trong tay chỉ lộ vỏ lưng/cạnh; không kết luận phone hoặc calculator chỉ từ dáng cầm.",
        "Mặt hướng vào vật và giấy riêng.",
    ),
    "NA-006": (
        "N/N",
        "Người áo xanh tóc búi gần cửa sổ bên phải",
        "Tay bút và tay chống cằm rõ; calculator trên bàn lộ hàng phím, không có thiết bị chưa phân loại của anchor.",
        "Mặt hướng xuống giấy riêng, không gán P từ góc nhìn nghiêng.",
    ),
    "NA-007": (
        "U/N",
        "Người áo khoác trắng xanh phía sau, cầm vật xanh nhạt",
        "Chỉ thấy cạnh/lưng xanh nhạt và một phần tay, không có mặt trước hay camera phân biệt.",
        "Đầu/mặt hướng vào vật trên bàn riêng.",
    ),
    "NA-008": (
        "N/N",
        "Người áo xanh kính lớn, dây đeo trắng trong cảnh calculator hồng",
        "Calculator hồng trên bàn hiện đủ phím và màn hình nhỏ trong input; hai tay viết/giữ giấy rõ.",
        "Mặt hướng xuống điểm bút trên giấy riêng.",
    ),
}
extras = []
for ident, item in derivatives.items():
    labels, desc, phone, looking = extra_notes[ident]
    row = dict(item)
    row.update(
        draft_labels=labels,
        anchor_description=desc,
        phone_reason=phone,
        looking_reason=looking,
        disposition="keep",
        training_ready=False,
        assigned_split=None,
        visual_evidence=["source_frame", "native_derivative", "final_224"],
    )
    row["anchor_id"] = {
        "NB-0012-R1": "A14_front_blue_writing",
        "NB-0018-R1": "A20_front_blue_writing",
        "NA-008": "A16_right_glasses_pink_calculator",
    }.get(ident, "draft_local_" + ident)
    for key in ("source", "crop", "input"):
        row[key + "_sha256"] = hashlib.sha256((ROOT / row[key]).read_bytes()).hexdigest()
    if ident == "NA-003":
        row["geometry_note"] = (
            "Khung rộng để giữ vật che một phần trên giấy; anchor phải rõ nhưng còn người bên trái, owner cần xem riêng geometry."
        )
    if ident == "NA-008":
        row["selection_note"] = (
            "Cùng anchor NB-0014, góc này giữ calculator hồng để bổ sung hard negative; không tính là người mới."
        )
    extras.append(row)
frame_notes = {
    2: "Cảnh rộng phía trước: thêm NA-001 nhìn ra ngoài và NA-002 cầm vật lưng trắng; các người còn lại trùng trạng thái/góc cận trong frame 3–10 hoặc đầu/tay bị người trước che.",
    3: "Hai crop supplied; xem người kính bên trái cầm thiết bị nhưng đồng dạng lưng/cạnh và khung dễ dính người giữa, không thêm gần lặp.",
    4: "Ba crop supplied bao phủ foreground cầm vật lưng trắng, bob nhìn trái, và calculator sau; không truyền nhãn metadata phone.",
    5: "Bốn crop supplied bao phủ dãy gần; rear white-blue cầm vật được chọn ở frame 9 với crop rõ hơn.",
    6: "Hai crop supplied; người trước cầm calculator hồng nhìn rõ phím; người bên phải khoanh tay. Các đầu phía sau đã có góc cận khác.",
    7: "Hai crop supplied; sửa NB-0012 để lấy lại bàn tay bị cắt. Người phía sau một tay khuất giữ U.",
    8: "Hai crop supplied; NB-0014 mất calculator khỏi crop, chọn thêm NA-008 ở frame 21; NB-0015 tay khuất giữ U.",
    9: "Hai crop supplied; thêm NA-007 rear trắng xanh cầm vật lưng xanh. Không gọi phone bằng màu vỏ.",
    10: "Hai crop supplied; mở NB-0018 để phục hồi bàn tay phải. Người kính sau có calculator và hai tay rõ.",
    13: "Ba crop supplied; NB-0022 có vật trắng cầm tay không phân loại. Người xa góc trái nhìn ngang quá nhỏ và tay bị bàn/người che, không thêm chỉ để tăng số lượng.",
    14: "Thêm NA-003 với vật che một phần cạnh sách; khung rộng có cờ geometry. Các học sinh sau còn nhỏ/che hoặc lặp state viết.",
    15: "Cảnh rộng nhiều đầu tiền cảnh và thiết bị chỉ lộ cạnh. Người nhìn trước ở hàng xa bị cắt đỉnh đầu và vùng tay, không lấy crop yếu này; NA-001 frame 2 có evidence looking tốt hơn.",
    16: "Lặp cảnh frame 3; người giữa chuyển sang viết nhưng looking vẫn N, người cầm vật vẫn chỉ lưng/cạnh; không nhân bản.",
    17: "Lặp cảnh frame 4; bob đã cúi xuống giấy nhưng có crop NN khác trong bộ, không cần tăng mẫu gần lặp. Vật trắng vẫn lưng trơn.",
    18: "Lặp frame 5; vật hồng vẫn mặt lưng, calculator đen vẫn phím rõ; không thêm.",
    19: "Lặp frame 6; calculator hồng lộ nhiều phím hơn nhưng cùng trạng thái N/N, không thêm.",
    20: "Lặp frame 7; hai người vẫn nhìn giấy và geometry tương tự, dùng hai crop/recrop đã chọn.",
    21: "Chọn NA-008 cho cùng anchor NB-0014 để có calculator hồng + hai tay trong input; không tính người mới.",
    22: "Thêm NA-004 người áo xanh phía phải có calculator và hai tay rõ; người khoác trắng trái đã có NB-0016, trạng thái vẫn N/N.",
    23: "Lặp frame 10, hai người viết và calculator phím rõ; không thêm.",
    24: "Thêm NA-005 lưng thiết bị trắng và NA-006 calculator bên cửa sổ. Cả hai hướng vào vùng riêng; không dùng tên metadata để đoán thiết bị.",
}
coverage = [
    {
        "id": f["id"],
        "frame_num": f["frame_num"],
        "source": f["source"],
        "visual_status": "screened_overview",
        "observations": frame_notes[f["frame_num"]],
    }
    for f in frames
]
result = {
    "status": "draft_visual_audit_not_acceptance",
    "scope": {
        "supplied_crops": 22,
        "source_frames_screened": 21,
        "native_contexts_viewed": 22,
        "native_full_frames_viewed": [2, 14, 15, 24],
        "derivative_inputs_viewed": 10,
    },
    "rubric": "artifacts/reports/E004-device-consistency-20261015/rubric.md",
    "supplied_reviews": rows,
    "derivative_reviews": extras,
    "frame_coverage": coverage,
    "limitations": [
        "Nguồn A có shot cận lặp và có thể cùng người qua nhiều góc; ID mới chỉ là anchor local, không là danh tính hay số người duy nhất.",
        "Nguồn overview sàng lọc đủ 21 frame, không tuyên bố đã mở native toàn bộ 21 frame.",
        "Nhãn chưa được owner review; source/split/training acceptance chưa được thiết lập.",
    ],
}
(REPORT / "source-A-review.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(
    "A: 22 supplied reviewed, 2 replacement crops, 8 added crop candidates, 21 source overview coverage"
)
