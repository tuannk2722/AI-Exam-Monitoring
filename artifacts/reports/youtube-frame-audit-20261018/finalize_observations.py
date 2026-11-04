"""Persist the visual review in UTF-8; no automatic visual labels or acceptance."""

import json
from pathlib import Path

P = Path(__file__).resolve().parent

FRAME_NOTES = {
    "Y01": {
        2: "Cặp giữa cửa sổ viết; tiền cảnh mất tay/đầu, ưu tiên khung cận F8/F41.",
        3: "Ba vị trí bàn sau và hai người viết bên trái; vật trên bàn cần kiểm input.",
        4: "Khớp panel trên trái ảnh tham chiếu; gile tiền cảnh tay sát đầu; không gán phone của bàn trái cho người gile.",
        5: "Người áo xanh đứng che cặp giữa; tiền cảnh mất phần đầu/tay, ưu tiên frame khác.",
        6: "Áo xanh che bên phải; cặp giữa trái viết, F38 có góc cận hơn.",
        7: "Hai người giữa tương tác quanh sổ, dễ lẫn anchor; phía sau trái viết riêng.",
        8: "Tóc sáng trái viết; blouse trắng tiền cảnh có vật đen trên bàn; nam phía sau viết. Thử ROI tách người.",
        9: "Cặp giữa nhìn chung giấy; tay/context chồng; tiền cảnh tóc sáng viết.",
        37: "Cặp tóc sáng/gile giữa: người gile quay trái ngoài trang; đầu tiền cảnh sát mép bàn cần bỏ khỏi crop.",
        38: "Áo kem trái cúi viết; áo trắng phải quay về trang bên trái. Mobile trắng có cụm camera trên bàn trái; bàn sau có vật tối.",
        39: "Ba vị trí bàn sau viết/đọc; mobile riêng trên hai bàn trái/giữa. Áo đen ngoài dấu cũng được xét.",
        40: "Tóc dài trái và blouse phối đen phía sau viết; mobile trên bàn; tiền cảnh phải che một phần.",
        41: "Cặp tóc sáng đọc/viết, kính sau ngẩng. Thiết bị xanh thuộc bàn sau phải, không gán sang người trước.",
        42: "Cận tay viết, mất đầu khỏi nguồn; không chọn crop đầy đủ.",
        43: "Nam tiền cảnh viết, vật tối trên bìa xanh; tóc xoăn cạnh bên chạm ROI. Kiểm vật ở input, không tự phone P.",
        44: "Cặp giữa viết; gile nâu bàn sau nhìn trước; đầu tiền cảnh che tay/bàn hàng giữa.",
        45: "Nữ cạnh áo polo nhìn trái; áo polo mất một phần tay mép dưới, F128 rõ hơn.",
        49: "Một người đứng giữa; áo kem trái còn nhìn bài; hàng sau nhìn trước. Chỉ giữ nếu có work context.",
        50: "Tư thế đứng nhìn trước rõ, có bàn/sổ dưới; chọn một đại diện, không nhân frame gần trùng.",
        51: "Áo trắng ngồi lại, tay che miệng; người sau đứng dậy, nhiều chồng lấn.",
        52: "Áo trắng đứng cạnh tủ nhìn trái; bàn sau gile nâu nhìn trước. Crop đứng thiếu vùng bài bị giữ lại.",
        59: "Tóc dài hàng sau đứng; cặp polo/kính ngồi, khó tách tay/bàn người đứng.",
        60: "Khớp panel dưới trái: tóc dài nhìn trước, blouse phối đen viết, gile xám sau nhìn trước. Phone cạnh tay phải không gán sang tóc dài.",
        67: "Áo khoác trắng đứng tiền cảnh, vùng bàn ngoài mép; chưa đủ context cho crop looking.",
        69: "Nữ tóc buộc đứng nhìn trước nhưng vùng tay/bài ngoài khung; không ưu tiên.",
        94: "Áo xanh che bàn sau; áo trắng giữa chống cằm nhìn trước; nhiều đầu tiền cảnh.",
        95: "Áo xanh quay lưng che trái; polo viền đen cầm vật nhỏ chưa nhận dạng; cặp tóc sáng đọc/viết.",
        96: "Blouse tiền cảnh và nam phải viết; tóc sáng sau ngẩng, tay tiền cảnh sát mép dưới.",
        97: "Polo/kính cùng cầm giấy, hai anchor cạnh tranh; tóc dài sau nhìn ngoài giấy.",
        98: "Áo trắng bàn sau cúi sát sổ có vật mặt kính đen; gile nâu nhìn trước có phone trên bàn riêng.",
        99: "Tóc ngắn trái viết; áo kem sau nhìn trước; áo trắng giữa nhìn vùng sổ; người sau cúi thấp mặt che.",
        100: "Cận tay viết mất đầu; không đề xuất crop đầy đủ.",
        102: "Tóc dài viết, mobile trên giấy cạnh tay; phải bỏ phone của người phía sau khỏi ROI.",
        124: "Polo nhìn trước; cặp tóc sáng một người cúi, một người chống tay nhìn trước. Tách từng người.",
        125: "Vị trí đứng như F52, góc rộng hơn; ưu tiên F98 cho bàn sau ít lẫn.",
        126: "Áo khoác trắng đứng dậy, nam cạnh nhìn ngoài trang; tay tiền cảnh bị mép cắt.",
        128: "Khớp panel trên phải: nhiều vị trí cửa sổ, polo bị nữ trước che tay/bàn; ROI nam viết phía giữa khá rõ.",
        129: "Polo viền đen đứng sát bàn nhìn ngoài sổ; kính bên cạnh viết. Giữ riêng nếu anchor trội.",
        133: "Hai người cửa sổ đứng, nhiều tay người khác trong context; các khung cận tốt hơn.",
        187: "Cặp cuối cạnh tủ ngẩng; người phải bị mép dưới cắt tay, không chọn mặc định.",
        188: "Blouse đứng cạnh bàn, người phải có tay khuất; attribution vật trên bàn chưa chắc, phone U.",
        189: "Gần trùng F188, tay dưới mép; không thêm khi không có trạng thái mới.",
        190: "Người đứng xoay phải giơ tay; không truyền phone P từ frame ngồi F8.",
        197: "Polo đứng cạnh người kính viết, có mobile cạnh tay người kính; tách ROI và kiểm attribution.",
    },
    "Y02": {
        11: "Đủ sáu vị trí; trước phải đọc giấy, trái cúi vùng riêng; vật đen bàn trước chưa tự đủ P.",
        12: "Đủ sáu; trước phải giơ giấy sát mép, kính cuối trái ngẩng, cuối phải nhìn bài.",
        13: "Đủ sáu; đa số nhìn giấy, vật đen trước phải không rõ camera/mặt kính; gần F11.",
        14: "Đủ sáu; cuối và trước phải ngẩng nhìn đối diện, giữa phải cầm giấy.",
        18: "Đủ sáu; nam giữa trái và kính cuối trái ngẩng, vật trong tay nam chưa rõ; trước trái/phải cúi.",
        19: "Đủ sáu; cuối phải chống cằm nhìn trái, trước phải quay trái, ba trái cúi; crop dễ lẫn tay.",
        23: "Đủ sáu; đa số đọc/viết, cuối phải nhìn ngang; trạng thái gần F13/F26.",
        24: "Đủ sáu; trước trái giơ tay nhưng nhìn xuống, kính cuối trái nhìn lên; không suy phone từ cử chỉ.",
        26: "Đủ sáu; trước và giữa trái cúi, kính cuối trái nhìn phải; bên phải viết.",
        29: "Đủ sáu; giữa/cuối phải ngẩng, trước phải viết; đầu hai người cạnh tranh trong ROI giữa.",
        31: "Đủ sáu; trước trái nhìn phải và trước phải nhìn trái, nam/kính trái cúi. Giữ cặp hướng nếu tách được.",
        33: "Đủ sáu; cuối phải cầm giấy, giữa phải ngẩng, trước phải viết; trước trái hướng giấy.",
        44: "Đủ sáu, đổi framing có viền đen; trước trái quay mạnh, nam/kính ngẩng; nhiều đầu chồng.",
        46: "Đủ sáu; trước trái nhìn phía nam, nam cúi; giữa/trước phải nhìn ngang; mép cắt vai phải.",
        58: "Đủ sáu; bên phải nhìn trái, bên trái cúi; không thêm frame cùng trạng thái.",
    },
    "Y03": {
        1: "Khớp ảnh tham chiếu; dãy đánh dấu hiện diện, đa số cúi; hàng giữa xa ngẩng. Thử ROI từng vị trí.",
        4: "Xanh tiền cảnh ngẩng/đổi tay; áo xám nhìn bài, giáo viên chuyển phải; hàng xa đầu nhỏ.",
        8: "Xanh tiền cảnh viết; áo xám chống đầu, polo cúi; người giữa đưa tay lên mặt.",
        11: "Gần F8; chữ ở vùng cao không đè anchor gần, áo xám tay che đầu.",
        17: "Polo chống tay, xanh gần nhìn bài; hàng xa hướng không rõ, không ép known.",
        20: "Áo trắng kính giữa trái ngồi thẳng, tay lên mặt nhìn trước; áo xám che mặt, xanh gần cúi.",
        24: "Áo xanh giữa ngẩng nhìn phải; áo xám gục/che mặt, xanh gần cúi. Người xa trái đứng ngoài dấu quá nhỏ/che tay.",
        41: "Áo xám sau xanh gần ngẩng nhìn trước; xanh gần cúi. Bố cục cố định, các vùng dấu còn trong frame.",
        42: "Polo giữa trái nhìn phải rõ; áo xám và xanh gần cúi. Thử đối chứng looking của polo.",
        45: "Xanh tiền cảnh nhìn phải, áo xám/polo ngẩng; giữ một đại diện cho mỗi trạng thái.",
        46: "Xanh gần vẫn nhìn phải; người sát tường gần đổi tay/cúi, không truyền nhãn F1; xa gần giống F45.",
    },
    "Y04": {
        1: "Khớp ảnh tham chiếu; bàn đơn cúi, cặp gần/giữa có người ngẩng; nguồn 480 px làm tay/vật rất nhỏ.",
        2: "Bàn đơn và giữa trước phải ngẩng; phần lớn hàng sau cúi; có mặt trong frame chưa đủ crop đạt.",
        7: "Bàn đơn nhìn bài, cặp gần nhìn trước, giữa sau chống cằm; bút/hộp bút không tự mobile.",
        8: "Bàn đơn ngẩng nhẹ, hàng sau phải nhìn trước; gần F7, không tăng mẫu gần trùng.",
        9: "Bàn đơn quay trái khỏi sách; thử đối chứng F1. Cặp gần nhìn trước, hàng xa mờ.",
        22: "Bàn đôi gần phải nhìn sách mở, trái chống tay; nhiều người giữa cúi. Thử N vị trí phải.",
        23: "Gần F22, bàn đơn cúi; cặp gần cúi/chống cằm, không thêm trạng thái trùng.",
        30: "Thử vị trí trái bàn đôi; QA cho thấy đầu vẫn ngoài trang nên không giữ N dự kiến.",
        54: "Bàn đơn ngẩng phía giáo viên, bàn đôi trái nhìn trước/phải cúi; hàng xa thiếu chi tiết.",
        55: "Gần F54, không có evidence mới ở đầu/tay; giữ một đại diện.",
        59: "Bàn đơn cúi, bàn đôi phải quay nhẹ, trái chống tay; không suy hướng chỉ từ có sách.",
        66: "Bàn đơn cầm/nhìn sách, cặp gần đọc, giữa chống cằm; tay khó thấy giữ phone U.",
        75: "Người giữa sau cặp đầu dãy dang tay/ngẩng, bàn gần đọc; thử biến thể và kiểm người nền.",
        79: "Người giữa đưa tay gần mặt, bàn đơn mở sách, giáo viên đứng lên; không có phone rõ mới.",
    },
    "Y05": {
        1: "Khớp ảnh tham chiếu; hai bàn gần cúi, đầu dãy giữa nhìn phải; hàng xa nhỏ.",
        2: "Bàn phải gần ngẩng phải, hàng tường sau đổi tay; F48 nhìn trước rõ hơn.",
        5: "Bàn trái gần tay gần mặt, đầu vẫn cúi hơn dự kiến; không giữ looking P sau QA. Ghế sau phải úp đầu.",
        10: "Hai bàn gần cúi; đầu giữa tay che mặt, dãy tường chống tay; không suy hướng khi bị che.",
        14: "Bàn phải gần nghiêng trái, tay trải trang; bàn trái cúi; nghiêng nhẹ chưa đủ P.",
        17: "Bàn phải chống cằm/cúi, trái cúi; đầu giữa che mặt; ít evidence mới.",
        29: "Hai bàn gần cúi; đầu giữa cầm vật nhỏ trước miệng, không nhận dạng mobile; tường sau úp đầu.",
        30: "Gần F29, đầu giữa đổi góc; không lấy vật nhỏ cầm tay làm phone P.",
        33: "Đầu dãy giữa nhìn trước, vật nhỏ chưa rõ loại; giữ U/P nếu anchor trội; bàn gần cúi.",
        48: "Bàn phải gần nhìn lên trước rõ, hai tay trên bàn; đầu giữa cúi. Cặp với F1.",
        50: "Bàn phải nhìn phải, hai tay trên trang; trái cúi; không thêm cùng trạng thái.",
        55: "Bàn phải chống cằm nhìn bài, tường sau ngẩng; đầu giữa che mặt.",
        69: "Hai bàn gần cúi viết/đọc, đầu giữa chống tay, hàng sau ngẩng; không mobile rõ.",
        70: "Bàn phải quay phải, trái cúi; đầu giữa nhìn ngoài, tương đồng trạng thái đã chọn.",
        71: "Bàn phải nhìn trang, trái cúi; đầu giữa ngẩng với tay che; hàng xa không rõ hơn.",
        94: "Hai bàn gần cúi; đầu giữa viết nhưng vùng đầu/bàn lẫn người cạnh; chưa chọn thêm.",
    },
    "Y06": {
        1: "Cận người đọc, gile kính trái và gile chống cằm phải. Chữ dưới phải cần bỏ; vị trí khác ngoài khung/che.",
        3: "Pan phải: gile chống cằm, hai áo trắng sau và gile cuối lối đi; đầu tiền cảnh che phải, người đọc ngoài khung.",
        4: "Góc phải rộng, đầu tiền cảnh che giữa; hàng xa chồng lấn, người đọc ngoài khung.",
        12: "Khoác viền đỏ, gile chống cằm, hai áo trắng sau, gile lối đi và gile khoanh tay hiện; người đọc ngoài khung.",
        27: "Gile cuối lối đi rõ thân nhưng vật trên đùi mơ hồ và không có bàn riêng; blouse trắng trước phải che một phần.",
        29: "Khớp panel phải; người đọc và các đầu khoanh có mặt, người quay lưng che tiền cảnh; đầu khoanh che phần thân/tay.",
        32: "Pan cửa sổ: blouse chống cằm, gile sau, blouse tiền cảnh; người đọc ngoài khung. Nhắm mắt/cúi không tự N.",
        33: "Khớp panel trái; blouse trắng tiền cảnh nhìn trái, tay dưới bàn; blouse chống cằm thiếu trang bài rõ.",
        36: "Cận người đọc/khoác viền đỏ/gile chống cằm; đầu nơ che dưới phải; thử ROI tránh cạnh tranh.",
        60: "Góc ngang rộng, đầu tiền cảnh che người đọc; bên phải nhìn trái nhưng thiếu tay/context.",
        64: "Góc đối diện: sách người đọc rõ, gile trái và áo kính; phone bàn tiền cảnh không thuộc người đọc.",
        72: "Góc xa, người từng quay lưng nay quay ngang và tay chồng; mapping cá nhân chưa chắc, không ghép danh tính.",
        73: "Gần F72, cảnh rộng hơn, nhiều người chồng; không thêm frame gần trùng.",
        80: "Người đọc, gile kính trái và blouse chống cằm phải hiện; bàn che bởi đầu tiền cảnh; ưu tiên F1/F33.",
        95: "Cảnh xa từ sau: hai người quay lưng che người đọc, hàng sau nhỏ; không có geometry tốt hơn.",
    },
}

# Location-based descriptions, not biometric identities.
LOCATIONS = {
    "Y01": [
        "Tiền cảnh phải, áo viền cổ tay",
        "Blouse trắng tiền cảnh cửa sổ",
        "Áo trắng viết cạnh cửa sổ",
        "Tóc sáng bên trái dãy cửa sổ",
        "Áo tay sẫm chống cằm ở dãy cửa sổ",
        "Tóc dài hàng sau cửa sổ",
        "Blouse phối đen hàng sau cửa sổ",
        "Gile đen dãy tường",
        "Áo trắng cạnh gile đen",
        "Áo kem giữa trái",
        "Áo trắng giữa phải",
        "Áo trắng bàn sau cạnh tủ",
        "Tóc ngắn áo trắng dãy tường",
        "Gile nâu bàn sau",
        "Áo trắng bàn sau giữa",
        "Áo đen bàn sau (ngoài dấu)",
        "Áo khoác xám cuối dãy cửa sổ",
        "Nam viết tiền cảnh cạnh bìa xanh",
        "Áo khoác trắng tiền cảnh",
        "Polo viền đen dãy cửa sổ",
        "Người đeo kính cạnh polo viền đen",
    ],
    "Y02": ["Trái gần", "Trái giữa", "Trái xa đeo kính", "Phải xa", "Phải giữa", "Phải gần"],
    "Y03": [
        "Dãy tường gần nhất",
        "Áo vàng dãy tường",
        "Áo tối sau áo vàng",
        "Áo tối dãy tường hàng tiếp",
        "Áo xanh tiền cảnh giữa",
        "Áo xám sau áo xanh tiền cảnh",
        "Áo trắng tay sẫm bên phải áo xám",
        "Polo trắng giữa trái",
        "Áo xanh sau polo trắng",
        "Áo xanh hàng giữa phải",
        "Áo xanh xa cạnh cửa sổ",
        "Áo trắng đeo kính giữa trái",
        "Áo trắng sau vị trí đeo kính",
        "Áo trắng hàng xa trái giữa",
        "Áo xanh ngay sau vị trí đeo kính",
        "Áo xanh đeo kính hàng xa",
    ],
    "Y04": [
        "Bàn đơn gần nhất",
        "Bàn đôi gần bên phải",
        "Bàn đôi gần bên trái",
        "Hàng sau gần bên phải",
        "Hàng sau gần bên trái",
        "Hàng tiếp phía cửa sổ",
        "Giữa phía cửa sổ",
        "Bàn đầu dãy giữa bên phải",
        "Bàn đầu dãy giữa bên trái",
        "Bàn sau cặp giữa",
        "Hàng xa phía phải",
        "Hàng xa trung tâm",
        "Hàng trái giữa",
        "Đầu dãy trái",
    ],
    "Y05": [
        "Áo tối bàn trái gần",
        "Áo xanh đeo kính bàn phải gần",
        "Dãy tường sau trái",
        "Dãy tường sau phải",
        "Dãy tường hàng tiếp trái",
        "Dãy tường hàng tiếp phải",
        "Áo tím đầu dãy giữa",
        "Bên phải áo tím",
        "Hàng phải áo xám",
        "Xa bên phải",
        "Áo xanh sau dãy giữa",
        "Áo tối giữa phía sau",
        "Áo xanh giữa xa",
        "Áo tối cuối hàng phải",
        "Áo cổ vàng giữa xa",
        "Áo xanh bên phải cổ vàng",
    ],
    "Y06": [
        "Blouse trắng tiền cảnh panel trái",
        "Áo trắng đeo kính ở góc đối diện",
        "Gile đen đeo kính cạnh người đọc",
        "Người đọc sách xanh",
        "Gile chống cằm sau người đọc",
        "Khoác viền đỏ sau người đọc",
        "Áo trắng hàng cuối bên trái",
        "Áo trắng hàng cuối bên phải",
        "Gile đen cuối lối đi",
        "Gile khoanh tay giữa phải",
        "Đầu khoanh sau trái gile giữa phải",
        "Đầu khoanh sau phải gile giữa phải",
        "Blouse trắng chống cằm",
        "Gile đen sau blouse trắng",
        "Gile bàn trái góc đối diện, mapping chưa chắc",
    ],
}

SPECIAL = {
    "Y01-A02-F00008": "Mobile mặt kính/viền đen cạnh tay viết; đầu hướng giấy. Tay người sau ở mép không phải evidence của anchor.",
    "Y01-A06-F00102": "Mobile mặt kính, viền sáng trên giấy cạnh tay; đã bỏ phone của người phía sau khỏi ROI. Đầu hướng bài.",
    "Y01-A07-F00060": "Mobile mặt kính phản sáng và viền máy cạnh tay phải; nhìn vào giấy riêng.",
    "Y01-A10-F00038": "Mobile trắng mặt sau có cụm camera trên bàn trái; người áo kem cúi viết. Người đứng chỉ còn phần thân ở mép.",
    "Y01-A12-F00098": "Mobile mặt kính/viền trên bàn cạnh tay; đầu cúi sát sổ che mặt/đích nên looking U.",
    "Y01-A14-F00039": "Mobile viền sáng/mặt kính cạnh sổ riêng; người gile nâu viết trên trang.",
    "Y01-A14-F00098": "Mobile viền sáng/mặt kính trên bàn riêng; chống cằm nhìn trước ngoài trang.",
    "Y01-A15-F00039": "Mobile mặt kính trên sách phía dưới; người áo trắng nhìn tờ giấy đang cầm nên looking N.",
    "Y01-A21-F00197": "Mobile có cấu trúc mặt lưng/cụm camera trên giấy cạnh tay; đầu cúi viết. Tay người đứng ở mép trái không dùng cho attribution.",
    "Y01-A18-F00043": "Vật tối trên bìa xanh thiếu đặc trưng mobile ở input, sửa phone P dự kiến thành U; hướng viết vào giấy rõ.",
    "Y01-A01-F00128": "Đầu cúi vào own-paper; tay còn lại bị thân/người phía sau che nên phone U.",
    "Y03-A15-F00001": "Đầu hơi nghiêng nhưng vẫn hướng vùng giấy; sửa looking P dự kiến thành N. Tay/vật nhỏ nên phone U.",
    "Y06-A04-F00001-R02": "Đầu hướng sách xanh, hai tay giữ sách; absence trong vùng nhìn thấy theo ngoại lệ giấy che hoàn toàn. R02 bỏ chữ sát mép dưới.",
    "Y06-A04-F00064": "Góc cạnh, đầu hướng sách đang cầm; hai tay giữ trang, không có thiết bị mơ hồ còn lộ. Không gán phone bàn tiền cảnh cho người đọc.",
    "Y06-A06-F00036": "Nhìn sang trái ngoài bàn; bàn tay còn lại nằm dưới cánh tay/mép nguồn nên phone U.",
}


def save(name, obj):
    (P / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    notes = []
    for group, items in FRAME_NOTES.items():
        for frame, note in items.items():
            notes.append(
                {
                    "frame_id": f"{group}-F{frame:05}",
                    "reviewer": "agent-visual-draft",
                    "note": note,
                    "review_pass": "full-frame-native-board",
                    "scope": "Quan sát theo vị trí/bố cục, không nhận diện khuôn mặt; không là annotation detector đầy đủ.",
                }
            )
    save("frame-notes.json", notes)
    rows = json.loads((P / "selections.json").read_text(encoding="utf-8"))
    for row in rows:
        loc = LOCATIONS[row["group"]][int(row["anchor"][1:]) - 1]
        row["location_description"] = loc
        phone, looking = row["draft_states"]
        phone_reason = {
            "P": "Mobile nhận dạng được, gắn vùng bàn/tay của anchor; đã xem native/input.",
            "N": "Tay và vùng thao tác đủ quan sát absence; không mobile hoặc vật mơ hồ còn lộ.",
            "U": "Tay/vùng thao tác bị che hoặc vật nhỏ chưa phân loại/attribution chưa chắc; không đủ absence.",
        }[phone]
        looking_reason = {
            "P": "Hướng đầu/nhìn ra trước hoặc sang bên ngoài vùng bài riêng.",
            "N": "Hướng đầu về trang/sách/vùng thao tác riêng.",
            "U": "Hướng/đích nhìn bị che hoặc thiếu context, chưa đủ known target.",
        }[looking]
        row["draft_reason"] = (
            loc + ": " + SPECIAL.get(row["candidate_id"], phone_reason + " " + looking_reason)
        )
        if row["qa_status"] == "pass_draft":
            row["qa_note"] = (
                "Đã xem source, native crop và input 224; anchor chính trội, known target còn đủ bằng chứng. Nhãn đề xuất chờ owner review."
            )
        else:
            row["qa_note"] = (
                "Không đề xuất: source/native/input thiếu hướng nhìn chắc, che phần cần thiết hoặc người khác cạnh tranh anchor. Các state lưu là giả thuyết trước QA, không là nhãn được giữ."
            )
    exceptions = {
        "Y01-A19-F00067": "Crop đứng thiếu vùng bài riêng để diễn giải looking; chưa đủ known target.",
        "Y01-A12-F00052": "Crop đứng thiếu work context, tay sát mép; ưu tiên crop ngồi F98.",
        "Y04-A03-F00030": "Đầu vẫn nhìn ngoài trang; không giữ N dự kiến. Không thêm vì gần trạng thái F1.",
        "Y06-A09-F00027": "Crop ngồi ở lối đi thiếu bàn/bài riêng; vật trên đùi mơ hồ. Chưa đủ looking P.",
        "Y06-A05-F00001": "Mắt nhìn xuống nhưng đích chưa rõ; vật xám trên bàn chưa phân loại. Không đủ known target.",
        "Y06-A04-F00001": "Thay bằng R02 để bỏ chữ sát mép dưới, giữ đủ sách/tay.",
    }
    for row in rows:
        if row["candidate_id"] in exceptions:
            row["qa_note"] = exceptions[row["candidate_id"]]
        if row["group"] == "Y02" and row["qa_status"] == "withheld":
            row["qa_note"] = (
                "Hai mặt/thân cạnh tranh; thu hẹp mất tay/bài. Vị trí A01 dùng R02; A02/A05/A06 chưa có khung đạt trong batch này."
            )
    save("selections.json", rows)
    lineage = json.loads((P / "lineage-review.json").read_text(encoding="utf-8"))
    lineage.update(
        comparison_scope="115 frame mới so với inventory 536 frame audit ngày 16/10; chưa kiểm toàn bộ lịch sử V11, không mở test media.",
        assignment="Chưa gán split; cần review lineage trước release.",
        visual_findings=[
            {
                "group": "Y05",
                "prior_group": "G17",
                "evidence": "P03-G17-F00012 và Y05-F00048 đã xem; phòng/góc máy, cửa sổ, rèm, bàn giáo viên và bố cục rất gần; khác người/tư thế không chứng minh độc lập.",
                "decision": "Quarantine cùng scene-family tiềm năng trước split; chưa nghiệm thu group.",
            },
            {
                "groups": ["Y03", "Y05"],
                "evidence": "Bố cục lớp/góc máy có điểm tương đồng; chưa xác minh là cùng room/session.",
                "decision": "Cờ kiểm thêm, không tự gán independence hoặc group accepted.",
            },
        ],
    )
    save("lineage-review.json", lineage)
    print(f"UTF-8 observations: {len(notes)} frames, {len(rows)} trials")


if __name__ == "__main__":
    main()
