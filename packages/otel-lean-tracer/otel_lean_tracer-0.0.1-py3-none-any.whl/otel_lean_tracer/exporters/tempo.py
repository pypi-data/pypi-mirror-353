# Grafana Tempo OTLP exporter factory
# Grafana Tempo OTLP エクスポーターファクトリー

from typing import Optional, Dict, Any
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
import logging

logger = logging.getLogger(__name__)


def create_tempo_exporter(
    endpoint: str = "http://localhost:4318/v1/traces",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 10,
    compression: Optional[str] = None
) -> OTLPSpanExporter:
    """
    Create a standardized OTLP exporter for Grafana Tempo
    Grafana Tempo用の標準化されたOTLPエクスポーターを作成
    
    Args:
        endpoint: Tempo OTLP HTTP endpoint URL
        headers: Optional HTTP headers (e.g., for authentication)
        timeout: Request timeout in seconds
        compression: Optional compression method ('gzip', etc.)
    
    Returns:
        Configured OTLPSpanExporter instance
    
    Example:
        >>> exporter = create_tempo_exporter(
        ...     endpoint="http://tempo:3200/v1/traces",
        ...     headers={"Authorization": "Bearer your-token"}
        ... )
    """
    # Default headers for Tempo
    # Tempo用のデフォルトヘッダー
    default_headers = {
        "Content-Type": "application/x-protobuf",
        "User-Agent": "otel-lean-tracer/0.1.0"
    }
    
    # Merge provided headers with defaults
    # 提供されたヘッダーをデフォルトとマージ
    if headers:
        default_headers.update(headers)
    
    try:
        # Create OTLP exporter with Tempo-specific configuration
        # Tempo固有の設定でOTLPエクスポーターを作成
        exporter = OTLPSpanExporter(
            endpoint=endpoint,
            headers=default_headers,
            timeout=timeout,
            compression=compression
        )
        
        logger.info(f"Created Tempo exporter for endpoint: {endpoint}")
        return exporter
        
    except Exception as e:
        logger.error(f"Failed to create Tempo exporter: {e}")
        raise


def create_tempo_exporter_from_config(config: Dict[str, Any]) -> OTLPSpanExporter:
    """
    Create Tempo exporter from configuration dictionary
    設定辞書からTempoエクスポーターを作成
    
    Args:
        config: Configuration dictionary with keys:
               - endpoint: Tempo endpoint URL
               - headers: Optional headers dict
               - timeout: Optional timeout in seconds
               - compression: Optional compression method
    
    Returns:
        Configured OTLPSpanExporter instance
    """
    return create_tempo_exporter(
        endpoint=config.get("endpoint", "http://localhost:4318/v1/traces"),
        headers=config.get("headers"),
        timeout=config.get("timeout", 10),
        compression=config.get("compression")
    )


# Common Tempo configurations
# 一般的なTempo設定
TEMPO_CONFIGS = {
    "local": {
        "endpoint": "http://localhost:4318/v1/traces",
        "timeout": 5
    },
    "docker": {
        "endpoint": "http://tempo:4318/v1/traces",
        "timeout": 10
    },
    "cloud": {
        "endpoint": "https://tempo-us-central1.grafana.net/tempo/api/push/v1/traces",
        "timeout": 30,
        "headers": {
            "Authorization": "Bearer ${GRAFANA_CLOUD_API_KEY}"
        }
    }
}


def create_tempo_exporter_preset(preset: str = "local", **kwargs) -> OTLPSpanExporter:
    """
    Create Tempo exporter using predefined presets
    事前定義されたプリセットを使用してTempoエクスポーターを作成
    
    Args:
        preset: Configuration preset ('local', 'docker', 'cloud')
        **kwargs: Override specific configuration values
    
    Returns:
        Configured OTLPSpanExporter instance
    """
    if preset not in TEMPO_CONFIGS:
        raise ValueError(f"Unknown preset '{preset}'. Available: {list(TEMPO_CONFIGS.keys())}")
    
    config = TEMPO_CONFIGS[preset].copy()
    config.update(kwargs)
    
    return create_tempo_exporter_from_config(config)