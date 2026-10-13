# Model Inspector & Comparison Studio 👁️

Công cụ giao diện Web cục bộ dùng để kiểm tra trực quan và đối chiếu dự đoán của các checkpoint `best.pt` trên **bất kỳ ảnh crop nào**.

---

## 🌟 Tính năng nổi bật

1. **Kiểm tra ảnh bất kỳ:**
   - Kéo thả file ảnh (JPG, PNG, WEBP).
   - Hỗ trợ dán trực tiếp từ bộ nhớ tạm (`Ctrl + V`).
2. **Đối chiếu song song 2 Model (Compare Mode):**
   - So sánh trực tiếp giữa Model A và Model B trên cùng một ảnh.
   - Hiển thị tỷ lệ phần trăm tin cậy cho từng hành vi (`phone_use`, `looking_around`).
   - Đánh dấu trạng thái **Đồng thuận** hoặc **Bất đồng quan điểm** giữa 2 mô hình.
3. **Thanh trượt ngưỡng linh hoạt (Confidence Threshold):**
   - Tùy chỉnh ngưỡng từ `0.05` đến `0.95` (mặc định `0.50`).
   - Cập nhật quyết định phát hiện tức thì mà không cần nạp lại mô hình.
4. **Xem ảnh tiền xử lý (Input Model View):**
   - Hiển thị ảnh gốc cạnh bên ảnh đã qua tiền xử lý letterbox $224 \times 224$ (đúng padding và màu nền mà mô hình thật sự nhìn thấy).
5. **Tự động nhận diện mọi Checkpoint:**
   - Quét toàn bộ thư mục `outputs/` để tìm các file `best.pt` và `last.pt`.
   - Hỗ trợ cả mô hình đầy đủ (E004+) lẫn mô hình chỉ lưu head (E001–E003).

---

## 🚀 Cách sử dụng

### 1. Khởi động giao diện Web
Từ thư mục gốc dự án, chạy lệnh:
```powershell
python inspect_model.py
```
*(Trình duyệt mặc định sẽ tự động mở tại địa chỉ `http://127.0.0.1:8501`)*

### 2. Quy trình làm việc khi phát hành phiên bản mới (Release E-model)
Do công cụ này nằm trên nhánh riêng `tools/model-inspector`:
1. Sau khi huấn luyện xong một phiên bản thực nghiệm mới ở nhánh khác:
   ```powershell
   git checkout tools/model-inspector
   ```
2. Chạy ứng dụng kiểm định:
   ```powershell
   python inspect_model.py
   ```
   *(Thư mục `outputs/` không bị Git theo dõi nên toàn bộ checkpoint vừa train xong vẫn giữ nguyên vẹn để nạp vào giao diện).*

