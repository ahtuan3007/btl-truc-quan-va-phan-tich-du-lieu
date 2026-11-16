# Hướng dẫn sử dụng dashboard Goodreads

Mở Goodreads_Dashboard_DaKiemTra.pbix trong thư mục 04_PowerBI_BanChinh bằng Power BI Desktop. File chứa snapshot dữ liệu đã kiểm tra, có thể mở và refresh mà không cần đường dẫn trên máy người dựng.

## Trạng thái mặc định

Mẫu chính có 8.402 bản ghi: Rating từ 1 đến 5 và ít nhất 100 lượt chấm. Rating trung bình là 3,954683, trung vị 3,97. Một bản ghi gắn với Book Id/ấn bản; chưa được xác minh là một tác phẩm độc lập.

Các bộ lọc danh mục ở All, khoảng lượt chấm từ 100 đến mức lớn nhất của mẫu. Trang tra cứu mở với Top 10; ô tìm tên chưa chọn sách.

## Năm trang

| Trang | Cách đọc |
|---|---|
| Tổng quan | Ba KPI chung, thiếu dữ liệu trong bộ lọc, histogram Rating và tỷ lệ bốn mức Rating trong 12 thể loại đông nhất |
| So sánh nhóm sách | Rating theo thể loại, nhà xuất bản, ngôn ngữ và nhóm số trang; chỉ hiện nhóm N ≥ 30 |
| Quan hệ với Rating | Ba scatter theo Book Id với số trang, lượt chấm và review; N theo cặp nằm dưới biểu đồ |
| Theo năm xuất bản | Rating và số bản ghi theo thập niên, cùng cơ cấu nhóm trang; đây là nhóm năm trên bản ghi/ấn bản |
| Tra cứu và Top N | Tìm tên sách, chọn số dòng Top N và xem xếp hạng trong tập ứng viên sau lọc |

## Lọc dữ liệu

Sáu bộ lọc ở cột trái được đồng bộ giữa năm trang: ngôn ngữ, nhóm trang, thập niên, thể loại, nhà xuất bản và khoảng lượt chấm.

1. Mở danh sách và chọn giá trị; với danh sách dài có thể gõ vào Search rồi đánh dấu kết quả.
2. Các lựa chọn trong cùng một danh mục được hiểu là OR. Các bộ lọc khác nhau được kết hợp bằng AND.
3. Chọn nhiều thể loại lấy hợp các Book Id thuộc các nhãn đó. Sách xuất hiện trong hai nhãn chỉ được tính một lần trong N của tập đang xem.
4. Bộ lọc lượt chấm có hai đầu mút chỉnh được. Mẫu chính vẫn luôn yêu cầu ít nhất 100; đặt thấp hơn không đưa sách ngoài mẫu chính vào phân tích.
5. Để bỏ lựa chọn, đưa chuột lên bộ lọc và bấm biểu tượng tẩy Clear selections. Có thể bỏ từng dấu chọn. Xóa chữ Search chỉ đổi danh sách gợi ý, chưa tự xóa lựa chọn đã đánh dấu.

Các danh sách danh mục được giữ độc lập để có thể chọn tổ hợp không có sách. Khi giao các bộ lọc rỗng, N bằng 0, Rating để trống và dashboard hiện thông báo. Nếu còn dữ liệu nhưng không nhóm nào đạt 30 bản ghi, trang so sánh không vẽ trung bình của nhóm nhỏ; đây là trường hợp khác với mất hết dữ liệu.

N ở dòng trạng thái là số bản ghi đang được phân tích. Di chuột lên cột để đọc cỡ mẫu trong tooltip. Top 12 thể loại/nhà xuất bản được chọn theo N sau lọc, không phải 12 nhóm có Rating cao nhất.

## Tìm tên và xếp hạng

Trên trang Tra cứu và Top N:

1. Mở danh sách Tìm tên sách, gõ từ khóa vào Search, sau đó đánh dấu một hoặc nhiều sách tìm được.
2. Chọn Top 5, 10, 20, 50 hoặc 100. Khi không chọn một giá trị Top N, mặc định là 10.
3. Thứ tự là Rating giảm dần, lượt chấm giảm dần, rồi Book Id dạng số tăng dần. Tie-break này bảo đảm không trả dư dòng do bằng điểm.
4. Dòng trạng thái phân biệt số ứng viên sau lọc với số dòng Top N đang hiện. Nếu có ba ứng viên và chọn Top 10, bảng chỉ có ba dòng.
5. Lọc tên và Top N chỉ dùng cho trang tra cứu. Sáu bộ lọc cột trái vẫn dùng chung cho cả năm trang.

Tên sách kèm ID giúp phân biệt bản ghi và giữ đúng chữ hoa/thường. Không cộng lượt chấm giữa các ấn bản để suy ra số độc giả duy nhất. Danh sách này xếp hạng bản ghi trong snapshot và bộ lọc, chưa phải bảng các tác phẩm tốt nhất của toàn Goodreads.

## Các quy ước cần biết

- Thể loại đa nhãn: không cộng các thanh thành tổng sách. Tỷ lệ Rating tính riêng trong từng thể loại.
- Bốn khoảng ở biểu đồ tỷ lệ là [1;3,5), [3,5;4), [4;4,5) và [4,5;5]. Đây là cách phân khoảng để vẽ mới, không sửa Rating hoặc thay các kết quả EDA.
- Histogram dùng khoảng rộng 0,1 điểm, với quy tắc thập phân thống nhất giữa Python và Power BI; bản ghi đúng ranh giới thuộc khoảng bắt đầu ở ranh giới đó.
- Nhãn có mã G/P trong ngoặc vuông phân biệt các tên nguồn chỉ khác chữ hoa/thường. Khóa số bảo toàn các nhóm theo EDA; không tự hợp nhất publisher hoặc genre.
- Scatter lượt chấm/review dùng ln(1+x), nên giữ được review bằng 0. Power BI có thể lấy mẫu khi hiển thị scatter; ba ảnh scatter Python dùng toàn bộ các cặp dữ liệu hợp lệ.
- Năm trên bản ghi không nhất thiết là năm xuất bản đầu tiên. Đường theo thập niên không phải lịch sử Rating của cùng một sách.

## Lấy hình và số liệu để viết báo cáo

Dùng 13 ảnh trong BieuDo_BaoCao và chú thích đi kèm. Ảnh cả năm trang trong Anh_Dashboard minh họa sản phẩm tương tác. Các hình Python mặc định dùng mẫu chính, trừ hình 13 đối chiếu bốn ngưỡng lượt chấm có mẫu số riêng.

Khi dùng ảnh sau lọc, ghi rõ bộ lọc và N đang hiện. Không chép số mặc định để giải thích một ảnh đã lọc khác. Insight đã đối chiếu và hướng dẫn viết nằm trong 03_BaoCao_DaCo.

## Chạy lại biểu đồ Python

Trong thư mục 02_Code_DuLieu_EDA:

    python -m pip install -r requirements.txt -r requirements_charts.txt
    python run_charts.py

Script kiểm tra fingerprint của raw, master và bridge trước khi vẽ. Ảnh ghi vào 04_PowerBI_BanChinh/BieuDo_BaoCao; manifest và bảng tham chiếu ghi vào work/charts_stage6. Không chạy lại làm sạch chỉ để tạo ảnh.

Trong PBIX, SourceFile mặc định rỗng để dùng snapshot đã nhúng. Chỉ đổi nguồn sau khi rà soát lại toàn bộ quy tắc và đối chiếu; không trỏ sang một CSV Goodreads khác rồi coi kết quả vẫn là bộ đã kiểm tra.
