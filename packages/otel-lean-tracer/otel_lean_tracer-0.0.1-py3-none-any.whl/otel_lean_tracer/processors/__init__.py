# Processors module for OTEL-Lean-Tracer
# OTEL-Lean-Tracer用プロセッサーモジュール

from .lean_processor import LeanTraceProcessor, instrument_lean

__all__ = ['LeanTraceProcessor', 'instrument_lean']