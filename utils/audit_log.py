"""
Structured audit logging — Phase 9F.

Provides a single `audit()` helper that emits a JSON-structured log event
for security-sensitive operations: deletes, permission changes, and data
exports.

Why structlog?
  Standard logging.getLogger produces unstructured text which is hard to
  query in log aggregation systems (Datadog, CloudWatch, ELK).  structlog
  emits key=value JSON by default, making events filterable by user_id,
  action, resource_type, etc. without regex parsing.

Usage:
    from utils.audit_log import audit
    audit("DELETE_REPORT", user_id=current_user.id, resource_id=report_id)
"""
import logging

try:
    import structlog

    _log = structlog.get_logger("audit")

    def _configure_once():
        import structlog
        structlog.configure(
            processors=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.BoundLogger,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
        )

    _configure_once()

    def audit(action: str, **kwargs):
        """Emit a structured audit log event.

        Parameters
        ----------
        action : str
            Machine-readable name for the operation,
            e.g. "DELETE_REPORT", "CHANGE_PERMISSIONS", "EXPORT_FILE".
        **kwargs
            Contextual fields: user_id, resource_id, resource_type, ip, etc.
        """
        _log.info("audit_event", action=action, **kwargs)

except ImportError:
    # Graceful degradation: structlog not installed → fall back to stdlib.
    _fallback = logging.getLogger("audit")

    def audit(action: str, **kwargs):  # type: ignore[misc]
        _fallback.info("audit_event action=%s %s", action,
                       " ".join(f"{k}={v}" for k, v in kwargs.items()))
