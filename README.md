# CV Chat Assistant 🤖

Trợ lý AI trả lời câu hỏi về CV của **Nguyễn Hồng Phong**, sử dụng DeepSeek API với khả năng hiển thị quá trình suy nghĩ (thinking process).

## ✨ Tính năng

- 💬 **Chat với CV**: Hỏi bất kỳ thông tin nào về CV của Phong
- 🧠 **Thinking Process**: Xem quá trình suy nghĩ của AI với format đẹp mắt
- 💡 **Gợi ý câu hỏi**: Endpoint cung cấp danh sách câu hỏi gợi ý
- 🔄 **Fallback thông minh**: Tự động chuyển sang tìm kiếm từ khóa nếu API không khả dụng
- 🌐 **CORS enabled**: Sẵn sàng tích hợp với frontend

## 🚀 Cài đặt

### 1. Clone hoặc tải project

```bash
git clone https://github.com/F1792005/chatbotnew.git
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình API Key (tùy chọn)

Tạo file `.env` trong thư mục project:

```bash
AZURE_API_KEY=your_azure_api_key_here
```

**Lưu ý**: Nếu không có API key, hệ thống sẽ tự động dùng fallback mode (tìm kiếm từ khóa trong `data.json`).

## 🎯 Chạy ứng dụng

### Chạy server

```bash
python3 main.py
```

Server sẽ chạy tại: `http://127.0.0.1:8000`

### Hoặc chạy trực tiếp với uvicorn

```bash
uvicorn chat_router:app --host 0.0.0.0 --port 8000 --reload
```

## 📡 API Endpoints

### 1. Health Check
```bash
GET /health
```

**Response:**
```json
{"status": "ok"}
```

### 2. Chat với CV (có thinking process)
```bash
POST /chat
```

**Request Body:**
```json
{
  "question": "Email của bạn là gì?",
  "include_thinking": true
}
```

**Response:**
```json
{
  "thinking": "🔍 Phân tích câu hỏi: Người dùng muốn biết email\n📋 Thông tin liên quan: fong1792005@gmail.com\n💡 Kết luận: Trả về email",
  "answer": "Email của tôi là fong1792005@gmail.com"
}
```

**Tham số:**
- `question` (required): Câu hỏi về CV
- `include_thinking` (optional, default: true): Có hiển thị quá trình suy nghĩ không

### 3. Lấy câu hỏi gợi ý
```bash
GET /suggestions
```

**Response:**
```json
{
  "suggestions": [
    "Email và thông tin liên hệ của Phong là gì?",
    "Phong có những kỹ năng lập trình nào?",
    "Mục tiêu nghề nghiệp của Phong là gì?",
    ...
  ]
}
```

## 🧪 Test API

### Sử dụng script demo

```bash
python3 test_api.py
```

### Hoặc test với curl

```bash
# Health check
curl http://127.0.0.1:8000/health

# Lấy gợi ý
curl http://127.0.0.1:8000/suggestions

# Chat (không có thinking)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"email của bạn là gì?","include_thinking":false}'

# Chat (có thinking)
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Phong có kỹ năng gì về AI?","include_thinking":true}'
```

### Test với Python requests

```python
import requests

# Chat request
response = requests.post("http://127.0.0.1:8000/chat", json={
    "question": "Mục tiêu nghề nghiệp của Phong là gì?",
    "include_thinking": True
})
data = response.json()
print(data["thinking"])  # Quá trình suy nghĩ
print(data["answer"])    # Câu trả lời
```

## 📁 Cấu trúc project

```
cvassitant/
├── chat_service.py      # Service xử lý logic chat (DeepSeek + fallback)
├── chat_router.py       # FastAPI routes và endpoints
├── main.py              # Entry point để chạy server
├── data.json            # Dữ liệu CV của Phong (JSON format)
├── data.txt             # Dữ liệu CV của Phong (Text format) - fallback nếu không có JSON
├── test_api.py          # Script demo test API
├── requirements.txt     # Python dependencies
├── .env                 # API keys (tùy chọn, không commit)
└── README.md            # File này
```

**Lưu ý về data**: Hệ thống sẽ ưu tiên load `data.json`, nếu không có sẽ tự động load `data.txt`.

## 🎨 Format Thinking Process

Khi có API key, thinking process sẽ được format đẹp với emoji:

```
🔍 Phân tích câu hỏi: [phân tích ý định người dùng]
📋 Thông tin liên quan: [liệt kê thông tin từ CV]
💡 Kết luận: [tổng hợp câu trả lời]
```

## 🔧 Mở rộng

### Thêm thông tin CV

Chỉnh sửa file `data.json` (JSON format) hoặc `data.txt` (plain text format). Hệ thống sẽ tự động nhận diện và sử dụng file có sẵn.

### Tùy chỉnh system prompt

Xem method `generate_response` trong class `DeepSeekService` (file `chat_service.py`).

### Thêm endpoint mới

Chỉnh sửa file `chat_router.py` và thêm route mới.

## 📦 Dependencies

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `openai` - Client cho DeepSeek API
- `python-dotenv` - Quản lý environment variables
- `requests` - HTTP client (cho test script)

## 🤝 Liên hệ
- Email: fong1792005@gmail.com
- Facebook: facebook.com/apctxyz112
- GitHub: github.com/F1792005
- Telegram: @apctxyz112
- Website: đang cập nhật
## 📝 License

MIT License - Tự do sử dụng và chỉnh sửa.

---

Được xây dựng với ❤️ bởi Phong
