# Tests for ExporterFactory
# ExporterFactoryのテスト

import pytest
import os
from unittest.mock import patch, Mock

from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GRPCSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HTTPSpanExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

from otel_lean_tracer.exporters import ExporterFactory, create_exporter
from otel_lean_tracer.exporters.factory import MultiSpanExporter


class TestExporterFactory:
    """
    Test cases for ExporterFactory
    ExporterFactoryのテストケース
    """
    
    def setup_method(self):
        """
        Set up test environment
        テスト環境をセットアップ
        """
        # Clear environment variables that might affect tests
        # テストに影響する可能性のある環境変数をクリア
        self.env_vars_to_clear = [
            'OTEL_LEAN_BACKEND',
            'OTEL_EXPORTER_OTLP_TRACES_ENDPOINT',
            'OTEL_EXPORTER_OTLP_HEADERS',
            'OTEL_EXPORTER_OTLP_TIMEOUT',
            'OTEL_EXPORTER_OTLP_INSECURE'
        ]
        
        self.original_env = {}
        for var in self.env_vars_to_clear:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """
        Restore original environment
        元の環境を復元
        """
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_create_exporter_factory(self):
        """
        Test creating ExporterFactory with default settings
        デフォルト設定でExporterFactoryを作成するテスト
        """
        factory = ExporterFactory()
        
        assert factory._backend == 'console'  # Default backend
        assert factory._endpoint is None
        assert factory._headers == {}
        assert factory._timeout == 10
        assert factory._insecure is False
    
    def test_create_exporter_factory_with_env_vars(self):
        """
        Test creating ExporterFactory with environment variables
        環境変数を使用してExporterFactoryを作成するテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'tempo'
        os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'http://tempo:3200/v1/traces'
        os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = 'x-api-key=secret,content-type=application/json'
        os.environ['OTEL_EXPORTER_OTLP_TIMEOUT'] = '30'
        os.environ['OTEL_EXPORTER_OTLP_INSECURE'] = 'true'
        
        factory = ExporterFactory()
        
        assert factory._backend == 'tempo'
        assert factory._endpoint == 'http://tempo:3200/v1/traces'
        assert factory._headers == {'x-api-key': 'secret', 'content-type': 'application/json'}
        assert factory._timeout == 30
        assert factory._insecure is True
    
    def test_create_console_exporter(self):
        """
        Test creating console exporter
        コンソールエクスポーターの作成をテスト
        """
        factory = ExporterFactory()
        exporter = factory.create_exporter()
        
        assert isinstance(exporter, ConsoleSpanExporter)
    
    @patch('otel_lean_tracer.exporters.factory.HTTPSpanExporter')
    def test_create_tempo_exporter(self, mock_http_exporter):
        """
        Test creating Tempo HTTP exporter
        Tempo HTTPエクスポーターの作成をテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'tempo'
        
        factory = ExporterFactory()
        exporter = factory.create_exporter()
        
        mock_http_exporter.assert_called_once_with(
            endpoint='http://localhost:3200/v1/traces',
            headers={},
            timeout=10
        )
    
    @patch('otel_lean_tracer.exporters.factory.GRPCSpanExporter')
    def test_create_grpc_exporter(self, mock_grpc_exporter):
        """
        Test creating gRPC exporter
        gRPCエクスポーターの作成をテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'grpc://localhost:4317'
        
        factory = ExporterFactory()
        exporter = factory.create_exporter()
        
        mock_grpc_exporter.assert_called_once_with(
            endpoint='http://localhost:4317',
            headers={},
            timeout=10,
            insecure=False
        )
    
    @patch('otel_lean_tracer.exporters.factory.HTTPSpanExporter')
    def test_create_custom_endpoint_exporter(self, mock_http_exporter):
        """
        Test creating exporter with custom endpoint
        カスタムエンドポイントでエクスポーターを作成するテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'tempo'
        os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'https://custom.tempo.io/v1/traces'
        
        factory = ExporterFactory()
        exporter = factory.create_exporter()
        
        mock_http_exporter.assert_called_once_with(
            endpoint='https://custom.tempo.io/v1/traces',
            headers={},
            timeout=10
        )
    
    @patch('otel_lean_tracer.exporters.factory.HTTPSpanExporter')
    def test_create_multi_backend_exporter(self, mock_http_exporter):
        """
        Test creating multi-backend exporter
        マルチバックエンドエクスポーターの作成をテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'tempo,jaeger'
        
        factory = ExporterFactory()
        exporter = factory.create_exporter()
        
        assert isinstance(exporter, MultiSpanExporter)
        assert len(mock_http_exporter.call_args_list) == 2
    
    def test_create_multi_backend_with_console_fallback(self):
        """
        Test creating multi-backend exporter with console fallback on error
        エラー時のコンソールフォールバック付きマルチバックエンドエクスポーターの作成をテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'invalid_backend,another_invalid'
        
        with patch('otel_lean_tracer.exporters.factory.ExporterFactory._create_single_exporter', 
                   side_effect=Exception("Connection failed")):
            factory = ExporterFactory()
            exporter = factory.create_exporter()
            
            assert isinstance(exporter, ConsoleSpanExporter)
    
    def test_determine_endpoint_with_url_backend(self):
        """
        Test endpoint determination when backend is a URL
        バックエンドがURLの場合のエンドポイント決定をテスト
        """
        factory = ExporterFactory()
        
        # Test HTTP URL
        # HTTP URLをテスト
        endpoint = factory._determine_endpoint('https://tempo.example.com/v1/traces')
        assert endpoint == 'https://tempo.example.com/v1/traces'
        
        # Test gRPC URL
        # gRPC URLをテスト
        endpoint = factory._determine_endpoint('grpc://tempo.example.com:4317')
        assert endpoint == 'grpc://tempo.example.com:4317'
    
    def test_determine_endpoint_with_hostname(self):
        """
        Test endpoint determination with hostname
        ホスト名でのエンドポイント決定をテスト
        """
        factory = ExporterFactory()
        
        endpoint = factory._determine_endpoint('my-tempo-host')
        assert endpoint == 'http://my-tempo-host:4318/v1/traces'
    
    def test_is_grpc_endpoint(self):
        """
        Test gRPC endpoint detection
        gRPCエンドポイント検出をテスト
        """
        factory = ExporterFactory()
        
        # gRPC schemes
        # gRPCスキーム
        assert factory._is_grpc_endpoint('grpc://localhost:4317') is True
        assert factory._is_grpc_endpoint('grpcs://secure.tempo.com:4317') is True
        
        # gRPC ports
        # gRPCポート
        assert factory._is_grpc_endpoint('http://localhost:4317') is True
        assert factory._is_grpc_endpoint('https://tempo.com:14250') is True
        
        # HTTP endpoints
        # HTTPエンドポイント
        assert factory._is_grpc_endpoint('http://localhost:3200/v1/traces') is False
        assert factory._is_grpc_endpoint('https://tempo.com:4318/v1/traces') is False
    
    def test_parse_headers(self):
        """
        Test header parsing from environment variable format
        環境変数形式からのヘッダー解析をテスト
        """
        factory = ExporterFactory()
        
        # Valid headers
        # 有効なヘッダー
        headers = factory._parse_headers('key1=value1,key2=value2')
        assert headers == {'key1': 'value1', 'key2': 'value2'}
        
        # Headers with spaces
        # スペースを含むヘッダー
        headers = factory._parse_headers(' key1 = value1 , key2 = value2 ')
        assert headers == {'key1': 'value1', 'key2': 'value2'}
        
        # Empty headers
        # 空のヘッダー
        headers = factory._parse_headers('')
        assert headers == {}
        
        # Invalid header format (should be logged as warning)
        # 無効なヘッダー形式（警告としてログに記録される）
        headers = factory._parse_headers('invalidheader,key2=value2')
        assert headers == {'key2': 'value2'}
    
    def test_get_backend_info(self):
        """
        Test getting backend configuration information
        バックエンド設定情報の取得をテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'tempo'
        os.environ['OTEL_EXPORTER_OTLP_TRACES_ENDPOINT'] = 'http://tempo:3200/v1/traces'
        os.environ['OTEL_EXPORTER_OTLP_HEADERS'] = 'x-api-key=secret'
        os.environ['OTEL_EXPORTER_OTLP_TIMEOUT'] = '30'
        os.environ['OTEL_EXPORTER_OTLP_INSECURE'] = 'true'
        
        factory = ExporterFactory()
        info = factory.get_backend_info()
        
        assert info == {
            'backend': 'tempo',
            'endpoint': 'http://tempo:3200/v1/traces',
            'timeout': 30,
            'insecure': True,
            'headers_count': 1
        }


class TestCreateExporterFunction:
    """
    Test cases for create_exporter convenience function
    create_exporter便利関数のテストケース
    """
    
    def setup_method(self):
        """
        Set up test environment
        テスト環境をセットアップ
        """
        # Clear environment variables
        # 環境変数をクリア
        if 'OTEL_LEAN_BACKEND' in os.environ:
            del os.environ['OTEL_LEAN_BACKEND']
    
    def test_create_exporter_default(self):
        """
        Test create_exporter with default settings
        デフォルト設定でcreate_exporterをテスト
        """
        exporter = create_exporter()
        assert isinstance(exporter, ConsoleSpanExporter)
    
    @patch('otel_lean_tracer.exporters.factory.HTTPSpanExporter')
    def test_create_exporter_with_backend_override(self, mock_http_exporter):
        """
        Test create_exporter with backend override
        バックエンドオーバーライド付きでcreate_exporterをテスト
        """
        exporter = create_exporter(backend='tempo')
        
        mock_http_exporter.assert_called_once_with(
            endpoint='http://localhost:3200/v1/traces',
            headers={},
            timeout=10
        )
    
    @patch('otel_lean_tracer.exporters.factory.HTTPSpanExporter')
    def test_create_exporter_backend_override_preserves_env(self, mock_http_exporter):
        """
        Test that backend override doesn't permanently change environment
        バックエンドオーバーライドが環境を永続的に変更しないことをテスト
        """
        os.environ['OTEL_LEAN_BACKEND'] = 'jaeger'
        
        # Override to tempo
        # tempoにオーバーライド
        exporter1 = create_exporter(backend='tempo')
        
        # Should use original jaeger setting
        # 元のjaeger設定を使用するはず
        exporter2 = create_exporter()
        
        # Check that tempo was called for first exporter
        # 最初のエクスポーターでtempoが呼ばれたことを確認
        first_call = mock_http_exporter.call_args_list[0]
        assert 'localhost:3200' in first_call[1]['endpoint']
        
        # Check that jaeger was called for second exporter
        # 2番目のエクスポーターでjaegerが呼ばれたことを確認
        second_call = mock_http_exporter.call_args_list[1]
        assert 'localhost:14268' in second_call[1]['endpoint']