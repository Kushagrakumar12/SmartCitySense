"""
Common Response Models
Shared response models for API endpoints
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    timestamp: str
    services: Dict[str, str]


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool
