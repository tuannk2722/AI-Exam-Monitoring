# D2 winner — owner review ngày 26/10/2026

Owner: “sau khi review toàn bộ frame thì D2 ko làm mất người và ko có crop trùng, chốt D2 winner. hãy thực hiện tiếp đi!”.

Chọn **D2, NMS IoU 0,30, conf 0,25**, giữ YOLOv8n/person-only/imgsz 640/max_det 100/CPU FP32. Nghiệm thu visual detector trên toàn bộ cohort 19 frame của diagnostic, theo xác nhận owner không mất người và không crop trùng. Supersede riêng trạng thái chưa chọn winner trong decision diagnostic; không sửa output/receipt/pins lịch sử.

Đây là nhận xét nghiệm thu batch của owner, không là bảng matching đã annotate hoặc phép đo precision/recall. Census/matching draft giữ nguyên; không tự điền unknown thành ground truth. Không ngoại suy thành bảo đảm cho mọi video hoặc nghiệm thu classifier/attribution.

Thực hiện tiếp bước crop/G0 đã mô tả trong proposal: giữ context-v1, G0 seed 20261023, preprocessing và calibration. Exact crop/source/input đã có được tái dùng prediction với provenance; crop thay đổi chạy G0 để review attribution/visibility. Chỉ cohort hiện có, không train, đổi classifier/ngưỡng, mở test, full-video rerun hoặc tracking/events. Media giữ deadline nguồn, không upload. Chuẩn bị revision runtime D2 riêng, bảo toàn config D0 cũ.
