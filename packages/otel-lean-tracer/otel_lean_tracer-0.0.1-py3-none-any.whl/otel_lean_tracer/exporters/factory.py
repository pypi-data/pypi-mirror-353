# ExporterFactory for creating OTLP exporters to various backends
# 様々なバックエンドへのOTLPエクスポーター作成用ExporterFactory

import os
import logging
from typing import List, Optional, Union
from urllib.parse import urlparse

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPSpanExporter
from opentelemetry.sdk.trace.export import SpanExporter, ConsoleSpanExporter, SpanExportResult
from opentelemetry.sdk.trace import ReadableSpan

logger = logging.getLogger(__name__)


class MultiSpanExporter(SpanExporter):
    """
    Simple multi-span exporter that sends spans to multiple backends
    複数のバックエンドにスパンを送信するシンプルなマルチスパンエクスポーター
    """
    
    def __init__(self, exporters: List[SpanExporter]):
        """
        Initialize multi-span exporter with list of exporters
        エクスポーターのリストでマルチスパンエクスポーターを初期化
        
        Args:
            exporters: List of span exporters
        """
        self._exporters = exporters
    
    def export(self, spans) -> SpanExportResult:
        """
        Export spans to all configured exporters
        設定されたすべてのエクスポーターにスパンをエクスポート
        """
        results = []
        for exporter in self._exporters:
            try:
                result = exporter.export(spans)
                results.append(result)
            except Exception as e:
                logger.warning("Failed to export to %s: %s", type(exporter).__name__, e)
                results.append(SpanExportResult.FAILURE)
        
        # Return success if at least one exporter succeeded
        # 少なくとも1つのエクスポーターが成功した場合は成功を返す
        if any(result == SpanExportResult.SUCCESS for result in results):
            return SpanExportResult.SUCCESS
        else:
            return SpanExportResult.FAILURE
    
    def shutdown(self) -> None:
        """
        Shutdown all exporters
        すべてのエクスポーターをシャットダウン
        """
        for exporter in self._exporters:
            try:
                exporter.shutdown()
            except Exception as e:
                logger.warning("Failed to shutdown %s: %s", type(exporter).__name__, e)


class ExporterFactory:
    """
    Factory class for creating OTLP exporters to various backends
    様々なバックエンドへのOTLPエクスポーターを作成するファクトリークラス
    
    Supports:
    - Grafana Tempo (OTLP/gRPC, OTLP/HTTP)
    - Jaeger (OTLP/gRPC, OTLP/HTTP)
    - Langfuse (HTTP)
    - Console output (for debugging)
    - Custom endpoints
    
    サポート:
    - Grafana Tempo (OTLP/gRPC, OTLP/HTTP)
    - Jaeger (OTLP/gRPC, OTLP/HTTP)
    - Langfuse (HTTP)
    - コンソール出力 (デバッグ用)
    - カスタムエンドポイント
    """
    
    # Default endpoints for common backends
    # 一般的なバックエンドのデフォルトエンドポイント
    DEFAULT_ENDPOINTS = {
        'tempo': 'http://localhost:3200/v1/traces',
        'jaeger': 'http://localhost:14268/api/traces',
        'langfuse': 'https://cloud.langfuse.com/api/public/traces',
        'console': None  # Special case for console output
    }
    
    def __init__(self):
        """
        Initialize ExporterFactory
        ExporterFactoryを初期化
        """
        self._backend = os.getenv('OTEL_LEAN_BACKEND', 'console')
        self._endpoint = os.getenv('OTEL_EXPORTER_OTLP_TRACES_ENDPOINT')
        self._headers = self._parse_headers(os.getenv('OTEL_EXPORTER_OTLP_HEADERS', ''))
        self._timeout = int(os.getenv('OTEL_EXPORTER_OTLP_TIMEOUT', '10'))
        self._insecure = os.getenv('OTEL_EXPORTER_OTLP_INSECURE', 'false').lower() == 'true'
        
        logger.debug("ExporterFactory initialized with backend: %s", self._backend)
    
    def create_exporter(self) -> SpanExporter:
        """
        Create span exporter(s) based on configuration
        設定に基づいてスパンエクスポーターを作成
        
        Returns:
            SpanExporter: Single or multi exporter based on configuration
        """
        backends = [b.strip() for b in self._backend.split(',')]
        
        if len(backends) == 1:
            # Single backend
            # 単一バックエンド
            return self._create_single_exporter(backends[0])
        else:
            # Multiple backends
            # 複数バックエンド
            exporters = []
            for backend in backends:
                try:
                    exporter = self._create_single_exporter(backend)
                    exporters.append(exporter)
                except Exception as e:
                    logger.warning("Failed to create exporter for backend '%s': %s", backend, e)
            
            if not exporters:
                logger.warning("No exporters created, falling back to console")
                return ConsoleSpanExporter()
            
            if len(exporters) == 1:
                return exporters[0]
            else:
                return MultiSpanExporter(exporters)
    
    def _create_single_exporter(self, backend: str) -> SpanExporter:
        """
        Create a single span exporter for the specified backend
        指定されたバックエンド用の単一スパンエクスポーターを作成
        
        Args:
            backend: Backend name (tempo, jaeger, langfuse, console, or custom URL)
        
        Returns:
            SpanExporter: Configured exporter instance
        """
        backend = backend.lower().strip()
        
        # Special case for console output
        # コンソール出力の特別ケース
        if backend == 'console':
            logger.info("Creating console span exporter")
            return ConsoleSpanExporter()
        
        # Determine endpoint
        # エンドポイントを決定
        endpoint = self._determine_endpoint(backend)
        
        # Create exporter based on protocol
        # プロトコルに基づいてエクスポーターを作成
        if self._is_grpc_endpoint(endpoint):
            return self._create_grpc_exporter(endpoint, backend)
        else:
            return self._create_http_exporter(endpoint, backend)
    
    def _determine_endpoint(self, backend: str) -> str:
        """
        Determine the endpoint URL for the given backend
        指定されたバックエンドのエンドポイントURLを決定
        
        Args:
            backend: Backend name or custom URL
        
        Returns:
            str: Endpoint URL
        """
        # Use explicit endpoint if provided
        # 明示的なエンドポイントが提供されている場合はそれを使用
        if self._endpoint:
            return self._endpoint
        
        # Check if backend is a URL
        # バックエンドがURLかどうかをチェック
        if backend.startswith(('http://', 'https://', 'grpc://', 'grpcs://')):
            return backend
        
        # Use default endpoint for known backends
        # 既知のバックエンドのデフォルトエンドポイントを使用
        if backend in self.DEFAULT_ENDPOINTS:
            default_endpoint = self.DEFAULT_ENDPOINTS[backend]
            if default_endpoint is None:
                raise ValueError(f"Backend '{backend}' does not have a default endpoint")
            return default_endpoint
        
        # For unknown backends, assume it's a hostname and use default HTTP port
        # 不明なバックエンドの場合、ホスト名として扱い、デフォルトHTTPポートを使用
        return f"http://{backend}:4318/v1/traces"
    
    def _is_grpc_endpoint(self, endpoint: str) -> bool:
        """
        Check if the endpoint uses gRPC protocol
        エンドポイントがgRPCプロトコルを使用するかチェック
        
        Args:
            endpoint: Endpoint URL
        
        Returns:
            bool: True if gRPC, False if HTTP
        """
        parsed = urlparse(endpoint)
        
        # Explicit gRPC schemes
        # 明示的なgRPCスキーム
        if parsed.scheme in ('grpc', 'grpcs'):
            return True
        
        # Common gRPC ports
        # 一般的なgRPCポート
        grpc_ports = [4317, 14250, 9411]  # OTLP gRPC, Jaeger gRPC, Zipkin gRPC
        if parsed.port in grpc_ports:
            return True
        
        # Default to HTTP for standard HTTP ports or when uncertain
        # 標準HTTPポートまたは不明な場合はHTTPをデフォルトとする
        return False
    
    def _create_grpc_exporter(self, endpoint: str, backend: str) -> SpanExporter:
        """
        Create gRPC OTLP span exporter
        gRPC OTLPスパンエクスポーターを作成
        
        Args:
            endpoint: gRPC endpoint URL
            backend: Backend name for logging
        
        Returns:
            GRPCSpanExporter: Configured gRPC exporter
        """
        # Clean up endpoint for gRPC
        # gRPC用にエンドポイントをクリーンアップ
        if endpoint.startswith('grpc://'):
            endpoint = endpoint.replace('grpc://', 'http://')
        elif endpoint.startswith('grpcs://'):
            endpoint = endpoint.replace('grpcs://', 'https://')
        
        logger.info("Creating gRPC OTLP exporter for %s: %s", backend, endpoint)
        
        return GRPCSpanExporter(
            endpoint=endpoint,
            headers=self._headers,
            timeout=self._timeout,
            insecure=self._insecure
        )
    
    def _create_http_exporter(self, endpoint: str, backend: str) -> SpanExporter:
        """
        Create HTTP OTLP span exporter
        HTTP OTLPスパンエクスポーターを作成
        
        Args:
            endpoint: HTTP endpoint URL
            backend: Backend name for logging
        
        Returns:
            HTTPSpanExporter: Configured HTTP exporter
        """
        logger.info("Creating HTTP OTLP exporter for %s: %s", backend, endpoint)
        
        return HTTPSpanExporter(
            endpoint=endpoint,
            headers=self._headers,
            timeout=self._timeout
        )
    
    def _parse_headers(self, headers_str: str) -> dict:
        """
        Parse OTLP headers from environment variable format
        環境変数形式からOTLPヘッダーを解析
        
        Args:
            headers_str: Headers in "key1=value1,key2=value2" format
        
        Returns:
            dict: Parsed headers
        """
        headers = {}
        if not headers_str:
            return headers
        
        for header_pair in headers_str.split(','):
            if '=' in header_pair:
                key, value = header_pair.split('=', 1)
                headers[key.strip()] = value.strip()
            else:
                logger.warning("Invalid header format: %s", header_pair)
        
        return headers
    
    def get_backend_info(self) -> dict:
        """
        Get information about the configured backend(s)
        設定されたバックエンドの情報を取得
        
        Returns:
            dict: Backend configuration information
        """
        return {
            'backend': self._backend,
            'endpoint': self._endpoint,
            'timeout': self._timeout,
            'insecure': self._insecure,
            'headers_count': len(self._headers)
        }


def create_exporter(backend: Optional[str] = None) -> SpanExporter:
    """
    Convenience function to create an exporter with optional backend override
    バックエンドオーバーライドオプション付きでエクスポーターを作成する便利関数
    
    Args:
        backend: Optional backend override (overrides OTEL_LEAN_BACKEND env var)
    
    Returns:
        SpanExporter: Configured exporter instance
    """
    factory = ExporterFactory()
    
    if backend:
        # Temporarily override backend
        # 一時的にバックエンドをオーバーライド
        original_backend = factory._backend
        factory._backend = backend
        try:
            return factory.create_exporter()
        finally:
            factory._backend = original_backend
    else:
        return factory.create_exporter()