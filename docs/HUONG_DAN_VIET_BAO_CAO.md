# Hướng dẫn tự viết báo cáo Goodreads

Tài liệu này là khung viết và danh sách đối chiếu. Người học tự viết báo cáo hoàn chỉnh bằng lời của mình, lựa chọn ảnh từ dashboard cuối và diễn giải các kết quả đã kiểm chứng trong `INSIGHT_DA_DOI_CHIEU.md`. Không coi đây là một báo cáo hoàn chỉnh để nộp nguyên văn.

## Tên và câu hỏi nghiên cứu

Tên phù hợp: **Phân tích và trực quan hóa các yếu tố liên quan đến điểm đánh giá sách trong bộ dữ liệu Goodreads**. Nếu giữ từ “ảnh hưởng” trong tên đề tài đã đăng ký, giải thích ngay trong mục tiêu rằng thiết kế EDA này nhận diện mối liên hệ, chưa chứng minh nhân quả.

Đặt một câu hỏi riêng cho từng yếu tố: số trang, thể loại, ngôn ngữ, nhà xuất bản, năm xuất bản, lượt chấm và số review liên quan thế nào đến Rating. Câu hỏi chung bổ sung: sách phổ biến có đồng thời là sách có Rating cao nhất không?

## Dàn ý có thể dùng

| Phần | Nội dung người viết cần hoàn thiện | Tài liệu và bằng chứng để lấy |
| --- | --- | --- |
| 1 Bài toán và mục tiêu | Giới thiệu Goodreads, Rating, đối tượng sử dụng dashboard và bảy câu hỏi; giới hạn cấp bản ghi | Đề bài môn học; phần phạm vi trong insight |
| 2 Nguồn và mô tả dữ liệu | Nguồn Kaggle, bộ nền, 13 cột gốc, 11.127 bản ghi; ghi mốc metadata chính xác và phân biệt với thời điểm crawl | `02_Code_DuLieu_EDA/docs/nguon_du_lieu.md`, `source_metadata.json`, data dictionary |
| 3 Chất lượng và làm sạch | Thiếu trang/genre/publisher, ngày lỗi, count=0, nghi lặp ấn bản; giữ master, thêm cờ và cột chuẩn hóa; không tự xóa hàng loạt | Báo cáo các mục 1–5 đã có; `cleaning_summary.csv`, audit và nhật ký |
| 4 Phương pháp và mẫu phân tích | Master 11.127, eligible 11.046, primary 8.402; ngưỡng 100 lượt chấm; n≥30 khi trình bày nhóm; distinct book_id; không trọng số theo count | `sample_flow.csv`, `docs/phuong_phap_va_gioi_han.md` |
| 5 Thống kê và phân phối Rating | Mean, median, SD mẫu, Q1–Q3; histogram có khoảng bin rõ; phân biệt SD, IQR, khoảng tin cậy | `descriptive_primary.csv`, histogram và boxplot cuối |
| 6 Bảy hướng phân tích | Mỗi yếu tố một tiểu mục theo cấu trúc câu hỏi → biểu đồ → N → số liệu → nhận xét → giới hạn | Bảy mục trong insight, các bảng groupby/correlation |
| 7 Thiết kế và sử dụng dashboard | Mục tiêu mỗi page, lọc chung, tìm sách, Top N, ngưỡng lượt chấm, cách đọc N và trạng thái rỗng; chỉ nêu chức năng có thật ở bản cuối | Dashboard cuối và hướng dẫn kiểm thử; ảnh có bộ lọc rõ ràng |
| 8 Kiểm tra độ nhạy | Bốn ngưỡng lượt chấm, giới hạn trang, giảm lặp gần đúng; nêu kết luận nào ổn định trong đúng phạm vi đã thử | `threshold_sensitivity.csv`, `correlations_pages_sensitivity.csv`, `correlations_edition_sensitivity.csv` |
| 9 Kết luận và đề xuất | Trả lời bảy câu hỏi bằng kết quả mô tả; tách phổ biến với Rating; đề xuất dữ liệu/kiểm chứng tiếp | Insight đã đối chiếu; không tự thêm mô hình chưa chạy |
| 10 Giới hạn và tài liệu tham khảo | Chọn mẫu, snapshot cũ, đa nhãn, mất cân đối ngôn ngữ, ấn bản/tác phẩm, thiếu thiết kế nhân quả; trích nguồn dữ liệu và thư viện | Nguồn được lưu, phương pháp, fingerprint và code |

## Cách viết mỗi nhận xét

Mỗi đoạn nhận xét nên đủ bốn thông tin: **phạm vi mẫu và N; số quan sát được; ý nghĩa mô tả; giới hạn**. Có thể dùng công thức câu sau rồi thay bằng lời của mình:

> Trong [mẫu và bộ lọc], [chỉ số] của [nhóm/biến] là [giá trị], với [N]. Kết quả cho thấy [mô tả trong mẫu]. Do [giới hạn cụ thể], chưa thể kết luận [suy rộng/nhân quả chưa được hỗ trợ].

Với biểu đồ nhóm, ghi rõ Top N được chọn **theo số bản ghi** hay **theo Rating**. Top12 theo N không được đổi tên thành 12 nhóm có Rating cao nhất. Mean và median là hai chỉ số khác nhau; chọn đúng chỉ số của biểu đồ.

Với scatter, ghi biến X, Y, thang log hay log1p, N cặp đủ dữ liệu và tên hệ số. Spearman đo liên hệ thứ hạng; Pearson trên dữ liệu gốc và Pearson sau log1p không thay thế nhau. Hệ số 0,126 không có nghĩa giải thích 12,6% Rating.

Với thời gian, dùng “Rating của các nhóm bản ghi xuất bản ở những thập niên khác nhau”. Chỉ có một snapshot Rating nên không mô tả sự tăng/giảm Rating của cùng sách theo thời gian.

## Chọn hình và bảng

- Dùng hình cuối cùng, đủ tên trục, đơn vị, chú thích, N và trạng thái bộ lọc; không dùng ảnh cũ còn thiếu nội dung để minh họa chức năng mới.
- Mỗi hình gắn với một câu hỏi và một nhận xét cụ thể trong bảng ánh xạ của insight. Không thêm nhiều hình lặp cùng thông tin chỉ để tăng số lượng.
- Với thể loại, lưu ý bridge nhiều nhãn: N là số bản ghi trong từng nhãn, các nhóm chồng lấn. Stacked 100% phải dùng mẫu số trong từng nhãn, không cộng phần trăm giữa nhãn.
- Với publisher, giữ nguyên khóa nhóm phân biệt hoa/thường theo EDA; kiểm tra biểu đồ cuối không vô tình gộp nhãn. Không tự chuẩn hóa lại dữ liệu gốc chỉ để khớp hình.
- Q1–Q3 có thể mô tả bằng boxplot; chưa có khoảng tin cậy/kiểm định nên không gắn nhãn “khác biệt có ý nghĩa thống kê”.

## Những câu cần tránh

| Tránh viết | Viết đúng phạm vi |
| --- | --- |
| Sách càng dài càng hay | Liên hệ trang–Rating tổng thể nhỏ; mean của các nhóm trang không tăng đơn điệu |
| Nhà xuất bản/thể loại này làm điểm cao hơn | Nhóm này có mean quan sát cao hơn trong mẫu và điều kiện đã nêu |
| Sách mới có điểm giảm dần theo thời gian | Các nhóm năm xuất bản có khác biệt Rating tại snapshot; chưa có lịch sử Rating |
| Review nhiều khiến điểm tăng/giảm | Các hệ số tổng thể gần 0 và đổi dấu theo phép đo/ngưỡng đã thử |
| Tổng lượt chấm là số độc giả hoặc doanh số | Đây là lượt chấm gắn với bản ghi nguồn, có giới hạn cấp ấn bản/tác phẩm |
| N lớn chứng minh đại diện toàn Goodreads | Cơ chế chọn mẫu chưa đủ rõ để suy rộng toàn nền tảng |
| Thể loại chiếm tỷ trọng tổng sách bằng tổng số nhóm | Một bản ghi có thể thuộc nhiều thể loại; công bố mẫu số riêng |

## Đối chiếu trước khi hoàn tất phần viết

1. Mốc nguồn đúng: bộ nền metadata 09/03/2020, bộ genre 30/12/2022; không gọi là dữ liệu Goodreads hiện tại.
2. Các hình dùng cùng mẫu với số liệu đang dẫn. 8.402 là mẫu mặc định, không áp dụng máy móc cho ảnh đã lọc hoặc phân tích cần thêm trường hợp lệ.
3. N trang 8.385, năm 8.401, publisher 8.399, có genre 8.400; không giấu mẫu thiếu khi từng phép tính dùng N khác nhau.
4. Mean mặc định 3,954683, median 3,97, SD mẫu 0,265769. Khi lọc lại, lấy số từ dashboard và bảng tương ứng thay vì chép mức mặc định.
5. Mỗi nhận xét chỉ dựa trên biểu đồ và bảng có thật; không tuyên bố kiểm định, hồi quy hay kết luận nhân quả chưa thực hiện.
6. Nêu kiểm tra độ nhạy cùng giới hạn, giữ raw/master và nhật ký. Nếu có thay đổi phương pháp phải ghi rõ và chạy lại đối chiếu, không âm thầm thay bộ số.
7. Bổ sung mục tiêu từng page và cách thao tác từ bản dashboard cuối sau nghiệm thu; không tự đánh dấu hoàn thành chỉ vì đã có khung báo cáo.

Tài liệu này không yêu cầu làm slide, gói nộp hay tạo thêm ứng dụng khác. Phạm vi hiện tại là hoàn thiện dashboard và cung cấp căn cứ để người học tự viết báo cáo.

## Cần chốt trước khi gọi là đáp ứng toàn bộ đề

Đọc REVIEW_RASOAT_CUOI.md: đề chung chấp nhận Power BI nhưng phần mẫu dùng
Plotly/Streamlit. Ghi đúng công cụ thực đã dùng; không viết đã có app Streamlit.
Phân công thành viên phải lấy tên và trách nhiệm thực. Slide không làm theo phạm vi
người dùng hiện tại, không có nghĩa bản yêu cầu gốc đã bỏ slide. Phần gợi ý ra quyết
định nay có căn cứ trong insight; có thể dùng làm đầu vào rồi viết lại bằng lời của mình.
