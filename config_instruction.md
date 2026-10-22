## 9 nhóm hằng số của config.py

| Nhóm | Gồm những giá trị nào |
|---|---|
| **Đường dẫn thư mục** | Thư mục gốc dự án, thư mục `data`, `backup`, thư mục chứa báo cáo xuất ra |
| **Tên file dữ liệu JSON** | Đường dẫn của từng file: bệnh nhân, bác sĩ, chuyên khoa, dịch vụ, lịch hẹn, phiếu khám, tài khoản, địa chỉ |
| **Cấu hình API địa chỉ** | URL gốc, phiên bản API đã chọn, thời gian chờ tối đa (timeout), số lần thử lại khi lỗi mạng |
| **Quy tắc nghiệp vụ phòng khám** | Thời lượng một lần khám mặc định, giờ mở và đóng cửa, bước chia ca khám, danh sách trạng thái lịch hẹn (đã đặt, đã khám, đã hủy), lựa chọn giới tính |
| **Tài khoản và bảo mật** | Tên các vai trò (admin, lễ tân), độ dài mật khẩu tối thiểu, thuật toán băm, độ dài salt |
| **Định dạng và mã hóa** | Định dạng ngày hiển thị và ngày lưu trong JSON, định dạng giờ, bảng mã file (`utf-8`), mức thụt lề khi ghi JSON |
| **Sao lưu** | Số bản sao lưu giữ lại tối đa, định dạng tên file sao lưu (kèm thời gian) |
| **Dữ liệu mẫu** | Số bệnh nhân và bác sĩ cần sinh, giá trị khởi tạo cho `random` (để ai chạy cũng ra cùng dữ liệu) |
| **Giao diện** | Tên ứng dụng, kích thước cửa sổ, font, bảng màu, tiêu đề các tab, kích thước vùng vẽ Canvas |

## Không nên đưa vào config.py

- **Biểu thức Regex** (số điện thoại, BHYT): để trong `validators.py` của A, vì chúng thuộc logic kiểm tra dữ liệu. Nếu nhóm muốn gom hết vào một chỗ thì vẫn được, nhưng cần thống nhất trước.
- **Dữ liệu thay đổi lúc chạy**: danh sách bệnh nhân đang tải lên, người đang đăng nhập... Đó là trạng thái của chương trình, không phải cấu hình.
- **Mật khẩu thật hay khóa bí mật**: không ghi trong code vì file này được đẩy lên GitHub. API địa chỉ không cần khóa nên nhóm này không áp dụng, nhưng nên giữ thói quen đó.
- **Hàm và lớp**: `config.py` chỉ chứa giá trị, không chứa xử lý.

## Quy ước khi chỉnh sửa config.py

Quy ước đặt tên: viết IN HOA, nối bằng dấu gạch dưới, và đặt tên theo ý nghĩa (ví dụ gắn "FILE_" cho đường dẫn file, "VAI_TRO_" cho vai trò) để cả nhóm đọc là hiểu. Cuối cùng, chia file thành các khối có dòng tiêu đề rõ ràng theo 9 nhóm trên, để A và B chỉ thêm vào khối của mình.