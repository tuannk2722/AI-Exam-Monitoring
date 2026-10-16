"""Recorded visual corrections for the unsealed refinement study."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def save(name, value):
    (HERE / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


v = read("visual-decisions.json")
notes = [
    (
        "Mobile riêng trên bàn cùng calculator trắng; giữ viết, sửa tóc, "
        "cầm calculator và góc sau pan."
    ),
    "Calculator xanh cùng mobile trên bàn; giữ góc nhìn và thao tác khác nhau.",
    (
        "Mobile trên bàn; lật giấy trong vùng bài riêng không tự thành "
        "looking U. Các cảnh còn lại lặp."
    ),
    "Thiết bị nhỏ trong tay chưa đủ đặc điểm phân biệt; không suy P chỉ từ thao tác bấm.",
    "Mobile trên giấy riêng và calculator đen; giữ tư thế viết, che mặt và thay đổi tay.",
    (
        "87 ảnh cùng người: giữ 8 cảnh khác về vật thể, tư thế hoặc hướng "
        "đầu; 303 nhìn ngoài bài, 294 hướng chưa chắc."
    ),
    "Mobile màn hình xanh và calculator riêng; giữ cầm, đặt, viết, thay đổi góc.",
    (
        "87 ảnh cùng áo khoác: giữ 7 cảnh đại diện; tay ôm đầu vẫn có thể "
        "đủ hướng bài riêng. 473 đọc giấy riêng nên N."
    ),
    "Calculator xanh và mobile trên bàn; giữ 5 cảnh rõ, không suy phone từ calculator.",
    "Phone trong tay; 524 mờ và 540/541 che mặt khiến looking U. Giữ 540 đại diện che khuất.",
    (
        "Mobile trên bàn và calculator; 571 giấy che thiết bị nên phone U,"
        " không kế thừa P từ frame khác."
    ),
    (
        "Mobile trên bàn; 582 quay ngoài bài; 592–594 thiết bị bị che nên "
        "U. Giữ các mức che khuất khác nhau."
    ),
    "Mobile nhìn được; 601–603 thiếu đầu ở nguồn nên looking U. Giữ một ví dụ cắt đầu.",
    "605–608 không thấy phone khi tay/bàn đủ rõ; 604/610 tay dưới bàn nên U. 609 quay ngoài bài.",
    "613 thiết bị chưa rõ; 614 quay ngoài bài; 615 che khuất không đủ cả hai target nên withheld.",
    "Giữ own-paper, quay đầu rõ và hướng chưa xác định. 631/638/639 có hướng ngoài bài.",
    "Phone riêng trên bàn; 647 quay đầu khỏi bài, giữ cặp tương phản với 644/646.",
    "Anchor áo đỏ và thiết bị riêng; giữ cảnh rõ, chuyển biến thể mờ/lặp sang alternatives.",
    "Phone trên bàn; giữ hai thao tác đại diện của cùng người.",
    (
        "Giữ làm bài, hướng ra ngoài và thay đổi quan sát thiết bị; các "
        "frame tương tự là alternatives."
    ),
    "694/696/697 nhìn thiết bị/bài trong vùng riêng nên looking N; giữ cảnh đổi hướng thật sự.",
    "Tay dưới bàn không chứng minh phone N; giữ cảnh đủ tay/bàn và các góc ngoài bài rõ.",
    (
        "727 đầu hướng trang riêng nên N; 733 hai tay dưới bàn nên phone "
        "U. Giữ viết, đọc và nhìn ra ngoài."
    ),
    (
        "734 không có đúng anchor áo đỏ nên withheld. Giữ đứng, quay bên, "
        "cúi bài; bàn bị che nên phone U."
    ),
    "Giữ đứng, hướng sang bên và cúi bài; không tăng số crop chỉ vì chuyển động tay nhỏ.",
    "Giữ lật giấy, quay sang bạn rõ và viết; không gọi hộp bút là mobile.",
    (
        "Giữ đọc, vật nhỏ chưa phân biệt, lật giấy và che mặt; phone U khi"
        " bằng chứng thiết bị chưa đủ."
    ),
]
for i, reason in enumerate(notes, 6):
    v["tracks"][str(i)]["reason"] = reason
save("visual-decisions.json", v)
plan = read("expansion-plan.json")
boxes = {
    "G1-A01": [70, 250, 335, 580],
    "G1-A03": [420, 185, 650, 465],
    "G1-A04": [710, 195, 925, 450],
    "G1-A06": [800, 120, 1030, 375],
    "G1-A07": [1570, 250, 1915, 610],
    "G2-A01": [0, 240, 350, 525],
    "G2-A02": [0, 85, 260, 365],
    "G2-A03": [280, 180, 510, 440],
    "G2-A04": [220, 65, 430, 300],
    "G2-A06": [640, 110, 850, 390],
    "G2-A08": [880, 160, 1080, 430],
    "G2-A09": [1000, 170, 1240, 455],
    "G2-A10": [1210, 85, 1410, 325],
    "G2-A12": [960, 570, 1400, 1080],
    "G2-A13": [1430, 280, 1750, 710],
    "G5-A02": [320, 100, 570, 350],
    "G5-A06": [760, 85, 1020, 320],
    "G5-A07": [1160, 30, 1440, 300],
    "G5-A08": [1420, 75, 1680, 390],
    "G5-A09": [300, 310, 960, 800],
    "G4-A03": [480, 215, 685, 400],
    "G4-A04": [645, 175, 825, 365],
    "G4-A05": [620, 265, 820, 490],
    "G4-A06": [1140, 145, 1350, 350],
    "G3-A08": [155, 215, 315, 390],
}
frame_boxes = {
    "G5-A01": {"97": [120, 30, 385, 290], "109": [120, 20, 385, 290]},
    "G5-A02": {"97": [370, 65, 580, 340], "109": [370, 65, 580, 340]},
    "G5-A03": {"99": [420, 0, 610, 225]},
    "G5-A04": {"97": [550, 0, 740, 255]},
    "G5-A05": {"109": [640, 0, 860, 210]},
    "G5-A06": {"99": [920, 0, 1140, 270], "112": [920, 0, 1140, 270]},
}
for a in plan["anchors"]:
    if a["id"] in boxes:
        a["box"] = boxes[a["id"]]
    if a["id"] in frame_boxes:
        a["frame_boxes"] = frame_boxes[a["id"]]
save("expansion-plan.json", plan)
