# Tests for FlowInstrumentationMixin
# FlowInstrumentationMixinのテスト

import pytest
import asyncio
import uuid
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from otel_lean_tracer.mixins.flow_mixin import FlowInstrumentationMixin, instrument_flow_function


class TestFlowInstrumentationMixin:
    """
    Test cases for FlowInstrumentationMixin
    FlowInstrumentationMixinのテストケース
    """
    
    def setup_method(self):
        """
        Set up test environment with in-memory span exporter
        インメモリスパンエクスポーターでテスト環境をセットアップ
        """
        # Set up OTEL tracing with isolated tracer
        # 独立したトレーサーでOTELトレーシングを設定
        self.span_exporter = InMemorySpanExporter()
        self.tracer_provider = TracerProvider()
        self.tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        
        # Get a tracer from our provider
        # プロバイダーからトレーサーを取得
        self.tracer = self.tracer_provider.get_tracer(__name__)
        
        # Clear any existing spans
        # 既存のスパンをクリア
        self.span_exporter.clear()
    
    def test_create_flow_mixin(self):
        """
        Test creating FlowInstrumentationMixin instance
        FlowInstrumentationMixinインスタンスの作成をテスト
        """
        mixin = FlowInstrumentationMixin()
        
        assert hasattr(mixin, '_tracer')
        assert hasattr(mixin, '_generation_id')
        assert hasattr(mixin, '_step_start_times')
        assert hasattr(mixin, '_flow_span')
        assert mixin._generation_id.startswith('gen-')
        assert len(mixin._generation_id) == 12  # 'gen-' + 8 hex chars
        assert isinstance(mixin._step_start_times, dict)
        assert mixin._flow_span is None
    
    def test_set_and_get_generation_id(self):
        """
        Test setting and getting custom generation ID
        カスタム生成IDの設定と取得をテスト
        """
        mixin = FlowInstrumentationMixin()
        custom_id = "test-gen-123"
        
        mixin.set_generation_id(custom_id)
        assert mixin.get_generation_id() == custom_id
    
    @pytest.mark.asyncio
    async def test_run_with_mock_super_run(self):
        """
        Test run method with mocked super().run()
        モックしたsuper().run()でrunメソッドをテスト
        """
        # Create a mock step that returns processed data
        # 処理されたデータを返すモックステップを作成
        mock_step = AsyncMock()
        mock_step.name = "processing_step"
        mock_step.run = AsyncMock(return_value="processed_test_input")
        
        class MockFlowMixin(FlowInstrumentationMixin):
            def __init__(self, tracer):
                super().__init__()
                self.name = "test_flow"
                self.steps = [mock_step]
                # Override tracer with test tracer
                # テスト用トレーサーでオーバーライド
                self._tracer = tracer
        
        mixin = MockFlowMixin(self.tracer)
        result = await mixin.run("test_input")
        
        assert result == "processed_test_input"
        
        # Check spans were created (flow span + step span)
        # スパンが作成されたことを確認（フロースパン + ステップスパン）
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 2
        
        # First span should be the step span
        # 最初のスパンはステップスパンのはず
        step_span = spans[0]
        assert step_span.name == "step.processing_step"
        
        # Second span should be the flow span
        # 2番目のスパンはフロースパンのはず
        flow_span = spans[1]
        assert flow_span.name == "flow.test_flow"
        assert flow_span.attributes["otel.lean.gen.id"] == mixin._generation_id
        assert flow_span.attributes["flow.type"] == "agents_sdk_models"
        assert flow_span.attributes["flow.input_type"] == "str"
        assert flow_span.attributes["otel.lean.gen.accepted"] is True
        assert flow_span.status.status_code == StatusCode.OK
    
    @pytest.mark.asyncio
    async def test_run_with_exception(self):
        """
        Test run method when execution fails
        実行が失敗した場合のrunメソッドをテスト
        """
        # Create a mock step that raises an exception
        # 例外を発生させるモックステップを作成
        mock_step = AsyncMock()
        mock_step.name = "failing_step"
        mock_step.run = AsyncMock(side_effect=ValueError("Test error"))
        
        class MockFlowMixin(FlowInstrumentationMixin):
            def __init__(self, tracer):
                super().__init__()
                self.name = "failing_flow"
                self.steps = [mock_step]
                self._tracer = tracer
        
        mixin = MockFlowMixin(self.tracer)
        
        with pytest.raises(ValueError, match="Test error"):
            await mixin.run("test_input")
        
        # Check error spans were created
        # エラースパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 2  # step span + flow span
        
        # First span should be the failed step span
        # 最初のスパンは失敗したステップスパンのはず
        step_span = spans[0]
        assert step_span.name == "step.failing_step"
        assert step_span.status.status_code == StatusCode.ERROR
        
        # Second span should be the failed flow span
        # 2番目のスパンは失敗したフロースパンのはず
        flow_span = spans[1]
        assert flow_span.name == "flow.failing_flow"
        assert flow_span.attributes["otel.lean.gen.accepted"] is False
        assert flow_span.status.status_code == StatusCode.ERROR
        assert "Test error" in flow_span.status.description
    
    @pytest.mark.asyncio
    async def test_execute_steps_with_list(self):
        """
        Test step execution with list format
        リスト形式でのステップ実行をテスト
        """
        # Mock steps
        # ステップをモック
        mock_step1 = AsyncMock()
        mock_step1.name = "step1"
        mock_step1.run = AsyncMock(return_value="result1")
        
        mock_step2 = AsyncMock()
        mock_step2.name = "step2"
        mock_step2.run = AsyncMock(return_value="result2")
        
        mixin = FlowInstrumentationMixin()
        mixin._tracer = self.tracer  # Use test tracer
        mixin.steps = [mock_step1, mock_step2]
        
        result = await mixin._execute_steps_with_instrumentation("input")
        
        assert result == "result2"
        mock_step1.run.assert_called_once_with("input")
        mock_step2.run.assert_called_once_with("result1")
        
        # Check step spans were created
        # ステップスパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 2
        
        step1_span = spans[0]
        assert step1_span.name == "step.step1"
        assert step1_span.attributes["step.name"] == "step1"
        assert step1_span.attributes["otel.lean.queue_age_ms"] == 0  # First step
        
        step2_span = spans[1]
        assert step2_span.name == "step.step2"
        assert step2_span.attributes["step.name"] == "step2"
        assert step2_span.attributes["otel.lean.queue_age_ms"] >= 0  # Second step
    
    @pytest.mark.asyncio
    async def test_execute_steps_with_dict(self):
        """
        Test step execution with dictionary format
        辞書形式でのステップ実行をテスト
        """
        # Mock steps
        # ステップをモック
        mock_step1 = AsyncMock()
        mock_step1.run = AsyncMock(return_value="result1")
        
        mock_step2 = AsyncMock()
        mock_step2.run = AsyncMock(return_value="result2")
        
        mixin = FlowInstrumentationMixin()
        mixin.steps = {
            "first_step": mock_step1,
            "second_step": mock_step2
        }
        
        result = await mixin._execute_steps_with_instrumentation("input")
        
        assert result == "result2"
        
        # Check step spans were created
        # ステップスパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 2
        
        # Note: Dict iteration order is guaranteed in Python 3.7+
        # 注意: Python 3.7+では辞書の反復順序が保証される
        step1_span = spans[0]
        assert step1_span.name == "step.first_step"
        assert step1_span.attributes["step.name"] == "first_step"
        
        step2_span = spans[1]
        assert step2_span.name == "step.second_step"
        assert step2_span.attributes["step.name"] == "second_step"
    
    @pytest.mark.asyncio
    async def test_execute_single_step(self):
        """
        Test single step execution
        単一ステップ実行をテスト
        """
        # Mock single step
        # 単一ステップをモック
        mock_step = AsyncMock()
        mock_step.name = "single_step"
        mock_step.run = AsyncMock(return_value="single_result")
        
        mixin = FlowInstrumentationMixin()
        mixin.steps = mock_step
        
        result = await mixin._execute_steps_with_instrumentation("input")
        
        assert result == "single_result"
        mock_step.run.assert_called_once_with("input")
        
        # Check step span was created
        # ステップスパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        step_span = spans[0]
        assert step_span.name == "step.single_step"
        assert step_span.attributes["step.name"] == "single_step"
    
    @pytest.mark.asyncio
    async def test_execute_single_step_with_callable(self):
        """
        Test single step execution with callable object
        呼び出し可能オブジェクトでの単一ステップ実行をテスト
        """
        # Mock callable step (no run method)
        # 呼び出し可能ステップをモック（runメソッドなし）
        async def mock_callable_step(input_data):
            return f"callable_{input_data}"
        
        mixin = FlowInstrumentationMixin()
        
        result = await mixin._execute_single_step("callable_step", mock_callable_step, "input")
        
        assert result == "callable_input"
        
        # Check step span was created
        # ステップスパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        step_span = spans[0]
        assert step_span.name == "step.callable_step"
        assert step_span.attributes["step.name"] == "callable_step"
    
    @pytest.mark.asyncio
    async def test_execute_single_step_with_error(self):
        """
        Test single step execution when step fails
        ステップが失敗した場合の単一ステップ実行をテスト
        """
        # Mock failing step
        # 失敗するステップをモック
        mock_step = AsyncMock()
        mock_step.name = "failing_step"
        mock_step.run = AsyncMock(side_effect=RuntimeError("Step failed"))
        
        mixin = FlowInstrumentationMixin()
        
        with pytest.raises(RuntimeError, match="Step failed"):
            await mixin._execute_single_step("failing_step", mock_step, "input")
        
        # Check error span was created
        # エラースパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        step_span = spans[0]
        assert step_span.name == "step.failing_step"
        assert step_span.attributes["otel.lean.gen.accepted"] is False
        assert step_span.status.status_code == StatusCode.ERROR
    
    @pytest.mark.asyncio
    async def test_instrument_original_flow(self):
        """
        Test instrumenting an existing Flow instance
        既存のFlowインスタンスの計装をテスト
        """
        # Mock original flow
        # 元のフローをモック
        original_flow = AsyncMock()
        original_flow.run = AsyncMock(return_value="original_result")
        original_flow.steps = ["step1", "step2"]
        original_flow.name = "original_flow"
        
        # Instrument the flow
        # フローを計装
        instrumented = FlowInstrumentationMixin.instrument_flow(original_flow)
        
        # Check attributes were copied
        # 属性がコピーされたことを確認
        assert instrumented.steps == ["step1", "step2"]
        assert instrumented.name == "original_flow"
        assert hasattr(instrumented, '_original_flow')
        assert instrumented._original_flow is original_flow
        
        # Test running the instrumented flow
        # 計装されたフローの実行をテスト
        result = await instrumented.run("test_input")
        
        assert result == "original_result"
        original_flow.run.assert_called_once_with("test_input")
        
        # Check span was created
        # スパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        flow_span = spans[0]
        assert flow_span.name == "flow.original_flow"
        assert flow_span.attributes["otel.lean.gen.accepted"] is True
    
    def test_update_generation_metadata_success(self):
        """
        Test updating generation metadata for successful execution
        成功実行時の生成メタデータ更新をテスト
        """
        mixin = FlowInstrumentationMixin()
        
        # Mock flow span
        # フロースパンをモック
        mock_span = Mock()
        mock_span.attributes = {"otel.lean.gen.attempt": 1}
        mixin._flow_span = mock_span
        
        mixin._update_generation_metadata(accepted=True)
        
        mock_span.set_attribute.assert_called_with("otel.lean.gen.accepted", True)
    
    def test_update_generation_metadata_failure(self):
        """
        Test updating generation metadata for failed execution
        失敗実行時の生成メタデータ更新をテスト
        """
        mixin = FlowInstrumentationMixin()
        
        # Mock flow span
        # フロースパンをモック
        mock_span = Mock()
        mock_span.attributes = {"otel.lean.gen.attempt": 1}
        mixin._flow_span = mock_span
        
        mixin._update_generation_metadata(accepted=False)
        
        # Check attempt count was incremented and accepted was set to False
        # 試行回数がインクリメントされ、acceptedがFalseに設定されたことを確認
        mock_span.set_attribute.assert_any_call("otel.lean.gen.attempt", 2)
        mock_span.set_attribute.assert_any_call("otel.lean.gen.accepted", False)
    
    @pytest.mark.asyncio
    async def test_execute_steps_no_steps(self):
        """
        Test step execution when no steps are available
        ステップが利用できない場合のステップ実行をテスト
        """
        mixin = FlowInstrumentationMixin()
        mixin.steps = []
        
        result = await mixin._execute_steps_with_instrumentation("input")
        
        # Should return input unchanged
        # 入力をそのまま返すはず
        assert result == "input"
        
        # No spans should be created
        # スパンは作成されないはず
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 0


class TestInstrumentFlowFunction:
    """
    Test cases for instrument_flow_function decorator
    instrument_flow_functionデコレーターのテストケース
    """
    
    def setup_method(self):
        """
        Set up test environment with in-memory span exporter
        インメモリスパンエクスポーターでテスト環境をセットアップ
        """
        # Set up OTEL tracing with isolated tracer
        # 独立したトレーサーでOTELトレーシングを設定
        self.span_exporter = InMemorySpanExporter()
        self.tracer_provider = TracerProvider()
        self.tracer_provider.add_span_processor(SimpleSpanProcessor(self.span_exporter))
        
        # Get a tracer from our provider
        # プロバイダーからトレーサーを取得
        self.tracer = self.tracer_provider.get_tracer(__name__)
        
        # Clear any existing spans
        # 既存のスパンをクリア
        self.span_exporter.clear()
    
    @pytest.mark.asyncio
    async def test_instrument_flow_function_success(self):
        """
        Test successful flow function instrumentation
        成功したフロー関数計装をテスト
        """
        @instrument_flow_function(tracer=self.tracer)
        async def test_flow_function(input_data):
            return f"processed_{input_data}"
        
        result = await test_flow_function("test_input")
        
        assert result == "processed_test_input"
        
        # Check span was created
        # スパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "flow_function.test_flow_function"
        assert span.attributes["function.name"] == "test_flow_function"
        assert span.attributes["otel.lean.gen.accepted"] is True
        assert span.status.status_code == StatusCode.OK
        # Generation ID should be present
        # 生成IDが存在するはず
        assert "otel.lean.gen.id" in span.attributes
        assert span.attributes["otel.lean.gen.id"].startswith("gen-")
    
    @pytest.mark.asyncio
    async def test_instrument_flow_function_error(self):
        """
        Test flow function instrumentation with error
        エラーありのフロー関数計装をテスト
        """
        @instrument_flow_function(tracer=self.tracer)
        async def failing_flow_function(input_data):
            raise ValueError("Function failed")
        
        with pytest.raises(ValueError, match="Function failed"):
            await failing_flow_function("test_input")
        
        # Check error span was created
        # エラースパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "flow_function.failing_flow_function"
        assert span.attributes["otel.lean.gen.accepted"] is False
        assert span.status.status_code == StatusCode.ERROR
        assert "Function failed" in span.status.description
    
    @pytest.mark.asyncio
    async def test_instrument_flow_function_with_args_kwargs(self):
        """
        Test flow function instrumentation with arguments and keyword arguments
        引数とキーワード引数ありのフロー関数計装をテスト
        """
        @instrument_flow_function(tracer=self.tracer)
        async def complex_flow_function(input_data, multiplier=2, prefix="result"):
            return f"{prefix}_{input_data * multiplier}"
        
        result = await complex_flow_function("test", multiplier=3, prefix="output")
        
        assert result == "output_testtesttest"
        
        # Check span was created
        # スパンが作成されたことを確認
        spans = self.span_exporter.get_finished_spans()
        assert len(spans) == 1
        
        span = spans[0]
        assert span.name == "flow_function.complex_flow_function"
        assert span.attributes["otel.lean.gen.accepted"] is True