# Quyết định audit R2 — Draft

Thứ tự phone / looking. `keep`: giữ geometry, nhãn là đề xuất. `recrop`: tạm rút crop hiện tại, thử geometry mới và duyệt lại cả hai nhãn. `exclude`: đề xuất rút supervision. Chưa áp dụng vào V11.

[Rubric](RUBRIC.md) · [Tổng quan](README.md) · [Gallery](../../../../data/interim/v11-legacy-crop-audit-20261018-r2/index.html)

| ID | V11 | R2 quan sát | Xử lý | Lý do | Quyết định của owner |
|---|---|---|---|---|
| V6-CA-001 | P/U | U/U | exclude | Source không có đầu của người cầm vật. |
| V6-CA-003 | P/U | U/N | recrop | Hai nữ cùng lớn và cùng vùng tay; cần chọn một anchor. | Loại, vì không thể có cách cắt nào mà không dính 2 người cả |
| V6-CA-004 | P/U | U/N | keep | Không nhận phone từ mặt lưng đen. |
| V6-CA-005 | N/U | N/N | keep | Tablet lớn, hai tay quan sát được. |
| V6-CA-006 | P/U | U/P | keep | Mặt ngẩng khỏi vật cầm, lưng đỏ chưa đủ ID. | U/N |
| V6-CA-009 | P/U | U/N | keep | Lưng xanh trơn không đủ camera. |
| V6-CA-010 | P/U | P/N | keep | Mặt màn hình/viền trong tay còn thấy; kiểm lại nhóm P ở lượt chốt. |
| V6-CA-011 | P/U | U/N | recrop | Hai mặt và vùng tay cạnh tranh. |
| V6-CA-012 | P/U | U/N | keep | Các đốm trên lưng đen không tách được camera chắc. | phone P, vì có thể nhìn được lỗ camera. Crop như nào cho hợp lý nhất thôi | Crop lại cho đỡ dính bạn ngồi cạnh |
| V6-CA-014 | P/U | U/N | keep | Vật cầm chưa có mặt/camera rõ; nữ trái vẫn trội. | Trong frame này tôi thấy có 2 người bên cạnh target anchor cũng có thể trở thành crop. Một là bạn nam bên cạnh P/N, nhưng crop phải không dính bạn nữ. Hai là bạn nữ bên cạnh, phone cần xem xét vì tôi thấy chấm đen của camera, looking_around P |
| V6-CA-015 | P/P | U/P | recrop | Khung person bao nhiều nữ; nữ phải nhìn ra trước. |
| V6-CA-016 | P/U | U/N | keep | Đốm đen trên lưng trắng không đủ mobile ID ở 224. |
| V6-CA-018 | U/P | N/P | keep | Tay khoanh đủ đọc, quay sang trái khỏi bàn. |
| V6-CA-021 | N/P | N/P | keep | Hai tay trên bàn, mặt quay sang trái. |
| V6-CA-023 | N/N | N/N | recrop | Nam giữa cầm giấy; nữ trái còn mặt/thân ngang vai trò. |
| V6-CA-025 | N/P | N/P | keep | Đầu hướng bài/người cạnh bên, không phải own-paper. | U/P, vì tay bị cắt mất, nếu recrop được rõ hết bộ phận thì xem xét lại |
| V6-CA-026 | N/U | U/N | keep | Vật xanh nhỏ trong tay không đủ nhận dạng. | N/P, vật xanh rõ ràng là sách/vở |
| V6-CA-028 | N/P | N/P | keep | Hai tay vùng giấy rõ, mặt quay phải khỏi trang. |
| V6-CA-030 | N/P | N/P | keep | Tay/bàn rõ, đầu quay phải khỏi vùng bàn riêng. | U/P, crop bị cắt mất tay, nếu recrop được rõ hết bộ phận thì xem xét lại |
| V6-CA-031 | N/N | N/P | keep | Nữ trái nhìn sang vùng bài bên phải. |
| V6-CA-033 | N/U | U/U | exclude | Vật hồng mơ hồ còn lộ; đầu úp che mặt. |
| V6-CA-035 | U/N | U/N | keep | Đầu vào trang, tay/vùng dưới bàn khuất. |
| V6-CA-036 | N/U | U/U | exclude | Tay và mặt bị đầu che, không có known target. |
| V6-CA-037 | N/U | U/U | exclude | Nằm gục, mặt/tay mất; không suy từ tư thế ngủ. |
| V6-CA-038 | P/U | U/U | exclude | Thiết bị trên sách không đủ ID tại input, mắt nhắm. |
| V6-CA-040 | N/U | U/U | exclude | Đầu úp và tay che, thiếu evidence hai target. |
| V6-CA-043 | N/U | U/U | exclude | Đầu úp, tay ngoài bàn, không cứu bằng nới source. |
| V6-CA-046 | P/U | U/U | exclude | Thiết bị đen bị mép source cắt, không chắc phone; mắt nhắm. |
| V6-CA-047 | P/U | U/N | keep | Hướng nhìn trang rõ, tay một phần bị vật tiền cảnh che. |
| V6R2-CA-001 | P/U | N/P | keep | Cầm bút, tay chống má thấy đủ, mặt ngẩng ra trước. | U/N, tay đưa gần má là đang cầm vật màu đen đó chắc chắn là phone rồi và tư thế giống nghe điện thoại. Mắt vẫn hướng own-paper |
| V6R2-CA-002 | P/U | U/N | keep | Vật trong tay chỉ cạnh/lưng trơn, đầu hướng vật trên trang. |
| V6R2-CA-003 | P/N | U/N | keep | Góc từ trên thấy đầu vào giấy viết; tay còn lại dưới bàn. | P/N |
| V6R2-CA-004 | P/U | U/N | keep | Lưng vàng thiếu camera/màn hình; người sau nhỏ hơn không lấy nhãn của họ. | P/N |
| V6R2-CA-006 | P/U | U/U | exclude | Vật đen nằm bàn chưa đủ ID, tay che gần hết mặt. |
| V6R2-CA-007 | U/P | U/P | keep | Mặt quay sang phải, vùng tay dưới bàn không đủ absence. |
| V6R2-CA-008 | U/N | U/N | recrop | Nữ trái hướng trang, người sau và tay chồng; cần cô lập anchor. | Frame gốc của crop có thể tận dụng, tôi thấy có rất nhiều crop hữu ích. Hãy phân tích kỹ frame này sau đó đề xuất thêm nhiều crop ngon nhất có thể |
| V6R2-CA-009 | P/P | U/P | recrop | Vật đen trên giấy chưa đủ ID; person box bao cả phần nữ phải. |
| V6R2-CA-010 | U/P | U/P | keep | Mặt quay phải khỏi vùng bàn, bàn tay ngoài khung. |
| V6R2-CA-012 | P/U | P/N | keep | Mobile mặt kính/viền trên trang riêng và tay tương tác rõ. |
| V6R2-CA-014 | N/U | N/U | keep | Tay khoanh đủ absence; đầu nghiêng, mắt/đích không đủ chắc. |
| V7-A-001 | P/U | P/N | keep | Mặt màn hình sáng lớn và viền máy trên trang, đầu hướng trang. |
| V7-A-002 | P/N | P/N | keep | Phone trên trang riêng, calculator ở bên; đầu hướng bài. |
| V7-A-003 | P/U | P/N | keep | Mặt kính và viền phone trắng trên sách còn rõ tại input. |
| V7-A-004 | N/N | U/N | recrop | Vật đen trên bài thiếu ID; đầu người tiền cảnh chiếm đáy. | Frame gốc của crop có thể tận dụng, tôi thấy có rất nhiều crop hữu ích. Hãy phân tích kỹ frame này sau đó đề xuất thêm nhiều crop ngon nhất có thể |
| V7-A-005 | P/U | P/N | keep | Mobile mặt trước trên bàn riêng cạnh bàn phím, đầu hướng vùng máy. |
| V7-A-035 | P/N | U/N | keep | Vật ngang cầm tay không đủ phân biệt phone/tablet ở 224. | P/N |
| V7-A-042 | P/U | U/N | keep | Vật đen dài trên bàn không có đặc trưng nhận mobile chắc. | P/N, crop có xuất hiện phone, trong khi có mỗi một người trong crop thì phone chắc chắn của target anchor rồi |
| V7-B-001 | P/U | U/N | keep | Vật ở tay/vùng trang chưa rõ; đầu vẫn vào trang riêng. |
| V7-B-003 | P/U | U/N | recrop | Lưng xám trơn; đầu/tay của bạn trái vẫn cạnh tranh. |
| V7-B-005 | P/U | U/N | keep | Lưng trắng không có camera rõ; không suy từ bấm ngón cái. |
| V7-B-007 | P/U | U/N | keep | Chỉ cạnh/mặt nghiêng đỏ thiếu chi tiết mobile tại input. |
| V7-B-009 | P/U | P/N | keep | Màn hình UI và viền mobile rõ trong tay anchor. |
| V7-B-011 | P/U | P/P | keep | Mobile mặt trước rõ cầm dưới mặt bàn, đầu hướng xuống dưới bàn. |
| V7-B-013 | P/U | U/N | recrop | Lưng vàng thiếu camera; nữ cạnh phải và phone khác nổi bật. |
| V7-B-015 | P/U | U/N | recrop | Nữ cầm mặt lưng mờ và nam đứng sát có vai trò ngang nhau. | exclude, Crop vẫn dính người khác |
| V7-B-017 | P/U | U/N | recrop | Hai trẻ cùng lớn, còn thiết bị sát mép bàn; cần một anchor. | exclude, Crop vẫn dính người khác |
| V7-B-019 | P/U | U/N | recrop | Ba mặt/vùng tay liền nhau, lưng đỏ chưa đủ mobile ID. | exclude, Crop vẫn dính người khác |
| V7-B-021 | P/U | U/N | recrop | Hai nam cùng lớn và tay chồng; thiết bị trong tay chưa đủ ID. | exclude, Crop vẫn dính người khác |
| V7-B-023 | P/U | U/P | recrop | Nữ trái ngẩng ra trước; lưng máy của tay người bên phải rất nổi bật. |
| V7-B-025 | P/U | U/U | exclude | Màn hình gần vuông chưa đủ mobile; hood che hướng đầu/đích. |
| V7-B-027 | P/U | U/N | keep | Mặt lưng/cạnh xanh, không camera rõ. |
| V7-B-029 | P/U | U/P | recrop | Nam trái và nam phải đều có mặt/thân rõ. | Đổi target anchor sang nam ngồi đi vì người này có looking_around P nên sẽ hữu ích hơn nam tiền cảnh chỉ có U/N |
| V7-B-031 | P/U | U/N | recrop | Tay người trái chạm vật, attribution chưa sạch. |
| V7-B-035 | P/U | U/N | recrop | Nhiều đầu/tay chồng quanh nam cầm vật. | Frame gốc của crop này có thể tận dụng thêm bạn nam ngồi phía trước đang quay đầu, crop đó sẽ là N/P |
| V7-B-039 | P/U | U/N | keep | Lưng xanh chỉ có đốm nhỏ. |
| V7-B-040 | N/N | N/N | recrop | Nữ tiền cảnh và tay viết lớn cạnh nam anchor. |
| V7-B-041 | P/U | U/N | recrop | Hai nữ và người sau cùng rõ, vùng tay chồng. | exclude, Crop vẫn dính người khác |
| V7-B-043 | P/U | U/N | keep | Không đủ camera trên lưng tối. |
| V7-B-047 | P/U | U/N | keep | Mặt/cạnh đen không đủ nhận mobile. |
| V7-B-049 | P/U | U/N | recrop | Nhiều nữ cùng kích thước, nhiều tay/thiết bị. | exclude, Crop vẫn dính người khác |
| V7-B-051 | P/U | U/P | recrop | Nam ngẩng khỏi vật, người cạnh cũng trội. | Frame gốc của crop này có thể tách thành 2 crop, lần lượt cho 2 nam ngồi cạnh nhau, nam áo xanh da trời là U/P, còn nam áo xám là U/N |
| V7-B-053 | P/U | P/N | recrop | Máy xanh có cụm camera lớn nhưng còn nữ trước và thiết bị khác. | Xem lại giúp tôi bạn nữ tiền cảnh đã có crop chưa, nếu chưa thì đổi thành crop bạn nữ đó và gán là P/N |
| V7-B-055 | P/U | U/N | recrop | Kiểm lại PNG 224: vật cầm nghiêng chỉ còn cạnh và vùng tối, chưa tách chắc màn hình; hai nữ cùng rõ và cùng bàn. | Tách thành 2 crop, trong đó bạn cầm vật sẽ là U/N còn bạn ngồi cạnh sẽ là U/P, hai crop phải không được dính người khác vào |
| V7-B-059 | P/U | U/N | keep | Lưng vàng không đủ camera tại input. |
| V7-B-063 | P/U | U/P | keep | Mặt ngẩng khỏi máy, lưng đen chưa nhận dạng. | U/N, vẫn đang nhìn vào máy |
| V7-B-065 | P/U | U/N | keep | Chỉ mặt/cạnh vật tối cầm sát thân. |
| V7-B-089 | N/N | N/N | keep | Hai tay viết/giữ trang riêng rõ. |
| V7-D-002 | P/U | U/N | recrop | Hai nữ cùng lớn đang nhìn chung thiết bị. | Tách thành 2 crop, trong đó bạn cầm vật sẽ là U/N còn bạn ngồi cạnh sẽ là U/P, hai crop phải không được dính người khác vào |
| V7-D-004 | P/U | U/N | recrop | Nhiều nữ và thiết bị cạnh bên ở cùng mức nổi bật. | exclude, crop dính quá nhiều người |
| V7-D-005 | P/U | U/N | recrop | Nam và nữ sát nhau đều còn mặt, cùng vùng thiết bị. | Frame gốc của crop này có thể tách thành 4 crop, lần lượt là nam ngồi trên target anchor U/P, hai nữ ngồi cạnh target anchor lần lượt thành 2 crop U/P |
| V7-D-008 | P/U | U/N | recrop | Nữ cạnh phải còn mặt và tay tác động gần máy. | Tách thành 2 crop, trong đó bạn cầm vật sẽ là U/N còn bạn ngồi cạnh sẽ là U/P, hai crop phải không được dính người khác vào |
| V7-D-009 | P/P | U/N | keep | Kiểm lại PNG 224: mặt đen trong tay chưa có màn hình hoặc camera phân biệt được; hướng vùng tay riêng rõ. |
| V7-D-010 | P/U | U/N | recrop | Hai nữ và hai vùng thao tác ngang vai trò. |
| V7-D-011 | P/U | U/N | keep | Vật trắng cầm nhỏ, thiếu đặc trưng mobile. |
| V7-D-012 | P/U | U/N | recrop | Nhóm nhiều mặt cùng lớn, lưng máy không rõ camera. |
| V7-D-013 | P/U | U/N | recrop | Nam ngồi và nam đứng sát cùng rõ. | Tách thành 2 crop, trong đó bạn cầm vật sẽ là U/N còn bạn áo vàng đang ngồi sẽ là U/P, hai crop phải không được dính người khác vào |
| V7-D-014 | P/U | U/N | recrop | Nữ cạnh phải và tay chỉ vào máy ngang vai trò. | Tách thành 2 crop, trong đó bạn cầm vật sẽ là U/N còn bạn ngồi cạnh sẽ là U/P, hai crop phải không được dính người khác vào |
| V7-D-015 | P/U | U/N | recrop | Tay/thiết bị tiền cảnh nổi bật ở cạnh phải. |
| V7-D-017 | U/P | U/N | recrop | Hai nữ cùng thao tác quanh vật đỏ. |
| V7-D-018 | P/U | U/N | recrop | Hai nam và tay/thiết bị chồng vùng bài. |
| V7-D-020 | P/U | U/N | keep | Lưng bạc trơn, đầu vào vùng tay riêng. |
| V7-D-021 | P/P | U/P | keep | Mặt nhìn trước cao hơn vật trong tay, camera không đủ rõ. | U/N, đang nhìn vào vật đang cầm |
| V7-D-022 | U/P | U/P | recrop | Nam trái nhìn/tác động vật của nam bên phải bị cắt. |
| V7-D-023 | P/U | U/N | keep | Thiết bị ngang chỉ cạnh/lưng, không đủ mobile ID. |
| V7-D-026 | N/N | U/N | recrop | Nam đứng và nữ ngồi cùng lớn; cần anchor đơn. |
| V7-OE-S066-A01 | P/U | N/N | recrop | Calculator có phím nhưng crop còn nhiều mặt cùng rõ. | P/N, cầm phone rõ ràng |
| V7-OE-S066-A02 | P/N | P/N | recrop | Phone mặt trước trên bàn; cần bỏ mặt/tay nữ cạnh trái. |
| V7-OE-S068-A01 | U/P | U/N | recrop | Nam trước nhìn bài, nam sau nhìn trước; person box gộp cả hai. |
| V7-OE-S068-A02 | N/N | N/N | keep | Viết trên giấy riêng, hai tay còn đủ đọc. |
| V7-OE-S069-A01 | P/U | U/N | recrop | Mặt lưng đen, nữ cạnh trái còn mặt/thân lớn. |
| V7-OE-S070-A01 | P/U | U/N | recrop | Hai nữ cùng lớn và hai vùng tay. |
| V7-OE-S071-A01 | P/U | U/N | recrop | Nam và nữ cùng mặt rõ, chung vùng thao tác. |
| V7-OE-S072-A01 | P/P | U/P | recrop | Nam quay sang nữ sau, cả hai mặt đều nổi bật. |
| V7-OE-S073-A01 | P/N | U/P | keep | Vật ở dưới mặt bàn, đầu rời trang hướng xuống vùng tay dưới bàn. | U/N, đang nhìn vào vật cầm trên tay |
| V7-OE-S074-A01 | P/U | U/P | keep | Đầu nhìn vật dưới mép bàn thay vì trang riêng; không nhận mobile từ lưng vàng. | U/N, đang nhìn vào vật cầm trên tay |
| V7-OE-S076-A01 | U/N | U/U | exclude | Tay che mắt/mặt và vùng tay còn lại thiếu evidence. | Sửa lại crop để quan sát toàn diện hơn, include, N/N |
| V7-OE-S077-A01 | U/P | N/P | recrop | Nam trước quay phải, nam sau cùng rõ và person box gộp. | U/P, nam trước bị che mất tay |
| V7-OE-S102-A01 | N/N | N/P | keep | Mắt/đầu ngẩng khỏi trang dù tay vẫn giữ bút. |
| V7-OE-S102-A02 | P/P | U/P | keep | Vật đen nhỏ trên bàn chưa rõ phone, mặt quay sang phải. | P/P, vật trên bàn khá rõ là phone |
| V7-OE-S103-A01 | N/N | P/N | keep | Mặt màn hình hồng sáng có vùng UI/viền máy, đầu vào trang. |
| V7-OE-S104-A01 | P/U | U/N | keep | Chỉ mặt/cạnh vàng nằm ngang, không suy phone từ dáng cầm. |
| V7-OE-S105-A01 | P/U | U/N | keep | Vật tối áp tai thiếu đặc trưng mobile, đầu vẫn hướng vùng bài. |
| V7-OE-S106-A01 | N/N | N/N | keep | Tablet lớn rõ và hai tay đủ quan sát. |
| V7-OE-S107-A01 | P/U | U/N | keep | Vật trong tay/mặt bàn chưa phân biệt, đầu hướng vùng riêng. | P/N, crop lại cho có thể nhìn hết vật cầm trên tay và màn hình phone có thể nhận diện rõ, nhưng không được dính người khác |
| V7-OE-S108-A01 | P/P | U/P | keep | Chỉ cạnh vật áp má; đầu nhìn trước khỏi giấy. |
| V7-OE-S109-A01 | P/P | U/P | keep | Vật đen trên bàn chưa rõ, mặt ngẩng khỏi trang. |
| V7-OE-S109-A02 | P/N | U/N | keep | Một tay dưới mặt bàn, đầu hướng giấy. |
| V7-OE-S110-A01 | N/N | N/N | keep | Hai tay chắp trên giấy đủ thấy, đầu hướng vùng giấy. |
| V7-R8-B-001 | P/U | P/P | keep | Màn hình/UI sáng trong tay, mặt nhìn ra trước khỏi máy. | P/N |
| V7-R8-D-001 | P/U | N/N | recrop | Nam đứng và nữ ngồi cùng rõ; tablet không phải mobile. |
| V7-UNAPPROVED-C-001 | U/P | U/P | keep | Tay phải ngoài mép source, đầu quay phải khỏi trang. |
| V7-UNAPPROVED-C-002 | N/P | N/P | keep | Tay/bàn rõ, quay trái khỏi own-paper. |
| V7-UNAPPROVED-C-003 | P/U | P/N | keep | Cụm camera nhiều thành phần trên lưng xanh còn rõ. |
| V7-UNAPPROVED-C-004 | P/N | P/N | keep | Cụm camera lớn trên lưng đỏ còn tách được. |
| EXP-CM-001 | P/U | U/N | keep | Khối máy tối trong hai tay không đủ camera/màn hình. |
| EXP-CM-002 | P/U | U/P | keep | Không dùng dáng áp vật vào tai làm mobile ID. |
| EXP-CM-003 | P/P | U/P | keep | Vật áp tai không còn đặc trưng phone tại input. |
| EXP-CM-004 | P/P | U/P | keep | Vật tối cạnh má, không đủ mobile ID. |
| EXP-CM-005 | N/N | N/N | keep | Hai tay đan trên bàn và nhìn vùng thao tác riêng. |
| EXP-CM-006 | N/U | N/N | keep | Tay giữ bút và tay còn lại trên bàn đọc được. |
| EXP-CM-007 | P/U | U/P | keep | Vật đen đưa về trước chưa đủ đặc trưng; đầu ngẩng. |
| EXP-CM-008 | P/U | U/N | keep | Một phần tay/vật ở mép bàn chưa rõ, đầu hướng vùng riêng. |
| EXP-CM-009 | N/N | N/N | keep | Hai tay và trang viết đủ quan sát. |
| EXP-CM-010 | N/U | U/P | keep | Giơ tay nhìn trước, tay còn lại ở đùi chưa đủ absence. |
| EXP-CM-011 | N/N | N/N | keep | Mặt cúi theo trang và hai tay viết/giữ rõ. |
| EXP-CM-012 | U/P | U/P | keep | Nam sau quay trái, một vùng tay dưới bàn khuất. |
| EXP-CM-013 | N/P | N/P | keep | Hai tay đặt/đan rõ, đầu quay trái khỏi bàn. |
| EXP-CM-014 | U/P | U/P | keep | Quay trái, vùng tay thấp bị bàn/vật tiền cảnh che. |
| EXP-CM-015 | N/U | N/N | keep | Tay trước thân còn đọc được, đầu hướng vùng bàn riêng. |
| EXP-CM-016 | U/N | U/P | keep | Một tay/vùng thao tác bị thân/bàn che, mặt ngẩng trước. |
| EXP-CM-017 | P/U | U/P | keep | Vật áp tai chỉ khối tối, không suy từ tư thế gọi. |
| EXP-CM-018 | N/N | N/N | keep | Hai tay giữ trang giấy rõ, nhìn trang. |
| EXP-CM-019 | N/P | N/P | keep | Đang giữ sách nhưng đầu quay phải khỏi trang. |
| EXP-CM-020 | N/N | N/N | keep | Đầu hướng sách đang giở, tay đủ rõ. |
| EXP-CM-021 | N/U | U/U | exclude | Đầu úp, tay bị đầu che. |
| EXP-CM-022 | P/U | U/N | keep | Chỉ lưng máy đen, đầu hướng vật. |
| EXP-CM-023 | P/U | U/N | keep | Lưng/cạnh mờ, không mobile ID. |
| EXP-CM-024 | U/P | N/P | keep | Hai tay đan rõ, đầu quay trái khỏi vùng tay. |
| V7-A-007 | P/U | U/P | keep | Vật đen/viền bạc trên bàn chưa rõ mobile, đầu nhìn người bên phải. | exclude |
| V7-A-008 | N/N | N/N | keep | Tay đặt rõ, hướng đầu vào màn laptop phía dưới. |
| V7-A-009 | P/U | U/P | keep | Vật nhỏ trên bàn chưa phân biệt, mặt hướng camera. | exclude |
| V7-A-011 | P/U | U/N | keep | Vật nhỏ gần chai nước chưa rõ; đầu hướng laptop. | exclude |
| V7-A-013 | P/P | U/P | keep | Vật đóng trên bàn không thấy màn hình/camera; mặt hướng trước. | P/P |
| V7-A-014 | N/N | N/N | keep | Laptop, bàn phím và tay đủ đọc; không thiết bị mơ hồ. | exclude |
| V7-A-015 | P/U | U/P | keep | Vật nhỏ đen trên bàn thiếu ID, mặt nhìn trước. | exclude |
| V7-A-017 | P/P | N/P | keep | Hai tay vùng bàn rõ, nhìn ra trước khỏi laptop. | U/P, bị che |
| V7-A-022 | N/P | N/P | keep | Tay/đĩa ăn rõ, nhìn sang trái khỏi vùng riêng. | exclude |
| V7-A-023 | P/U | P/N | keep | Màn hình/viền mobile trên bàn rõ, đầu hướng laptop. |
| V7-A-025 | P/U | N/N | keep | Thiết bị bàn có dây và tay/keyboard đọc được, không mobile. | exclude |
| V7-A-026 | N/P | N/P | keep | Cầm bút nhưng đầu/nhìn trước khỏi giấy. |
| V7-A-027 | P/U | N/N | keep | Tay và vật làm thủ công đủ phân biệt, đầu hướng vùng tay. | exclude |
| V7-A-029 | P/U | N/N | recrop | Nữ trước là đích, person box còn bao nữ phía sau. | U/N, tay bị che |
| V7-A-031 | P/P | U/P | keep | Vật nhỏ trên bàn chưa rõ, nhìn camera. |
| V7-A-040 | P/U | N/N | keep | Tay, giấy và laptop rõ, nhìn màn riêng. |
| V7-A-043 | N/N | N/N | keep | Tay gập/khoanh và tay keyboard đủ đọc, nhìn laptop. | exclude |
| V7-A-046 | N/N | N/N | keep | Chống miệng không tự U khi tay/bàn còn đủ rõ. |
| V7-A-047 | N/N | N/N | keep | Tay trên keyboard và tay giơ ngón cái rõ. |
| V7-A-049 | N/N | N/N | keep | Tay typing và hướng màn laptop riêng rõ. |
| V7-B-067 | P/U | U/N | keep | Vật đen tại hông chưa rõ, đầu hướng màn riêng bên phải. | exclude |
| V7-B-069 | P/U | U/N | recrop | Hai nam cùng lớn, thiết bị cầm chỉ mặt lưng. |
| V7-B-087 | U/P | N/P | keep | Laptop và tay thấy đủ, mặt nhìn camera. | U/P, bị che |
| V7-C-095 | U/N | N/N | keep | Sách và hai tay rõ, đầu hướng trang. |
| V7-C-097 | U/N | N/N | recrop | Hai nam cùng lớn bên laptop, cần anchor đơn. |
| V7-C-099 | U/N | N/N | keep | Typing laptop, tay và vùng thao tác đủ đọc. | exclude |
| V7-C-100 | U/N | N/N | keep | Tay chống đầu và vùng laptop/bàn đủ đọc. | exclude |
| V7-C-114 | U/P | N/P | keep | Tay trên laptop nhưng nhìn trước khỏi màn laptop. | exclude |
| V7-C-115 | U/P | N/P | keep | Nhìn sang người đối diện, không nhìn laptop riêng. | exclude |
| V7-C-116 | U/P | N/P | recrop | Nam trái quay sang phải; nam cạnh còn mặt/thân cùng rõ. |
| V7-C-118 | U/N | N/N | recrop | Nam phải dùng laptop, nam trái còn mặt/thân lớn. | exclude |
| V7-D-028 | P/U | U/N | recrop | Vật có phím nhưng loại thiết bị chưa chắc; nữ sau còn mặt lớn. | exclude |
| V7-D-029 | P/U | U/P | keep | Thiết bị bạc nhỏ chưa rõ mobile, mặt hướng trước. |
| V7-D-031 | P/U | U/N | keep | Vật đen cầm không đủ nhận dạng. |
| V7-D-034 | P/U | U/P | keep | Thiết bị bạc có ô/chấm nhưng chưa chắc camera hay mobile; mặt trước. |
| V7-D-035 | P/U | U/P | keep | Lưng nâu có logo không thay camera/màn hình, nhìn trước khỏi máy. | exclude |
| V7-D-038 | P/U | P/N | recrop | Screen/UI rõ nhưng ba người ngang vai trò. |
| V7-OE-S039-A01 | U/P | U/P | keep | Vật áp tai chỉ mảnh tối, nhìn ra trước khỏi laptop. |
| V7-OE-S040-A01 | P/U | P/N | keep | UI/màn kính và viền mobile rõ, đầu hướng thiết bị trên trang. |
| V7-OE-S041-A01 | U/N | N/N | recrop | Person box bao nhóm hàng bàn; cần box nam tiền cảnh. | exclude |
| V7-OE-S042-A01 | P/U | U/N | recrop | Nam trái còn mặt/thân cùng rõ với nam cầm vật. |
| V7-OE-S042-A02 | N/N | U/N | keep | Vật nhỏ tối gần tay chưa chắc phone, đầu hướng vùng thao tác. |
| V7-OE-S043-A01 | P/U | U/P | keep | Vật sát tai không đủ ID, mắt nhìn trước khỏi trang. |
| V7-OE-S043-A02 | P/P | U/U | exclude | Mắt nhắm, tay dưới bàn; calculator không cứu absence. | include, P/P |
| V7-OE-S043-A03 | P/N | N/N | keep | Hai tay trên trang rõ, đầu hướng trang. | P/N |
| V7-OE-S043-A04 | U/P | N/P | keep | Tay chắp rõ, mặt quay lên phải khỏi giấy. | U/P, vật gần khuỷu tay trên bàn |
| V7-OE-S044-A01 | P/U | U/N | keep | Mặt/cạnh máy trong tay không đủ mobile ID. |
| V7-OE-S044-A02 | P/P | U/P | keep | Vùng tay dưới bàn thiếu, mặt ngẩng khỏi bài. | P/P |
| V7-OE-S044-A03 | P/P | N/P | keep | Hai tay đan rõ, đầu ngẩng khỏi trang. | P/P |
| V7-OE-S044-A04 | U/P | N/P | keep | Hai tay trên bàn đủ đọc, đầu hướng ra bên. | U/P |
| V7-OE-S047-A01 | N/N | N/N | keep | Tay keyboard và hướng màn riêng đủ rõ. | U/N |
| V7-OE-S049-A01 | P/U | P/P | keep | Màn hình/UI phone rõ dưới bàn, đầu rời laptop hướng tay dưới bàn. | P/N |
| V7-OE-S050-A01 | N/N | N/N | keep | Tay viết và tay chống đầu thấy đủ, hướng trang. |
| V7-OE-S050-A02 | N/N | N/N | keep | Hai tay và giấy riêng rõ. |
| V7-OE-S051-A01 | P/U | U/N | recrop | Hai nam cùng lớn, thiết bị/tay chồng. | P/P |
| V7-OE-S052-A01 | P/U | U/P | keep | Vật đen trên bàn không đủ ID, mặt ngẩng ra trước. | P/P |
| V7-OE-S053-A01 | N/N | N/N | recrop | Nam áo xanh trái, nam giữa và nam phải cùng trội. | nam áo xanh đeo kính N/P |
| V7-OE-S054-A01 | N/N | N/N | recrop | Nhóm ba người chung tablet, cần chọn một người. | N/P |
| V7-OE-S055-A01 | U/P | U/P | keep | Nam đứng nhìn ra trước, vùng bàn tay chưa đầy đủ. |
| V7-OE-S056-A01 | P/N | P/N | recrop | Mặt trước phone trên giấy cạnh laptop; nhiều người cùng rõ. |
| V7-OE-S056-A02 | P/N | P/N | keep | Phone mặt kính/viền trên giấy gần tay, nữ phải trội. |
| V7-OE-S057-A01 | U/N | N/N | recrop | Nam ngồi, nữ sau và nam đứng cùng rõ. | exclude |
| V7-OE-S057-A02 | P/U | N/N | recrop | Cả hàng người và bàn tay/laptop còn chung crop. | exclude |
| V7-OE-S058-A01 | U/N | U/U | exclude | Các đầu gục/tay che; không chọn người mới để cứu group crop. |
| V7-OE-S061-A01 | U/P | U/P | recrop | Nhiều người cùng nhìn người hướng dẫn, tay bị chồng. | Nữ áo xanh là tiền cảnh U/P |
| V7-OE-S063-A01 | U/N | U/N | recrop | Hướng mặt vào dãy máy riêng, nhưng bốn người ngang vai trò. | exclude |
| V7-OE-S064-A01 | U/N | U/N | recrop | Dãy nữ nhìn máy riêng, nhiều anchor và tay khuất. | exclude |
| V7-PF-A-001 | P/U | U/N | keep | Vật đen trên bàn chưa đủ ID, đầu vào màn máy trước mặt. | P/N |
| V7-PF-A-002 | P/U | P/N | keep | Mặt kính/viền phone xanh trên bàn đủ nhận, đầu vào trang. |
| V7-PF-A-004 | P/P | U/P | recrop | Phone/vùng bàn dùng chung, person box chứa nhiều nam. | P/P |
| V7-PF-A-005 | P/N | U/N | keep | Vật nhỏ đen ở bàn chưa rõ phone, đầu vào giấy. | P/N |
| V7-PF-A-006 | N/N | N/N | recrop | Nam trẻ và nữ lớn cùng rõ bên tablet. |
| V7-PF-A-007 | N/U | N/N | recrop | Hai nữ viết cùng lớn và cùng vùng tay. | exclude |
| V7-PF-B-001 | P/U | U/P | keep | Vật trên đùi chưa phân biệt, đầu nhìn xuống dưới mặt bàn. | P/N |
| V7-PF-C-001 | U/N | N/N | recrop | Tay/thân người tiền cảnh cắt ngang anchor phía sau. | exclude |
| V7-PF-C-002 | U/N | U/N | keep | Đầu vào trang rõ, tay còn lại thiếu evidence. |
| V7-PF-C-003 | U/P | U/P | recrop | Giơ tay nhìn người hướng dẫn, nữ cạnh phải còn rõ. | N/P |
| V7-PF-C-004 | U/N | N/N | recrop | Hai nữ viết cùng lớn. | exclude |
| V7-PF-D-001 | P/U | U/N | recrop | Thiết bị ngang thiếu ID và ba mặt/vùng tay chồng. | exclude |
| V7-PF-D-002 | P/U | P/N | recrop | Game/UI trên mặt máy rõ, nhưng nhóm ba nam ngang vai trò. |
| V7-UNAPPROVED-C-005 | P/P | U/P | keep | Vật trên bàn chỉ mặt phẳng mờ, đầu quay trái. | P/P |
| V7-UNAPPROVED-C-006 | P/N | U/N | keep | Vật nhỏ trên bàn thiếu ID, đầu hướng vùng viết. | P/N |
| V7-UNAPPROVED-C-007 | P/U | U/N | keep | Lưng xám/cụm chấm chưa đủ camera tại input. | P/N, có thể thấy rõ lỗ camera |
| E004-CF-C007 | P/N | P/N | keep | Màn hình/UI và viền máy rõ trong tay trên sách. |
| E004-CF-C008 | N/N | N/N | keep | Nữ trước trội, hai tay và trang viết rõ. |
| E004-CF-C009 | N/P | N/P | keep | Tay còn ở giấy nhưng mặt ngẩng khỏi trang. |
| E004-CF-C010 | N/N | N/N | keep | Hai tay viết/giữ trang đủ rõ. |
| E004-CF-C011 | N/P | N/U | keep | Tóc che mặt và đích nhìn không đủ chắc; tay/bài đủ absence. | N/P |
| E004-CF-C016 | P/P | P/P | keep | Màn hình/UI phone rõ, mặt nhìn trước khỏi trang. |
| E004-CF-C018 | P/N | P/N | keep | Phone mặt trước trên sách riêng, đầu vào trang. |
| E004-CF-C021 | P/P | P/P | recrop | Phone anchor rõ nhưng người/tay/phone tiền cảnh cạnh tranh mạnh. |
| E004-CF-C028 | N/P | N/P | keep | Phím calculator rõ, hai tay thấy đủ; quay phải khỏi giấy. |
| E004-CF-C029 | N/N | N/N | keep | Calculator đủ phím, đầu/tay vào trang riêng. |
| E004-CF-C030 | U/P | N/P | keep | Tay gập trên bàn rõ, nhìn trước khỏi trang. | U/P |
| E004-CF-C031 | U/N | N/N | keep | Đầu vào giấy, tay và vật liệu giấy đọc được. | U/P |
| E004-EX-C117 | P/N | P/N | keep | UI trên mobile rõ, đầu hướng máy trên sách. |
| E004-EX-C118 | P/U | P/N | keep | Mặt trước sáng/viền phone, hướng đầu vào máy riêng. |
| E004-EX-C119 | P/U | P/N | keep | UI/màn hình mobile rõ trong tay, đầu hướng tay. |
| E004-EX-C120 | P/U | U/U | exclude | Source chỉ bàn tay và thiết bị có phím chưa phân biệt. |
| E004-EX-C121 | P/U | P/N | keep | Mặt màn hình xanh/UI rõ, đầu hướng máy trên bàn. |
| E004-EX-C122 | U/P | U/P | keep | Tay ở hông dưới bàn thiếu absence, mặt ngẩng khỏi bài. | N/P |
| E004-EX-C123 | P/N | P/N | keep | Phone mặt trước trên trang, đầu hướng trang. |
| E004-EX-C124 | N/P | N/P | recrop | Nữ nhìn sang nam phải; mặt nam ở mép còn gây nhiễu. |
| E004-EX-C125 | N/P | N/P | keep | Tay giữ giấy rõ, mặt ngẩng ra trước. |
| E004-EX-C129 | N/P | N/U | keep | Giấy và tay rõ; mắt nhắm/đích không chắc. | exclude |
| E004-EX-C130 | P/N | U/N | keep | Lưng đen không có camera phân biệt. |
| E004-EX-C136 | P/N | U/N | recrop | Nam trước và nữ sau cùng mặt/vùng thiết bị rõ. | exclude |
| E004-EX-C139 | P/N | P/N | keep | Mặt kính sáng và viền phone trong tay trên trang. |
| E004-EX-C142 | P/N | U/N | keep | Lưng xanh thiếu camera rõ, mắt hướng vật cầm bên trái. | P/N, có thể thấy lỗ camera và icon apple |
| E004-EX-C143 | P/N | U/N | keep | Chấm trên lưng xanh không đủ mobile ID. |
| E004-EX-C144 | P/N | P/N | keep | Mặt trước phone trên trang rõ, đầu hướng bài. |
| E004-EX-C151 | P/N | U/N | keep | Lưng tối không rõ camera, đầu hướng vùng tay riêng. |
| E004-EX-C152 | P/N | U/N | keep | Lưng trắng trong tay không đủ đặc trưng mobile. | P/N, có thể thấy màn hình sáng |
| E004-EX-C162 | U/N | U/N | keep | Tay dưới bàn khuất, đầu hướng trang đang viết. |
| E004-EX-C163 | N/N | U/N | keep | Vật đen phẳng chưa đủ phone ID, nữ trước vẫn trội. |
| E004-EX-C164 | N/N | N/N | recrop | Đầu tiền cảnh ở đáy có thể bỏ bớt, giữ tay và trang anchor. |
| E004-EX-C165 | N/P | U/P | recrop | Nữ sau ngẩng khỏi bài, thân/tay nữ trước chiếm khung. | N/P |
| E004-EX-C166-R2 | N/N | N/N | recrop | Cần giảm mặt nữ sau và vùng bàn tiền cảnh. |
| E004-EX-C169 | N/N | N/N | recrop | Nam ngồi trội nhưng nam đứng/vật trên tay còn nổi bật. |
| E004-EX-C170-R2 | N/P | N/P | keep | Nữ quay phải khỏi trang, tay/bàn đủ đọc. |
| E004-EX-C171 | N/N | N/N | recrop | Person box chưa bao đúng đầu/người, context có tay tiền cảnh dư. |
| E004-EX-C172 | U/N | N/N | keep | Giấy, tay và phím calculator đủ quan sát. | Xem xét, vật giấu trong tay áo sáng là màn hình phone |
| V6-EX-001 | P/U | P/N | keep | UI và viền phone rõ dưới tay trên bàn. |
| V6-EX-002 | P/P | U/P | recrop | Hai nam chồng cơ thể/tay, cần anchor đơn. |
| V6-EX-003 | P/U | U/N | keep | Lưng hồng thiếu camera rõ, đầu vào vật. |
| V6-EX-004 | P/U | U/N | keep | Lưng trắng/chấm nhỏ không đủ ID tại 224. |
| V6-EX-007 | P/U | U/N | keep | Vật đen cầm chưa nhận dạng, nữ trước vẫn trội. |
| V6-EX-009 | P/U | U/N | keep | Lưng bạc thiếu đặc trưng camera. |
| V6-EX-010 | P/U | U/N | keep | Mặt lưng/cạnh đen không đủ mobile ID. |
| V6-EX-012 | P/U | P/P | keep | Mobile mặt kính/viền rõ, đầu nhìn camera khỏi giấy. | Thêm 1 crop nữa cho bạn nữ bên cạnh P/P |
| V6-EX-015 | P/U | U/P | recrop | Đầu/tay nam tiền cảnh che vùng bài của nam sau. |
| V6-EX-017 | N/P | N/P | keep | Tay và giấy rõ, đầu nhìn trái khỏi trang. |
| V6-EX-019 | U/P | U/P | keep | Vùng bàn tay dưới khung thiếu, đầu quay phải. |
| V6-EX-020 | P/P | U/P | keep | Vật đen trên bàn chưa đủ phân biệt, đầu quay sang bên. |
| V6-EX-021 | U/P | U/P | keep | Tay sát đùi/ngoài khung thiếu absence, mặt quay trái. |
| V6-EX-022 | N/P | N/P | keep | Tay trên giấy rõ, đầu quay trái khỏi trang. |
| V6-EX-023 | U/P | U/P | keep | Một tay/vùng bàn khuất, đầu nhìn sang phải. |
| V6-EX-024 | N/P | N/P | keep | Tay cầm bút và tay còn lại trên trang, mặt quay phải. |
| V6-EX-025 | U/P | U/P | keep | Tay bị người/đồ che, đầu quay phải khỏi bài. |
| V6-EX-026 | U/P | U/P | recrop | Crop gần đầu thiếu vùng tay/bài; thử context cùng panel nguồn. |
| V6-EX-027 | N/P | U/P | keep | Tay một phần ngoài vùng quan sát, đầu quay trái. |
| V6-EX-029 | U/P | U/P | recrop | Nam nhìn thiết bị của nữ cạnh, vật/tay người cạnh gây nhầm. |
| V6-EX-030 | N/P | U/P | exclude | Dải cảnh khác ở đáy crop, không inpaint để cứu. |
| V6-EX-031 | N/P | N/P | recrop | Nam nhìn vùng bài nữ trái, hai mặt cùng lớn. |
| V6-EX-032 | N/N | N/N | recrop | Nam đỏ sau có mặt lớn cạnh nam viết trước. |
| V6-EX-034 | N/N | N/P | recrop | Nam trước ngẩng khỏi giấy, nam đỏ sau cùng rõ. |
| V6-EX-035 | N/U | N/P | recrop | Nam trước nhìn trước, nam đỏ sau cùng mặt rõ. |
| V6-EX-036 | N/N | N/N | keep | Tay gập và trang đủ rõ, nhìn vùng tay riêng. |
| V6-EX-037 | N/N | N/N | keep | Hai tay và trang viết rõ. |
| V6-EX-038 | U/N | U/N | keep | Vùng tay mờ/cắt, đầu vẫn vào bài riêng. |
| V6-EX-039 | N/U | N/P | keep | Hai tay trên giấy, đầu ngẩng khỏi bài. |
| V6-EX-040 | N/N | N/N | recrop | Nam đỏ sau còn mặt lớn cạnh nam đang viết. |
| V6-EX-041 | N/N | N/N | recrop | Hai mặt cùng rõ, cần khung nam viết trước. |
| V6-EX-042 | N/N | U/N | keep | Đầu hướng giấy, tay còn lại dưới bàn thiếu absence. | Crop thêm bạn nữ ngồi trên U/P |
| V6-EX-043 | N/N | U/N | keep | Đầu hướng trang cầm bên phải, tay còn lại thiếu evidence. |
| V6-EX-044 | N/N | N/N | keep | Tay viết/giữ trang đủ rõ. |
| V6R2-EX-001 | P/P | U/P | recrop | Nam quay sang nữ sau; mặt lưng máy chưa đủ ID và hai mặt cùng rõ. |
| V6R2-EX-002 | P/U | P/N | keep | Màn hình/UI mobile trên trang rõ, đầu hướng trang. |
| V6R2-EX-004 | P/U | U/N | keep | Lưng hồng không đủ camera rõ. |
| V6R2-EX-007 | N/P | N/P | keep | Hai tay ở giấy, đầu quay ra sau khỏi bài. |
| V6R2-EX-008 | N/P | U/N | keep | Đầu vào trang đang cầm, phần tay còn lại thiếu evidence. | N/P, crop lại cho thấy toàn cảnh target anchor hơn |
| V6R2-EX-009 | P/P | P/P | keep | Phone màn hình xanh rõ trong tay, đầu quay khỏi bài. |
| V6R2-EX-010 | N/P | U/P | keep | Đầu quay trái, một tay dưới bàn thiếu absence. | N/P, chỉ mất có tí tôi, nếu frame gốc có thì nên crop lại |
| V6R2-EX-012 | U/P | U/P | keep | Chống má thấy một tay, tay kia ngoài crop; mặt hướng trước. |
| V6R2-EX-015 | N/N | N/N | keep | Tay viết/giữ giấy rõ. |
| V6R2-EX-017 | N/N | U/N | keep | Đầu vào trang, tay bên kia thiếu evidence. |
| V7-C-079 | U/P | N/N | keep | Hai tay trên giấy rõ. | N/P |
| V7-C-087 | U/N | N/N | keep | Cầm bút, giữ trang, đầu vào bài. | Crop thêm bạn nữ áo xanh N/P |
| V7-OE-S081-A01 | U/N | U/P | recrop | Nam sau nhìn nữ trước, thân/đầu nữ cắt vùng anchor. | Frame gốc của crop này có thể tận dụng thêm, có vài bạn đang looking_around P nên hãy phân tích kỹ đề thêm được crop hữu ích |
| V7-OE-S082-A01 | N/N | N/N | keep | Tay viết/giữ trang còn rõ dù input nhỏ. |
| V7-R8-C-001 | N/P | N/P | recrop | Nữ trước quay trái, nam sau vẫn có mặt lớn. |
| V7-R8-C-002 | N/N | N/N | keep | Hai tay và vùng giấy đọc được. |
| V7-A-036 | P/P | U/P | keep | Mặt nhìn trước, hai tay ở dưới bàn thiếu absence. |
| V7-A-037 | P/U | N/P | recrop | Hai nữ cùng lớn, nữ sọc nhìn khỏi keyboard. | exclude |
| V7-A-038 | P/U | U/N | keep | Kiểm lại PNG 224: vật trắng có vùng tối nhỏ nhưng chưa tách chắc màn hình/phím để nhận mobile; nhìn laptop riêng. | exclude | exclude |
| V7-A-051 | N/U | N/N | keep | Máy ảnh có ống kính rõ và hai tay cầm, không gọi DSLR là phone. | exlcude |
| V7-A-052 | N/U | N/P | keep | Hai tay rõ, nhìn ra trước khỏi vùng keyboard. | exclude |
| V7-A-053 | N/N | N/N | keep | Một tay gập, tay kia keyboard, hướng laptop riêng. | exclude |
| V7-A-054 | N/N | N/N | keep | Tay/bàn rõ, mắt hướng màn máy riêng bên phải. | exclude |
| V7-A-056 | P/U | U/N | keep | Vật trắng nhỏ trên bàn chưa đủ ID, đầu hướng laptop. | exclude |
| V7-A-057 | P/U | U/N | keep | Vật nhỏ mặt đen trên trang thiếu cấu trúc phân biệt phone. | P/N |
| V7-A-058 | P/P | U/P | keep | Vật đen đóng trên bàn thiếu ID; mặt nhìn camera. | exclude |
| V7-A-061 | N/N | U/N | keep | Vật xám trên bàn chưa phân biệt, đầu đọc giấy. |
| V7-A-062 | P/P | U/P | keep | Vật nhỏ đen trên bàn chưa chắc mobile, nhìn camera. | P/P |
| V7-A-064 | N/N | U/N | keep | Một tay ngoài khung, đầu hướng keyboard. | exclude |
| V7-A-065 | N/N | U/P | recrop | Nữ xanh và các mặt quanh cùng rõ, tay thiếu; nhìn khỏi laptop. | exclude |
| V7-A-066 | N/N | U/N | keep | Một tay ở mép ngoài crop, đầu hướng màn riêng. | exclude |
| V7-A-067 | N/N | N/N | keep | Hai tay keyboard và hướng laptop rõ. | exclude |
| V7-A-068 | P/U | N/P | keep | Tay/vật không thiết bị đủ đọc, mặt ngẩng khỏi bàn. | exclude |
| V7-A-069 | P/U | P/N | keep | Mobile screen/UI xanh trong case đỏ trên bàn, hướng vùng riêng. |
| V7-A-070 | P/P | U/P | keep | Một tay khuất dưới bàn, nhìn camera. |
| V7-A-071 | P/U | U/P | keep | Vật đen phẳng trên bàn chưa đủ mobile ID, đầu hướng trước. | P/P |
| V7-A-072 | P/U | U/N | recrop | Tay/thiết bị người cạnh ở tiền cảnh, vùng bàn dùng chung. | P/N |
| V7-A-073 | P/U | N/N | recrop | Nhiều nam cùng lớn trong crop keyboard. | exclude |
| V7-A-074 | P/P | U/P | keep | Vật trắng nhỏ trên bàn thiếu ID, nhìn người bên trái. | P/P |
| V7-A-075 | N/N | N/N | recrop | Hai nam cùng rõ và hai laptop. | exclude |
| V7-A-076 | N/N | N/N | keep | Hai tay keyboard, nhìn màn riêng. | exclude |
| V7-B-071 | P/U | P/N | keep | Màn hình/UI mobile tím rõ trong tay riêng. |
| V7-B-073 | P/U | P/N | keep | Mặt screen xanh và viền máy trong tay còn rõ. |
| V7-B-074 | P/U | U/N | keep | Mặt/cạnh đen cầm chưa đủ mobile ID. | P/N |
| V7-B-076 | P/U | U/N | keep | Mặt sau trắng có mảng tối nhưng chưa đủ camera tại input. |
| V7-B-077 | P/U | U/N | recrop | Vật chính chưa rõ, máy/tay người cạnh ở mép phải nổi bật. |
| V7-B-078 | P/U | U/N | recrop | Ba nam cùng lớn, thiết bị cầm chưa rõ loại. | P/N |
| V7-B-086 | N/U | N/N | keep | Tai nghe/thiết bị bàn có dây rõ, hai tay máy tính đọc được. | exclude |
| V7-B-092 | N/N | N/N | keep | Sách và hai tay rõ, đầu vào trang. |
| V7-B-093 | N/P | N/P | keep | Điện thoại bàn có dây, tay/bàn rõ; nhìn ra trước khỏi giấy. |
| V7-B-094 | N/N | N/N | keep | Tay và vật liệu mô hình đủ phân biệt, đầu hướng thao tác. | U/N |
| V7-B-096 | U/N | N/N | keep | Chống má và tay keyboard đủ đọc, đầu hướng màn riêng. | exclude |
| V7-B-097 | N/N | N/N | keep | Hai tay keyboard rõ, đầu vào màn riêng. | exclude |
| V7-B-098 | N/N | N/N | keep | Tay typing và vùng laptop đủ quan sát. | exclude |
| V7-B-099 | N/N | N/N | keep | Thiết bị điện tử có dây và tay keyboard đủ rõ. | exclude |
| V7-B-100 | U/N | U/N | keep | Quầy/thiết bị che vùng bàn tay, đầu hướng vùng thao tác. |
| V7-B-101 | N/U | N/P | keep | Tay chống miệng và tay bàn đủ rõ, nhìn camera. | exclude |
| V7-B-102 | N/P | N/P | keep | Hai tay trên giấy rõ, mặt hướng trước khỏi giấy. |
| V7-B-103 | N/P | N/P | keep | Hai tay chắp rõ, mặt ngẩng khỏi vùng sách. |
| V7-B-104 | N/U | N/P | recrop | Tay người tiền cảnh lớn ngay trước bàn tay anchor. | exclude |
| V7-B-106 | N/N | N/N | keep | Tay và giấy rõ, đầu hướng trang. |
| V7-B-107 | N/N | N/N | recrop | Hai người cùng lớn cạnh laptop. |
| V7-B-108 | N/U | N/P | keep | Hai tay chắp rõ, đầu nhìn trước/chéo trái khỏi vùng tay. |
| V7-B-109 | N/N | N/N | recrop | Person box gộp nam đứng và nữ ngồi bên máy. | exclude |
| V7-B-110 | N/N | N/N | keep | Hai tay keyboard/mouse và hướng màn riêng rõ. | exclude |
| V7-B-111 | N/P | N/P | keep | Cầm bút nhưng mặt nhìn camera khỏi sách. |
| V7-C-102 | U/N | N/N | keep | Tay vùng laptop rõ, đầu vào màn riêng. | exclude |
| V7-C-104 | U/N | N/N | recrop | Nam trẻ cầm vở nhưng người lớn/tay phía sau còn lớn. | N/P |
| V7-C-105 | U/N | U/N | keep | Vật nhỏ ở tay chưa đủ nhận dạng, đầu hướng vùng laptop. | exclude |
| V7-C-106 | U/N | U/U | exclude | Mắt nhắm, một tay dưới bàn; không có known target chắc. |
| V7-C-107 | U/P | N/P | keep | Tay typing đủ rõ, nhìn camera. |
| V7-C-108 | U/P | N/P | keep | Tay giấy/bút rõ, nhìn sang người bên trái. |
| V7-C-109 | U/P | N/P | keep | Tay bàn và tay đùi đọc được, quay trái khỏi vùng thao tác. |
| V7-C-110 | U/P | U/P | keep | Hai tay thấp/khuất, mặt quay phải khỏi trang. |
| V7-C-111 | U/P | N/P | keep | Tay khoanh đủ đọc, đầu nhìn trái khỏi bàn. |
| V7-C-119 | U/P | N/P | keep | Hai tay giấy/bút rõ, mặt ngẩng khỏi trang. |
| V7-C-121 | U/P | U/P | keep | Vật xám nhỏ trên bàn chưa đủ ID, đầu quay phải. |
| V7-C-123 | U/P | N/P | keep | Hai tay khoanh rõ, nhìn sang người bên phải. |
| V7-C-125 | N/N | U/N | keep | Tay ở mép khung thiếu evidence, đầu hướng trang. | N/N, crop lại để thấy được rõ tay |
| V7-C-126 | N/N | N/N | keep | Tay viết/giữ trang đủ đọc, đầu vào bài. |
| V7-C-127 | U/N | U/N | keep | Vật nhỏ ở bàn tay chưa phân biệt, đầu hướng màn riêng. | exclude |
| V7-C-128 | U/N | N/N | keep | Tay keyboard và vùng laptop đủ rõ. | exclude |
| V7-C-129 | U/N | U/N | keep | Màn laptop che một phần vùng tay, đầu hướng màn riêng. | exclude |
| V7-C-130 | U/N | U/N | keep | Vật đen nhỏ gần keyboard chưa đủ ID. | exclude |
| V7-C-131 | U/N | N/N | keep | Hai tay giữ trang giấy rõ. |
| V7-C-132 | U/N | N/N | keep | Hai tay và giấy viết rõ. |
| V7-C-133 | U/N | N/N | keep | Tay viết/giữ trang đủ quan sát. |
| V7-C-134 | U/N | N/N | keep | Đầu sát trang nhưng đích và hai tay rõ. |
| V7-C-136 | U/N | N/N | recrop | Person box/context chứa cả nhóm người và dãy laptop. | exclude |
| V7-C-137 | U/N | N/N | keep | Đầu hướng giấy, hai tay đủ absence. |
| V7-C-139 | U/N | U/N | keep | Một tay sau màn laptop, đầu hướng máy. | exclude |
| V7-C-141 | U/P | N/P | keep | Tay kiểm đồng hồ rõ, đầu quay trái khỏi vùng bàn. |
| V7-C-142 | U/P | N/P | keep | Tay khoanh đủ đọc, mặt quay phải. | U/P |
| V7-C-143 | U/N | U/N | keep | Laptop che vùng tay, đầu hướng màn máy trên đùi. | exclude |
| V7-C-144 | U/N | N/N | recrop | Người/tay tiền cảnh che vùng keyboard của nam giữa. | exclude |
| V7-D-042 | P/U | U/N | keep | Vật bạc ngang chưa đủ mobile ID. |
| V7-D-044 | P/U | U/P | recrop | Nhiều nam ngồi/đứng cùng rõ; máy nhỏ chưa nhận dạng. | exclude |
| V7-D-046 | P/U | U/N | recrop | Thân người đứng chiếm phải crop, vật cầm còn chỉ cạnh/mặt lưng. | exclude |
| V7-D-049 | U/N | U/N | recrop | Hai người cùng lớn và hai laptop, vùng tay khuất. | exclude |
| V7-D-050 | P/N | P/N | recrop | Phone screen/UI rõ ở đùi nam giữa nhưng có ba người cạnh tranh. |
| V7-D-051 | P/U | U/N | keep | Lưng máy hồng thiếu camera rõ, nữ trước vẫn trội. |
| V7-D-053 | U/N | U/N | keep | Tay còn lại sau laptop, đầu hướng màn riêng. | U/P |
| V7-D-054 | U/N | N/N | recrop | Nam đứng và hai nữ cùng rõ ở vùng giấy chung. | exclude |
| V7-D-056 | U/N | N/N | recrop | Hai nam và tay keyboard chồng, cần box đơn. |
| V7-D-057 | U/N | N/N | recrop | Person box chứa hai nam, nhiều vùng tay/máy. | exclude |
| V7-D-058 | P/U | U/N | recrop | Hai nữ và hai vật cầm cùng lớn, lưng máy chưa rõ. | P/N |
| V7-OE-S002-A01 | N/N | N/N | keep | Tay chống má và tay bàn/màn lớn đủ quan sát. | exclude |
| V7-OE-S003-A01 | P/U | P/N | recrop | Mặt screen/UI mobile rõ, đầu/vai người trước chiếm khung. |
| V7-OE-S006-A01 | N/N | N/N | keep | Màn laptop và tay tương tác, đầu hướng màn riêng. | exclude |
| V7-OE-S009-A01 | U/P | U/P | recrop | Ba nam cùng rõ và hướng ra trước, tay/vùng bài không đủ riêng. | Frame gốc của crop này có thể tận dụng để cắt ra được nhiều crop hữu ích, hãy kiểm tra thật kỹ |
| V7-OE-S012-A01 | N/N | N/N | keep | Hai tay trên giấy và hướng trang rõ. |
| V7-OE-S019-A01 | U/N | N/N | recrop | Nam trái vẫn có mặt/thân lớn cạnh nam chống cằm. | exclude |
| V7-OE-S021-A01 | N/N | N/N | keep | Hai tay viết/giữ giấy rõ. |
| V7-OE-S022-A01 | U/P | N/P | keep | Tay chống cằm đọc được, nhìn ra trước khỏi bàn cờ. | exclude |
| V7-OE-S023-A01 | U/N | U/P | keep | Tay một bên dưới bàn, nhìn khỏi màn máy. | exclude | P/P, crop lại sẽ thấy được phone đặt ở đùi |
| V7-OE-S024-A01 | U/P | N/P | keep | Tay cổ và tay còn lại quan sát được, mặt ngẩng trước. |
| V7-OE-S025-A01 | U/P | U/P | keep | Mặt nhìn trước, vùng tay ngoài crop. |
| V7-OE-S030-A01 | N/N | N/N | keep | Hai tay keyboard và hướng laptop đủ rõ. | exclude |
| V7-OE-S033-A01 | U/P | U/P | recrop | Cả nhóm đứng cùng rõ, thiếu vùng tay riêng cho từng người. | exclude |
| V7-OE-S035-A01 | N/N | N/N | keep | Hai tay găng và vật thí nghiệm rõ, đầu hướng thao tác. |
| E004-EX-C001 | P/P | P/P | keep | Cụm nhiều ống kính trên lưng máy rõ, nhìn ra trước khỏi vật. |
| E004-EX-C002 | P/N | U/N | keep | Mặt/cạnh tối cầm chưa đủ ID. | Thu hẹp crop lại sao cho khít target anchor |
| E004-EX-C003 | U/N | U/N | keep | Lưng vàng/viền chưa đủ camera. | N/N |
| E004-EX-C006 | P/N | P/N | keep | Screen/UI phone trong túi bút còn rõ, đầu hướng máy. |
| E004-EX-C007 | P/N | U/N | keep | Lưng trắng thiếu đặc trưng phân biệt. |
| E004-EX-C008 | P/N | P/N | keep | Ba thành phần camera mặt sau đủ tách ở input. |
| E004-EX-C009 | P/N | P/N | keep | UI/mặt kính mobile trong túi bút rõ. |
| E004-EX-C013 | N/N | U/N | keep | Vật nhỏ trên vùng bàn chưa phân biệt, đầu hướng giấy. |
| E004-EX-C018 | N/N | N/N | keep | Góc từ trên thấy hai tay và trang riêng rõ. |
| E004-EX-C021-R2 | P/N | U/N | keep | Chỉ cạnh/lưng máy cầm, không camera rõ. |
| E004-EX-C022 | N/N | U/N | keep | Lưng máy và dáng cầm không thay ID phone. |
| E004-EX-C023 | P/U | P/N | keep | Màn hình/UI mobile rõ trên trang sách. |
| E004-EX-C026 | N/P | N/P | keep | Tay bút và tay chỉ rõ, nhìn sang người khác. |
| E004-EX-C027 | U/P | N/N | keep | Đầu nghiêng theo trang được nâng trong tay, không tự P vì nghiêng. | N/P |
| E004-EX-C028 | N/N | N/N | keep | Calculator có phím, tay và trang rõ. |
| E004-EX-C029 | N/P | N/P | keep | Hai tay trên bàn rõ, nhìn phải khỏi giấy. |
| E004-EX-C030 | P/N | N/N | keep | Calculator rõ và hai tay/vùng bài đủ đọc. |
| E004-EX-C041 | P/N | P/N | recrop | Phone/UI trên bài rõ nhưng hai sinh viên cùng lớn. |
| E004-EX-C042 | P/P | P/P | recrop | Phone mặt trước ở bàn riêng, mặt quay sang nam đứng; còn nhiều người. |
| E004-EX-C044 | N/P | N/P | keep | Cầm bút nhưng mặt/nhìn trái khỏi trang. |
| E004-EX-C045 | N/N | N/N | keep | Hai tay và bút trên bài, đầu hướng bài riêng. |
| E004-EX-C048 | P/N | U/N | keep | Vật phẳng bên phải chưa đủ dấu hiệu mobile ở input; nhìn sách riêng. | P/N |
| E004-EX-C049 | N/P | N/P | keep | Tay bút và tay còn lại rõ, nhìn sang phải khỏi giấy. |
| E004-EX-C050 | N/P | U/P | keep | Vật trắng trong tay đưa sau ghế không đủ nhận dạng; quay nhìn phía sau. | N/P |
| E004-EX-C051 | N/N | N/N | keep | Hai tay trên giấy, nhìn bài riêng. |
| E004-EX-C054 | N/P | N/P | keep | Hai tay cầm trang rõ, ngẩng nhìn phía trước khỏi trang. |
| E004-EX-C055 | P/P | U/P | keep | Thiết bị phẳng trước tay chưa phân biệt chắc phone/calculator; nhìn trái khỏi bài. |
| E004-EX-C056 | P/P | U/P | keep | Một tay và vùng dưới bàn thiếu, vật đen phẳng chưa có dấu hiệu mobile; nhìn trái. | P/P |
| E004-EX-C066 | P/N | U/N | recrop | Mặt kính đen chưa đủ nhận dạng ở input; mặt và tay người trái cạnh tranh anchor. | P/N |
| E004-EX-C193 | N/N | N/N | keep | Hai tay và bút rõ trên bài riêng. |
| E004-EX-C194 | N/P | N/P | keep | Hai tay rõ, mặt ngẩng nhìn phía trước bên trái khỏi giấy. |
| E004-EX-C195 | P/N | U/N | keep | Vật phẳng bên phải chưa đủ dấu hiệu mobile; hướng sách riêng rõ. | P/N |
| E004-EX-C198 | U/P | N/P | keep | Hai tay với trang sách rõ; mặt hướng trước khỏi trang. |
| E004-EX-C199 | P/P | U/P | recrop | Tay dưới bàn không rõ, quay nhìn người sau; nhiều mặt lớn trong crop. | P/P |
| EXP-RF-001 | N/N | N/N | keep | Hai tay bút và giấy rõ, anchor trước trội hơn người nền. |
| EXP-RF-003 | N/P | N/P | recrop | Hai tay đan không có vật, nhìn phải; phụ đề phủ cổ tay/cẳng tay cần xử lý geometry hoặc rút crop. |
| EXP-RF-004 | U/P | U/P | keep | Tay thiếu trong khung, đầu quay hẳn sang trái khỏi bàn riêng. |
| EXP-RF-006 | N/N | N/N | recrop | Hai tay trên bài rõ; thử bỏ dải chữ đáy nhưng phải giữ đủ tay và bài. |
| EXP-RF-007 | U/P | N/P | keep | Tay bút trên bàn và tay tựa ghế thấy rõ, đầu nhìn sang phải khỏi bài. | Crop lại sao cho thấy toàn bộ tay |
| EXP-RF-008 | U/P | U/U | exclude | Tay thiếu, tóc che mặt và nguồn ít pixel không xác định hướng nhìn đáng tin. | include, U/P, crop rộng ra |
| EXP-RF-009 | U/P | U/P | keep | Một tay ngoài khung; mặt hướng phải phía trước khỏi trang ở đáy. |
| EXP-RF-010 | N/N | N/N | recrop | Hai tay trên bài, đầu hướng trang; bỏ dải chữ đáy nếu giữ được ngữ cảnh. |
| EXP-RF-013 | N/N | N/N | keep | Bút và trang giấy cầm trong tay rõ; hướng về trang riêng. |
| EXP-RF-015 | N/U | U/U | exclude | Mắt nhắm, đầu đè lên tay; không đủ hai target để giữ supervision. |
| EXP-RF-017 | N/P | N/P | keep | Tay bút và vùng làm bài rõ; nhìn thẳng phía trước khỏi bài. |
| EXP-RF-019 | N/P | N/P | keep | Hai tay rõ trên giấy, đầu quay sang phải phía sau. |
| EXP-RF-021 | U/P | U/P | recrop | Crop cắt tay và bài trong nguồn, mặt hướng sang trái; cần lấy lại ngữ cảnh riêng. | N/P, crop dài xuống dưới để thấy được tay |
| EXP-RF-023 | U/P | U/P | recrop | Tay trao giấy bị cắt và đầu tiền cảnh chen vào, nhìn sang người trái. |
| P002-person-01 | P/U | U/N | keep | Lưng vật cầm tay không có camera/màn hình đủ rõ; hướng xuống vùng tay riêng. |
| P006-extra-01 | U/P | N/P | recrop | Tay khoanh rõ nhưng hai mặt gần bằng nhau; target áo xanh nhìn trái. |
| P006-person-01 | P/U | U/N | keep | Vật cầm tay chỉ có lưng mờ, không đủ camera; nhìn vùng tay riêng. |
| P006-person-02 | P/U | U/N | keep | Lưng thiết bị không đủ chi tiết mobile ở input; hướng xuống tay riêng. |
| P007-extra-01 | U/P | N/P | recrop | Tay khoanh rõ, nhìn phía trước; hai mặt lớn cạnh tranh anchor. |
| P007-person-01 | P/U | U/N | keep | Vật cầm tay mờ không đủ dấu hiệu nhận dạng; đầu hướng vùng tay. |
| P007-person-02 | P/U | U/N | keep | Không thấy camera/màn hình của vật cầm tay; hướng xuống vùng tay riêng. |
| P008-extra-01 | U/P | N/P | keep | Hai bàn tay đan trên bàn rõ, nhìn phía trước khỏi bàn. |
| P008-person-01 | P/U | U/N | keep | Thấy lưng và cạnh trơn, không camera rõ; nhìn vật ở vùng tay riêng. |
| P009-person-01 | P/U | U/N | recrop | Thiết bị và bàn tay bị cắt ở đáy; cần mở ngữ cảnh từ nguồn. |
| P019-person-01 | P/U | U/N | keep | Lưng thiết bị nhỏ dưới bàn không có camera đủ rõ; hướng xuống vùng tay riêng. |
| P022-person-01 | P/U | U/N | keep | Vật nhỏ trong tay chỉ còn mảng tối, nhìn vùng tay trên bàn. |
| P029-person-01 | P/U | U/N | keep | Tay bên dưới bàn không thấy đủ; hướng đầu xuống bài riêng. |
| P029-person-02 | P/U | U/N | keep | Một tay ở dưới mép bàn không đủ chi tiết; đầu hướng bài. |
| P030-person-01 | P/U | U/N | keep | Vật dưới bàn tay còn mảng tối chưa đủ mặt kính/camera; nhìn trang riêng. |
| P031-person-01 | P/U | U/N | keep | Thiết bị phẳng đen bị tay che, thiếu dấu hiệu nhận dạng; hướng bài. | P/N |
| P032-person-01 | P/U | P/N | keep | Mặt kính có nội dung màn hình và viền rõ dưới tay; nhìn vùng bài riêng. |
| P033-person-01 | P/P | U/P | keep | Vật phẳng đen không đủ chi tiết phân loại ở input; quay sang phải khỏi bài. | P/P |
| P034-person-01 | P/U | P/N | keep | Mặt kính phản chiếu với viền điện thoại rõ trên bàn, đầu hướng vùng làm việc. |
| P035-person-01 | P/U | P/N | keep | Mặt kính và viền mobile rõ ở tay trên bàn; hướng vùng riêng. |
| P036-person-01 | P/U | P/N | keep | Màn hình và viền phone rõ trên bàn, hướng vùng làm việc riêng. |
| P038-person-01 | P/U | P/N | recrop | Màn hình phone rõ; người sau có mặt lớn và person box bao hai người. |
| P039-person-01 | P/U | P/N | recrop | Mặt kính/UI rõ trên bàn riêng, cần tách người sau khỏi anchor. |
| P043-person-01 | P/U | U/N | keep | Lưng đen không thấy camera rõ, hướng vùng tay riêng. |
| P047-extra-01 | U/P | N/P | keep | Hai tay nghỉ trên bàn rõ; quay phải khỏi vùng bài. |
| P047-person-01 | P/U | U/N | keep | Vật cầm có lưng trơn mờ, không đủ camera; nhìn vùng tay và sách riêng. |
| V7-A-028 | N/N | N/N | keep | Tay bút và tay tựa đầu rõ, vẫn nhìn trang riêng. |
| V7-A-030 | N/N | U/N | keep | Tay còn lại không thấy; nghiêng đầu nhưng mắt hướng trang riêng. |
| V7-A-032 | N/N | N/N | keep | Bút và trang giấy trong hai tay rõ, nhìn bài riêng. |
| V7-A-034 | N/N | U/N | keep | Một tay ngoài vùng thấy rõ, đầu hướng sách riêng. |
| V7-B-010 | N/N | N/N | recrop | Tay viết và bài rõ nhưng hai mặt cạnh tranh, người trái chen sát đầu target. |
| V7-B-026 | N/N | N/N | keep | Hai tay và bài rõ, nhìn trang riêng. |
| V7-B-046 | N/N | N/N | keep | Hai tay rõ trên bài, nhìn trang riêng. |
| V7-C-055 | U/P | U/P | keep | Một tay thiếu phía bàn, quay hẳn sang phải khỏi bàn riêng. |
| V7-C-059 | U/P | U/P | recrop | Tay/vật nhỏ mờ, nhìn phải; nhiều mặt tương đương trong crop. |
| V7-C-061 | U/P | U/P | recrop | Box bao cả hai người, target tiền cảnh quay về người sau; tay và vùng bàn riêng thiếu. |
| V7-C-063 | U/P | U/P | recrop | Nhìn sang trái khỏi vùng riêng; crop thiếu tay và ngữ cảnh bàn ở nguồn. |
| V7-C-065 | U/P | N/P | recrop | Hai tay trên bàn rõ, quay trái; người sau còn mặt lớn cạnh tranh. |
| V7-C-069 | U/P | N/P | keep | Hai tay trên giấy rõ nhưng mặt hướng sang trái về bạn, không hướng trang riêng. |
| V7-C-075 | U/P | U/P | keep | Tay và bài bị cắt đáy nguồn; đầu quay phải rõ. |
| V7-C-081 | U/P | U/P | keep | Tay dưới màn hình không đủ quan sát; nhìn người bên trái. |
| V7-C-083 | U/P | N/P | recrop | Hai tay với mẩu giấy rõ, nhìn sang phải; box cắt thân và vùng bàn riêng dù nguồn còn. |
| V7-C-085 | U/P | U/P | recrop | Tay riêng bị che, nghiêng sang nhìn bàn khác; hai mặt cùng lớn. |
| V7-C-088 | U/N | N/N | keep | Hai tay với bút và giấy rõ, hướng trang riêng. |
| V7-C-090 | U/P | U/P | keep | Một tay sau trang thiếu, mặt hướng sang bạn bên phải. |
| V7-C-091 | U/N | N/N | recrop | Hai tay bút trên bài, crop cắt nửa mặt và thân; cần chỉnh box một người. | U/N |
| V7-OE-S084-A01 | N/N | N/N | keep | Tay tựa đầu và tay trên giấy rõ, đầu nghiêng nhưng hướng bài riêng. |
| V7-OE-S085-A01 | N/P | N/P | recrop | Hai tay trên bàn rõ, nhìn trái; người sau còn mặt lớn cần tách. |
| V7-OE-S111-A01 | P/N | U/N | recrop | Tay viết bị cắt đáy để tránh phụ đề, cần xem khả năng giữ đủ ngữ cảnh. |
| V7-OE-S112-A01 | N/N | U/N | keep | Tay kia sau sách không thấy đủ, đầu hướng sách riêng. |
| V7-OE-S113-A01 | U/P | U/N | keep | Tay dưới bàn không rõ, nhìn xuống vùng bài riêng. |
| V7-OE-S113-A02 | U/N | U/N | keep | Tay cạnh bàn thấp chỉ thấy phần nhỏ; mặt hướng giấy riêng. |
| V7-OE-S114-A01 | N/N | U/N | keep | Calculator có phím rõ nhưng tay còn lại dưới bàn; hướng trang riêng. |
| V7-OE-S114-A02 | U/P | U/P | keep | Vật ở mép bàn phải chưa đủ nhận dạng; mắt nhìn khỏi bài về phía trái trước. | N/P |
| V7-OE-S116-A01 | P/P | U/P | keep | Vật đen dưới tay chưa đủ mặt kính/camera, nhìn thẳng phía trước. |
| V7-OE-S116-A02 | N/N | N/N | keep | Hai tay trên bài và bút rõ, đầu hướng trang. |
| EXP-SCB-003 | N/P | N/P | keep | Hai tay khoanh rõ, nhìn phía trước khỏi sách. |
| EXP-SCB-004 | U/P | U/P | keep | Tay và mặt bàn khuất sau thân, đầu ngẩng về phía trước. |
| EXP-SCB-006 | N/P | N/P | keep | Hai tay đan rõ trên bàn, nhìn trước khỏi bài. |
| EXP-SCB-007 | U/P | N/P | keep | Một tay trước ngực và tay kia buông rõ, đầu quay phải khỏi giấy. |
| EXP-SCB-021 | N/N | N/P | keep | Hai tay trên bài rõ nhưng đầu quay sang trái khỏi trang. |
| EXP-SCB-024 | U/P | U/P | recrop | Nhìn phía trước, tay bị đầu tiền cảnh che; cần giảm đầu người trước nếu nguồn cho phép. |
| EXP-SCB-033 | U/P | N/P | keep | Hai tay khoanh rõ trên bàn, mặt hướng trái khỏi giấy. |
| EXP-SCB-037 | U/P | N/P | recrop | Tay khoanh, nhìn phía trước; mặt tiền cảnh lớn cạnh tranh target. |
| EXP-SCB-040 | U/P | U/P | keep | Tay gần mặt và vùng bàn quá ít chi tiết để xác nhận không device, nhìn trái. |
| EXP-SCB-041 | U/P | U/P | keep | Tay khuất sau thân, đầu quay trái khỏi bàn riêng. | exclude |
| EXP-SCB-045 | U/P | U/P | keep | Tay thiếu và nguồn tối, đầu ngẩng phía trước rõ. |
| EXP-SCB-047 | U/P | U/P | keep | Tay còn lại khuất, mặt ngẩng trước khỏi bàn. |
| SCB-turnhead-001 | U/P | U/P | keep | Tay dưới bị che, mặt hướng trước khi giơ tay; không suy phone từ động tác. |
| SCB-turnhead-002 | U/P | U/U | exclude | Mặt/tay/vật bị nhòe nặng, hướng mắt so với trang không đủ chắc. |
| SCB-turnhead-003 | U/P | U/P | keep | Vật trắng giơ bên mặt không nhận dạng mobile, mặt quay phải khỏi bàn. |
| SCB-turnhead-004 | U/P | U/P | keep | Một tay khuất ở mép phải, mặt quay phải khỏi bài. |
| SCB-turnhead-005 | U/P | U/P | keep | Tay và bàn riêng phía trước thân bị khuất, đầu hướng lên phía trước. |
| SCB-turnhead-006 | U/P | U/P | keep | Tay ngoài khung, mặt ngẩng khỏi bàn rõ dù nguồn tối. | exclude |
| SCB-turnhead-007 | U/P | U/P | keep | Tay/vật nhỏ quá mờ để quyết định phone, mặt ngẩng phía trước khỏi bài. | N/P |
| SCB-turnhead-008 | U/P | N/P | keep | Hai tay đặt trên bàn đủ rõ, quay mặt khỏi bài về phía máy quay. |
| SCB-turnhead-009 | U/P | U/U | exclude | Nguồn quá nhòe cả tay và mặt, không dựa tên turnhead để gán P. |
| SCB-turnhead-010 | U/P | U/P | keep | Tay khuất sau thân, đầu ngẩng phía trước rõ. | exclude |
| SCB-turnhead-011 | U/P | U/P | keep | Tay thiếu, mặt ngẩng ra trước khỏi bàn; đầu tiền cảnh chỉ phần nhỏ. | exclude |
| SCB-turnhead-012 | U/P | N/P | keep | Tay khoanh rõ trên bàn, đầu quay trái khỏi giấy. |
| SCB-turnhead-013 | U/P | U/P | keep | Một tay khuất bởi người trước, mặt ngẩng sang trái khỏi sách. |
| SCB-turnhead-016 | U/P | N/P | keep | Hai tay khoanh trên bàn rõ, nhìn sang trái khỏi bài. |
| SCB-turnhead-018 | U/P | U/U | exclude | Chỉ lưng đầu nhòe, thiếu tay và hướng nhìn so với vùng riêng. |
| SCB-turnhead-019 | U/P | U/U | exclude | Mặt và tay nhòe không đủ xác định hai target. |
| SCB-turnhead-020 | U/N | U/U | exclude | Mặt cúi bị đầu tiền cảnh che và nhòe, tay không đủ rõ. |
| SCB-turnhead-021 | U/P | U/U | exclude | Nguồn quá ít chi tiết, không xác nhận hướng nhìn hoặc tay. |
| SCB-turnhead-024 | U/P | U/P | keep | Tay khuất sau thân, đầu quay trái rõ khỏi vùng bàn trước. |
| SCB-turnhead-026 | U/P | N/P | recrop | Tay bút và tay nghỉ rõ, nhìn trái; mặt tiền cảnh cạnh tranh cần tách. |
| SCB-turnhead-027 | U/P | N/P | keep | Hai tay trên bàn rõ, mặt ngẩng trước khỏi sách. |
| SCB-turnhead-028 | U/P | U/U | exclude | Chỉ thấy sau đầu/thân, không đủ phân biệt nhìn bài với phía trước. |
| V7-C-001 | U/P | U/P | recrop | Đầu quay phải khỏi giấy, tay bị người đối diện che; nhiều thân/mặt cạnh tranh. |
| V7-C-003 | U/P | N/P | recrop | Tay trên bàn đủ rõ, nhìn khỏi bài; box rộng chứa nhiều mặt cùng cỡ. |
| V7-C-005 | U/P | N/P | keep | Tay khoanh rõ trên bàn, đầu quay phải khỏi vùng riêng. |
| V7-C-007 | U/P | U/P | recrop | Tay bị tiền cảnh che, nhìn sang trái; cần bỏ phần người trước. |
| V7-C-009 | U/P | U/P | recrop | Đầu quay trái rõ nhưng tay/giấy bị nhiều người che và box chứa nhóm. |
| V7-C-011 | U/P | N/P | keep | Tay tựa mặt và tay trên bàn đủ rõ, mặt ngẩng phía trước. |
| V7-C-013 | U/P | N/P | keep | Hai tay gập trên bàn rõ, mặt ngẩng trước khỏi bài. |
| V7-C-015 | U/N | U/U | recrop | Mặt cúi mờ và tay bị người trước che, cần tách target rồi xét lại hướng nhìn. |
| V7-C-016 | U/N | U/N | recrop | Hướng xuống trang riêng nhưng tay bị che/cắt, nhiều thân trong box. | exclude |
| V7-C-017 | U/P | U/P | recrop | Tay target bị mặt tiền cảnh che, đầu quay trái khỏi bàn. |
| V7-C-019 | U/P | U/P | recrop | Đầu quay trái về người cạnh, tay khuất và context box lệch mất vùng riêng. |
| V7-C-021 | U/P | U/P | recrop | Ngẩng trước khỏi bàn, tay che ở mặt; nhiều mặt cùng cỡ trong crop. | N/P |
| V7-C-023 | U/P | U/U | recrop | Đầu nghiêng chưa đủ phân biệt nhìn bài hay bên trái, người trước che tay. |
| V7-C-033 | U/P | N/P | recrop | Tay khoanh rõ, nhìn trước; person box hiện gồm cả người bên phải. |
| V7-C-035 | U/P | U/P | recrop | Box gồm hai người, target giơ bút nhìn trước; tay còn lại bị che. |
| V7-C-039 | U/P | U/P | keep | Tay phía trước thân thiếu, đầu ngẩng trước khỏi bàn. |
| V7-C-041 | U/P | N/P | keep | Tay giơ và tay trên bàn rõ, quay trái khỏi trang. |
| V7-C-043 | U/P | U/P | recrop | Mặt ngẩng trước nhưng tay bị người tiền cảnh che; nhiều mặt cạnh tranh. |
| V7-C-047 | U/P | U/P | recrop | Target quay trái, crop cắt thân/tay và chứa nhiều phần người sau. |
| V7-C-049 | U/P | U/P | recrop | Một tay không đủ rõ, nhìn phía trước; nhiều mặt cùng cỡ. |
| V7-C-051 | U/P | N/P | recrop | Hai tay gập rõ, đầu quay phải; nhiều mặt và thân trong crop. |
| V7-C-053 | U/P | U/P | keep | Tay không giơ bị khuất, đầu ngẩng phía trước rõ. |
| V7-C-093 | U/N | N/P | recrop | Tay bút trên bàn rõ, nhìn người cạnh; hai mặt và thân cạnh tranh. | N/N |
| V7-C-094 | U/N | N/N | recrop | Hai tay trên giấy, hướng trang riêng; box gồm nhiều đầu/thân. |
| V7-OE-S086-A01 | U/P | N/P | recrop | Target giơ tay nhìn trước, tay kia trên bàn; box quá rộng chứa nhóm. | exclude |
| V7-OE-S087-A01 | N/N | N/N | recrop | Box nhóm hai người; nữ bên trái viết và hướng bài riêng, cần định vị lại một anchor. |
| V7-OE-S088-A01 | U/N | U/N | recrop | Một tay khuất cạnh bàn, hướng sách riêng; người sau lớn và box chứa nhiều thân. |
| V7-OE-S089-A01 | U/N | U/U | recrop | Box cả nhóm không có một anchor rõ, chưa thể gán nhãn cho một người. | Tách thành 2 crop là 2 bạn nam và nữ đang cầm bút cúi đầu viết đi N/N |
| V7-OE-S090-A01 | U/N | U/U | recrop | Hai người ngang nhau trong box, cần xác định target trước khi gán hai nhãn. | Crop bạn nam áo đen N/N |
| V7-OE-S091-A01 | U/N | N/N | recrop | Người trước khoanh tay hướng sách nhưng box chứa nhiều người, cần anchor một người. |
| V7-R8-C-003 | U/P | N/P | recrop | Hai tay trên bàn rõ, quay nhìn người bên trái; nhiều mặt cùng cỡ. |
| V7-R8-C-006 | U/N | N/P | keep | Tay bút và tay giấy rõ, mặt quay trái khỏi trang riêng. | N/N |
| EXP-SCB-001 | N/N | N/N | keep | Hai tay trên giấy rõ, hướng xuống bài riêng. |
| EXP-SCB-002 | N/N | N/N | keep | Hai tay trên trang rõ, đầu nghiêng theo sách riêng. |
| EXP-SCB-005 | N/P | N/P | keep | Tay khoanh rõ, nhìn sang phải khỏi mặt bàn. | N/N |
| EXP-SCB-009 | N/N | N/N | keep | Hai tay và bút trên trang, hướng bài riêng. |
| EXP-SCB-010 | N/P | N/P | keep | Hai tay giữ sách rõ, nhìn trước khỏi sách. |
| EXP-SCB-011 | U/N | U/N | keep | Trang đọc rõ nhưng bàn tay ít pixel không đủ loại trừ vật khác; hướng trang cầm. | exclude |
| EXP-SCB-012 | U/N | N/N | keep | Hai tay trên bàn đủ rõ, hướng xuống bài riêng. |
| EXP-SCB-013 | U/N | N/P | keep | Tay khoanh đủ rõ, đầu ngẩng trước khỏi sách. | N/N |
| EXP-SCB-014 | N/P | N/N | recrop | Target bên phải cúi nhìn bàn, hai tay khoanh; mặt người trái cùng cỡ. |
| EXP-SCB-015 | N/U | N/U | keep | Tay tựa đầu và tay ngực rõ; mắt nhắm/che không xác định hướng nhìn. |
| EXP-SCB-016 | N/N | N/N | keep | Hai tay và giấy rõ, đầu hướng trang riêng. |
| EXP-SCB-017 | U/N | U/N | keep | Tay khuất sau sách, đầu hướng trang riêng. |
| EXP-SCB-020 | N/N | N/U | keep | Hai tay đan rõ, mặt úp xuống tay không đủ xác định nhìn trang. | N/N |
| EXP-SCB-025 | N/N | N/N | keep | Hai tay khoanh trên bàn, đầu hướng trang riêng. |
| EXP-SCB-026 | N/N | N/N | keep | Tay gập trên bàn rõ, nhìn xuống sách riêng. |
| EXP-SCB-027 | N/N | N/N | keep | Tay tựa má và tay trên bàn rõ, hướng sách riêng. |
| EXP-SCB-028 | N/N | N/N | keep | Hai tay trên giấy rõ, đầu hướng bài riêng. |
| EXP-SCB-034 | N/U | N/N | keep | Hai tay giữ trang, đầu hướng trang cầm thuộc vùng riêng. |
| EXP-SCB-042 | N/P | N/P | keep | Tay khoanh trên bàn đủ rõ, mặt ngẩng trước khỏi sách. | N/N |
| EXP-SCB-043 | N/U | U/P | keep | Một tay sau sách đứng không thấy, mặt nhìn phía trước khỏi trang. | U/N |
| EXP-SCB-044 | N/N | N/N | keep | Tay bút và tay trên ngực rõ, nhìn trang riêng. |
| EXP-SCB-048 | U/N | U/U | recrop | Lưng đầu và sách giơ che hướng, người trước lớn; cần kiểm tra lại target/context. | exclude |
| SCB-read-001 | U/N | N/U | keep | Tay khoanh đủ rõ nhưng tóc che mặt, không ép N từ dáng cúi. | N/N |
| SCB-read-003 | U/N | U/N | keep | Tay khuất sau thân, đầu hướng xuống trang ngay trước mặt. |
| SCB-read-004 | U/N | N/U | keep | Tay giữ sách và tay nghỉ đủ rõ, tóc che hoàn toàn mặt. | Chọn crop khác đi, hãy phân tích kỹ frame gốc và bạn sẽ thấy có rất nhiều người có thể quan sát rất rõ ràng và thích hợp hơn nhiều để trở thành crop, trong đó thì đa số là N/N |
| SCB-read-005 | U/N | U/U | exclude | Tay và mặt nhòe nặng, không đủ xác nhận hai target. |
| SCB-read-006 | U/N | U/U | exclude | Đầu tiền cảnh che tay, mặt nhòe không xác định hướng. |
| SCB-read-007 | U/N | U/U | exclude | Nguồn quá ít pixel cho mặt và tay, mở crop không khôi phục chi tiết. |
| SCB-read-008 | U/N | U/P | recrop | Mặt nhìn trước khỏi bài nhưng đầu người trước che gần hết tay và cạnh tranh anchor. | exclude |
| SCB-read-009 | U/N | U/U | exclude | Tóc che mặt, tay khuất và nguồn mờ, không có target đáng tin. |
| SCB-read-010 | U/N | U/N | keep | Tay còn lại khuất/cắt đáy, đầu hướng trang riêng. |
| SCB-read-012 | U/N | U/P | recrop | Nhìn trước khỏi trang, tay dưới bị đầu tiền cảnh che. |
| SCB-read-013 | U/N | U/U | exclude | Chỉ mảng đầu/tay nhòe, không đủ hai target. |
| SCB-read-014 | U/N | U/U | exclude | Mặt bị bàn tay/tóc che, tay còn lại khuất, không có supervision đáng tin. |
| SCB-read-015 | N/N | N/N | keep | Hai tay trên bài đủ rõ, hướng trang riêng. | Thêm một crop cho bạn nam ngồi đầu bàn phía gần cô giáo N/P | 
| SCB-read-016 | U/N | U/U | exclude | Mặt và vật gần miệng nhòe, không xác định phone hay hướng nhìn. |
| SCB-read-017 | U/N | U/U | exclude | Mặt che bởi tóc và tay mờ khuất, không đủ hai target. |
| SCB-read-019 | U/N | U/U | exclude | Mặt và tay không đủ chi tiết để gán chắc nhãn. |
| SCB-read-020 | U/N | N/N | keep | Hai tay trên sách rõ, hướng trang riêng. |
| SCB-read-021 | U/N | N/N | keep | Hai tay khoanh trên bàn rõ, nhìn sách riêng. |
| SCB-read-022 | U/N | U/U | exclude | Nhiều người chồng và nguồn nhòe, không có hai target đáng tin cho anchor. |
| SCB-read-023 | U/N | N/N | keep | Hai tay khoanh rõ trên bàn, mặt hướng sách riêng. |
| SCB-read-025 | U/N | U/U | exclude | Tay bị đầu tiền cảnh che và mặt nhòe, không đủ hai target. |
| SCB-read-026 | U/N | U/U | exclude | Nguồn rất ít pixel, tóc che mặt và vật/tay không phân biệt được. |
| SCB-read-027 | U/N | U/N | keep | Một tay dưới bàn thiếu, mặt hướng trang đang cầm rõ. |
| SCB-read-028 | U/N | U/N | keep | Tay khuất sau thân, đầu hướng xuống giấy riêng rõ. |
| SCB-write-001 | N/N | N/N | keep | Hai tay trên bài và bút đủ rõ, hướng xuống trang riêng. |
| SCB-write-002 | N/N | N/N | keep | Hai tay trên giấy và bút rõ, đầu hướng bài riêng. |
| SCB-write-004 | U/N | U/N | recrop | Đầu hướng trang nhưng tay bị đầu tiền cảnh che, cần giảm người trước. | exclude |
| SCB-write-005 | U/N | U/U | exclude | Mặt và tay nhòe mạnh, không đủ xác nhận hai target. |
| SCB-write-006 | N/N | N/N | keep | Tay bút và tay giấy rõ, đầu cúi sát bài riêng. |
| SCB-write-007 | U/N | U/U | exclude | Đầu tiền cảnh che gần hết tay và trang, mặt target nhòe/khuất. |
| SCB-write-008 | U/N | U/N | recrop | Hướng bài riêng nhưng tay/vật mờ và hai người cạnh tranh anchor. | exclude |
| SCB-write-009 | N/N | N/N | keep | Hai tay và bút trên sách rõ, hướng bài riêng. |
| SCB-write-010 | U/N | N/N | keep | Hai tay trên trang và bút đủ rõ, nhìn bài riêng. |
| SCB-write-011 | U/N | U/N | recrop | Hướng xuống trang, tay và phần bài bị đầu tiền cảnh che. |
| SCB-write-012 | U/N | N/N | keep | Tay bút và tay giữ bài đủ rõ, hướng bài riêng. | exclude |
| SCB-write-013 | N/N | N/N | keep | Hai tay trên bài rõ, đầu hướng trang riêng. |
| SCB-write-014 | N/N | U/N | keep | Vật đỏ giữa hai tay chưa phân biệt chắc dụng cụ hay device; đầu hướng vùng bài. | N/N |
| SCB-write-016 | U/N | U/N | keep | Tay/vật nhỏ mờ chưa đủ xác nhận phone N, hướng vùng bài riêng. | N/N |
| SCB-write-017 | U/N | U/U | exclude | Đầu người trước che mặt và tay, không có target đáng tin. |
| SCB-write-018 | U/N | U/N | recrop | Hướng trang riêng rõ, tay bị đầu tiền cảnh che; cần giảm người trước. | Frame gốc của crop có rất nhiều người có thể trở thành crop rõ ràng hơn, hãy phân tích thật kỹ frame và lựa chọn cho hợp lý nhất |
| SCB-write-019 | U/N | U/N | keep | Tay/vật trên bàn chưa đủ chi tiết, hướng xuống bài riêng. | Frame gốc của crop có rất nhiều người có thể trở thành crop rõ ràng hơn, hãy phân tích thật kỹ frame và lựa chọn cho hợp lý nhất |
| SCB-write-020 | U/N | N/N | keep | Bút và hai tay trên giấy đủ rõ, đầu hướng bài riêng. |
| SCB-write-021 | U/N | N/N | keep | Tay bút và tay giữ sách đủ rõ, đầu hướng trang riêng. |
| SCB-write-022 | U/N | U/U | exclude | Pixel hóa mạnh, tóc che mặt và tay/vật không phân biệt rõ. |
| SCB-write-023 | U/N | N/P | keep | Hai tay đan trên bàn rõ, mặt ngẩng phía trước khỏi bài. | Frame gốc của crop có rất nhiều người có thể trở thành crop rõ ràng hơn, hãy phân tích thật kỹ frame và lựa chọn cho hợp lý nhất |
| SCB-write-024 | U/N | U/U | exclude | Tóc/mặt nhòe và tay che khuất, nguồn không đủ để cứu hai target. |
| SCB-write-025 | U/N | U/U | exclude | Mặt và tay nhòe mạnh, không gán từ dáng ngồi. |
| SCB-write-027 | U/N | U/N | keep | Vật/tay gần trang thiếu chi tiết phân loại, đầu hướng trang riêng. | Frame gốc của crop có rất nhiều người có thể trở thành crop rõ ràng hơn, hãy phân tích thật kỹ frame và lựa chọn cho hợp lý nhất |
| SCB-write-028 | U/N | N/N | keep | Hai tay trên sách đủ rõ, đầu hướng trang riêng. |
| V7-C-002 | U/N | U/U | recrop | Box gồm nhiều người, không xác định một anchor để gán nhãn. | exclude |
| V7-C-004 | U/N | U/U | recrop | Hai mặt cùng lớn, tay bị người trước che; cần tách anchor và lấy vùng bài. | Frame gốc của crop có rất nhiều người có thể trở thành crop rõ ràng hơn, hãy phân tích thật kỹ frame và lựa chọn cho hợp lý nhất |
| V7-C-006 | U/N | N/N | recrop | Nữ giữa viết trên bài riêng, tay rõ nhưng nhiều mặt/thân cùng cỡ. |
| V7-C-008 | U/N | N/N | recrop | Hai tay giữ sách rõ, đầu hướng sách; đầu tiền cảnh và người trái cạnh tranh. | U/P |
| V7-C-010 | U/N | U/N | recrop | Nữ trước hướng sách, tay khuất mép bàn; hai người lớn trong khung. | Crop bạn khác rõ ràng hơn |
| V7-C-018 | U/N | N/N | recrop | Bút và hai tay đủ rõ, hướng bài; đầu tiền cảnh lớn cần giảm. |
| V7-C-026 | U/N | U/U | exclude | Nhiều người chồng, tay và mặt nhòe không đủ xác định hai target. |
| V7-C-028 | U/N | U/U | recrop | Box bao nhiều học sinh tương đương; chưa có một target rõ. | Frame gốc của crop có rất nhiều người có thể trở thành crop rõ ràng hơn, hãy phân tích thật kỹ frame và lựa chọn cho hợp lý nhất |
| V7-C-030 | U/N | N/N | keep | Hai tay và bút trên trang rõ, hướng bài riêng. |
| V7-C-038 | U/N | N/N | recrop | Nữ giữa giữ sách và hướng trang riêng; nhiều mặt cùng cỡ cần tách. |
| V7-C-042 | U/N | N/N | keep | Hai tay và bút rõ trên bài; đầu tiền cảnh chỉ phần nhỏ, target trội. |
| V7-C-044 | U/N | U/N | recrop | Đầu hướng xuống bài nhưng crop cắt tay/giấy; nguồn còn ngữ cảnh để sửa. |
| V7-C-046 | U/N | U/N | recrop | Vật/tay ở bàn chưa đủ nhận dạng, mặt hướng vùng riêng; nhiều người ngang nhau. | Thay bằng crop bạn áo đỏ ngồi dãy trên tiền cảnh P/P |
| V7-C-048 | U/N | U/U | exclude | Tóc che mặt và tay/vật nhòe, không đủ supervision. |
| V7-C-050 | U/N | N/U | keep | Tay tựa đầu và tay khoanh rõ; tóc che hướng nhìn, không suy N từ cúi đầu. | N/N |
| V7-C-052 | U/N | N/N | recrop | Nữ giữa tay khoanh và hướng sách, nam trái còn mặt/thân lớn. |
| V7-C-054 | U/N | N/N | keep | Hai tay trên trang rõ, đầu hướng sách; anchor trước trội. |
| V7-OE-S093-A01 | N/N | U/U | recrop | Box bao nhóm nhiều người, cần xác định một target trước gán nhãn. | Tách thành 2 crop là hai bạn nam tiền cảnh ngồi cạnh nhau, đều là N/N |
| V7-OE-S094-A01 | U/P | N/P | recrop | Target giơ tay nhìn trước, tay kia trên bàn rõ; nhiều mặt cùng cỡ. |
| V7-OE-S096-A01 | N/N | N/N | keep | Hai tay trên trang rõ, mặt hướng sách riêng. |
| V7-OE-S099-A01 | N/N | U/U | recrop | Hai nữ ngang nhau, một nhìn bài một nhìn phải; không gán chung box nhóm. | Cả 4 bạn ngồi bàn đầu đều có thể trở thành 4 crop khác nhau, tình từ bạn nam trở đi sẽ là N/P, N/N, N/N, N/P |
| V7-OE-S101-A01 | U/N | N/N | recrop | Target trước hướng giấy, tay rõ; nhiều mặt lớn phía sau và box nhóm. |
| V6-SB-003 | P/U | U/N | keep | Vật phẳng trên bàn không đủ kính/camera ở input; hướng vùng bài riêng. | Frame gốc của crop này có nhiều người có thể trở thành crop hữu ích, hãy nghiên cứu thật kỹ và crop phù hợp nhất |
| V6-SB-004 | P/U | U/N | recrop | Lưng vật trong tay target không rõ camera; người sau và vật riêng gây cạnh tranh. |
| V6-SB-005 | P/U | U/N | keep | Cạnh/lưng trắng trong tay không đủ nhận dạng mobile, hướng tay riêng. |
| V6-SB-008 | P/U | U/N | recrop | Lưng vật trong tay thiếu camera rõ; người phía sau có mặt lớn cạnh tranh. |
| V6-SB-009 | P/N | U/N | keep | Vật tối dưới tay trên bàn chưa đủ mặt kính/chi tiết; hướng vùng riêng. |
| V6-SB-010 | P/N | U/N | keep | Vật tím phẳng chưa đủ dấu hiệu mobile, mặt hướng vùng bàn riêng. |
| V6-SB-011 | U/N | U/N | keep | Vật nhỏ bị hai tay che không xác nhận mobile, hướng sách riêng. |
| V6-SB-012 | U/N | U/N | keep | Vật trên trang chỉ mảng chữ nhật mờ, không đủ nhận dạng; đầu hướng trang. |
| V6-SB-013 | P/U | P/N | keep | Màn hình màu và viền phone phân biệt được trên bàn; nhìn vùng riêng. |
| V6-SB-014 | P/U | U/N | keep | Lưng đen trong tay không thấy camera đủ rõ, nhìn vùng tay riêng. |
| V6-SB-015 | P/U | U/N | keep | Vật nằm dưới tay mờ không đủ nhận dạng; hướng vùng bàn riêng. |
| V6-SB-016 | P/U | U/P | keep | Lưng vàng không có camera rõ, mặt ngẩng phía trước khỏi tay. |
| V6-SB-018 | U/P | U/P | recrop | Tay target bị người trước che, mặt quay trái; đầu người trước lớn hơn anchor. | exclude |
| V6-SB-019 | U/P | U/P | keep | Hai tay dưới bàn khuất, đầu quay sang phải khỏi vùng riêng. |
| V6-SB-021 | U/P | U/U | recrop | Crop cắt gần hết đầu và tay, cần lấy lại target từ nguồn. | exclude |
| V6-SB-022 | U/P | U/P | keep | Vật trong tay nhòe chưa xác định phone, mặt quay phải khỏi bài. | N/P, có thể chỉnh lại crop để có thể quan sát toàn diện hơn |
| V6-SB-023 | U/P | P/P | keep | Mặt kính đen với viền trắng phone rõ trên bàn, mặt quay trái khỏi bàn. |
| V6-SB-028 | U/P | U/P | keep | Tay dưới bàn thiếu, mặt quay trái khỏi sách riêng. |
| V6-SB-029 | N/P | N/P | recrop | Hai tay đan rõ, mặt hướng trước khỏi sách; nhiều mặt lớn trong crop. |
| V6-SB-030 | P/P | P/P | recrop | Phone màn hình/viền trên bàn riêng, mặt quay phải; người sau và device riêng cần tách. |
| V6-SB-032 | U/P | U/P | recrop | Một tay khuất, mặt ngẩng trước khỏi sách; nhiều mặt cạnh tranh. |
| V6-SB-033 | N/N | N/N | keep | Bút và hai tay trên bài rõ, hướng trang riêng. |
| V6-SB-034 | N/N | N/N | recrop | Hai tay với trang sách rõ, đầu hướng bài; người cạnh còn mặt lớn. |
| V6-SB-035 | N/N | U/N | keep | Một tay sau sách thiếu, đầu hướng trang cầm rõ. |
| V6-SB-038 | N/N | N/N | keep | Hai tay giữ sách rõ, hướng trang riêng. |
| V6-SB-040 | N/N | U/N | recrop | Vật hồng trên bàn chưa nhận dạng chắc, hướng vùng riêng; nhiều mặt trong box. | N/N |
| V6-SB-041 | N/N | N/N | recrop | Tay trên sách và tay tựa rõ, nhìn trang; hai người cùng lớn. |
| V6-SB-042 | N/N | N/P | recrop | Người ngồi trước giữ giấy và nhìn trước, box còn bao người đứng và nhóm. | N/N |
| V6-SB-043 | N/N | N/N | keep | Hai tay trên bài rõ, mặt hướng trang riêng; target trước trội. |
| V6-SB-044 | N/N | U/U | recrop | Box gồm nhiều người, chưa có một anchor rõ; không gán chung nhãn. | exclude |
| V6-SB-045 | N/N | U/N | keep | Một tay bị cắt phía trái nguồn, hướng sách riêng. | Thay thành crop bạn ngồi cạnh tiền cảnh N/P |
| V6-SB-046 | N/N | N/N | keep | Tay bút và tay gập rõ, đầu cúi theo trang riêng. |
| V6-SB-047 | N/N | N/N | recrop | Nữ áo xanh giữ trang và nhìn bài; box kéo cả người phía trước vào anchor. |
| V6-SB-048 | N/N | U/U | recrop | Hai người cùng lớn và mặt/tay ít chi tiết; cần tách target rồi xét lại. | Frame gốc của crop này có nhiều người có thể trở thành crop hữu ích, hãy nghiên cứu thật kỹ và crop phù hợp nhất | 
| V6R2-MP-001 | N/N | U/N | keep | Một tay dưới bàn thiếu, đầu hướng trang riêng. | exclude |
| V6R2-MP-002 | N/N | U/N | keep | Vật dưới tay không đủ nhận dạng, đầu hướng trang riêng; không suy phone từ cử chỉ. | N/N |
| V6R2-MP-004 | U/P | N/P | recrop | Tay tựa cổ và tay nghỉ đủ rõ, nhìn trước; người trái cùng cỡ. |
| V6R2-MP-005 | U/P | U/P | recrop | Một tay khuất, mặt ngẩng trước; nhiều mặt cùng cỡ cần tách. |
| V6R2-MP-006 | U/P | U/P | keep | Vật tím dưới tay chưa phân biệt chắc, tay kia thiếu; nhìn trước khỏi trang. |
| V6R2-MP-007 | U/P | U/P | recrop | Tay dưới bàn thiếu, nhìn trước; ba mặt cùng lớn cạnh tranh target. |
| V6R2-MP-008 | U/P | U/N | recrop | Mặt và tay bị cắt sát mép; hướng trang riêng, cần kiểm khả năng mở lại source. | exclude |
| V6R2-MP-009 | P/U | U/N | keep | Lưng/cạnh vật trong tay không có camera rõ; hướng vùng tay riêng. |
| V6R2-MP-010 | P/U | U/N | keep | Vật trong tay chỉ lưng mờ, không đủ mobile; hướng vùng tay riêng. |
| V6R2-MP-011 | P/U | U/N | keep | Lưng đỏ bị tay che không đủ camera/màn hình; hướng tay riêng. |
| V6R2-MP-012 | P/P | U/P | keep | Vật phẳng đen trên bàn chưa đủ chi tiết nhận dạng; mặt ngẩng trước khỏi bài. | P/P |
| V6R2-MP-013 | P/P | U/P | keep | Vật trên bàn chỉ mảng tối/viền mờ, không đủ phone P; mặt ngẩng trước. | P/P |
| V6R2-MP-014 | U/N | U/N | keep | Hai tay dưới bàn thiếu, đầu hướng bài riêng. |
| V6R2-MP-016 | U/P | U/P | keep | Vật nhỏ trong tay không rõ mobile, mặt hướng trước khỏi sách. |
| V6R2-MP-018 | U/P | U/U | exclude | Tay khuất, mặt không đủ phân biệt nhìn bài hay phía trước. |
| V6R2-MP-019 | N/N | N/U | keep | Tay tựa đầu và tay trên giấy rõ, tóc che hướng nhìn. | N/N |
| V6R2-MP-020 | N/N | N/N | keep | Hai tay đan trên bài rõ, hướng xuống trang riêng. |
| V6R2-MP-021 | U/N | U/N | keep | Tay sau sách khuất, đầu hướng trang riêng. |
| V6R2-MP-022 | U/P | U/P | recrop | Tay dưới thiếu, mặt hướng trước; người sau có mặt sát cùng cỡ. |
| V6R2-MP-023 | U/P | U/P | keep | Tay còn lại dưới sách thiếu, mặt hướng trước khỏi trang. |
| V6R2-MP-024 | N/P | N/P | recrop | Hai tay giữ sách rõ, mặt ngẩng trước; nhiều mặt lớn phía sau. |
| V6R2-MP-025 | N/N | U/N | recrop | Một tay sau laptop thiếu, nhìn màn hình riêng; mặt người sau cạnh tranh. | exclude |
| V6R2-MP-026 | N/N | N/N | keep | Hai tay trên giấy rõ, đầu hướng bài riêng. |
| V6R2-MP-030 | P/U | U/N | keep | Vật nhỏ trong tay chỉ mảng màu chưa đủ màn hình/camera; hướng vùng tay trên bài. |
| V6R2-MP-031 | P/U | U/N | keep | Vật nghiêng cạnh trong tay không đủ nhận dạng; hướng xuống vùng tay trên bàn. |
| V6R2-MP-032 | P/U | U/N | keep | Vật dưới hai tay mờ không đủ nhận dạng; đầu hướng vùng bài riêng. |
| V6R2-MP-034 | P/U | U/N | keep | Vật dưới tay chỉ mảng màu/viền không rõ, đầu hướng vùng riêng. |
| V6R2-MP-035 | P/U | U/N | keep | Lưng/cạnh vật nhỏ trong hai tay không camera rõ; hướng vùng tay riêng. |
| V6R2-MP-037 | U/P | U/P | recrop | Hai tay khuất, mặt hướng trước; nhiều mặt lớn phía sau. |
| V6R2-MP-038 | P/P | U/P | keep | Vật phẳng trên bàn thiếu dấu hiệu mobile rõ, mặt hướng trước khỏi bàn. | P/P |
| V6R2-MP-039 | N/P | N/P | recrop | Tay đan rõ, mặt hướng trước khỏi sách; ba mặt cạnh tranh. |
| V6R2-MP-040 | P/U | U/N | recrop | Lưng vật dưới tay không đủ camera; người sau và device riêng cạnh tranh. |
| V6R2-MP-041 | N/N | N/N | keep | Hai tay trên trang rõ, đầu hướng bài riêng. | U/N |
| V6R2-MP-043 | P/P | U/P | recrop | Vật phẳng đen trên bàn chưa đủ nhận dạng, mặt ngẩng trước; nhiều mặt lớn. | P/P |
| V6R2-MP-044 | U/P | U/P | keep | Tay gần đáy bị cắt và tay kia khuất, đầu ngẩng trước rõ. |
| V6R2-MP-046 | P/U | U/U | exclude | Vật phẳng trên bàn chưa đủ nhận dạng, mặt úp xuống tay không rõ hướng nhìn. | P/N |
| V6R2-MP-047 | U/P | U/P | keep | Hai tay dưới bàn thiếu, mặt ngẩng trước khỏi sách; người sau nhỏ hơn và tách biệt. |
| V6R2-MP-048 | U/P | N/P | recrop | Tay bút và tay gần miệng đủ rõ, nhìn trước; người sát bên cạnh tranh. |
| V6R2-MP-049 | U/P | U/P | keep | Tay khuất sau ghế, mặt ngẩng trước khỏi sách. |
| V6R2-MP-050 | U/P | U/P | keep | Hai tay khuất sau ghế, mặt hướng trước khỏi vùng riêng. |
| V6R2-MP-053 | P/U | U/P | recrop | Vật trong tay không đủ nhận dạng, mặt hướng trước; người sau và device riêng cạnh tranh. |
| V6R2-MP-057 | U/P | U/U | exclude | Một tay thiếu, mặt mờ không phân biệt hướng bài hay phía trước. |
| V6R2-MP-058 | U/P | U/P | keep | Tay dưới bàn thiếu, đầu ngẩng trước khỏi sách đủ rõ. | exclude |
| V6R2-MP-059 | U/P | N/U | keep | Tay tựa trán và tay trên bàn rõ, mặt che không xác định hướng nhìn. | N/P |
| V6R2-MP-061 | U/P | U/P | keep | Vật/tay ở đáy thiếu chi tiết, mặt hướng trước khỏi vùng riêng. | exclude |
| V6R2-MP-063 | U/N | N/N | recrop | Hai tay và sách rõ, hướng trang; crop cắt một phần đầu bên trái cần sửa. | exclude |
| V6R2-MP-066 | P/P | U/P | keep | Cạnh/lưng thiết bị cầm không đủ camera/màn hình, quay trái khỏi vùng riêng. |
| V6R2-MP-067 | P/P | U/P | keep | Vật trên bàn chỉ mảng tối, mặt ngẩng trước khỏi bàn. |
| V6R2-MP-068 | P/U | U/N | keep | Lưng đen trong tay không camera rõ, hướng vùng tay riêng. |
| V6R2-MP-072 | U/P | U/P | keep | Tay khuất sau ghế, mặt ngẩng trước khỏi vùng riêng. |
| V6R2-MP-073 | U/P | U/P | keep | Vật nhỏ giữa hai tay chưa đủ nhận dạng, mặt ngẩng trước. |
| V6R2-MP-074 | U/N | U/N | recrop | Tay còn lại không rõ, hướng xuống sách; nhiều mặt lớn phía sau. |
| V6R2-MP-079 | P/U | U/N | keep | Mặt lưng/cạnh đen không camera rõ, đầu hướng vật riêng trong tay. |
| V6R2-MP-080 | P/U | P/N | recrop | Màn hình màu và viền phone rõ trên bàn, hướng vùng riêng; mặt người sau lớn. |
| V6R2-MP-081 | P/P | U/P | keep | Vật phẳng đen chưa đủ dấu hiệu nhận dạng; đầu ngẩng trước khỏi bài. | P/P |
| V6R2-MP-084 | P/U | U/N | keep | Vật đen chỉ lưng không có camera rõ, nhìn vùng tay riêng. |
| V6R2-MP-085 | P/U | U/N | keep | Vật trong tay chỉ lưng/cạnh mờ, hướng xuống vùng tay riêng. |
| V6R2-MP-089 | P/U | U/N | recrop | Vật nhỏ trong tay mờ, hướng bài riêng; thân và device người sau cạnh tranh. |
| V6R2-MP-090 | P/U | U/N | keep | Vật dưới tay chỉ mảng màu, không đủ mobile; đầu hướng vùng bài riêng. |
| V6R2-MP-091 | N/P | U/P | recrop | Một tay sau laptop khuất, mặt quay trái khỏi màn hình; người sau mặt lớn. | exclude |
| V6R2-MP-092 | P/P | U/P | recrop | Vật đen trên bàn thiếu dấu hiệu nhận dạng, quay phải; người sau với device riêng. | P/P |
| V6R2-MP-093 | P/U | U/N | keep | Lưng đen trong tay không có camera rõ, đầu hướng vùng tay riêng. |
| V6R2-SB-001 | P/U | U/N | recrop | Vật trong tay không đủ camera/màn hình, hướng tay; mặt người sau sát target. |
| V6R2-SB-002 | P/U | U/N | recrop | Lưng vật không đủ nhận dạng, đầu hướng tay; mặt tiền cảnh chen lớn. |
| V6R2-SB-003 | P/U | U/P | keep | Vật tím phẳng dưới tay chưa đủ nhận dạng, mặt ngẩng trước khỏi sách. |
| V6R2-SB-006 | P/U | U/N | keep | Lưng vàng không có camera tách biệt tại input, đầu hướng vật trong tay riêng. |
| V6R2-SB-008 | U/P | U/P | recrop | Hai tay khuất dưới bàn, mặt quay ra trước; hai mặt phía sau cạnh tranh anchor. |
| V6R2-SB-009 | U/N | U/N | recrop | Đầu hướng sách nhưng tay và thân bị khung rất hẹp cắt; thử nới về phía trong source. |
| V6R2-SB-010 | U/P | U/P | keep | Lưng vật đỏ trong tay chưa đủ nhận mobile, đầu quay trái khỏi vùng tay; người mép không có mặt trọn. |
| V6R2-SB-011 | U/P | U/P | keep | Một tay khuất dưới bàn, đầu quay sang vùng người bên trái khỏi bàn riêng. |
| V6R2-SB-013 | N/N | N/N | recrop | Bút và hai tay trên sách đủ thấy, đầu hướng bài; nhiều mặt phía sau và bên trái nằm trong khung. |
| V6R2-SB-014 | N/U | U/N | recrop | Tay nâng bút rõ nhưng tay kia dưới bàn, đầu hướng trang; các mặt phía sau quá gần target. |
| V6R2-SB-015 | N/N | N/N | recrop | Tay gần cằm và tay đặt sách đủ thấy, đầu hướng sách; mặt người sau cạnh tranh. |
| V6R2-SB-016 | U/N | U/N | keep | Hướng sách rõ, hai tay bị bàn và người tiền cảnh che; mặt target vẫn trội. |
| V6R2-SB-017 | N/N | N/N | keep | Hai tay và bút trên giấy đọc được, đầu hướng bài; người nền nhỏ và lệch khỏi target. |
| V6R2-SB-018 | N/U | N/N | recrop | Target phía trước viết trên giấy, hai tay rõ; person box bao cả hai trẻ có mặt tương đương. |
| V7-B-002 | N/N | N/N | keep | Hai tay và bút trên sách đủ thấy, hướng sách rõ; target trội ở tiền cảnh. |
| V7-B-016 | N/N | U/N | recrop | Tay còn lại không tách rõ khỏi thân và bàn, đầu hướng bài; ba người chen trong crop. | Crop người khác dễ quan sát hơn |
| V7-B-018 | N/N | N/N | recrop | Hai tay trên giấy và hướng bài rõ; mặt phải và đầu tiền cảnh cạnh tranh anchor. |
| V7-B-020 | N/N | N/N | keep | Bút, hai tay và hướng trang rõ; người cạnh chỉ còn phần thân/mặt ở mép, target trội. |
| V7-B-022 | N/N | U/N | keep | Đầu hướng bài rõ, một phần tay mất tại biên source; không suy absence hoặc nới ra ngoài ảnh gốc. | Frame gốc của crop này có nhiều người có thể trở thành crop hữu ích, hãy nghiên cứu thật kỹ và crop phù hợp nhất |
| V7-B-024 | N/N | N/P | recrop | Target giữa khoanh tay đủ thấy, ngẩng ra trước khỏi sách; person box bao nhiều học sinh. |
| V7-B-028 | N/N | N/N | recrop | Hai tay trên trang và hướng bài rõ; mặt người sau lớn sát đầu target, cần thu khung. |
| V7-B-030 | N/N | N/N | recrop | Target giữa viết trên trang với hai tay rõ; person box bao ba người cạnh nhau. |
| V7-B-034 | N/N | N/N | keep | Hai tay thao tác vật dụng trên bàn đủ thấy, đầu hướng vùng tay riêng. |
| V7-B-042 | N/N | U/N | keep | Hướng bài rõ nhưng phần tay mất tại cạnh phải source; chữ phía dưới không đè vùng hành vi. | Frame gốc của crop này có nhiều người có thể trở thành crop hữu ích, hãy nghiên cứu thật kỹ và crop phù hợp nhất |
| V7-B-048 | N/N | N/N | keep | Hai tay trên giấy, bút và hướng đầu về bài đủ rõ; target tiền cảnh trội. |
| V7-B-062 | N/N | U/N | recrop | Hướng bài rõ nhưng tay bị đầu tiền cảnh che; nhiều mặt cạnh tranh, cần sửa khung. |
| E004-CN-042 | U/P | U/P | recrop | Tay giơ rõ, tay còn lại bị người trước che; nhìn phía giáo viên khỏi bàn, đầu tiền cảnh chiếm lớn. |
| E004-CN-043 | U/N | N/N | keep | Bút và vùng hai tay tại giấy đủ thấy, đầu hướng trang riêng; target rõ ở tiền cảnh. | U/N |
| E004-CN-044 | N/P | N/P | recrop | Tay chống má và tay đặt giấy đủ thấy, đầu quay sang phải khỏi trang; mặt người cạnh lớn. |
| E004-CN-045 | N/P | N/P | keep | Hai tay trên giấy có bút, mặt hướng trước/phải khỏi trang; người cạnh chỉ còn phần tay. |
| E004-CN-046 | U/N | U/N | recrop | Nhìn sách dựng riêng, tay bị sách và biên che; khung ngang cắt đỉnh đầu dù source còn đầu. |
| E004-CN-047 | U/N | U/N | recrop | Đầu hướng sách dựng, một tay sau sách chưa đủ quan sát; người bên phải và đầu tiền cảnh chen khung. |
| E004-CN-048 | N/N | N/N | keep | Sách mở và hai tay giữ rõ, nhìn xuống sách; người đứng là anchor trội. |
| E004-CN-050 | U/N | N/N | keep | Hai tay trên trang và bút đọc được, đầu hướng bài; target trước trội hơn người nền. |
| E004-CN-052 | N/U | N/U | recrop | Hai tay trên bàn không có vật mơ hồ, tóc che kín mặt và đích nhìn; người cạnh chiếm lớn. | N/N |
| E004-CN-053 | N/N | N/N | recrop | Target áo đen viết và nhìn trang, hai tay rõ; tay và tóc người tiền cảnh chen cùng vùng giấy. |
| E004-CN-055 | N/N | U/N | recrop | Bút và hướng trang rõ nhưng tay còn lại khuất sau đầu tiền cảnh lớn; cần thử khung sạch hơn. |
| E004-CN-056 | N/N | U/N | recrop | Đầu hướng giấy, tay còn lại bị thân người trước che; cần giảm người tiền cảnh và kiểm lại input. |
| E004-EX-C078 | P/N | U/N | keep | Chỉ thấy lưng/cạnh vật trong tay, không có camera hoặc màn hình rõ tại input; đầu hướng tay riêng. |
| E004-EX-C079 | P/N | U/N | keep | Vật cầm ngang chỉ thấy lưng đen không có camera rõ, đầu hướng vùng tay riêng. | exclude |
| E004-EX-C080 | P/P | U/N | keep | Vật áp tai chỉ thấy lưng/ốp không đủ camera, không suy P từ tư thế gọi; mặt hướng màn hình riêng. | exclude |
| E004-EX-C082 | P/N | U/N | keep | Lưng ốp nhiều màu, chấm tối không đủ tách camera ở input; nhìn vật trong tay riêng. |
| E004-EX-C083 | P/N | P/N | keep | Cụm camera ở góc lưng thiết bị có các vòng tối tách được, đầu hướng thiết bị riêng. |
| E004-EX-C084 | U/N | U/N | keep | Tay cầm cốc rõ nhưng tay còn lại dưới bàn/khuất thân, đầu hướng vùng laptop riêng. | exclude |
| E004-EX-C085 | N/N | N/N | keep | Hai tay tại bàn phím laptop đủ thấy, nhìn màn hình riêng; không có mobile mơ hồ. | exclude |
| E004-EX-C089 | N/P | N/N | recrop | Target áo xanh có hai tay tại bài/laptop riêng, nhìn vùng thao tác; hai mặt và thân lớn cạnh nhau. | N/P |
| E004-EX-C102 | U/N | N/N | recrop | Hai tay viết trên trang và hướng bài rõ, nhưng person box cắt đỉnh đầu và crop chứa ghế tiền cảnh lớn. |
| E004-EX-C179 | N/U | U/N | keep | Bàn sửa thiết bị có các linh kiện/vật phẳng chưa phân loại đủ ở input, không suy phone từ bối cảnh; đầu hướng tay riêng. | exclude |
| E004-EX-C183 | N/N | N/N | recrop | Hai tay và bút tại trang rõ, đầu hướng bài; mặt người bên phải cùng cỡ cần giảm trong khung. |
| E004-EX-C184 | N/U | N/N | keep | Hai tay tại giấy và bút đọc được, đầu chếch về trang riêng; người mép chỉ là phần phụ. | U/N |
| E004-EX-C185 | P/U | P/U | keep | Màn hình xanh có viền máy nằm sát tay riêng nhận được mobile; tóc che mặt nên đích nhìn chưa chắc. | P/N |
| V7-R8-C-007 | U/P | N/P | keep | Hai tay chồng gần cằm đủ thấy, mặt ngẩng nhìn trước khỏi trang; target rõ. |
| V7-R8-C-008 | U/N | N/N | keep | Bút và hai tay tại trang đọc được qua mép ghế, đầu nghiêng nhưng vẫn hướng bài riêng. |
