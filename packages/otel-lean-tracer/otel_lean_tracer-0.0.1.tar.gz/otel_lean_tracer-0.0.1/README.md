# 🚀 OTEL-Lean-Tracer

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![OpenTelemetry](https://img.shields.io/badge/OpenTelemetry-1.25+-green.svg)](https://opentelemetry.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**🎯 Zero-config OpenTelemetry tracing with Lean Production KPIs for LLM/Agent applications**

OTEL-Lean-Tracer seamlessly adds "Lean Production 7 Wastes" metrics to your LLM and Agent execution traces, giving you real-time visibility into bottlenecks and waste in your AI applications through beautiful Grafana dashboards.

## ✨ Why OTEL-Lean-Tracer?

### 🔍 **Instant Visibility**
- **Zero configuration** - Just add one line and start seeing your AI application's performance
- **Real-time bottleneck detection** - Spot queue delays, context waste, and retry loops instantly
- **Beautiful Grafana dashboards** - Pre-built visualizations for immediate insights

### 📊 **Lean Production Metrics**
Track the 7 wastes of Lean Production applied to LLM applications:
- 🕒 **Queue Time** - Time spent waiting for API responses
- 🔄 **Retry Waste** - Failed generation attempts and retries
- 📈 **Context Waste** - Unused tokens in prompts
- 💰 **Cost Tracking** - Real-time API cost monitoring (generation + evaluation)
- ⚡ **Processing Delays** - Identify slow components
- 🎯 **Quality Issues** - Track acceptance rates and evaluation scores
- 🚚 **Transport Overhead** - Network and serialization costs

### 🎯 **GenAgent Evaluation Tracking**
Advanced quality monitoring for agents-sdk-models:
- 📊 **Evaluation Scores** - Track quality scores (0-100) vs thresholds
- 🔄 **Retry Analysis** - Monitor threshold-based retry patterns
- 💡 **Improvement Insights** - Capture AI-generated improvement suggestions
- 💰 **Separate Cost Tracking** - Split generation and evaluation costs
- 📈 **Quality Trends** - Visualize quality progression over time
- 🎛 **Multi-Step Monitoring** - Track quality across Flow pipelines

### 🛠 **Developer Friendly**
- **OpenTelemetry compatible** - Works with your existing observability stack
- **Agent SDK integration** - Built for modern LLM frameworks
- **Grafana + Tempo ready** - Enterprise-grade trace storage and visualization

## 🚀 Quick Start

### Installation

```bash
# Install via uv (recommended)
uv add otel-lean-tracer

# Or via pip
pip install otel-lean-tracer
```

### ⚡ Super Simple Setup

Add just **one line** to your LLM application:

```python
from otel_lean_tracer import instrument_lean

# Enable lean tracing (that's it!)
instrument_lean()

# Your existing code works unchanged
from agents_sdk_models import create_simple_gen_agent

agent = create_simple_gen_agent(
    name="story_generator",
    instructions="Generate creative stories",
    model="gpt-4o-mini",
    threshold=75  # Quality threshold for evaluation
)

result = await agent.run("Tell me a story about a robot")
```

### 📊 Instant Dashboard

Your traces automatically include:

**Core Attributes (OTEL Semantic Conventions):**
- `otel.lean.gen.attempt` - Generation attempt number (1, 2, 3...)
- `otel.lean.gen.accepted` - Whether output was accepted
- `llm.evaluation.score` - Quality evaluation score (0-100)
- `llm.evaluation.threshold` - Quality threshold setting
- `llm.evaluation.passed` - Whether evaluation passed
- `otel.lean.retry.reason` - Why retry was needed
- `llm.context.bytes_total` - Total prompt size
- `llm.context.bytes_useful` - Actually referenced content  
- `otel.lean.queue_age_ms` - Time waiting in queues
- `llm.usage.cost_usd` - Generation API costs
- `llm.evaluation.cost_usd` - Evaluation API costs

**Optional Attributes (when available):**
- `model_scale_b` - Model scale in billions of parameters
- `retry_energy_kwh` - Estimated energy consumption for retries

## 🎛 Supported Environments

| Environment | Status | Version |
|-------------|--------|---------|
| **Python** | ✅ | 3.11+ |
| **OpenTelemetry** | ✅ | 1.25+ |
| **Agents SDK** | ✅ | 0.22+ |
| **Grafana Tempo** | ✅ | Latest |
| **OpenAI** | ✅ | All models |
| **Anthropic** | ✅ | Claude series |
| **Ollama** | ✅ | Local models |

## 📈 Advanced Configuration

### Custom Exporters

```python
from otel_lean_tracer import instrument_lean
from otel_lean_tracer.exporters import create_tempo_exporter

# Configure Tempo backend
exporter = create_tempo_exporter(
    endpoint="http://tempo:3200",
    headers={"Authorization": "Bearer your-token"}
)

instrument_lean(exporter=exporter)
```

### Evaluation Data Tracking

```python
from otel_lean_tracer.attributes import LeanAttributes

# Evaluation data is automatically captured from GenAgent:
# - Quality scores and thresholds
# - Improvement suggestions
# - Retry reasons and patterns
# - Separate cost tracking for generation vs evaluation
```

### Flow Metrics

```python
from otel_lean_tracer.mixins import FlowInstrumentationMixin

class MyAgent(FlowInstrumentationMixin):
    async def process(self, input_data):
        # Automatically measures queue_age_ms and evaluation metrics
        return await self.instrumented_call(input_data)
```

## 🎯 Real-World Benefits

### 💡 **Before OTEL-Lean-Tracer**
- ❌ No visibility into LLM application performance
- ❌ Manual cost tracking and estimation
- ❌ Difficult to spot bottlenecks and waste
- ❌ No quality monitoring or evaluation insights
- ❌ Complex observability setup required

### ✨ **After OTEL-Lean-Tracer**
- ✅ **Zero-config** observability for LLM apps
- ✅ **Automatic cost tracking** with real-time dashboards
- ✅ **Instant bottleneck detection** using Lean metrics
- ✅ **Quality evaluation monitoring** with improvement insights
- ✅ **Beautiful Grafana dashboards** out of the box

## 🔧 Integration Examples

### With OpenAI Agents SDK + Evaluation

```python
from agents_sdk_models import create_simple_gen_agent, Flow
from otel_lean_tracer import instrument_lean

instrument_lean()

# Create agents with quality thresholds
classifier = create_simple_gen_agent(
    name="intent_classifier",
    instructions="Classify user intent accurately",
    model="gpt-4o-mini",
    threshold=80  # Higher threshold for classification
)

responder = create_simple_gen_agent(
    name="response_generator", 
    instructions="Generate helpful responses",
    model="gpt-4o",
    threshold=75  # Quality threshold for responses
)

# Create flow - evaluation data automatically traced!
flow = Flow(steps=[classifier, responder])
result = await flow.run("Help me plan a vacation")

# Dashboard shows:
# - Quality scores for each step
# - Cost breakdown (generation vs evaluation)
# - Retry patterns and improvement suggestions
# - Multi-step quality progression
```

### With Custom Evaluation Systems

```python
from otel_lean_tracer.processors import LeanTraceProcessor
from opentelemetry import trace

# Custom evaluation data is automatically detected
custom_result = {
    "content": "Generated response",
    "evaluation": {
        "score": 85.5,
        "threshold": 75.0,
        "passed": True,
        "improvements": ["Add more examples", "Improve clarity"]
    }
}

# Lean processor extracts evaluation data automatically
processor = LeanTraceProcessor()
trace.get_tracer_provider().add_span_processor(processor)
```

## 📊 Grafana Dashboard Setup

Pre-built dashboards included in `/examples/grafana/`:

1. **Lean Production Metrics** - Overview of waste and efficiency
2. **Quality Analysis** - Evaluation scores, trends, and improvement tracking
3. **Cost Analysis** - Real-time API cost breakdown (generation + evaluation)
4. **Performance Monitoring** - Latency and throughput metrics
5. **Error Analysis** - Retry patterns and failure modes

Import `lean-tracer-dashboard.json` into your Grafana instance for instant visualizations!

## 🏗 Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Your LLM App  │───▶│ OTEL-Lean-Tracer │───▶│ Grafana + Tempo │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │ Lean Metrics │
                       │ • Queue Time │
                       │ • Retry Waste│
                       │ • Context    │
                       │ • Quality    │
                       │ • Cost       │
                       └──────────────┘
```

## 🤝 Contributing

We love contributions! Check out our [Contributing Guide](CONTRIBUTING.md) to get started.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/otel-lean-tracer.git
cd otel-lean-tracer

# Install in development mode
uv pip install -e .

# Install dev dependencies
uv add --group dev pytest pytest-cov pytest-asyncio

# Run tests
pytest
```

## 📚 Documentation

- 📖 [Complete Documentation](docs/)
- 🏗 [Architecture Guide](docs/architecture.md)
- 🎯 [Use Cases](docs/usecase_spec.md)
- 🔧 [Function Reference](docs/function_spec.md)
- 📊 [Grafana Setup Guide](examples/grafana/dashboard-setup-guide.md)
- 🎓 [Tutorial with Evaluation Examples](docs/tutorial.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenTelemetry community for the amazing observability framework
- Grafana team for beautiful visualization tools
- Lean Production methodology for waste reduction principles
- agents-sdk-models for advanced LLM agent capabilities

---

**Made with ❤️ for the LLM/Agent developer community**

*Start tracking your AI application's efficiency AND quality in under 60 seconds! 🚀*