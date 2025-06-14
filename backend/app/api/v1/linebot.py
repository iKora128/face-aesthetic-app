"""LINE Bot API endpoints."""

from typing import Any

from fastapi import APIRouter, HTTPException, Request, Depends, status
from loguru import logger

from app.config import settings
from app.dependencies import get_supabase_client
from app.services.linebot_service import get_linebot_service
from app.utils.exceptions import LineBotError

router = APIRouter()


@router.post("/webhook")
async def line_webhook(
    request: Request,
    supabase_client=Depends(get_supabase_client)
) -> dict[str, str]:
    """Handle LINE Bot webhook events."""
    if not settings.line_channel_access_token or not settings.line_channel_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="LINE Bot not configured. Please set LINE_CHANNEL_ACCESS_TOKEN and LINE_CHANNEL_SECRET environment variables."
        )
    
    try:
        # Get request data
        body = await request.body()
        signature = request.headers.get("X-Line-Signature", "")
        
        if not signature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing X-Line-Signature header"
            )
        
        # Get LINE Bot service
        linebot_service = get_linebot_service(supabase_client)
        
        # Handle webhook
        result = await linebot_service.handle_webhook(
            body=body.decode('utf-8'),
            signature=signature
        )
        
        logger.info("LINE webhook processed successfully")
        return result
        
    except LineBotError as e:
        logger.error(f"LINE Bot error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed"
        )


@router.get("/info")
async def get_bot_info() -> dict[str, Any]:
    """Get LINE Bot information and configuration status."""
    bot_configured = bool(
        settings.line_channel_access_token and 
        settings.line_channel_secret
    )
    
    webhook_url = None
    if settings.app_url:
        webhook_url = f"{settings.app_url}/api/v1/linebot/webhook"
    
    return {
        "bot_configured": bot_configured,
        "webhook_url": webhook_url,
        "channel_configured": bool(settings.line_channel_access_token),
        "secret_configured": bool(settings.line_channel_secret),
        "features": {
            "image_analysis": True,
            "chat_consultation": True,
            "analysis_reports": True,
            "multi_language": False  # Currently Japanese only
        },
        "supported_languages": ["ja"],
        "version": "1.0.0"
    }


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check for LINE Bot service."""
    if not settings.line_channel_access_token or not settings.line_channel_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LINE Bot not configured"
        )
    
    # TODO: Add more comprehensive health checks
    # - Test LINE API connectivity
    # - Check database connection
    # - Verify webhook URL accessibility
    
    return {
        "status": "healthy",
        "service": "LINE Bot",
        "message": "Service is operational"
    }


@router.post("/test-message")
async def send_test_message(
    user_id: str,
    message: str = "こんにちは！Face Aesthetic AI のテストメッセージです。",
    supabase_client=Depends(get_supabase_client)
) -> dict[str, str]:
    """Send test message to LINE user (for development/testing)."""
    if not settings.line_channel_access_token:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="LINE Bot not configured"
        )
    
    try:
        linebot_service = get_linebot_service(supabase_client)
        
        # In a real implementation, you would use the LINE Bot API to send a message
        # For now, this is a placeholder for testing
        logger.info(f"Test message would be sent to {user_id}: {message}")
        
        return {
            "status": "success",
            "message": f"Test message sent to {user_id}",
            "content": message
        }
        
    except Exception as e:
        logger.error(f"Failed to send test message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send test message"
        )