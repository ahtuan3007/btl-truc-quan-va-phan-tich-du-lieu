# Model và quy tắc của dashboard cuối

## Nguồn và cấp dữ liệu

Master giữ nguyên 11.127 Book Id; bridge gốc giữ 94.794 cặp. PBIX nhúng snapshot,
SourceFile rỗng. Mẫu phân tích mặc định là Rating 1–5 và n_ratings ≥ 100: N=8.402.
Không xóa bản ghi thiếu genre/publisher khỏi KPI tổng. Mean/median không trọng số.

## Quan hệ

| Bảng một | Bảng nhiều | Hướng lọc |
|---|---|---|
| Sách[Mã sách] | Gán thể loại[Mã sách] | Hai chiều, phục vụ lọc hợp nhiều thể loại |
| Thể loại[Khóa] | Gán thể loại[Khóa thể loại] | Một chiều từ danh mục |
| Nhà xuất bản[Khóa] | Sách[Khóa nhà xuất bản] | Một chiều từ danh mục |

Danh mục thể loại có 890 khóa; publisher có 2.283 khóa, gồm khóa thiếu 0.
Khóa số và nhãn hiển thị riêng giữ các nhóm nguồn khác hoa/thường. Sáu nhãn genre
trong ba cặp và 55 nhãn publisher trong 27 nhóm có hậu tố G/P để Power BI không gộp.
Đối chiếu nhóm bằng khóa số với EDA, không bằng text đã bị collation gộp.

Đếm sách bằng DISTINCTCOUNT Book Id; tổng nhóm đa nhãn không phải tổng sách.
Chọn nhiều genre là OR/hợp, kết hợp các loại bộ lọc là AND. Top 12 nhóm chọn theo N
sau lọc, chỉ vẽ mean nhóm N≥30; hòa N dùng nhãn nguồn thứ tự tăng dần theo mã ký tự.

## Chỉ số và xếp hạng

Sáu slicer chung đồng bộ năm trang. Danh sách slicer không lọc lẫn nhau, để người
dùng có thể chọn tổ hợp rỗng; chúng lọc toàn bộ visual phân tích. Khi rỗng, N=0,
mean/median trống và có thông báo. Ba KPI chung chỉ ở Tổng quan.

Top N là bảng rời 5/10/20/50/100, mặc định 10. Candidate lấy sau lọc và lựa chọn
tên sách. Xếp Rating giảm, lượt chấm giảm, Book Id số tăng. Measure candidate
tái áp dụng hợp khóa genre khi dùng ALLSELECTED, tránh mất lọc qua bridge.
Tên tìm kiếm kèm ID phân biệt bản ghi trùng tên; gõ Search chưa tự chọn bản ghi.

Scatter có category Book Id, X/Y lấy MAX ở đúng một bản ghi; lượt chấm/review dùng
ln(1+x). Power BI có thể giảm số điểm khi render; ba scatter Python dùng toàn bộ
cặp hợp lệ: 8.385 / 8.402 / 8.402. Không dùng số điểm nhìn thấy để suy N.

Histogram khoảng 0,1 điểm dùng ranh giới thập phân: rating quy về phần trăm điểm
nguyên trước khi chia bin ở Python, khớp toàn bộ 40 khoảng với model. Bốn mức
ở cột chồng là [1;3,5),[3,5;4),[4;4,5),[4,5;5], là quy ước trực quan bổ sung,
không thay ba mức mô tả cũ trong EDA. Tỷ lệ dùng mẫu số trong từng thể loại.

## Bằng chứng

`../work/powerbi_final/` có DAX, ánh xạ khóa, kết quả thực và kỳ vọng.
9.173 phép đối chiếu gồm toàn bộ nhóm genre/publisher trong mẫu chính,
ngưỡng/cỡ mẫu/mean/median, hợp genre, nhãn khác hoa/thường, trạng thái rỗng,
Top N và histogram. Sai số tuyệt đối lớn nhất 4,67e-14, dưới dung sai 1e-10.
Các file nguồn, master, bridge, code làm sạch và bảng EDA cũ không đổi byte.
