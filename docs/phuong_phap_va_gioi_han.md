# Phương pháp phân tích và giới hạn kết quả

Phần kiểm tra độ nhạy và giới hạn là một phần của phương pháp nghiên cứu: nó giúp đánh giá kết luận có thay đổi khi đổi điều kiện phân tích hay không. Kết quả ổn định với các quy tắc đã thử chưa có nghĩa dữ liệu đại diện toàn Goodreads hoặc chứng minh quan hệ nhân quả.

## Đơn vị quan sát và phạm vi

Một dòng là bản ghi Goodreads theo `Book Id`, gắn với thông tin ISBN/ấn bản. Có 263 nhóm tên sách–chuỗi tác giả trùng chính xác, với 574 dòng; các nhóm này có Rating giống nhau nhưng số lượt chấm khác nhau. Đây là bằng chứng nội bộ gợi ý các trường có thể khác cấp tác phẩm/ấn bản, chưa phải xác nhận chính thức từ nguồn.

Không gộp theo tên sách hoặc cộng lượt chấm giữa các dòng. Kết quả là thống kê theo bản ghi; chưa thể gọi mỗi dòng là một tác phẩm độc lập hoặc tổng lượt chấm là số người đọc duy nhất.

## Tập dữ liệu dùng cho từng phép tính

| Phạm vi | Số bản ghi |
| --- | ---: |
| Master bảo toàn nguồn | 11.127 |
| Rating từ 1 đến 5 và lượt chấm dương | 11.046 |
| Mẫu chính có ít nhất 100 lượt chấm | 8.402 |
| Mẫu chính có số trang dương | 8.385 |
| Mẫu chính có ngày hợp lệ | 8.401 |
| Đối chiếu giảm lặp gần đúng | 8.189 |

N trong thống kê nhóm là số `Book Id` duy nhất. Quy ước n≥30 giúp tránh diễn giải các nhóm rất nhỏ; đó không phải bảo đảm độ chính xác. Q1–Q3 là khoảng giữa của phân phối, không phải khoảng tin cậy.

## Các kiểm tra độ nhạy đã làm

**Ngưỡng lượt chấm.** Đối chiếu mốc 1, 100, 500 và 1.000, tương ứng 11.046, 8.402, 6.153 và 5.114 dòng. Rating trung bình tăng từ 3,943 lên 3,964; thay đổi khoảng 0,021 điểm. Chưa loại vĩnh viễn các bản ghi dưới một ngưỡng.

**Bản ghi nghi cùng tác phẩm.** Tạo riêng mẫu một dòng/cặp tên–chuỗi người đóng góp đã chuẩn hóa; ưu tiên count lớn nhất, hòa thì Book Id số nhỏ nhất. Đây là giảm lặp gần đúng, có thể bỏ sót bản dịch khác tên hoặc chuỗi người đóng góp khác. Chọn ấn bản phổ biến nhất cũng có thiên lệch riêng. Mẫu này không thay thế master.

**Số trang ngoại lệ.** Tạm giới hạn 20–2.000 trang khi đối chiếu, còn 8.300 dòng. Spearman số trang–Rating khoảng 0,129 so với 0,126 ở mẫu chính. Không dùng phép thử này làm lý do xóa sách mỏng hoặc tuyển tập.

**Phân tầng.** Tính tương quan trong sáu nhãn có nhiều bản ghi và nhóm English. Một số tương quan trong nhóm cao hơn tổng thể, ví dụ số trang trong Literature khoảng 0,264, Novels khoảng 0,280. Các nhóm thể loại chồng lấn và chưa đồng thời kiểm soát mọi biến.

**Pivot.** Xuất cả trung bình và số đếm theo thập niên × khoảng trang; có bản ẩn trung bình khi n<30. Không điền Rating 0 cho ô thiếu. Nhóm 2010–2019 có 100 bản ghi với ngày hợp lệ, nhưng còn 99 khi pivot yêu cầu thêm số trang hợp lệ.

## Những kết luận phù hợp với dữ liệu

- Các tương quan **tổng thể** của bốn biến số đã khảo sát với Rating trong mẫu chính đều nhỏ. Điều này không khẳng định mọi tương quan có điều kiện đều nhỏ hoặc các yếu tố không liên quan ở quần thể rộng hơn.
- Review gần như không có quan hệ đơn điệu tổng thể với Rating trong các phạm vi đã thử. Dấu hệ số đổi nhẹ theo ngưỡng/phép đo, nên không kết luận review làm tăng hoặc giảm Rating.
- Nhóm 601+ trang có trung bình 4,119; nhóm 201–400 trang 3,912. Tuy nhiên nhóm 1–200 trang 3,953 cao hơn nhóm 201–400, nên không nói “càng dài càng được đánh giá cao”.
- Kết quả tương quan thay đổi nhỏ khi giảm lặp gần đúng. Chỉ kết luận ổn định với quy tắc đối chiếu đã thử; chưa xử lý hết phụ thuộc giữa ấn bản, series hoặc tác giả.

## Giới hạn phải giữ trong báo cáo chính

1. Phương pháp chọn sách của nguồn chưa đủ rõ để chứng minh mẫu đại diện toàn Goodreads.
2. Ngày xuất bản là ngày ghi trên bản ghi/ấn bản; không có lịch sử Rating theo thời gian hoặc ngày xuất bản đầu tiên đã xác minh.
3. Nguồn metadata và thời điểm bổ sung thể loại khác nhau. Không mô tả đây là Goodreads hiện tại.
4. English chiếm 97,74% mẫu chính, khiến so sánh ngôn ngữ rất mất cân đối.
5. Thể loại đa nhãn và các nhóm publisher có cơ cấu tác phẩm khác nhau; thứ tự trung bình không đo được chất lượng hoặc tác động của nhóm.
6. Chưa có thiết kế nhân quả, định danh tác phẩm đầy đủ hoặc dữ liệu độc giả độc lập. Không dùng từ “ảnh hưởng” như bằng chứng nguyên nhân.

Vì vậy, phần kết quả phù hợp cho một bài EDA và trực quan hóa dữ liệu khi luôn ghi rõ mẫu số, quy ước, số quan sát và giới hạn đi kèm. Chưa phải kết luận nhân quả hoặc mô hình dự đoán Rating đã được đánh giá.
