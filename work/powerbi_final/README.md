# Hồ sơ kiểm chứng Power BI cuối

`model_test_queries.json`: 81 truy vấn DAX cùng kỳ vọng từ master/bridge/bảng EDA.
`expected_filter_cases.json`: 56 trạng thái lọc và các tập xếp hạng tham chiếu.
`model_query_results.json`: kết quả thực đọc từ model Power BI Desktop.
`model_validation_summary.json`: 9.173 kiểm tra số liệu, 0 lỗi; dung sai 1e-10.
`ui_acceptance.json`: 13 tình huống giao diện đã quan sát trực tiếp.

Các CSV khóa giữ nguyên nhóm nguồn phân biệt hoa/thường; bridge có 94.794 cặp duy nhất.
`dashboard_measures.json` lưu định nghĩa 26 measure bổ sung; 17 measure gốc được giữ.

Để kiểm tra lại kết quả đã lưu, chạy `python validate_model_results.py` tại thư mục này.
Muốn đọc lại model đang mở: dùng Windows PowerShell 5.1, thư viện ADOMD của SSMS 20,
rồi chạy `run_model_queries.ps1 -Port <cổng Analysis Services của phiên Power BI>`.
Cổng phụ thuộc mỗi lần mở; không dùng cổng của máy/phiên cũ. Sau đó chạy validator.
Không dùng script kiểm chứng để sửa model hoặc dữ liệu.
