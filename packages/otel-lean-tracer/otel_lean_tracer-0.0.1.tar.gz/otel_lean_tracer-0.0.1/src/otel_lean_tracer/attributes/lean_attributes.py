# Lean attributes data classes for OTEL-Lean-Tracer
# OTEL-Lean-Tracer用のLean属性データクラス

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class GenerationMetadata(BaseModel):
    """
    Metadata related to LLM generation process
    LLM生成プロセスに関するメタデータ
    """
    generation_id: str = Field(..., description="Unique ID for the generation request / 生成リクエストの一意なID")
    attempt_count: int = Field(default=1, ge=1, description="Number of generation attempts / 生成試行回数")
    acceptance_status: bool = Field(default=True, description="Whether the generation was accepted / 生成が受け入れられたか")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp / 作成タイムスタンプ")
    
    def update_attempt(self) -> None:
        """
        Increment the attempt counter
        試行回数をインクリメント
        """
        self.attempt_count += 1
    
    def mark_accepted(self, accepted: bool = True) -> None:
        """
        Mark the generation as accepted or rejected
        生成を受け入れ済みまたは拒否済みとしてマーク
        """
        self.acceptance_status = accepted


class ContextMetrics(BaseModel):
    """
    Metrics related to context efficiency
    コンテキスト効率に関するメトリクス
    """
    total_bytes: int = Field(default=0, ge=0, description="Total context bytes transferred / 転送された総コンテキストバイト数")
    useful_bytes: int = Field(default=0, ge=0, description="Actually used context bytes / 実際に使用されたコンテキストバイト数")
    
    @property
    def efficiency_ratio(self) -> float:
        """
        Calculate context efficiency ratio
        コンテキスト効率比を計算
        """
        if self.total_bytes == 0:
            return 0.0
        return self.useful_bytes / self.total_bytes
    
    def calculate_efficiency(self) -> float:
        """
        Calculate context efficiency as percentage
        コンテキスト効率をパーセンテージで計算
        """
        return self.efficiency_ratio * 100
    
    def is_wasteful(self, threshold: float = 0.5) -> bool:
        """
        Check if context usage is wasteful
        コンテキスト使用が無駄かどうかをチェック
        """
        return self.efficiency_ratio < threshold


class QueueMetrics(BaseModel):
    """
    Metrics related to queue waiting time
    キュー待機時間に関するメトリクス
    """
    entry_time: Optional[datetime] = Field(None, description="Queue entry timestamp / キュー入力タイムスタンプ")
    exit_time: Optional[datetime] = Field(None, description="Queue exit timestamp / キュー出力タイムスタンプ")
    age_ms: int = Field(default=0, ge=0, description="Queue age in milliseconds / キュー滞留時間（ミリ秒）")
    
    def calculate_age(self) -> int:
        """
        Calculate queue age in milliseconds
        キュー滞留時間をミリ秒で計算
        """
        if self.entry_time and self.exit_time:
            delta = self.exit_time - self.entry_time
            self.age_ms = int(delta.total_seconds() * 1000)
        return self.age_ms
    
    def is_bottleneck(self, threshold_ms: int = 5000) -> bool:
        """
        Check if queue time indicates a bottleneck
        キュー時間がボトルネックを示しているかチェック
        """
        return self.age_ms > threshold_ms


class CostMetrics(BaseModel):
    """
    Metrics related to API costs
    APIコストに関するメトリクス
    """
    provider: str = Field(default="unknown", description="LLM provider name / LLMプロバイダー名")
    model: str = Field(default="unknown", description="Model name / モデル名")
    input_tokens: int = Field(default=0, ge=0, description="Number of input tokens / 入力トークン数")
    output_tokens: int = Field(default=0, ge=0, description="Number of output tokens / 出力トークン数")
    cost_usd: float = Field(default=0.0, ge=0.0, description="Total cost in USD / 総コスト（USD）")
    
    def calculate_cost(self, price_per_1k_input: float = 0.0, price_per_1k_output: float = 0.0) -> float:
        """
        Calculate total cost based on token counts and prices
        トークン数と価格に基づいて総コストを計算
        """
        input_cost = (self.input_tokens / 1000) * price_per_1k_input
        output_cost = (self.output_tokens / 1000) * price_per_1k_output
        self.cost_usd = input_cost + output_cost
        return self.cost_usd


class EvaluationMetrics(BaseModel):
    """
    Metrics related to GenAgent evaluation and quality assessment
    GenAgentの評価と品質アセスメントに関するメトリクス
    """
    score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Evaluation score (0-100) / 評価スコア（0-100）")
    threshold: Optional[float] = Field(None, ge=0.0, le=100.0, description="Quality threshold / 品質閾値")
    passed: Optional[bool] = Field(None, description="Whether evaluation passed threshold / 評価が閾値を通過したか")
    evaluator_model: Optional[str] = Field(None, description="Model used for evaluation / 評価に使用されたモデル")
    improvement_points: Optional[List[str]] = Field(None, description="Suggested improvements / 改善提案")
    retry_reason: Optional[str] = Field(None, description="Reason for retry if score below threshold / 閾値未満の場合の再試行理由")
    evaluation_cost_usd: Optional[float] = Field(None, ge=0.0, description="Cost of evaluation process / 評価プロセスのコスト")
    
    def is_quality_pass(self) -> bool:
        """
        Check if the evaluation meets the quality threshold
        評価が品質閾値を満たしているかチェック
        """
        if self.score is None or self.threshold is None:
            return True  # Default to pass if no evaluation data
        return self.score >= self.threshold
    
    def get_quality_gap(self) -> Optional[float]:
        """
        Get the gap between score and threshold
        スコアと閾値の差を取得
        """
        if self.score is None or self.threshold is None:
            return None
        return self.threshold - self.score
    
    def should_retry(self) -> bool:
        """
        Determine if generation should be retried based on evaluation
        評価に基づいて生成を再試行すべきかどうかを判定
        """
        return not self.is_quality_pass()


class LeanSpanAttributes(BaseModel):
    """
    Complete set of Lean attributes for a span
    Span用のLean属性の完全なセット
    """
    # Generation related attributes / 生成関連属性
    gen_id: str = Field(..., description="Generation correlation ID / 生成相関ID")
    gen_attempt: int = Field(default=1, ge=1, description="Generation attempt number / 生成試行番号")
    gen_accepted: bool = Field(default=True, description="Whether generation was accepted / 生成が受け入れられたか")
    
    # Context efficiency attributes / コンテキスト効率属性
    context_bytes: int = Field(default=0, ge=0, description="Total context bytes / 総コンテキストバイト数")
    useful_bytes: int = Field(default=0, ge=0, description="Useful context bytes / 有用なコンテキストバイト数")
    
    # Queue metrics / キューメトリクス
    queue_age_ms: int = Field(default=0, ge=0, description="Queue waiting time in ms / キュー待機時間（ミリ秒）")
    
    # Evaluation attributes / 評価属性
    eval_score: Optional[float] = Field(None, ge=0.0, le=100.0, description="Evaluation score / 評価スコア")
    eval_threshold: Optional[float] = Field(None, ge=0.0, le=100.0, description="Quality threshold / 品質閾値")
    eval_passed: Optional[bool] = Field(None, description="Whether evaluation passed / 評価が通過したか")
    eval_model: Optional[str] = Field(None, description="Evaluator model / 評価モデル")
    retry_reason: Optional[str] = Field(None, description="Reason for retry / 再試行理由")
    
    # Optional attributes / オプション属性
    model_scale_b: Optional[float] = Field(None, ge=0, description="Model scale in billions of parameters / モデル規模（十億パラメータ）")
    retry_energy_kwh: Optional[float] = Field(None, ge=0, description="Estimated retry energy consumption in kWh / 再試行の推定エネルギー消費量（kWh）")
    cost_usd: float = Field(default=0.0, ge=0.0, description="API cost in USD / APIコスト（USD）")
    eval_cost_usd: Optional[float] = Field(None, ge=0.0, description="Evaluation cost in USD / 評価コスト（USD）")
    
    # Nested models / ネストされたモデル
    generation_metadata: Optional[GenerationMetadata] = None
    context_metrics: Optional[ContextMetrics] = None
    queue_metrics: Optional[QueueMetrics] = None
    cost_metrics: Optional[CostMetrics] = None
    evaluation_metrics: Optional[EvaluationMetrics] = None
    
    def validate(self) -> bool:
        """
        Validate that all required attributes are properly set
        すべての必須属性が適切に設定されているか検証
        """
        return all([
            self.gen_id,
            self.gen_attempt >= 1,
            self.context_bytes >= 0,
            self.useful_bytes >= 0,
            self.useful_bytes <= self.context_bytes,
            self.queue_age_ms >= 0,
            self.cost_usd >= 0
        ])
    
    def to_otel_attributes(self) -> Dict[str, Any]:
        """
        Convert to OpenTelemetry attribute format using semantic conventions
        OpenTelemetryセマンティック規約に従った属性形式に変換
        """
        attributes = {
            # Generation tracking - using lean namespace for custom metrics
            "otel.lean.gen.id": self.gen_id,
            "otel.lean.gen.attempt": self.gen_attempt,
            "otel.lean.gen.accepted": self.gen_accepted,
            
            # Context metrics - using llm semantic conventions
            "llm.context.bytes_total": self.context_bytes,
            "llm.context.bytes_useful": self.useful_bytes,
            
            # Queue and performance metrics
            "otel.lean.queue_age_ms": self.queue_age_ms,
            
            # Cost tracking - using llm semantic conventions
            "llm.usage.cost_usd": self.cost_usd,
        }
        
        # Add evaluation attributes if present / 評価属性が存在する場合は追加
        if self.eval_score is not None:
            attributes["llm.evaluation.score"] = self.eval_score
        if self.eval_threshold is not None:
            attributes["llm.evaluation.threshold"] = self.eval_threshold
        if self.eval_passed is not None:
            attributes["llm.evaluation.passed"] = self.eval_passed
        if self.eval_model is not None:
            attributes["llm.evaluation.model"] = self.eval_model
        if self.retry_reason is not None:
            attributes["otel.lean.retry.reason"] = self.retry_reason
        if self.eval_cost_usd is not None:
            attributes["llm.evaluation.cost_usd"] = self.eval_cost_usd
        
        # Add optional attributes if present / オプション属性が存在する場合は追加
        if self.model_scale_b is not None:
            attributes["otel.lean.model_scale_b"] = self.model_scale_b
        if self.retry_energy_kwh is not None:
            attributes["otel.lean.retry_energy_kwh"] = self.retry_energy_kwh
            
        # Add schema URL / スキーマURLを追加
        attributes["otel.lean.schema_url"] = "https://kitfactory.github.io/otel-lean-tracer/schema/0.2.0"
        
        return attributes
    
    @classmethod
    def from_metadata(
        cls,
        gen_id: str,
        generation: Optional[GenerationMetadata] = None,
        context: Optional[ContextMetrics] = None,
        queue: Optional[QueueMetrics] = None,
        cost: Optional[CostMetrics] = None,
        evaluation: Optional[EvaluationMetrics] = None
    ) -> "LeanSpanAttributes":
        """
        Create LeanSpanAttributes from metadata objects
        メタデータオブジェクトからLeanSpanAttributesを作成
        """
        attrs = cls(gen_id=gen_id)
        
        if generation:
            attrs.gen_attempt = generation.attempt_count
            attrs.gen_accepted = generation.acceptance_status
            attrs.generation_metadata = generation
            
        if context:
            attrs.context_bytes = context.total_bytes
            attrs.useful_bytes = context.useful_bytes
            attrs.context_metrics = context
            
        if queue:
            attrs.queue_age_ms = queue.calculate_age()
            attrs.queue_metrics = queue
            
        if cost:
            attrs.cost_usd = cost.cost_usd
            attrs.cost_metrics = cost
            
        if evaluation:
            attrs.eval_score = evaluation.score
            attrs.eval_threshold = evaluation.threshold
            attrs.eval_passed = evaluation.passed
            attrs.eval_model = evaluation.evaluator_model
            attrs.retry_reason = evaluation.retry_reason
            attrs.eval_cost_usd = evaluation.evaluation_cost_usd
            attrs.evaluation_metrics = evaluation
            
        return attrs