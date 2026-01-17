# Monitoring System – FastAPI, MongoDB, RabbitMQ, Telegram

## 1. Giới thiệu

Dự án này là một **hệ thống monitoring đơn giản theo hướng microservices**, được xây dựng để minh họa:

- Sử dụng **FastAPI** cho API ingest dữ liệu
- **MongoDB** để lưu trữ metric, threshold và alert
- **RabbitMQ** làm message queue
- **Worker / background / long-running task** để xử lý alert
- Gửi cảnh báo (**alert**) qua **Telegram Bot**
- Chạy toàn bộ hệ thống bằng **Docker Compose**

Dự án phù hợp cho:
- Bài test backend
- Demo kiến trúc event-driven
- Ôn tập FastAPI + RabbitMQ + MongoDB

---

## 2. Kiến trúc tổng thể

```
Client / Device
      |
      v
Device Service (FastAPI)
      |
      | publish metric
      v
RabbitMQ (metrics_exchange)
      |
      v
Alert Service (Worker)
  - so sánh threshold
  - sinh alert
  - lưu MongoDB
      |
      v
RabbitMQ (alerts_exchange)
      |
      v
Notify Service (Worker)
  - gửi Telegram
```

### Ý tưởng chính
- API **không xử lý nặng**
- Mọi tác vụ tốn thời gian đều chạy ở **background worker**
- Dễ scale từng service độc lập

---

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ |
|----------|----------|
| API | FastAPI |
| Database | MongoDB |
| Message Queue | RabbitMQ |
| Worker | Python |
| Notify | Telegram Bot API |
| Container | Docker, Docker Compose |

---

## 4. Cấu trúc thư mục

```
monitoring-system/
├── docker-compose.yml
├── .env
│
├── device-service/
│   ├── main.py
│   ├── rabbit.py
│   ├── config.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── alert-service/
│   ├── consumer.py
│   ├── rabbit.py
│   ├── seed.py
│   ├── config.py
│   ├── Dockerfile
│   └── requirements.txt
│
└── notify-service/
    ├── consumer.py
    ├── rabbit.py
    ├── config.py
    ├── Dockerfile
    └── requirements.txt
```

---

## 5. Database schema (MongoDB)

### Database: `monitoring`

#### Collection: `metrics`
```json
{
  "device_id": "router-01",
  "metric": "cpu_usage",
  "value": 95,
  "timestamp": "2025-12-10T10:00:00"
}
```

#### Collection: `thresholds`
```json
{
  "metric": "cpu_usage",
  "normal": 60,
  "warning": 61,
  "critical": 80
}
```

#### Collection: `alerts`
```json
{
  "_id": "ObjectId",
  "device_id": "router-01",
  "metric": "cpu_usage",
  "value": 95,
  "level": "critical",
  "timestamp": "2025-12-10T10:00:00"
}
```

---

## 6. Luồng xử lý chính

1. Client gửi metric vào API `/metrics`
2. Device-service:
   - Lưu metric vào MongoDB
   - Publish message vào RabbitMQ (`metrics_exchange`)
3. Alert-service:
   - Consume metric
   - So sánh với threshold
   - Sinh alert nếu vượt ngưỡng
   - Lưu alert vào MongoDB
   - Publish alert sang `alerts_exchange`
4. Notify-service:
   - Consume alert
   - Gửi thông báo Telegram

---

## 7. Seed threshold khi start service

Alert-service tự động:
- Tạo **unique index** cho field `metric`
- Seed dữ liệu threshold mặc định khi service start
- Restart service **không tạo trùng dữ liệu**

Áp dụng pattern: **idempotent seed**

---

## 8. Cấu hình môi trường (.env)

```env

MONGO_HOST=mongo
MONGO_PORT=27017
MONGO_USER=
MONGO_PASSWORD=
MONGO_DB=monitoring

RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASS=guest

METRICS_QUEUE=metrics_queue
ALERTS_QUEUE=alerts_queue

METRICS_EXCHANGE=metrics_exchange
ALERTS_EXCHANGE=alerts_exchange

TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
CHAT_ID=YOUR_CHAT_ID
```

> ⚠️ Không commit file `.env` trên máy chỉ commit `.env` mẫu

---

## 9. Chạy project bằng Docker Compose

### Build & start

```bash
docker-compose up --build
```

### RabbitMQ Management UI

```
http://localhost:15672
user: guest
pass: guest
```

---

## 10. Test API

```bash
curl -X POST http://localhost:8000/metrics \
-H "Content-Type: application/json" \
-d '{
  "device_id": "router-01",
  "metric": "cpu_usage",
  "value": 95,
  "timestamp": "2025-12-10T10:00:00"
}'
```

➡️ Telegram sẽ nhận được alert ngay nếu vượt threshold.

---

## 11. Điểm nổi bật của project

- Event-driven architecture
- Không block API
- Worker chạy độc lập
- Dễ scale
- Config tách biệt bằng env
- Phù hợp production mindset

---


