# Test cases for Lean attributes data classes
# Lean属性データクラスのテストケース

import pytest
from datetime import datetime, timedelta
from otel_lean_tracer.attributes import (
    LeanSpanAttributes,
    GenerationMetadata,
    ContextMetrics,
    QueueMetrics,
    CostMetrics,
)


class TestGenerationMetadata:
    """
    Test cases for GenerationMetadata class
    GenerationMetadataクラスのテストケース
    """
    
    def test_create_generation_metadata(self):
        """
        Test creating a GenerationMetadata instance
        GenerationMetadataインスタンスの作成をテスト
        """
        gen_meta = GenerationMetadata(generation_id="gen-123")
        assert gen_meta.generation_id == "gen-123"
        assert gen_meta.attempt_count == 1
        assert gen_meta.acceptance_status is True
        assert isinstance(gen_meta.created_at, datetime)
    
    def test_update_attempt(self):
        """
        Test updating attempt count
        試行回数の更新をテスト
        """
        gen_meta = GenerationMetadata(generation_id="gen-123")
        gen_meta.update_attempt()
        assert gen_meta.attempt_count == 2
        gen_meta.update_attempt()
        assert gen_meta.attempt_count == 3
    
    def test_mark_accepted(self):
        """
        Test marking generation as accepted/rejected
        生成の受け入れ/拒否マーキングをテスト
        """
        gen_meta = GenerationMetadata(generation_id="gen-123")
        gen_meta.mark_accepted(False)
        assert gen_meta.acceptance_status is False
        gen_meta.mark_accepted(True)
        assert gen_meta.acceptance_status is True


class TestContextMetrics:
    """
    Test cases for ContextMetrics class
    ContextMetricsクラスのテストケース
    """
    
    def test_create_context_metrics(self):
        """
        Test creating a ContextMetrics instance
        ContextMetricsインスタンスの作成をテスト
        """
        context = ContextMetrics(total_bytes=1000, useful_bytes=500)
        assert context.total_bytes == 1000
        assert context.useful_bytes == 500
    
    def test_efficiency_ratio(self):
        """
        Test calculating efficiency ratio
        効率比の計算をテスト
        """
        context = ContextMetrics(total_bytes=1000, useful_bytes=750)
        assert context.efficiency_ratio == 0.75
        
        # Test with zero total bytes
        context_zero = ContextMetrics(total_bytes=0, useful_bytes=0)
        assert context_zero.efficiency_ratio == 0.0
    
    def test_calculate_efficiency(self):
        """
        Test calculating efficiency percentage
        効率パーセンテージの計算をテスト
        """
        context = ContextMetrics(total_bytes=1000, useful_bytes=600)
        assert context.calculate_efficiency() == 60.0
    
    def test_is_wasteful(self):
        """
        Test checking if context usage is wasteful
        コンテキスト使用が無駄かどうかのチェックをテスト
        """
        # Efficient usage
        context_efficient = ContextMetrics(total_bytes=1000, useful_bytes=800)
        assert not context_efficient.is_wasteful(threshold=0.5)
        
        # Wasteful usage
        context_wasteful = ContextMetrics(total_bytes=1000, useful_bytes=300)
        assert context_wasteful.is_wasteful(threshold=0.5)


class TestQueueMetrics:
    """
    Test cases for QueueMetrics class
    QueueMetricsクラスのテストケース
    """
    
    def test_create_queue_metrics(self):
        """
        Test creating a QueueMetrics instance
        QueueMetricsインスタンスの作成をテスト
        """
        now = datetime.utcnow()
        queue = QueueMetrics(entry_time=now, exit_time=now + timedelta(seconds=2))
        assert queue.entry_time == now
        assert queue.exit_time == now + timedelta(seconds=2)
    
    def test_calculate_age(self):
        """
        Test calculating queue age
        キュー滞留時間の計算をテスト
        """
        now = datetime.utcnow()
        queue = QueueMetrics(
            entry_time=now,
            exit_time=now + timedelta(milliseconds=1500)
        )
        age = queue.calculate_age()
        assert age == 1500
        assert queue.age_ms == 1500
    
    def test_is_bottleneck(self):
        """
        Test checking if queue indicates a bottleneck
        キューがボトルネックを示しているかのチェックをテスト
        """
        # Fast queue
        queue_fast = QueueMetrics(age_ms=1000)
        assert not queue_fast.is_bottleneck(threshold_ms=5000)
        
        # Slow queue (bottleneck)
        queue_slow = QueueMetrics(age_ms=10000)
        assert queue_slow.is_bottleneck(threshold_ms=5000)


class TestCostMetrics:
    """
    Test cases for CostMetrics class
    CostMetricsクラスのテストケース
    """
    
    def test_create_cost_metrics(self):
        """
        Test creating a CostMetrics instance
        CostMetricsインスタンスの作成をテスト
        """
        cost = CostMetrics(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500
        )
        assert cost.provider == "openai"
        assert cost.model == "gpt-4"
        assert cost.input_tokens == 1000
        assert cost.output_tokens == 500
    
    def test_calculate_cost(self):
        """
        Test calculating API cost
        APIコストの計算をテスト
        """
        cost = CostMetrics(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500
        )
        # GPT-4 pricing example: $0.03 per 1K input, $0.06 per 1K output
        total_cost = cost.calculate_cost(
            price_per_1k_input=0.03,
            price_per_1k_output=0.06
        )
        assert total_cost == 0.06  # (1000/1000 * 0.03) + (500/1000 * 0.06)
        assert cost.cost_usd == 0.06


class TestLeanSpanAttributes:
    """
    Test cases for LeanSpanAttributes class
    LeanSpanAttributesクラスのテストケース
    """
    
    def test_create_lean_span_attributes(self):
        """
        Test creating a LeanSpanAttributes instance
        LeanSpanAttributesインスタンスの作成をテスト
        """
        attrs = LeanSpanAttributes(gen_id="gen-123")
        assert attrs.gen_id == "gen-123"
        assert attrs.gen_attempt == 1
        assert attrs.gen_accepted is True
        assert attrs.context_bytes == 0
        assert attrs.useful_bytes == 0
        assert attrs.queue_age_ms == 0
        assert attrs.cost_usd == 0.0
    
    def test_validate(self):
        """
        Test validation of attributes
        属性の検証をテスト
        """
        # Valid attributes
        attrs_valid = LeanSpanAttributes(
            gen_id="gen-123",
            context_bytes=1000,
            useful_bytes=500
        )
        assert attrs_valid.validate()
        
        # Invalid: useful_bytes > context_bytes
        attrs_invalid = LeanSpanAttributes(
            gen_id="gen-123",
            context_bytes=500,
            useful_bytes=1000
        )
        assert not attrs_invalid.validate()
    
    def test_to_otel_attributes(self):
        """
        Test converting to OpenTelemetry attributes
        OpenTelemetry属性への変換をテスト
        """
        attrs = LeanSpanAttributes(
            gen_id="gen-123",
            gen_attempt=2,
            gen_accepted=False,
            context_bytes=1000,
            useful_bytes=750,
            queue_age_ms=1500,
            cost_usd=0.05,
            model_scale_b=175.0,
            retry_energy_kwh=0.002
        )
        
        otel_attrs = attrs.to_otel_attributes()
        
        assert otel_attrs["otel.lean.gen.id"] == "gen-123"
        assert otel_attrs["otel.lean.gen.attempt"] == 2
        assert otel_attrs["otel.lean.gen.accepted"] is False
        assert otel_attrs["otel.lean.context_bytes"] == 1000
        assert otel_attrs["otel.lean.useful_bytes"] == 750
        assert otel_attrs["otel.lean.queue_age_ms"] == 1500
        assert otel_attrs["otel.lean.cost_usd"] == 0.05
        assert otel_attrs["otel.lean.model_scale_b"] == 175.0
        assert otel_attrs["otel.lean.retry_energy_kwh"] == 0.002
        assert otel_attrs["otel.lean.schema_url"] == "https://kitfactory.github.io/otel-lean-tracer/schema/0.2.0"
    
    def test_to_otel_attributes_without_optional(self):
        """
        Test converting to OpenTelemetry attributes without optional fields
        オプションフィールドなしでのOpenTelemetry属性への変換をテスト
        """
        attrs = LeanSpanAttributes(gen_id="gen-123")
        otel_attrs = attrs.to_otel_attributes()
        
        # Optional attributes should not be present
        assert "otel.lean.model_scale_b" not in otel_attrs
        assert "otel.lean.retry_energy_kwh" not in otel_attrs
    
    def test_from_metadata(self):
        """
        Test creating LeanSpanAttributes from metadata objects
        メタデータオブジェクトからLeanSpanAttributesを作成するテスト
        """
        # Create metadata objects
        gen_meta = GenerationMetadata(generation_id="gen-123", attempt_count=3)
        context_meta = ContextMetrics(total_bytes=2000, useful_bytes=1500)
        queue_meta = QueueMetrics(age_ms=2500)
        cost_meta = CostMetrics(cost_usd=0.08)
        
        # Create attributes from metadata
        attrs = LeanSpanAttributes.from_metadata(
            gen_id="gen-123",
            generation=gen_meta,
            context=context_meta,
            queue=queue_meta,
            cost=cost_meta
        )
        
        assert attrs.gen_id == "gen-123"
        assert attrs.gen_attempt == 3
        assert attrs.context_bytes == 2000
        assert attrs.useful_bytes == 1500
        assert attrs.queue_age_ms == 2500
        assert attrs.cost_usd == 0.08
        
        # Check that metadata objects are stored
        assert attrs.generation_metadata == gen_meta
        assert attrs.context_metrics == context_meta
        assert attrs.queue_metrics == queue_meta
        assert attrs.cost_metrics == cost_meta