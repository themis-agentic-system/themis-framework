"""Middleware for request logging, auditing, and monitoring."""

from __future__ import annotations

import time
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from api.logging_config import (
    get_audit_logger,
    get_performance_logger,
    get_request_logger,
)

request_logger = get_request_logger()
audit_logger = get_audit_logger()
performance_logger = get_performance_logger()

# Maximum request body size (10MB by default)
MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB in bytes


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.request_count = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        self.request_count += 1
        request_id = f"req-{self.request_count}"

        # Extract request info
        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        # Log incoming request
        request_logger.info(
            f"[{request_id}] {method} {path} | client={client_ip}"
        )

        # Track request duration
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log response
        status_code = response.status_code
        level = "info" if status_code < 400 else "error" if status_code < 500 else "critical"

        log_message = (
            f"[{request_id}] {method} {path} | "
            f"status={status_code} | duration={duration_ms:.2f}ms | client={client_ip}"
        )

        getattr(request_logger, level)(log_message)

        # Log performance metrics for slow requests
        if duration_ms > 1000:  # Requests > 1 second
            performance_logger.warning(
                f"Slow request: {method} {path} | "
                f"duration={duration_ms:.2f}ms | client={client_ip}"
            )

        # Add custom headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

        return response


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log security-relevant events."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log security audit events."""
        # Extract authentication info - sanitize to prevent credential leakage
        auth_header = request.headers.get("authorization", "")
        # Sanitize auth header for logging (only log type, not credentials)
        auth_type = auth_header.split()[0] if auth_header else "none"

        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        # Process request
        response = await call_next(request)

        # Log authentication attempts
        if path.startswith("/orchestrator"):
            status_code = response.status_code

            if status_code == 401:
                audit_logger.warning(
                    f"Authentication failed: {method} {path} | "
                    f"client={client_ip} | auth_type={auth_type}"
                )
            elif status_code == 429:
                audit_logger.warning(
                    f"Rate limit exceeded: {method} {path} | client={client_ip}"
                )
            elif status_code == 200 and method in ["POST", "DELETE"]:
                audit_logger.info(
                    f"Authorized action: {method} {path} | client={client_ip}"
                )

        return response


class CostTrackingMiddleware(BaseHTTPMiddleware):
    """Middleware to track estimated LLM costs."""

    # Approximate token costs (per 1M tokens) for Claude 3.5 Sonnet
    INPUT_COST_PER_MILLION = 3.00  # $3 per 1M input tokens
    OUTPUT_COST_PER_MILLION = 15.00  # $15 per 1M output tokens

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.total_estimated_cost = 0.0
        self.request_count = 0

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Track estimated costs for LLM operations."""
        # Process request
        response = await call_next(request)

        # Track costs for execute endpoint (which calls LLMs)
        if request.url.path == "/orchestrator/execute" and response.status_code == 200:
            self.request_count += 1

            # Rough estimation: Each execution involves ~3 agents with ~2 LLM calls each
            # Average input: ~1000 tokens, Average output: ~500 tokens per call
            estimated_input_tokens = 6 * 1000  # 6 calls * 1000 tokens
            estimated_output_tokens = 6 * 500  # 6 calls * 500 tokens

            estimated_cost = (
                (estimated_input_tokens / 1_000_000) * self.INPUT_COST_PER_MILLION +
                (estimated_output_tokens / 1_000_000) * self.OUTPUT_COST_PER_MILLION
            )

            self.total_estimated_cost += estimated_cost

            performance_logger.info(
                f"Execution completed | "
                f"estimated_cost=${estimated_cost:.4f} | "
                f"total_cost=${self.total_estimated_cost:.2f} | "
                f"total_executions={self.request_count}"
            )

        return response


class PayloadSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce maximum request payload size for DoS prevention."""

    def __init__(self, app: ASGIApp, max_size: int = MAX_REQUEST_SIZE):
        super().__init__(app)
        self.max_size = max_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Enforce maximum payload size."""
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")

        if content_length:
            try:
                content_length_int = int(content_length)
                if content_length_int > self.max_size:
                    audit_logger.warning(
                        f"Request payload too large: {content_length_int} bytes "
                        f"(max: {self.max_size} bytes) | "
                        f"client={request.client.host if request.client else 'unknown'} | "
                        f"path={request.url.path}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Request payload too large. Maximum size: {self.max_size} bytes ({self.max_size // (1024 * 1024)}MB)",
                    )
            except ValueError:
                # Invalid Content-Length header
                audit_logger.warning(
                    f"Invalid Content-Length header: {content_length} | "
                    f"client={request.client.host if request.client else 'unknown'}"
                )

        # Process request
        return await call_next(request)
