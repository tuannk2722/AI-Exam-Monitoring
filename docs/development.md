# Hướng dẫn phát triển repository

## 1. Đọc theo task và xác định thẩm quyền

Đọc [index](00-INDEX.md), [status](status.md) và TASK hiện hành, sau đó đúng contract/code và hồ sơ liên quan. Không đọc mọi report/archive. Spec quy định behavior; code chứng minh implementation; manifest/run/metrics/receipt là evidence đúng version; proposal không là approval. Quyết định owner đúng scope và pins được bảo toàn. Nếu mâu thuẫn, báo conflict, không sửa số liệu/labels/pins để hợp thức hóa mô tả.

## 2. Workflow

1. Đối chiếu user scope, Git/files/code, requirement và approval của đúng artifact; không chọn ID lớn nhất làm input mặc định.
2. Ghi TASK trước sửa theo [template](templates/task-template.md): đầu ra, quyền theo hành động, inputs/version, checks và lifecycle outputs.
3. Thực hiện tập trung; core ở src, variables trong config, notebook launcher. Thiếu quyết định scientific/architecture/schema thì chuẩn bị proposal và hỏi đúng phần; tiếp tục phần độc lập đã được phép.
4. Kiểm theo diff và consumer; software PASS không thay data/model acceptance.
5. Bàn giao kết quả và limitations ở đúng nơi theo §5. **Không thay đổi spec là kết quả bình thường nếu contract không đổi.** Chỉ cập nhật status nếu capability/input/proposal/blocker hiện hành thay đổi.
6. Dọn scratch sau bảo toàn evidence và kiểm dependencies. Stage/commit/push chỉ khi user yêu cầu; không stage chỉ để checker PASS.

## 3. Môi trường và commands hiện có

Python >=3.11,<3.13, CI 3.11; `.venv` local hiện đã có. Setup mới chỉ khi thiếu môi trường, không tạo thêm bản env/checkout cho mỗi task:

```powershell
py -3.11 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements/base.txt -r requirements/dev.txt
```

`requirements/base.txt` cài package editable, dev thêm Ruff/Mypy; `classifier-cpu.txt` cho synthetic classifier tests, `classifier-cpu-lock.txt` là closure Python 3.11 Windows CPU đã đo ở E001. Historical lock gồm torch 2.8.0+cpu/torchvision 0.23.0+cpu và exact dependencies; tái lập run phải dùng environment đã ghi, không gọi lock đó là universal Linux/Colab lock. Nhóm ML/DVC chỉ cài khi task dùng, không tự tải weights.

Các CLI đã có đều dưới prefix `ai_exam_monitoring`: `data.audit`, `data.overlay`, `data.validate_labels`, `data.image_similarity`; `training.train`, `training.evaluate`, `training.error_audit`; `inference.detect`; `common.history`. Kiểm flags bằng `--help`/code khi thực hiện. Không có training `dvc.yaml`, vì vậy không dùng `dvc repro` thay trainer CLI.

Colab/GPU vẫn là hướng tương lai được scope approve riêng: exact checkout → dependencies → auth từ secret → pull đúng versions có quyền → verify → smoke → canonical CLI → sync last/best/status. Notebook không thay logic, runtime kết thúc/OOM giữ trạng thái; đổi variables tạo run identity mới.

## 4. Kiểm tra theo phạm vi thay đổi

| Thay đổi | Checks cần làm |
|---|---|
| Chỉ spec/AGENTS/TASK | Nội dung/trạng thái/traceability, links và diff; checker nếu đổi index/cấu trúc; không ML suite hoặc hash mọi media |
| Python module/test | Ruff/type phần đổi và unit tests trực tiếp; mở rộng consumers khi đổi helper/schema hoặc có failure |
| Codec/loader/preprocess/loss | Tests masks/versions/rights/freeze/group, preprocessing geometry/modes, consumers training/evaluation; kiểm pins của version liên quan |
| Dataset/experiment config | Parse/schema/digest và approval đúng scope; smoke/rebuild chỉ nếu task cần và inputs đủ; không tự chạy training |
| Binary release/model | QA/checksum/rebuild/evaluation theo protocol được duyệt; không sửa accepted bytes vì refactor |
| Trước merge / thay đổi rộng | Full base và classifier nếu liên quan ML, lint/compile/checker/diff; không model/test inference thật chỉ để kiểm phần mềm |

Chạy một nhóm, ví dụ checker:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -p test_check_repo.py -q
.venv/Scripts/python.exe scripts/check_repo.py --require-git
```

Các lệnh đầy đủ khi phạm vi yêu cầu:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -q
.venv/Scripts/python.exe -m unittest discover -s tests -p 'test_training*.py' -q
.venv/Scripts/python.exe -m ruff check src tests scripts
.venv/Scripts/python.exe -m compileall -q src tests scripts
.venv/Scripts/python.exe scripts/check_repo.py --require-git
```

CI quality dùng base/dev, classifier job dùng Torch CPU/training + preservation fixtures. Base skip đúng tests cần Torch; không dataset/GPU/weights download. Commands/workflow là hướng dẫn thực thi; kết quả kiểm trong hồ sơ handoff không chứng minh task tương lai đã PASS.

Strict mypy là gate cho active source và repo checker: `.venv/Scripts/python.exe -m mypy src/ai_exam_monitoring scripts/check_repo.py`. Torchvision chưa có marker typed được phân tích bằng `follow_untyped_imports`, không tắt strict toàn project. Classifier CI cài dev dependencies và chạy gate này; lịch sử xử lý typing ở hồ sơ handoff.

`check_repo.py --require-git` kiểm required paths/index links, archive registry/pointer và Git index kể cả staged/force-added. Required files và source/tests/scripts/docs/config/requirements/CI mới phải nằm trong index; staged deletion không được lấp bằng untracked file cùng path. Archive pointer mới phải khai báo trong `archive/index.json`, path/MD5/size hợp lệ; binary ZIP vẫn bị chặn. Checker không là content secret scanner hoặc model-quality gate. ZIP mode thiếu Git chỉ kiểm cấu trúc; `--require-git` phải fail. Trước commit review staged diff và chạy checker; sau commit kiểm clean checkout không có local binaries để chứng minh source/spec đầy đủ.

## 5. Nơi ghi kết quả và quy tắc cập nhật

| Nội dung thay đổi | Nơi ghi | Khi nào sửa spec? |
|---|---|---|
| Requirement/semantics/schema/interface được duyệt | System/data/training contract; decision locator nếu thay đổi quan trọng | Có, cập nhật đúng contract và consumer |
| Bug fix/refactor giữ contract | Code/tests, TASK và PR/commit khi có | Không; sửa reference nếu API/cách dùng thay đổi |
| Experiment | `outputs/<run-id>` artifacts; `artifacts/reports/<run-id>` summary/analysis/evidence cần giữ; reports index | Không chỉ vì có metrics mới |
| Dataset release | `data/processed/<family>/<version>` card/manifest/coverage; report/approval/pointer theo release; reports index | Chỉ khi contract dữ liệu thay đổi |
| Research/audit | Hồ sơ theo source/snapshot hoặc câu hỏi trong `artifacts/reports`; có kết luận/limitations/evidence | Chỉ khi kết luận dẫn tới quy tắc được owner duyệt |
| Proposal | Hồ sơ thiết kế và config theo ID trong `configs/experiments` hoặc `configs/datasets` | Draft không thay contract Accepted |
| Capability/input được chọn/blocker/ưu tiên | [Status](status.md): thay nội dung hiện hành, dẫn tới evidence/proposal | Không chỉ vì tiến độ thay đổi |
| Setup/CLI/restore/process | Guide/reference/runbook tương ứng | Không phải thay đổi product spec |
| Backup/checks bàn giao | Receipt hoặc report vận hành khi cần giữ lâu dài | Không chép số tests/bytes vào spec/runbook |

Report theo **đối tượng nghiên cứu/release/run**, không bắt buộc một file mới cho mọi task. Tận dụng run/summary/README đã có; hồ sơ chưa seal có thể cập nhật, hồ sơ đã pin giữ nguyên và tạo addendum/revision riêng khi cần. Index chỉ giữ ID/purpose/status ngắn và locator; không chép bảng metrics. So sánh nhiều runs dùng report có cohorts/protocol rõ. Không đẩy mọi lịch sử sang một file tổng hợp mới.

Spec thay đổi theo contract; trạng thái thay thế thông tin cũ; hồ sơ lịch sử giữ version/date và không là backlog hiện hành. Chỉ nội dung đang cần thực hiện nằm trong proposal/status; “next” trong receipt lịch sử là ý định ở thời điểm receipt. README/index/AGENTS không giữ số liệu runs/releases. Không tự thêm trang/card chỉ để lặp output máy đã đủ rõ.

## 6. Storage và vòng đời

Git giữ source/spec/guide/config/metadata nhỏ; không media/model/checkpoint/env/cache/credentials. Raw bất biến, derivative ở interim/processed; release/model/config đã pin không mutate. DVC pointer không là binary backup; remote push đúng owner scope, không tự upload người thật.

| Output | Nơi lưu và xử lý |
|---|---|
| Scratch/preview/checkout | `outputs/_scratch/<task-id>`; kiểm không có dependency độc nhất hoặc accepted pin trước xóa |
| Batch review đang làm | `data/interim/<task-id>` với current pointer; revisions đã review/hash giữ khi còn dependency |
| Run/release/evidence | Canonical outputs/data và metadata report tương ứng; bảo toàn pins, provenance, scope |
| TASK | Một task hiện hành; thay khi task mới, không làm WORKLOG hoặc authority khoa học |
| Archive/backup | Registry/pointer/manifest có verification; snapshot mới có identity mới, không reseal bản cũ |

[Chính sách retention](storage.md) là nơi quy định giữ/nghỉ lưu, backup và xử lý thiếu input. [Operations](operations.md) chỉ dẫn thao tác restore khi task cần. Không tự chạy lại script cleanup/backup trong report lịch sử; chúng gắn với inventory và identity của đợt đó.

## 7. Trạng thái, traceability và kiểm tài liệu

Decision Draft/Proposed chưa approval; Accepted đúng scope; Superseded chỉ rõ bản thay và phần bị thay; Rejected không chọn. Run FINISHED chỉ hoàn tất kỹ thuật; model Continue/Rejected/Candidate/Selected là decision riêng. Dataset Accepted không tự cấp training/test; model Selected không tự nghiệm thu video/demo. Dùng literal thật của artifact, không đổi schema để khớp từ ngữ docs.

Khi bàn giao, kiểm: contract có thật sự đổi không; output đã ở đúng hồ sơ chưa; index/status có tìm được không; links/anchors/historical locators có đúng không; receipt/pins có giữ nguyên không. Luồng đọc thử: task → index/status → contract + input/proposal → evidence/code. Mỗi kết quả chỉ có một nơi chịu trách nhiệm; bản tóm tắt dẫn nguồn, không tạo approval song song.

Khi di chuyển tài liệu, kiểm mọi incoming references và pin dependencies trước sửa. Files đã pin giữ bytes, dùng locator Git/archive hoặc companion revision có tên riêng; không đổi config/approval để sửa một link chết. Tài liệu mới cần được Git giao đầy đủ khi user yêu cầu commit. `check_repo.py --require-git` với index thật sẽ báo file docs/config mới chưa stage: báo đúng trạng thái; có thể kiểm snapshot/index tạm để chuẩn bị, không gọi đó là Git đã staged/committed.
