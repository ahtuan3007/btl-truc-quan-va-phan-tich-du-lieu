# Tiến độ theo kế hoạch mười bước

Cập nhật 16/11/2026 sau vòng rà soát độc lập và sửa trình bày. Trạng thái dưới đây áp dụng cho kế hoạch Goodreads + Power BI đã chọn, không phải chứng nhận khớp tuyệt đối toàn văn yêu cầu của thầy.
Phạm vi đã chốt: không làm slide hoặc chuẩn bị nộp. Theo lời nhắn mới nhất,
người học tự viết báo cáo tổng; các căn cứ kỹ thuật và hướng dẫn đã chuẩn bị xong.

| Bước | Trạng thái và căn cứ |
|---|---|
| 1. Mục tiêu và câu hỏi | Đã có: Rating và bảy yếu tố, diễn giải mối liên hệ trong snapshot. |
| 2. Mô tả dữ liệu | Đã có nguồn, 13 cột gốc, cấp bản ghi/ấn bản và giới hạn chọn mẫu. |
| 3. Chất lượng | Đã có audit, thiếu/trùng/ngoại lệ và giới hạn cấp tác phẩm. |
| 4. Làm sạch | Đã có code, master 11.127, bridge 94.794, nhật ký; giữ nguyên nguồn. |
| 5. EDA | Đã có thống kê, groupby, pivot, tương quan, độ nhạy; kết quả cũ được bảo toàn. |
| 6. Bộ biểu đồ | Hoàn thành 13 ảnh Python riêng cùng chú thích và code tái tạo. Đủ so sánh, phân phối/boxplot, thời gian, cột chồng và scatter. |
| 7. Năm page | Hoàn thành: Tổng quan; So sánh; Quan hệ Rating; Năm xuất bản; Tra cứu/Top N. Ba KPI chung chỉ ở Tổng quan. Bảng người phụ trách từng page còn chờ thông tin thật. |
| 8. Tương tác | Hoàn thành sáu bộ lọc đồng bộ, OR genre qua bridge, publisher theo khóa số, tìm tên, Top N, ngưỡng lượt chấm, trạng thái rỗng. Đã kiểm tra model và giao diện. |
| 9. Insight | Hoàn thành tài liệu insight đối chiếu bảy yếu tố, mức phổ biến so với Rating, độ nhạy và giới hạn; ánh xạ từng hình với mẫu số. Đã bổ sung gợi ý ra quyết định có căn cứ sau khi phát hiện phần này còn thiếu ở lần báo trước. |
| 10. Báo cáo và hướng dẫn | Căn cứ số liệu, ảnh, code, hướng dẫn sử dụng và khung viết đã sẵn sàng. Báo cáo tổng do người học viết; chưa đánh dấu phần viết này hoàn thành. |

## Những việc chưa thể tự đánh dấu hoàn thành

- Đề chung cho phép Power BI, nhưng phần mẫu chi tiết dùng Plotly/Streamlit và
  bố cục bán lẻ; cần xác nhận cách áp dụng của thầy. Xem [review rà soát cuối](REVIEW_RASOAT_CUOI.md).
- Bảng phân công dưới đây chưa có người phụ trách được người dùng xác nhận.
- Báo cáo tổng còn do người học viết. Không làm slide/chuẩn bị nộp trong phạm vi hiện tại.

| Page | Người phụ trách |
|---|---|
| Tổng quan | Chưa cung cấp |
| So sánh nhóm sách | Chưa cung cấp |
| Quan hệ với Rating | Chưa cung cấp |
| Theo năm xuất bản | Chưa cung cấp |
| Tra cứu và Top N | Chưa cung cấp |

## Kết quả nghiệm thu kỹ thuật

- 81 truy vấn DAX, 56 trạng thái tham chiếu, 9.173 phép so sánh giá trị/danh sách: 0 lỗi (không phải 9.173 chức năng độc lập),
  sai số tuyệt đối lớn nhất 4,6602e-14 (dung sai 1e-10).
- Đã mở lại chính PBIX đã lưu trong thư mục bài và đọc lại đủ 81 truy vấn: vẫn đạt 9.173 phép đối chiếu.
- 13 tình huống UI quan sát: mặc định, tìm tên/chọn/bỏ chọn, Top 5/10, ngưỡng 500,
  đồng bộ trang, lọc rỗng và phục hồi. Cả năm trang render được, không thấy lỗi visual.
- Kiểm tra toàn bộ nhóm genre/publisher bằng khóa, không chỉ vài giá trị KPI;
  đủ 40 khoảng histogram khớp Python/Power BI. 13 hình riêng và năm ảnh trang đã rà bố cục.
- Raw/master/bridge, code làm sạch và bảng EDA cũ giữ nguyên byte. Chỉ bổ sung
  quy tắc trình bày bốn khoảng Rating và các khóa/measure phục vụ dashboard.

Đây là các kiểm tra thực tế được lưu bằng chứng; không tuyên bố đã chạy lặp 100 lần
hoặc bảo đảm dữ liệu không còn bất kỳ giới hạn nào.

Rà soát bổ sung đã kiểm riêng 1.888 dòng genre×bin, từng bản ghi số trong model,
bridge và 36 truy vấn Top12/Top50/100 theo ngữ cảnh. UI đã thử thêm Top50/100 và
hợp Fiction + Fantasy. Các bằng chứng này bổ sung phạm vi cũ, không cộng dồn thành
một số “KPI kiểm thử” để suy ra bài hoàn hảo.

## Việc tiếp theo của người viết

1. Mở [hướng dẫn viết](HUONG_DAN_VIET_BAO_CAO.md) để chọn cấu trúc báo cáo tổng.
2. Lấy nhận xét và số liệu từ [insight đã đối chiếu](INSIGHT_DA_DOI_CHIEU.md).
3. Chèn ảnh riêng từ ../04_PowerBI_BanChinh/BieuDo_BaoCao và ảnh sản phẩm từ Anh_Dashboard.
4. Mô tả tương tác theo [hướng dẫn sử dụng](HUONG_DAN_SU_DUNG.md).
5. Sau khi viết, đối chiếu lại số liệu, N, bộ lọc và tên hình trong bản thảo.

Power BI là công cụ đã chọn thay ứng dụng Streamlit trong kế hoạch cũ. Python/Pandas
phục vụ làm sạch, EDA; Matplotlib tạo ảnh riêng. Không có việc tạo thêm ứng dụng khác
hoặc thay dữ liệu chỉ để làm đẹp kết quả.

Code biểu đồ và tài liệu kiểm chứng đã cập nhật lên [GitHub, commit 2f71f83](https://github.com/ahtuan3007/btl-truc-quan-va-phan-tich-du-lieu/tree/2f71f832d4d4c694376844a35e4e966e69dd61c3), branch codex/goodreads-eda. PBIX và ảnh sản phẩm nằm trong thư mục bài cục bộ.
