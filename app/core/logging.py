"""
Enhanced logging configuration with structured logging.
"""
import structlog
import logging
import sys
from typing import Any, Dict, Optional, List
from datetime import datetime
import uuid

from app.core.config import settings


def configure_logging():
    """Configure structured logging for the application."""
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level
            structlog.stdlib.add_log_level,
            # Add logger name
            structlog.stdlib.add_logger_name,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add stack info for errors
            structlog.processors.StackInfoRenderer(),
            # Format exception info
            structlog.processors.format_exc_info,
            # Ensure unicode
            structlog.processors.UnicodeDecoder(),
            # Add request ID if available
            add_request_id,
            # JSON renderer for production, console for development
            structlog.processors.JSONRenderer() if not settings.DEBUG 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def add_request_id(logger, method_name, event_dict):
    """Add request ID to log entries if available."""
    # This would be set by middleware
    request_id = getattr(logger, '_request_id', None)
    if request_id:
        event_dict['request_id'] = request_id
    return event_dict


class AuthLogger:
    """Specialized logger for authentication events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("auth")
    
    def log_registration_attempt(
        self, 
        email: str, 
        success: bool, 
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log user registration attempt."""
        log_data = {
            "email": email,
            "success": success,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(
                event="user_registration_success",
                email=email,
                success=success,
                request_id=log_data["request_id"]
            )
        else:
            self.logger.warning(
                event="user_registration_failed",
                **log_data
            )
    
    def log_login_attempt(
        self, 
        email: str, 
        success: bool, 
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log user login attempt."""
        log_data = {
            "email": email,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(
                event="user_login_success",
                **log_data
            )
        else:
            self.logger.warning(
                event="user_login_failed",
                **log_data
            )
    
    def log_token_operation(
        self, 
        operation: str, 
        user_id: str, 
        success: bool,
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log token operation."""
        log_data = {
            "operation": operation,
            "user_id": user_id,
            "success": success,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(
                event="token_operation_success",
                **log_data
            )
        else:
            self.logger.warning(
                event="token_operation_failed",
                **log_data
            )
    
    def log_logout(
        self, 
        user_id: str, 
        success: bool,
        error: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log user logout."""
        log_data = {
            "user_id": user_id,
            "success": success,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        if error:
            log_data["error"] = error
        
        if success:
            self.logger.info(
                event="user_logout_success",
                **log_data
            )
        else:
            self.logger.warning(
                event="user_logout_failed",
                **log_data
            )
    
    def log_account_lockout(
        self, 
        email: str, 
        failed_attempts: int,
        lockout_duration: int,
        request_id: Optional[str] = None
    ):
        """Log account lockout event."""
        self.logger.warning(
            event="account_lockout",
            email=email,
            failed_attempts=failed_attempts,
            lockout_duration_minutes=lockout_duration,
            request_id=request_id or str(uuid.uuid4())[:8]
        )
    
    def log_security_event(
        self, 
        event_type: str, 
        description: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """Log security-related events."""
        log_data = {
            "event_type": event_type,
            "description": description,
            "user_id": user_id,
            "ip_address": ip_address,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        if additional_data:
            log_data.update(additional_data)
        
        self.logger.warning(
            event="security_event",
            **log_data
        )


class TaskExecutionLogger:
    """Specialized logger for task execution events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("task_execution")
    
    def log_execution_started(
        self,
        task_id: str,
        execution_id: str,
        user_id: str,
        task_type: str,
        organization_id: str,
        gps_coordinates: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        """Log task execution start."""
        log_data = {
            "task_id": task_id,
            "execution_id": execution_id,
            "user_id": user_id,
            "task_type": task_type,
            "organization_id": organization_id,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        if gps_coordinates:
            log_data["gps_latitude"] = gps_coordinates.get("latitude")
            log_data["gps_longitude"] = gps_coordinates.get("longitude")
            log_data["gps_accuracy"] = gps_coordinates.get("accuracy")
        
        self.logger.info(
            event="task_execution_started",
            **log_data
        )
    
    def log_execution_completed(
        self,
        task_id: str,
        execution_id: str,
        user_id: str,
        task_type: str,
        organization_id: str,
        duration_minutes: Optional[int] = None,
        quality_rating: Optional[int] = None,
        materials_count: int = 0,
        photos_count: int = 0,
        labor_hours: float = 0,
        gps_quality_score: Optional[int] = None,
        request_id: Optional[str] = None
    ):
        """Log task execution completion."""
        log_data = {
            "task_id": task_id,
            "execution_id": execution_id,
            "user_id": user_id,
            "task_type": task_type,
            "organization_id": organization_id,
            "duration_minutes": duration_minutes,
            "quality_rating": quality_rating,
            "materials_count": materials_count,
            "photos_count": photos_count,
            "labor_hours": labor_hours,
            "gps_quality_score": gps_quality_score,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.info(
            event="task_execution_completed",
            **log_data
        )
    
    def log_execution_failed(
        self,
        task_id: str,
        user_id: str,
        task_type: str,
        organization_id: str,
        error_type: str,
        error_message: str,
        validation_errors: Optional[List[str]] = None,
        request_id: Optional[str] = None
    ):
        """Log task execution failure."""
        log_data = {
            "task_id": task_id,
            "user_id": user_id,
            "task_type": task_type,
            "organization_id": organization_id,
            "error_type": error_type,
            "error_message": error_message,
            "validation_errors": validation_errors or [],
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.error(
            event="task_execution_failed",
            **log_data
        )
    
    def log_photo_upload(
        self,
        execution_id: str,
        user_id: str,
        organization_id: str,
        photo_count: int,
        total_size_bytes: int,
        upload_type: str,
        gps_embedded_count: int = 0,
        validation_warnings: Optional[List[str]] = None,
        request_id: Optional[str] = None
    ):
        """Log photo upload for task execution."""
        log_data = {
            "execution_id": execution_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "photo_count": photo_count,
            "total_size_bytes": total_size_bytes,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "upload_type": upload_type,
            "gps_embedded_count": gps_embedded_count,
            "validation_warnings": validation_warnings or [],
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.info(
            event="task_execution_photo_upload",
            **log_data
        )
    
    def log_gps_validation(
        self,
        execution_id: str,
        user_id: str,
        latitude: float,
        longitude: float,
        accuracy: Optional[float],
        validation_result: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Log GPS validation for task execution."""
        log_data = {
            "execution_id": execution_id,
            "user_id": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "accuracy_meters": accuracy,
            "validation_passed": validation_result.get("valid", False),
            "quality_score": validation_result.get("quality_rating", 0),
            "accuracy_assessment": validation_result.get("accuracy_score", "unknown"),
            "warnings": validation_result.get("recommendations", []),
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        log_level = "info" if validation_result.get("valid", False) else "warning"
        getattr(self.logger, log_level)(
            event="task_execution_gps_validation",
            **log_data
        )
    
    def log_material_tracking(
        self,
        execution_id: str,
        user_id: str,
        organization_id: str,
        materials_used: List[Dict[str, Any]],
        compliance_result: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Log material tracking for task execution."""
        log_data = {
            "execution_id": execution_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "materials_count": len(materials_used),
            "total_cost": sum(m.get("total_cost", 0) for m in materials_used if m.get("total_cost")),
            "compliance_status": "compliant" if compliance_result.get("compliant", False) else "non_compliant",
            "missing_materials": len(compliance_result.get("missing_materials", [])),
            "dosage_issues": len(compliance_result.get("dosage_issues", [])),
            "material_types": list(set(m.get("input_item_name", "unknown") for m in materials_used)),
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        log_level = "info" if compliance_result.get("compliant", False) else "warning"
        getattr(self.logger, log_level)(
            event="task_execution_material_tracking",
            **log_data
        )
    
    def log_quality_assessment(
        self,
        execution_id: str,
        user_id: str,
        organization_id: str,
        quality_assessment: Dict[str, Any],
        request_id: Optional[str] = None
    ):
        """Log quality assessment for task execution."""
        log_data = {
            "execution_id": execution_id,
            "user_id": user_id,
            "organization_id": organization_id,
            "total_score": quality_assessment.get("total_score", 0),
            "grade": quality_assessment.get("grade", "F"),
            "gps_quality": quality_assessment.get("factor_breakdown", {}).get("gps_quality", 0),
            "documentation_quality": quality_assessment.get("factor_breakdown", {}).get("documentation_quality", 0),
            "data_completeness": quality_assessment.get("factor_breakdown", {}).get("data_completeness", 0),
            "execution_efficiency": quality_assessment.get("factor_breakdown", {}).get("execution_efficiency", 0),
            "recommendations": quality_assessment.get("recommendations", []),
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        log_level = "info" if quality_assessment.get("total_score", 0) >= 70 else "warning"
        getattr(self.logger, log_level)(
            event="task_execution_quality_assessment",
            **log_data
        )


class RBACLogger:
    """Specialized logger for RBAC permission evaluation events."""
    
    def __init__(self):
        self.logger = structlog.get_logger("rbac")
    
    def log_permission_evaluation(
        self,
        user_id: str,
        organization_id: str,
        resource: str,
        action: str,
        effect: str,
        source: str,
        roles: List[str],
        evaluation_duration: Optional[float] = None,
        base_permissions: Optional[Dict[str, str]] = None,
        org_overrides: Optional[Dict[str, str]] = None,
        request_id: Optional[str] = None
    ):
        """Log permission evaluation with detailed context."""
        log_data = {
            "user_id": user_id,
            "organization_id": organization_id,
            "resource": resource,
            "action": action,
            "effect": effect,
            "source": source,
            "roles": roles,
            "evaluation_duration_seconds": evaluation_duration,
            "base_permissions": base_permissions or {},
            "org_overrides": org_overrides or {},
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        log_level = "info" if effect == "ALLOW" else "warning"
        getattr(self.logger, log_level)(
            event="permission_evaluation",
            **log_data
        )
    
    def log_permission_denial(
        self,
        user_id: str,
        organization_id: str,
        resource: str,
        action: str,
        denial_reason: str,
        roles: List[str],
        attempted_context: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log permission denial with reason."""
        log_data = {
            "user_id": user_id,
            "organization_id": organization_id,
            "resource": resource,
            "action": action,
            "denial_reason": denial_reason,
            "roles": roles,
            "attempted_context": attempted_context,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.warning(
            event="permission_denied",
            **log_data
        )
    
    def log_override_application(
        self,
        organization_id: str,
        role_id: str,
        role_type: str,
        permission_resource: str,
        permission_action: str,
        effect: str,
        operation: str,
        created_by: str,
        override_id: Optional[str] = None,
        previous_effect: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log organization permission override application."""
        log_data = {
            "organization_id": organization_id,
            "role_id": role_id,
            "role_type": role_type,
            "permission_resource": permission_resource,
            "permission_action": permission_action,
            "effect": effect,
            "operation": operation,
            "created_by": created_by,
            "override_id": override_id,
            "previous_effect": previous_effect,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.info(
            event="permission_override_applied",
            **log_data
        )
    
    def log_role_assignment(
        self,
        organization_id: str,
        user_id: str,
        role_id: str,
        role_type: str,
        operation: str,
        assigned_by: str,
        previous_role: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """Log role assignment operation."""
        log_data = {
            "organization_id": organization_id,
            "user_id": user_id,
            "role_id": role_id,
            "role_type": role_type,
            "operation": operation,
            "assigned_by": assigned_by,
            "previous_role": previous_role,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.info(
            event="role_assignment",
            **log_data
        )
    
    def log_rbac_cache_operation(
        self,
        operation: str,
        cache_key: str,
        hit_miss: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
        request_id: Optional[str] = None
    ):
        """Log RBAC cache operations."""
        log_data = {
            "operation": operation,
            "cache_key": cache_key,
            "hit_miss": hit_miss,
            "user_id": user_id,
            "organization_id": organization_id,
            "ttl_seconds": ttl_seconds,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.info(
            event="rbac_cache_operation",
            **log_data
        )
    
    def log_rbac_configuration_change(
        self,
        organization_id: str,
        change_type: str,
        changed_by: str,
        change_details: Dict[str, Any],
        affected_users_count: Optional[int] = None,
        request_id: Optional[str] = None
    ):
        """Log RBAC configuration changes."""
        log_data = {
            "organization_id": organization_id,
            "change_type": change_type,
            "changed_by": changed_by,
            "change_details": change_details,
            "affected_users_count": affected_users_count,
            "request_id": request_id or str(uuid.uuid4())[:8]
        }
        
        self.logger.info(
            event="rbac_configuration_change",
            **log_data
        )


class RequestLogger:
    """Logger for HTTP requests."""
    
    def __init__(self):
        self.logger = structlog.get_logger("request")
    
    def log_request_start(
        self, 
        method: str, 
        path: str, 
        ip_address: str,
        user_agent: str,
        request_id: str
    ):
        """Log request start."""
        self.logger.info(
            event="request_started",
            method=method,
            path=path,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id
        )
    
    def log_request_end(
        self, 
        method: str, 
        path: str, 
        status_code: int,
        duration_ms: float,
        request_id: str,
        user_id: Optional[str] = None
    ):
        """Log request completion."""
        log_level = "info" if status_code < 400 else "warning" if status_code < 500 else "error"
        
        log_data = {
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "request_id": request_id,
            "user_id": user_id
        }
        
        getattr(self.logger, log_level)(
            event="request_completed",
            **log_data
        )
    
    def log_validation_error(
        self, 
        field_errors: Dict[str, list],
        request_id: str
    ):
        """Log validation errors."""
        self.logger.warning(
            event="validation_error",
            field_errors=field_errors,
            request_id=request_id
        )
    
    def log_rate_limit_exceeded(
        self, 
        ip_address: str,
        endpoint: str,
        request_id: str
    ):
        """Log rate limit exceeded."""
        self.logger.warning(
            event="rate_limit_exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            request_id=request_id
        )


# Global logger instances
auth_logger = AuthLogger()
request_logger = RequestLogger()
task_execution_logger = TaskExecutionLogger()
rbac_logger = RBACLogger()


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_application_startup():
    """Log application startup."""
    logger = get_logger("startup")
    logger.info(
        event="application_startup",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        log_level=settings.LOG_LEVEL
    )


def log_application_shutdown():
    """Log application shutdown."""
    logger = get_logger("shutdown")
    logger.info(
        event="application_shutdown",
        app_name=settings.APP_NAME
    )