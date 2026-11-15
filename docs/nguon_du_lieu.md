# Nguồn dữ liệu và khả năng đối chiếu

- Bộ chọn: [Goodreads-books-with-genres của middlelight](https://www.kaggle.com/datasets/middlelight/goodreadsbookswithgenres), phiên bản 1, metadata cập nhật 30/12/2022.
- Bộ nền: [Goodreads-books của jealousleopard](https://www.kaggle.com/datasets/jealousleopard/goodreadsbooks), phiên bản 2, metadata cập nhật 09/03/2020; tác giả mô tả bắt đầu thu thập qua Goodreads API năm 2019.
- File: `Goodreads_books_with_genres.csv`, 11.127 dòng, 13 cột, 2.956.663 byte.
- Metadata Kaggle của hai nguồn khai báo **CC0: Public Domain**. Nguồn dữ liệu được ghi nhận riêng; repository không gán một giấy phép mới bao trùm nội dung của bên thứ ba.

Theo tác giả middlelight, genre chủ yếu được bổ sung từ Goodreads; khoảng 300 bản ghi được bổ sung qua Google Books, còn 97 bản ghi chưa có nhãn. Ngày cập nhật không đồng nghĩa ngày thu thập từng trường. Chưa có căn cứ gọi danh sách này là mẫu ngẫu nhiên toàn Goodreads.

SHA-256 của CSV nguồn:

```text
721fc3bbe6367e91f2d3537d2cbe1c1ca4b585535d8ce63862c38a353d662b97
```

`data/reference/source_snapshot.json` chứa fingerprint, cấu trúc và các số đếm kiểm chứng cho đúng phiên bản này. `data/raw/source_metadata.json` lưu mô tả nguồn lúc kiểm tra. Code xác nhận fingerprint **trước khi ghi kết quả**, sau đó kiểm tra bảo toàn số dòng, thứ tự, giá trị 13 cột nguồn và khóa liên kết sau xuất/đọc lại CSV.

Các báo cáo Word trong `reports/` là bản đã dựng cho nguồn này. Pipeline chính tái tạo dữ liệu và bảng EDA; các gói phụ thuộc dựng Word không nằm trong yêu cầu cài đặt phân tích.
