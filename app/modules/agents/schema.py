from pydantic import BaseModel, Field
from typing import List

class RiskInvestigationReport(BaseModel):
    """Schema representing the structured investigation report compiled by the Agent."""
    transaction_id: str = Field(..., description="The transaction ID evaluated")
    risk_level: str = Field(..., description="Evaluated risk level (LOW, MEDIUM, HIGH)")
    fraud_probability: float = Field(..., description="Estimated probability of fraud from prediction models")
    key_signals: List[str] = Field(..., description="List of synthesized warning signals identified in the transaction")
    recommended_action: str = Field(..., description="System action recommended (APPROVE, MANUAL_REVIEW, BLOCK)")
    explanation: str = Field(..., description="A detailed markdown summary analyzing why the transaction is classified as such")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "018fc1a3-2d2c-7b0a-8bf8-d3f3e2b2a1a0",
                "risk_level": "HIGH",
                "fraud_probability": 0.91,
                "key_signals": [
                    "Transaction type is TRANSFER.",
                    "Sender balance becomes zero after transaction.",
                    "The model assigned a high fraud probability."
                ],
                "recommended_action": "BLOCK",
                "explanation": "### Giao dịch đáng ngờ\n\nPhát hiện giao dịch chuyển khoản trị giá **1,000,000 VND** từ tài khoản **C200000001** sang **C200000002**.\n\n**Tín hiệu cảnh báo:**\n- Loại giao dịch `TRANSFER` có tỉ lệ rủi ro cao trong tập dữ liệu PaySim.\n- Số dư người gửi bị rút cạn sạch về `0.0` ngay sau giao dịch.\n- Mô hình máy học đánh giá xác suất gian lận cực cao (`91%`).\n\n**Đề xuất:** Khóa giao dịch này ngay lập tức (`BLOCK`) để điều tra thêm."
            }
        }
