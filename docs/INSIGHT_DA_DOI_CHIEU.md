# Insight đã đối chiếu cho đề tài Rating sách Goodreads

Tài liệu này cung cấp số liệu và cách diễn giải để người học tự viết báo cáo. Các giá trị dưới đây là trạng thái mặc định của mẫu chính, chưa áp dụng bộ lọc tương tác bổ sung. Đối chiếu ngày 16 tháng 11 năm 2026; số hiển thị được làm tròn, phép tính dùng giá trị đầy đủ.

## Phạm vi và nguồn số liệu

Nguồn làm việc là thư mục gốc của repository. Mọi kết quả lấy từ `data/processed/books_cleaned_master.csv`, `book_genres_bridge.csv` và các CSV trong `eda_tables/`; không lấy số từ chiều cao cột của ảnh biểu đồ.

- Master: **11.127 bản ghi**, 11.127 `book_id` duy nhất. Một dòng là bản ghi Goodreads gắn với ấn bản, chưa phải một tác phẩm độc lập.
- Mẫu đủ điều kiện: **11.046** bản ghi có Rating 1–5 và lượt chấm dương.
- Mẫu chính: **8.402** bản ghi đủ điều kiện và có **ít nhất 100 lượt chấm**. Các bản ghi ngoài mẫu vẫn được bảo toàn trong master.
- Mẫu số trang: **8.385**; năm hợp lệ: **8.401**; có nhà xuất bản: **8.399**; có thể loại: **8.400**.
- N nhóm luôn là **số `book_id` duy nhất**. Quy ước n≥30 là ngưỡng trình bày, không phải bảo đảm đại diện hay khoảng tin cậy.
- Mean là trung bình Rating giữa các bản ghi, mỗi bản ghi có trọng số bằng nhau; không phải trung bình có trọng số theo lượt chấm. SD dùng độ lệch chuẩn mẫu (`ddof=1`).

Nguồn `middlelight/goodreadsbookswithgenres` v1 có metadata cập nhật **30/12/2022**, dựa trên `jealousleopard/goodreadsbooks` v2 cập nhật **09/03/2020**; tác giả bộ nền cho biết bắt đầu thu thập qua API năm 2019. Ngày cập nhật không phải ngày thu thập chính xác của từng trường. Khoảng 300 bản ghi được bổ sung thể loại từ Google Books. Chưa có căn cứ gọi đây là Goodreads hiện tại hoặc mẫu ngẫu nhiên toàn nền tảng. Căn cứ: `data/raw/source_metadata.json`, `docs/nguon_du_lieu.md`.

Fingerprint CSV nguồn: `721fc3bbe6367e91f2d3537d2cbe1c1ca4b585535d8ce63862c38a353d662b97`.

## Mức nền của Rating

Trong mẫu chính n=8.402, Rating trung bình **3,954683**, trung vị **3,97**, SD mẫu **0,265769**, Q1 **3,79**, Q3 **4,14**, thấp nhất **2,40**, cao nhất **4,82**. Có **18** bản ghi dưới 3,0; **4.562** từ 3,0 đến dưới 4,0; **3.822** từ 4,0 trở lên. Các số này cộng đúng 8.402. Q1–Q3 mô tả 50% giữa phân phối; không gọi là khoảng tin cậy.

Nguồn: `descriptive_primary.csv` và đếm trực tiếp từ master với `primary_sample=True`.

## Bảy yếu tố và cách diễn giải

### Thể loại

**12 nhãn có nhiều bản ghi nhất trong mẫu chính**, không phải 12 nhãn có Rating cao nhất:

| Nhãn thể loại | N distinct | Rating trung bình | Trung vị |
| --- | --- | --- | --- |
| Fiction | 5.817 | 3,929 | 3,940 |
| Classics | 2.721 | 4,010 | 4,010 |
| Nonfiction | 2.394 | 4,015 | 4,030 |
| Literature | 2.383 | 3,938 | 3,940 |
| Novels | 2.191 | 3,872 | 3,880 |
| Fantasy | 2.152 | 3,987 | 4,000 |
| Historical,Historical Fiction | 1.533 | 3,924 | 3,930 |
| Audiobook | 1.395 | 3,946 | 3,970 |
| Mystery | 1.366 | 3,894 | 3,910 |
| Romance | 1.316 | 3,901 | 3,910 |
| History | 1.260 | 4,021 | 4,040 |
| Historical | 1.216 | 3,967 | 3,980 |

Trong 12 nhãn này, History có mean **4,021** (n=1.260), Novels **3,872** (n=2.191). Đây là khác biệt quan sát giữa các tập sách có cơ cấu khác nhau; chưa có kiểm soát đồng thời tác giả, năm, độ dài hoặc mức phổ biến. Không viết “History làm Rating tăng” hoặc gọi bảng này là “Top 12 thể loại tốt nhất”.

Bridge toàn bộ có **94.794 cặp bản ghi–nhãn**, **890 nhãn**, không lặp cặp khóa. Trong mẫu chính có **79.278 cặp**, thuộc **8.400 bản ghi**, với **793 nhãn** xuất hiện; **278 nhãn** có n≥30. Một bản ghi nằm trong nhiều nhóm, vì vậy không cộng N của các nhóm thành tổng số sách. Nhãn `Historical,Historical Fiction` giữ nguyên như một nhãn nguồn; dấu chấm phẩy mới là dấu tách nhãn của CSV, không tự tách tiếp bằng dấu phẩy. `Audiobook` là tag của nguồn, không được tự suy thành định dạng đã xác minh.

Nguồn: `group_genre_top12_by_size.csv`, `group_genre_all.csv`, bridge và master.

### Nhà xuất bản

**12 nhà xuất bản có N lớn nhất**, giữ nguyên khóa phân biệt hoa/thường của `publisher_clean` trong EDA:

| Nhà xuất bản | N distinct | Rating trung bình | Trung vị |
| --- | --- | --- | --- |
| Vintage | 312 | 3,896 | 3,910 |
| Penguin Books | 245 | 3,911 | 3,940 |
| Penguin Classics | 176 | 3,952 | 3,975 |
| Mariner Books | 136 | 3,955 | 3,945 |
| Ballantine Books | 134 | 3,878 | 3,920 |
| Harper Perennial | 106 | 3,906 | 3,910 |
| Bantam | 105 | 3,892 | 3,890 |
| Pocket Books | 100 | 3,911 | 3,920 |
| HarperCollins | 90 | 4,047 | 4,130 |
| VIZ Media LLC | 86 | 4,248 | 4,280 |
| Berkley | 81 | 3,903 | 3,900 |
| Del Rey | 75 | 4,051 | 4,040 |

Trong 12 nhóm đông nhất, VIZ Media LLC có mean **4,248** (n=86); Ballantine Books **3,878** (n=134). Vintage có nhiều bản ghi nhất, **312**, nhưng mean **3,896**. Nếu xét tất cả **57 nhóm đủ n≥30**, Library of America có mean quan sát cao nhất **4,281** (n=34). Phải phân biệt rõ xếp theo N và xếp theo Rating; không suy ra thứ hạng chất lượng nhà xuất bản.

Trong mẫu chính có **1.538 khóa publisher** có dữ liệu; **3** bản ghi thiếu. Đây là so sánh cơ cấu danh mục theo bản ghi, có thể gồm nhiều ấn bản của cùng tác phẩm. Trường nhà xuất bản gắn với ấn bản, Rating có thể khác cấp tổng hợp.

Power BI cần dùng khóa nhóm phân biệt hoa/thường để đối chiếu đúng EDA. Nếu gộp bằng nhãn trực tiếp, `VIZ Media` và `Viz Media`, hoặc `University Of Chicago Press` và `University of Chicago Press`, có thể bị cộng nhóm. Không đổi raw/master hoặc tự gộp nhóm EDA trong phần viết báo cáo.

Nguồn: `group_publisher_all.csv`, `group_publisher_n30.csv`, master.

### Ngôn ngữ

English có **8.212/8.402 = 97,7386%** mẫu chính. Chỉ **3 nhóm** đạt ngưỡng n≥30:

| Nhóm ngôn ngữ | N distinct | Rating trung bình | Trung vị |
| --- | --- | --- | --- |
| English | 8.212 | 3,954 | 3,970 |
| spa | 91 | 3,969 | 3,960 |
| fre | 48 | 3,950 | 3,960 |

Mean giữa ba nhóm khoảng **3,950–3,969**, chênh lệch nhỏ trên mẫu rất mất cân đối. Không dùng các nhóm rất ít quan sát, ví dụ tiếng Nhật n=8, để kết luận ngôn ngữ nào tốt hơn. Ngôn ngữ của ấn bản không phải quốc gia hoặc ngôn ngữ gốc của tác phẩm.

Nguồn: `group_language_all.csv`, `group_language_n30.csv`; tỷ lệ English tính trực tiếp từ master.

### Số trang

| Khoảng trang | N distinct | Mean Rating | Trung vị | Q1 | Q3 |
| --- | --- | --- | --- | --- | --- |
| 1-200 | 1.861 | 3,953 | 3,970 | 3,780 | 4,140 |
| 201-400 | 4.128 | 3,912 | 3,930 | 3,760 | 4,090 |
| 401-600 | 1.558 | 3,981 | 3,990 | 3,840 | 4,140 |
| 601+ | 838 | 4,119 | 4,130 | 3,960 | 4,290 |

Nhóm **601+ trang** có mean **4,118675** (n=838), cao hơn nhóm **201–400** mean **3,911744** (n=4.128), chênh **0,206931 điểm**. Tuy nhiên nhóm **1–200** có mean **3,952617**, cao hơn nhóm **201–400**; vì vậy không mô tả “càng dài thì Rating càng cao”.

Trên **8.385 cặp đủ số trang**, Spearman số trang–Rating là **0,125570**; Pearson thang gốc **0,199001**. Đây là liên hệ dương nhỏ ở tổng thể. Nếu dùng thang log cho trục X, phải ghi rõ; Pearson với `ln(1+pages)` chỉ **0,092300**, là phép đo khác.

Khi tạm giới hạn 20–2.000 trang, n=**8.300**, Spearman **0,128699**, gần mức chính. Đây là kiểm tra độ nhạy, không phải căn cứ xóa vĩnh viễn sách mỏng hoặc tuyển tập. Phân tầng Literature cho rho **0,263884** (n=2.382), Novels **0,279576** (n=2.189), Fantasy **0,039865** (n=2.149); không suy từ hệ số tổng thể sang mọi thể loại.

Nguồn: `group_pages_all.csv`, `correlations_by_threshold.csv`, `correlations_pages_sensitivity.csv`, `correlations_stratified.csv`.

### Năm và thập niên xuất bản

Các nhóm thập niên đủ n≥30:

| Đầu thập niên | N distinct | Rating trung bình | Trung vị |
| --- | --- | --- | --- |
| 1960 | 40 | 4,019 | 4,045 |
| 1970 | 125 | 4,015 | 4,030 |
| 1980 | 417 | 3,998 | 4,010 |
| 1990 | 1.852 | 3,968 | 3,980 |
| 2000 | 5.833 | 3,945 | 3,960 |
| 2010 | 100 | 3,989 | 3,995 |

Nhóm **2000–2009** chiếm **5.833** bản ghi, mean **3,944713**; nhóm **1990–1999** n=1.852, mean **3,968283**; **2010–2019** n=100, mean **3,988600**. Đây là so sánh Rating ở snapshot giữa các nhóm năm xuất bản của bản ghi/ấn bản; không có lịch sử Rating của một sách theo thời gian. Chưa xác minh đây là năm xuất bản đầu tiên của tác phẩm.

Spearman năm–Rating **−0,061631** trên **8.401 cặp**, cho thấy liên hệ đơn điệu tổng thể rất nhỏ. Không kết luận Rating đang giảm theo thời gian. Khi pivot còn yêu cầu số trang hợp lệ, nhóm 2010–2019 còn **99** bản ghi; mẫu số phụ thuộc phép tính.

Nguồn: `group_decade_all.csv`, `group_decade_n30.csv`, `correlations_by_threshold.csv`, `pivot_n_decade_by_pages.csv`.

### Số lượt chấm

Với n=**8.402**, Spearman lượt chấm–Rating **0,066525**; Pearson thang gốc **0,043961**; Pearson với `ln(1+n_ratings)` **0,079353**. Số lượt chấm có phân bố lệch mạnh: trung vị **1.823**, trung bình **23.742,443**, tối đa **4.597.666**. Scatter nên dùng trục lượt chấm dạng log và công bố phép biến đổi/thang trục.

Mức phổ biến trong snapshot và Rating là hai đại lượng cần đọc riêng. Bản ghi Twilight (`book_id=41865`) đứng đầu lượt chấm của mẫu với **4.597.666** lượt, Rating **3,59**; bản ghi The Complete Calvin and Hobbes (`book_id=24812`) có Rating cao nhất mẫu **4,82**, với **32.213** lượt chấm. Ví dụ này minh họa xếp hạng theo hai chỉ tiêu khác nhau, không chứng minh nguyên nhân. Không gọi lượt chấm là số người mua, doanh số hoặc số độc giả duy nhất; không cộng lượt chấm giữa các ấn bản để suy ra tổng người đọc.

Nguồn: `correlations_by_threshold.csv`, `descriptive_primary.csv`, hai bản ghi đối chiếu trực tiếp từ master.

### Số bài review

Với n=**8.402**, Spearman review–Rating **−0,018432**, Pearson thang gốc **0,032627**, Pearson với `ln(1+n_reviews)` **−0,008324**. Các hệ số gần 0, dấu khác nhau theo phép đo. Trong bốn ngưỡng lượt chấm, Spearman biến thiên từ **0,025681** đến **−0,048728**. Kết luận phù hợp là chưa thấy liên hệ đơn điệu tổng thể rõ ràng trong các phạm vi đã thử; không kết luận review làm tăng/giảm Rating.

Số review trung vị **99**, trung bình **716,375**, tối đa **94.265**. `n_reviews` là số bài nhận xét; `n_ratings` là số lượt chấm. Không thay thế hai biến này cho nhau.

Nguồn: `correlations_by_threshold.csv`, `descriptive_primary.csv`.


## Gợi ý ra quyết định trong phạm vi dữ liệu

**Cho người đọc tìm sách.** Chọn thể loại và các điều kiện phù hợp trước, rồi đọc
đồng thời Rating và số lượt chấm của từng bản ghi. Có thể thử ngưỡng 100, 500 và
1.000 để xem danh sách còn lại; đây là thao tác khảo sát, không phải ngưỡng bảo đảm
chất lượng. Toàn mẫu ở ba ngưỡng lần lượt có 8.402, 6.153 và 5.114 bản ghi; khi lọc
thêm thể loại phải lấy N thực đang hiện. Không loại một cuốn sách chỉ vì ít lượt chấm.

**Cho đơn vị giới thiệu sách.** Trình bày hai thông tin riêng: mức độ phổ biến qua
lượt chấm và Rating quan sát. Twilight có 4.597.666 lượt chấm nhưng Rating 3,59;
The Complete Calvin and Hobbes có Rating 4,82 với 32.213 lượt chấm. Vì thứ hạng
hai chỉ tiêu khác nhau, không dùng riêng lượng tương tác để gắn nhãn “được đánh giá
cao”. Top N của dashboard xếp theo Rating trong tập đã lọc; không phải mô hình
cá nhân hóa hoặc danh sách những tác phẩm tốt nhất của toàn Goodreads.

**Khi lựa chọn danh mục sách.** Có thể dùng các khác biệt giữa nhóm để đặt câu hỏi
nghiên cứu tiếp, chưa dùng chúng để quy kết chất lượng publisher, ngôn ngữ hoặc
quyết định mua sách theo một bảng mean. English chiếm 97,74% mẫu; các thể loại
chồng lấn; nhóm publisher và độ dài có cơ cấu tác phẩm khác nhau. Cần xem thêm
N, nội dung sách và mục tiêu người đọc. Dữ liệu này chưa có giá/doanh số hoặc
hiệu quả kinh doanh để đưa ra khuyến nghị lợi nhuận.

**Nếu mở rộng nghiên cứu.** Ưu tiên bổ sung định danh tác phẩm và ấn bản đã xác minh,
thời điểm ghi nhận Rating/count, năm xuất bản đầu tiên, cùng mẫu ngôn ngữ cân đối
hơn. Đây là đề xuất thu thập dữ liệu tiếp theo; các thông tin đó chưa được tạo,
nối hoặc giả định là đã có trong bộ kết quả hiện tại.

## Bảng hệ số dùng khi đối chiếu biểu đồ

| Biến với Rating | N cặp | Spearman | Pearson gốc | Pearson ln1p |
| --- | --- | --- | --- | --- |
| Số trang | 8.385 | 0,125570 | 0,199001 | 0,092300 |
| Lượt chấm | 8.402 | 0,066525 | 0,043961 | 0,079353 |
| Số review | 8.402 | -0,018432 | 0,032627 | -0,008324 |
| Năm xuất bản | 8.401 | -0,061631 | -0,065336 | — |

Các hệ số này là mô tả tổng thể của mẫu chính, không phải hệ số hồi quy đã kiểm soát đồng thời bảy yếu tố. Không diễn giải 0,126 là “giải thích 12,6% Rating”.

## Độ nhạy và mức bất định

| Lượt chấm tối thiểu | N | Mean Rating | Trung vị | SD mẫu |
| --- | --- | --- | --- | --- |
| 1 | 11.046 | 3,943134 | 3,960000 | 0,295213 |
| 100 | 8.402 | 3,954683 | 3,970000 | 0,265769 |
| 500 | 6.153 | 3,961482 | 3,970000 | 0,259547 |
| 1.000 | 5.114 | 3,964447 | 3,975000 | 0,254279 |

Mean đổi từ **3,943134** ở ngưỡng 1 lên **3,964447** ở ngưỡng 1.000, khoảng **0,021312 điểm**. Kết quả này cho thấy mean ít thay đổi theo bốn ngưỡng đã thử, không chứng minh toàn bộ kết luận đều ổn định hay dữ liệu đại diện hơn.

Giảm lặp gần đúng theo tên–chuỗi người đóng góp, ưu tiên count lớn nhất, cho mẫu **8.189** bản ghi. Spearman trang–Rating **0,125268** (n=8.172), lượt chấm **0,066520** (n=8.189), review **−0,019365** (n=8.189), năm **−0,060781** (n=8.188). Đây chỉ là một quy tắc giảm lặp; không khẳng định đã xác định được tác phẩm độc lập. Nguồn: `correlations_edition_sensitivity.csv` và `docs/phuong_phap_va_gioi_han.md`.

Chưa có khoảng tin cậy/kiểm định chênh lệch hay mô hình nhân quả được kiểm chứng trong các bảng này. Sai số hệ thống do chọn mẫu, khác cấp ấn bản/tác phẩm, cơ cấu thể loại, tác giả và tuổi sách không được giải quyết chỉ bằng N lớn. Không dùng “khác biệt có ý nghĩa thống kê” nếu chưa có phép kiểm định tương ứng.

## Ánh xạ hình cuối với nhận xét và mẫu số

Các ảnh dùng trong báo cáo nằm trong 04_PowerBI_BanChinh/BieuDo_BaoCao. Các số trong tài liệu này mô tả trạng thái mặc định; sau lọc phải lấy N và giá trị mới từ dashboard.

| Hình | Tên file | Mẫu số và cách đọc |
|---|---|---|
| 1 | 01_PhanPhoi_Rating_MauChinh.png | 8.402 bản ghi; histogram khoảng [x;x+0,1), thống nhất ranh giới thập phân với Power BI. |
| 2 | 02_Boxplot_Rating_NhomSoTrang.png | 8.385 bản ghi có trang; boxplot bốn nhóm trang, không phải boxplot thể loại hoặc publisher. |
| 3 | 03_TrungBinh_Rating_NhomSoTrang.png | Bốn nhóm trang có N riêng; mean không tăng đơn điệu. Không suy nguyên nhân. |
| 4 | 04_Rating_Top12_NhanTheLoai_TheoN.png | 12 nhãn đông nhất theo N; mỗi nhãn có số Book Id riêng. Hợp 12 nhãn có 8.348 bản ghi, tạo 25.744 lượt thuộc nhãn. |
| 5 | 05_Rating_Top12_NhaXuatBan_TheoN.png | 12 publisher đông nhất theo N; giữ nhóm exact-case, không xếp toàn bộ publisher theo mean. |
| 6 | 06_BaoPhu_NgonNgu.png | 8.402 bản ghi; English 8.212, chiếm 97,74%; trục số lượng log10. |
| 7 | 07_Rating_NgonNgu_N30.png | Chỉ ba ngôn ngữ n≥30; N: English 8.212, spa 91, fre 48. |
| 8 | 08_Rating_VaN_TheoThapNien.png | 8.401 bản ghi có năm; chỉ vẽ mean nhóm n≥30. Không phải lịch sử Rating. |
| 9 | 09_CotChong100_Rating_TheoTheLoai.png | Mẫu số trong từng nhãn; bốn khoảng [1;3,5), [3,5;4), [4;4,5), [4,5;5]. Không cộng tỷ lệ giữa nhãn. |
| 10 | 10_Scatter_Rating_SoTrang.png | 8.385 cặp trang–Rating; giữ toàn bộ điểm, kể cả số trang ngoại lệ. |
| 11 | 11_Scatter_Rating_LuotCham.png | 8.402 cặp lượt chấm–Rating; ln(1+x), nhãn trục hiển thị số gốc. Spearman 0,066525. |
| 12 | 12_Scatter_Rating_NhanXet.png | 8.402 cặp review–Rating; ln(1+x) giữ review bằng 0. Spearman −0,018432. |
| 13 | 13_DoNhay_NguongLuotCham.png | Bốn ngưỡng 1/100/500/1.000 có N=11.046/8.402/6.153/5.114; không dùng một mẫu số chung. |

Bốn khoảng ở hình 9 là quy ước trình bày bổ sung của mục 6, dùng đồng nhất trong Python và Power BI. Các số đếm ba mức dưới 3,0 / 3,0–<4,0 / ≥4,0 ở phần mức nền vẫn là thống kê mô tả riêng, không phải chú giải của hình 9. Không sửa Rating, master hoặc kết quả EDA để tạo các khoảng mới.

Boxplot hiện có theo nhóm số trang. Không mô tả đã vẽ boxplot thể loại, publisher hoặc ngôn ngữ. Bảng Top N trên dashboard dùng Rating giảm dần, lượt chấm giảm dần, Book Id số tăng dần, khác Top 12 nhóm theo cỡ mẫu của các hình so sánh.

## Các nguồn kiểm chứng ưu tiên

1. `data/raw/source_metadata.json`, `data/reference/source_snapshot.json`: nguồn, thời điểm metadata, fingerprint.
2. `data/processed/books_cleaned_master.csv`: số liệu cấp bản ghi và các cờ phân tích.
3. `data/processed/book_genres_bridge.csv`: khóa thể loại đa nhãn.
4. `eda_tables/sample_flow.csv`, `descriptive_primary.csv`, `group_*`, `correlations_*`, `threshold_sensitivity.csv`, `pivot_n_decade_by_pages.csv`: mẫu số và kết quả.
5. `docs/phuong_phap_va_gioi_han.md`: giới hạn và quy tắc giảm lặp gần đúng.

Đã tái tính và so trực tiếp toàn bộ năm bảng groupby theo trang, publisher, ngôn ngữ, thập niên và thể loại: 0 sai khác ở N/mean/median/SD/Q1/Q3/trung vị lượt chấm, trong sai số làm tròn CSV 5,1×10⁻⁹. Đã kiểm tra N, Spearman và Pearson gốc của 16 dòng trong `correlations_by_threshold.csv`: 0 sai khác ngoài sai số trên. Các số bổ sung được đếm trực tiếp từ master/bridge; không sửa nguồn hoặc bảng EDA.
