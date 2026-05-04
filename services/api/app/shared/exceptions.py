from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class MesException(HTTPException):
    error_code: str = "MES_ERROR"

    def __init__(self, detail: str | None = None):
        super().__init__(status_code=self.status_code, detail=detail or self.default_detail)

    status_code: int = 500
    default_detail: str = "서버 오류가 발생했습니다"


class NotFoundException(MesException):
    status_code = 404
    error_code = "NOT_FOUND"
    default_detail = "리소스를 찾을 수 없습니다"


class ValidationException(MesException):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    default_detail = "입력값이 올바르지 않습니다"


class UnauthorizedException(MesException):
    status_code = 401
    error_code = "UNAUTHORIZED"
    default_detail = "인증이 필요합니다"


class ForbiddenException(MesException):
    status_code = 403
    error_code = "FORBIDDEN"
    default_detail = "접근 권한이 없습니다"


class LotNotFoundException(NotFoundException):
    error_code = "LOT_NOT_FOUND"
    default_detail = "LOT를 찾을 수 없습니다"


class WorkOrderNotFoundException(NotFoundException):
    error_code = "WORK_ORDER_NOT_FOUND"
    default_detail = "생산지시를 찾을 수 없습니다"


class CcpDeviationException(MesException):
    status_code = 422
    error_code = "CCP_DEVIATION"
    default_detail = "CCP 기준값 이탈이 감지되었습니다"


class WorkOrderStatusException(MesException):
    status_code = 409
    error_code = "INVALID_STATUS_TRANSITION"
    default_detail = "작업지시 상태 전환이 유효하지 않습니다"


async def mes_exception_handler(request: Request, exc: MesException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
            }
        },
    )
