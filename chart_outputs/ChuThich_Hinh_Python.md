# Chú thích hình cho phần trực quan hóa

Tất cả hình dùng mẫu chính Rating 1–5 và n_ratings ≥ 100, trừ hình 13 đối chiếu ngưỡng. n trong so sánh nhóm là số Book Id duy nhất. Các hình tĩnh được dựng bằng Python từ dữ liệu đã kiểm tra.

## Hình 1 Phân phối Rating trong mẫu phân tích chính

File: `01_PhanPhoi_Rating_MauChinh.png`

8.402 bản ghi · Rating 1–5 · ít nhất 100 lượt chấm

Mẫu chính có trung bình 3,955, trung vị 3,97; các khoảng [x;x+0,1) dùng quy tắc thập phân khớp Power BI.

## Hình 2 Phân phối Rating theo nhóm số trang

File: `02_Boxplot_Rating_NhomSoTrang.png`

8.385 bản ghi có số trang dương · 17 bản ghi thiếu số trang không dùng trong hình

Các phân phối Rating chồng lấn. Chênh lệch nhóm độ dài chưa chứng minh thêm số trang sẽ làm Rating tăng.

## Hình 3 Rating trung bình theo nhóm số trang

File: `03_TrungBinh_Rating_NhomSoTrang.png`

Mẫu chính có số trang dương · bốn nhóm đều có ít nhất 30 bản ghi

Nhóm 601+ trang: 4,119; nhóm 201–400: 3,912. Nhóm 1–200 cao hơn 201–400 nên không có xu hướng tăng đều. Đường đứt: trung bình 8.402 bản ghi; không phải mô hình nhân quả.

## Hình 4 Rating của 12 nhãn thể loại có nhiều bản ghi nhất

File: `04_Rating_Top12_NhanTheLoai_TheoN.png`

Chọn và sắp xếp theo n giảm dần; hòa n thì theo nhãn gốc · chỉ nhóm n ≥ 30

Trong các nhóm hiển thị, History có trung bình 4,021 (n=1.260); Novels có trung bình 3,872 (n=2.191). Một sách thuộc nhiều nhãn; tổng n giữa các nhóm không cộng thành số sách duy nhất. Giữ nguyên nhãn và chữ hoa/thường; dấu phẩy bên trong nhãn không bị tách.

## Hình 5 Rating của 12 nhà xuất bản có nhiều bản ghi nhất

File: `05_Rating_Top12_NhaXuatBan_TheoN.png`

Chọn và sắp xếp theo n giảm dần; hòa n thì theo tên gốc · chỉ nhóm n ≥ 30

Trong các nhóm hiển thị, VIZ Media LLC có trung bình 4,248 (n=86); Ballantine Books có trung bình 3,878 (n=134). Giữ tên sau chuẩn hóa khoảng trắng; không gộp theo chữ thường hoặc gộp các imprint. Khác biệt có thể phản ánh cơ cấu tác phẩm; chưa đo tác động của nhà xuất bản.

## Hình 6 Mức độ bao phủ ngôn ngữ trong mẫu chính

File: `06_BaoPhu_NgonNgu.png`

English: 8.212 / 8.402 bản ghi (97,74%)

So sánh ngôn ngữ mất cân đối mạnh: English chiếm 97,74% mẫu chính; không suy rộng các nhóm nhỏ.

## Hình 7 Rating theo ngôn ngữ có đủ số bản ghi

File: `07_Rating_NgonNgu_N30.png`

Chỉ nhóm n ≥ 30 · sắp xếp theo số bản ghi, không theo Rating

Trong các nhóm hiển thị, spa có trung bình 3,969 (n=91); fre có trung bình 3,950 (n=48). English chiếm phần lớn mẫu. Mỗi nhóm có cơ cấu sách và ấn bản khác nhau. Không kết luận ngôn ngữ gây ra chênh lệch Rating; các mã nhỏ không bị xóa khỏi master.

## Hình 8 Rating theo thập niên xuất bản của bản ghi

File: `08_Rating_VaN_TheoThapNien.png`

8.401 bản ghi có ngày hợp lệ · chỉ vẽ Rating trung bình khi nhóm có n ≥ 30

Các nhóm năm khác nhau có cỡ mẫu rất khác nhau; thập niên 2000 chiếm 5.833 bản ghi. Trung bình của nhóm n<30 không được vẽ.

## Hình 9 Cơ cấu mức Rating trong 12 nhãn thể loại phổ biến

File: `09_CotChong100_Rating_TheoTheLoai.png`

12 nhãn phổ biến theo n · cột chồng 100% tính riêng trong từng nhãn

Các mức Rating dùng khoảng [1;3,5), [3,5;4), [4;4,5), [4,5;5]. Tỷ lệ được tính riêng trong từng nhãn đa trị.

## Hình 10 Mối liên hệ giữa số trang và Rating

File: `10_Scatter_Rating_SoTrang.png`

8.385 chấm = 8.385 Book Id · giữ toàn bộ bản ghi có dữ liệu cho cặp biến

Hiển thị toàn bộ 8.385 bản ghi, không lấy mẫu hoặc tổng hợp thành điểm trung bình. Spearman ρ = 0,125570. Trục số trang tuyến tính, giữ cả bản ghi nhiều trang.

## Hình 11 Mối liên hệ giữa lượt chấm sao và Rating

File: `11_Scatter_Rating_LuotCham.png`

8.402 chấm = 8.402 Book Id · giữ toàn bộ bản ghi có dữ liệu cho cặp biến

Hiển thị toàn bộ 8.402 bản ghi, không lấy mẫu hoặc tổng hợp thành điểm trung bình. Spearman ρ = 0,066525. Trục ngang đặt tại ln(1+x), nhãn hiển thị số gốc; phép log chỉ phục vụ hiển thị.

## Hình 12 Mối liên hệ giữa số bài nhận xét và Rating

File: `12_Scatter_Rating_NhanXet.png`

8.402 chấm = 8.402 Book Id · giữ toàn bộ bản ghi có dữ liệu cho cặp biến

Hiển thị toàn bộ 8.402 bản ghi, không lấy mẫu hoặc tổng hợp thành điểm trung bình. Spearman ρ = -0,018432. Trục ngang đặt tại ln(1+x), nhãn hiển thị số gốc; phép log chỉ phục vụ hiển thị.

## Hình 13 Độ nhạy của Rating trung bình theo ngưỡng lượt chấm

File: `13_DoNhay_NguongLuotCham.png`

Bốn ngưỡng 1, 100, 500 và 1.000 · không xóa vĩnh viễn các bản ghi dưới ngưỡng

Rating trung bình thay đổi từ 3,943 ở ngưỡng 1 đến 3,964 ở ngưỡng 1.000, chênh lệch khoảng 0,021 điểm. Ngưỡng cao cũng làm giảm số quan sát.
