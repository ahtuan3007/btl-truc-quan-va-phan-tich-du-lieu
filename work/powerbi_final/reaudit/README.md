# Bằng chứng rà soát bổ sung

`independent_numeric_audit.json`: tính độc lập từ raw, các nhóm/correlation/56states
và từng1.888 dòng genre×bin. `extra_*`:36truy vấn Top12/cộtchồng/Top50/100.
`exact_readback_summary.json`: đọc từng bản ghi số và bridge từ model; full dump
được giữ ngoài folder bài để tránh sao chép trùng dữ liệu. `applied_aliases.json`:
chỉ đổi tên hiển thị, không đổi toán hoặc dữ liệu. `DOI_CHIEU_YEU_CAU_DOCX.md`:
phân biệt phần chung và mẫu chi tiết trong đề. `render_summary.json`: so ảnh mới/cũ.

Chạy `python audit_independent.py` để tái tính từ raw và so model81query đã lưu ở
thư mục cha. `python validate_extra_results.py` so36query với kỳ vọng độc lập.
Hai script dùng dữ liệu của chính bản sao/repository, không cần đường dẫn máy dựng.
Muốn tái tạo full dump native cần Power BI đang mở và ADOMD/SSMS20: chạy script
PowerShell `run_model_queries.ps1 -Port <cổng phiên đang mở>`, rồi
`python compare_exact_model.py`. Full dump chưa chép vào đây để tránh dữ liệu lặp.
Không phải một app và không tự kết luận đủ mọi yêu cầu chỉ vì số kiểm tra lớn.
