# Lean Trace Processor for OpenTelemetry
# OpenTelemetry用リーントレースプロセッサー

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, Union
from opentelemetry.sdk.trace import Span, SpanProcessor
from opentelemetry.trace import Status, StatusCode
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.trace import set_tracer_provider

from ..exporters import create_exporter
from ..attributes import (
    LeanSpanAttributes,
    GenerationMetadata,
    ContextMetrics,
    QueueMetrics,
    CostMetrics,
    EvaluationMetrics,
)
from ..utils.cost import CostCalculator
from ..utils.context import ContextAnalyzer


logger = logging.getLogger(__name__)


class LeanTraceProcessor(SpanProcessor):
    """
    OpenTelemetry Span Processor that adds Lean Production KPIs to spans
    Spanにリーン生産KPIを追加するOpenTelemetry Spanプロセッサー
    """
    
    def __init__(
        self,
        cost_calculator: Optional[CostCalculator] = None,
        context_analyzer: Optional[ContextAnalyzer] = None,
        enabled: bool = True
    ):
        """
        Initialize the Lean Trace Processor
        リーントレースプロセッサーを初期化
        """
        self.cost_calculator = cost_calculator or CostCalculator()
        self.context_analyzer = context_analyzer or ContextAnalyzer()
        self.enabled = enabled
        self._generation_metadata: Dict[str, GenerationMetadata] = {}
        self._queue_start_times: Dict[str, datetime] = {}
        
        logger.info("LeanTraceProcessor initialized with enabled=%s", enabled)
    
    def on_start(self, span: Span, parent_context: Optional[Any] = None) -> None:
        """
        Called when a span is started
        Spanが開始されたときに呼び出される
        """
        if not self.enabled:
            return
        
        try:
            # Generate or extract generation ID
            # 生成IDを生成または抽出
            gen_id = self._get_or_create_generation_id(span)
            
            # Initialize generation metadata
            # 生成メタデータを初期化
            if gen_id not in self._generation_metadata:
                self._generation_metadata[gen_id] = GenerationMetadata(
                    generation_id=gen_id
                )
            
            # Record queue entry time
            # キュー入力時間を記録
            span_id = self._get_span_id(span)
            self._queue_start_times[span_id] = datetime.utcnow()
            
            # Set initial lean attributes
            # 初期リーン属性を設定
            initial_attrs = LeanSpanAttributes(gen_id=gen_id)
            self._set_lean_attributes(span, initial_attrs)
            
            logger.debug("Lean attributes initialized for span %s with gen_id %s", 
                        span_id, gen_id)
        
        except Exception as e:
            logger.warning("Failed to process span start: %s", e)
    
    def on_end(self, span: Span) -> None:
        """
        Called when a span is ended
        Spanが終了したときに呼び出される
        """
        if not self.enabled:
            return
        
        try:
            # Extract span information
            # Span情報を抽出
            span_id = self._get_span_id(span)
            span_name = span.name
            span_attributes = dict(span.attributes) if span.attributes else {}
            
            # Get generation ID
            # 生成IDを取得
            gen_id = span_attributes.get("otel.lean.gen.id")
            if not gen_id:
                logger.warning("No generation ID found for span %s", span_id)
                return
            
            # Calculate queue metrics
            # キューメトリクスを計算
            queue_metrics = self._calculate_queue_metrics(span_id)
            
            # Extract context, cost, and evaluation information
            # コンテキスト、コスト、評価情報を抽出
            context_metrics = self._extract_context_metrics(span_attributes)
            cost_metrics = self._extract_cost_metrics(span_attributes)
            evaluation_metrics = self._extract_evaluation_metrics(span_attributes)
            
            # Update generation metadata based on span status
            # Spanステータスに基づいて生成メタデータを更新
            generation_metadata = self._generation_metadata.get(gen_id)
            if generation_metadata:
                if span.status.status_code == StatusCode.ERROR:
                    generation_metadata.mark_accepted(False)
                    generation_metadata.update_attempt()
            
            # Create comprehensive lean attributes
            # 包括的なリーン属性を作成
            lean_attrs = LeanSpanAttributes.from_metadata(
                gen_id=gen_id,
                generation=generation_metadata,
                context=context_metrics,
                queue=queue_metrics,
                cost=cost_metrics,
                evaluation=evaluation_metrics
            )
            
            # Set final lean attributes
            # 最終リーン属性を設定
            self._set_lean_attributes(span, lean_attrs)
            
            # Clean up temporary data
            # 一時データをクリーンアップ
            self._cleanup_span_data(span_id, gen_id)
            
            logger.debug("Lean attributes finalized for span %s", span_id)
        
        except Exception as e:
            logger.warning("Failed to process span end: %s", e)
    
    def shutdown(self) -> None:
        """
        Shutdown the processor
        プロセッサーをシャットダウン
        """
        logger.info("LeanTraceProcessor shutting down")
        self._generation_metadata.clear()
        self._queue_start_times.clear()
    
    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """
        Force flush any pending data
        保留中のデータを強制的にフラッシュ
        """
        return True
    
    def _get_or_create_generation_id(self, span: Span) -> str:
        """
        Get existing generation ID or create a new one
        既存の生成IDを取得するか、新しいものを作成
        """
        # Try to get from span attributes first
        # 最初にSpan属性から取得を試行
        if span.attributes:
            existing_id = span.attributes.get("gen.id") or span.attributes.get("generation_id")
            if existing_id:
                return str(existing_id)
        
        # Try to get from parent span
        # 親Spanから取得を試行
        parent_span = getattr(span, "parent", None)
        if parent_span and hasattr(parent_span, "attributes"):
            parent_gen_id = parent_span.attributes.get("otel.lean.gen.id")
            if parent_gen_id:
                return str(parent_gen_id)
        
        # Generate new ID
        # 新しいIDを生成
        return f"gen-{uuid.uuid4().hex[:8]}"
    
    def _get_span_id(self, span: Span) -> str:
        """
        Get a unique identifier for the span
        Spanの一意な識別子を取得
        """
        return f"span-{span.context.span_id:016x}" if span.context else f"span-{id(span)}"
    
    def _calculate_queue_metrics(self, span_id: str) -> Optional[QueueMetrics]:
        """
        Calculate queue waiting time metrics
        キュー待機時間メトリクスを計算
        """
        start_time = self._queue_start_times.get(span_id)
        if not start_time:
            return None
        
        end_time = datetime.utcnow()
        queue_metrics = QueueMetrics(
            entry_time=start_time,
            exit_time=end_time
        )
        queue_metrics.calculate_age()
        
        return queue_metrics
    
    def _extract_context_metrics(self, span_attributes: Dict[str, Any]) -> Optional[ContextMetrics]:
        """
        Extract context efficiency metrics from span attributes
        Span属性からコンテキスト効率メトリクスを抽出
        """
        # Look for context-related attributes
        # コンテキスト関連属性を探す
        prompt = span_attributes.get("llm.prompt") or span_attributes.get("gen.system") or ""
        response = span_attributes.get("llm.response") or span_attributes.get("gen.choices.0.message.content") or ""
        
        if prompt:
            total_bytes = self.context_analyzer.calculate_context_bytes(prompt)
            useful_bytes = self.context_analyzer.estimate_useful_bytes(prompt, response)
            
            return ContextMetrics(
                total_bytes=total_bytes,
                useful_bytes=useful_bytes
            )
        
        return None
    
    def _extract_cost_metrics(self, span_attributes: Dict[str, Any]) -> Optional[CostMetrics]:
        """
        Extract and calculate cost metrics from span attributes
        Span属性からコストメトリクスを抽出・計算
        """
        # Extract provider and model information
        # プロバイダーとモデル情報を抽出
        provider = span_attributes.get("gen.system") or span_attributes.get("llm.system") or "unknown"
        model = span_attributes.get("gen.model") or span_attributes.get("llm.request.model") or "unknown"
        
        # Extract token usage
        # トークン使用量を抽出
        input_tokens = self._safe_int(span_attributes.get("llm.usage.prompt_tokens") or 
                                     span_attributes.get("gen.usage.prompt_tokens") or 0)
        output_tokens = self._safe_int(span_attributes.get("llm.usage.completion_tokens") or 
                                      span_attributes.get("gen.usage.completion_tokens") or 0)
        
        if input_tokens > 0 or output_tokens > 0:
            cost_metrics = CostMetrics(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            # Calculate cost
            # コストを計算
            cost_metrics.cost_usd = self.cost_calculator.calculate_cost(
                provider=provider,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            return cost_metrics
        
        return None
    
    def _extract_evaluation_metrics(self, span_attributes: Dict[str, Any]) -> Optional[EvaluationMetrics]:
        """
        Extract evaluation metrics from span attributes (from agents-sdk-models GenAgent)
        Span属性から評価メトリクスを抽出（agents-sdk-models GenAgentから）
        """
        # Look for agents-sdk-models evaluation attributes
        # agents-sdk-models評価属性を探す
        
        # GenAgent evaluation score (0-100)
        # GenAgent評価スコア（0-100）
        score = self._safe_float(span_attributes.get("gen.evaluation.score") or 
                                span_attributes.get("eval.score") or
                                span_attributes.get("agents.evaluation.score"))
        
        # Quality threshold setting
        # 品質閾値設定
        threshold = self._safe_float(span_attributes.get("gen.evaluation.threshold") or
                                   span_attributes.get("eval.threshold") or
                                   span_attributes.get("agents.threshold") or
                                   span_attributes.get("gen.threshold"))
        
        # Evaluation status
        # 評価ステータス
        passed = span_attributes.get("gen.evaluation.passed") or span_attributes.get("eval.passed")
        if passed is not None:
            passed = bool(passed)
        
        # Evaluator model information
        # 評価モデル情報
        evaluator_model = (span_attributes.get("gen.evaluation.model") or 
                          span_attributes.get("eval.model") or
                          span_attributes.get("agents.evaluation.model"))
        
        # Retry reason (why score was below threshold)
        # 再試行理由（スコアが閾値未満だった理由）
        retry_reason = (span_attributes.get("gen.retry.reason") or
                       span_attributes.get("retry.reason") or
                       span_attributes.get("agents.retry.reason"))
        
        # Improvement points from evaluation
        # 評価からの改善点
        improvement_points_str = (span_attributes.get("gen.evaluation.improvements") or
                                 span_attributes.get("eval.improvements"))
        improvement_points = None
        if improvement_points_str:
            try:
                # Assume comma-separated or JSON format
                # カンマ区切りまたはJSON形式と仮定
                if improvement_points_str.startswith('['):
                    import json
                    improvement_points = json.loads(improvement_points_str)
                else:
                    improvement_points = [p.strip() for p in improvement_points_str.split(',') if p.strip()]
            except (json.JSONDecodeError, ValueError):
                improvement_points = [improvement_points_str]
        
        # Evaluation cost (if tracked separately)
        # 評価コスト（別途追跡されている場合）
        eval_cost = self._safe_float(span_attributes.get("gen.evaluation.cost_usd") or
                                   span_attributes.get("eval.cost_usd"))
        
        # Create evaluation metrics if we have any evaluation data
        # 評価データがある場合は評価メトリクスを作成
        if any([score is not None, threshold is not None, passed is not None, 
                evaluator_model, retry_reason, improvement_points, eval_cost is not None]):
            
            # Auto-calculate passed status if we have score and threshold
            # スコアと閾値がある場合は通過ステータスを自動計算
            if passed is None and score is not None and threshold is not None:
                passed = score >= threshold
            
            evaluation_metrics = EvaluationMetrics(
                score=score,
                threshold=threshold,
                passed=passed,
                evaluator_model=evaluator_model,
                improvement_points=improvement_points,
                retry_reason=retry_reason,
                evaluation_cost_usd=eval_cost
            )
            
            logger.debug("Extracted evaluation metrics: score=%s, threshold=%s, passed=%s", 
                        score, threshold, passed)
            
            return evaluation_metrics
        
        return None
    
    def _safe_float(self, value: Any) -> Optional[float]:
        """
        Safely convert value to float
        値を安全にfloatに変換
        """
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value: Any) -> int:
        """
        Safely convert value to integer
        値を安全に整数に変換
        """
        try:
            return int(value) if value is not None else 0
        except (ValueError, TypeError):
            return 0
    
    def _set_lean_attributes(self, span: Span, lean_attrs: LeanSpanAttributes) -> None:
        """
        Set lean attributes on the span
        SpanにLean属性を設定
        """
        # Check if span is writable (not ReadableSpan)
        # Spanが書き込み可能か確認（ReadableSpanではない）
        if not hasattr(span, 'set_attribute'):
            logger.debug("Cannot set attributes on ReadableSpan, skipping")
            return
        
        try:
            otel_attrs = lean_attrs.to_otel_attributes()
            for key, value in otel_attrs.items():
                if value is not None:
                    span.set_attribute(key, value)
        except Exception as e:
            logger.warning("Failed to set lean attributes: %s", e)
    
    def _cleanup_span_data(self, span_id: str, gen_id: str) -> None:
        """
        Clean up temporary data for completed spans
        完了したSpanの一時データをクリーンアップ
        """
        # Remove queue start time
        # キュー開始時間を削除
        self._queue_start_times.pop(span_id, None)
        
        # Keep generation metadata for potential retries
        # 潜在的な再試行のため生成メタデータを保持
        # (In a production system, you might want to implement cleanup based on time)
        # (本番システムでは、時間に基づくクリーンアップを実装することを検討)


def instrument_lean(
    service_name: str = "otel-lean-tracer",
    otlp_endpoint: Optional[str] = None,
    console_export: bool = False,
    enabled: bool = True
) -> None:
    """
    Instrument OpenTelemetry with Lean Production KPIs
    リーン生産KPIでOpenTelemetryを計装
    """
    if not enabled:
        logger.info("Lean instrumentation is disabled")
        return
    
    # Create tracer provider
    # トレーサープロバイダーを作成
    tracer_provider = TracerProvider()
    set_tracer_provider(tracer_provider)
    
    # Add Lean processor
    # Leanプロセッサーを追加
    lean_processor = LeanTraceProcessor(enabled=enabled)
    tracer_provider.add_span_processor(lean_processor)
    
    # Add exporters
    # エクスポーターを追加
    if console_export:
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(
            BatchSpanProcessor(console_exporter)
        )
    
    # Use ExporterFactory for flexible backend configuration
    # 柔軟なバックエンド設定のためにExporterFactoryを使用
    try:
        exporter = create_exporter()
        tracer_provider.add_span_processor(
            BatchSpanProcessor(exporter)
        )
        logger.info("Exporter configured using ExporterFactory")
    except Exception as e:
        logger.warning("Failed to configure exporter: %s", e)
        if not console_export:
            # Fallback to console if exporter creation fails and no console export
            # エクスポーター作成が失敗し、コンソールエクスポートがない場合はコンソールにフォールバック
            console_exporter = ConsoleSpanExporter()
            tracer_provider.add_span_processor(
                BatchSpanProcessor(console_exporter)
            )
            logger.info("Fallback to console exporter")
    
    # Legacy OTLP endpoint support (will be deprecated)
    # 従来のOTLPエンドポイントサポート（将来廃止予定）
    if otlp_endpoint:
        logger.warning("OTLP_ENDPOINT is deprecated. Use OTEL_LEAN_BACKEND environment variable instead.")
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
            tracer_provider.add_span_processor(
                BatchSpanProcessor(otlp_exporter)
            )
            logger.info("Legacy OTLP exporter configured for endpoint: %s", otlp_endpoint)
        except Exception as e:
            logger.warning("Failed to configure legacy OTLP exporter: %s", e)
    
    logger.info("Lean instrumentation initialized with service_name='%s'", service_name)