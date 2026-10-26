# Đối chứng D2 / YOLOv8s / YOLOv10s — chuẩn bị census và variables

Owner đã duyệt hướng nghiên cứu và yêu cầu thực hiện đến hoàn tất. [proposal.yaml](proposal.yaml) cụ thể hóa variables mới; chưa là run approval số. D2/G0/labels giữ nguyên. Không huấn luyện hoặc dùng V14 làm detector dataset.

## Bước 1: census

[Gallery 19 frame](../../../outputs/runtime-d2-census-review-20261026/index.html) và [manifest](../../../outputs/runtime-d2-census-review-20261026/census-draft.json) dựng từ 342 D2 anchors, chỉ gộp exact C01/C02/P04/P06 đã accepted => 338 nhóm draft. Không gọi đây là 338 người thật. 4 different và 4 keeper được giữ. Các nhóm riêng chưa tự coi là khác nhau; complete_visible_person_census=false, missing_people/false_boxes=null cho tới owner review. Mã p local trong frame, không track.

Owner xem source và overlay, nghiệm thu batch hoặc ghi ngoại lệ bằng giây + mã p/b: nhóm còn trùng, box không có người, người trong source chưa có nhóm, hoặc chưa rõ. Không yêu cầu annotate lại hành vi hoặc review lại 4 same đã accepted. Sau phản hồi tạo receipt/census revision mới, không sửa manifest gốc. Schema D2 riêng không đưa vào validator D0 để giả qua gate. Census D0 cũ giữ nguyên.

## Bước 2: đối chứng hữu hạn

- D2 dùng cached detections đã pin, không chạy lại. V8S và V10S mỗi model 19 source frame, tối đa 38 lượt xử lý frame thật, CPU FP32/4 threads/seed 20261026; không extra real smoke hoặc sweep.
- Cả hai 640 px, conf 0,25, max_det 100, rect=true, batch 1, không augmentation. V8S NMS IoU 0,30 như D2; V10S yêu cầu đúng one-to-one/end2end, không thêm NMS, không truyền IoU như biến có tác dụng. Model khác có score calibration khác: operating point chung chỉ là vòng screening đã cố định, không so PR curve hoặc kết luận tối ưu từng model.
- Source chính thức [Ultralytics assets v8.3.0](https://github.com/ultralytics/assets/releases/tag/v8.3.0). API xác nhận V8S asset 195719452, 22.588.772 bytes; V10S asset 195719628, 16.623.111 bytes. Không lấy checkpoint khác từ THU-MIG thay âm thầm: bản đó có bytes/packaging khác. SHA hiện null vì chưa tải; sau approval acquisition pin exact bytes trước load.
- Package đã có V10 head/end2end path, nhưng cần kiểm checkpoint/taxonomy/preprocess thực tế trước frame đầu. Model không tương thích thì failed và báo, không đổi nguồn/checkpoint hoặc upgrade package tự động. Giữ hướng license Ultralytics đã chấp nhận cho prototype; không đổi license repository.
- Giữ crop context-v1 để so tác động downstream, không chạy G0 trong stage này. Bốn keeper là reference về người/evidence, không yêu cầu detector mới sinh box y hệt. Không giữ box bằng confidence cao nhất để giả đúng keeper.

## Matching và acceptance

Census accepted là chuẩn người nhìn thấy trên 19 frame. Agent shortlist mapping box mới tới người và render source/overlay/crop; owner nghiệm thu batch/ngoại lệ. Không dùng IoU với D2 làm ground truth identity, không suy người từ tổng box. Sau mapping accepted mới báo số người miss, duplicate extras (max số box của một người trừ 1), false boxes, unresolved và crop evidence failures. Một box trùm nhiều người chưa rõ anchor phải giữ unresolved, không tự map nhiều người để tăng recall.

Mục tiêu development đề xuất: không mất người đã accepted, không duplicate còn xác nhận, không box giả hoặc matching unresolved; crop giữ đúng người và không mất evidence đã review. Nếu không arm nào đáp ứng thì không chọn winner chỉ vì ít box hơn. Báo từng tiêu chí và tradeoff, không đổi gate để qua. 8 cặp review chỉ là regression cases, không thay whole-frame census. D2 mới có visual review, chưa mặc định metrics = 0 khi census chưa accepted.

Candidate thắng development vẫn chưa được nghiệm thu mọi video. Cần protocol confirmation trên đoạn/frame chưa dùng để chọn model, freeze trước khi mở; cùng clip vẫn có tương quan, không gọi độc lập như camera mới. Không tự dùng các frame chưa review làm test ngay; sau development chuẩn bị protocol riêng. Runtime tích hợp chỉ sau crop QA/receipt phù hợp, không tracking/events từ approval này.

## Quyết định cần owner

1. Review census 19 frame: chốt toàn batch hoặc liệt kê ngoại lệ/chưa rõ.
2. Duyệt variables và scope acquisition + implementation/tests + 38 detector frame forwards ở proposal.yaml, với mục tiêu development ở trên. Có thể duyệt phần này trong lúc census đang hoàn thiện; run vẫn chờ census accepted.

Đây là hai quyết định khác nhau: approval thực hiện không xác nhận census. AGENTS yêu cầu owner chốt thresholds/metrics/pretrained; không xin lại approval hướng đã có. Không tải weights hoặc run trước khi variables mới được duyệt.
