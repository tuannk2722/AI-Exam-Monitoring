# CLEANUP-COMMIT-20261106 — Dọn và commit hồ sơ crop/V15

- Trạng thái: hoàn tất rà soát và chuẩn bị commit local theo yêu cầu owner; phần xóa cache bị automatic approval review chặn. Không push.

## Yêu cầu và hiện trạng
- Đã đọc AGENTS, index/status, development, storage và task template; đối chiếu Git và hồ sơ crop/V15 thực tế.
- HEAD `b915c08`; có 11 file report crop ngày 05/11 đã staged từ trước, report/config V15 cùng docs chưa stage. Không có thay đổi active source.
- Scratch `outputs/_scratch/dataset-merge-20261106` hiện không tồn tại. Receipt trước ghi lần xóa bị chặn; giữ nguyên receipt lịch sử, chỉ bổ sung trạng thái quan sát hiện tại, không nhận đã thực hiện xóa.

## Quyết định và inputs
- Phạm vi: hoàn chỉnh bàn giao crop ngày 05/11 và `pilot-b-20261106-v15`, cleanup phần tạm không còn cần thiết và commit source/docs/config/metadata liên quan.
- Giữ raw, crop/frame/gallery hiện hành, dataset/model và dependencies. Config/receipt/worksheet đã pin không sửa bytes hoặc reseal release. Không train, inference, upload hoặc push.
- Inputs và quyết định nhãn/split: `artifacts/reports/dataset-merge-20261106/README.md`, `owner-direction.json`, `package-pointers.json` và release V15.

## Outputs và vòng đời
- Giữ snapshot worksheet đã thực thi trong report làm evidence; không biến thành API production hoặc chạy lại lên output đã tồn tại.
- Dọn nhận định bàn giao đã lỗi thời trong README chưa seal; bổ sung checks/cleanup hiện tại trong hồ sơ cùng release, giữ receipts cũ.
- Chỉ stage paths đã inspect; không media/model/cache/env/credentials. Commit local, không push.
- Bổ sung `.gitattributes` bảo toàn bytes config V15 qua checkout Windows/Linux, theo convention V11–V14; không đổi bytes config.

## Contract impact và checks
- Không đổi contract — không sửa spec. Không đổi membership/nhãn/split/config hoặc dataset bytes.
- Kiểm pins/dependencies liên quan, JSON/syntax/links, Ruff active source, type check và regression tests đúng scope; kiểm staged diff và `check_repo.py --require-git` trước commit.
- Không cần train/smoke hoặc rebuild dataset vì cleanup metadata; software checks không thay data/model acceptance.

## Checkpoint và bàn giao
- Scratch task dữ liệu không còn từ lúc kiểm đầu. Đã lập manifest cho 172 file cache / 49.219.300 bytes; lệnh PowerShell xóa đúng cache bị từ chối `blocked by policy`, cache giữ nguyên, không thử phương thức khác.
- PASS: 73 tests liên quan, Ruff active source, strict Mypy 92 files, 23 referenced pins và 8 tooling pins, JSON/syntax, 368 gallery cards / 736 links và source roots. Không đổi active source, nhãn/split hoặc payload dataset.
- Đã stage và inspect hồ sơ crop ngày 05/11, V15, config và docs; checker `--require-git` không lỗi, staged diff check PASS. Kiểm bytes trong index và checkout filters trước commit; không cần dataset rebuild, train hoặc full ML suite.
- Bàn giao tại `artifacts/reports/dataset-merge-20261106/README.md` và `cleanup-commit-validation.json`. Giữ snapshots/receipts đã pin, ghi giới hạn cleanup rõ ràng; tiếp theo chỉ thực hiện commit local và kiểm Git status.
