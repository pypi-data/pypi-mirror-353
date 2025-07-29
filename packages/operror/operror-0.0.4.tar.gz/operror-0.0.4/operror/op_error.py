from typing import Any, Dict, Optional, Type, TypeVar

from operror.op_status import Case, Code, Status


class OpError(Exception):
    """Represents an operation error.
    
    Args:
        status: The status of the operation that raised this error.
        module: The module where this error occured.
    """

    _DEFAULT_MODULE = "none"
    
    def __init__(self, status: Status, module: Optional[str] = None):
        super().__init__(status)
        self._status = status
        self._module = module if module is not None and module.strip() else self._DEFAULT_MODULE
    
    @property
    def status(self) -> Status:
        return self._status
    
    @property
    def module(self) -> str:
        return self._module
        
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(module={self.module}, status={self.status})"

    def add_more_ctx_to_msg(self, more_ctx: str) -> None:
        """Augments the message of the status with more contextual information."""
        self.status.add_more_ctx_to_msg(more_ctx)

    # Factory functions for creating OpError instances

    @staticmethod
    def new_from_status(status: Status, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError with the given status."""
        return OpError(status=status, module=module)

    @staticmethod
    def new_op_cancelled(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for cancelled operation."""
        status = Status(Code.OP_CANCELLED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_unknown_error(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for unknown error."""
        status = Status(Code.UNKNOWN_ERROR).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_illegal_input(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for illegal input."""
        status = Status(Code.ILLEGAL_INPUT).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_timeout(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for timeout."""
        status = Status(Code.TIMEOUT).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_not_found(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for not found."""
        status = Status(Code.NOT_FOUND).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_already_exists(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for already exists."""
        status = Status(Code.ALREADY_EXISTS).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_permission_denied(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for permission denied."""
        status = Status(Code.PERMISSION_DENIED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_unauthenticated(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for unauthenticated."""
        status = Status(Code.UNAUTHENTICATED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_resource_exhausted(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for resource exhausted."""
        status = Status(Code.RESOURCE_EXHAUSTED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_failed_precondition(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for failed precondition."""
        status = Status(Code.FAILED_PRECONDITION).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_op_aborted(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for aborted."""
        status = Status(Code.OP_ABORTED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_out_of_range(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for out of range."""
        status = Status(Code.OUT_OF_RANGE).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_unimplemented(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for unimplemented."""
        status = Status(Code.UNIMPLEMENTED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_internal_error(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for internal error."""
        status = Status(Code.INTERNAL_ERROR).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_unavailable(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for unavailable."""
        status = Status(Code.UNAVAILABLE).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_data_corrupted(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for data corrupted."""
        status = Status(Code.DATA_CORRUPTED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_authorization_expired(message: str, case: Optional[Case] = None, details: Optional[Dict[str, Any]] = None, module: Optional[str] = None) -> 'OpError':
        """Creates an OpError for authorization expired."""
        status = Status(Code.AUTHORIZATION_EXPIRED).with_msg(message)
        if case is not None:
            status = status.with_case(case)
        if details is not None and details:
            status = status.with_details(details)
        return OpError(status, module)

    @staticmethod
    def new_from_http_resp(status_code: int, headers: Any = None, body: str = "") -> 'OpError':
        """Creates an OpError from an HTTP response."""
        return OpError(Status.new_from_http_resp(status_code, headers, body))

E = TypeVar('E', bound=OpError) # generic type represents subclass of OpError

class ErrorBuilder:
    def __init__(self, status: Status):
        self._status = status
        self._module = OpError._DEFAULT_MODULE

    def with_module(self, module: str) -> 'ErrorBuilder':
        module = module.strip()
        if not module:
            return self
        self._module = module
        return self

    def with_message(self, msg: str) -> 'ErrorBuilder':
        self._status = self._status.with_msg(msg)
        return self

    def with_case(self, case: Case) -> 'ErrorBuilder':
        self._status = self._status.with_case(case)
        return self

    def with_details(self, details: Dict[str, Any] = {}) -> 'ErrorBuilder':
        self._status = self._status.with_details(details)
        return self

    def build(self, cls: Type[E]=OpError, **kwargs: Any) -> E:
        if kwargs:
            details = {} if self._status.details is None else self._status.details
            details.update(kwargs)
            self._status = self._status.with_details(details)
        return cls(self._status, self._module)

    # Factory functions for creating ErrorBuilder instances
    
    @staticmethod
    def new_from_status(status: Status) -> 'ErrorBuilder':
        """Creates a new ErrorBuilder with the given status."""
        return ErrorBuilder(status=status)

    @staticmethod
    def new_op_cancelled() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for cancelled operation."""
        return ErrorBuilder(status=Status(Code.OP_CANCELLED))

    @staticmethod
    def new_unknown_error() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for unknown error."""
        return ErrorBuilder(status=Status(Code.UNKNOWN_ERROR))

    @staticmethod
    def new_illegal_input() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for illegal input."""
        return ErrorBuilder(status=Status(Code.ILLEGAL_INPUT))

    @staticmethod
    def new_timeout() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for timeout."""
        return ErrorBuilder(status=Status(Code.TIMEOUT))

    @staticmethod
    def new_not_found() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for not found."""
        return ErrorBuilder(status=Status(Code.NOT_FOUND))

    @staticmethod
    def new_already_exists() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for already exists."""
        return ErrorBuilder(status=Status(Code.ALREADY_EXISTS))

    @staticmethod
    def new_permission_denied() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for permission denied."""
        return ErrorBuilder(status=Status(Code.PERMISSION_DENIED))

    @staticmethod
    def new_unauthenticated() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for unauthenticated."""
        return ErrorBuilder(status=Status(Code.UNAUTHENTICATED))

    @staticmethod
    def new_resource_exhausted() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for resource exhausted."""
        return ErrorBuilder(status=Status(Code.RESOURCE_EXHAUSTED))

    @staticmethod 
    def new_failed_precondition() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for failed precondition."""
        return ErrorBuilder(status=Status(Code.FAILED_PRECONDITION))

    @staticmethod
    def new_op_aborted() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for aborted."""
        return ErrorBuilder(status=Status(Code.OP_ABORTED))

    @staticmethod
    def new_out_of_range() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for out of range."""
        return ErrorBuilder(status=Status(Code.OUT_OF_RANGE))

    @staticmethod
    def new_unimplemented() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for unimplemented."""
        return ErrorBuilder(status=Status(Code.UNIMPLEMENTED))

    @staticmethod
    def new_internal_error() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for internal error."""
        return ErrorBuilder(status=Status(Code.INTERNAL_ERROR))

    @staticmethod
    def new_unavailable() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for unavailable."""
        return ErrorBuilder(status=Status(Code.UNAVAILABLE))

    @staticmethod
    def new_data_corrupted() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for data corrupted."""
        return ErrorBuilder(status=Status(Code.DATA_CORRUPTED))

    @staticmethod
    def new_authorization_expired() -> 'ErrorBuilder':
        """Creates a new ErrorBuilder for authorization expired."""
        return ErrorBuilder(status=Status(Code.AUTHORIZATION_EXPIRED)) 

    @staticmethod
    def new_from_http_resp(status_code: int, headers: Any = None, body: str = "") -> 'ErrorBuilder':
        """Creates a new ErrorBuilder from an HTTP response."""
        return ErrorBuilder(status=Status.new_from_http_resp(status_code, headers, body))