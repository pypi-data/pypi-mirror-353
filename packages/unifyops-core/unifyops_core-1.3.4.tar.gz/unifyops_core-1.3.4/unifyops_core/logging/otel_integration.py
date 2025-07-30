"""
OpenTelemetry Integration for Signoz

This module provides OpenTelemetry integration for log correlation and service
attribution in Signoz.

Usage:
    from unifyops_core.logging.otel_integration import setup_otel_logging
    setup_otel_logging()
"""

import os
import logging
import platform
import uuid
from typing import Optional, Dict, Any

from opentelemetry import _logs
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

# Configuration defaults
OTEL_AVAILABLE = True
DEFAULT_SERVICE_NAME = "unifyops-api"
DEFAULT_SERVICE_VERSION = "1.0.0" 
DEFAULT_SERVICE_NAMESPACE = "unifyops"
DEFAULT_ENVIRONMENT = "development"
DEFAULT_OTLP_ENDPOINT = "http://localhost:4317"
DEFAULT_LOG_LEVEL = "INFO"


class ResourceBuilder:
    """Builder for OpenTelemetry resource attributes."""
    
    def __init__(self):
        self.attributes = {}
    
    def add_service_info(self) -> "ResourceBuilder":
        """Add core service attributes."""
        self.attributes.update({
            "service.name": os.getenv("SERVICE_NAME", DEFAULT_SERVICE_NAME),
            "service.version": os.getenv("SERVICE_VERSION", DEFAULT_SERVICE_VERSION),
            "service.namespace": os.getenv("SERVICE_NAMESPACE", DEFAULT_SERVICE_NAMESPACE),
            "service.instance.id": self._get_instance_id(),
            "deployment.environment": os.getenv("DEPLOYMENT_ENVIRONMENT", 
                                               os.getenv("ENVIRONMENT", DEFAULT_ENVIRONMENT))
        })
        return self
    
    def add_host_info(self) -> "ResourceBuilder":
        """Add host and OS attributes."""
        self.attributes.update({
            "host.name": os.getenv("HOSTNAME", platform.node()),
            "host.type": self._get_host_type(),
            "host.arch": platform.machine(),
            "os.type": platform.system().lower(),
            "os.name": platform.system(),
            "os.version": platform.release()
        })
        return self
    
    def add_process_info(self) -> "ResourceBuilder":
        """Add process and runtime attributes."""
        self.attributes.update({
            "process.pid": os.getpid(),
            "process.runtime.name": "python",
            "process.runtime.version": platform.python_version(),
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry"
        })
        return self
    
    def add_kubernetes_info(self) -> "ResourceBuilder":
        """Add Kubernetes attributes if available."""
        k8s_attrs = {
            "k8s.pod.name": os.getenv("K8S_POD_NAME"),
            "k8s.pod.uid": os.getenv("K8S_POD_UID"),
            "k8s.namespace.name": os.getenv("K8S_NAMESPACE_NAME"),
            "k8s.node.name": os.getenv("K8S_NODE_NAME"),
            "k8s.cluster.name": os.getenv("K8S_CLUSTER_NAME"),
            "container.name": os.getenv("CONTAINER_NAME"),
            "container.id": os.getenv("CONTAINER_ID")
        }
        # Only add non-None values
        self.attributes.update({k: v for k, v in k8s_attrs.items() if v})
        return self
    
    def add_cloud_info(self) -> "ResourceBuilder":
        """Add cloud provider attributes if available."""
        cloud_provider = os.getenv("CLOUD_PROVIDER")
        if cloud_provider:
            self.attributes.update({
                "cloud.provider": cloud_provider,
                "cloud.region": os.getenv("CLOUD_REGION"),
                "cloud.availability_zone": os.getenv("CLOUD_AVAILABILITY_ZONE")
            })
        return self
    
    def build(self) -> Optional["Resource"]:
        """Build the Resource object."""
        if not OTEL_AVAILABLE:
            return None
        
        # Filter out None values
        clean_attrs = {k: v for k, v in self.attributes.items() if v is not None}
        return Resource.create(clean_attrs)
    
    def _get_instance_id(self) -> str:
        """Generate or retrieve service instance ID."""
        # Check environment variable first
        if instance_id := os.getenv("SERVICE_INSTANCE_ID"):
            return instance_id
        
        # Use pod UID if in Kubernetes
        if pod_uid := os.getenv("K8S_POD_UID"):
            namespace_uuid = uuid.UUID("4d63009a-8d0f-11ee-aad7-4c796ed8e320")
            return str(uuid.uuid5(namespace_uuid, pod_uid))
        
        # Generate random UUID
        return str(uuid.uuid4())
    
    def _get_host_type(self) -> str:
        """Determine host type based on environment."""
        if os.getenv("KUBERNETES_SERVICE_HOST"):
            return "container"
        return os.getenv("HOST_TYPE", "physical")


def create_otel_resource() -> Optional["Resource"]:
    """Create OpenTelemetry Resource with all required attributes."""
    return (ResourceBuilder()
            .add_service_info()
            .add_host_info()
            .add_process_info()
            .add_kubernetes_info()
            .add_cloud_info()
            .build())


def get_otlp_endpoint() -> str:
    """Get OTLP endpoint from environment or use default."""
    return (os.getenv("OTEL_EXPORTER_OTLP_LOGS_ENDPOINT") or
            os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") or
            os.getenv("SIGNOZ_ENDPOINT") or
            DEFAULT_OTLP_ENDPOINT)


def get_otlp_headers() -> Dict[str, str]:
    """Get headers for OTLP exporter."""
    headers = {}
    
    # Parse environment headers
    if env_headers := os.getenv("OTEL_EXPORTER_OTLP_HEADERS"):
        for header_pair in env_headers.split(","):
            if "=" in header_pair:
                key, value = header_pair.strip().split("=", 1)
                headers[key] = value
    
    # Add Signoz access token if available
    if token := os.getenv("SIGNOZ_ACCESS_TOKEN"):
        headers["signoz-access-token"] = token
    
    return headers


def setup_otel_logging(
    signoz_endpoint: Optional[str] = None,
    enable_console_logs: bool = True,
    log_level: str = DEFAULT_LOG_LEVEL
) -> bool:
    """
    Set up OpenTelemetry logging with Signoz integration.
    
    Args:
        signoz_endpoint: Signoz OTLP endpoint (auto-detected if not provided)
        enable_console_logs: Whether to also enable console logging
        log_level: Minimum log level
        
    Returns:
        True if setup successful, False otherwise
    """
    if not OTEL_AVAILABLE:
        logging.warning("OpenTelemetry not available. Using fallback logging.")
        return False
    
    try:
        # Create resource
        resource = create_otel_resource()
        if not resource:
            logging.error("Failed to create OpenTelemetry resource")
            return False
        
        # Get endpoint
        endpoint = signoz_endpoint or get_otlp_endpoint()
        
        # Create OTLP exporter
        exporter = OTLPLogExporter(
            endpoint=endpoint,
            insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true",
            headers=get_otlp_headers()
        )
        
        # Create logger provider
        provider = LoggerProvider(resource=resource)
        provider.add_log_record_processor(
            BatchLogRecordProcessor(exporter)
        )
        
        # Set global logger provider
        _logs.set_logger_provider(provider)
        
        # Create and configure handler
        handler = LoggingHandler(
            level=getattr(logging, log_level.upper()),
            logger_provider=provider
        )
        
        # Configure root logger
        root_logger = logging.getLogger()
        if not enable_console_logs:
            root_logger.handlers.clear()
        root_logger.addHandler(handler)
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Log success
        logger = logging.getLogger(__name__)
        logger.info(
            "OpenTelemetry logging configured",
            extra={
                "otel.endpoint": endpoint,
                "service.name": resource.attributes.get("service.name"),
                "service.version": resource.attributes.get("service.version")
            }
        )
        
        return True
        
    except Exception as e:
        logging.error(f"Failed to setup OpenTelemetry logging: {e}")
        return False


def verify_otel_setup() -> Dict[str, Any]:
    """Verify OpenTelemetry setup and return status information."""
    if not OTEL_AVAILABLE:
        return {
            "status": "unavailable",
            "error": "OpenTelemetry packages not installed"
        }
    
    try:
        provider = _logs.get_logger_provider()
        resource = getattr(provider, '_resource', None)
        
        if resource:
            return {
                "status": "configured",
                "service_name": resource.attributes.get("service.name"),
                "service_instance_id": resource.attributes.get("service.instance.id"),
                "attributes": dict(resource.attributes)
            }
        else:
            return {
                "status": "not_configured",
                "error": "No resource configured"
            }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


# Auto-setup if requested
if os.getenv("AUTO_SETUP_OTEL", "false").lower() == "true":
    setup_otel_logging() 