# Flow Instrumentation Mixin for agents-sdk-models integration
# agents-sdk-models統合用フロー計装ミックスイン

import uuid
import time
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Union, TYPE_CHECKING
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..attributes import LeanSpanAttributes, GenerationMetadata, QueueMetrics, EvaluationMetrics

# Import agents-sdk-models types only for type checking
# タイプチェック時のみagents-sdk-modelsをインポート
if TYPE_CHECKING:
    try:
        from agents_sdk_models.flow import Flow
        from agents_sdk_models.step import Step
    except ImportError:
        Flow = Any
        Step = Any

logger = logging.getLogger(__name__)


class FlowInstrumentationMixin:
    """
    Mixin class to add Lean instrumentation to agents-sdk-models Flow
    agents-sdk-modelsのFlowにLean計装を追加するミックスインクラス
    
    Usage:
    ------
    # Option 1: Create instrumented Flow class
    class InstrumentedFlow(FlowInstrumentationMixin, Flow):
        pass
    
    # Option 2: Apply mixin to existing Flow instance
    original_flow = Flow(steps=my_steps)
    instrumented_flow = FlowInstrumentationMixin.instrument_flow(original_flow)
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the mixin with instrumentation capabilities
        計装機能付きでミックスインを初期化
        """
        super().__init__(*args, **kwargs)
        self._tracer = trace.get_tracer(__name__)
        self._generation_id = f"gen-{uuid.uuid4().hex[:8]}"
        self._step_start_times: Dict[str, datetime] = {}
        self._flow_span: Optional[Any] = None
        
        logger.debug("FlowInstrumentationMixin initialized with gen_id: %s", self._generation_id)
    
    async def run(self, input_data: Any, **kwargs) -> Any:
        """
        Instrumented version of Flow.run()
        計装版のFlow.run()
        """
        # Start flow span
        # フロースパンを開始
        with self._tracer.start_as_current_span(
            name=f"flow.{getattr(self, 'name', 'unknown')}",
            attributes={
                "otel.lean.gen.id": self._generation_id,
                "flow.type": "agents_sdk_models",
                "flow.input_type": type(input_data).__name__
            }
        ) as flow_span:
            self._flow_span = flow_span
            
            try:
                # Call original run method
                # 元のrunメソッドを呼び出し
                result = await self._instrumented_run(input_data, **kwargs)
                
                # Mark as successful
                # 成功としてマーク
                flow_span.set_status(Status(StatusCode.OK))
                flow_span.set_attribute("otel.lean.gen.accepted", True)
                
                return result
                
            except Exception as e:
                # Mark as failed and increment attempt
                # 失敗としてマークし、試行回数をインクリメント
                flow_span.set_status(Status(StatusCode.ERROR, str(e)))
                flow_span.set_attribute("otel.lean.gen.accepted", False)
                
                # Update generation metadata
                # 生成メタデータを更新
                self._update_generation_metadata(accepted=False)
                
                logger.warning("Flow execution failed: %s", e)
                raise
            
            finally:
                self._flow_span = None
    
    async def _instrumented_run(self, input_data: Any, **kwargs) -> Any:
        """
        Internal method to handle the actual flow execution with instrumentation
        計装付きの実際のフロー実行を処理する内部メソッド
        """
        # If instrumenting an existing Flow instance, call its run method
        # 既存のFlowインスタンスを計装している場合、そのrunメソッドを呼び出し
        if hasattr(self, '_original_flow'):
            return await self._instrument_original_flow_run(input_data, **kwargs)
        
        # Fallback: basic step execution
        # フォールバック: 基本的なステップ実行
        return await self._execute_steps_with_instrumentation(input_data, **kwargs)
    
    async def _instrument_super_run(self, input_data: Any, **kwargs) -> Any:
        """
        Instrument the parent class's run method
        親クラスのrunメソッドを計装
        """
        return await super().run(input_data, **kwargs)
    
    async def _instrument_original_flow_run(self, input_data: Any, **kwargs) -> Any:
        """
        Instrument an existing Flow instance's run method
        既存のFlowインスタンスのrunメソッドを計装
        """
        original_flow = getattr(self, '_original_flow')
        return await original_flow.run(input_data, **kwargs)
    
    async def _execute_steps_with_instrumentation(self, input_data: Any, **kwargs) -> Any:
        """
        Execute steps with instrumentation when no original Flow is available
        元のFlowが利用できない場合の計装付きステップ実行
        """
        steps = getattr(self, 'steps', [])
        if not steps:
            logger.warning("No steps found in Flow")
            return input_data
        
        current_data = input_data
        
        # Handle different step formats
        # 異なるステップ形式を処理
        if isinstance(steps, dict):
            # Dictionary format: {"step1": step1, "step2": step2}
            for step_name, step in steps.items():
                current_data = await self._execute_single_step(step_name, step, current_data)
        elif isinstance(steps, list):
            # List format: [step1, step2, step3]
            for i, step in enumerate(steps):
                step_name = getattr(step, 'name', f"step_{i}")
                current_data = await self._execute_single_step(step_name, step, current_data)
        else:
            # Single step
            step_name = getattr(steps, 'name', 'single_step')
            current_data = await self._execute_single_step(step_name, steps, current_data)
        
        return current_data
    
    async def _execute_single_step(self, step_name: str, step: Any, input_data: Any) -> Any:
        """
        Execute a single step with instrumentation
        単一ステップを計装付きで実行
        """
        # Record step start time
        # ステップ開始時間を記録
        step_start_time = datetime.utcnow()
        self._step_start_times[step_name] = step_start_time
        
        # Calculate queue age if there was a previous step
        # 前のステップがあった場合、キュー滞留時間を計算
        queue_age_ms = 0
        if len(self._step_start_times) > 1:
            previous_times = list(self._step_start_times.values())[:-1]
            if previous_times:
                last_step_time = max(previous_times)
                queue_age_ms = int((step_start_time - last_step_time).total_seconds() * 1000)
        
        # Extract step configuration for evaluation tracking
        # 評価追跡用のステップ設定を抽出
        step_threshold = getattr(step, 'threshold', None)
        step_evaluator = getattr(step, 'evaluator', None)
        
        # Start step span
        # ステップスパンを開始
        with self._tracer.start_as_current_span(
            name=f"step.{step_name}",
            attributes={
                "otel.lean.gen.id": self._generation_id,
                "step.name": step_name,
                "step.type": type(step).__name__,
                "otel.lean.queue_age_ms": queue_age_ms,
                **({"gen.threshold": step_threshold} if step_threshold is not None else {}),
                **({"eval.model": str(step_evaluator)} if step_evaluator is not None else {})
            }
        ) as step_span:
            
            try:
                # Execute step
                # ステップを実行
                if hasattr(step, 'run'):
                    result = await step.run(input_data)
                elif hasattr(step, '__call__'):
                    result = await step(input_data) if callable(step) else step
                else:
                    logger.warning("Step %s is not callable", step_name)
                    result = input_data
                
                # Extract evaluation data from result if available
                # 結果から評価データを抽出（利用可能な場合）
                self._extract_and_set_evaluation_data(step_span, step, result)
                
                # Mark step as successful
                # ステップを成功としてマーク
                step_span.set_status(Status(StatusCode.OK))
                step_span.set_attribute("otel.lean.gen.accepted", True)
                
                return result
                
            except Exception as e:
                # Mark step as failed
                # ステップを失敗としてマーク
                step_span.set_status(Status(StatusCode.ERROR, str(e)))
                step_span.set_attribute("otel.lean.gen.accepted", False)
                
                # Handle evaluation-based retries
                # 評価ベースの再試行を処理
                self._handle_evaluation_failure(step_span, step, e)
                
                # Update generation metadata for retry
                # 再試行のため生成メタデータを更新
                self._update_generation_metadata(accepted=False)
                
                logger.warning("Step %s failed: %s", step_name, e)
                raise
    
    def _update_generation_metadata(self, accepted: bool = True) -> None:
        """
        Update generation metadata for the current flow
        現在のフローの生成メタデータを更新
        """
        if self._flow_span:
            current_attempt = self._flow_span.attributes.get("otel.lean.gen.attempt", 1)
            if not accepted:
                # Increment attempt count on failure
                # 失敗時に試行回数をインクリメント
                self._flow_span.set_attribute("otel.lean.gen.attempt", current_attempt + 1)
            
            self._flow_span.set_attribute("otel.lean.gen.accepted", accepted)
    
    @classmethod
    def instrument_flow(cls, flow_instance: Any) -> 'FlowInstrumentationMixin':
        """
        Apply instrumentation to an existing Flow instance
        既存のFlowインスタンスに計装を適用
        
        Args:
            flow_instance: The Flow instance to instrument
        
        Returns:
            Instrumented flow instance
        """
        # Create a new instance that wraps the original flow
        # 元のフローをラップする新しいインスタンスを作成
        instrumented = cls()
        instrumented._original_flow = flow_instance
        
        # Copy attributes from original flow
        # 元のフローから属性をコピー
        for attr in ['steps', 'name']:
            if hasattr(flow_instance, attr):
                setattr(instrumented, attr, getattr(flow_instance, attr))
        
        logger.info("Flow instance instrumented with Lean tracing")
        return instrumented
    
    def set_generation_id(self, gen_id: str) -> None:
        """
        Set a custom generation ID
        カスタム生成IDを設定
        """
        self._generation_id = gen_id
        logger.debug("Generation ID updated to: %s", gen_id)
    
    def get_generation_id(self) -> str:
        """
        Get the current generation ID
        現在の生成IDを取得
        """
        return self._generation_id
    
    def _extract_and_set_evaluation_data(self, span: Any, step: Any, result: Any) -> None:
        """
        Extract evaluation data from step result and set as span attributes
        ステップ結果から評価データを抽出し、Span属性として設定
        """
        try:
            # Check for evaluation data in step itself (GenAgent)
            # ステップ自体（GenAgent）の評価データをチェック
            if hasattr(step, 'last_evaluation'):
                evaluation = getattr(step, 'last_evaluation')
                if evaluation:
                    self._set_evaluation_attributes(span, evaluation)
                    return
            
            # Check for evaluation data in result
            # 結果内の評価データをチェック
            if hasattr(result, 'evaluation'):
                evaluation = getattr(result, 'evaluation')
                if evaluation:
                    self._set_evaluation_attributes(span, evaluation)
                    return
            
            # Check for evaluation data as dict in result
            # 結果内の辞書形式の評価データをチェック
            if isinstance(result, dict):
                if 'evaluation' in result:
                    self._set_evaluation_attributes(span, result['evaluation'])
                    return
                
                # Check for direct evaluation fields in result
                # 結果内の直接的な評価フィールドをチェック
                if any(key in result for key in ['score', 'evaluation_score', 'quality_score']):
                    evaluation_data = {}
                    for score_key in ['score', 'evaluation_score', 'quality_score']:
                        if score_key in result:
                            evaluation_data['score'] = result[score_key]
                            break
                    
                    # Look for threshold in result or step
                    # 結果またはステップ内の閾値を探す
                    threshold = (result.get('threshold') or 
                               result.get('quality_threshold') or
                               getattr(step, 'threshold', None))
                    if threshold is not None:
                        evaluation_data['threshold'] = threshold
                    
                    # Look for evaluator info
                    # 評価者情報を探す
                    evaluator = (result.get('evaluator') or 
                               result.get('eval_model') or
                               getattr(step, 'evaluator', None))
                    if evaluator is not None:
                        evaluation_data['evaluator_model'] = str(evaluator)
                    
                    # Look for improvement points
                    # 改善点を探す
                    improvements = (result.get('improvements') or 
                                  result.get('feedback') or
                                  result.get('suggestions'))
                    if improvements:
                        if isinstance(improvements, str):
                            evaluation_data['improvement_points'] = [improvements]
                        elif isinstance(improvements, list):
                            evaluation_data['improvement_points'] = improvements
                    
                    if evaluation_data:
                        self._set_evaluation_attributes_from_dict(span, evaluation_data)
            
        except Exception as e:
            logger.debug("Failed to extract evaluation data: %s", e)
    
    def _set_evaluation_attributes(self, span: Any, evaluation: Any) -> None:
        """
        Set evaluation attributes from evaluation object
        評価オブジェクトから評価属性を設定
        """
        try:
            # Handle different evaluation object formats
            # 異なる評価オブジェクト形式を処理
            if hasattr(evaluation, 'score'):
                span.set_attribute("gen.evaluation.score", float(evaluation.score))
            
            if hasattr(evaluation, 'threshold'):
                span.set_attribute("gen.evaluation.threshold", float(evaluation.threshold))
            
            if hasattr(evaluation, 'passed'):
                span.set_attribute("gen.evaluation.passed", bool(evaluation.passed))
            
            if hasattr(evaluation, 'model'):
                span.set_attribute("gen.evaluation.model", str(evaluation.model))
            
            if hasattr(evaluation, 'feedback') or hasattr(evaluation, 'improvements'):
                feedback = getattr(evaluation, 'feedback', None) or getattr(evaluation, 'improvements', None)
                if feedback:
                    if isinstance(feedback, list):
                        span.set_attribute("gen.evaluation.improvements", ','.join(str(f) for f in feedback))
                    else:
                        span.set_attribute("gen.evaluation.improvements", str(feedback))
            
            # Calculate passed status if not explicitly set
            # 明示的に設定されていない場合は通過ステータスを計算
            if (hasattr(evaluation, 'score') and hasattr(evaluation, 'threshold') and 
                not hasattr(evaluation, 'passed')):
                passed = evaluation.score >= evaluation.threshold
                span.set_attribute("gen.evaluation.passed", passed)
                
        except Exception as e:
            logger.debug("Failed to set evaluation attributes from object: %s", e)
    
    def _set_evaluation_attributes_from_dict(self, span: Any, evaluation_data: Dict[str, Any]) -> None:
        """
        Set evaluation attributes from dictionary
        辞書から評価属性を設定
        """
        try:
            if 'score' in evaluation_data:
                span.set_attribute("gen.evaluation.score", float(evaluation_data['score']))
            
            if 'threshold' in evaluation_data:
                span.set_attribute("gen.evaluation.threshold", float(evaluation_data['threshold']))
            
            if 'passed' in evaluation_data:
                span.set_attribute("gen.evaluation.passed", bool(evaluation_data['passed']))
            
            if 'evaluator_model' in evaluation_data:
                span.set_attribute("gen.evaluation.model", str(evaluation_data['evaluator_model']))
            
            if 'improvement_points' in evaluation_data:
                improvements = evaluation_data['improvement_points']
                if isinstance(improvements, list):
                    span.set_attribute("gen.evaluation.improvements", ','.join(str(i) for i in improvements))
                else:
                    span.set_attribute("gen.evaluation.improvements", str(improvements))
            
            # Auto-calculate passed status
            # 通過ステータスを自動計算
            if ('score' in evaluation_data and 'threshold' in evaluation_data and 
                'passed' not in evaluation_data):
                passed = evaluation_data['score'] >= evaluation_data['threshold']
                span.set_attribute("gen.evaluation.passed", passed)
                
        except Exception as e:
            logger.debug("Failed to set evaluation attributes from dict: %s", e)
    
    def _handle_evaluation_failure(self, span: Any, step: Any, exception: Exception) -> None:
        """
        Handle evaluation-based failures and set retry reasons
        評価ベースの失敗を処理し、再試行理由を設定
        """
        try:
            # Check if failure was due to evaluation threshold
            # 失敗が評価閾値によるものかチェック
            error_message = str(exception).lower()
            
            if any(keyword in error_message for keyword in ['threshold', 'quality', 'score', 'evaluation']):
                span.set_attribute("gen.retry.reason", "evaluation_threshold_not_met")
            elif 'timeout' in error_message:
                span.set_attribute("gen.retry.reason", "timeout")
            elif 'rate_limit' in error_message or 'rate limit' in error_message:
                span.set_attribute("gen.retry.reason", "rate_limit")
            else:
                span.set_attribute("gen.retry.reason", "general_error")
            
            # Extract threshold information if available
            # 利用可能な場合は閾値情報を抽出
            threshold = getattr(step, 'threshold', None)
            if threshold is not None:
                span.set_attribute("gen.evaluation.threshold", float(threshold))
                
        except Exception as e:
            logger.debug("Failed to handle evaluation failure: %s", e)


def instrument_flow_function(flow_func=None, *, tracer=None):
    """
    Decorator to instrument a function that creates and runs a Flow
    Flowを作成・実行する関数を計装するデコレーター
    
    Usage:
    ------
    @instrument_flow_function
    async def my_flow_function(input_data):
        flow = Flow(steps=my_steps)
        return await flow.run(input_data)
    
    # With custom tracer (for testing)
    @instrument_flow_function(tracer=custom_tracer)
    async def my_flow_function(input_data):
        flow = Flow(steps=my_steps)
        return await flow.run(input_data)
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Use provided tracer or get default
            # 提供されたトレーサーまたはデフォルトを使用
            _tracer = tracer or trace.get_tracer(__name__)
            gen_id = f"gen-{uuid.uuid4().hex[:8]}"
            
            with _tracer.start_as_current_span(
                name=f"flow_function.{func.__name__}",
                attributes={
                    "otel.lean.gen.id": gen_id,
                    "function.name": func.__name__
                }
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    span.set_attribute("otel.lean.gen.accepted", True)
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("otel.lean.gen.accepted", False)
                    raise
        
        return wrapper
    
    # Handle both @instrument_flow_function and @instrument_flow_function()
    # @instrument_flow_functionと@instrument_flow_function()の両方を処理
    if flow_func is None:
        return decorator
    else:
        return decorator(flow_func)