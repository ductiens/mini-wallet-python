# AGENTS.md

Tài liệu hướng dẫn dành cho các AI Coding Agent làm việc trong dự án **Fintech FraudOps Copilot**.

Hãy đọc kỹ tài liệu này trước khi chỉnh sửa bất kỳ phần mã nguồn nào. Đây là bộ quy tắc của dự án về kiến trúc, kiểm thử, phạm vi sản phẩm và phương thức giao tiếp.

---

## 🌟 1. Project Overview & Focus

**Fintech FraudOps Copilot** is a prototype AI/Data Engineering project for fintech fraud detection.
It ingests PaySim transaction data, cleans and engineers features, trains fraud detection models,
runs batch inference, stores outputs in MongoDB, and exposes a Risk Investigation Agent through FastAPI.

### Các cấu phần trọng tâm của MVP:
1. **Data Pipeline**: Profiling thô, làm sạch, và kỹ nghệ đặc trưng (feature engineering) từ bộ dữ liệu mô phỏng giao dịch Kaggle PaySim.
2. **AI/ML Model**: Huấn luyện mô hình phân loại Logistic Regression baseline và Random Forest Classifier champion, lưu model `.joblib` và feature JSON phục vụ dự đoán.
3. **Batch Inference**: Thực hiện dự đoán offline hàng loạt và xuất kết quả `predictions.csv`.
4. **MongoDB Data Serving**: Lưu trữ và truy vấn tối ưu các giao dịch, đặc trưng và dự đoán phục vụ API.
5. **Risk Investigation Agent**: Agent bán tự động phân tích rủi ro dựa trên rules và mô hình AI để đưa ra báo cáo chi tiết kèm giải thích bằng Markdown phục vụ các điều tra viên gian lận (FraudOps).

---

## 🚫 2. Phạm vi Sản phẩm (Scope Limits)
Để tránh làm quá tải và phình to phạm vi MVP một cách không cần thiết, **TUYỆT ĐỐI KHÔNG** tự ý tích hợp:
- Real-time streaming hoặc Event-driven architecture bằng Kafka / RabbitMQ.
- Giao diện người dùng frontend / Dashboard (ngoại trừ tài liệu Swagger tự động của FastAPI).
- Tích hợp thực tế với các LLM bên ngoài (OpenAI, Gemini API, LangChain, v.v.). MVP hiện tại sử dụng Risk Investigation Agent dạng rule-based chất lượng cao, phản hồi tĩnh/dựa trên quy tắc nội bộ.
- Real wallet money movement, deposits, withdrawals, peer-to-peer transfers.
- Double-entry ledger hoặc sổ cái kép production.
- Cơ chế Auth JWT phức tạp hoặc user management.
- Real payment integration hoặc production compliance.

---

## 📂 3. Repository Architecture Rules
Tuân thủ cấu trúc thư mục:
- `app/modules/`: Chứa router, service, repository và schema cho từng miền API:
  - `transactions/`: Đọc giao dịch PaySim.
  - `risk/`: Đọc kết quả ML prediction và định nghĩa quy tắc rủi ro.
  - `analytics/`: Thống kê phân tích.
  - `agents/`: Senior Risk Investigation Agent.
- `pipelines/`: Chứa các script pipeline ML/ETL độc lập tuần tự: `ingestion/`, `processing/`, `training/`, `inference/`.
- `scripts/`: Chứa các script điều phối (`run_pipeline.py`) và nạp dữ liệu MongoDB (`seed_sample_data.py`, `import_transactions_to_mongo.py`).
- `data/sample/`: Chứa file `paysim_sample.csv` (10 dòng) để phục vụ test nhanh không cần tải dữ liệu Kaggle khổng lồ.
- `reports/`: Chứa các báo cáo phân tích tự động dưới dạng Markdown (`data_profile.md`, `model_report.md`).
- `models/`: Lưu trữ artifact mô hình máy học.

> [!NOTE]
> Không còn thư mục legacy nào (`users/`, `wallets/`, `ledger/`). Chúng đã được xóa hoàn toàn khỏi codebase.

---

## ⚖️ 4. Business & Risk Mapping Rules
Các quy định về phân loại rủi ro của dự án:
- **Fraud Probability to Risk Level**:
  - `fraud_probability < 0.3` => `LOW`
  - `0.3 <= fraud_probability < 0.7` => `MEDIUM`
  - `fraud_probability >= 0.7` => `HIGH`
- **Risk Level to System Action**:
  - `LOW` => `APPROVE` (Tự động duyệt)
  - `MEDIUM` => `MANUAL_REVIEW` (Cần kiểm tra thủ công)
  - `HIGH` => `BLOCK` (Khóa giao dịch ngay lập tức)

---

## 🧪 5. Testing & Validation Rules
- Mọi chức năng mới hoặc sửa đổi bắt buộc phải được kiểm thử đầy đủ bằng `pytest`.
- Không thiết kế test phụ thuộc vào việc kết nối tới Kaggle thật hoặc cơ sở dữ liệu cloud remote. Sử dụng dữ liệu mẫu `data/sample/paysim_sample.csv` và mock database nếu cần.
- Chạy lệnh kiểm thử trước khi kết thúc task:
  ```bash
  pytest
  ```

---

## 💬 6. Communication with Repository Owner
- Chủ sở hữu dự án đang trong quá trình học tập về Fintech và kiến trúc hệ thống backend.
- **Ngôn ngữ giao tiếp mặc định**: Tiếng Việt đơn giản, dễ hiểu, kết hợp các thuật ngữ kỹ thuật tiếng Anh ngắn gọn (ví dụ: *pipeline*, *feature engineering*, *inference*, *agent*).
- Sử dụng các ví dụ trực quan như:
  - Giao dịch chuyển khoản 1,000,000 VND từ tài khoản A sang B.
  - Số dư tài khoản gửi bị rút sạch về 0.0 sau giao dịch.
  - Mô hình AI dự đoán xác suất gian lận 95% dẫn đến hành động BLOCK giao dịch.
- Tránh giả vờ rằng các phần code chưa hoàn thiện là đã xong. Luôn trung thực và đề xuất bước đi tiếp theo cụ thể.
