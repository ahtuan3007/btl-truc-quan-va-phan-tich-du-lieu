# Đối chiếu độc lập yêu cầu gốc với sản phẩm

Rà soát 16/11/2026. Chỉ đọc đề, code, cấu trúc PBIX và tài liệu đã giao; không sửa nguồn hoặc sản phẩm. Không dùng số lượng kiểm tra DAX để thay chứng minh tuân thủ yêu cầu.

## Đúng bản đề bài

Đã đọc `D:/tmp/btl trực quan/01_DeBai/TrucQuanHoaDuLieu_HuongDan_BaiTapLon.docx` và so SHA-256 với bản `C:/Users/ASUS/Downloads/TrucQuanHoaDuLieu_HuongDan_BaiTapLon.docx`: cùng **52851d5647a468bddd3a5e657221f4ffd42da228ecffabfb8a550731dea9298c**.

Số đoạn dưới đây là vị trí 1-based của mọi `w:p` trong `word/document.xml`, gồm đoạn rỗng và ô bảng, với nội dung lấy từ `w:t`. Đây không phải số trang hoặc dòng Word.

## Kết luận quan trọng

Không thể chứng nhận **khớp tuyệt đối toàn văn đề bài**. Tệp gốc có hai lớp chỉ dẫn không nhất quán. Phần yêu cầu chung chấp nhận Streamlit/Power BI; phần hướng dẫn chi tiết theo mẫu bán lẻ viết riêng cho Python/Plotly/Streamlit và có các yêu cầu chưa hiện diện. Phương án Goodreads + Power BI là phạm vi đã chọn cùng người dùng, nhưng chưa thấy chứng cứ thầy chấp nhận việc ánh xạ toàn bộ mẫu bán lẻ sang đề tài Goodreads.

Người dùng đã loại slide và việc chuẩn bị nộp; đó là **thay đổi phạm vi người dùng**, không phải sửa được nguyên văn quy định của thầy. Không tự làm lại slide hoặc thêm Streamlit trái với phạm vi mới; cũng không viết rằng nguyên văn đề không yêu cầu chúng.

## Phần yêu cầu chung: đối chiếu chức năng

| Tiêu chí trong đề | Đoạn | Hiện trạng có bằng chứng | Kết luận có giới hạn |
|---|---:|---|---|
| Dashboard tương tác Streamlit / Power BI | 17; công cụ khuyến nghị 24–26 | PBIX thực có năm page; các visual native và slicer | Power BI có căn cứ rõ ở phần này |
| Mỗi sinh viên làm một trang | 19 | Có năm page; chưa thấy bảng tên thành viên–page trong tài liệu Markdown đã giao | Thiếu hồ sơ phân công; không được tự bịa tên |
| Mô tả nguồn, số dòng/cột, ý nghĩa, kiểu dữ liệu | 28–32 | Hai báo cáo mục 1–3/4–5, source metadata, từ điển và master hiện có | Có sản phẩm; kiểm số liệu là nhiệm vụ audit số liệu riêng |
| Kiểm thiếu/ngoại lệ, thống kê, lọc, groupby | 34–38 | `run_phase_4_5.py` có clean_books/describe/group_summary/run_pipeline; bảng sample_flow/descriptive/group_* | Có triển khai thực; không chỉ có lời mô tả |
| Pivot nếu phù hợp | 39 | Code pivot_table dòng 339,347; ba bảng pivot thập niên × trang | Có; tiêu chí có điều kiện, không bắt buộc tạo pivot vô nghĩa |
| So sánh bar/line | 43 | PBIX có clusteredBarChart và lineChart; ảnh Python so sánh nhóm | Có loại biểu đồ yêu cầu |
| Histogram/boxplot | 44 | Histogram trong PBIX; Python có cả histogram và boxplot nhóm trang | Có; đề dùng dấu /, không bắt buộc cả hai |
| Xu hướng thời gian | 45 | Line theo thập niên xuất bản | Có so sánh cohort theo thời gian; vì dữ liệu không có lịch sử Rating, phải giữ chú giải rằng đây không phải biến động Rating của một sách |
| Grouped/stacked | 46 | Clustered column và cột chồng 100% theo thể loại | Có; loại grouped/stacked yêu cầu chung không bắt buộc nội dung riêng do trợ lý tự đề xuất |
| Sidebar ≥2 điều kiện | 49 | Sáu slicer trái cho ngôn ngữ, trang, thập niên, genre, publisher, lượt chấm | Có hơn hai điều kiện; tính đúng số liệu cần audit riêng |
| Tabs hoặc Columns | 50 | Năm page/tab native Power BI và bố cục nhiều vùng | Đạt mục đích tổ chức theo phương án Power BI; không phải bằng chứng có st.tabs/st.columns |
| Visual cập nhật tương tác, rõ ràng | 51–52 | PBIX có slicer và visualInteractions; đã có ảnh năm trang | Có cấu hình; visual QA và UI độc lập cần đánh giá chất lượng thực |
| Phát hiện chính, so sánh/xu hướng | 54–55 | `INSIGHT_DA_DOI_CHIEU.md` có bảy yếu tố, phân biệt phổ biến và Rating, giới hạn | Có nội dung cụ thể, không chỉ tiêu đề |
| Gợi ý ra quyết định | 56 | Insight hiện chủ yếu là kết quả và cảnh báo; chưa có mục hành động cho người đọc/đơn vị giới thiệu sách | **Chưa hoàn thiện rõ**. Hướng dẫn viết mới yêu cầu người học viết đề xuất, chưa thay thế đề xuất thực tế |
| Source code trên GitHub | 59 | Có repository và commit trong README/progress | Có theo công việc trước; agent này không xác minh remote lần nữa |
| File ứng dụng và báo cáo | 60–61 | Có PBIX và các báo cáo từng phần; chưa có báo cáo tổng | PBIX có; báo cáo tổng đang để người dùng viết theo chỉ đạo mới nhất, không đánh dấu hoàn thành phần viết |

## Phần hướng dẫn chi tiết: những chỗ không thể gọi là khớp nguyên văn

| Chỉ dẫn chi tiết | Đoạn | So với Goodreads hiện tại | Đánh giá |
|---|---:|---|---|
| “Công cụ chính: Python (Pandas, Plotly) + Streamlit” | 82 | Code phân tích dùng Pandas/NumPy, ảnh dùng Matplotlib; không có import Plotly/Streamlit hoặc app Streamlit | **Chưa đáp ứng nguyên văn**; đồng thời xung đột lựa chọn Power BI được cho phép ở đoạn17/26 |
| Ứng dụng 05 page | 84 | PBIX có đúng năm page | Khớp số page |
| Slide dự án | 85;163–173 | Không làm theo chỉ đạo mới của người dùng | Ngoài phạm vi người dùng hiện tại, nhưng đề gốc vẫn ghi bắt buộc |
| Doanh nghiệp bán lẻ, doanh thu/khu vực/sản phẩm | 88–93 | Dữ liệu Goodreads không có doanh thu, đơn hàng, khu vực | Mẫu chưa được ánh xạ chính thức. Không được tạo KPI doanh thu/đơn hàng giả để lấp chỗ thiếu |
| Phân công SV1–SV5, mỗi người một page | 95–115 | Năm trang có tên chức năng; không có bảng người phụ trách đã xác thực | Thiếu bằng chứng tổ chức nhóm. Chỉ điền tên khi người dùng cung cấp |
| Page1 KPI doanh thu/đơn/sản phẩm và st.metric | 123–124 | N/mean/median là KPI phù hợp Goodreads nhưng không phải ba KPI bán lẻ; Power BI không dùng st.metric | Có lý do thích nghi theo đề tài, **không khớp nguyên văn** |
| Page2 line doanh thu, slider/date_input, Plotly | 132–135 | Line Rating theo thập niên nằm trang4; lọc thời gian là dropdown thập niên, không slider/date_input; không Plotly | Không khớp thư viện/control/vị trí/nội dung bán lẻ; tương đương một phần mục tiêu phân tích thời gian |
| Page3 bar theo khu vực, multiselect | 141–144 | So sánh genre/publisher/ngôn ngữ ở trang2; không có biến khu vực | Ánh xạ sang so sánh nhóm là quyết định đề tài, không phải dữ liệu khu vực thật |
| Page4 Top N sản phẩm và biểu đồ cột/ngang | 150–153 | Top N sách ở trang5 và hiện là **tableEx**, không có bar Top N sách | Nếu áp dụng mục tiêu Top N của mẫu này cho Goodreads, **thiếu biểu đồ Top N riêng**; các bar theo genre/publisher không thay thế xếp hạng sách |
| Page5 sidebar chứa toàn bộ bộ lọc | 159 | Sáu lọc chung ở x=24; `bookSearch` ở x=300,y=150 và `topN` ở x=1260,y=150 trên vùng chính | Không khớp chữ “toàn bộ”; hai control riêng trang5 nằm ngoài sidebar |
| Page5 Tabs hoặc Expander | 160 | Có native page tabs của toàn báo cáo; không có tabs/expander nội trang5 kiểu Streamlit | Không khớp kỹ thuật Streamlit nguyên văn; có tổ chức bằng page native |
| Cache tối ưu | 162 | Không có st.cache_data | **Khuyến khích**, không được coi thiếu bắt buộc; Power BI có cơ chế lưu model riêng, không nên gọi đó là đã viết st.cache |

## Các yêu cầu không tồn tại trong tệp này

- Không có chữ **Jupyter**, **Notebook**, **ipynb**. Sản phẩm hiện không có notebook nhưng đó **không phải lỗi tuân thủ** dựa vào bản đề này.
- Không có yêu cầu **ít nhất 5 insight**. Thầy yêu cầu phát hiện chính, so sánh/xu hướng, gợi ý ra quyết định; số lượng năm là điều kiện không có trong tệp.
- Không có số lượng **13 biểu đồ** bắt buộc. 13 là số sản phẩm trợ lý đã dựng để trả lời câu hỏi, không phải KPI để chứng minh đạt điểm.
- Dữ liệu Goodreads không nằm trong tám đề tài gợi ý cuối tệp. Đó là danh sách **gợi ý**, chưa đủ để kết luận đề tài tự chọn bị cấm hoặc đã được thầy duyệt.

## Câu nên sửa trong thông báo/tiến độ

1. “Mục 1–9 hoàn thành” chỉ có thể dùng với **kế hoạch Goodreads + Power BI đã chọn**, không đồng nghĩa hoàn thành mọi yêu cầu nguyên văn của thầy.
2. Mục9 chưa có gợi ý hành động cụ thể rõ trong bộ insight hiện tại. Nên bổ sung vài đề xuất được gắn với kết quả thật hoặc đánh dấu phần đề xuất còn chờ người viết.
3. Ghi riêng trạng thái **yêu cầu chung có bằng chứng**, **hướng dẫn mẫu bán lẻ chưa ánh xạ/không khớp nguyên văn**, **phạm vi đã loại theo người dùng**, **hồ sơ nhóm chưa có**.
4. Không lấy 9.173 kiểm tra số liệu để chứng nhận Plotly/Streamlit, phân công, đề xuất, báo cáo tổng hay chất lượng thẩm mỹ. Những trục này độc lập.

## Việc không nên tự làm

Không tự tạo số liệu doanh thu/khu vực, không tự thêm tên sinh viên, không dựng thêm Streamlit hoặc slide chỉ để làm hồ sơ trông đủ. Cần nói rõ mâu thuẫn nguồn và phạm vi, rồi để người dùng xác nhận với thầy phần công cụ/mẫu nếu muốn chứng nhận khớp toàn bộ đề.
