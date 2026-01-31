# Installation and Usage Guide

## Installation

### 1. Clone or Download the Repository

```bash
cd d:\cyber-cypher
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and configure:

```bash
copy .env.example .env
```

Edit `.env` and add your configuration:
- `OPENAI_API_KEY` - Your OpenAI API key (if using LLM-enhancement)
- Other settings as needed

## Quick Start

### Option 1: Run the Demo (Recommended First Step)

The demo script shows a complete migration crisis scenario:

```bash
python demo.py
```

This will:
- Generate simulated signals representing a checkout auth issue
- Run the full agent cycle (OBSERVE → REASON → DECIDE → ACT → EXPLAIN)
- Display the agent's decision with full explainability
- Export results to `decision_output.json`

### Option 2: Run Simple Example

```bash
python examples\simple_example.py
```

This shows basic programmatic usage of the system.

### Option 3: Start the API Server

```bash
python -m supervisor.api.server
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

## API Usage

### Ingest Signals

```bash
curl -X POST http://localhost:8000/signals/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "signals": [{
      "id": "sig_001",
      "timestamp": "2026-01-31T18:00:00Z",
      "signal_type": "support_ticket",
      "merchant_id": "merchant_123",
      "migration_stage": "mid_migration",
      "title": "Checkout issue",
      "description": "Checkout page blank",
      "severity": "high",
      "category": "checkout"
    }]
  }'
```

### Run Analysis

```bash
curl -X POST http://localhost:8000/agent/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "time_window_hours": 24,
    "auto_approve": false
  }'
```

### Get Decision History

```bash
curl http://localhost:8000/agent/decisions
```

## Programmatic Usage

```python
from supervisor.core.agent import SupervisorAgent
from supervisor.models import Signal, SignalType, MigrationStage
from datetime import datetime

# Initialize agent
agent = SupervisorAgent(confidence_threshold=0.75)

# Create signal
signal = Signal(
    id="sig_001",
    timestamp=datetime.utcnow(),
    signal_type=SignalType.SUPPORT_TICKET,
    merchant_id="merchant_123",
    migration_stage=MigrationStage.MID_MIGRATION,
    title="Checkout not working",
    description="Customers report blank checkout page",
    severity="high",
    category="checkout"
)

# Ingest signal
agent.ingest_signal(signal)

# Run analysis cycle
decision = agent.run_cycle(
    time_window_hours=24,
    auto_approve=False
)

# Access results
print(decision.hypothesis.description)
print(f"Confidence: {decision.hypothesis.confidence:.0%}")
print(f"Risk: {decision.risk_level.value}")

# Approve and execute actions if needed
if decision.requires_human_approval:
    for action in decision.proposed_actions:
        result = agent.executor.execute_action(action, approved=True)
        print(result)
```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_agent.py -v

# Run with coverage
python -m pytest tests/ --cov=supervisor --cov-report=html
```

## System Architecture

```
supervisor/
├── core/           # Core agent loop
│   ├── observation.py  # Signal ingestion
│   ├── decision.py     # Decision making
│   └── agent.py        # Main orchestrator
├── reasoning/      # Pattern detection & hypothesis
│   └── engine.py
├── actions/        # Action execution
│   └── executor.py
├── memory/         # State management
│   └── manager.py
├── api/            # FastAPI endpoints
│   └── server.py
└── models.py       # Data models
```

## Key Concepts

### The Agent Loop

1. **OBSERVE**: Ingest signals from support tickets, logs, errors
2. **REASON**: Detect patterns and formulate hypotheses
3. **DECIDE**: Select appropriate actions with risk assessment
4. **ACT**: Execute approved actions (with safety boundaries)
5. **EXPLAIN**: Provide full transparency into decisions

### Safety Constraints

The system enforces strict safety boundaries:

- **Human-in-the-loop**: High-risk actions require approval
- **Checkout protection**: Any checkout/payment issues require approval
- **Confidence thresholds**: Low confidence triggers monitoring, not action
- **No live modifications**: Cannot modify checkout, deployments, or merchant configs

### Risk Assessment

Risk is assessed based on:
- Number of affected merchants
- Involvement of critical systems (checkout, payments)
- Migration stage (mid-migration is higher risk)
- Error severity

### Explainability

Every decision includes:
- Observations made
- Hypothesis with confidence and evidence
- Reasoning process
- Proposed actions with expected impact
- Risk assessment
- Explainability notes explaining the decision

## Configuration

Edit `.env` or pass parameters:

```python
agent = SupervisorAgent(
    confidence_threshold=0.75,  # 75% confidence required for auto-action
    memory_retention_days=7     # Keep signals for 7 days
)
```

## Extending the System

### Add Custom Action Types

1. Add to `ActionType` enum in `models.py`
2. Implement handler in `actions/executor.py`
3. Update decision logic in `core/decision.py`

### Add Custom Pattern Detection

1. Add detection method to `reasoning/engine.py`
2. Call from `detect_patterns()` method

### Add LLM Integration

The system is designed to integrate with LLMs for:
- More sophisticated hypothesis formulation
- Natural language response generation
- Advanced pattern recognition

See `reasoning/engine.py` for integration points.

## Troubleshooting

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Database Errors

The system uses SQLite by default. Ensure the directory is writable:
```bash
mkdir -p data
```

### API Connection Issues

Check that the API server is running:
```bash
python -m supervisor.api.server
```

## Support

For issues or questions:
1. Check the example scripts in `examples/`
2. Review the test files in `tests/` for usage patterns
3. Read the implementation plan in the brain directory

## License

MIT License - See LICENSE file for details
