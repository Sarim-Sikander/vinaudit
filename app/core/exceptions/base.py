from http import HTTPStatus


class APIException(Exception):
    status_code: int
    code: str
    msg: str
    detail: str
    ex: Exception

    def __init__(
        self,
        *,
        status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR,
        code: str = "000000",
        msg: str = None,
        detail: str = None,
        ex: Exception = None,
    ):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.detail = detail
        self.ex = ex
        super().__init__(ex)


class NotFoundException(APIException):
    def __init__(self, custom_msg: str = None, ex: Exception = None):
        default_msg = HTTPStatus.NOT_FOUND.description
        detail_msg = f"{custom_msg}" if custom_msg else default_msg

        super().__init__(
            status_code=HTTPStatus.NOT_FOUND,
            msg=HTTPStatus.NOT_FOUND.description,
            detail=detail_msg,
            code=f"{HTTPStatus.NOT_FOUND}{'1'.zfill(4)}",
            ex=ex,
        )
