from typing import Any, Dict, Generic, Optional, TypeVar
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar("T")


class Metadata(BaseModel):
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))
    requestId: str = Field(default_factory=lambda: f"req_{uuid4().hex[:6]}")


class ErrorDetail(BaseModel):
    code: str
    message: str
    target: Optional[str] = None
    source: Optional[str] = None


class APIResponse(GenericModel, Generic[T]):
    data: Optional[T] = None
    metadata: Metadata = Field(default_factory=Metadata)


class ErrorResponse(BaseModel):
    error: ErrorDetail
    requestId: str = Field(default_factory=lambda: f"req_{uuid4().hex[:6]}")
    timestamp: int = Field(default_factory=lambda: int(datetime.now().timestamp() * 1000))


class IResponseBase(GenericModel, Generic[T]):  # type: ignore
    message: str = ""
    meta: Optional[Dict[str, Any]] = {}
    data: Optional[T] = None


class IGetResponseBase(IResponseBase[T], Generic[T]):
    message: str = "Data got correctly"
    data: Optional[T] = None


class IPostResponseBase(IResponseBase[T], Generic[T]):
    message: str = "Data created correctly"
