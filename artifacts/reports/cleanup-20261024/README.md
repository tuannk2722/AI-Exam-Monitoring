# Cleanup sau E007 — 24/10/2026

Owner yêu cầu dọn sâu tài sản cũ không còn phục vụ nghiên cứu và commit. Phạm vi này thay riêng quyết định giữ payload lịch sử của các đợt trước đối với exact paths trong [manifest](cleanup-manifest.json); không đổi labels/splits/metrics, không sửa pins hoặc source E007 đã chạy.

Đã xóa **8.971 file / 10.693.617.941 bytes** (9,959 GiB logical). Dung lượng trống ổ D tăng **8.239.742.976 bytes** (7,674 GiB) trong lượt apply; số đo toàn ổ có thể chịu ảnh hưởng tiến trình khác. Khác biệt chủ yếu do workspace archive và một DVC blob là hardlink cùng nội dung. Không gọi dung lượng đếm lặp là dung lượng đĩa đã thu hồi.

Workspace giảm từ **23,692 GiB xuống khoảng 13,748 GiB**; [kiểm sau cleanup](verification.json) xác nhận **21.177 protected files giữ nguyên SHA/size** và đủ 8.971 target đã vắng mặt. Phần còn lại chủ yếu là archive nguồn 5,54 GiB, môi trường Python 3,45 GiB, data/nguồn 3,42 GiB và outputs hiện hành 1,11 GiB. Các con số là snapshot trước Git commit, không tính Downloads ngoài workspace.

## Giữ và nghỉ lưu

- Giữ V13 đầy đủ, source-inputs và bundle rebuild V13, raw/nguồn độc nhất phục vụ recrop/QA, các archive nguồn hiện có và môi trường Python đang dùng.
- Giữ ba `best.pt` D1 và ba `best.pt` R0 của E007; giữ metrics, predictions, histories, configs, approvals, source/weights/license pins và evidence của mọi run.
- Nghỉ lưu checkpoint/feature cache E001–E006 đã superseded; E007 FINISHED bỏ last/resume và model của smoke/nhánh không được chọn. Original E007 trên private Drive là locator khôi phục, không sửa checksums để che file nghỉ lưu.
- Nghỉ lưu crops của các package lịch sử đã thay bởi V13; giữ metadata và source/archive. Package chỉ còn metadata không còn là package runnable đầy đủ. Không tự restore hoặc dựng ảnh khác để vượt loader guard.
- Ảnh interim chỉ bỏ khi SHA trùng một file giữ lại; `restore_from` ghi exact locator. Cache công cụ, source extraction DINO, scratch và bundle chuyển Colab có thể nghỉ lưu sau khi bảo toàn evidence.

Nguồn sự thật là [manifest](cleanup-manifest.json), [receipt apply](cleanup-result.json) và [protected snapshot](protected-before.json). Script [apply-cleanup.ps1](apply-cleanup.ps1) là migration một lần, kiểm absolute paths/size/hash trước xóa và không ghi đè receipt. Không chạy lại sau completion.

Script audit E007 đã copy nguyên bytes vào [e007-cloud-audit.py](e007-cloud-audit.py), giữ SHA trong `cloud-import-receipt.json`; original scratch có thể nghỉ lưu. Script này là evidence một lần, không là lệnh chạy lại sau retirement vì kiểm tất cả checkpoint cũ sẽ thiếu payload theo chủ đích.

## Giới hạn và phục hồi

Đọc availability tại đây trước các report/pins lịch sử. DVC pointer không chứng minh cache hoặc remote backup còn đủ. Không xóa raw hoặc archive độc nhất chỉ để giảm con số dung lượng. Giữ source API/test lịch sử đang là dependency của trainer/loader E007; cleanup không refactor thuật toán đã freeze. Không upload/purchase/train/inference/test trong task này.

Downloads nằm ngoài workspace và được giữ nguyên. Source/metadata/results vào Git; media/checkpoints/archive/env/cache không stage. Backup cùng ổ không chống hỏng ổ; E007 cloud đã có bản private được tải và kiểm trước cleanup.

Các file cache/scratch đã xóa hết; automatic approval review chặn riêng thao tác xóa cây thư mục rỗng với “blocked by policy”. Giữ các thư mục rỗng, không bypass. Hai source files E007 có dòng trắng cuối file nằm trong code hash; Git attributes miễn riêng lỗi blank-at-eof để giữ nguyên bytes, không tắt lint hoặc đổi algorithm.

Kiểm phần mềm trước retirement: **210 tests PASS**, Ruff PASS, strict mypy PASS 55 source files; [receipt](software-checks.json). Source/model acceptance là hai phạm vi khác nhau. Không train lại để kiểm cleanup.
