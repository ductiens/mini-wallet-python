import logging
import json
from openai import AsyncOpenAI
from app.config import settings
from app.modules.agents.prompts import RISK_INVESTIGATION_AGENT_PROMPT
from app.modules.agents.schema import RiskInvestigationReport

logger = logging.getLogger(__name__)

async def call_openai_risk_agent(
    transaction: dict, 
    prediction: dict, 
    features: dict
) -> RiskInvestigationReport:
    """
    Call OpenAI Chat Completions API with Structured Outputs to analyze a transaction.
    """
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
        raise ValueError("OpenAI API Key is not configured.")
        
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    # Pre-process details for prompt readability (removing mongo db _id fields if present)
    clean_txn = {k: v for k, v in transaction.items() if k != "_id"}
    clean_pred = {k: v for k, v in prediction.items() if k != "_id"}
    clean_feat = {k: v for k, v in features.items() if k != "_id"}
    
    # Construct a comprehensive prompt with all available context
    user_content = f"""
Hãy đóng vai trò là Senior Risk Investigation Agent. Phân tích giao dịch rủi ro dựa trên thông tin giao dịch mẫu, dự đoán của mô hình và các đặc trưng kỹ nghệ.

### 1. THÔNG TIN GIAO DỊCH (TRANSACTION DATA)
{json.dumps(clean_txn, indent=2, ensure_ascii=False)}

### 2. DỰ ĐOÁN MÁY HỌC (AI PREDICTION)
{json.dumps(clean_pred, indent=2, ensure_ascii=False)}

### 3. ĐẶC TRƯNG KỸ NGHỆ (ENGINEERED FEATURES)
{json.dumps(clean_feat, indent=2, ensure_ascii=False)}

### Yêu cầu đầu ra:
Trả về phản hồi JSON có cấu trúc chính xác theo schema `RiskInvestigationReport`:
1. `transaction_id`: Khớp chính xác ID giao dịch trên (`{clean_txn.get('transaction_id')}`).
2. `risk_level`: Phải là "LOW", "MEDIUM", hoặc "HIGH" khớp với phân loại từ AI/ML score.
3. `fraud_probability`: Xác suất gian lận từ prediction.
4. `key_signals`: Phân tích và sinh ít nhất 3 tín hiệu nghi vấn/rủi ro hành vi bằng Tiếng Việt.
5. `recommended_action`: Hành động đề xuất ("APPROVE", "MANUAL_REVIEW", hoặc "BLOCK").
6. `explanation`: Báo cáo phân tích chi tiết và lập luận thuyết phục bằng định dạng Markdown (Tiếng Việt) dành cho các điều tra viên gian lận (FraudOps). Viết báo cáo chất lượng cao và phân tích cụ thể các sai sót về số dư hoặc hành vi.
"""

    logger.info(f"Sending LLM Agent request to OpenAI model '{settings.OPENAI_MODEL}' for transaction {clean_txn.get('transaction_id')}...")
    
    response = await client.beta.chat.completions.parse(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": RISK_INVESTIGATION_AGENT_PROMPT},
            {"role": "user", "content": user_content}
        ],
        response_format=RiskInvestigationReport
    )
    
    parsed_report = response.choices[0].message.parsed
    if not parsed_report:
        raise ValueError("Failed to parse structured output from OpenAI.")
        
    logger.info("Successfully received structured investigation report from OpenAI.")
    return parsed_report
