# OTEL-Lean-Tracer: OpenTelemetry-compatible tracing library with Lean Production KPIs
# OTEL-Lean-Tracer: リーン生産方式のKPIを持つOpenTelemetry互換トレーシングライブラリ

__version__ = "0.0.1"

# Import instrument_lean when available
# instrument_leanが利用可能な場合にインポート
try:
    from .processors.lean_processor import instrument_lean
    __all__ = ["instrument_lean"]
except ImportError:
    __all__ = []