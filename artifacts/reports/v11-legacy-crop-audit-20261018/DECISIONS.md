# Đề xuất từng crop — Draft

Chưa sửa V11. `recrop` và `exclude` đều đề xuất withheld; nhãn ở ca recrop chỉ là evidence hiện tại, phải duyệt lại geometry mới.

| ID | Vai trò V11 | Hiện tại | Đề xuất | Hành động | Evidence | Quyết định của owner |
|---|---|---|---|---|---|
| V6-CA-001 | val | P/U | P/U | keep | Source cũng mất đầu, không thể nới để phục hồi; giữ phone-only vì mobile/anchor rõ, looking vẫn U. | Loại; giải thích: tư thế cầm đã xuất hiện trong rất nhiều crop hiện nay, phone U |
| V6-CA-003 | val | P/U | P/N | recrop | Person box lịch sử bao cả hai người; cần person/context mới cho người tiền cảnh, không dùng group box làm person. |
| V6-CA-004 | train | P/U | P/N | keep | Sau đối chiếu source và input thấy mặt kính dài, viền máy và tay ôm mobile; vật cam phía sau không thay phone đang cầm. | U/N |
| V6-CA-005 | train | N/U | N/N | keep | Tablet lớn, hai tay thao tác quan sát được; hướng vào thiết bị riêng. |
| V6-CA-006 | train | P/U | U/N | keep | Vật đỏ nhỏ/lưng trơn không đủ nhận mobile; đầu hướng vùng tay/bàn riêng. |
| V6-CA-009 | train | P/U | P/N | keep | Thiết bị mobile cầm hai tay với màn hình/viền; đầu nhìn thiết bị riêng. | Xem xét; Có chắc chắn đó là phone P được không? |
| V6-CA-010 | train | P/U | P/N | keep | Vật cầm có mặt kính/viền và tỷ lệ mobile còn phân biệt tại 224, đầu hướng thiết bị riêng. | Xem xét; Có chắc chắn đó là phone P được không? |
| V6-CA-011 | val | P/U | U/N | recrop | Person box bao nhóm, phone người sau không được truyền cho người viết tiền cảnh; cần khung/person box riêng. |
| V6-CA-012 | train | P/U | P/N | keep | Mobile mặt sau có cụm camera rõ, hai tay thao tác và mắt hướng máy. | Xem xét; Có chắc chắn đó là phone P được không? |
| V6-CA-014 | val | P/U | P/N | keep | Mobile trong hai tay trước mặt, hướng nhìn vào máy; bối cảnh ngoài lớp chỉ metadata. | Xem xét; Có chắc chắn đó là phone P được không? |
| V6-CA-015 | val | P/P | U/P | keep | Vật đen chỉ lộ lưng/cạnh sau sách, không đủ đặc trưng mobile tại 224; đầu nhìn khỏi sách rõ. |
| V6-CA-016 | train | P/U | P/N | keep | Mặt sau trắng còn camera/viền và hình dạng mobile tại 224, đầu hướng máy trên bài. | Xem xét; Có chắc chắn đó là phone P được không? |
| V6-CA-018 | train | U/P | N/P | keep | Hai tay khoanh trên bàn không có vật mơ hồ, đầu quay trái ngoài vùng bàn riêng. |
| V6-CA-021 | train | N/P | N/P | keep | Hai tay trên bàn trống, đầu quay sang cạnh rõ. |
| V6-CA-023 | train | N/N | N/N | keep | Hai tay giữ giấy trên đùi quan sát được, hướng mắt vào giấy riêng. |
| V6-CA-025 | train | N/P | U/P | keep | Tay cầm bút nhìn sang trái; tay bên trái/vùng liên quan mất ở biên crop nên phone U. |
| V6-CA-026 | train | N/U | N/N | keep | Vật xanh là sách/tập có trang/mép giấy, hai tay thấy đủ; đầu hướng sách riêng. | N/P; giải thích: hướng nhìn không vào own-paper |
| V6-CA-028 | train | N/P | N/P | keep | Hai tay cầm bút/giữ giấy trên bàn, đầu quay phải ngoài trang riêng. |
| V6-CA-030 | train | N/P | U/P | keep | Đầu quay phải rõ; một tay/vùng trái cắt khuất, absence không đủ. |
| V6-CA-031 | train | N/N | N/N | keep | Hai tay khoanh trên vùng bàn, không có vật mơ hồ; đầu hướng bàn riêng. | Xem xét; Hướng nhìn hơi lệch sang một bên |
| V6-CA-033 | train | N/U | U/U | exclude | Đầu úp trên tay nên không xác định đích nhìn; tay bị đầu che, vật hồng có thể thiết bị mơ hồ. | N/N; giải thích: tay và quan có thể quan sát rõ, và không looking_around |
| V6-CA-035 | val | U/N | U/N | keep | Đầu hướng xuống bài, bàn và một tay khuất ở mép trái, phone absence thiếu. |
| V6-CA-036 | train | N/U | U/U | exclude | Đầu úp che mặt và hai tay, không đủ hướng nhìn hay absence mobile. | Tương tự với crop V6-CA-033 | 
| V6-CA-037 | train | N/U | U/U | exclude | Nằm gục ngang bàn, tóc che mặt và vùng tay khuất; không diễn giải chắc hai target. |
| V6-CA-038 | train | P/U | N/U | keep | Thiết bị có vùng màn hình/keypad calculator, tay còn lại đủ review; đầu gục che mắt nên looking U. | N/N; giải thích: giống với crop V6-CA-036 |
| V6-CA-040 | train | N/U | U/U | exclude | Đầu úp trên tay, không biết đích nhìn và thiếu evidence absence. | Giống với crop V6-CA-038 | 
| V6-CA-043 | train | N/U | U/U | exclude | Đầu úp che mặt, một tay ngoài bàn; không suy looking từ tư thế ngủ. | Giống với crop V6-CA-040 |
| V6-CA-046 | train | P/U | P/U | keep | Mobile mặt kính dài trên bài còn viền/mặt máy rõ; mắt nhắm không xác nhận đích nhìn. | P/P; giải thích: không nhìn vào own-paper |
| V6-CA-047 | val | P/U | N/N | keep | Hai tay trong vùng viết và giữ giấy, không vật mơ hồ; đầu hướng trang bài. | U/N; giải thích: đang cầm vật đen và tay bị giấy che một phần |
| V6R2-CA-001 | val | P/U | N/P | keep | Bút trong tay, tay còn lại sát má, không vật lạ; đầu quay khỏi bài. | U/N; giải thích: một tay sát má là đang cầm vật màu đen, mắt vẫn nhìn vào own-paper |
| V6R2-CA-002 | train | P/U | P/N | keep | Thiết bị trong hai tay còn mặt kính/viền mobile rõ tại input, mắt hướng máy riêng. |
| V6R2-CA-003 | train | P/N | U/N | keep | Tay trái xuống đùi/khuất, tay phải viết; đầu hướng trang riêng rõ. |
| V6R2-CA-004 | val | P/U | P/N | keep | Mobile trong hai tay còn cụm camera góc/viền đủ phân biệt; phone của người sau không là bằng chứng chính. | Xem xét; Có chắc chắn đó là phone P được không? |
| V6R2-CA-006 | train | P/U | U/U | exclude | Hai người cạnh tranh trong khung, anchor cúi/che mặt và thiếu vùng tay; không đủ hai target. | U/N; giải thích: có thể crop lại để không dính người tiền cảnh, vật đen trên bàn, tư thế này có trong nhiều accepted crop hiện nay và đang gán là looking_around N |
| V6R2-CA-007 | train | U/P | U/P | keep | Đầu quay hẳn sang phải, bàn/tay phía dưới bị cắt nên phone U. |
| V6R2-CA-008 | val | U/N | U/N | keep | Anchor trắng đang viết, hướng xuống bài rõ; tay và bàn một phần bị người tiền cảnh che. |
| V6R2-CA-009 | train | P/P | P/P | keep | Mobile mặt kính và viền trên bài nhận được, đầu quay trái ngoài trang. |
| V6R2-CA-010 | val | U/P | U/P | keep | Đầu và mắt hướng bên phải, tay nằm ngoài crop phía dưới; không đủ absence. |
| V6R2-CA-012 | train | P/U | P/N | keep | Mobile nằm trong tay trái với mặt kính/viền, tay phải viết; mắt nhìn vùng thao tác riêng. |
| V6R2-CA-014 | train | N/U | N/U | keep | Tay khoanh quan sát được không có vật mơ hồ; mắt nhắm/đầu nghiêng không đủ xác nhận đích nhìn. |
| V7-A-001 | val | P/U | P/N | keep | Màn hình mobile sáng tím trên bài, đầu cúi về vùng bài/thiết bị riêng. |
| V7-A-002 | val | P/N | N/N | keep | Calculator có màn hình nhỏ và keypad trên bàn, tay viết/giữ bài; đầu nhìn trang riêng. | P/N; giải thích: phone P có thể quan sát rõ ràng |
| V7-A-003 | val | P/U | P/N | keep | Thiết bị trắng trên giấy là mobile mặt kính lớn/viền, không thấy keypad calculator; đầu hướng máy/bài riêng. |
| V7-A-004 | train | N/N | U/N | keep | Thiết bị nhỏ trên bài mất chi tiết phân biệt mobile/calculator ở input; không giữ known chỉ nhờ source lớn. |
| V7-A-005 | val | P/U | P/N | keep | Mobile mặt kính trên bàn sát tay anchor, đầu hướng bàn/máy tính riêng. |
| V7-A-035 | train | P/N | P/N | keep | Mobile cầm ngang có mặt kính và viền, không keypad; đầu hướng máy riêng. |
| V7-A-042 | train | P/U | P/N | keep | Mobile nằm trên bàn có màn hình/viền; đầu hướng bàn riêng, không gán thiết bị của người cạnh. |
| V7-B-001 | train | P/U | P/N | keep | Mobile trong hai tay còn mặt máy/viền dài nhận được tại input; đầu hướng vùng thao tác. | U/N |
| V7-B-003 | train | P/U | P/N | keep | Mobile trong hai tay, mặt máy và cạnh đủ nhận; đầu nhìn máy riêng. | U/N |
| V7-B-005 | train | P/U | U/N | keep | Mặt lưng trắng không giữ được đặc trưng camera chắc tại 224; đầu hướng tay, không suy phone từ cử chỉ. |
| V7-B-007 | train | P/U | P/N | keep | Phone đỏ cầm trên bàn với mặt kính rõ, đầu nhìn xuống thiết bị riêng. | U/N |
| V7-B-009 | train | P/U | P/N | keep | Mobile màn hình sáng và viền rõ trong tay; nhìn vùng bài/thiết bị riêng dù góc sau đầu. |
| V7-B-011 | train | P/U | P/N | keep | Mobile màn hình dài trong tay dưới bàn, đầu hướng thiết bị riêng; chưa suy duration. |
| V7-B-013 | train | P/U | U/N | keep | Lưng vàng trơn không giữ được camera/đặc trưng tại 224; không truyền nhận dạng từ người cạnh. |
| V7-B-015 | train | P/U | P/N | recrop | Person box bao nhóm, mobile người nữ rõ nhưng cần box một anchor và context mới. | Có thể loại nếu crop kiểu gì cũng dính nhiều người, phone U |
| V7-B-017 | train | P/U | P/N | keep | Mobile mặt kính trong tay, đầu và mắt hướng thiết bị riêng. |
| V7-B-019 | train | P/U | P/N | recrop | Person box bao nhiều người/thiết bị, cần cô lập người cầm; không nhân cùng evidence cho cả nhóm. | Có thể loại nếu crop kiểu gì cũng dính nhiều người, phone U |
| V7-B-021 | train | P/U | P/N | recrop | Person box bao nhiều người, thiết bị của người áo nâu nhận mobile nhưng cần crop/person box riêng. | Có thể loại nếu crop kiểu gì cũng dính nhiều người, phone U |
| V7-B-023 | train | P/U | P/P | keep | Mobile mặt kính trên bàn riêng đủ nhận, không chỉ dựa vật giơ lên; mắt nhìn ngoài vùng bài/máy. | Crop bạn khác rõ hơn đi, bạn áo hồng cầm phone xanh đen hoặc bạn áo trằng bên dưới cũng được hoặc crop hết. Nhưng phone P thì cần xem xét vì phải thực sự chắc chắn giống các crop khác mới được |
| V7-B-025 | train | P/U | U/U | exclude | Thiết bị màn hình gần vuông không đủ phân biệt mobile/tablet, đầu bị hood che hoàn toàn; không còn target chắc. |
| V7-B-027 | val | P/U | P/N | keep | Mobile xanh cầm ngang hai tay, mặt kính/viền rõ; đầu nhìn máy trong vùng riêng. | U/N |
| V7-B-029 | train | P/U | U/P | keep | Thiết bị cầm chỉ còn lưng/cạnh không phân loại ở 224; mặt nhìn ra trước khỏi vật. | Crop lại vì bị dính người ngồi cạnh, looking_around N |
| V7-B-031 | val | P/U | U/N | keep | Vật trắng đang mở/thao tác thiếu đặc trưng mobile, không suy từ thao tác; nhìn vùng tay. |
| V7-B-035 | train | P/U | P/N | keep | Mobile màn hình sáng trên tay, đầu hướng thiết bị; anchor đủ nổi bật dù source mờ. | U/N |
| V7-B-039 | train | P/U | U/N | keep | Mặt lưng bạc và chấm tối mờ không đủ phân biệt phone tại input; đầu nhìn vật. |
| V7-B-040 | train | N/N | U/N | keep | Một tay viết và đầu hướng bài; tay còn lại bị cắt khỏi khung nên absence thiếu. |
| V7-B-041 | train | P/U | P/N | recrop | Person box bao nhóm phụ nữ và người trước; phone rõ nhưng cần một anchor/person box. | phone U |
| V7-B-043 | train | P/U | P/N | keep | Mobile mặt kính trong tay trên bài, đầu hướng thiết bị riêng. | U/N |
| V7-B-047 | train | P/U | U/N | keep | Vật cầm ngang chỉ còn khối đen, chưa phân biệt phone/controller tại 224; đầu nhìn vật. |
| V7-B-049 | train | P/U | U/N | keep | Mặt sau trắng chỉ còn khối/mảnh trơn không đủ nhận mobile tại 224; đầu hướng tay. | Crop dính quá nhiều người, nếu không xử lý được thì loại |
| V7-B-051 | train | P/U | P/U | recrop | Person box bao người trước và người sau, cần tách người tiền cảnh cầm phone; góc sau đầu giữ looking U. | Crop dính quá nhiều người, phone U |
| V7-B-053 | train | P/U | P/N | keep | Mobile trong tay có khung và mặt kính, thêm phone trên bàn; đầu hướng vùng thiết bị riêng. | U/N |
| V7-B-055 | train | P/U | P/N | recrop | Person box bao hai người, cần một anchor với phone của người tiền cảnh; đầu hướng máy. | phone U |
| V7-B-059 | train | P/U | U/N | keep | Mặt lưng vàng thiếu cấu trúc camera phân biệt tại 224, đầu nhìn vật; không dùng màu vỏ. |
| V7-B-063 | train | P/U | P/N | keep | Mobile đen trong hai tay có mặt kính/cạnh rõ, đầu hướng máy riêng. | phone U |
| V7-B-065 | val | P/U | P/N | keep | Mobile cầm ngang với mặt máy nhận được, đầu nhìn thiết bị trên vùng riêng. | phone U |
| V7-B-089 | train | N/N | N/N | keep | Hai tay viết và giữ giấy, bàn không có vật mơ hồ, mắt hướng trang riêng. |
| V7-D-002 | train | P/U | U/N | recrop | Person box bao cả hai người, vật đen mặt lưng chưa đủ phone; cần cô lập người cầm. |
| V7-D-004 | train | P/U | U/N | keep | Thiết bị nhỏ mờ sau resize không đủ nhận mobile, đầu nhìn vùng tay riêng. | Crop dính nhiều người, nếu không xử lý được thì loại |
| V7-D-005 | val | P/U | P/N | recrop | Phone rõ ở tay người nam nhưng person box bao nhiều người; cần box một anchor. | phone U |
| V7-D-008 | train | P/U | P/N | keep | Mobile mặt kính trong tay người nam áo xanh, đầu hướng máy; người cạnh chỉ một phần. | phone U |
| V7-D-009 | val | P/P | P/N | keep | Mobile màn hình/viền rõ trong tay, đầu nhìn thiết bị riêng. | phone U |
| V7-D-010 | train | P/U | P/N | recrop | Person box bao hai người cầm thiết bị khác nhau, cần một anchor/context mới; không chia phone evidence của cả nhóm. |
| V7-D-011 | train | P/U | U/N | keep | Thiết bị trắng trong tay không giữ đặc trưng mobile tại 224, đầu hướng vật. |
| V7-D-012 | train | P/U | P/N | recrop | Person box bao nhóm nhiều người, phone người cầm rõ nhưng cần cô lập anchor và box đơn. |
| V7-D-013 | train | P/U | P/N | keep | Mobile mặt kính trong tay, đầu hướng thiết bị; người sau không phải chủ thể cầm. |
| V7-D-014 | val | P/U | U/N | keep | Mặt lưng đen không thấy đặc trưng mobile chắc ở 224, đầu hướng vật; không suy từ cử chỉ. |
| V7-D-015 | train | P/U | P/N | keep | Thiết bị nhỏ cầm ngang có màn hình/viền, đầu hướng thiết bị riêng. |
| V7-D-017 | train | U/P | P/N | keep | Mobile đỏ mặt kính trong vùng tay, nhìn máy riêng; người cạnh bị cắt một phần. |
| V7-D-018 | train | P/U | P/N | recrop | Person box bao hai người, phone ở tay người trước rõ; cần box đơn và context riêng. |
| V7-D-020 | val | P/U | U/N | keep | Mặt sau bạc trơn thiếu camera/đặc trưng ở input, đầu hướng vùng tay. |
| V7-D-021 | train | P/P | P/N | keep | Mobile ốp có cụm camera ở góc, trong hai tay; mắt hướng máy. |
| V7-D-022 | train | U/P | U/U | recrop | Source cho thấy đang với thiết bị người bên cạnh, nhưng evidence bị cắt khỏi crop; cần context mới, không truyền P từ source ngoài khung. |
| V7-D-023 | train | P/U | P/N | keep | Mobile mặt kính cầm ngang hai tay trên đùi, đầu nhìn xuống thiết bị. |
| V7-D-026 | train | N/N | U/N | keep | Tay sát thân và một phần dưới bàn/cắt khuất; đầu nhìn xuống bàn riêng nhưng không đủ absence. |
| V7-OE-S066-A01 | val | P/U | N/N | keep | Calculator có keypad rõ trên giấy, tay/bàn đủ review; đầu nhìn thiết bị và bài riêng. |
| V7-OE-S066-A02 | val | P/N | N/N | keep | Tay viết và giữ giấy thấy rõ; túi mềm có nếp trên bàn không phải mobile, đầu hướng bài. |
| V7-OE-S068-A01 | train | U/P | U/P | recrop | Person box bao người hàng sau và đầu người trước, tay anchor bị che; cần box/context một người. |
| V7-OE-S068-A02 | train | N/N | N/N | keep | Hai tay viết/giữ giấy nhìn thấy, đầu hướng bài; không có vật mơ hồ. |
| V7-OE-S069-A01 | val | P/U | U/N | keep | Mặt lưng đen trơn không phân biệt mobile tại 224, đầu hướng vật. |
| V7-OE-S070-A01 | train | P/U | U/N | keep | Lưng trắng thiếu đặc trưng camera tại 224, đầu hướng máy; không lấy phone của người cạnh. |
| V7-OE-S071-A01 | val | P/U | P/N | recrop | Phone trong tay người nữ rõ nhưng hai mặt cạnh tranh, cần person box chỉ anchor và context mới. |
| V7-OE-S072-A01 | train | P/P | P/P | keep | Mobile trong tay thấp sát đùi rõ, đầu quay sang người bên phải ngoài bài riêng. |
| V7-OE-S073-A01 | train | P/N | P/N | keep | Mobile mặt kính/cạnh trong tay dưới bàn, đầu nhìn máy; không gán phone người sau. |
| V7-OE-S074-A01 | val | P/U | U/N | keep | Lưng vàng/chấm mờ không đủ phân biệt mobile ở input, đầu hướng vật. |
| V7-OE-S076-A01 | train | U/N | U/U | exclude | Tay che gần hết mặt và vùng tay/bàn không đủ review; không xác định hướng/absence. |
| V7-OE-S077-A01 | val | U/P | U/P | keep | Đầu quay sang phải rõ, hai tay/vùng liên quan bị cắt ở đáy. |
| V7-OE-S102-A01 | train | N/N | N/P | keep | Hai tay cầm bút/giữ giấy rõ, đầu quay trái khỏi trang bài. |
| V7-OE-S102-A02 | train | P/P | P/P | keep | Mobile đen mặt kính trên bàn, hai tay rõ; đầu quay phải ngoài trang bài. |
| V7-OE-S103-A01 | train | N/N | U/N | keep | Vật hồng còn lộ ở cạnh thân không phân biệt phone/đồ khác tại input; không áp ngoại lệ che hoàn toàn. |
| V7-OE-S104-A01 | val | P/U | U/N | keep | Chỉ cạnh/lưng mỏng của thiết bị, không đủ mobile ở input; đầu hướng vùng tay. |
| V7-OE-S105-A01 | val | P/U | P/N | keep | Mobile áp tai nhận dạng được; đầu cúi về vùng bàn/giấy riêng, không tự looking P vì gọi máy. |
| V7-OE-S106-A01 | train | N/N | N/N | keep | Tablet lớn có tỉ lệ/cấu trúc rõ trong hai tay, đầu nhìn tablet; không nhầm tablet thành mobile. |
| V7-OE-S107-A01 | train | P/U | U/N | recrop | Source còn phần tay/thiết bị bên phải đã cắt khỏi crop, nên có thể draft context mới; hiện giữ U. |
| V7-OE-S108-A01 | val | P/P | P/P | keep | Mobile trắng áp tai rõ; đầu/mắt quay trái ra ngoài trang bài. |
| V7-OE-S109-A01 | train | P/P | P/U | keep | Mobile trên bàn rõ nhưng hướng mắt/đích không đủ chắc, không biến nghiêng đầu thành P hoặc N. |
| V7-OE-S109-A02 | train | P/N | P/N | keep | Mobile trên bàn và hai tay viết/giữ giấy rõ; đầu hướng bài riêng. |
| V7-OE-S110-A01 | train | N/N | N/N | keep | Hai tay viết và giữ trang quan sát được, không vật mơ hồ; đầu hướng trang bài dưới mặt. |
| V7-R8-B-001 | train | P/U | P/P | keep | Mobile màn hình sáng trong tay; đầu quay khỏi máy và bàn riêng rõ dù thiếu sáng. |
| V7-R8-D-001 | train | P/U | U/N | recrop | Person box bao cả người đứng và ngồi, tablet không mobile; cần cô lập anchor và giữ tay đầy đủ. |
| V7-UNAPPROVED-C-001 | train | U/P | U/P | keep | Source cũng hết ở tay giơ bên phải, không có pixels để nới cứu absence; giữ một target looking P. |
| V7-UNAPPROVED-C-002 | train | N/P | N/P | keep | Tay chỉ và tay giữ giấy đủ thấy không vật lạ; đầu quay trái ngoài bài. |
| V7-UNAPPROVED-C-003 | val | P/U | P/N | keep | Lưng xanh có cụm camera hình khối/ống kính phân biệt tại 224, không chỉ chấm nhòe; đầu nhìn máy. |
| V7-UNAPPROVED-C-004 | val | P/N | P/N | keep | Thiết bị đỏ có cụm camera góc rõ, tay kia viết; đầu nhìn vùng thiết bị/bài riêng. |
| EXP-CM-001 | train | P/U | U/N | keep | Vật đen nhỏ trong tay thiếu mặt kính/camera phân biệt, đầu hướng tay; source không phục hồi chi tiết input. |
| EXP-CM-002 | train | P/U | P/P | keep | Mobile áp tai với cạnh/mặt máy rõ; đầu ngẩng nhìn phía trước khỏi vùng bàn. |
| EXP-CM-003 | train | P/P | P/P | keep | Mobile áp tai, đầu quay sang bên ngoài bàn riêng rõ. |
| EXP-CM-004 | train | P/P | P/P | keep | Mobile áp tai của anchor áo sọc, đầu quay bên ngoài vùng làm việc. |
| EXP-CM-005 | train | N/N | N/N | keep | Hai tay đặt/khoanh trên bàn rõ không vật lạ; đầu hướng xuống vùng tay riêng. |
| EXP-CM-006 | train | N/U | N/N | keep | Hai tay nắm trên bàn không vật mơ hồ, đầu cúi nhìn vùng bàn riêng. |
| EXP-CM-007 | train | P/U | U/P | keep | Vật đen giơ lên chỉ còn khối mờ ở 224, đầu ngẩng ngoài bàn; không suy từ kiểu cầm. |
| EXP-CM-008 | train | P/U | U/N | keep | Bàn tay áp tai che vùng vật có thể cầm, không thấy mobile rõ; đầu hướng vùng bàn trước thân. |
| EXP-CM-009 | train | N/N | N/N | keep | Hai tay giữ/đọc sách quan sát đủ, không vật mơ hồ; đầu hướng trang riêng. |
| EXP-CM-010 | train | N/U | U/P | keep | Một tay giơ cao, tay còn lại khuất/cắt đáy; mặt ngẩng hướng trước ngoài vùng bàn. |
| EXP-CM-011 | train | N/N | N/N | keep | Hai tay cầm bút/giữ giấy rõ, đầu nhìn vùng viết riêng. |
| EXP-CM-012 | train | U/P | U/P | keep | Đầu quay trái rõ; tay/vùng đùi bị che ở đáy và sau người tiền cảnh. |
| EXP-CM-013 | train | N/P | N/P | keep | Hai tay đan trên bàn rõ không vật lạ, đầu quay sang trái ngoài bàn. |
| EXP-CM-014 | train | U/P | U/P | keep | Đầu quay trái rõ, bàn tay/vùng thấp cắt khuất cạnh chai nên absence thiếu. |
| EXP-CM-015 | train | N/U | N/N | keep | Hai tay cầm bút/giơ sát ngực còn đủ thấy, không vật mơ hồ; đầu hướng trang phía trước thân. |
| EXP-CM-016 | train | U/N | U/P | keep | Đầu/mắt ngẩng ra phía trước khỏi mặt bàn; hai tay/vùng đùi không đủ quan sát. |
| EXP-CM-017 | train | P/U | P/P | keep | Mobile áp tai rõ, mặt ngẩng nhìn trước ngoài bàn. |
| EXP-CM-018 | train | N/N | N/N | keep | Hai tay cầm/giở sách rõ, đầu hướng trang riêng; không vật mobile mơ hồ. |
| EXP-CM-019 | train | N/P | N/P | keep | Hai tay giữ sách rõ, đầu quay trái khỏi sách. |
| EXP-CM-020 | train | N/N | N/N | keep | Hai tay giở sách rõ không vật lạ, đầu hướng trang riêng. |
| EXP-CM-021 | train | N/U | U/U | exclude | Đầu úp khuất hoàn toàn trong thân/tay; không diễn giải hướng nhìn và absence chắc chắn. |
| EXP-CM-022 | train | P/U | U/N | keep | Thiết bị đen thiếu cấu trúc phân biệt mobile tại input, đầu hướng tay. |
| EXP-CM-023 | train | P/U | U/N | keep | Chỉ mặt/cạnh đen mờ của vật cầm, không đủ mobile tại input, đầu hướng tay. |
| EXP-CM-024 | train | U/P | U/P | keep | Vật đen dưới tay thiếu chi tiết phân biệt mobile, đầu nhìn ngoài bàn rõ. |
| V7-A-007 | train | P/U | P/U | keep | Mobile gập trên bàn rõ, source cũng không giữ toàn bộ đầu nên không có pixels để cứu looking; phone-only. |
| V7-A-008 | val | N/N | N/N | keep | Laptop lớn, hai tay thao tác rõ không vật mơ hồ, đầu nhìn màn hình riêng. |
| V7-A-009 | train | P/U | N/P | keep | Hai tay khoanh quan sát được, đầu/mắt ngẩng nhìn ra khỏi laptop. |
| V7-A-011 | train | P/U | N/N | keep | Hai tay thao tác keyboard đủ thấy, đầu hướng laptop, không nhầm laptop với phone. |
| V7-A-013 | train | P/P | P/P | keep | Mobile kiểu gập với bản lề/viền rõ trên bàn, đầu quay khỏi laptop. |
| V7-A-014 | train | N/N | U/N | keep | Một tay/vùng liên quan sau laptop không thấy đủ; hướng đầu vào laptop riêng. |
| V7-A-015 | val | P/U | P/P | keep | Thiết bị trên bàn có keypad/mặt máy mobile phân biệt được; đầu hướng ngoài laptop. |
| V7-A-017 | train | P/P | U/P | keep | Mặt hướng camera khỏi bàn, một tay/vùng bàn bị che bởi người và mặt bàn. |
| V7-A-022 | train | N/P | N/P | keep | Hai tay ở bàn/cốc/báo thấy rõ không vật mơ hồ, đầu quay sang phải khỏi vùng đọc. |
| V7-A-023 | train | P/U | P/N | keep | Mobile mặt kính viền rõ trên bàn, đầu hướng laptop; không cần dựa màu vỏ. |
| V7-A-025 | val | P/U | U/N | keep | Mặt hướng laptop nhưng tay xa bị thân/laptop che, không đủ absence. |
| V7-A-026 | train | N/P | N/P | keep | Hai tay cầm bút/giữ giấy rõ, đầu ngẩng hướng trước khỏi giấy. |
| V7-A-027 | train | P/U | N/N | keep | Vật đen có bố cục phím/đầu thu dạng remote, không mobile; hai tay đồ thủ công rõ, đầu hướng vùng làm. |
| V7-A-029 | val | P/U | P/N | keep | Mobile mặt kính viền sáng trên bàn riêng rõ, đầu hướng vùng làm. |
| V7-A-031 | train | P/P | P/P | keep | Mobile dạng gập trên bàn có mặt máy/bản lề rõ, mặt quay khỏi laptop. |
| V7-A-040 | train | P/U | N/N | keep | Hai tay trên mouse/giấy đủ thấy, đầu hướng laptop riêng; không vật mơ hồ. |
| V7-A-043 | train | N/N | U/N | keep | Laptop rõ nhưng tay/vùng đùi cắt khuất, đầu hướng màn hình riêng. |
| V7-A-046 | train | N/N | N/N | keep | Tay chống cằm và tay còn lại thao tác bàn nhìn được, không vật mơ hồ; đầu hướng máy tính. |
| V7-A-047 | val | N/N | U/N | keep | Tay/vùng sau laptop thiếu evidence absence; đầu nhìn màn hình riêng. |
| V7-A-049 | train | N/N | N/N | keep | Trong crop vẫn thấy bàn tay và vùng thao tác đủ absence dù sát biên, không tự U vì cắt rất ít đầu ngón; nhìn laptop rõ. |
| V7-B-067 | train | P/U | U/N | keep | Thiết bị có dây trong tay không phân biệt mobile/controller/player tại 224, đầu hướng vùng máy riêng. |
| V7-B-069 | train | P/U | P/N | recrop | Phone mặt máy/keypad rõ, nhưng person box bao hai người; cần box/context một anchor. |
| V7-B-087 | val | U/P | N/P | keep | Hai tay ở laptop đủ thấy không vật mơ hồ, mặt ngẩng nhìn camera khỏi màn hình. |
| V7-C-095 | train | U/N | N/N | keep | Hai tay cầm sách rõ không vật mơ hồ, mặt hướng trang sách. |
| V7-C-097 | train | U/N | U/N | recrop | Vật đen nhỏ không đủ mobile ở 224, person box bao hai người có đầu/tay nổi bật; cần khung đơn. |
| V7-C-099 | train | U/N | N/N | keep | Hai tay trên keyboard quan sát được, hướng vào laptop; thiếu sáng nhưng evidence hành vi còn. |
| V7-C-100 | train | U/N | U/N | keep | Vật trên giấy là tablet lớn, không phone; tay phía sau laptop vẫn thiếu nên không tự N cho phone, đầu hướng laptop. |
| V7-C-114 | val | U/P | N/P | keep | Hai tay thao tác laptop rõ, đầu quay trái ra ngoài màn hình riêng. |
| V7-C-115 | train | U/P | N/N | keep | Hai tay trên keyboard rõ không vật mơ hồ, đầu hướng laptop riêng. |
| V7-C-116 | train | U/P | U/U | recrop | Crop mất bàn tay và đích nhìn/laptop bên phải, source cho phép bổ sung context; hiện không đủ hai target. |
| V7-C-118 | train | U/N | N/N | keep | Hai tay trên laptop nhìn được, đầu hướng màn hình, không vật mobile mơ hồ. |
| V7-D-028 | train | P/U | P/N | keep | Thiết bị cầm có màn hình/keypad kiểu mobile rõ, đầu nhìn máy trong tay. |
| V7-D-029 | val | P/U | U/P | keep | Vật trắng trong tay thiếu đặc trưng loại thiết bị tại input, mặt ngẩng ngoài vùng bàn. |
| V7-D-031 | train | P/U | U/N | keep | Vật đen cầm trên bàn chỉ lộ mặt/lưng mờ, không đủ mobile tại input; đầu hướng vật. |
| V7-D-034 | train | P/U | U/P | keep | Thiết bị bạc có lens/screen nhỏ nhưng chưa phân biệt camera/phone chắc ở input, mặt ngẩng khỏi thiết bị. |
| V7-D-035 | train | P/U | P/P | keep | Mobile có màn hình/viền trong tay, mắt hướng trước khỏi máy. |
| V7-D-038 | train | P/U | P/N | recrop | Phone mặt kính rõ nhưng person box bao nhóm, cần một anchor và context mới. |
| V7-OE-S039-A01 | train | U/P | P/N | keep | Mobile áp tai còn thấy cạnh máy, đầu hướng khu vực laptop/bài riêng; không suy looking P từ gọi máy. |
| V7-OE-S040-A01 | train | P/U | P/N | keep | Mobile mặt kính/viền trong hai tay trên bài, đầu hướng máy. |
| V7-OE-S041-A01 | train | U/N | U/N | recrop | Person box bao hàng nhiều người, tay anchor tiền cảnh bị che; cần box đơn, không dùng group box. |
| V7-OE-S042-A01 | train | P/U | U/N | keep | Thiết bị đen sau laptop không giữ chi tiết nhận mobile ở 224, đầu hướng vùng tay. |
| V7-OE-S042-A02 | train | N/N | U/N | keep | Vật đen trong tay còn mơ hồ, không giữ N chỉ vì đang viết; đầu hướng vùng giấy/tay. |
| V7-OE-S043-A01 | train | P/U | P/P | keep | Thiết bị áp tai thấy hình dạng mobile rõ, mặt hướng ngoài trang bài. |
| V7-OE-S043-A02 | train | P/P | U/U | exclude | Vật trên bàn có keypad calculator, nhưng tay dưới bàn và mắt nhắm làm hai target chưa đủ evidence; phone calculator không cứu absence. |
| V7-OE-S043-A03 | train | P/N | U/N | keep | Tay bị cắt ở biên source/crop, không có pixels nới để xác nhận absence; hướng vào trang rõ nên giữ một target. |
| V7-OE-S043-A04 | train | U/P | N/P | keep | Hai tay đan trước ngực thấy rõ không vật mơ hồ, đầu nhìn sang phải ngoài trang bài. |
| V7-OE-S044-A01 | train | P/U | U/N | keep | Thiết bị cầm đen nhỏ/mờ không đủ phân biệt mobile tại input, đầu hướng tay. |
| V7-OE-S044-A02 | train | P/P | U/P | keep | Calculator keypad trên bàn rõ, không mobile; tay dưới bàn thiếu absence, đầu ngẩng khỏi trang. |
| V7-OE-S044-A03 | train | P/P | U/P | keep | Tay bị cắt ngay biên source nên không recrop phục hồi, đầu nhìn ngoài trang rõ. |
| V7-OE-S044-A04 | train | U/P | N/P | keep | Hai tay khoanh trên bàn rõ không vật mơ hồ, mặt hướng ngoài trang riêng. |
| V7-OE-S047-A01 | train | N/N | N/N | keep | Hai tay thao tác laptop quan sát được, mặt hướng màn hình; không vật lạ. |
| V7-OE-S049-A01 | train | P/U | P/N | keep | Mobile có mặt kính/viền trong hai tay dưới bàn, đầu hướng thiết bị. |
| V7-OE-S050-A01 | train | N/N | N/N | keep | Tay chống trán và tay viết trên trang riêng đủ review, không vật mơ hồ; đầu hướng trang. |
| V7-OE-S050-A02 | train | N/N | N/N | keep | Hai tay viết/giữ trang nhìn được, đầu hướng bài riêng, không vật mơ hồ. |
| V7-OE-S051-A01 | val | P/U | P/N | recrop | Mobile mặt kính trong tay rõ nhưng person box bao hai người, cần anchor/context riêng. |
| V7-OE-S052-A01 | train | P/U | P/P | keep | Mobile mặt kính nằm trên bàn cạnh mouse của anchor; mặt ngẩng khỏi laptop/trang bài. |
| V7-OE-S053-A01 | train | N/N | U/N | recrop | Person box bao nhóm thảo luận với tablet, cần box một anchor; không tự phone N khi tay bị nhóm che. |
| V7-OE-S054-A01 | train | N/N | U/N | recrop | Person box bao nhóm, tay chủ thể chưa rõ trong RGB; cần tách anchor và review lại crop mới. |
| V7-OE-S055-A01 | train | U/P | U/P | keep | Mặt hướng ngoài vùng laptop/giấy rõ sau đối chiếu context, tay vẫn dưới bàn/khuất nên phone U. |
| V7-OE-S056-A01 | train | P/N | P/N | keep | Mobile mặt kính trên bàn gần anchor rõ, đầu hướng laptop/giấy riêng. |
| V7-OE-S056-A02 | train | P/N | P/P | keep | Mobile mặt kính trên sách trước anchor, đầu quay khỏi laptop về phía trước. |
| V7-OE-S057-A01 | train | U/N | N/N | keep | Anchor tiền cảnh cầm tablet lớn, hai tay thấy đủ không mobile, đầu hướng màn hình riêng. |
| V7-OE-S057-A02 | train | P/U | U/N | recrop | Person box bao nhóm đứng/ngồi, các màn hình là laptop/tablet không đủ phone P; cần một anchor mới. |
| V7-OE-S058-A01 | val | U/N | U/U | exclude | Nhóm nhiều người gục/che mặt, tay và đích nhìn không đủ rõ ở crop. |
| V7-OE-S061-A01 | train | U/P | U/P | recrop | Person box bao nhiều người với gaze/tay khác nhau, cần cô lập chủ thể; không đổi label theo cả nhóm. |
| V7-OE-S063-A01 | val | U/N | U/P | recrop | Person box là cả hàng người, tay dưới bàn chưa đủ; cần box đơn và context cho hướng nhìn. |
| V7-OE-S064-A01 | val | U/N | N/P | recrop | Person box bao ba người, tay thấy đủ nhưng cần tách một anchor cho RGB classifier. |
| V7-PF-A-001 | train | P/U | P/N | keep | Mobile mặt kính trên bàn cạnh laptop rõ, đầu hướng màn hình riêng; tay sát mặt không tự U khi phone đã rõ. |
| V7-PF-A-002 | train | P/U | P/N | keep | Mobile mặt kính trên bàn rõ, đầu hướng giấy đang viết dù khăn che mặt. |
| V7-PF-A-004 | train | P/P | U/P | recrop | Nhiều người trong person box, phone gần bàn chung chưa đủ attribution cho người trước; cần box/context mới. |
| V7-PF-A-005 | train | P/N | U/N | keep | Vật đen trên bàn chỉ thấy case/lưng, không đủ nhận mobile; tay viết/trang rõ và đầu hướng giấy. |
| V7-PF-A-006 | train | N/N | N/N | recrop | Person box bao người nam và nữ, tablet không mobile; cần một anchor/context mới. |
| V7-PF-A-007 | val | N/U | N/N | recrop | Person box bao nhiều người viết, cần tách anchor chứ không dùng group box làm person. |
| V7-PF-B-001 | val | P/U | N/N | keep | Tablet lớn cầm trên đùi, hai tay thao tác rõ, đầu hướng màn hình riêng. |
| V7-PF-C-001 | train | U/N | U/N | recrop | Anchor là người phía sau, nhưng RGB bị tay/đầu người trước lấn; cần khung tách nếu giữ đủ tay. |
| V7-PF-C-002 | train | U/N | U/N | keep | Tay cầm bút rõ nhưng tay còn lại bị khuất sau trang/bàn; đầu hướng bài riêng. |
| V7-PF-C-003 | val | U/P | N/P | keep | Tay giơ và tay cầm bút thấy đủ không vật lạ, đầu ngẩng ngoài vùng bài. |
| V7-PF-C-004 | val | U/N | N/N | recrop | Anchor hàng sau có box nhưng người tiền cảnh lấn khung, cần context mới tránh hai tay cạnh tranh. |
| V7-PF-D-001 | val | P/U | N/N | recrop | Thiết bị lớn là tablet, người giữa có anchor box nhưng nhiều mặt/tay lấn khung; đề xuất cô lập. |
| V7-PF-D-002 | val | P/U | P/N | keep | Mobile màn hình game/viền rõ, đầu hướng thiết bị trong hai tay. |
| V7-UNAPPROVED-C-005 | train | P/P | P/P | keep | Mobile mặt kính/viền trên bàn trước anchor còn nhận được tại 224, hai tay không cầm thiết bị khác; đầu quay khỏi giấy. |
| V7-UNAPPROVED-C-006 | train | P/N | P/N | keep | Mobile mặt kính/viền nằm sát tay trên bàn rõ, đầu hướng thiết bị/bài. |
| V7-UNAPPROVED-C-007 | train | P/U | P/N | keep | Mobile có cụm camera ở góc trong tay, mắt hướng thiết bị riêng. |
| E004-CF-C007 | train | P/N | P/N | keep | Mobile mặt kính sáng trong tay đặt trên sách, đầu hướng bài/máy riêng. |
| E004-CF-C008 | train | N/N | N/N | keep | Hai tay giữ giấy rõ, đầu nhìn trang riêng; không vật mobile mơ hồ. |
| E004-CF-C009 | train | N/P | N/P | keep | Hai tay trên notebook rõ, mặt ngẩng nhìn ngoài trang. |
| E004-CF-C010 | train | N/N | N/N | keep | Hai tay cầm bút/giữ trang rõ, đầu hướng bài riêng. |
| E004-CF-C011 | train | N/P | N/N | keep | Hai tay giữ giấy/bút quan sát được, đầu hướng trang dù tóc che một phần mặt. |
| E004-CF-C016 | train | P/P | P/P | keep | Mobile màn hình/viền rõ ngay tay, đầu ngẩng nhìn ngoài thiết bị/bài. |
| E004-CF-C018 | train | P/N | N/N | keep | Tablet lớn trên bàn không là mobile, hai tay viết/giở trang rõ; đầu hướng bài. |
| E004-CF-C021 | train | P/P | P/P | keep | Mobile màn hình rõ do anchor cầm, đầu quay về người bên trái ngoài máy; không lấy phone tiền cảnh làm bằng chứng duy nhất. |
| E004-CF-C028 | train | N/P | N/P | keep | Calculator có keypad rõ trên bàn, hai tay cầm bút rõ; đầu quay sang người bên phải. |
| E004-CF-C029 | train | N/N | N/N | keep | Calculator keypad rõ được thao tác, hai tay/bàn đủ thấy, đầu hướng vùng bài riêng. |
| E004-CF-C030 | train | U/P | U/P | keep | Mặt ngẩng nhìn trước ngoài giấy, hai tay bị túi đỏ/bàn che nên absence thiếu. |
| E004-CF-C031 | train | U/N | U/N | keep | Đầu hướng bài nhưng hai tay bị túi đỏ/vùng bàn che, absence chưa đủ. |
| E004-EX-C117 | train | P/N | P/P | keep | Mobile mặt kính sáng trên sách rõ, mặt quay sang cạnh khỏi bài/máy. |
| E004-EX-C118 | train | P/U | P/P | keep | Mobile mặt kính sáng trong tay, đầu quay khỏi máy sang bên trái. |
| E004-EX-C119 | train | P/U | P/N | keep | Mobile mặt kính/viền và giao diện rõ, hướng đầu vào thiết bị riêng. |
| E004-EX-C120 | train | P/U | U/U | exclude | Thiết bị có bàn phím và phần vỏ/cover nhưng không phân biệt chắc mobile/calculator ở 224; source cũng không có đầu, không còn known target chắc. |
| E004-EX-C121 | train | P/U | P/U | keep | Source cũng không có mặt/đầu đầy đủ để nới, giữ phone-only với màn hình rõ, looking U. |
| E004-EX-C122 | train | U/P | N/P | keep | Hai tay trên bàn không vật mơ hồ, mặt ngẩng khỏi trang bài. |
| E004-EX-C123 | train | P/N | P/N | keep | Trong crop còn profile đầu/hướng vào bài đủ diễn giải, source cũng cắt mép mặt nên không đề xuất nới vô ích; phone rõ. |
| E004-EX-C124 | train | N/P | N/P | keep | Hai tay cầm bút/giữ trang rõ, đầu quay về người cạnh ngoài bài riêng. |
| E004-EX-C125 | train | N/P | N/P | keep | Hai tay giữ giấy rõ, mắt/đầu hướng phải ngoài trang riêng. |
| E004-EX-C129 | train | N/P | N/P | keep | Tablet lớn cầm hai tay, đầu ngẩng khỏi màn hình riêng; không nhầm tablet với mobile. |
| E004-EX-C130 | train | P/N | P/N | keep | Mobile mặt sau có cụm camera rõ trong tay, đầu hướng máy. |
| E004-EX-C136 | val | P/N | P/N | keep | Mobile mặt kính trong hai tay ở bàn, đầu hướng thiết bị; người sau không phải evidence phone. |
| E004-EX-C139 | train | P/N | P/N | keep | Mobile màn hình sáng trong tay, tay kia viết; đầu hướng vùng bài/thiết bị riêng. |
| E004-EX-C142 | val | P/N | P/N | keep | Mobile xanh có cụm camera góc trong tay, đầu nhìn máy; tay chống má không ảnh hưởng P đã rõ. |
| E004-EX-C143 | train | P/N | P/N | keep | Mobile mặt kính và cạnh trong tay, đầu hướng xuống máy trên bài. |
| E004-EX-C144 | train | P/N | P/N | keep | Mobile màn hình sáng trên trang, hai tay viết/giữ giấy; đầu hướng vùng bài. |
| E004-EX-C151 | val | P/N | P/N | keep | Mobile mặt kính trong hai tay, mắt hướng thiết bị riêng. |
| E004-EX-C152 | train | P/N | U/N | keep | Vật trắng nhỏ trong tay không giữ cấu trúc mobile tại input, đầu hướng vùng giấy/tay. |
| E004-EX-C162 | val | U/N | U/N | keep | Đầu hướng trang đang viết, tay bên kia/vùng sau chồng sách thiếu evidence absence trong bóng tối. |
| E004-EX-C163 | val | N/N | N/N | keep | Sách đen có trang và gáy rõ trên bàn, hai tay viết/giữ giấy; đầu hướng bài. |
| E004-EX-C164 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu nghiêng sát trang nhưng hướng vào bài riêng. |
| E004-EX-C165 | train | N/P | N/P | keep | Hai tay tựa bàn thấy đủ không vật lạ, mặt ngẩng khỏi giấy. |
| E004-EX-C166-R2 | train | N/N | N/N | keep | Hai tay giữ giấy rõ, đầu hướng bài riêng. |
| E004-EX-C169 | train | N/N | N/N | keep | Hai tay giữ giấy/bút rõ, đầu hướng trang; người đứng sau không là anchor. |
| E004-EX-C170-R2 | train | N/P | N/P | keep | Hai tay cầm bút/giữ trang rõ, đầu quay trái khỏi bài riêng. |
| E004-EX-C171 | train | N/N | N/N | keep | Hai tay viết/giữ trang quan sát được, đầu hướng bài. |
| E004-EX-C172 | train | U/N | U/N | keep | Mảnh trắng/tím trong tay quá ít đặc trưng mobile, không nâng P; calculator riêng rõ, đầu hướng bài. |
| V6-EX-001 | val | P/U | P/N | keep | Mobile màn hình sáng trên bàn và thiết bị khác cạnh tay, đầu hướng thao tác riêng. |
| V6-EX-002 | train | P/P | U/P | keep | Tay thò xuống dưới bàn không thấy đủ, đầu quay phải khỏi bài; người sau không bổ sung absence. |
| V6-EX-003 | val | P/U | U/N | keep | Mặt lưng hồng không có đặc trưng mobile phân biệt tại input, profile đầu vẫn hướng vật; không kế thừa phone P từ cử chỉ. |
| V6-EX-004 | val | P/U | P/N | keep | Mobile trắng có camera mặt sau trong tay, tay kia viết; đầu hướng vùng riêng. |
| V6-EX-007 | train | P/U | P/N | keep | Mobile mặt kính trong tay sát bài, đầu hướng máy. |
| V6-EX-009 | train | P/U | U/N | keep | Mặt lưng bạc/chấm nhỏ không đủ nhận mobile tại 224, đầu hướng tay. |
| V6-EX-010 | train | P/U | P/N | keep | Mobile mặt kính trong tay trên bàn, đầu nhìn thiết bị riêng. |
| V6-EX-012 | train | P/U | P/P | keep | Mobile mặt kính dựng trước thân rõ, đầu ngẩng nhìn người xem ngoài bài. |
| V6-EX-015 | train | P/U | U/P | recrop | Person box bao người hàng sau và người trước, phone trên bàn gần không đủ attribution; cần một anchor/context. |
| V6-EX-017 | val | N/P | N/P | keep | Hai tay trên bài/cầm bút rõ không vật lạ, đầu quay trái ngoài trang. |
| V6-EX-019 | train | U/P | U/P | keep | Đầu quay phải rõ nhưng tay nằm dưới bàn/khuất khỏi crop. |
| V6-EX-020 | train | P/P | N/P | keep | Tay chống cằm và tay cầm bút đều thấy, đầu quay phải khỏi trang; không U chỉ vì tay sát mặt. |
| V6-EX-021 | train | U/P | U/P | keep | Đầu quay trái ngoài vùng bàn, tay bị vách ghế/túi che và cắt đáy. |
| V6-EX-022 | train | N/P | N/P | keep | Hai tay trên giấy rõ, đầu quay trái khỏi trang; watermark nhỏ vùng giấy cần ghi cờ provenance. |
| V6-EX-023 | train | U/P | U/P | keep | Đầu quay phải rõ, một tay trong túi và tay kia ngoài khung nên thiếu absence. |
| V6-EX-024 | train | N/P | N/P | keep | Hai tay thấy rõ trên bàn/giơ sát mặt, đầu quay phải ngoài bài. |
| V6-EX-025 | train | U/P | U/P | keep | Đầu quay phải rõ, tay/vùng dưới bàn không thấy đủ; tai nghe không là mobile. |
| V6-EX-026 | train | U/P | U/P | keep | Đầu quay phải khỏi bài rõ, tay/vùng bàn bị cắt ở đáy và khuất sau người. |
| V6-EX-027 | train | N/P | U/P | keep | Đầu quay trái rõ, một tay/vùng bàn bị cắt và che nên thiếu absence. |
| V6-EX-029 | train | U/P | U/N | keep | Đầu hướng trang riêng, một tay xuống dưới bàn/cắt biên nên phone U. |
| V6-EX-030 | train | N/P | U/P | exclude | Dải hình từ cảnh khác ghép/chèn ở đáy crop, gây nhiễu nguồn và vùng tay; không sửa bằng inpaint. |
| V6-EX-031 | train | N/P | N/P | keep | Hai tay giữ bút trên bàn rõ, đầu quay sang người bên trái khỏi giấy. |
| V6-EX-032 | train | N/N | N/N | keep | Hai tay cầm bút/giữ giấy rõ, đầu hướng trang riêng. |
| V6-EX-034 | train | N/N | N/P | keep | Hai tay cầm bút và đặt trên bàn rõ, mặt ngẩng nhìn trước khỏi trang. |
| V6-EX-035 | train | N/U | N/P | keep | Hai tay đặt trên trang rõ, đầu ngẩng nhìn ngoài vùng viết. |
| V6-EX-036 | val | N/N | N/N | keep | Hai tay đan trên bài rõ, đầu nhìn xuống vùng bài riêng. |
| V6-EX-037 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng bài riêng. |
| V6-EX-038 | train | U/N | U/N | keep | Ảnh cháy sáng/mờ, đầu vẫn hướng giấy nhưng một tay và phần bàn bị cắt/khó thấy. |
| V6-EX-039 | train | N/U | N/P | keep | Hai tay và bút trên giấy rõ, đầu quay trái ra ngoài trang. |
| V6-EX-040 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu cúi vào trang riêng. |
| V6-EX-041 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy đủ, đầu hướng trang riêng. |
| V6-EX-042 | train | N/N | U/N | keep | Tay viết rõ, tay còn lại/vùng thấp bị bàn che; đầu hướng giấy riêng. |
| V6-EX-043 | train | N/N | U/N | keep | Đầu hướng giấy nhưng bàn tay/vùng thấp bị cắt sát đáy; absence chưa đủ. |
| V6-EX-044 | train | N/N | N/N | keep | Hai tay viết/giữ giấy quan sát được, đầu hướng trang riêng. |
| V6R2-EX-001 | train | P/P | P/P | keep | Mobile mặt kính trong tay thấp sát đùi rõ, đầu quay sang người bên phải. |
| V6R2-EX-002 | val | P/U | P/N | keep | Mobile màn hình/viền trên bàn rõ, đầu hướng bài/thiết bị riêng dù góc sau. |
| V6R2-EX-004 | val | P/U | U/N | keep | Mặt lưng/cạnh thiết bị hồng thiếu cấu trúc phone tại 224, đầu hướng vật; phụ đề ngoài crop không truyền nhãn. |
| V6R2-EX-007 | val | N/P | U/P | keep | Đầu quay hẳn ra sau, tay chỉ ra sau ngoài crop nên absence thiếu. |
| V6R2-EX-008 | train | N/P | N/P | keep | Hai tay viết/giữ trang nhìn được, đầu quay trái khỏi giấy. |
| V6R2-EX-009 | val | P/P | P/P | keep | Mobile mặt kính sáng trong tay thấp bên bàn rõ, đầu hướng sang cạnh khỏi bài. |
| V6R2-EX-010 | train | N/P | U/P | keep | Đầu quay trái rõ, tay bên trái/vùng thấp không thấy đủ. |
| V6R2-EX-012 | train | U/P | U/P | keep | Tay chống má rõ nhưng tay kia ngoài khung, mắt hướng cạnh khỏi bài. |
| V6R2-EX-015 | train | N/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng giấy riêng. |
| V6R2-EX-017 | train | N/N | N/N | keep | Hai tay trong vùng viết quan sát được, đầu hướng trang, không vật mơ hồ dù crop nhỏ. |
| V7-C-079 | val | U/P | N/P | keep | Hai tay trên sách rõ, đầu quay trái ngoài vùng đọc. |
| V7-C-087 | val | U/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng giấy riêng. |
| V7-OE-S081-A01 | train | U/N | N/P | keep | Hai tay tựa/khoanh trên bàn quan sát được, đầu nhìn sang người bên trái. |
| V7-OE-S082-A01 | train | N/N | N/N | keep | Hai tay cầm bút/giữ sách rõ, đầu hướng trang riêng. |
| V7-R8-C-001 | train | N/P | N/P | keep | Hai tay đặt trên giấy thấy đủ, đầu quay trái khỏi bài riêng. |
| V7-R8-C-002 | train | N/N | N/N | keep | Hai tay viết/giữ bài rõ, đầu hướng trang, không vật mơ hồ. |
| V7-A-036 | train | P/P | P/P | keep | Mobile mặt kính/viền trên laptop cá nhân trước anchor còn phân biệt được, mặt ngẩng khỏi bàn. |
| V7-A-037 | train | P/U | N/N | keep | Hai tay ở keyboard/mouse đủ quan sát, đầu hướng máy tính riêng. |
| V7-A-038 | train | P/U | P/N | keep | Mobile trắng mặt kính trên bàn rõ, đầu hướng laptop; không nhầm laptop với phone. |
| V7-A-051 | train | N/U | N/N | keep | DSLR với lens lớn rõ trong hai tay, đầu hướng camera riêng; camera không là mobile. |
| V7-A-052 | train | N/U | N/P | keep | Hai tay rõ ở ghế/bàn, điện thoại có dây trên bàn không là mobile; mặt ngẩng khỏi bài. |
| V7-A-053 | train | N/N | U/N | keep | Tay/vùng sau laptop và thân bị khuất, đầu hướng laptop riêng. |
| V7-A-054 | train | N/N | N/P | keep | Hai tay mouse/giấy thấy đủ, mắt nhìn khỏi vùng keyboard/bài. |
| V7-A-056 | train | P/U | U/N | keep | Thiết bị trắng có dây có thể player/mobile, input không đủ phân biệt; đầu hướng laptop riêng. |
| V7-A-057 | train | P/U | P/N | keep | Mobile mặt kính trên bàn rõ, đầu hướng laptop riêng. |
| V7-A-058 | train | P/P | U/P | keep | Vật đen dạng case/ví mở không có mặt máy đủ nhận mobile, mặt ngẩng khỏi keyboard. |
| V7-A-061 | train | N/N | U/N | keep | Vật đen/bạc nhỏ trên bàn chưa phân biệt calculator/mobile ở input, đầu hướng giấy; không giữ N theo nhãn cũ. |
| V7-A-062 | train | P/P | P/P | keep | Mobile mặt kính trên bàn rõ, mặt hướng camera ngoài sách đang viết. |
| V7-A-064 | train | N/N | U/N | keep | Một tay trên keyboard, tay còn lại cắt/khuất sau laptop; đầu nhìn màn hình. |
| V7-A-065 | train | N/N | U/N | recrop | Source còn bàn tay/keyboard bên phải, có thể draft context mới; crop hiện mất tay nên phone U. |
| V7-A-066 | train | N/N | U/N | keep | Source cũng chạm biên trái ở đầu/tay, không có pixels nới hữu ích; giữ looking N từ profile vào màn hình. |
| V7-A-067 | train | N/N | N/N | keep | Hai tay keyboard thấy đủ, laptop không là mobile; đầu hướng màn hình. |
| V7-A-068 | val | P/U | N/U | keep | Hai tay cầm thức ăn/đồ dùng rõ không mobile, mắt nhắm và đích nhìn không đủ xác định. |
| V7-A-069 | train | P/U | U/N | keep | Thiết bị viền cam nằm ngang có thể media player/mobile, không đủ phân biệt tại 224; không tự P vì sáng. |
| V7-A-070 | val | P/P | U/P | keep | Một tay dưới bàn/khuất, mặt hướng camera ngoài vùng giấy. |
| V7-A-071 | train | P/U | P/P | keep | Mobile mặt kính trên bàn rõ, đầu ngẩng ngoài notebook. |
| V7-A-072 | val | P/U | P/N | keep | Mobile trắng mặt kính trên bàn rõ, đầu hướng vùng viết riêng. |
| V7-A-073 | train | P/U | N/N | keep | Hai tay keyboard nhìn được, đầu hướng màn hình riêng, anchor tiền cảnh đủ rõ. |
| V7-A-074 | val | P/P | P/P | keep | Mobile trắng mặt kính trên bàn rõ, đầu quay trái ngoài trang riêng; watermark chân ảnh không che đầu/tay. |
| V7-A-075 | train | N/N | N/N | recrop | Person box bao hai người, hai tay keyboard và đầu vào laptop rõ; cần một anchor/context. |
| V7-A-076 | train | N/N | N/N | keep | Hai tay mouse/keyboard rõ, đầu hướng màn hình riêng, không vật mơ hồ. |
| V7-B-071 | train | P/U | P/N | keep | Mobile mặt kính sáng trong tay, đầu nhìn máy riêng. |
| V7-B-073 | train | P/U | P/N | keep | Mobile mặt kính/viền trong tay, đầu hướng máy; không lấy thiết bị của người bên cạnh. |
| V7-B-074 | train | P/U | U/N | keep | Chỉ mặt/cạnh đen của vật cầm không giữ đặc trưng mobile tại input, đầu hướng tay. |
| V7-B-076 | val | P/U | U/N | keep | Thiết bị trắng có cụm đen lớn nhưng chưa phân biệt camera/phone tại 224, không suy từ cách cầm. |
| V7-B-077 | train | P/U | P/N | keep | Mobile mặt kính và cạnh trong hai tay, đầu hướng máy riêng. |
| V7-B-078 | train | P/U | U/N | recrop | Thiết bị màn hình gần vuông chưa phân biệt mobile/PDA/camera, person box bao hai người; cần khung đơn. |
| V7-B-086 | train | N/U | N/N | keep | Handset trắng có dây/kiểu landline, không mobile; tay còn lại trên bàn DJ thấy đủ, đầu hướng vùng thao tác. |
| V7-B-092 | train | N/N | N/N | keep | Hai tay đọc/lật sách thấy đủ, vật dạ quang là bút; đầu hướng trang. |
| V7-B-093 | train | N/P | N/P | keep | Landline có dây trắng không là mobile, tay kia viết rõ; mắt ngẩng ngoài trang. |
| V7-B-094 | train | N/N | N/N | keep | Hai tay làm giấy/màu thấy đủ, đầu hướng vùng làm riêng, không vật mobile. |
| V7-B-096 | train | U/N | N/N | keep | Tay chống cằm và tay keyboard thấy đủ không vật lạ, đầu hướng laptop. |
| V7-B-097 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| V7-B-098 | train | N/N | N/N | keep | Hai tay keyboard rõ, đầu hướng laptop; dây tai nghe không tự mobile. |
| V7-B-099 | train | N/N | N/N | keep | Thiết bị bàn có cấu trúc camera/đồ âm thanh không mobile, hai tay laptop rõ; đầu hướng màn hình. |
| V7-B-100 | val | U/N | U/N | keep | Vùng tay bị hộp/counter che, đầu hướng giấy/máy tính riêng. |
| V7-B-101 | train | N/U | N/P | keep | Tay chống cằm và tay mouse thấy đủ, đầu quay ra khỏi màn hình. |
| V7-B-102 | train | N/P | N/P | keep | Hai tay cầm bút/giữ giấy rõ, mặt ngẩng khỏi bài. |
| V7-B-103 | train | N/P | N/P | keep | Hai tay đan trước mặt rõ, mắt hướng ngoài sách trên bàn. |
| V7-B-104 | train | N/U | N/P | keep | Hai tay trên bàn trộn âm rõ, mặt hướng người xem khỏi tài liệu/máy. |
| V7-B-106 | train | N/N | N/N | keep | Hai tay trên bản đồ thấy đủ, đầu hướng vùng làm riêng. |
| V7-B-107 | train | N/N | N/N | recrop | Person box bao hai người, cần một anchor và context; hai tay keyboard và hướng laptop còn rõ. |
| V7-B-108 | train | N/U | N/P | keep | Hai tay đan trên bàn rõ, đầu quay trái khỏi vùng làm. |
| V7-B-109 | train | N/N | N/P | keep | Hai tay trên giấy/keyboard rõ, đầu ngẩng về người đứng bên cạnh. |
| V7-B-110 | train | N/N | N/N | keep | Hai tay keyboard/mouse rõ, đầu hướng màn hình riêng. |
| V7-B-111 | train | N/P | N/P | keep | Hai tay giữ sách/bút rõ, mặt hướng người xem ngoài sách. |
| V7-C-102 | val | U/N | U/P | keep | Tay khuất sau laptop trong bóng tối, mặt ngẩng ngoài màn hình. |
| V7-C-104 | val | U/N | N/P | keep | Hai tay cầm sách/bút rõ, đầu quay sang phải khỏi trang. |
| V7-C-105 | train | U/N | U/N | keep | Thiết bị bị cắt ở chính biên source, không có pixels để phục hồi loại vật; đầu nhìn vùng riêng đủ N. |
| V7-C-106 | train | U/N | U/U | exclude | Mắt nhắm/tay chống mặt, tay còn lại cắt/khuất; source không cung cấp đích nhìn chắc, không còn known target. |
| V7-C-107 | val | U/P | U/P | recrop | Source còn bàn tay/keyboard bên trái đã mất trong crop; đề xuất context mới, hiện phone U. |
| V7-C-108 | train | U/P | U/P | keep | Đầu quay trái khỏi trang, tay còn lại/vùng bàn bị cắt. |
| V7-C-109 | val | U/P | N/P | keep | Tay mouse và tay trên đùi thấy đủ, đầu quay khỏi bàn. |
| V7-C-110 | train | U/P | U/P | keep | Đầu quay trái ngoài trang rõ, hai tay dưới bàn không thấy. |
| V7-C-111 | val | U/P | N/P | keep | Hai tay khoanh thấy rõ, đầu quay trái ngoài vùng trang. |
| V7-C-119 | train | U/P | N/P | keep | Hai tay giữ tài liệu rõ, mắt ngẩng khỏi trang. |
| V7-C-121 | val | U/P | N/P | keep | Hai tay chắp trước ngực rõ, đầu quay ngoài laptop. |
| V7-C-123 | val | U/P | N/P | keep | Hai tay khoanh thấy đủ, đầu quay phải khỏi vùng tài liệu. |
| V7-C-125 | train | N/N | U/N | recrop | Source còn vùng viết/bàn tay bên phải, có thể draft context mới; hiện thiếu absence, hướng bài rõ. |
| V7-C-126 | train | N/N | N/N | keep | Hai tay viết/giữ giấy quan sát được, đầu hướng trang riêng. |
| V7-C-127 | val | U/N | N/N | keep | Hai tay thao tác giấy/keyboard nhìn được, đầu hướng vùng riêng. |
| V7-C-128 | val | U/N | U/N | recrop | Source còn bàn tay bên trái nhưng crop đã cắt, cần nới theo anchor; đầu hướng laptop. |
| V7-C-129 | train | U/N | U/N | keep | Tay chống cằm thấy rõ nhưng tay kia sau laptop, đầu hướng màn hình. |
| V7-C-130 | val | U/N | U/N | recrop | Source có vùng mouse/tay trái bên ngoài crop, đề xuất nới; tay sau laptop vẫn cần QA riêng. |
| V7-C-131 | train | U/N | N/N | keep | Hai tay đọc/giở giấy rõ, đầu hướng trang riêng. |
| V7-C-132 | val | U/N | N/N | keep | Calculator keypad rõ, hai tay viết/giữ giấy, đầu nhìn trang. |
| V7-C-133 | train | U/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng bài riêng. |
| V7-C-134 | train | U/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang dù nhìn góc sau. |
| V7-C-136 | train | U/N | N/N | recrop | Person box bao ghế/cảnh và người sau, nên định nghĩa box đơn rồi context gọn giữ tay/laptop. |
| V7-C-137 | train | U/N | N/N | keep | Tay viết và tay đỡ trang rõ không vật mơ hồ, đầu hướng bài riêng. |
| V7-C-139 | val | U/N | U/N | keep | Một tay mouse rõ, tay kia sau laptop bị che; đầu hướng màn hình. |
| V7-C-141 | train | U/P | N/P | keep | Hai tay đan rõ, đầu quay trái ngoài màn hình laptop. |
| V7-C-142 | val | U/P | N/P | keep | Hai tay khoanh rõ, đầu quay phải khỏi màn hình/tài liệu. |
| V7-C-143 | train | U/N | U/N | recrop | Person box rộng gồm người/cảnh phụ và laptop tiền cảnh, tay anchor khuất; đề xuất khung một người. |
| V7-C-144 | train | U/N | U/N | recrop | Person box bao nhóm/monitor, tay và chủ thể RGB chưa cô lập; cần khung mới. |
| V7-D-042 | train | P/U | P/N | keep | Mobile trắng mặt kính trong tay rõ, đầu hướng máy/bài riêng. |
| V7-D-044 | val | P/U | U/N | recrop | Thiết bị nhỏ trong tay chưa đủ mobile, person box bao cả người cạnh; cần box một anchor. |
| V7-D-046 | val | P/U | N/N | keep | Tablet lớn trong hai tay đủ thấy, đầu hướng tablet riêng; không mobile. |
| V7-D-049 | val | U/N | U/N | recrop | Person box bao hai người/laptops, tay bị màn hình che; cần một anchor và context. |
| V7-D-050 | val | P/N | U/U | recrop | Person box bao nhiều người, phone ở đùi không tự thuộc mọi anchor; cần tách một người trước gán target. |
| V7-D-051 | train | P/U | P/N | keep | Mobile hồng mặt kính trong hai tay rõ, đầu hướng máy riêng. |
| V7-D-053 | train | U/N | U/N | keep | Tay bị laptop/cạnh bàn che, đầu hướng màn hình riêng; không suy N từ đang laptop. |
| V7-D-054 | val | U/N | N/N | recrop | Person box là nhóm đứng/ngồi, cần anchor đơn; không đưa nguyên group box vào person geometry. |
| V7-D-056 | train | U/N | U/N | keep | Vật/tay trên keyboard thiếu đặc trưng mobile, không suy phone từ động tác; đầu hướng bàn. |
| V7-D-057 | train | U/N | U/N | recrop | Person box bao nhiều người/monitor, tay anchor bị che; cần cô lập chủ thể. |
| V7-D-058 | train | P/U | P/N | keep | Mobile mặt kính trong tay rõ, đầu hướng máy riêng. |
| V7-OE-S002-A01 | train | N/N | N/N | keep | Tay chống cằm và tay thao tác laptop thấy đủ, đầu hướng màn hình riêng. |
| V7-OE-S003-A01 | train | P/U | P/N | keep | Mobile mặt kính sáng trong tay rõ, đầu hướng máy riêng. |
| V7-OE-S006-A01 | train | N/N | N/N | keep | Tablet màn hình lớn, hai tay mở rõ không mobile, đầu hướng tablet riêng. |
| V7-OE-S009-A01 | val | U/P | U/P | recrop | Person box bao hàng người, tay/đích thuộc nhiều người; cần box đơn, không label cả nhóm. |
| V7-OE-S012-A01 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu về bài; timestamp góc không che evidence, ghi cờ overlay. |
| V7-OE-S019-A01 | train | U/N | N/N | keep | Tay chống cằm và tay keyboard đủ thấy, đầu hướng màn hình riêng. |
| V7-OE-S021-A01 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, tablet lớn trên bàn không mobile, đầu nhìn bài. |
| V7-OE-S022-A01 | val | U/P | N/P | keep | Hai tay sát mặt thấy đủ không vật lạ, mắt ngẩng khỏi bàn cờ. |
| V7-OE-S023-A01 | train | U/N | N/N | keep | Tay mouse và tay trên đùi thấy đủ, đầu hướng máy tính. |
| V7-OE-S024-A01 | train | U/P | N/P | keep | Tay chống cổ và tay đặt rõ trên đùi, mắt hướng trước khỏi trang riêng. |
| V7-OE-S025-A01 | train | U/P | U/P | keep | Mặt hướng người xem ngoài bàn, tay/vùng bàn bị cắt ở đáy. |
| V7-OE-S030-A01 | train | N/N | U/N | keep | Source cũng cắt mép bàn tay ở bên phải, không có pixels nới hữu ích; giữ looking N, phone U. |
| V7-OE-S033-A01 | val | U/P | U/P | recrop | Person box bao nhiều người với vùng bài khác nhau, cần cô lập anchor trước review crop mới. |
| V7-OE-S035-A01 | train | N/N | N/N | keep | Hai tay giữ mẫu/thao tác rõ, đầu về vùng thực hành riêng; không mobile. |
| E004-EX-C001 | val | P/P | P/P | keep | Mobile mặt sau có cụm camera rõ, đầu quay trái ra ngoài thiết bị/bàn. |
| E004-EX-C002 | val | P/N | P/N | keep | Mobile mặt kính trong tay rõ, đầu hướng máy riêng. |
| E004-EX-C003 | val | U/N | N/N | keep | Tay chống trán và tay trên giấy thấy đủ không vật mơ hồ, đầu hướng bài. |
| E004-EX-C006 | train | P/N | P/N | keep | Phần mặt kính tím và viền máy trên túi đỏ còn đủ nhận mobile tại input, đầu hướng vùng thao tác. |
| E004-EX-C007 | val | P/N | P/N | keep | Thiết bị trắng có cụm camera/viền còn phân biệt được ở input, đầu hướng máy riêng. |
| E004-EX-C008 | val | P/N | P/N | keep | Mobile mặt sau có cụm camera rõ, đầu hướng thiết bị riêng. |
| E004-EX-C009 | train | P/N | P/N | keep | Mobile màn hình tím có viền trên túi đỏ rõ, đầu hướng máy/bài riêng. |
| E004-EX-C013 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang, không vật mơ hồ. |
| E004-EX-C018 | val | N/N | N/N | keep | Hai tay viết/giữ sách rõ, đầu hướng trang riêng. |
| E004-EX-C021-R2 | train | P/N | U/N | keep | Lưng/cạnh đen của thiết bị thiếu đặc trưng mobile tại 224, đầu hướng tay. |
| E004-EX-C022 | train | N/N | N/N | keep | Calculator xanh có keypad rõ, hai tay cầm bút/mở bàn tay quan sát được, đầu hướng bài. |
| E004-EX-C023 | train | P/U | P/N | keep | Mobile mặt kính có viền/giao diện rõ trên sách, hướng đầu vào máy riêng. |
| E004-EX-C026 | train | N/P | N/P | keep | Hai tay cầm bút/chỉ đều thấy, đầu quay phải khỏi trang bài. |
| E004-EX-C027 | train | U/P | U/N | keep | Đầu nghiêng nhưng hướng vào tờ giấy đang giữ của chính anchor, không P chỉ vì giơ giấy; tay thấp vẫn khuất. |
| E004-EX-C028 | train | N/N | N/N | keep | Calculator keypad rõ, tay viết và tay sát tóc không vật mơ hồ, đầu hướng bài. |
| E004-EX-C029 | train | N/P | N/P | keep | Calculator có keypad, hai tay bàn rõ; đầu quay phải khỏi trang riêng. |
| E004-EX-C030 | train | P/N | P/N | keep | Mobile mặt kính/viền trên bàn cạnh tay anchor nhận được, không nhầm calculator bàn bên phải; đầu nhìn bài riêng. |
| E004-EX-C041 | train | P/N | P/N | keep | Thiết bị mặt kính với nội dung hiển thị/viền đủ mobile tại input, không keypad vật lý calculator; đầu hướng máy. |
| E004-EX-C042 | train | P/P | P/P | keep | Mobile mặt kính/viền đỏ trên bàn riêng rõ, đầu quay sang người khác khỏi giấy. |
| E004-EX-C044 | train | N/P | N/P | keep | Hai tay giữ giấy/bút rõ, mặt ngẩng trái khỏi vùng bài. |
| E004-EX-C045 | train | N/N | N/N | keep | Hai tay trên trang rõ, đầu hướng bài riêng. |
| E004-EX-C048 | train | P/N | P/N | keep | Mobile mặt kính viền sáng trên bàn riêng, đầu hướng sách; không gán người hàng sau. |
| E004-EX-C049 | train | N/P | N/P | keep | Hai tay tựa/đan trên bàn rõ, đầu quay phải khỏi trang. |
| E004-EX-C050 | train | N/P | U/P | keep | Tay kéo ra sau lưng/túi mất evidence absence, đầu quay trái khỏi bàn. |
| E004-EX-C051 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy đủ, đầu hướng bài riêng. |
| E004-EX-C054 | train | N/P | N/P | keep | Vật mỏng là giấy có mép/trang cong trong tay, không mobile; hai tay rõ, mặt ngẩng khỏi bài. |
| E004-EX-C055 | train | P/P | P/P | keep | Mobile mặt kính trên bàn riêng còn cấu trúc rõ, đầu quay trái khỏi trang. |
| E004-EX-C056 | train | P/P | P/P | keep | Mobile mặt kính đen trên bàn rõ, đầu quay sang trái ngoài vùng riêng. |
| E004-EX-C066 | train | P/N | P/N | keep | Mobile mặt kính viền trắng trên bàn rõ, đầu hướng trang đang viết. |
| E004-EX-C193 | train | N/N | N/N | keep | Hai tay trên trang rõ không vật mơ hồ, đầu nhìn giấy riêng. |
| E004-EX-C194 | train | N/P | N/P | keep | Hai tay/động tác giơ ngón rõ không mobile, mặt quay trái khỏi bài. |
| E004-EX-C195 | train | P/N | P/N | keep | Mobile mặt kính viền sáng trên bàn riêng, đầu hướng sách; rất gần biến thể cùng cảnh cần kiểm lặp. |
| E004-EX-C198 | train | U/P | N/P | keep | Vật cầm là giấy có mép cong, hai tay bút/giấy rõ; mặt hướng người khác ngoài bài. |
| E004-EX-C199 | train | P/P | P/P | keep | Mobile mặt kính đen trên bàn rõ, đầu quay ra sau về người khác. |
| EXP-RF-001 | train | N/N | N/N | keep | Hai tay viết/giữ trang thấy đủ, đầu hướng bài riêng dù khẩu trang. |
| EXP-RF-003 | val | N/P | N/P | keep | Hai tay trên giấy rõ, đầu quay phải khỏi trang; phụ đề ở đáy cần cờ overlay, không suy nhãn từ text. |
| EXP-RF-004 | val | U/P | U/P | keep | Đầu quay hẳn ra sau, tay/vùng bàn cắt khuất ở đáy. |
| EXP-RF-006 | val | N/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng bài; chữ overlay vùng đáy cần cờ QA riêng. |
| EXP-RF-007 | train | U/P | U/P | keep | Tay cầm bút thấy rõ nhưng tay còn lại kéo ra sau khỏi crop, đầu quay khỏi bài. |
| EXP-RF-008 | train | U/P | U/U | exclude | Crop 58 × 140, mặt/hướng và tay bị mờ/che; không đủ evidence hai target. |
| EXP-RF-009 | train | U/P | U/P | keep | Đầu quay phải rõ, cánh tay/vùng tay ra ngoài crop nên thiếu absence. |
| EXP-RF-010 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng bài; watermark nhỏ dưới khung không thay evidence. |
| EXP-RF-013 | val | N/N | N/N | keep | Hai tay cầm bút/giữ trang còn thấy, đầu hướng bài; cháy sáng nhưng chưa mất cấu trúc hành vi. |
| EXP-RF-015 | train | N/U | U/U | exclude | Mắt nhắm ngủ trên hai tay, không xác định hướng nhìn và absence ở tay bị đầu che. |
| EXP-RF-017 | train | N/P | N/P | keep | Hai tay cầm bút rõ không vật mơ hồ, mặt hướng camera ngoài trang. |
| EXP-RF-019 | train | N/P | N/P | keep | Hai tay viết/giữ giấy rõ, đầu quay phải khỏi trang. |
| EXP-RF-021 | val | U/P | U/P | keep | Mặt quay trái khỏi vùng bàn, tay hoàn toàn ngoài crop. |
| EXP-RF-023 | train | U/P | U/P | keep | Đầu quay trái rõ, hai tay/vùng bàn bị cắt và người trước che. |
| P002-person-01 | train | P/U | U/N | keep | Vật đen quá ít chi tiết tại native 46 × 92 không đủ mobile, đầu hướng tay riêng. |
| P006-extra-01 | train | U/P | N/P | keep | Hai tay khoanh trên bàn rõ, đầu quay trái ngoài trang riêng. |
| P006-person-01 | train | P/U | U/N | keep | Native quá mờ ở thiết bị, không đủ phân biệt mobile với vật khác tại input; đầu hướng tay. |
| P006-person-02 | train | P/U | U/N | keep | Vật đen cầm hai tay không giữ chi tiết mobile ở input, đầu hướng vật. |
| P007-extra-01 | train | U/P | N/P | keep | Hai tay khoanh rõ, đầu quay trái ngoài vùng bàn. |
| P007-person-01 | train | P/U | U/N | keep | Thiết bị nhỏ chỉ còn khối mờ, không xác nhận mobile từ cử chỉ; đầu hướng tay. |
| P007-person-02 | train | P/U | U/N | keep | Lưng/cạnh thiết bị không đủ đặc trưng mobile tại 224, đầu hướng vật. |
| P008-extra-01 | train | U/P | N/P | keep | Hai tay đan trên bàn rõ, đầu ngẩng nhìn trước ngoài vùng giấy. |
| P008-person-01 | train | P/U | U/N | keep | Thiết bị cầm chỉ lộ cạnh/mặt tối mờ, không đủ mobile tại input, đầu hướng tay. |
| P009-person-01 | val | P/U | U/N | keep | Đầu hướng vùng riêng, hai tay bị cắt đáy/che bởi thân nên absence thiếu. |
| P019-person-01 | train | P/U | P/N | keep | Mobile mặt kính dưới bàn trong tay rõ, đầu hướng thiết bị; không lấy người sau. |
| P022-person-01 | train | P/U | U/N | keep | Thiết bị rất mờ/méo không đủ phone identity, đầu hướng tay; source không phục hồi input. |
| P029-person-01 | train | P/U | P/U | keep | Mobile trên bàn rõ, hướng mắt/đích vẫn chưa chắc với đầu nghiêng; giữ looking U thay suy từ posture. |
| P029-person-02 | train | P/U | P/N | keep | Mobile mặt kính trên bàn rõ, đầu cúi về giấy riêng. |
| P030-person-01 | train | P/U | P/N | keep | Mobile mặt kính dưới tay trên bàn rõ, đầu hướng trang/máy riêng. |
| P031-person-01 | train | P/U | P/N | keep | Mobile mặt kính dựng dưới tay trên bàn rõ, đầu hướng vùng bài. |
| P032-person-01 | train | P/U | P/N | keep | Mobile có màn hình trong tay trên bài rõ, đầu hướng thiết bị riêng. |
| P033-person-01 | train | P/P | P/P | keep | Mobile mặt kính trên bàn rõ, đầu quay phải khỏi giấy. |
| P034-person-01 | train | P/U | P/N | keep | Mobile mặt kính trên bàn riêng, đầu nhìn xuống vùng bài/thiết bị. |
| P035-person-01 | train | P/U | P/N | keep | Mobile có màn hình trong tay trên bàn rõ, đầu hướng vùng thao tác riêng. |
| P036-person-01 | train | P/U | P/N | keep | Mobile mặt kính trên bàn riêng rõ, đầu nhìn thiết bị/bài trước thân. |
| P038-person-01 | train | P/U | P/N | keep | Mobile mặt kính ngay tay trên bàn rõ, đầu hướng giấy/máy riêng. |
| P039-person-01 | train | P/U | P/N | keep | Mobile mặt kính ngay tay trên bàn rõ, đầu hướng vùng giấy. |
| P043-person-01 | train | P/U | P/N | keep | Mobile mặt kính trong hai tay rõ, đầu hướng máy riêng. |
| P047-extra-01 | train | U/P | U/P | keep | Đầu quay ra sau rõ, tay/bàn cắt khuất; watermark lớn ngang bàn cần cờ QA. |
| P047-person-01 | train | P/U | U/N | keep | Vật cầm chỉ còn mặt lưng/khối mờ không đủ phone identity; đầu hướng tay, watermark lớn không dùng làm evidence. |
| V7-A-028 | train | N/N | N/N | keep | Tay chống đầu và tay viết thấy đủ, hướng đầu vào bài riêng. |
| V7-A-030 | val | N/N | U/N | keep | Tay viết rõ nhưng tay còn lại mất ở đáy crop, đầu hướng trang riêng. |
| V7-A-032 | train | N/N | N/N | keep | Hai tay viết/giữ sách rõ, đầu hướng trang riêng. |
| V7-A-034 | train | N/N | N/N | keep | Tay chống má và tay giữ sách thấy đủ, đầu hướng sách riêng. |
| V7-B-010 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng; người cạnh không phải anchor. |
| V7-B-026 | train | N/N | N/N | keep | Hai tay viết/giữ bài rõ, đầu hướng giấy riêng. |
| V7-B-046 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, mắt hướng trang riêng. |
| V7-C-055 | val | U/P | U/P | keep | Mặt hướng ra cửa sổ ngoài bàn, một tay/vùng bàn không đủ thấy. |
| V7-C-059 | val | U/P | N/P | keep | Hai tay khoanh trên bàn thấy được, đầu quay phải ngoài trang dù ảnh mờ. |
| V7-C-061 | train | U/P | U/P | recrop | Person box bao hai người và tay che, cần anchor đơn/context riêng; không lấy gaze người trước cho người sau. |
| V7-C-063 | train | U/P | U/U | recrop | Đích nhìn là vùng người bên trái ở ngoài crop, source cho phép nới context; crop hiện thiếu cả tay và vùng bài. |
| V7-C-065 | train | U/P | U/P | keep | Đầu quay ra sau trái rõ, một tay bị cắt ở mép trái. |
| V7-C-069 | val | U/P | N/P | keep | Hai tay cầm bút/giữ giấy rõ, đầu ngẩng trái khỏi trang. |
| V7-C-075 | val | U/P | U/P | keep | Đầu quay phải rõ, một bàn tay bị cắt ngoài biên trái. |
| V7-C-081 | val | U/P | U/P | keep | Đầu quay trái rõ, hai tay bị monitor/đáy crop che. |
| V7-C-083 | train | U/P | U/P | keep | Đầu quay phải ngoài bài, tay giơ giấy kéo ra biên crop nên absence thiếu. |
| V7-C-085 | train | U/P | U/U | recrop | Đầu nghiêng sang người cạnh nhưng trang/đích ngoài crop, source có thể bổ sung context; hiện U/U. |
| V7-C-088 | train | U/N | N/N | keep | Hai tay viết/giữ notebook rõ, đầu hướng trang riêng. |
| V7-C-090 | val | U/P | U/P | keep | Đầu quay phải sang người cạnh, một tay sau tờ giấy và ngoài crop thiếu evidence absence. |
| V7-C-091 | train | U/N | N/N | keep | Hai tay viết/giữ bài rõ, đầu hướng giấy riêng. |
| V7-OE-S084-A01 | train | N/N | N/N | keep | Tay chống đầu và tay giữ giấy thấy đủ không vật lạ, đầu hướng trang riêng. |
| V7-OE-S085-A01 | train | N/P | N/P | keep | Hai tay trên trang đủ thấy, đầu quay trái khỏi bài. |
| V7-OE-S111-A01 | val | P/N | U/N | recrop | Crop cắt bàn tay/vùng viết, source có thể nới nhưng cần tránh phụ đề chồng vùng evidence; current phone U. |
| V7-OE-S112-A01 | train | N/N | N/N | keep | Hai tay bút/sách thấy đủ, đầu hướng trang riêng. |
| V7-OE-S113-A01 | train | U/P | U/P | keep | Vật đen trên trang không phân loại chắc mobile tại 224, một tay dưới bàn; mặt ngẩng ngoài trang rõ. |
| V7-OE-S113-A02 | train | U/N | U/N | keep | Vật đen nhỏ trên trang và tay dưới bàn không đủ absence/identity, đầu hướng giấy. |
| V7-OE-S114-A01 | train | N/N | N/N | keep | Calculator keypad rõ, hai tay viết/giữ giấy, đầu hướng bài. |
| V7-OE-S114-A02 | train | U/P | N/P | keep | Calculator trên bàn không mobile, hai tay viết/giữ giấy rõ, mặt ngẩng ngoài trang. |
| V7-OE-S116-A01 | train | P/P | P/P | keep | Mobile mặt kính dưới tay trên bàn rõ, mặt hướng trước ngoài trang riêng. |
| V7-OE-S116-A02 | train | N/N | N/N | keep | Hai tay viết/giữ trang rõ, không vật mơ hồ, đầu hướng giấy riêng. |
| EXP-SCB-003 | train | N/P | N/P | keep | Hai tay khoanh trên bàn thấy đủ, đầu quay trái khỏi bài. |
| EXP-SCB-004 | train | U/P | U/U | recrop | Source có bàn/vùng làm nhưng crop chỉ back view/tay che mặt, cần context mới nếu muốn giữ looking known. |
| EXP-SCB-006 | train | N/P | N/P | keep | Hai tay khoanh trên bàn rõ, mặt hướng trái ngoài trang riêng. |
| EXP-SCB-007 | train | U/P | N/P | keep | Tay sát ngực và tay buông cạnh bàn thấy đủ, đầu quay sang phải ngoài bài. |
| EXP-SCB-021 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| EXP-SCB-024 | val | U/P | U/P | keep | Kiểm lại input riêng: mặt ngẩng và quay ra trước khỏi vùng bài đủ rõ dù tay bị người trước che; giữ looking P, phone U. Không loại chỉ vì crop nhỏ. |
| EXP-SCB-033 | train | U/P | N/P | keep | Hai tay khoanh trên bàn rõ, đầu quay trái ngoài trang. |
| EXP-SCB-037 | train | U/P | N/P | keep | Hai tay khoanh rõ, đầu/mắt ngẩng ngoài trang bài còn trong crop. |
| EXP-SCB-040 | val | U/P | U/P | keep | Đầu ngẩng/quay khỏi vùng giấy nhưng tay và vật bị mờ mất cấu trúc nên absence thiếu. |
| EXP-SCB-041 | train | U/P | U/U | recrop | Crop chỉ góc sau đầu và tay khuất, source có context lớp nhưng không truyền label vào crop hiện tại. |
| EXP-SCB-045 | train | U/P | U/U | recrop | Crop thiếu vùng bài/đích từ góc sau; đề xuất mở context từ source rồi review SHA mới. |
| EXP-SCB-047 | val | U/P | U/U | recrop | Đầu ở góc sau và tay che mặt, vùng bài ngoài crop; source có thể bổ sung context, không tự looking P. |
| SCB-turnhead-001 | train | U/P | U/P | keep | Mặt ngẩng ngoài bài, tay giơ cao và vùng tay thấp mờ/che nên absence chưa đủ. |
| SCB-turnhead-002 | train | U/P | U/P | keep | Đầu quay rõ sang trái ngoài trang, nhưng một tay/vùng bàn khuất; không cần thấy con ngươi để looking P khi hướng rõ. |
| SCB-turnhead-003 | train | U/P | N/P | keep | Hai tay khoanh trên bàn đủ thấy, đầu quay ra sau khỏi trang. |
| SCB-turnhead-004 | train | U/P | N/P | keep | Hai tay trên bài đủ thấy, đầu quay phải sang cạnh ngoài trang. |
| SCB-turnhead-005 | val | U/P | U/U | recrop | Back view và tay/bài thiếu trong crop, source có thể thêm vùng desk/context; hiện không giữ P chỉ theo class nguồn. |
| SCB-turnhead-006 | train | U/P | U/U | recrop | Profile đầu nhưng vùng bài/đích ngoài crop, source có thể thêm context; current U/U. |
| SCB-turnhead-007 | train | U/P | N/P | keep | Tay cầm bút và tay trên bàn thấy đủ, đầu quay phải khỏi giấy. |
| SCB-turnhead-008 | train | U/P | N/P | keep | Hai tay trên bài nhìn được, đầu quay ra sau về camera/người khác. |
| SCB-turnhead-009 | train | U/P | U/U | exclude | Native 47 × 44, mặt và tay mất chi tiết; không đủ hai target. |
| SCB-turnhead-010 | val | U/P | U/U | recrop | Back view không đủ vùng bài để diễn giải, đề xuất context mới theo source, không truyền label từ scene rộng. |
| SCB-turnhead-011 | val | U/P | U/U | recrop | Góc sau đầu nhỏ và bàn bị người trước che, có thể thử context rộng; chưa xác nhận được known target trên crop hiện tại. |
| SCB-turnhead-012 | train | U/P | N/P | keep | Hai tay đan trên bàn thấy đủ, đầu quay trái khỏi trang riêng. |
| SCB-turnhead-013 | train | U/P | N/P | keep | Hai tay khoanh trên bàn rõ, đầu quay trái ra ngoài sách. |
| SCB-turnhead-016 | val | U/P | N/P | keep | Vật đen trên bàn có cấu trúc ví/case, hai tay khoanh thấy được không thiết bị mơ hồ; đầu quay trái ngoài trang. |
| SCB-turnhead-018 | train | U/P | U/U | exclude | Native 35 × 54, chỉ sau đầu và vai mờ, không đủ hands/gaze/context. |
| SCB-turnhead-019 | train | U/P | U/U | exclude | Native 44 × 56, mặt/hướng và tay quá mờ/che, không đủ evidence. |
| SCB-turnhead-020 | train | U/N | U/U | exclude | Source cũng bị đầu người trước che tay/vùng bài, nới không phục hồi evidence trong cùng frame; không đủ hai target. |
| SCB-turnhead-021 | val | U/P | U/U | exclude | Native 46 × 56, vùng tay bị đầu người trước che và hướng mặt không rõ. |
| SCB-turnhead-024 | train | U/P | U/U | recrop | Back view thiếu tay/vùng bài, source có context lớp để draft rộng hơn; không giữ looking P từ class nguồn. |
| SCB-turnhead-026 | train | U/P | U/P | recrop | Đầu quay trái khỏi giấy rõ, tay giơ và người trước lấn khung; có source để thử context giữ tay đầy đủ. |
| SCB-turnhead-027 | train | U/P | N/P | keep | Hai tay trên bàn rõ, mặt/mắt ngẩng khỏi trang dù mắt nheo. |
| SCB-turnhead-028 | train | U/P | U/U | recrop | Back view chỉ vai/đầu trong crop, cần context vùng bài từ source rồi review SHA mới. |
| V7-C-001 | val | U/P | N/P | keep | Tay sát cổ và tay trên bài còn thấy, đầu quay phải khỏi trang. |
| V7-C-003 | train | U/P | N/P | keep | Hai tay trên bài thấy đủ, đầu quay ra sau về người xem. |
| V7-C-005 | train | U/P | N/P | keep | Hai tay khoanh rõ, đầu quay phải khỏi vùng bài. |
| V7-C-007 | val | U/P | U/P | keep | Đầu quay trái rõ, tay/vùng dưới bàn bị crop/người trước che. |
| V7-C-009 | val | U/P | U/P | keep | Đầu quay ra sau trái rõ, một tay sát mặt nhưng tay kia không thấy đủ. |
| V7-C-011 | train | U/P | N/P | keep | Tay chống má và tay trên bài rõ, mặt ngẩng ngoài giấy. |
| V7-C-013 | train | U/P | N/U | keep | Hai tay đan trên bàn thấy đủ không mobile, mắt/hướng nhìn không đủ rõ để chốt khỏi bài. |
| V7-C-015 | train | U/N | U/P | keep | Đầu quay sang người bên phải rõ, tay bị người trước/vùng bàn che. |
| V7-C-016 | val | U/N | U/N | keep | Trong crop còn trang sách ngay trước mặt và head/profile hướng vào đó, đủ looking N; tay vẫn che nên phone U. |
| V7-C-017 | val | U/P | U/P | keep | Đầu quay trái rõ, tay/vùng giấy bị đầu người trước che. |
| V7-C-019 | train | U/P | U/U | recrop | Đầu hướng trái nhưng bài/đích thiếu trong crop, source có thể thêm vùng bàn; chưa giữ P theo taxonomy. |
| V7-C-021 | train | U/P | U/P | keep | Sau mở lại thấy đầu ngẩng/quay khỏi vùng bài, không phải mặt gục trên tay; tay vẫn thiếu evidence absence. |
| V7-C-023 | val | U/P | U/N | keep | Hướng đầu vào trang trước thân còn diễn giải được, tay bị người trước che; không giữ P chỉ vì nghiêng đầu. |
| V7-C-033 | train | U/P | N/P | keep | Hai tay khoanh trên bàn thấy đủ, mặt quay trái/ngẩng ngoài bài. |
| V7-C-035 | train | U/P | U/P | recrop | Person box bao nhiều người, cần chọn anchor đơn; head/tay người khác không được dùng chung. |
| V7-C-039 | train | U/P | U/P | keep | Đầu quay ra sau trái rõ, tay ở bàn bị thân/ghế che nên absence thiếu. |
| V7-C-041 | train | U/P | N/N | keep | Hai tay cầm giấy/bút đủ thấy, đầu hướng tờ giấy đang giữ; không P chỉ vì giấy được dựng. |
| V7-C-043 | train | U/P | U/P | recrop | Anchor hàng sau nhìn ngoài bài, tay bị đầu người trước che; cần thử context cô lập, không lấy tay người trước. |
| V7-C-047 | train | U/P | U/P | recrop | Person box bao hai người và crop mất đầu người sau, cần box/context một anchor để tránh nhãn mâu thuẫn. |
| V7-C-049 | train | U/P | N/P | keep | Hai tay đặt/đan trên đùi rõ, mặt hướng người xem ngoài vùng bài. |
| V7-C-051 | train | U/P | N/P | keep | Hai tay trên giấy/bút thấy đủ, đầu quay sang người bên phải. |
| V7-C-053 | train | U/P | U/P | keep | Tay giơ cao rõ nhưng tay còn lại dưới bàn mất evidence, đầu ngẩng ngoài vùng bài. |
| V7-C-093 | train | U/N | N/P | keep | Hai tay trên giấy rõ, đầu quay về người cạnh ngoài trang riêng. |
| V7-C-094 | val | U/N | N/N | keep | Hai tay viết/giữ trang nhìn được, đầu hướng bài riêng. |
| V7-OE-S086-A01 | train | U/P | U/P | recrop | Person box bao nhóm và tay giơ ra biên, cần box đơn/context theo anchor. |
| V7-OE-S087-A01 | train | N/N | N/N | recrop | Person box bao hai người viết, cần box đơn; hai tay/bài còn đủ evidence ở từng người. |
| V7-OE-S088-A01 | train | U/N | U/N | keep | Đầu hướng sách đang đọc, một tay dưới bàn/khuất ngoài khung nên absence thiếu. |
| V7-OE-S089-A01 | train | U/N | U/U | recrop | Person box bao nhóm nhiều người với đích khác nhau, chưa có một target RGB rõ; cần chọn box đơn trước. |
| V7-OE-S090-A01 | train | U/N | U/N | recrop | Person box bao hai người/vật cầm mờ, cần anchor đơn; không auto phone P từ cử chỉ. |
| V7-OE-S091-A01 | train | U/N | N/P | recrop | Person box bao nhiều người và người đứng, cần anchor đơn để giữ hướng nhìn ra ngoài bài. |
| V7-R8-C-003 | train | U/P | N/P | keep | Hai tay cầm bút/giữ giấy rõ, đầu quay ra sau khỏi trang. |
| V7-R8-C-006 | train | U/N | N/N | keep | Tay viết và tay giữ trang thấy được, đầu cúi vào bài; bàn tay tiền cảnh không phải evidence anchor. |
| EXP-SCB-001 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| EXP-SCB-002 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy được, đầu hướng trang riêng. |
| EXP-SCB-005 | val | N/P | N/P | keep | Hai tay khoanh rõ, đầu quay phải khỏi bài. |
| EXP-SCB-009 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| EXP-SCB-010 | train | N/P | N/P | keep | Hai tay giữ tờ giấy rõ, mắt ngẩng khỏi giấy. |
| EXP-SCB-011 | train | U/N | N/N | keep | Hai tay giữ giấy thấy được, đầu hướng tờ giấy đang đọc; ảnh nhỏ nhưng đích rõ. |
| EXP-SCB-012 | train | U/N | N/N | keep | Hai tay khoanh trên bàn thấy được, đầu hướng giấy trước thân. |
| EXP-SCB-013 | train | U/N | N/N | keep | Hai tay khoanh trên bàn nhìn được, đầu hướng giấy riêng. |
| EXP-SCB-014 | val | N/P | N/N | keep | Hai tay khoanh rõ, đầu hướng trang giấy trên bàn, không vật mơ hồ. |
| EXP-SCB-015 | train | N/U | N/U | keep | Tay che mặt và tay sát ngực quan sát được không vật lạ, hướng mắt/đích bị che nên looking U. |
| EXP-SCB-016 | train | N/N | N/N | keep | Hai tay giữ giấy rõ, đầu hướng trang riêng. |
| EXP-SCB-017 | train | U/N | U/U | exclude | Đầu úp khuất trong hood, tay và đích bị chồng sách che trong cùng source; không có known target chắc. |
| EXP-SCB-020 | train | N/N | N/N | keep | Hai tay đan trên giấy rõ, đầu hướng vùng bài riêng. |
| EXP-SCB-025 | train | N/N | N/N | keep | Hai tay viết/giữ trang nhìn được, đầu hướng bài riêng. |
| EXP-SCB-026 | train | N/N | N/N | keep | Hai tay khoanh trên bàn thấy rõ, mặt hướng trang sách trước thân. |
| EXP-SCB-027 | train | N/N | N/N | keep | Tay chống má và tay giữ sách rõ, đầu hướng trang riêng. |
| EXP-SCB-028 | train | N/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng bài riêng. |
| EXP-SCB-034 | train | N/U | N/P | keep | Hai tay bút/giấy thấy được, đầu ngẩng trái ngoài trang. |
| EXP-SCB-042 | train | N/P | N/N | keep | Hai tay khoanh rõ, đầu hướng trang trước thân. |
| EXP-SCB-043 | train | N/U | U/N | keep | Tablet lớn không là mobile, một tay sau tablet không thấy đủ; đầu hướng tablet. |
| EXP-SCB-044 | val | N/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng bài riêng. |
| EXP-SCB-048 | train | U/N | U/U | recrop | Back view và tờ giấy chỉ lộ một phần, cần context mới cho vùng bài; không giữ looking N theo class read. |
| SCB-read-001 | train | U/N | N/N | keep | Hai tay khoanh trên bàn thấy được, đầu hướng sách riêng. |
| SCB-read-003 | val | U/N | U/N | keep | Góc sau đầu hướng trang riêng còn thấy, một tay/vùng bàn bị khuất nên phone U. |
| SCB-read-004 | train | U/N | N/N | keep | Hai tay khoanh/giữ trang rõ, đầu hướng sách riêng. |
| SCB-read-005 | val | U/N | N/N | keep | Hai tay khoanh nhìn được, đầu hướng trang trước thân; ảnh nhỏ vẫn có quan hệ đầu/bài. |
| SCB-read-006 | train | U/N | U/U | exclude | Native/source đều quá ít chi tiết và bị đầu người trước che tay/vùng bài, nới không phục hồi evidence. |
| SCB-read-007 | val | U/N | U/N | keep | Đầu hướng sách đang giữ, tay/vùng sau sách mờ/che chưa đủ absence. |
| SCB-read-008 | val | U/N | U/U | recrop | Person box/crop chứa hai người, tay/bài bị che; cần xác định một anchor và context mới từ source. |
| SCB-read-009 | train | U/N | U/U | exclude | Mặt mờ và vùng tay/bài bị người trước che ngay source, không phục hồi evidence bằng nới crop. |
| SCB-read-010 | val | U/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng bài riêng. |
| SCB-read-012 | train | U/N | N/U | keep | Tay chống má và tay giữ sách thấy đủ, đầu/mắt chưa xác định đích chắc ở input. |
| SCB-read-013 | val | U/N | U/U | exclude | Native 61 × 56, mặt/tay mất chi tiết, thiếu đích nhìn và absence. |
| SCB-read-014 | train | U/N | U/U | exclude | Tay che gần toàn mặt và tay còn lại khuất, chưa đủ phone absence hoặc gaze; không còn known target. |
| SCB-read-015 | train | N/N | N/N | keep | Hai tay giữ/đọc trang thấy đủ, đầu hướng giấy riêng. |
| SCB-read-016 | val | U/N | U/U | exclude | Native 38 × 54, tay/mặt quá mờ và che, không đủ hai target. |
| SCB-read-017 | val | U/N | U/U | exclude | Native 34 × 40, mặt và tay không có chi tiết nhận định hai target. |
| SCB-read-019 | val | U/N | U/N | keep | Kiểm lại source/native/input: đầu hướng vùng trang mở ngay trước người đủ rõ, không cần thấy con ngươi; tay còn bị che nên phone U. Không loại chỉ vì native 47 × 69. |
| SCB-read-020 | train | U/N | N/N | keep | Hai tay giữ trang thấy đủ, đầu hướng bài đang đọc. |
| SCB-read-021 | train | U/N | N/N | keep | Hai tay khoanh rõ trên bàn, đầu hướng sách đang mở. |
| SCB-read-022 | val | U/N | U/U | exclude | Mặt/tay bị người trước che và source cũng mờ, không đủ hai target ổn định. |
| SCB-read-023 | train | U/N | N/N | keep | Hai tay khoanh trên bàn thấy được, đầu hướng trang riêng. |
| SCB-read-025 | train | U/N | U/N | keep | Đầu hướng giấy nhưng tay bị người trước che và native nhỏ; absence chưa đủ. |
| SCB-read-026 | train | U/N | U/U | exclude | Native 35 × 29, không đủ chi tiết nhận hands/gaze/object. |
| SCB-read-027 | train | U/N | U/N | keep | Đầu hướng sách đang cầm, một tay ngoài vùng quan sát nên absence thiếu. |
| SCB-read-028 | train | U/N | U/N | keep | Đầu hướng trang riêng ở góc sau, tay xa bị thân che nên phone U. |
| SCB-write-001 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy đủ, đầu hướng trang riêng. |
| SCB-write-002 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| SCB-write-004 | train | U/N | U/N | keep | Đầu hướng trang, tay/vùng bàn bị đầu người trước che nên thiếu absence. |
| SCB-write-005 | val | U/N | U/U | exclude | Native 53 × 40, đầu và tay mờ/che, không đủ hai target. |
| SCB-write-006 | train | N/N | N/N | keep | Hai tay viết/giữ trang thấy đủ, đầu hướng trang sách sát mặt. |
| SCB-write-007 | train | U/N | U/N | keep | Đầu hướng bài nhưng tay bị đầu người trước che, không đủ absence. |
| SCB-write-008 | val | U/N | U/N | keep | Đầu hướng vùng viết, tay/vật nhỏ mờ thiếu evidence absence chắc. |
| SCB-write-009 | train | N/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng bài riêng. |
| SCB-write-010 | val | U/N | N/N | keep | Hai tay viết/giữ sách thấy đủ, đầu hướng trang riêng. |
| SCB-write-011 | train | U/N | U/N | keep | Đầu hướng trang nhưng tay bị đầu người trước che, absence thiếu. |
| SCB-write-012 | train | U/N | N/N | keep | Hai tay viết/giữ trang thấy được, đầu hướng sách riêng. |
| SCB-write-013 | train | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng bài riêng. |
| SCB-write-014 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy được, đầu hướng trang. |
| SCB-write-016 | train | U/N | N/N | keep | Hai tay bút/trang còn thấy dù native nhỏ, đầu hướng giấy; không dùng kích thước đơn lẻ để loại. |
| SCB-write-017 | train | U/N | U/N | keep | Đầu hướng giấy nhưng một tay bị đầu người trước che, absence thiếu. |
| SCB-write-018 | train | U/N | N/N | keep | Hai tay giữ/đọc sách rõ, đầu hướng sách riêng. |
| SCB-write-019 | train | U/N | U/N | keep | Đầu hướng vùng viết nhưng tay/vật rất nhỏ mờ và cắt khuất, không đủ absence. |
| SCB-write-020 | train | U/N | N/N | keep | Hai tay viết/giữ giấy nhìn được, đầu hướng bài riêng. |
| SCB-write-021 | train | U/N | N/N | keep | Hai tay viết/giữ trang thấy được, đầu hướng sách; gần biến thể write-012 cần kiểm lặp. |
| SCB-write-022 | train | U/N | U/U | exclude | Native 45 × 42, mặt/tay bị mờ mất cấu trúc, không đủ hai target. |
| SCB-write-023 | train | U/N | N/N | keep | Hai tay đan trên trang thấy đủ, đầu hướng sách trước thân. |
| SCB-write-024 | train | U/N | N/N | keep | Hai tay viết/giữ giấy còn thấy, đầu hướng trang riêng dù ảnh mờ. |
| SCB-write-025 | train | U/N | N/N | keep | Hai tay viết/giữ sách thấy được, đầu hướng trang riêng. |
| SCB-write-027 | train | U/N | N/N | keep | Hai tay viết/giữ trang còn thấy, đầu sát giấy riêng; không tự nhìn ngoài bài từ nghiêng đầu. |
| SCB-write-028 | train | U/N | N/N | keep | Hai tay viết/giữ trang thấy đủ, đầu hướng bài riêng. |
| V7-C-002 | val | U/N | U/N | recrop | Person box bao hai người đọc, cần box đơn và context; không dùng hands của người khác xác nhận absence. |
| V7-C-004 | train | U/N | U/N | recrop | Person box bao nhiều người và cắt tay, cần box đơn/context mới theo source. |
| V7-C-006 | val | U/N | N/N | recrop | Person box bao nhiều người viết, cần anchor đơn; giữ rõ đầu/tay/bài của người được chọn trong crop mới. |
| V7-C-008 | val | U/N | N/N | keep | Hai tay giữ sách rõ, đầu hướng trang riêng; người trước chỉ che phần rìa. |
| V7-C-010 | train | U/N | N/N | recrop | Person box bao hai người đọc/viết, cần tách anchor, không gán nhãn nhóm thành người. |
| V7-C-018 | train | U/N | N/N | keep | Hai tay viết/giữ giấy nhìn được, đầu hướng trang riêng. |
| V7-C-026 | train | U/N | U/N | keep | Vùng tay sát mặt quá mờ không đủ phân loại/absence, đầu vẫn hướng trang riêng; không truyền N từ source class. |
| V7-C-028 | train | U/N | U/N | recrop | Person box bao nhiều người, tay/giấy chồng che; cần chọn một anchor và context mới. |
| V7-C-030 | train | U/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng sách riêng. |
| V7-C-038 | train | U/N | N/N | keep | Hai tay giữ trang thấy đủ, đầu hướng sách riêng. |
| V7-C-042 | train | U/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| V7-C-044 | train | U/N | N/N | keep | Hai tay khoanh trên bàn rõ, đầu hướng bài trước thân. |
| V7-C-046 | val | U/N | N/N | recrop | Person box bao nhiều người đọc, cần box đơn; evidence đầu/tay của mỗi người xét riêng. |
| V7-C-048 | val | U/N | U/N | keep | Túi mềm trên bàn không mobile, nhưng tay sau túi bị che; đầu hướng vùng bài riêng. |
| V7-C-050 | train | U/N | N/U | keep | Tay sát mặt và tay khoanh trên bàn đủ review absence, đích nhìn bị tóc/mặt che nên looking U. |
| V7-C-052 | train | U/N | N/N | keep | Hai tay khoanh rõ, đầu hướng trang sách riêng. |
| V7-C-054 | val | U/N | N/N | keep | Hai tay giữ/đọc sách rõ, đầu hướng bài riêng. |
| V7-OE-S093-A01 | train | N/N | U/U | recrop | Person box là nhóm đông có gaze khác nhau, chưa có một anchor RGB rõ; cần khung mới trước dùng supervision. |
| V7-OE-S094-A01 | val | U/P | N/P | keep | Tay sát mặt và tay trên bàn đủ thấy, mặt ngẩng ngoài trang riêng. |
| V7-OE-S096-A01 | train | N/N | N/N | keep | Hai tay giữ trang thấy đủ, đầu hướng sách riêng. |
| V7-OE-S099-A01 | train | N/N | U/U | recrop | Person box bao hai người có hướng nhìn khác nhau, cần anchor đơn trước gán target cho RGB crop. |
| V7-OE-S101-A01 | train | U/N | N/N | keep | Hai tay viết/giữ giấy thấy đủ, đầu hướng trang riêng. |
| V6-SB-003 | train | P/U | U/N | keep | Thiết bị trên giấy chỉ là khối đen nhỏ mờ, không đủ mobile identity ở input; đầu hướng vùng tay. |
| V6-SB-004 | train | P/U | U/N | keep | Mặt lưng bạc thiếu camera/đặc trưng phân biệt tại input, đầu hướng tay; không suy từ kiểu cầm. |
| V6-SB-005 | train | P/U | U/N | keep | Chỉ cạnh/lưng thiết bị trong tay thiếu phone identity ở input, đầu hướng vật. |
| V6-SB-008 | train | P/U | U/N | keep | Vật trắng nhỏ trong tay không giữ đặc trưng mobile tại input, đầu hướng vật. |
| V6-SB-009 | train | P/N | P/N | keep | Mobile mặt kính/viền dưới tay trên bàn vẫn nhận được tại 224, đầu hướng máy/bài riêng. |
| V6-SB-010 | train | P/N | P/N | keep | Mobile viền tím/mặt kính trên bàn vẫn có cấu trúc phân biệt, đầu hướng vùng máy/bài riêng. |
| V6-SB-011 | train | U/N | U/N | keep | Vật nhỏ trên sách dưới tay không giữ phone identity ở input, đầu hướng trang; không nâng P từ source xa. |
| V6-SB-012 | train | U/N | N/N | keep | Hai tay giữ/đọc sách thấy được, đầu hướng trang riêng. |
| V6-SB-013 | train | P/U | P/N | keep | Mobile viền đỏ/mặt kính dưới tay trên bàn rõ, đầu hướng thiết bị riêng. |
| V6-SB-014 | train | P/U | U/N | keep | Mặt lưng đen trong hai tay không đủ camera/mặt máy phân biệt ở input, đầu hướng vật. |
| V6-SB-015 | train | P/U | U/N | keep | Vật đen trên bàn quá mờ, không đủ phân biệt mobile/calculator, đầu hướng thao tác. |
| V6-SB-016 | train | P/U | U/P | keep | Lưng bạc thiếu camera/mặt máy phân biệt tại input, mặt ngẩng ra trước khỏi vật. |
| V6-SB-018 | train | U/P | U/U | exclude | Tay bị người trước che, mặt/hướng nhỏ mờ và thiếu vùng bài, không đủ hai target. |
| V6-SB-019 | train | U/P | U/P | keep | Đầu quay phải rõ, hai tay dưới bàn/cắt đáy nên absence thiếu. |
| V6-SB-021 | train | U/P | U/U | exclude | Native 48 × 65 cắt mất đầu và tay bị ghế che, không đủ hai target. |
| V6-SB-022 | train | U/P | U/P | keep | Đầu quay phải rõ, tay/vật nhỏ dưới bàn quá mờ để xác nhận absence. |
| V6-SB-023 | train | U/P | P/P | keep | Mobile mặt kính trên bàn riêng rõ, đầu quay trái ngoài máy/vùng bài. |
| V6-SB-028 | train | U/P | U/P | keep | Đầu quay trái rõ, tay dưới bàn/cắt khuất nên phone U. |
| V6-SB-029 | train | N/P | N/P | keep | Hai tay đan trên bài thấy đủ, đầu quay trái khỏi trang. |
| V6-SB-030 | train | P/P | P/P | keep | Mobile mặt kính trên bàn rõ, đầu quay phải khỏi vùng máy. |
| V6-SB-032 | train | U/P | U/P | keep | Mảnh đen dưới sách không đủ mobile identity, một tay khuất, đầu quay trái khỏi trang. |
| V6-SB-033 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| V6-SB-034 | val | N/N | N/N | keep | Hai tay viết/giữ bài nhìn được, đầu hướng trang riêng. |
| V6-SB-035 | val | N/N | U/N | keep | Đầu hướng sách đang dựng, một tay sau sách không thấy đủ absence. |
| V6-SB-038 | train | N/N | N/N | keep | Hai tay giữ/đọc giấy rõ, đầu hướng trang riêng. |
| V6-SB-040 | val | N/N | N/N | keep | Hai tay khoanh rõ, đầu hướng sách trước thân; nhiễu hạt ảnh không tự positive. |
| V6-SB-041 | val | N/N | N/N | keep | Tay sát mặt và tay giữ trang đủ thấy, đầu nhìn sách riêng. |
| V6-SB-042 | val | N/N | N/N | keep | Đích nhìn vẫn vào trang/sách riêng, không tự P vì mặt hơi ngẩng; hai tay bút/trang rõ không vật lạ. |
| V6-SB-043 | val | N/N | N/N | keep | Hai tay đọc/giữ trang rõ, đầu hướng bài riêng. |
| V6-SB-044 | val | N/N | U/U | recrop | Person box bao nhiều người/back view, cần box đơn/context trước supervision; không dùng gaze người sau cho người trước. |
| V6-SB-045 | val | N/N | N/N | keep | Hai tay giữ sách rõ, đầu hướng trang riêng. |
| V6-SB-046 | val | N/N | N/N | keep | Tay sát ngực và tay viết thấy đủ, đầu hướng giấy riêng. |
| V6-SB-047 | val | N/N | N/P | keep | Hai tay trên bài thấy đủ, đầu quay trái ngoài trang. |
| V6-SB-048 | val | N/N | U/P | keep | Đầu quay sang phải ngoài trang rõ, tay/vùng dưới bàn và người cạnh che nên absence thiếu. |
| V6R2-MP-001 | train | N/N | N/N | keep | Tay chống đầu và tay giữ trang thấy được, đầu hướng giấy riêng. |
| V6R2-MP-002 | train | N/N | N/N | keep | Tay chống đầu và tay giữ giấy nhìn được, đầu hướng bài riêng. |
| V6R2-MP-004 | train | U/P | N/P | keep | Tay chống cổ và tay trên trang thấy được không vật lạ, mặt ngẩng khỏi bài. |
| V6R2-MP-005 | train | U/P | N/P | keep | Hai tay khoanh thấy được không vật mơ hồ, đầu ngẩng ngoài trang. |
| V6R2-MP-006 | train | U/P | U/P | keep | Vật trên sách chỉ còn khối đen nhỏ không đủ mobile identity ở input, mặt ngẩng khỏi bài. |
| V6R2-MP-007 | train | U/P | U/P | keep | Mặt ngẩng khỏi trang, hai tay dưới bàn/cắt đáy không đủ absence. |
| V6R2-MP-008 | train | U/P | U/U | exclude | Source đã cắt mất mặt ở mép trái, không có pixels recrop để cứu hướng nhìn; tay/thiết bị cũng thiếu, U/U. |
| V6R2-MP-009 | train | P/U | U/N | keep | Thiết bị đen cầm hai tay thiếu đặc trưng mobile tại input, đầu hướng vật. |
| V6R2-MP-010 | train | P/U | U/N | keep | Vật cầm chỉ còn mặt/lưng mờ không đủ mobile, đầu hướng vật. |
| V6R2-MP-011 | train | P/U | U/N | keep | Mặt lưng/cạnh đỏ không đủ phân biệt phone ở input, không nhận bằng màu vỏ; đầu hướng tay. |
| V6R2-MP-012 | train | P/P | P/P | keep | Mobile mặt kính viền sáng trên bàn rõ, mặt ngẩng ngoài giấy. |
| V6R2-MP-013 | train | P/P | P/P | keep | Mobile mặt kính trên bàn rõ, mặt ngẩng ngoài trang riêng. |
| V6R2-MP-014 | train | U/N | U/U | exclude | Đầu cúi che mặt, đích dưới bàn/trang chưa rõ và tay dưới bàn thiếu absence; không còn known target chắc. |
| V6R2-MP-016 | train | U/P | N/P | keep | Tay sát cằm và tay trước thân thấy đủ không vật mơ hồ, mặt ngẩng ngoài giấy. |
| V6R2-MP-018 | train | U/P | U/N | keep | Đầu hướng trang riêng, hai tay dưới bàn không thấy đủ absence. |
| V6R2-MP-019 | train | N/N | N/N | keep | Tay chống đầu và tay giữ trang nhìn được, đầu hướng giấy riêng. |
| V6R2-MP-020 | train | N/N | N/N | keep | Hai tay đan trên giấy thấy đủ, đầu hướng trang riêng. |
| V6R2-MP-021 | train | U/N | U/N | keep | Đầu hướng giấy đang đọc, hai tay/vùng bàn cắt khuất thiếu absence. |
| V6R2-MP-022 | train | U/P | U/P | keep | Tay che mặt rõ nhưng tay kia dưới bàn, mắt ngẩng ngoài bài. |
| V6R2-MP-023 | train | U/P | U/P | keep | Tay sát miệng nhưng tay kia dưới bàn/khuất, mặt ngẩng ngoài trang. |
| V6R2-MP-024 | train | N/P | N/P | keep | Hai tay giữ sách rõ, đầu quay trái khỏi sách đang cầm. |
| V6R2-MP-025 | train | N/N | U/N | keep | Tay mouse rõ nhưng tay kia sau laptop, đầu hướng màn hình riêng. |
| V6R2-MP-026 | train | N/N | N/N | keep | Hai tay giữ/giở giấy rõ, đầu hướng trang riêng. |
| V6R2-MP-030 | train | P/U | U/N | keep | Thiết bị nhỏ mờ trong tay mất đặc trưng mobile, đầu hướng vùng thao tác. |
| V6R2-MP-031 | train | P/U | P/N | keep | Thiết bị mặt kính/viền dưới tay trên bàn còn đủ nhận mobile ở input, đầu hướng máy. |
| V6R2-MP-032 | train | P/U | N/N | keep | Hai tay viết/giữ giấy thấy được, đầu hướng trang riêng. |
| V6R2-MP-034 | train | P/U | U/N | keep | Vật nhỏ cầm trong tay chỉ còn mặt/lưng mờ, không đủ phone identity; đầu hướng tay. |
| V6R2-MP-035 | train | P/U | U/N | keep | Thiết bị nhỏ mặt lưng mờ không đủ phone identity tại input, đầu hướng tay. |
| V6R2-MP-037 | train | U/P | U/P | keep | Mặt ngẩng ngoài trang, hai tay dưới bàn/cắt đáy thiếu absence. |
| V6R2-MP-038 | train | P/P | P/P | keep | Mobile mặt kính viền sáng trên bàn rõ, đầu hướng trái ngoài trang. |
| V6R2-MP-039 | train | N/P | N/P | keep | Hai tay đan trên giấy rõ, đầu quay trái ngoài vùng bài. |
| V6R2-MP-040 | train | P/U | U/N | keep | Vật trong hai tay chỉ còn cạnh/lưng mờ không đủ nhận mobile tại input; đầu hướng tay trên sách. |
| V6R2-MP-041 | train | N/N | U/N | keep | Đầu hướng trang và tay viết; tay còn lại bị người cạnh che nên không khẳng định phone absence. |
| V6R2-MP-043 | train | P/P | P/P | keep | Mobile mặt kính trên bàn riêng rõ, mặt ngẩng ngoài bài. |
| V6R2-MP-044 | train | U/P | U/P | keep | Mặt ngẩng hướng lên ngoài bàn, tay/vùng dưới bàn cắt khuất. |
| V6R2-MP-046 | train | P/U | P/N | keep | Thiết bị mặt kính có viền trên giấy riêng còn nhận mobile tại input; đầu hướng trang và máy. |
| V6R2-MP-047 | train | U/P | U/P | keep | Đầu ngẩng ngoài trang, hai tay dưới bàn không thấy đủ. |
| V6R2-MP-048 | train | U/P | N/P | keep | Tay sát miệng và tay cầm bút thấy đủ không vật mơ hồ, mắt hướng ngoài giấy. |
| V6R2-MP-049 | train | U/P | N/P | keep | Hai tay giữ sách thấy được, mặt ngẩng khỏi trang. |
| V6R2-MP-050 | train | U/P | U/P | keep | Mặt ngẩng ngoài bài, bàn tay dưới khung/ghế thiếu evidence absence. |
| V6R2-MP-053 | train | P/U | U/P | keep | Thiết bị cầm chỉ còn cạnh/mặt mờ, không đủ mobile identity tại input; mặt ngẩng khỏi vùng bài. |
| V6R2-MP-057 | train | U/P | N/N | keep | Hai tay giữ sách/giấy thấy được, đầu hướng trang riêng. |
| V6R2-MP-058 | train | U/P | U/N | keep | Đầu hướng giấy riêng, tay dưới bàn/khuất thiếu evidence absence. |
| V6R2-MP-059 | train | U/P | N/N | keep | Tay sát thái dương và tay giữ giấy rõ, đầu hướng trang riêng. |
| V6R2-MP-061 | train | U/P | U/P | keep | Mặt ngẩng ngoài bài, tay/vùng thấp bị ghế/crop che. |
| V6R2-MP-063 | train | U/N | U/N | keep | Đầu hướng trang, tay phía trái bị cắt ngoài crop nên phone U. |
| V6R2-MP-066 | train | P/P | U/P | keep | Thiết bị cầm thiếu mặt kính/camera phân biệt ở input; đầu quay sang người bên cạnh. |
| V6R2-MP-067 | train | P/P | P/P | keep | Mobile mặt kính trên bàn rõ, mặt ngẩng ngoài giấy. |
| V6R2-MP-068 | train | P/U | U/N | keep | Mặt lưng đen trong tay không đủ đặc trưng mobile ở input; đầu hướng vật. |
| V6R2-MP-072 | train | U/P | N/P | keep | Hai tay bút/giấy thấy được, mặt ngẩng ngoài trang. |
| V6R2-MP-073 | train | U/P | N/P | keep | Hai tay đan rõ trên bài, đầu ngẩng khỏi trang riêng. |
| V6R2-MP-074 | train | U/N | U/N | keep | Đầu nghiêng xuống bài, tay phía dưới cắt/khuất nên absence thiếu. |
| V6R2-MP-079 | train | P/U | U/N | keep | Thiết bị mặt lưng mờ cầm trước ngực không đủ mobile identity; đầu hướng vật. |
| V6R2-MP-080 | train | P/U | P/N | keep | Mobile viền đỏ/mặt kính dưới tay trên bàn rõ, đầu nhìn máy. |
| V6R2-MP-081 | train | P/P | P/P | keep | Mobile mặt kính viền sáng trên bàn rõ, đầu ngẩng ngoài giấy. |
| V6R2-MP-084 | train | P/U | U/N | keep | Vật đen trong hai tay không giữ mặt kính/camera phân biệt ở input; đầu hướng thao tác. |
| V6R2-MP-085 | train | P/U | U/N | keep | Mặt lưng xám/đen thiếu đặc trưng phân biệt mobile ở input; đầu hướng tay. |
| V6R2-MP-089 | train | P/U | U/N | keep | Vật cầm trước người quá mờ không đủ phone identity ở input; đầu hướng tay. |
| V6R2-MP-090 | train | P/U | N/N | keep | Hai tay viết/giữ trang thấy được, đầu hướng giấy riêng. |
| V6R2-MP-091 | train | N/P | U/P | keep | Tay mouse rõ nhưng tay kia sau laptop, đầu quay trái ngoài màn hình. |
| V6R2-MP-092 | train | P/P | P/P | keep | Mobile mặt kính trên bàn cạnh sách rõ, đầu quay phải khỏi trang. |
| V6R2-MP-093 | train | P/U | U/N | keep | Vật đen trong một tay thiếu mobile identity, tay kia chống miệng; đầu hướng vùng tay riêng. |
| V6R2-SB-001 | train | P/U | U/N | keep | Lưng trắng trong tay không đủ camera/đặc trưng mobile ở input; đầu hướng tay. |
| V6R2-SB-002 | train | P/U | U/N | keep | Thiết bị sau người trước bị che và chỉ còn lưng mờ; đầu hướng tay của chính anchor. |
| V6R2-SB-003 | train | P/U | P/P | keep | Mobile mặt kính/viền tím đặt trên trang và tay tương tác còn nhận được tại input; mặt quay lên trái khỏi bài. |
| V6R2-SB-006 | train | P/U | U/N | keep | Lưng vàng trong tay không đủ đặc trưng phone ở input; đầu hướng vùng tay. |
| V6R2-SB-008 | train | U/P | U/P | keep | Mặt ngẩng khỏi bài, hai tay dưới bàn/crop không thấy đủ. |
| V6R2-SB-009 | train | U/N | U/N | keep | Góc méo và native 35 × 100, đầu vẫn hướng trang nhưng tay/vật không đủ chi tiết absence. |
| V6R2-SB-010 | train | U/P | U/P | keep | Thiết bị nhỏ một phần bị che, không đủ phone identity tại input; mặt quay sang trái khỏi tay. |
| V6R2-SB-011 | train | U/P | U/P | keep | Tay và vùng trước thân bị che, đầu quay khỏi vùng bài; không suy vật từ động tác tay. |
| V6R2-SB-013 | val | N/N | N/N | keep | Hai tay đọc/giữ sách thấy đủ, đầu hướng trang riêng; nhiễu hạt không tự đổi nhãn. |
| V6R2-SB-014 | val | N/U | U/N | keep | Đầu hướng trang, tay sát đầu nhưng tay kia dưới bàn/cắt khung thiếu absence. |
| V6R2-SB-015 | val | N/N | N/N | keep | Tay sát má và tay cầm bút trên trang thấy đủ, đầu hướng bài riêng. |
| V6R2-SB-016 | val | U/N | U/N | keep | Vật đen trên bàn bị cắt và mờ không đủ phân biệt phone/tablet; đầu hướng trang. |
| V6R2-SB-017 | val | N/N | N/N | keep | Hai tay viết/giữ trang rõ, đầu hướng giấy riêng. |
| V6R2-SB-018 | train | N/U | N/N | keep | Hai tay giữ/viết trang thấy đủ, đầu hướng sách; visor che trán không tự U khi hướng rõ. |
| V7-B-002 | val | N/N | N/N | keep | Hai tay viết/giữ sách rõ, đầu hướng trang riêng. |
| V7-B-016 | val | N/N | N/N | keep | Anchor nữ viết rõ trên trang riêng, hai tay/vùng thao tác đủ và không có vật lạ; người hai bên không cản attribution. |
| V7-B-018 | val | N/N | N/N | keep | Hai tay giữ/đọc giấy rõ, đầu hướng trang riêng. |
| V7-B-020 | val | N/N | N/N | keep | Hai tay khoanh thấy đủ, đầu hướng vùng bài trước thân. |
| V7-B-022 | val | N/N | N/N | keep | Hai tay viết/giữ giấy thấy được, đầu hướng trang riêng. |
| V7-B-024 | val | N/N | N/P | keep | Hai tay khoanh rõ, mặt ngẩng ngoài trang riêng. |
| V7-B-028 | val | N/N | N/N | keep | Hai tay viết/giữ sách rõ, đầu hướng trang riêng. |
| V7-B-030 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng trang riêng. |
| V7-B-034 | val | N/N | N/N | keep | Hai tay giữ/đọc giấy nhìn được, đầu hướng trang riêng. |
| V7-B-042 | val | N/N | N/N | keep | Hai tay viết/giữ trang thấy được, đầu hướng giấy; watermark đáy cần cờ QA, không che evidence. |
| V7-B-048 | val | N/N | N/N | keep | Hai tay viết/giữ giấy rõ, đầu hướng bài riêng. |
| V7-B-062 | val | N/N | N/N | recrop | Đầu/tay nam ở giữa đọc được nhưng person box bao cả người trước và người sau; cần box đơn, context giữ trang. |
| E004-CN-042 | train | U/P | U/P | keep | Anchor giơ tay nhìn về giáo viên, rõ ngoài vùng bài; tay còn lại dưới bàn nên phone absence chưa đủ. |
| E004-CN-043 | train | U/N | U/N | keep | Đầu hướng bài đang viết, tay xa/vùng dưới bàn cắt khuất thiếu absence. |
| E004-CN-044 | train | N/P | N/P | keep | Tay sát má và tay giữ giấy rõ, đầu quay phải khỏi trang. |
| E004-CN-045 | train | N/P | N/P | keep | Hai tay trên giấy/bút rõ, đầu quay phải khỏi bài. |
| E004-CN-046 | train | U/N | U/N | keep | Đầu hướng bảng/sách dựng, một tay sau vật lớn bị che nên absence thiếu. |
| E004-CN-047 | train | U/N | U/N | keep | Đầu hướng bảng/sách dựng, tay sát mặt và tay còn lại bị che nên absence chưa đủ. |
| E004-CN-048 | val | N/N | N/N | keep | Hai tay giữ sách rõ, đầu hướng tờ bài đang đọc. |
| E004-CN-050 | val | U/N | N/N | keep | Hai tay giữ sách/trang thấy được, đầu hướng trang riêng. |
| E004-CN-052 | train | N/U | N/U | recrop | Person box bao hai nữ, tóc che hoàn toàn mặt anchor sọc; cần box đơn và kiểm lại đích nhìn, không truyền gaze từ người cạnh. |
| E004-CN-053 | train | N/N | N/N | keep | Nữ áo đen là anchor trội, đầu và hai tay hướng trang viết riêng; không cần loại chỉ vì có người cạnh. |
| E004-CN-055 | val | N/N | U/N | keep | Đầu nam hướng trang riêng; một tay và vùng thao tác bị người trước che nên phone absence chưa đủ. |
| E004-CN-056 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy được, đầu hướng bài riêng. |
| E004-EX-C078 | train | P/N | P/N | keep | Mobile mặt kính/viền trong hai tay rõ, đầu hướng máy riêng. |
| E004-EX-C079 | val | P/N | P/N | keep | Mobile mặt kính trong tay trước thân rõ, đầu hướng máy riêng. |
| E004-EX-C080 | train | P/P | P/N | keep | Mobile áp tai rõ, đầu hướng khu vực màn hình/làm việc riêng, không tự looking P vì gọi máy. |
| E004-EX-C082 | train | P/N | P/N | keep | Mobile mặt sau có cụm camera rõ trong tay, đầu hướng máy trên bài riêng. |
| E004-EX-C083 | train | P/N | P/N | keep | Mobile mặt sau có cụm camera rõ, đầu hướng máy trên vùng bài riêng. |
| E004-EX-C084 | train | U/N | N/N | keep | Hai tay cầm cốc/giữ trang thấy đủ không vật mơ hồ, đầu hướng vùng làm riêng. |
| E004-EX-C085 | train | N/N | N/N | keep | Hai tay keyboard rõ, đầu hướng laptop riêng. |
| E004-EX-C089 | train | N/P | U/N | recrop | Person box chứa hai người, nữ trái hướng trang riêng còn nữ phải hướng laptop; cần box đơn và duyệt lại attribution. |
| E004-EX-C102 | train | U/N | U/N | keep | Đầu hướng trang đang viết rõ; ghế che tay/vùng dưới bàn nên phone absence chưa đủ, source không thêm evidence. |
| E004-EX-C179 | val | N/U | N/N | keep | Hai tay làm linh kiện rõ, tablet lớn trên bàn không mobile, đầu hướng vùng thực hành riêng. |
| E004-EX-C183 | train | N/N | N/N | keep | Hai tay viết/giữ giấy thấy đủ, đầu hướng bài riêng. |
| E004-EX-C184 | train | N/U | U/N | keep | Đầu hướng giấy ở góc sau, tay gần thân che khuất thiếu evidence absence. |
| E004-EX-C185 | val | P/U | P/U | keep | Mobile màn hình xanh trên bàn rõ, tóc/mặt che khuất không đủ xác nhận đích nhìn. |
| V7-R8-C-007 | train | U/P | N/P | keep | Hai tay cầm bút/đan trên bàn thấy đủ, mặt ngẩng ngoài bài. |
| V7-R8-C-008 | train | U/N | N/U | keep | Hai tay/cánh tay giữ bút và tựa bàn đủ review absence, mặt gục/nhắm mắt không xác định hướng nhìn. |
