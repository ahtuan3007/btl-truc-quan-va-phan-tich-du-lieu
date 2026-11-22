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

Khi tính tổng số bản ghi theo nhiều thể loại, đếm mã sách duy nhất vì mỗi sách có thể thuộc nhiều thể loại.

## Chạy lại mã xử lý

Dùng Python 3.12 trở lên. Mở terminal tại thư mục chứa `run_phase_4_5.py` và chạy:

```powershell
python -m pip install -r requirements.txt
python run_phase_4_5.py --output-root ket_qua_chay_lai
```

Chương trình kiểm tra CSV nguồn, làm sạch và xuất dữ liệu, bảng EDA cùng kết quả kiểm chứng vào `ket_qua_chay_lai/`.
