# E004 — Vì sao chưa cải thiện và hướng tiến tới promotion

Ngày 14/10/2026. Nghiên cứu từ artifacts E001–E004, release V9 và source hiện hành; không training, inference mới hoặc mở test/reserve. Đây là phân tích và đề xuất, không phải approval chạy experiment hoặc nghiệm thu model. Giữ nguyên các snapshots đã pin.

**Kết luận:** E004-L4 học train rất mạnh nhưng không tổng quát hóa sang selection mới. Dữ liệu được review kỹ đã cải thiện độ tin cậy nhãn/provenance, nhưng không bảo đảm số tình huống độc lập, tín hiệu thị giác ở input 224 hoặc coverage đúng domain. Chưa phát hiện bug triển khai giải thích thất bại trong phạm vi đã kiểm. Recipe thích nghi quá dễ ghi nhớ train và chênh lệch nguồn/cohort là các hướng điều tra ưu tiên; không có bằng chứng chỉ cần tăng epochs hoặc đổi threshold là đủ.

## 1. Bốn vòng không phải bốn lần fine-tune nối tiếp

| Experiment | Train / tập chọn epoch | Phần học | BCE / macro AP trên tập chọn epoch |
|---|---|---|---|
| E001, V4 | 60 / 13 | Head mới, ResNet18 frozen | 0,54773 / 0,92730 |
| E002, V5 | 80 / 13 | Head mới, ResNet18 frozen | 0,63336 / 0,98087 |
| E003, V6 | 317 / 50 | Head mới, ResNet18 frozen | 0,61078 / 0,78781 |
| E004-V9-LP | 716 / 71 | Matched frozen control | 0,67785 / 0,57537 |
| E004-V9-L4 | 716 / 71 | Head và layer4 | 0,70932 / 0,54123 |

E001–E003 không tiếp tục cải thiện backbone từ checkpoint vòng trước. E004-L4 cũng khởi đầu từ ImageNet và shared random head, không từ head LP đã học. LP/L4 có cùng input, order và initialization để kiểm riêng tác động mở layer4. Chỉ có một seed và một recipe L4, chưa phải tìm kiếm nhiều cách thích nghi.

E001/E002 dùng cùng val 13; E003 đổi thành 50; E004 dùng selection mới 71. Không ghép các scalar thành bằng chứng chất lượng giảm liên tục. Val 13 chỉ có phone 7 P/1 N và looking 3 P/3 N; macro AP cao ở đây không chứng minh khả năng dùng thực tế. E001 looking recall bằng 0 tại threshold 0,5. Nguồn: [baseline review](../baseline-review-20261011/README.md), metrics gốc [E001](../E001/metrics.json), [E002](../E002/metrics.json), [E003](../E003/metrics.json), [E004](../E004-v9-execution-20261013/matched-results.json).

## 2. Nguyên nhân và mức độ chắc chắn

### Đã xác nhận: L4 overfit nhanh, không phải không học được train

| Epoch L4 | Train BCE | Selection BCE |
|---|---:|---:|
| 1, checkpoint tốt nhất | 0,48062 | 0,70932 |
| 3 | 0,11341 | 0,88164 |
| 5 | 0,00807 | 1,56633 |
| 11 | 0,000179 | 2,37671 |

Nguồn trực tiếp: [history L4](../../../outputs/E004-V9-L4/history.json). LP cũng có khoảng cách tại best epoch 10: train 0,46292, selection 0,67785. Train thêm theo recipe cũ không có cơ sở khắc phục; early stopping đã giữ epoch 1 của L4 đúng rule, không lấy epoch cuối thất bại để báo cáo.

Recipe: 224, batch 16, AdamW, LR head 0,001/layer4 0,0001, weight decay 0,0001, BN eval, không augmentation, không scheduler, không warm-up head. Với 716 mẫu, mỗi epoch có 45 optimizer steps; epoch 1 đã là 45 updates. Không có đánh giá epoch 0/sub-epoch nên chưa biết có cửa sổ tốt hơn trước checkpoint đầu. Đây là khoảng trống chẩn đoán, chưa phải bug hoặc bằng chứng LR cụ thể nào sẽ tốt hơn.

**Giả thuyết:** mở layer4 cùng random head, nhiều capacity so với tình huống hữu ích, thiếu regularization và sampling theo ảnh khiến model ghi nhớ các tín hiệu của train. Cần ablation để quy trách nhiệm riêng cho LR, initialization, augmentation hoặc nguồn; history không chứng minh riêng một cơ chế.

### Đã xác nhận: kết quả phụ thuộc mạnh cohort; domain shift là giả thuyết có bằng chứng hỗ trợ

Trên diagnostic49, L4 tốt hơn LP: BCE 0,57700 so 0,62270, macro AP 0,82472 so 0,75955. Trên selection71, chiều cải thiện đảo ngược. Điều này phù hợp với việc học hữu ích cho các nguồn cũ nhưng không chuyển tốt sang nhóm mới; chưa phải thí nghiệm nhân quả xác nhận domain shift.

Cached predictions cho thấy train có 14 source IDs, selection có 3. Hai source IDs xuất hiện ở selection là consolidated-frames và pexels chỉ có tổng 14/716 mẫu train; selection còn có studentclassroombehavior. Source ID là provenance, không phải chứng minh domain/camera độc lập. Train có 605/716 work-context unknown; không được diễn giải 605 ảnh này là sai nhãn hay chắc chắn ngoài domain.

Selection có 10 quarantine families, riêng CF-Q072 chiếm 45/71 (63,4%). Điều này làm 71 crop không tương đương 71 tình huống độc lập. Tuy vậy, khó khăn không chỉ nằm ở family lớn: ngoài CF-Q072, L4 phone recall là 1/8, looking 0/11; LP là 2/8 và 4/11. Không đề xuất loại family khó để cải thiện số đo. Số này là diagnostic hậu nghiệm, không M4 hoặc kiểm định độc lập.

### Đã xác nhận: nhiều version/review không tương đương nhiều supervision mới

V7 có 689 train, V8/V9 có 716: tăng 27 (3,9%) so V7. V9 bổ sung/hợp nhất quản lý nhiều records, nhưng 71 development và 199 reserve không được dùng optimizer. Việc giữ chúng ngoài train là đúng vai trò đánh giá. Trong 308 anchors review, 27 đã là train trong V8; các anchors còn lại gồm development, reserve, 4 candidates và 7 U/U. Không cộng 308 thành train mới.

V9 train có phone 247 P/193 N/276 U; looking 213 P/297 N/206 U. Chỉ 234/716 (32,7%) biết cả hai target; 482 mẫu chỉ giám sát một target. Unknown được mask đúng. Đây là giới hạn mật độ supervision, không yêu cầu ép nhãn còn thiếu. So với E003, train thực sự đã tăng đáng kể; không phủ nhận công sức thu thập. Nhưng số lượng alone không xác nhận targeted coverage hoặc generalization.

Nguồn: [V9 consolidation](../E004-v9-consolidation-20261013/README.md), [support snapshot](../E004-v9-execution-20261013/cohort-support.json), [data research](../data-research-20261011/README.md). Counts unaccepted-family trong support snapshot là trước owner acceptance; không dùng chúng để phủ nhận approval cuối ngày 13/10.

### Có bằng chứng lịch sử, chưa định lượng lại toàn V9: evidence nhỏ và attribution khó

Audit E003 ghi 6/8 phone FN val là desk-phone, 6/8 visually small; 7/8 bị downsample tại 224. Looking FN có head-side/turn/crowded và thiếu chi tiết. Target yêu cầu nhận điện thoại thuộc đúng anchor hoặc nhìn ngoài vùng bài, không chỉ nhận người/quay đầu. Context crop chứa nhiều người có thể làm bài toán attribution khó với global pooled classifier; chưa có ablation chứng minh đây là nguyên nhân chính E004.

Review đúng ảnh gốc không bảo đảm chi tiết vẫn đủ sau letterbox 224. Các lần review/recrop mới có giá trị, nhưng không có bằng chứng ở task này rằng mọi FN hiện tại mất evidence tại 224. Chưa xem lại từng ảnh E004; cần review có mục tiêu source → native crop → exact input, giữ nhãn accepted trừ khi có quy trình revision riêng. Tăng resolution không khôi phục chi tiết vốn không tồn tại ở ảnh gốc.

## 3. Có phải code sai hoặc threshold sai?

Rà trực tiếp các đường [model](../../../src/ai_exam_monitoring/training/adaptation_model.py), [trainer](../../../src/ai_exam_monitoring/training/adaptation_train.py), [loader](../../../src/ai_exam_monitoring/training/adaptation_data.py), [preprocess](../../../src/ai_exam_monitoring/training/data.py), [loss](../../../src/ai_exam_monitoring/training/adaptation_metrics.py), [metrics](../../../src/ai_exam_monitoring/training/metrics.py), [reload](../../../src/ai_exam_monitoring/training/adaptation_evaluate.py):

- Targets giữ đúng order, unknown không thành negative trong loss/metrics; BCE dùng logits, sigmoid dùng báo scores.
- Train và evaluation dùng cùng RGB/letterbox/normalization. Không thấy train/eval transform mismatch.
- L4 và head có optimizer groups/LR riêng; prefix đóng băng, BN buffers eval theo recipe. Không thấy quên backward/step hoặc vô tình freeze L4.
- Best model deepcopy theo minimum selection BCE; diagnostic không tham gia chọn epoch; reload full state đúng bundle.
- Guard kiểm ID/source/crop/family giữa train và development. Giới hạn independence được ghi waiver, không tự biến family IDs thành độc lập đã chứng minh.

Code identity hiện tại khớp cả hai runs. Kiểm SHA của history/config/metrics/run và 5 cached prediction cohorts mỗi run khớp checksums. Tính lại confusion/AP/BCE bằng Python standard library, không gọi implementation metric: confusion khớp chính xác, AP và BCE sai khác dưới 1e-6. Đây là kiểm độc lập phép tính trên scores; không chứng minh ground truth đúng từng ảnh. Reload parity bằng 0 là evidence execution trước đó, không chạy lại inference trong task này.

Phân tích tất cả điểm phân loại có thể có từ **scores selection đã lưu** cho biết không target nào của LP/L4 có threshold đạt đồng thời precision ≥85%, recall ≥80%, FPR ≤10%. Không chọn threshold mới hoặc đổi operating point.

| Model / target | FPR nhỏ nhất khi recall ≥80% | Precision lớn nhất khi recall ≥80% |
|---|---:|---:|
| LP phone | 60,6% | 52,4% |
| LP looking | 50,0% | 54,8% |
| L4 phone | 57,6% | 54,2% |
| L4 looking | 60,5% | 50,0% |

Các extrema tính riêng trên mọi threshold tại score duy nhất; không hàm ý chúng luôn ở cùng threshold. Đây là kiểm khả năng đạt gate trên development hậu nghiệm, không estimate holdout. AP mỗi target hiện cũng dưới 0,8; đổi threshold không đổi ranking/AP. Vì vậy vấn đề vượt quá calibration tại 0,5. Evidence có input hashes và kết quả ở [cached-score-audit.json](cached-score-audit.json).

**Kết luận về code:** chưa phát hiện lỗi ở các đường đã rà và kiểm; không tuyên bố toàn repository không có bug. Một recipe chạy đúng vẫn có thể không phù hợp. Chưa có cơ sở sửa production code hoặc làm lại dataset chỉ vì nghi pipeline sai.

## 4. Khoảng cách tới promotion

[Protocol frozen](../../../configs/experiments/E004-v9-execution-20261013/protocol.json) pin [metrics policy](../../../configs/experiments/E004-v9-execution-20261013/protocol-proposal.json), được [owner approval](../E004-v9-execution-20261013/owner-execution-approval.json) chấp thuận dù proposal giữ status lịch sử pending.

M1 yêu cầu precision ≥0,85, recall ≥0,80, FPR ≤0,10 cho mỗi target; M2 AP mỗi target ≥0,80, macro ≥0,85; M3 BCE ≤0,9 constant. Trên selection hiện tại M3 tương ứng khoảng 0,62765, trong khi LP 0,67785/L4 0,70932. Đây là khoảng cách development, chưa phải final-test gate.

M4 vẫn INCONCLUSIVE vì thiếu accepted context slice enrollment; M5 intervals chỉ độ nhạy theo quarantine grouping, không independent confidence claim. M6 benchmark đã PASS ở scope crop CPU. M7 gồm rights/bundle/evidence/owner decision. Waiver support/independence cho phép nghiên cứu, không biến chất lượng chưa đạt thành Selected; không yêu cầu quay lại bù quota cũ đã miễn.

Promotion classifier trên reviewed crops khác nghiệm thu pipeline video. Detector → automatic context crop → classifier, tracking/events/risk còn công việc riêng theo system. Không gộp thời gian hoàn thiện hệ thống vào thời gian cải thiện classifier.

## 5. Hướng tiếp theo đề xuất, chưa phải config được duyệt

1. **Audit lỗi có giới hạn, trước khi thu thêm đại trà.** Dùng FN/FP LP/L4 và mẫu đúng đối chứng theo family; draft bảng evidence native/224, anchor attribution, phone nhỏ/desk/held/occluded, own-workarea và primary/auxiliary. Agent/công cụ shortlist và chuẩn bị bảng; owner review batch/ngoại lệ. Không yêu cầu review lại toàn bộ dataset. Đầu ra cần phân biệt: evidence mất ở resize, evidence gốc thiếu, model sai dù evidence rõ, hoặc nhãn cần revision.
2. **Kiểm recipe trước bằng ablation nhỏ trên train/development hiện có.** Ưu tiên hypothesis LP head warm-start rồi mở layer4; so với khởi đầu random head dưới cùng recipe/cohorts để tách tác động initialization. Sau đó mới ablate LR layer4 thấp hơn hoặc regularization/augmentation giữ đúng semantics. Đo epoch 0 và sớm trong epoch đầu để không bỏ lỡ cửa sổ adaptation. Không đổi đồng thời data/resolution/optimizer rồi quy gain cho một yếu tố. Candidate có gain cần kiểm độ ổn định qua seeds trong budget đã duyệt, không săn best seed.
3. **Chỉ mở nhánh resolution/attribution nếu audit ủng hộ.** Nếu evidence có ở crop gốc nhưng mất ở 224, đề xuất matched resolution ablation và benchmark lại latency. Nếu nhiều người trong context gây nhầm anchor, đề xuất cách biểu diễn anchor/context trước, vì đây là thay đổi input/architecture cần quyết định. Không mặc định bỏ context hoặc chuyển temporal model ngoài scope MVP.
4. **Thu thêm đúng thiếu hụt nếu recipe không đủ.** Ưu tiên tình huống mục tiêu khác family/camera có evidence rõ, positives và hard negatives tương ứng, không thêm nhiều biến thể gần trùng chỉ để tăng count. Role/quarantine/freeze chốt trước; không kéo reserve199 hoặc selection hiện tại sang train để cải thiện số đo. Chưa có bằng chứng định ra một con số ảnh tối thiểu sẽ bảo đảm thành công.
5. **Chỉ chuẩn bị final-test sau development đủ thuyết phục.** Chốt candidate/operating point/slices/use scope và quyền truy cập đúng version; giữ reserve đóng đến đó. Hạn chế số lượt thử trên selection71 để tránh overfit quyết định vào chính tập nhỏ này. Không mở holdout để tìm hướng sửa model.

LP warm-start có cơ sở nghiên cứu từ [Kumar và cộng sự, ICLR 2022](https://arxiv.org/abs/2202.10054): fine-tuning cùng random head có thể làm biến dạng pretrained features dưới distribution shift; LP rồi FT là một hướng giảm vấn đề. Nghiên cứu đó không chứng minh E004 cùng cơ chế, và full FT trong paper không đồng nhất layer4 FT ở đây; đề xuất vẫn phải được kiểm bằng ablation local.

**Điểm dừng:** nếu recipe mới giảm train loss nhưng selection ranking/BCE không cải thiện ổn định hoặc chỉ tốt một family, không kéo dài epochs. Nếu audit cho thấy evidence nguồn thiếu, dừng nhánh tăng resolution. Nếu gain biến mất qua seeds/groups, chưa freeze candidate. Mỗi nhánh nên trả lời một câu hỏi, không tạo vòng version/train mới vô hạn.

## 6. Ước lượng công sức có điều kiện

Đây là ước lượng lập kế hoạch của audit, không số đo lịch sử hoặc cam kết promotion. Giả định một người làm chính, công cụ chuẩn bị batch, inputs hiện có truy cập được, ngày công khoảng 6–8 giờ tập trung; chờ quyền/nguồn/review có thể tăng thời gian lịch.

| Công việc tương lai | Công sức dự kiến | Điều kiện / đầu ra |
|---|---|---|
| Audit thị giác có mục tiêu và chốt 1–2 hypothesis | 1–2 ngày công | Evidence matrix từ development, không review cả corpus |
| Implement/fixture + vài ablation recipe hữu hạn + phân tích | 2–4 ngày công | Scope/config/compute được duyệt; quyết định recipe có cứu được không |
| Nếu cần bổ sung tình huống mới | Thêm 1–3 tuần lịch | Có nguồn đúng use scope, group/context và batch review; thiếu nguồn có thể lâu hơn |
| Candidate ổn định, freeze/protocol/slices, evaluation được duyệt | 2–5 ngày công | Chỉ bắt đầu khi development đạt; không bảo đảm final-test PASS |

Mốc thực tế nên cam kết là **sau khoảng 3–6 ngày công có câu trả lời rõ hơn về nhánh recipe hay nhánh data/input**, không cam kết đã promotion. Nếu recipe đủ, có thể tiến tới candidate trong khoảng 1–2 tuần làm việc; nếu phải thu dữ liệu, khoảng 3–6 tuần lịch hoặc hơn là kịch bản lập kế hoạch, không dự báo xác suất thành công. Không có dữ liệu learning curve/scaling đủ để hứa còn đúng bao nhiêu vòng train.

Hai matched runs thực tế mất 1.679,97 + 1.146,33 giây, khoảng 47,1 phút tổng thời gian recorded run; gồm công việc bên trong trainer/reporting, không toàn bộ chuẩn bị/smoke/evaluation/human review. Vì vậy hiện nút thắt công sức chủ yếu là thiết kế thí nghiệm, kiểm evidence và diversity, không số giờ train. Recipe mới/resolution mới hoặc nhiều seeds có thể đổi compute đáng kể; cần đo thay vì suy tuyến tính từ hai runs này.

## 7. Kiểm và giới hạn bàn giao

Cached metric audit dùng 5 cohorts có sẵn mỗi run (train, selection, diagnostic49, comparator48, added35); không cộng diagnostic subsets chồng nhau. Independent BCE tính mean Bernoulli cross-entropy trên known mỗi target rồi mean hai target; AP nhóm equal scores và cộng precision theo delta recall. Threshold feasibility xét mọi unique score; trạng thái all-negative không thể đạt recall ≥0,8. Không dùng sklearn hay cùng metric implementation để xác nhận chính nó.

Đã chạy `.venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -p test_training_adaptation.py -q`: 16 tests PASS trong 58,554 giây, synthetic fixtures; không train/inference model thật. Không đổi source/config/spec/accepted artifacts; không commit/upload. Phạm vi chưa làm: review thị giác mới toàn FN E004, ablation nhân quả, multi-seed, inference hoặc final-test. Các phần này không bị gọi là đã xác nhận chỉ dựa vào report cũ.
