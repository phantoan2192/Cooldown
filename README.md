# Discord Cooldown Bot

Bot Discord cho phép nhập số để đặt cooldown mặc định 60 phút.

## 💡 Chức năng
- Gõ `1` → cooldown account 1 = 60 phút
- Gõ `1 45` → cooldown 45 phút
- Gõ lại `1` → reset cooldown về 60 phút
- Lệnh `!check` hiển thị bảng cooldown:
  - 🟩 cooldown = 0
  - 🟨 < 10 phút
  - 🟥 > 10 phút
- Tự ping khi cooldown về 0
- Lưu cooldown vào file JSON

## 🚀 Deploy trên Render
1. Tạo repo GitHub
2. Deploy → New Web Service
3. Chọn build command:
