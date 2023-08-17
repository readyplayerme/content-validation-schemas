"""Custom reusable validators."""

from collections.abc import Callable
from typing import Any, TypeAlias

from pydantic import (
    FieldValidationInfo,
    ValidationError,
    ValidatorFunctionWrapHandler,
)
from pydantic_core import ErrorDetails, PydanticCustomError

# Make a TypeAlias for the inner function signature
ErrorMsgReturnType: TypeAlias = tuple[str, str] | tuple[None, None]
GetErrorMsgFunc: TypeAlias = Callable[[str, ErrorDetails], ErrorMsgReturnType]  # input: field_name, error_details


class CustomValidator:
    """Provides a wrapper-function for validators to raise custom error types and messages.

    The purpose of this class is to reuse its custom_error_validator method to wrap validations for different fields.
    To raise a custom pydantic error, the class needs to be instantiated with a function that takes the field name
    and error details as input, and returns a tuple of (error_type: str, error_msg: str).

    Usage:
        def error_msg_func(field_name: str, error_details: ErrorDetails) -> ErrorMsgReturnType:
            if field_name == "a":
                return "MyCustomErrorType", f"A custom error message. Wrong value: {error_details['value']}"
            return None, None  # Makes custom_error_validator raise the original error!

        class MyModel(BaseModel):
            a: int
            b: str

            val_wrap = field_validator("*", mode="wrap")(CustomValidator(error_msg_func).custom_error_validator)
    """

    def __init__(self, error_msg_fn: GetErrorMsgFunc):
        self._get_error_msg = error_msg_fn

    def custom_error_validator(
        self, value: Any, handler: ValidatorFunctionWrapHandler, info: FieldValidationInfo
    ) -> Any:
        """Wrap a validator function to raise a custom error type and message.

        If error type and message returned by the error message func evaluate to False, the original error is raised.
        """
        try:
            return handler(value)
        except ValidationError as error:
            for err in error.errors():
                error_type, error_msg = self._get_error_msg(info.field_name, err)
                if error_type and error_msg:
                    raise PydanticCustomError(error_type, error_msg) from error
                raise  # We didn't cover this error, so raise the original error.
