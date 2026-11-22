"""Domain errors raised by services.

Services don't know about HTTP. They raise these, and one handler in main.py
turns them into JSON responses with the right status code.
"""


class AppError(Exception):
    status_code: int = 400

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class AuthenticationError(AppError):
    status_code = 401
