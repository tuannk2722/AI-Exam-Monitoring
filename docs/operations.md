# Runbook lưu trữ và tái lập

Chỉ đọc khi task cần restore/reproduction/backup. Đây là hướng dẫn thao tác, không phải yêu cầu sản phẩm hoặc quyền mở lại test. [Reports index](../artifacts/reports/README.md) tìm evidence; [development](development.md) quy định lifecycle. Các lệnh theo version dưới đây chỉ áp dụng đúng historical identity; kiểm availability/pins trước chạy.

## Trước khi restore

Đọc [retention](storage.md#thiếu-input) và [availability](../artifacts/reports/storage-retention-20261016/availability.json). Registry/DVC pointer định danh, không chứng minh binary còn tồn tại. Recipes bên dưới chỉ dùng khi task cần và đủ inputs; không phải lệnh chạy lại lịch sử.

Hai backup hiện hành và receipt nằm trong availability. Chúng dùng `common.history`, đã kiểm restore, cùng ổ D; remote chưa xác minh. Không tự push/pull hoặc phục hồi để lấp payload đã chủ động nghỉ lưu.

### Inputs tối thiểu để dùng lại kết quả

| Nhu cầu | Inputs cần có | Cách kiểm / giới hạn |
|---|---|---|
| Đọc kết quả E001–E003 | `artifacts/reports/E00N/metrics.json`, hồ sơ baseline-review-20261011 | Không cần restore source hoặc chạy inference |
| Verify package v4/v6/v7 | Package đầy đủ + `checksums.sha256`, manifest/ledger/release/split/freeze | `integrity.verify_payload` + codec; không tự cấp test access |
| Verify loader v5 | Package v5 và v4; v5 release approval/preservation; ba pins membership/groups/proposal | Ba metadata dependencies còn trong Git; crops active V4/V5 đã nghỉ lưu. Chỉ verify loader khi đã có đủ package đúng pins |
| Evaluate/reproduce E001–E003 | Exact Git commits `45240ea` / `0825239` / `4e206a6`; configs/approvals; package v4/v5/v6; pretrained đúng weights SHA; run artifacts và environment của `run.json` | Original package-wide code identity; evaluator đòi output mới. Scope final test giữ nguyên, restore không là approval mở lại test |
| Rebuild v7 | Snapshot source trước cleanup, exact config v7, parent v6/source inputs, ledger/assignment/whole-family/rights/provenance/review pointer và dependencies chúng trỏ tới | Dùng restore recipe bên dưới trong workspace riêng; current builder đã đổi self-SHA nên không chạy để reseal |
| Tái dùng shortlist/review | docs/reference.md#data-tools mapping → Git module gốc/import closure → exact source/config pins | Read-only `git show` trước; chỉ thích nghi phần cần dùng cho task mới, có tests |

Thiếu path: kiểm active → `common.history list/show` đúng prefix → `git show <commit>:<path>` cho tracked text/code → backup được kiểm. Không dùng output của `git show` qua PowerShell text redirection để restore bytes có pin; dùng subprocess bytes và đối chiếu SHA trước ghi. Raw không có trong inventory/backup thì báo thiếu và reacquire đúng snapshot theo quyền, không đoán version. Restore không được ghi đè file khác content.

**Kết luận nghiên cứu/results được định tuyến từ artifacts/reports/README.md; decisions ở docs/decisions.md.** Chỉ vào archive khi cần original IDs/full evidence/source media/code/config bytes. Có thể lấy một file text hoặc khôi phục một nhánh; không bung 12.820 file vào active cho mỗi task.

Archive `archive/history-20261010.zip` có manifest original path/size/SHA, content dedup; không dùng Extract-All thông thường để tạo workspace. `common.history` hỗ trợ `list`, `show`, `verify`, `restore`; verify blobs/inventory/path và restore từ chối overwrite khác content. Index `archive/index.json` pin SHA/container/verification. ZIP 2,47 GB trong workspace là readonly hardlink với blob DVC cache: cùng một nội dung local, **không hai bản backup độc lập**; không sửa ZIP/cache trực tiếp. Bản copy riêng tại thư mục backup [handoff](../artifacts/reports/repository-handoff-20261011/README.md) không dùng hardlink.

Ví dụ tra đúng nhánh evidence, không đọc whole archive:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.common.history list archive/history-20261010.zip --prefix artifacts/reports/pilot-b-v6-source-research-20261007
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.common.history show archive/history-20261010.zip docs/data/fpi-scb-research-20261007.md
```

`show` kiểm file SHA/size và dành cho text nhỏ; binary/JSON lớn dùng restore. Windows có source filenames dài, dùng destination ngắn + extended path:

```powershell
$historyPin = (Get-Content -Raw -Encoding UTF8 archive/index.json | ConvertFrom-Json).bundles[0].sha256
$historyWorkspace = '\\?\' + (Join-Path (Get-Location).Path 'archive/restore')
.venv/Scripts/python.exe -m ai_exam_monitoring.common.history restore archive/history-20261010.zip --destination $historyWorkspace --prefix artifacts/reports/pilot-b-v6-source-research-20261007 --sha256 $historyPin
```

Restore chọn nhánh cho research rồi tạo derivative/version mới theo [data contract](data.md). Tái lập historical release/run cần dependency closure đủ original paths/source/config/approval/parent, không chỉ report một file. Builder v7 có **self-SHA pin**; evaluator/model run có package-wide code identity. Current source đã retire modules/refactor imports, nên **không dùng current source với hash cũ hoặc sửa pin cho qua**. Snapshot trong archive là source trước lượt active/archive; exact E001–E003 code dùng Git commit/environment trong run evidence (E001: `45240ea`, E002: `0825239`, E003: `4e206a6`) khi cần tái lập.

Ví dụ v7 integrity-only rebuild đã được kiểm byte-exact; chỉ chạy trong workspace riêng khi thực sự cần, output/cache chưa tồn tại:

```powershell
.venv/Scripts/python.exe -m ai_exam_monitoring.common.history restore archive/history-20261010.zip --destination $historyWorkspace --exclude data/processed/pilot-b/pilot-b-20261010-v7 --exclude outputs/pilot-b-v7-release-sources-20261010-r1 --sha256 $historyPin
$env:PYTHONPATH = $historyWorkspace + '\src'
.venv/Scripts/python.exe -X utf8 -m ai_exam_monitoring.data.v7_release_acceptance --workspace $historyWorkspace --config configs/datasets/pilot_b_release_v7.yaml
Remove-Item Env:PYTHONPATH
```

Đã verify archive, restore 10.617 paths và original v7 rebuild 883 file byte-exact; accepted packages/models giữ SHA. Đây là bằng chứng khả năng khôi phục, không yêu cầu rebuild mỗi task. Gỡ workspace restore sau dùng. Nếu mất ZIP nhưng DVC cache còn, `dvc checkout archive/history-20261010.zip.dvc` lấy lại; nếu mất cả binary/cache và chưa remote backup thì Git metadata không khôi phục media.

Cleanup đầu đã xóa unused acquisition/preview/cache/staging và source checkouts: ignored bytes đã xóa không nằm trong archive mới, không hứa restore toàn nguồn. Code/docs tracked lịch sử còn Git `ab34b32`; original cleanup receipt `outputs/cleanup-20261010.json.gz` trong archive, không là media backup. Kiểm manifest inventory/availability trước reuse audit data, không download version khác cùng tên để lấp missing pins.
