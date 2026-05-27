from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_db
from app.modules.agents import service
from app.modules.agents.schema import RiskInvestigationReport
from app.common.response import success_response

router = APIRouter(prefix="/agents", tags=["Risk Investigation Agent"])

@router.get("/risk-investigator/{transaction_id}", response_model=None)
async def run_investigator_agent(
    transaction_id: str,
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Run the Risk Investigation Agent on a specific transaction ID.
    Synthesizes transaction data and AI predictions to compile a detailed fraud report.
    """
    report = await service.analyze_transaction_risk(db, transaction_id)
    return success_response(data=report, message="Risk investigation report compiled successfully by Agent")
