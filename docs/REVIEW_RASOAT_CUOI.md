# Review số liệu cách tính trình bày và yêu cầu đề bài

Rà soát độc lập ngày 16/11/2026, sau khi người dùng yêu cầu kiểm lại và sửa nốt.
Không có cơ sở gọi sản phẩm “hoàn hảo” hoặc cam kết điểm 10/10. Chưa phát hiện số
liệu phân tích bị bịa trong phạm vi đã đối chiếu; có thiếu sót thật ở cách trình bày
và cách báo tiến độ, đã sửa như dưới đây.

## Kết quả đối chiếu

| Nội dung | Bằng chứng và kết luận |
|---|---|
| Mẫu phân tích | Tính lại từ 13 cột raw, không gọi lại hàm clean_books: master 11.127, mẫu chính 8.402; mean 3,9546834087122114, median 3,97, SD mẫu 0,2657690491044255. |
| Cách tính | Mean/median giữa các Book Id, không trọng số theo lượt chấm. Số cặp thiếu biến được loại riêng từng phép tính. N theo genre dùng Book Id duy nhất; OR khi chọn nhiều nhãn. |
| Bảng EDA | Tái tính độc lập năm bảng groupby và 16 dòng tương quan ở bốn ngưỡng; không thấy sai ngoài làm tròn CSV. Không sửa bảng EDA để làm khớp kiểm tra. |
| Bốn khoảng Rating | Đã so riêng từng dòng n/share và tập khóa của 1.888 dòng genre×bin, không chỉ so tổng theo nhãn. Không có sai khác. |
| Model nguồn | Đọc trực tiếp toàn bộ 11.127 bản ghi và 94.794 cặp bridge; đối chiếu từng trường số, cờ mẫu và khóa publisher, không chỉ so mean toàn bảng. |
| Top N và chọn nhóm | Kiểm thêm 36 truy vấn: Top12 genre/publisher và cột chồng ở mười ngữ cảnh lọc; Top50/100 ở toàn mẫu, hợp genre và ngưỡng500. Không có sai khác sau khi phân biệt ô count=0 với ô bị pandas bỏ vì rỗng. |
| Giao diện | Thử thật Top50 và Top100, kéo đến dòng cuối 50/100; chọn Fiction + Fantasy cho N=5.871 và đồng bộ Tổng quan, mean hiển thị3,930, median3,94; bỏ lọc trả về8.402. Đây là quan sát UI, không phải test tự động. |
| Trình bày | Đã đổi tiêu đề bảng thành Hạng/Tên sách và ID/Rating/Lượt chấm/Review/Số trang/Năm; trục scatter là Số trang/ln(1+lượt chấm)/ln(1+review) và Rating. Chỉ đổi displayName, không đổi DAX, field, sort hoặc bộ lọc. |
| Ảnh | Xuất lại năm trang. Trang3 và5 đã kiểm ảnh đầy đủ; trang1/2/4 giống từng pixel với ảnh đã duyệt trước đó. 13 hình Python riêng không thay đổi. |
| Insight | Đã bổ sung phần gợi ý ra quyết định cho người đọc/đơn vị giới thiệu sách, gắn với kết quả thật, không suy nhân quả hoặc doanh số. |

Power BI có cơ chế lưu chuỗi không phân biệt hoa/thường: các cột text cũ có thể
hiển thị một cách viết chung cho các chuỗi chỉ khác case. Vì vậy, không dùng cột
publisher text cũ để tạo nhóm; dùng dimension có khóa số và nhãn G/P. Tên sách để
tra cứu dùng tên kèm ID duy nhất. Raw/master trên đĩa không bị thay. Hồ sơ kiểm
từng dòng và nhãn hiển thị được lưu riêng, không gọi mọi chuỗi text cũ là bản sao
đúng chữ hoa/thường tuyệt đối.

## Con số 9.173 thực sự có nghĩa gì

Đây là số phép so sánh giá trị hoặc danh sách do validator đếm, không phải 9.173
thí nghiệm độc lập, chức năng ứng dụng hoặc chứng chỉ đáp ứng đề bài.

| Nhóm kiểm tra cũ | Số phép so sánh |
|---|---:|
| 56 trạng thái thống kê | 504 |
| 20 trường hợp danh sách xếp hạng | 40 |
| Khóa/N/mean/median của nhóm genre và publisher | 6.998 |
| Tổng N và tổng share theo genre | 1.586 |
| Các số đếm nguồn | 5 |
| Khoảng histogram | 40 |
| Tổng | 9.173 |

Nhánh bin cũ chưa kiểm riêng từng ô; lần rà soát này đã bổ sung cách tính độc lập.
Nhật ký UI13 trước đó chỉ bao phủ những thao tác đã ghi, không chứng minh mọi tổ
hợp lọc. Các kiểm tra mới khép thêm khoảng trống, vẫn không bảo đảm tuyệt đối mọi
tình huống hoặc chất lượng dữ liệu ngoài snapshot.

## Yêu cầu nào khớp và chỗ nào chưa thể chứng nhận

Đúng bản đề đã gửi: bản trong folder bài và Downloads cùng SHA-256
52851d5647a468bddd3a5e657221f4ffd42da228ecffabfb8a550731dea9298c.

- Phần yêu cầu chung cho phép dashboard “Streamlit / Power BI”; có mô tả dữ liệu,
  EDA bằng code, groupby/pivot, bốn nhóm biểu đồ, ít nhất hai bộ lọc và insight.
  Bộ Goodreads hiện có bằng chứng cho các nội dung chung này.
- Phần hướng dẫn chi tiết phía sau viết cho ví dụ bán lẻ và Python/Plotly/Streamlit,
  st.metric, slider/date_input, Tabs/Expander. Bài hiện dùng Pandas/Matplotlib và
  Power BI, không có app Streamlit hoặc code Plotly; không gọi đó là khớp nguyên văn.
- So với mẫu chi tiết, Top N sách là bảng thay vì bar Top N; tìm tên và Top N nằm
  ở vùng chính trang5, trong khi câu của mẫu ghi toàn bộ lọc ở sidebar. Đây là
  khác biệt đã công bố, không tự thêm chỉ số doanh thu/khu vực hoặc dữ liệu giả để lấp.
- Chưa có tên người phụ trách từng page. Đã có bảng chờ điền trong tiến độ; không
  tự ghi tên hoặc nhận là đã phân công đủ sinh viên.
- Báo cáo tổng do người học viết theo chỉ đạo hiện tại. Slide và chuẩn bị nộp đã
  bị loại khỏi phạm vi người dùng; nguyên văn đề vẫn nhắc slide, không xóa sự thật đó.

Vì tệp yêu cầu có hai lớp không nhất quán, muốn kết luận đáp ứng toàn bộ quy định
của thầy cần xác nhận thầy áp dụng phần chung cho Power BI hay bắt buộc phần mẫu
Streamlit. Chưa có xác nhận đó trong hồ sơ; trợ lý không thể tự phê duyệt thay thầy.

Đề này không yêu cầu Jupyter Notebook, ít nhất5 insight hoặc đúng13 biểu đồ.
Không tự tạo các tiêu chí đó để báo thiếu, cũng không dùng số lượng hình làm bằng
chứng đạt chất lượng.

## Bằng chứng để kiểm tra lại

- Sản phẩm: PBIX hiện dùng trong bộ bài tập cục bộ; không upload vào repository.
- Số liệu/kiểm tra: ../02_Code_DuLieu_EDA/work/powerbi_final/reaudit/.
- Đối chiếu yêu cầu chi tiết nằm trong cùng thư mục bằng chứng, kèm số đoạn XML
  có định nghĩa rõ; đó không phải số trang Word.
- [Insight đã bổ sung đề xuất](INSIGHT_DA_DOI_CHIEU.md),
  [tiến độ đã đính chính](TIEN_DO.md), [hướng dẫn viết](HUONG_DAN_VIET_BAO_CAO.md).
