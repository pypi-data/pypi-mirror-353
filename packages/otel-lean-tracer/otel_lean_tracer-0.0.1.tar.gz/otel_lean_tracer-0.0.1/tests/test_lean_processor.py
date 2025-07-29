# Test cases for LeanTraceProcessor and related utilities
# LeanTraceProcessorと関連ユーティリティのテストケース

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.trace import TraceFlags, SpanContext

from otel_lean_tracer.processors.lean_processor import LeanTraceProcessor, instrument_lean
from otel_lean_tracer.utils.cost import CostCalculator
from otel_lean_tracer.utils.context import ContextAnalyzer


class TestCostCalculator:
    """
    Test cases for CostCalculator utility
    CostCalculatorユーティリティのテストケース
    """
    
    def test_create_cost_calculator(self):
        """
        Test creating a CostCalculator instance
        CostCalculatorインスタンスの作成をテスト
        """
        calculator = CostCalculator()
        assert "openai" in calculator.pricing
        assert "anthropic" in calculator.pricing
        assert "google" in calculator.pricing
    
    def test_calculate_openai_cost(self):
        """
        Test calculating cost for OpenAI models
        OpenAIモデルのコスト計算をテスト
        """
        calculator = CostCalculator()
        
        # Test GPT-4 cost calculation
        cost = calculator.calculate_cost("openai", "gpt-4", 1000, 500)
        expected = (1000/1000 * 0.03) + (500/1000 * 0.06)  # $0.06
        assert cost == expected
        
        # Test GPT-3.5-turbo cost calculation
        cost = calculator.calculate_cost("openai", "gpt-3.5-turbo", 2000, 1000)
        expected = (2000/1000 * 0.0015) + (1000/1000 * 0.002)  # $0.005
        assert cost == expected
    
    def test_calculate_anthropic_cost(self):
        """
        Test calculating cost for Anthropic models
        Anthropicモデルのコスト計算をテスト
        """
        calculator = CostCalculator()
        
        cost = calculator.calculate_cost("anthropic", "claude-3-sonnet", 1000, 500)
        expected = (1000/1000 * 0.003) + (500/1000 * 0.015)  # $0.0105
        assert cost == expected
    
    def test_unknown_model_returns_zero(self):
        """
        Test that unknown models return zero cost
        未知のモデルがゼロコストを返すことをテスト
        """
        calculator = CostCalculator()
        cost = calculator.calculate_cost("unknown", "unknown-model", 1000, 500)
        assert cost == 0.0
    
    def test_custom_pricing(self):
        """
        Test adding custom model pricing
        カスタムモデル価格の追加をテスト
        """
        calculator = CostCalculator()
        calculator.add_custom_model("custom", "my-model", 0.01, 0.02)
        
        cost = calculator.calculate_cost("custom", "my-model", 1000, 500)
        expected = (1000/1000 * 0.01) + (500/1000 * 0.02)  # $0.02
        assert cost == expected
    
    @patch.dict('os.environ', {
        'OTEL_LEAN_PRICE_OPENAI_CUSTOM_INPUT': '0.001',
        'OTEL_LEAN_PRICE_OPENAI_CUSTOM_OUTPUT': '0.002'
    })
    def test_env_pricing(self):
        """
        Test loading pricing from environment variables
        環境変数からの価格読み込みをテスト
        """
        calculator = CostCalculator()
        cost = calculator.calculate_cost("openai", "custom", 1000, 500)
        expected = (1000/1000 * 0.001) + (500/1000 * 0.002)  # $0.002
        assert cost == expected


class TestContextAnalyzer:
    """
    Test cases for ContextAnalyzer utility
    ContextAnalyzerユーティリティのテストケース
    """
    
    def test_create_context_analyzer(self):
        """
        Test creating a ContextAnalyzer instance
        ContextAnalyzerインスタンスの作成をテスト
        """
        analyzer = ContextAnalyzer()
        assert analyzer is not None
    
    def test_calculate_context_bytes_string(self):
        """
        Test calculating bytes for string content
        文字列コンテンツのバイト計算をテスト
        """
        analyzer = ContextAnalyzer()
        
        # ASCII string
        bytes_count = analyzer.calculate_context_bytes("Hello World")
        assert bytes_count == len("Hello World".encode('utf-8'))
        
        # Unicode string
        bytes_count = analyzer.calculate_context_bytes("こんにちは")
        assert bytes_count == len("こんにちは".encode('utf-8'))
    
    def test_calculate_context_bytes_dict(self):
        """
        Test calculating bytes for dictionary content
        辞書コンテンツのバイト計算をテスト
        """
        analyzer = ContextAnalyzer()
        
        data = {"key": "value", "number": 123}
        bytes_count = analyzer.calculate_context_bytes(data)
        import json
        expected = len(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        assert bytes_count == expected
    
    def test_estimate_useful_bytes(self):
        """
        Test estimating useful context bytes
        有用なコンテキストバイトの推定をテスト
        """
        analyzer = ContextAnalyzer()
        
        context = "This is a long context with lots of information that may or may not be useful."
        total_bytes = analyzer.calculate_context_bytes(context)
        
        # Short response should indicate low context usage
        short_response = "Yes"
        useful_bytes = analyzer.estimate_useful_bytes(context, short_response)
        assert useful_bytes == int(total_bytes * 0.1)
        
        # Medium response should indicate medium context usage
        medium_response = "This is a medium length response that shows some use of context."
        useful_bytes = analyzer.estimate_useful_bytes(context, medium_response)
        assert useful_bytes == int(total_bytes * 0.3)  # 50-200 chars = 0.3 ratio
        
        # Long response should indicate high context usage  
        long_response = "This is a very detailed response that shows significant use of the provided context. " * 15  # >1000 chars
        useful_bytes = analyzer.estimate_useful_bytes(context, long_response)
        assert useful_bytes == int(total_bytes * 0.9)
    
    def test_analyze_context_efficiency(self):
        """
        Test analyzing context efficiency
        コンテキスト効率の分析をテスト
        """
        analyzer = ContextAnalyzer()
        
        # Highly efficient usage
        result = analyzer.analyze_context_efficiency(1000, 850)
        assert result["efficiency_ratio"] == 0.85
        assert result["efficiency_percentage"] == 85.0
        assert result["classification"] == "highly_efficient"
        
        # Inefficient usage
        result = analyzer.analyze_context_efficiency(1000, 150)
        assert result["efficiency_ratio"] == 0.15
        assert result["classification"] == "highly_inefficient"
        assert len(result["recommendations"]) > 0


class TestLeanTraceProcessor:
    """
    Test cases for LeanTraceProcessor
    LeanTraceProcessorのテストケース
    """
    
    def setup_method(self):
        """
        Set up test fixtures
        テストフィクスチャのセットアップ
        """
        self.processor = LeanTraceProcessor()
        self.mock_span = self._create_mock_span()
    
    def _create_mock_span(self, span_id: int = 12345, trace_id: int = 67890):
        """
        Create a mock span for testing
        テスト用のモックSpanを作成
        """
        mock_span = Mock(spec=Span)
        mock_span.name = "test_span"
        mock_span.attributes = {}
        mock_span.status = Status(StatusCode.OK)
        
        # Create mock span context
        span_context = SpanContext(
            trace_id=trace_id,
            span_id=span_id,
            is_remote=False,
            trace_flags=TraceFlags.DEFAULT
        )
        mock_span.context = span_context
        
        # Mock set_attribute method
        def set_attribute(key, value):
            mock_span.attributes[key] = value
        mock_span.set_attribute = set_attribute
        
        return mock_span
    
    def test_create_lean_processor(self):
        """
        Test creating a LeanTraceProcessor instance
        LeanTraceProcessorインスタンスの作成をテスト
        """
        processor = LeanTraceProcessor()
        assert processor.enabled is True
        assert processor.cost_calculator is not None
        assert processor.context_analyzer is not None
    
    def test_disabled_processor(self):
        """
        Test disabled processor does nothing
        無効なプロセッサーが何もしないことをテスト
        """
        processor = LeanTraceProcessor(enabled=False)
        mock_span = self._create_mock_span()
        
        # Should not add any attributes when disabled
        processor.on_start(mock_span)
        processor.on_end(mock_span)
        
        assert len(mock_span.attributes) == 0
    
    def test_on_start(self):
        """
        Test span start processing
        Span開始処理をテスト
        """
        mock_span = self._create_mock_span()
        
        self.processor.on_start(mock_span)
        
        # Should add initial lean attributes
        assert "otel.lean.gen.id" in mock_span.attributes
        assert mock_span.attributes["otel.lean.gen.attempt"] == 1
        assert mock_span.attributes["otel.lean.gen.accepted"] is True
        
        # Should record queue start time
        span_id = f"span-{mock_span.context.span_id:016x}"
        assert span_id in self.processor._queue_start_times
    
    def test_on_end_with_llm_attributes(self):
        """
        Test span end processing with LLM attributes
        LLM属性を持つSpan終了処理をテスト
        """
        mock_span = self._create_mock_span()
        
        # Simulate span start
        self.processor.on_start(mock_span)
        
        # Add LLM-specific attributes
        mock_span.attributes.update({
            "llm.prompt": "What is the capital of France?",
            "llm.response": "The capital of France is Paris.",
            "llm.request.model": "gpt-4",
            "llm.usage.prompt_tokens": 100,
            "llm.usage.completion_tokens": 50,
            "gen.system": "openai"
        })
        
        # Process span end
        self.processor.on_end(mock_span)
        
        # Should have cost calculation
        assert "otel.lean.cost_usd" in mock_span.attributes
        assert mock_span.attributes["otel.lean.cost_usd"] > 0
        
        # Should have context metrics
        assert "otel.lean.context_bytes" in mock_span.attributes
        assert "otel.lean.useful_bytes" in mock_span.attributes
        assert mock_span.attributes["otel.lean.context_bytes"] > 0
        
        # Should have queue metrics
        assert "otel.lean.queue_age_ms" in mock_span.attributes
        assert mock_span.attributes["otel.lean.queue_age_ms"] >= 0
    
    def test_on_end_with_error_status(self):
        """
        Test span end processing with error status
        エラーステータスでのSpan終了処理をテスト
        """
        mock_span = self._create_mock_span()
        mock_span.status = Status(StatusCode.ERROR)
        
        # Simulate span start
        self.processor.on_start(mock_span)
        gen_id = mock_span.attributes["otel.lean.gen.id"]
        
        # Process span end
        self.processor.on_end(mock_span)
        
        # Should mark as not accepted and increment attempt
        generation_metadata = self.processor._generation_metadata.get(gen_id)
        if generation_metadata:
            assert generation_metadata.acceptance_status is False
            assert generation_metadata.attempt_count == 2
    
    def test_generation_id_persistence(self):
        """
        Test generation ID persistence across spans
        Span間での生成ID永続化をテスト
        """
        # First span
        span1 = self._create_mock_span(span_id=1)
        self.processor.on_start(span1)
        gen_id1 = span1.attributes["otel.lean.gen.id"]
        
        # Second span with same generation ID
        span2 = self._create_mock_span(span_id=2)
        span2.attributes = {"gen.id": gen_id1}  # Simulate inherited gen_id
        
        self.processor.on_start(span2)
        gen_id2 = span2.attributes["otel.lean.gen.id"]
        
        assert gen_id1 == gen_id2
    
    def test_cleanup_span_data(self):
        """
        Test cleanup of span data
        Spanデータのクリーンアップをテスト
        """
        mock_span = self._create_mock_span()
        
        # Process span lifecycle
        self.processor.on_start(mock_span)
        span_id = f"span-{mock_span.context.span_id:016x}"
        
        # Verify data exists
        assert span_id in self.processor._queue_start_times
        
        # Process span end
        self.processor.on_end(mock_span)
        
        # Verify cleanup
        assert span_id not in self.processor._queue_start_times
    
    def test_processor_shutdown(self):
        """
        Test processor shutdown
        プロセッサーシャットダウンをテスト
        """
        # Add some data
        mock_span = self._create_mock_span()
        self.processor.on_start(mock_span)
        
        # Shutdown
        self.processor.shutdown()
        
        # Verify cleanup
        assert len(self.processor._generation_metadata) == 0
        assert len(self.processor._queue_start_times) == 0


class TestInstrumentLean:
    """
    Test cases for instrument_lean function
    instrument_lean関数のテストケース
    """
    
    @patch('otel_lean_tracer.processors.lean_processor.set_tracer_provider')
    @patch('otel_lean_tracer.processors.lean_processor.TracerProvider')
    def test_instrument_lean_basic(self, mock_tracer_provider_class, mock_set_tracer_provider):
        """
        Test basic instrument_lean functionality
        基本的なinstrument_lean機能をテスト
        """
        mock_tracer_provider = Mock()
        mock_tracer_provider_class.return_value = mock_tracer_provider
        
        instrument_lean(service_name="test-service")
        
        # Should create tracer provider
        mock_tracer_provider_class.assert_called_once()
        mock_set_tracer_provider.assert_called_once_with(mock_tracer_provider)
        
        # Should add span processor
        assert mock_tracer_provider.add_span_processor.called
    
    @patch('otel_lean_tracer.processors.lean_processor.set_tracer_provider')
    @patch('otel_lean_tracer.processors.lean_processor.TracerProvider')
    @patch('otel_lean_tracer.processors.lean_processor.OTLPSpanExporter')
    def test_instrument_lean_with_otlp(self, mock_otlp_exporter, mock_tracer_provider_class, mock_set_tracer_provider):
        """
        Test instrument_lean with OTLP endpoint
        OTLPエンドポイントでのinstrument_leanをテスト
        """
        mock_tracer_provider = Mock()
        mock_tracer_provider_class.return_value = mock_tracer_provider
        mock_otlp_exporter.return_value = Mock()
        
        instrument_lean(
            service_name="test-service",
            otlp_endpoint="http://localhost:4318/v1/traces"
        )
        
        # Should create OTLP exporter
        mock_otlp_exporter.assert_called_once_with(
            endpoint="http://localhost:4318/v1/traces"
        )
    
    @patch('otel_lean_tracer.processors.lean_processor.set_tracer_provider')
    @patch('otel_lean_tracer.processors.lean_processor.TracerProvider')
    @patch('otel_lean_tracer.processors.lean_processor.ConsoleSpanExporter')
    def test_instrument_lean_with_console(self, mock_console_exporter, mock_tracer_provider_class, mock_set_tracer_provider):
        """
        Test instrument_lean with console export
        コンソールエクスポートでのinstrument_leanをテスト
        """
        mock_tracer_provider = Mock()
        mock_tracer_provider_class.return_value = mock_tracer_provider
        mock_console_exporter.return_value = Mock()
        
        instrument_lean(
            service_name="test-service",
            console_export=True
        )
        
        # Should create console exporter
        mock_console_exporter.assert_called_once()
    
    def test_instrument_lean_disabled(self):
        """
        Test instrument_lean when disabled
        無効化されたinstrument_leanをテスト
        """
        with patch('otel_lean_tracer.processors.lean_processor.logger') as mock_logger:
            instrument_lean(enabled=False)
            mock_logger.info.assert_called_with("Lean instrumentation is disabled")