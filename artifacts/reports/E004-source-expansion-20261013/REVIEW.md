# E004 — Nghiệm thu batch bổ sung 199 crop

Ngày 2026-10-13. **Draft — chưa có approval cho các crop mới trong bảng này.** Approval 109 anchors trước giữ nguyên; không cần review lại. [Kết quả và gaps](README.md), [QA exact geometry/hashes/context](qa-proposals.json), [family/role](family-proposals.json), [sửa sau QA](qa-corrections.json).

Mở giao diện local [REVIEW.html](../../../data/interim/E004-source-expansion-20261013/REVIEW.html): có source với person/context, crop và input 224; lọc theo nhãn/role. Đây là nhãn cuối sau QA của agent, vẫn cần owner nghiệm thu. Có thể approve cả batch và chỉ ghi ngoại lệ theo ID. Cột Pending được owner đổi thành Approve/Reject hoặc quyết định qua chat để nhập receipt exact SHA.

Phạm vi cần chốt cùng batch: **nhãn phone/looking, geometry, work context, family và role proposal**. Context đề xuất trong QA/HTML là quyết định riêng; ledger hiện chưa tự derive normal từ NN. P/N/U không nói lên gian lận; các stock/collaboration frames chỉ là evidence hành vi theo semantics hiện hành.

Đề xuất **27 train, 47 new-development, 125 reserve holdout**. Cả family cùng role, bao gồm các frames chưa crop. Không đổi role đã duyệt ở CF. Train tập trung nguồn auxiliary/office/home và cảnh mới; không chuyển frame của family development/holdout vào train. 52 family có crop là ranh giới quarantine bảo thủ, không phải 52 nhóm độc lập đã chứng minh.

Nếu approve, bước tiếp theo là nhập exact crop decisions/context và family reservation, chuẩn bị V8 bổ sung 27 train (V7 train 689 → 716; val 49 và test 11 giữ nguyên), cùng cohort development/reserve riêng. Release vẫn phải vượt kiểm lineage/package/preservation; approval batch không tự freeze test hoặc cho chạy E004. Reserve là đề xuất cho test mới sau protocol, không phải accepted test hiện tại.

QA đã kiểm 200 proposals qua source/crop/input 224: giữ 199, loại C116 do mờ; 10 recrop dùng hậu tố R2, giữ original để truy vết. U không cộng vào support. Trong 199 crop mới: phone 88 P / 74 N / 37 U; looking 63 P / 121 N / 15 U. Gộp reserve hiện có, projection holdout: phone 76 P / 84 N, looking 75 P / 115 N; còn thiếu 24 phone P, 16 phone N và 25 looking P so với điều kiện đã giữ. Không yêu cầu owner đổi quota trong lần review này.

| Crop | Frame | Phone/Looking | Family | Vai trò | Quyết định |
|---|---|---|---|---|---|
| E004-EX-C001 | PX-001 | P/P | EX-PX-001 | Train bổ sung | Approve |
| E004-EX-C002 | PX-002 | P/N | EX-PX-002 | Train bổ sung | Approve |
| E004-EX-C003 | PX-002 | U/N | EX-PX-002 | Train bổ sung | Approve |
| E004-EX-C004 | PX-003 | P/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C005 | PX-003 | U/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C006 | PX-004 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C007 | PX-005 | P/N | EX-PX-005 | Train bổ sung | Approve |
| E004-EX-C008 | PX-006 | P/N | EX-PX-006 | Train bổ sung | Approve |
| E004-EX-C009 | PX-007 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C010 | PX-008 | P/P | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C011 | PX-008 | U/N | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C012-R2 | PX-009 | N/N | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C013 | PX-010 | N/N | EX-PX-010 | Train bổ sung | Approve |
| E004-EX-C014 | PX-011 | P/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C015 | PX-011 | U/P | CF-Q137 | Reserve holdout | N/P |
| E004-EX-C016 | PX-012 | N/N | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C017 | PX-013 | P/N | CF-Q169 | Reserve holdout | Approve |
| E004-EX-C018 | PX-014 | N/N | EX-PX-014 | Train bổ sung | Approve |
| E004-EX-C019 | PX-015 | U/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C020 | PX-015 | P/U | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C021-R2 | PX-016 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C022 | PX-017 | P/N | CF-Q072 | New-development | N/N, giải thích: người đang cầm tài liệu (phao) chứ không phải phone |
| E004-EX-C023 | PX-018 | P/U | EX-STUDY-BOOK | Train bổ sung | Approve |
| E004-EX-C024 | PX-020 | N/P | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C025 | PX-021 | P/P | EX-PX-021 | Reserve holdout | Approve |
| E004-EX-C026 | PX-022 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C027 | PX-022 | U/P | CF-Q072 | New-development | Approve |
| E004-EX-C028 | PX-024 | N/N | CF-Q072 | New-development | Approve |
| E004-EX-C029 | PX-025 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C030 | PX-026 | P/N | CF-Q072 | New-development | Có phone cạnh tay của áo kem chứ không phải là người đang cầm |
| E004-EX-C031 | PX-027 | N/P | EX-PX-027 | Reserve holdout | Approve |
| E004-EX-C032 | PX-027 | U/N | EX-PX-027 | Reserve holdout | Approve |
| E004-EX-C033 | PX-028 | P/P | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C034 | PX-029 | U/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C035 | PX-029 | P/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C036 | PX-030 | P/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C037 | PX-030 | U/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C038 | PX-031 | P/N | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C039 | PX-033 | P/N | EX-PX-033 | Reserve holdout | Approve |
| E004-EX-C040 | PX-034 | P/U | CF-Q133 | Reserve holdout | P/N, giải thích: người đang nhìn vào thiết bị của mình |
| E004-EX-C041 | PX-035 | P/N | EX-LECTURE | New-development | Approve |
| E004-EX-C042 | PX-035 | U/P | EX-LECTURE | New-development | P/P, giải thích: có phone đặt trên cạnh mép bàn bị che một ít bởi tài liệu |
| E004-EX-C043 | PX-037 | P/N | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C044 | PX-038 | N/P | EX-ROUND-DESK | New-development | Approve |
| E004-EX-C045 | PX-041 | N/N | EX-ROUND-DESK | New-development | Approve |
| E004-EX-C046 | PX-042 | P/U | EX-PX-042 | Reserve holdout | Approve |
| E004-EX-C047 | PX-043 | P/U | EX-PX-043 | Reserve holdout | Approve |
| E004-EX-C048 | PX-044 | P/N | EX-LECTURE | New-development | Approve |
| E004-EX-C049 | PX-046 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C050 | PX-047 | U/P | CF-Q072 | New-development | N/P, giải thích: hai tay người đều có thể quan sát rõ và không có dấu hiệu phone |
| E004-EX-C051 | PX-048 | N/N | CF-Q072 | New-development | Approve |
| E004-EX-C052-R2 | PX-051 | U/P | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C053 | PX-052 | U/N | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C054 | PX-053 | P/P | EX-LECTURE | New-development | N/P, giải thích: người đang cầm tài liệu chứ không phải phone |
| E004-EX-C055 | PX-055 | P/P | EX-LECTURE | New-development | Approve |
| E004-EX-C056 | PX-056 | P/P | EX-LECTURE | New-development | Approve |
| E004-EX-C057 | PX-058 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C058 | PX-059 | N/N | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C059-R2 | PX-060 | U/P | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C060 | PX-061 | N/N | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C061 | PX-062 | N/N | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C062 | PX-063 | N/N | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C063 | PX-064 | N/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C064 | PX-065 | N/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C065 | PX-066 | N/N | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C066 | PX-067 | P/N | EX-LECTURE | New-development | Approve |
| E004-EX-C067 | US-001 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C068 | US-001 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C069 | US-002 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C070 | US-002 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C071 | US-003 | P/N | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C072 | US-003 | P/P | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C073 | US-005 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C074 | US-005 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C075 | US-006 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C076 | US-006 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C077 | US-007 | P/N | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C078 | US-008 | P/N | EX-US-OFFICE | Train bổ sung | Approve |
| E004-EX-C079 | US-009 | P/N | EX-US-009 | Train bổ sung | Approve |
| E004-EX-C080 | US-010 | P/P | EX-US-OFFICE | Train bổ sung | Approve |
| E004-EX-C081 | US-011 | P/U | EX-US-011 | Reserve holdout | Approve |
| E004-EX-C082 | US-013 | P/N | EX-STUDY-BOOK | Train bổ sung | Approve |
| E004-EX-C083 | US-014 | P/N | EX-STUDY-BOOK | Train bổ sung | Approve |
| E004-EX-C084 | US-015 | U/N | EX-US-015 | Train bổ sung | Approve |
| E004-EX-C085 | US-016 | N/N | EX-US-016 | Train bổ sung | Approve |
| E004-EX-C086 | US-017 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C087 | US-018 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C088 | US-019 | P/N | EX-US-019 | Reserve holdout | Approve |
| E004-EX-C089 | US-020 | N/N | EX-US-020 | Train bổ sung | N/P, giải thích: anchor áo xanh nhìn sang laptop của người ngồi cạnh |
| E004-EX-C090 | US-022 | N/P | EX-US-022 | Reserve holdout | Approve |
| E004-EX-C091 | US-023 | U/N | EX-US-023 | Reserve holdout | N/N, giải thích: nhìn rất rõ tay và không có dấu hiệu của phone |
| E004-EX-C092 | US-024 | U/N | EX-US-LECTURE | Reserve holdout | Không biết là đang crop ai |
| E004-EX-C093 | US-025 | N/N | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C094 | US-025 | N/P | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C095 | US-026 | U/N | EX-US-026 | Reserve holdout | Approve |
| E004-EX-C096 | US-027 | U/P | EX-US-LECTURE | Reserve holdout | P/P, giải thích: có phone cạnh sách trên bàn, crop nên tập trung vào đúng anchor |
| E004-EX-C097 | US-029 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C098 | US-029 | P/N | EX-US-BLUECLASS | Reserve holdout | Approve |
| E004-EX-C099 | US-030 | P/N | EX-US-030 | Reserve holdout | Approve |
| E004-EX-C100 | US-031 | N/N | EX-US-031 | Reserve holdout | Approve |
| E004-EX-C101 | US-033 | N/N | EX-US-033 | Reserve holdout | Có phone trên bàn nhưng bị che một phần bên dưới tay |
| E004-EX-C102 | US-036 | U/N | EX-US-036 | Train bổ sung | Approve |
| E004-EX-C103 | CF-001 | N/P | CF-Q001 | Reserve holdout | Approve |
| E004-EX-C104 | CF-007 | N/N | CF-Q001 | Reserve holdout | Approve |
| E004-EX-C105 | CF-009 | U/P | CF-Q009 | Reserve holdout | Approve |
| E004-EX-C106 | CF-030 | N/N | CF-Q030 | Reserve holdout | Approve |
| E004-EX-C107 | CF-030 | N/P | CF-Q030 | Reserve holdout | Approve |
| E004-EX-C108 | CF-030 | N/N | CF-Q030 | Reserve holdout | Approve |
| E004-EX-C109 | CF-030 | N/N | CF-Q030 | Reserve holdout | Approve |
| E004-EX-C110 | CF-030 | N/N | CF-Q030 | Reserve holdout | Approve |
| E004-EX-C111 | CF-041 | U/P | CF-Q030 | Reserve holdout | Xem xét lại, vì không có dấu hiệu phone |
| E004-EX-C112 | CF-044 | N/P | CF-Q030 | Reserve holdout | Approve |
| E004-EX-C113 | CF-055 | U/P | CF-Q030 | Reserve holdout | Xem xét lại, vì không có dấu hiệu phone |
| E004-EX-C114 | CF-061 | N/N | CF-Q061 | Reserve holdout | Approve |
| E004-EX-C115 | CF-061 | U/P | CF-Q061 | Reserve holdout | Xem xét lại, vì không có dấu hiệu phone |
| E004-EX-C117 | CF-074 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C118 | CF-077 | P/U | CF-Q072 | New-development | Approve |
| E004-EX-C119 | CF-078 | P/U | CF-Q072 | New-development | Approve |
| E004-EX-C120 | CF-081 | P/U | CF-Q072 | New-development | Approve |
| E004-EX-C121 | CF-087 | P/U | CF-Q072 | New-development | Approve |
| E004-EX-C122 | CF-094 | U/P | CF-Q072 | New-development | Xem xét lại, vì không có dấu hiệu phone |
| E004-EX-C123 | CF-096 | P/U | CF-Q072 | New-development | P/N, không nhìn thấy toàn bộ đầu nhưng hướng mắt vẫn rõ là nhìn vào own-paper |
| E004-EX-C124 | CF-100 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C125 | CF-103 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C126 | CF-112 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C127 | CF-115 | U/P | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C128 | CF-117 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C129 | CF-123 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C130 | CF-127 | P/N | CF-Q072 | New-development | Crop tập chung đúng anchor hơn |
| E004-EX-C131 | CF-131 | P/N | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C132 | CF-132 | P/N | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C133 | CF-132 | U/P | CF-Q126 | Reserve holdout | Người đang đứng này có tính không? và phone thì hoàn toàn không có |
| E004-EX-C134 | CF-133 | N/P | CF-Q133 | Reserve holdout | Crop đúng người hơn và một tay của người tiền cảnh để dưới bàn |
| E004-EX-C135 | CF-134 | N/N | CF-Q133 | Reserve holdout | Approve |
| E004-EX-C136 | CF-136 | P/N | CF-Q136 | Train bổ sung | Approve |
| E004-EX-C137 | CF-138 | P/N | CF-Q137 | Reserve holdout | Crop tập chung vào anchor hơn |
| E004-EX-C138 | CF-138 | P/N | CF-Q137 | Reserve holdout | Crop tập chung vào anchor hơn |
| E004-EX-C139 | CF-139 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C140 | CF-140 | P/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C141-R2 | CF-141 | U/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C142 | CF-142 | P/N | CF-Q142 | Train bổ sung | Approve |
| E004-EX-C143 | CF-144 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C144 | CF-146 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C145 | CF-147 | P/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C146 | CF-147 | U/P | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C147 | CF-148 | P/U | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C148 | CF-151 | P/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C149 | CF-154 | P/N | CF-Q129 | Reserve holdout | Approve |
| E004-EX-C150 | CF-154 | U/P | CF-Q129 | Reserve holdout | Approve |
| E004-EX-C151 | CF-155 | P/N | CF-Q155 | Train bổ sung | Approve |
| E004-EX-C152 | CF-156 | P/N | CF-Q072 | New-development | Approve |
| E004-EX-C153 | CF-160 | N/N | CF-Q112 | Reserve holdout | Crop tập chung vào anchor hơn |
| E004-EX-C154-R2 | CF-162 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C155 | CF-163 | U/N | CF-Q112 | Reserve holdout | N/N |
| E004-EX-C156 | CF-164 | N/N | CF-Q112 | Reserve holdout | Một tay đặt dưới bàn nhưng có vẻ không có dấu hiệu sử dụng điện thoại |
| E004-EX-C157-R2 | CF-164 | N/P | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C158 | CF-167 | U/N | CF-Q161 | Reserve holdout | N/N, tại sao tay gần mặt lại cho phone là U? có thể quan sát rõ là không có dấu hiệu gì của phone mà |
| E004-EX-C159-R2 | CF-168 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C160 | CF-168 | N/P | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C161 | CF-169 | N/N | CF-Q169 | Reserve holdout | Approve |
| E004-EX-C162 | CF-170 | U/N | CF-Q170 | Train bổ sung | Approve |
| E004-EX-C163 | CF-173 | N/N | CF-Q173 | Train bổ sung | Approve |
| E004-EX-C164 | CF-174 | N/N | CF-Q174 | Train bổ sung | Approve |
| E004-EX-C165 | CF-175 | U/P | CF-Q072 | New-development | N/P, tay đặt trên bàn và không có vật gì gây nhiễu |
| E004-EX-C166-R2 | CF-178 | N/N | CF-Q072 | New-development | Approve |
| E004-EX-C167 | CF-180 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C168 | CF-180 | N/P | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C169 | CF-183 | N/N | CF-Q072 | New-development | Approve |
| E004-EX-C170-R2 | CF-185 | N/P | CF-Q072 | New-development | Approve |
| E004-EX-C171 | CF-188 | N/N | CF-Q072 | New-development | Approve |
| E004-EX-C172 | CF-190 | U/N | CF-Q072 | New-development | Approve |
| E004-EX-C173 | CF-198 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C174 | CF-201 | N/P | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C175 | CF-213 | N/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C176 | CF-213 | P/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C177 | CF-215 | P/N | CF-Q112 | Reserve holdout | Approve |
| E004-EX-C178 | US-004 | P/N | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C179 | US-012 | N/U | EX-US-012 | Train bổ sung | Approve |
| E004-EX-C180 | US-021 | N/P | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C181 | US-028 | N/P | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C182 | US-028 | P/P | EX-US-LECTURE | Reserve holdout | Approve |
| E004-EX-C183 | US-034 | N/N | EX-US-034 | Train bổ sung | Approve |
| E004-EX-C184 | US-034 | N/U | EX-US-034 | Train bổ sung | Approve |
| E004-EX-C185 | US-035 | P/U | EX-US-035 | Train bổ sung | Approve |
| E004-EX-C186 | PX-019 | N/P | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C187 | PX-019 | N/P | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C188 | PX-023 | N/P | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C189 | PX-023 | N/N | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C190 | PX-032 | P/N | CF-Q126 | Reserve holdout | Approve |
| E004-EX-C191 | PX-036 | N/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C192 | PX-036 | P/N | CF-Q137 | Reserve holdout | Approve |
| E004-EX-C193 | PX-039 | U/N | EX-ROUND-DESK | New-development | N/N, vật trong tay rõ ràng là bút |
| E004-EX-C194 | PX-040 | N/P | EX-ROUND-DESK | New-development | Approve |
| E004-EX-C195 | PX-045 | P/N | EX-LECTURE | New-development | Approve |
| E004-EX-C196 | PX-049 | U/P | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C197 | PX-049 | N/P | CF-Q131 | Reserve holdout | Approve |
| E004-EX-C198 | PX-054 | P/P | EX-LECTURE | New-development | Vật trong tay là tài liệu chứ không phải phone, nhưng trong crop có phone ở bàn dưới |
| E004-EX-C199 | PX-057 | P/P | EX-LECTURE | New-development | Approve |
| E004-EX-C200 | PX-068 | P/N | CF-Q137 | Reserve holdout | Approve |
