import json
from datetime import datetime, timezone
import pytest
from fastapi.responses import JSONResponse

from app.common.constants import (
    PaySimTransactionType,
    RiskLevel,
    RecommendedAction,
    ModelVersion,
)
from app.common.exceptions import (
    AppException,
    NotFoundException,
    BadRequestException,
    DuplicateRequestException,
)
from app.common.response import success_response, error_response
from app.common.utils import (
    generate_id,
    now_utc,
)


def test_constants():
    # PaySimTransactionType
    assert PaySimTransactionType.TRANSFER == "TRANSFER"
    assert PaySimTransactionType.CASH_OUT == "CASH_OUT"
    assert PaySimTransactionType.CASH_IN == "CASH_IN"
    assert PaySimTransactionType.PAYMENT == "PAYMENT"
    assert PaySimTransactionType.DEBIT == "DEBIT"

    # RiskLevel
    assert RiskLevel.LOW == "LOW"
    assert RiskLevel.MEDIUM == "MEDIUM"
    assert RiskLevel.HIGH == "HIGH"

    # RecommendedAction
    assert RecommendedAction.APPROVE == "APPROVE"
    assert RecommendedAction.MANUAL_REVIEW == "MANUAL_REVIEW"
    assert RecommendedAction.BLOCK == "BLOCK"

    # ModelVersion
    assert ModelVersion.V1 == "v1.0.0"


def test_exceptions():
    # Base AppException
    exc = AppException("Base error", error_code="BASE_ERR", status_code=500, details={"info": "test"})
    assert exc.message == "Base error"
    assert exc.error_code == "BASE_ERR"
    assert exc.status_code == 500
    assert exc.details == {"info": "test"}

    # NotFoundException
    exc_nf = NotFoundException("Transaction not found", details={"transaction_id": "123"})
    assert exc_nf.message == "Transaction not found"
    assert exc_nf.error_code == "RESOURCE_NOT_FOUND"
    assert exc_nf.status_code == 404
    assert exc_nf.details == {"transaction_id": "123"}

    # BadRequestException
    exc_br = BadRequestException("Invalid transaction type")
    assert exc_br.message == "Invalid transaction type"
    assert exc_br.error_code == "BAD_REQUEST"
    assert exc_br.status_code == 400

    # DuplicateRequestException
    exc_dr = DuplicateRequestException("Prediction already exists")
    assert exc_dr.message == "Prediction already exists"
    assert exc_dr.error_code == "DUPLICATE_REQUEST"
    assert exc_dr.status_code == 409


def test_response_helpers():
    # success_response
    res_success = success_response(data={"id": "xyz"}, message="Created successfully", status_code=201)
    assert isinstance(res_success, JSONResponse)
    assert res_success.status_code == 201
    
    body_success = json.loads(res_success.body)
    assert body_success["success"] is True
    assert body_success["message"] == "Created successfully"
    assert body_success["data"] == {"id": "xyz"}

    # error_response
    res_error = error_response(message="Invalid format", error_code="VALIDATION_FAILED", status_code=422, details={"field": "amount"})
    assert isinstance(res_error, JSONResponse)
    assert res_error.status_code == 422
    
    body_error = json.loads(res_error.body)
    assert body_error["success"] is False
    assert body_error["error_code"] == "VALIDATION_FAILED"
    assert body_error["message"] == "Invalid format"
    assert body_error["details"] == {"field": "amount"}


def test_utils_generate_id():
    uuid_str1 = generate_id()
    uuid_str2 = generate_id()
    
    assert isinstance(uuid_str1, str)
    assert len(uuid_str1) == 36
    assert uuid_str1 != uuid_str2
    
    # Check simple UUID structure
    parts = uuid_str1.split("-")
    assert len(parts) == 5
    assert all(len(part) > 0 for part in parts)


def test_utils_now_utc():
    t = now_utc()
    assert isinstance(t, datetime)
    assert t.tzinfo == timezone.utc
    
    # Verify it is close to current time
    t2 = datetime.now(timezone.utc)
    delta = t2 - t
    assert abs(delta.total_seconds()) < 5.0
