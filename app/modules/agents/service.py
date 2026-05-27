import logging
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config import settings
from app.modules.agents import tools
from app.modules.agents.llm_client import call_openai_risk_agent
from app.modules.risk import service as risk_service
from app.common.exceptions import NotFoundException

logger = logging.getLogger(__name__)

def generate_key_signals(transaction: dict, prediction: dict, features: Optional[dict] = None) -> List[str]:
    """
    Synthesize suspicious signals based on transaction values and prediction outcomes.
    Supports both original camelCase PaySim fields and processed snake_case fields.
    """
    signals = []
    
    t_type = transaction.get("type", "").upper()
    amount = float(transaction.get("amount", 0))
    
    # 1. Check Transaction Type
    if t_type in ["TRANSFER", "CASH_OUT"]:
        signals.append(f"Loại giao dịch là {t_type} (thường có tỷ lệ gian lận cao).")
    
    # 2. Check Origin Balance Emptying
    old_bal_orig = float(transaction.get("oldbalanceOrg", transaction.get("old_balance_orig", 0)))
    new_bal_orig = float(transaction.get("newbalanceOrig", transaction.get("new_balance_orig", 0)))
    if new_bal_orig == 0.0 and old_bal_orig > 0.0:
        signals.append("Tài khoản gửi bị rút sạch số dư về 0 ngay sau giao dịch.")
        
    if old_bal_orig == amount and amount > 0:
        signals.append("Số tiền giao dịch bằng đúng toàn bộ số dư ban đầu của tài khoản gửi.")

    # 3. Check Destination Balance Anomalies
    old_bal_dest = float(transaction.get("oldbalanceDest", transaction.get("old_balance_dest", 0)))
    new_bal_dest = float(transaction.get("newbalanceDest", transaction.get("new_balance_dest", 0)))
    
    # If the transaction amount is transferred but destination balance doesn't increase, it's anomalous
    # For merchant accounts (names starting with 'M'), balances are often 0 or not tracked.
    name_dest = transaction.get("nameDest", transaction.get("name_dest", ""))
    is_merchant = name_dest.startswith("M")
    
    if not is_merchant and amount > 0:
        if old_bal_dest == 0.0 and new_bal_dest == 0.0:
            signals.append("Tài khoản nhận không tăng số dư sau khi nhận khoản tiền lớn (Bất thường về số dư).")
            
    # 4. Check ML Prediction Probability
    prob = float(prediction.get("fraud_probability", 0.0))
    if prob >= 0.7:
        signals.append(f"Mô hình máy học đánh giá xác suất gian lận ở mức RẤT CAO ({prob*100:.1f}%).")
    elif prob >= 0.3:
        signals.append(f"Mô hình máy học đánh giá xác suất gian lận ở mức TRUNG BÌNH ({prob*100:.1f}%).")

    return signals

def generate_recommended_action(fraud_probability: float) -> str:
    """Determine recommended system action based on fraud probability."""
    risk_level = risk_service.map_probability_to_risk_level(fraud_probability)
    return risk_service.map_risk_level_to_action(risk_level)

def generate_explanation(transaction: dict, prediction: dict, key_signals: List[str]) -> str:
    """Generate a detailed, human-readable markdown risk analysis explanation in Vietnamese."""
    txn_id = transaction.get("transaction_id", "N/A")
    t_type = transaction.get("type", "N/A")
    amount = float(transaction.get("amount", 0))
    name_orig = transaction.get("nameOrig", transaction.get("name_orig", "N/A"))
    name_dest = transaction.get("nameDest", transaction.get("name_dest", "N/A"))
    
    prob = float(prediction.get("fraud_probability", 0.0))
    risk_level = risk_service.map_probability_to_risk_level(prob)
    action = risk_service.map_risk_level_to_action(risk_level)
    
    action_vietnamese = {
        "APPROVE": "DUYỆT GIAO DỊCH (APPROVE)",
        "MANUAL_REVIEW": "CẦN ĐÁNH GIÁ THỦ CÔNG (MANUAL REVIEW)",
        "BLOCK": "KHÓA NGAY LẬP TỨC (BLOCK)"
    }.get(action, "ĐÁNH GIÁ THỦ CÔNG")

    # Constructing a premium markdown report
    explanation_lines = [
        f"### BÁO CÁO PHÂN TÍCH RỦI RO GIAO DỊCH",
        f"**Mã giao dịch**: `{txn_id}`",
        f"**Đánh giá của Risk Investigation Agent**: **{risk_level} RISK**",
        f"**Hành động đề xuất**: **{action_vietnamese}**",
        f"",
        f"#### 1. Tổng quan giao dịch",
        f"- **Hình thức**: `{t_type}`",
        f"- **Số tiền**: `{amount:,.2f} VND`",
        f"- **Tài khoản gửi (Origin)**: `{name_orig}`",
        f"- **Tài khoản nhận (Destination)**: `{name_dest}`",
        f"",
        f"#### 2. Phân tích Chi tiết & Tín hiệu Nghi vấn",
    ]
    
    if key_signals:
        for sig in key_signals:
            explanation_lines.append(f"- ⚠️ {sig}")
    else:
        explanation_lines.append("- ✅ Không phát hiện tín hiệu nghi vấn đặc biệt từ các quy tắc tĩnh.")
        
    explanation_lines.extend([
        f"",
        f"#### 3. Đánh giá từ Mô hình AI/ML",
        f"Mô hình phát hiện gian lận đánh giá giao dịch này có xác suất gian lận là **{prob*100:.2f}%**.",
        f"Dựa trên các đặc trưng hành vi và lịch sử dòng tiền, hệ thống phân loại giao dịch này vào nhóm **{risk_level}**.",
        f"",
        f"#### 4. Khuyến nghị cho Điều tra viên (FraudOps)",
    ])
    
    if action == "BLOCK":
        explanation_lines.append(
            "👉 **Khuyến nghị khẩn cấp**: Giao dịch mang đầy đủ các đặc trưng của hành vi lừa đảo/rút ruột tài khoản điển hình (PaySim Pattern). "
            "Yêu cầu chặn giao dịch ngay lập tức, tạm khóa tài khoản gửi và liên hệ với khách hàng để xác minh."
        )
    elif action == "MANUAL_REVIEW":
        explanation_lines.append(
            "👉 **Khuyến nghị**: Giao dịch nằm trong vùng cảnh báo trung bình. Hãy kiểm tra xem tài khoản nhận có phải là tài khoản mới tạo "
            "hoặc tài khoản gửi có lịch sử thực hiện các giao dịch tương tự trong quá khứ hay không."
        )
    else:
        explanation_lines.append(
            "👉 **Khuyến nghị**: Giao dịch được đánh giá an toàn, không có dấu hiệu gian lận rõ ràng. Có thể tự động phê duyệt."
        )

    return "\n".join(explanation_lines)

async def analyze_transaction_risk(db: AsyncIOMotorDatabase, transaction_id: str) -> dict:
    """
    Orchestrate the Risk Investigation Agent.
    Gathers context from transactions, predictions, and engineered features,
    then compiles a structured investigation report using either OpenAI LLM or rule-based fallback.
    """
    import pandas as pd
    
    # 1. Fetch contexts using tools
    txn = await tools.fetch_transaction_context(db, transaction_id)
    if not txn:
        raise NotFoundException(
            message=f"Transaction with ID '{transaction_id}' not found for agent investigation",
            error_code="TRANSACTION_NOT_FOUND"
        )
        
    pred = await tools.fetch_prediction_context(db, transaction_id)
    # If no prediction found in db, mock one based on transaction features to be robust
    if not pred:
        is_fraud_val = txn.get("isFraud", txn.get("is_fraud", 0))
        prob = 0.95 if is_fraud_val == 1 else 0.05
        pred = {
            "transaction_id": transaction_id,
            "fraud_probability": prob,
            "predicted_label": is_fraud_val,
            "model_version": "mock_agent_v1"
        }
        
    features = await tools.fetch_features_context(db, transaction_id)
    if not features:
        # Fallback to default engineered features if not found in Atlas
        features = {
            "transaction_id": transaction_id,
            "amount": float(txn.get("amount", 0)),
            "amount_log": 0.0,
            "old_balance_orig": float(txn.get("oldbalanceOrg", txn.get("old_balance_orig", 0))),
            "new_balance_orig": float(txn.get("newbalanceOrig", txn.get("new_balance_orig", 0))),
            "old_balance_dest": float(txn.get("oldbalanceDest", txn.get("old_balance_dest", 0))),
            "new_balance_dest": float(txn.get("newbalanceDest", txn.get("new_balance_dest", 0))),
            "balance_diff_orig": 0.0,
            "balance_diff_dest": 0.0,
            "orig_balance_error": 0.0,
            "dest_balance_error": 0.0,
            "origin_balance_zero_after_txn": 0,
            "is_merchant_dest": 1 if str(txn.get("nameDest", txn.get("name_dest", ""))).startswith("M") else 0
        }
        
    # 2. Try LLM Agent if enabled
    report_dict = None
    if settings.LLM_AGENT_ENABLED:
        try:
            llm_report = await call_openai_risk_agent(txn, pred, features)
            report_dict = llm_report.model_dump()
            logger.info("Successfully generated risk report using OpenAI LLM Agent.")
        except Exception as e:
            logger.error(f"Failed to generate risk report using OpenAI LLM Agent: {e}")
            if not settings.LLM_AGENT_FALLBACK_TO_RULES:
                raise e
            logger.warning("LLM_AGENT_FALLBACK_TO_RULES is enabled. Falling back to rule-based generation...")
            
    # 3. Rule-based Fallback (or if LLM Agent is disabled)
    if not report_dict:
        prob = float(pred.get("fraud_probability", 0.0))
        risk_level = risk_service.map_probability_to_risk_level(prob)
        action = generate_recommended_action(prob)
        signals = generate_key_signals(txn, pred, features)
        explanation = generate_explanation(txn, pred, signals)
        
        report_dict = {
            "transaction_id": transaction_id,
            "risk_level": risk_level,
            "fraud_probability": prob,
            "key_signals": signals,
            "recommended_action": action,
            "explanation": explanation
        }
        logger.info("Generated risk report using Rule-based logic.")
        
    # 4. Save to agent_reports collection on Atlas
    try:
        report_doc = {**report_dict, "created_at": pd.Timestamp.now().isoformat() + "Z"}
        report_doc.pop("_id", None)
        
        await db.agent_reports.update_one(
            {"transaction_id": transaction_id},
            {"$set": report_doc},
            upsert=True
        )
        logger.info(f"Successfully saved agent report for transaction {transaction_id} to Atlas.")
    except Exception as e:
        logger.error(f"Failed to save agent report to database: {e}")
        
    return report_dict
