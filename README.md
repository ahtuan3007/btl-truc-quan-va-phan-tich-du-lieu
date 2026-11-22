# BTL trực quan và phân tích dữ liệu · Nhóm 5

Phân tích và trực quan hóa các yếu tố ảnh hưởng đến điểm đánh giá (Rating) của sách trên Goodreads. Dữ liệu này dùng để khảo sát mối liên hệ giữa các biến trong mẫu.

## Dữ liệu

| Tệp | Nội dung |
| --- | --- |
| `data/raw/Goodreads_books_with_genres.csv` | CSV gốc có 11.127 bản ghi và 13 cột. |
| `data/processed/books_cleaned_master.csv` | Dữ liệu sạch theo bản ghi sách/ấn bản. 8.402 bản ghi thuộc mẫu phân tích chính (`primary_sample=True`, Rating hợp lệ từ 1 đến 5 và ít nhất 100 lượt chấm). |
| `data/processed/book_genres_bridge.csv` | Bảng nối sách với thể loại, mỗi cặp mã sách và thể loại có một dòng. |
| `data/processed/genres_dimension.csv` | Danh mục thể loại. |
| `data/reference/source_snapshot.json` | Mã SHA-256, danh sách cột và số đếm để mã Python đối chiếu dữ liệu nguồn. |

Nguồn dữ liệu là [Goodreads-books-with-genres của middlelight trên Kaggle](https://www.kaggle.com/datasets/middlelight/goodreadsbookswithgenres), giấy phép CC0 theo công bố của bộ dữ liệu.

### Các cột và tiêu chí so sánh Rating

CSV gốc có 13 cột. Phân tích dùng `average_rating` làm điểm cần so sánh và dùng bảy cột ngay sau đó trong bảng làm tiêu chí chính.

| Cột trong CSV | Ý nghĩa | Cách dùng |
| --- | --- | --- |
| `average_rating` | Điểm đánh giá trung bình của bản ghi sách trên Goodreads, theo thang 5 điểm | Điểm cần phân tích |
| `num_pages` | Số trang của ấn bản | So sánh Rating giữa các nhóm độ dài |
| `genres` | Các thể loại được gắn cho sách | So sánh Rating theo thể loại qua bảng nối `book_genres_bridge.csv` |
| `language_code` | Mã ngôn ngữ của ấn bản | So sánh Rating giữa các nhóm ngôn ngữ |
| `publisher` | Nhà xuất bản ghi trong dữ liệu | So sánh Rating giữa các nhà xuất bản, kèm số bản ghi từng nhóm |
| `publication_date` | Ngày xuất bản ghi trong dữ liệu | Tách năm hoặc thập niên để so sánh các nhóm ấn bản theo thời điểm xuất bản |
| `ratings_count` | Số lượt chấm sao | Xem mối liên hệ giữa số lượt chấm và Rating. Dùng để lọc mẫu theo số lượt chấm tối thiểu |
| `text_reviews_count` | Số bài nhận xét bằng chữ | Xem mối liên hệ giữa số bài nhận xét và Rating |
| `Author` | Tên tác giả hoặc người đóng góp ghi trong dữ liệu | Có thể so sánh bổ sung theo tác giả nếu mỗi nhóm có đủ bản ghi |
| `Book Id` | Mã bản ghi sách trên Goodreads | Nhận diện bản ghi và nối với bảng thể loại |
| `Title` | Tên sách | Tra cứu và hiển thị |
| `isbn` | Mã ISBN-10 của ấn bản | Nhận diện và tra cứu ấn bản |
| `isbn13` | Mã ISBN-13 của ấn bản | Nhận diện và tra cứu ấn bản |

Khi tính tổng số bản ghi theo nhiều thể loại, đếm mã sách duy nhất vì mỗi sách có thể thuộc nhiều thể loại.

## Chạy lại mã xử lý

Dùng Python 3.12 trở lên. Mở terminal tại thư mục chứa `btl_truc_quan.py` và chạy:

```powershell
python -m pip install -r requirements.txt
python btl_truc_quan.py --output-root ket_qua_chay_lai
```

Chương trình kiểm tra CSV nguồn, làm sạch và xuất dữ liệu, bảng EDA cùng kết quả kiểm chứng vào `ket_qua_chay_lai/`.
