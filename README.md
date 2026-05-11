# SHB AI Financial Assistant 🚀

Trợ lý AI chuyên gia về phân tích cổ phiếu SHB (Ngân hàng TMCP Sài Gòn - Hà Nội). Hệ thống kết hợp sức mạnh của **Gemini 2.5 Flash** cùng dữ liệu thị trường thực tế và báo cáo phân tích chuyên sâu.

## ✨ Tính năng nổi bật

- **🔍 PDF Deep Search:** Tự động tra cứu và trích dẫn thông tin từ các báo cáo phân tích tổ chức (Institutional Reports).
- **📈 Real-time Market Data:** Tích hợp **VNStock 4.0** để cập nhật giá chứng khoán, khối lượng giao dịch và chỉ số tài chính mới nhất.
- **🧠 Expert Reasoning:** Hệ thống Prompt chuyên gia giúp AI phối hợp dữ liệu tĩnh (PDF) và dữ liệu động (VNStock) để đưa ra nhận định khách quan.
- **💼 Admin Dashboard:** Quản lý hội thoại, theo dõi đánh giá người dùng (Ratings) và hiệu suất của AI.
- **⚡ Background Processing:** Sử dụng Celery & Redis để xử lý các tác vụ phân tích nặng và gửi thông báo.

## 🛠️ Công nghệ sử dụng

| Thành phần | Công nghệ |
|-----------|-----------|
| **AI Brain** | Gemini 2.5 Flash (Google) |
| **Framework AI** | PydanticAI |
| **Backend** | FastAPI + Pydantic v2 + SQLAlchemy (Async) |
| **Frontend** | Next.js 15 + React 19 + Tailwind CSS |
| **Database** | PostgreSQL (Supabase) |
| **Real-time Data**| VNStock API v4 |
| **Cache & Task** | Redis + Celery |

## 🚀 Cài đặt nhanh (Local)

### 1. Chuẩn bị môi trường
Yêu cầu: Docker, Python 3.12+, Node.js 20+.

```bash
# Clone dự án
git clone https://github.com/username/shb-chatbot.git
cd shb-chatbot
```

### 2. Cấu hình Backend
Tạo file `shb_chatbot/backend/.env`:
```bash
GEMINI_API_KEY=your_gemini_key
VNSTOCK_API_KEY=your_vnstock_key
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/shb_chatbot
REDIS_URL=redis://localhost:6379/0
```

### 3. Khởi chạy với Docker
```bash
# Chạy database và redis
docker-compose up -d db redis

# Cài đặt dependencies (dùng uv)
cd shb_chatbot/backend
uv sync
uv run shb_chatbot db upgrade
uv run shb_chatbot user create --email admin@example.com --password admin123 --superuser

# Chạy Server & Worker
uv run shb_chatbot server run --reload
```

### 4. Khởi chạy Frontend
```bash
cd shb_chatbot/frontend
npm install
npm run dev
```
Truy cập: [http://localhost:3000](http://localhost:3000)

## 🌐 Kế hoạch Triển khai (Production)

Dự án đã sẵn sàng để triển khai lên các nền tảng Cloud:
1.  **Database:** Supabase (PostgreSQL).
2.  **Backend:** Render / Railway (Docker Support).
3.  **Frontend:** Cloudflare Pages / Vercel.

Chi tiết các bước triển khai có tại: `plans/deployment-plan.md`.

## 📁 Cấu trúc thư mục

```
shb_chatbot/
├── backend/            # FastAPI Source Code
│   ├── app/agents/     # AI Agent logic & Tools
│   ├── app/api/        # REST & WebSocket Routes
│   └── tests/          # Integration & Unit tests
├── frontend/           # Next.js Application
└── docs/               # Technical Documentation
```

## 🤝 Đóng góp
Mọi ý kiến đóng góp và báo lỗi xin vui lòng tạo Issue hoặc Pull Request trên GitHub.

---
*Phát triển bởi chuyên gia AI dành cho cộng đồng nhà đầu tư SHB.*
