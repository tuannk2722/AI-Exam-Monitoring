# Experiment chỉ bổ sung dữ liệu — đề xuất cụ thể

Trạng thái: Draft, chưa chạy. Chỉ materialize config có payload pin khi package đủ điều kiện.

Đề xuất `E004-C345-W-H`: so với baseline `E004-RC1-W-H`, thay train 716 bằng 1.061 nếu toàn bộ 345 eligible, giữ đúng selection 71. Dùng lại head đã học từ E004-V9-LP epoch 10 (`learned-head.pt`, SHA `852498780ddf682f334eefbc62efc231f60187e100d8f8db7ca2bce887bb9a37`) và ImageNet ResNet18 SHA `f37072fd47e89c5e827621c5baffa7500819f7896bbacec160b1a16c560e07ec`. Không huấn luyện head warm mới bằng dữ liệu mới, để chỉ thay train membership.

Giữ nguyên recipe baseline: mở layer4 và head; seed 42, input 224 RGB letterbox bilinear/fill 124,116,104; batch 16; CPU 4 threads, workers 0; AdamW LR head 0,001/layer4 0,0001, weight decay 0,0001; BN eval; objective global-known-normalized minibatch BCE; uniform permutation/no drop; tối đa 50 epochs, patience 10, min_delta 0,0001; threshold 0,5; wall-time tối đa 7.200 giây cho run mới; diagnostics steps 15/30 giữ baseline.

Tăng số crop cũng tăng số updates mỗi epoch: 45 → 67. Đây là tác động của bổ sung dữ liệu theo cùng recipe/epoch policy, không là thí nghiệm equal-update. Giữ ghi rõ khi phân tích. Không tự đổi batch/epochs nếu hết budget hoặc OOM.

Baseline cached chỉ dùng sau kiểm pins và chứng minh code đổi chỉ ở schema/export/derived validation, còn đường transform/loss/model V1 giữ semantics. Code identity mới phải được ghi trong run mới; không đổi historical SHA. Nếu kiểm parity không đạt, dừng để chuẩn bị control mới thay vì tuyên bố matched.

Kết quả cần có train/selection masked BCE, AP và confusion từng target, cùng errors/family slices theo protocol hiện hành. Không tuning threshold mới hoặc dùng test/reserve. Báo cả số liệu tổng và ngoài CF-Q072; không loại family khó. Dataset mới 345 crop không tự chứng minh independence; M4 chưa kết luận. Kết quả research không tự Selected/promotion.

Sau owner chốt thiết kế: tạo exact config/readiness/protocol pins, smoke riêng với package mới, chạy vào output mới, reload và so sánh. Compute cho smoke giới hạn kiểm kỹ thuật; không dùng để chọn recipe. Không mở downstream hoặc final test từ approval research.
