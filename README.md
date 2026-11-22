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

## Phân tích khám phá dữ liệu (EDA)

Mẫu chính có 8.402 bản ghi với Rating hợp lệ từ 1 đến 5 và ít nhất 100 lượt chấm. Rating trung bình là 3,955 và trung vị là 3,97. Số lượt chấm sao có tương quan Spearman 0,067 với Rating trên 8.402 bản ghi. [Thống kê mô tả](eda_tables/descriptive_primary.csv) · [Bảng tương quan](eda_tables/correlations_by_threshold.csv)

| Nội dung | Bảng để đối chiếu |
| --- | --- |
| Cỡ mẫu trước và sau khi lọc | [Luồng chọn mẫu](eda_tables/sample_flow.csv) |
| Rating theo nhóm | [Số trang](eda_tables/group_pages_all.csv) · [Thể loại](eda_tables/group_genre_all.csv) · [Ngôn ngữ](eda_tables/group_language_all.csv) · [Nhà xuất bản](eda_tables/group_publisher_all.csv) · [Thập niên xuất bản](eda_tables/group_decade_all.csv) |
| So sánh thập niên kết hợp với nhóm số trang | [Rating trung bình](eda_tables/pivot_rating_decade_by_pages.csv) · [Cỡ mẫu từng ô](eda_tables/pivot_n_decade_by_pages.csv) |
| Độ nhạy theo số lượt chấm tối thiểu | [Các ngưỡng 1, 100, 500 và 1.000](eda_tables/threshold_sensitivity.csv) |

[Thư mục EDA](eda_tables/) có 26 bảng CSV, gồm thống kê mô tả, tổng hợp nhóm, tương quan, bảng xoay và phân tích độ nhạy.

## Biểu đồ

[Thư mục biểu đồ](chart_outputs/) có 13 ảnh PNG, gồm biểu đồ phân phối, hộp, cột, đường, cột chồng và phân tán. [Chú thích từng hình](chart_outputs/ChuThich_Hinh_Python.md) ghi cỡ mẫu và cách đọc. Các hình 1–12 dùng mẫu chính, với số bản ghi có đủ dữ liệu theo từng biểu đồ. Hình 13 đối chiếu bốn ngưỡng lượt chấm. Biểu đồ theo thập niên so sánh các nhóm ấn bản theo thời điểm xuất bản.

## Chạy lại quy trình

| Tệp Python | Vai trò |
| --- | --- |
| `clean_data.py` | Kiểm tra CSV gốc, làm sạch và xuất master cùng hai bảng thể loại. |
| `eda.py` | Đọc dữ liệu sạch, tính thống kê, so sánh nhóm và xuất bảng EDA. |
| `visualize.py` | Đọc dữ liệu sạch và bảng EDA để kiểm tra, tạo và lưu biểu đồ. |
| `run_pipeline.py` | Chạy từng bước hoặc chạy toàn bộ theo thứ tự. |

Dùng Python 3.12 trở lên. Mở terminal tại thư mục chứa `run_pipeline.py`.

```powershell
python -m pip install -r requirements.txt
python run_pipeline.py
```

Để chạy từng bước, dùng các lệnh sau theo thứ tự.

```powershell
python run_pipeline.py --step clean
python run_pipeline.py --step eda
python run_pipeline.py --step visualize
```

Kết quả mới nằm trong `ket_qua_chay_lai/`. Có thể dùng `--output-root` để chọn thư mục khác. Để chỉ vẽ lại các hình từ dữ liệu và bảng EDA có sẵn trong gói, chạy `python run_pipeline.py --step visualize --data-root .`.
