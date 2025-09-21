"""
Correlation ID management for request tracking across components.
"""
import uuid
from contextvars import ContextVar
from typing import Optional

# Context variable for storing correlation ID
correlation_id: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)

def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())[:8]

def set_correlation_id(corr_id: Optional[str] = None) -> str:
    """Set correlation ID for current context."""
    if corr_id is None:
        corr_id = generate_correlation_id()
    correlation_id.set(corr_id)
    return corr_id

def get_correlation_id() -> Optional[str]:
    """Get current correlation ID."""
    return correlation_id.get()

def log_with_correlation(logger, level: str, message: str, **kwargs):
    """Log message with correlation ID."""
    corr_id = get_correlation_id()
    extra = kwargs.get('extra', {})
    if corr_id:
        extra['correlation_id'] = corr_id
    kwargs['extra'] = extra

    getattr(logger, level)(f"[{corr_id or 'NO-ID'}] {message}", **kwargs)