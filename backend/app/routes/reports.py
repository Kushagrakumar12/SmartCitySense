"""
Report Routes
Endpoints for user-submitted reports
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from typing import Optional, Dict, Any, List
import json

from app.models.report import (
    Report, ReportCreate, ReportResponse, ReportListResponse
)
from app.models.common import SuccessResponse
from app.utils.auth_middleware import get_current_user, get_optional_user
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_report(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(""),
    photos: List[UploadFile] = File(default=[]),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """
    Submit a new citizen report with optional photo uploads
    
    Allows users to submit reports about events they observe.
    Reports can include:
    - Text description
    - Multiple photos (up to 5, max 5MB each)
    - Geo-location
    - Category
    
    The system will automatically:
    - Store uploaded images
    - Analyze images with AI vision model
    - Perform sentiment analysis
    - Suggest event categorization
    - Convert high-confidence reports to events
    """
    try:
        # Handle file uploads if any
        media_urls = []
        if photos:
            for photo in photos:
                # Validate file type
                if not photo.content_type or not photo.content_type.startswith('image/'):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File {photo.filename} is not an image"
                    )
                
                # Read file content
                content = await photo.read()
                
                # Validate file size (5MB max)
                if len(content) > 5 * 1024 * 1024:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"File {photo.filename} is too large (max 5MB)"
                    )
                
                # TODO: Upload to Firebase Storage or other cloud storage
                # For now, we'll store a placeholder
                # In production, you'd upload to Firebase Storage and get a URL
                media_urls.append(f"placeholder://{photo.filename}")
        
        # Create report data
        from app.models.event import LocationData
        report_data = ReportCreate(
            title=title,
            description=description,
            category=category,
            location=LocationData(
                latitude=latitude,
                longitude=longitude,
                address=address
            ),
            media_urls=media_urls
        )
        
        # Get user ID if authenticated, otherwise use anonymous
        user_id = current_user['uid'] if current_user else 'anonymous'
        
        report = await report_service.create_report(report_data, user_id)
        
        return ReportResponse(
            report=report,
            message="Report submitted successfully. Thank you for keeping the city informed!"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit report: {str(e)}"
        )



@router.get("", response_model=ReportListResponse)
async def list_reports(
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List all reports
    
    Returns all reports in the system.
    """
    try:
        # Pass None for user_id to get all reports
        result = await report_service.list_reports(
            user_id=None,
            status=status,
            page=page,
            page_size=page_size
        )
        
        return ReportListResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list reports: {str(e)}"
        )


@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific report
    
    Returns detailed information about a single report.
    """
    try:
        report = await report_service.get_report(report_id)
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Verify user owns this report
        if report.reported_by != current_user['uid']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this report"
            )
        
        return ReportResponse(report=report)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get report: {str(e)}"
        )
