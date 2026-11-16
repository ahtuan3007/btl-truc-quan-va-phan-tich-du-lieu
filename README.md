# BTL trực quan và phân tích dữ liệu

**Đề tài:** Phân tích và trực quan hóa các yếu tố liên quan đến điểm đánh giá Rating của sách trên Goodreads.

Repository gồm dữ liệu nguồn cố định, code Python/Pandas làm sạch và EDA, các bảng kết quả cùng báo cáo. Phiên bản hiện tại có kết quả kỹ thuật mục 1–9, bổ sung code tái tạo 13 biểu đồ và hồ sơ đối chiếu dashboard Power BI năm trang. Bản PBIX và ảnh dashboard được quản lý trong thư mục bài tập cục bộ; không nằm trong repository. Người học tự viết báo cáo tổng từ căn cứ đã kiểm chứng.

## Kết quả chính

Mẫu so sánh chính có **8.402 bản ghi** với Rating từ 1 đến 5 và ít nhất 100 lượt chấm. Master vẫn giữ **11.127 bản ghi**; không xóa các dòng chỉ vì thiếu một biến.

| Biến so với Rating | Số cặp có dữ liệu | Spearman tổng thể |
| --- | ---: | ---: |
| Số trang | 8.385 | 0,125570 |
| Số lượt chấm sao | 8.402 | 0,066525 |
| Số bài nhận xét | 8.402 | −0,018432 |
| Năm xuất bản ghi trên bản ghi | 8.401 | −0,061631 |

Rating trung bình mẫu chính là **3,955**, trung vị **3,97**. Các tương quan tổng thể này nhỏ; một số tương quan trong nhóm thể loại khác với kết quả tổng thể. Nhóm từ 601 trang có Rating trung bình cao hơn nhóm 201–400 trang trong mẫu, nhưng các khoảng độ dài không tăng đều. Không diễn giải các kết quả thành quan hệ nhân quả hoặc xếp hạng toàn bộ Goodreads.

Đọc [phương pháp, kiểm tra độ nhạy và giới hạn](docs/phuong_phap_va_gioi_han.md) để biết chính xác ý nghĩa của kết quả.

## Chạy chương trình

Môi trường đã kiểm tra: **Python 3.12**, Pandas 3.0.1, NumPy 2.3.5. Dữ liệu đã có trong repository, không cần tài khoản Kaggle để chạy lại.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python run_phase_4_5.py
```

Ghi kết quả sang thư mục riêng:

```powershell
python run_phase_4_5.py --output-root ket_qua_chay_lai
```

`--input` dùng để chỉ đường dẫn tới **đúng bản CSV nguồn của báo cáo**, không quảng bá là công cụ nhận mọi CSV Goodreads. Chương trình kiểm tra SHA-256 và cấu trúc nguồn trước khi ghi bất kỳ kết quả nào. Nếu cần thay dữ liệu, phải rà soát lại manifest đối chiếu, quy tắc và báo cáo.

Chạy các kiểm tra chức năng:

```powershell
python -m unittest discover -s tests -v
```

Bộ kiểm tra gồm các trường hợp dữ liệu có rủi ro và một lần chạy toàn pipeline trên snapshot thật, đối chiếu lại cỡ mẫu cùng hệ số trong báo cáo. CSV nguồn được đặt `-text` trong `.gitattributes` để Git không đổi xuống dòng làm sai fingerprint khi clone trên máy khác.

## Đọc code theo thứ tự nào

1. `parse_args()` và `main()`: đọc tham số, gọi pipeline; import module không tự chạy phân tích.
2. `run_pipeline()`: xác nhận nguồn trước khi tạo kết quả, chọn phạm vi EDA, xuất bảng và kiểm chứng.
3. `clean_books()`: giữ nguyên 13 cột nguồn, thêm các cột chuẩn hóa và cờ kiểm tra.
4. `describe()`, `group_summary()`, `corr_table()`: thống kê mô tả, tổng hợp nhóm và tương quan theo cặp có dữ liệu.
5. `data/reference/source_snapshot.json`: fingerprint, cột nguồn và các số đếm đối chiếu của bản dữ liệu này.

Các quy ước được đặt tên ở đầu code: `PRIMARY_MIN_RATINGS=100`, `MIN_GROUP_SIZE=30` và `SENSITIVITY_THRESHOLDS=(1, 100, 500, 1000)`. Đây là quy ước của phiên bản báo cáo, không phải ngưỡng bảo đảm độ chính xác thống kê. Chúng cũng được ghi vào `work/eda_results.json`.

## Cấu trúc dự án

```text
run_phase_4_5.py                Code chính làm sạch và EDA
requirements.txt               Thư viện cho phân tích
data/raw/                      CSV nguyên bản và metadata nguồn
data/reference/                Manifest kiểm chứng snapshot
data/processed/                Master, bridge thể loại và danh mục nhãn
eda_tables/                    Thống kê, groupby, pivot và nhật ký thay đổi
work/eda_results.json          Kết quả đầy đủ và cấu hình phân tích
work/validation_results.json   Các kiểm tra bảo toàn và đối chiếu nguồn
tests/                         Kiểm tra các trường hợp có ý nghĩa
docs/                          Phương pháp, giới hạn và nguồn dữ liệu
reports/                       Các báo cáo Word đã dựng và kiểm tra bố cục
```

## Quy tắc dữ liệu quan trọng

- Master **11.127 dòng × 45 cột** giữ 13 cột nguồn và thêm 32 trường. Ngày/số trang/nhà xuất bản chuẩn hóa nằm ở cột mới.
- 76 số trang 0 thành thiếu ở `pages`; hai ngày không tồn tại thành thiếu ở ngày chuẩn hóa; 5 `Not Avail` thành thiếu ở `publisher_clean`.
- Giữ 81 dòng có lượt chấm 0, trong đó 55 có Rating dương. Không tự sửa Rating hoặc gọi tất cả là dữ liệu sai.
- Giữ ISBN dạng chuỗi; chỉ thêm cờ kiểm tra. Không tự thêm số 0 vào mã bất thường.
- Genre tách bằng dấu **chấm phẩy**, giữ dấu phẩy bên trong nhãn. Bảng bridge có **94.794 cặp**, **890 nhãn**; tổng nhóm đa nhãn có thể vượt tổng số bản ghi.
- Không cộng lượt chấm giữa các ấn bản. Tên/người đóng góp giống nhau chưa chứng minh là tác phẩm độc lập đã được xác minh.

Các file phân tích dùng UTF-8 có BOM, ô thiếu để trống. Power BI hiện giữ Book Id/ISBN dạng Text, lọc thể loại qua bridge và giữ nhóm publisher khác hoa/thường bằng khóa số. Xem docs/powerbi_model.md.

## Báo cáo và nguồn

- [Mục tiêu, mô tả và kiểm tra dữ liệu](reports/BaoCao_MucTieu_MoTa_KiemTra.docx)
- [Báo cáo làm sạch và EDA](reports/BaoCao_LamSach_EDA.docx)
- [Bản review làm sạch và EDA](reports/Review_LamSach_EDA.docx)
- [Nguồn và phiên bản dữ liệu](docs/nguon_du_lieu.md)

Báo cáo Word là bản cố định theo snapshot và cấu hình đã công bố. `requirements.txt` chỉ phục vụ tái tạo dữ liệu và bảng EDA; không bao gồm bộ dựng Word. Không có yêu cầu cài Microsoft Word để chạy code phân tích.

## Biểu đồ và dashboard đã kiểm tra (mục 6–9)

```powershell
python -m pip install -r requirements.txt -r requirements_charts.txt
python run_charts.py
```

Script đọc snapshot đã duyệt và kiểm tra fingerprint trước khi vẽ. Khi chạy trong
repository, 13 PNG và chú thích nằm trong `chart_outputs/`; manifest, bảng tham chiếu
và số liệu viết báo cáo nằm trong `work/charts_stage6/`. Có thể đổi đích bằng
`--output-dir` và `--work-dir`. Không cần chạy lại làm sạch để tạo biểu đồ.

Python/Pandas/NumPy giữ phiên bản như trên; Matplotlib 3.10.8 được thêm trong
requirements_charts.txt. Ba scatter dùng đầy đủ cặp hợp lệ, không lấy mẫu.
Histogram thập phân khớp 40 khoảng Power BI; các nhóm genre dùng Book Id duy nhất.

- [Insight đã đối chiếu](docs/INSIGHT_DA_DOI_CHIEU.md)
- [Hướng dẫn tự viết báo cáo](docs/HUONG_DAN_VIET_BAO_CAO.md)
- [Hướng dẫn sử dụng Power BI](docs/HUONG_DAN_SU_DUNG.md)
- [Model, khóa nhóm và quy tắc tính](docs/powerbi_model.md)
- [Hồ sơ kiểm chứng](work/powerbi_final/README.md)

Dashboard có năm trang, sáu bộ lọc đồng bộ, tìm sách và Top N. Đã đọc lại model từ
PBIX lưu trên đĩa: 81 truy vấn, 9.173 kiểm tra số liệu đạt, 0 lỗi; 13 tình huống UI
đã quan sát. Raw/master/bridge, pipeline và các bảng EDA cũ được bảo toàn.
Các đường dẫn 03_BaoCao_DaCo/04_PowerBI_BanChinh nhắc trong hướng dẫn là cấu trúc
của bộ bài tập cục bộ, không phải thư mục đã upload lên GitHub.
