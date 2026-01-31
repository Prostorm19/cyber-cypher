# Complete Setup and Demo Guide

## System Overview

The Self-Healing Support Supervisor consists of two components:
1. **Backend**: Python FastAPI server with the AI agent
2. **Frontend**: Next.js web dashboard for visualization and control

## Complete Setup

### Backend Setup

```bash
# Navigate to project root
cd d:\cyber-cypher

# Install Python dependencies
pip install -r requirements.txt

# Configure environment (optional)
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY if using LLM features

# Start the backend server
python -m supervisor.api.server
```

Backend will be available at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### Frontend Setup

```bash
# Navigate to UI directory
cd ui

# Install Node dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Demo Scenario: Checkout Migration Crisis

### Step 1: Start Both Servers

**Terminal 1 - Backend:**
```bash
cd d:\cyber-cypher
python -m supervisor.api.server
```

**Terminal 2 - Frontend:**
```bash
cd d:\cyber-cypher\ui
npm run dev
```

### Step 2: Ingest Signals

Navigate to `http://localhost:3000/signals`

Submit 3-5 signals with these patterns:

**Signal 1:**
- Type: `checkout_issue`
- Merchant ID: `merchant_001`
- Migration Stage: `mid_migration`
- Category: `checkout`
- Severity: `high`
- Title: `Checkout page blank`
- Description: `Customers report checkout page shows blank screen after migration`

**Signal 2:**
- Type: `error_log`
- Merchant ID: `merchant_002`
- Migration Stage: `mid_migration`
- Category: `checkout`
- Severity: `high`
- Description: `Auth token invalid - checkout authentication failed`

**Signal 3:**
- Type: `checkout_issue`
- Merchant ID: `merchant_003`
- Migration Stage: `mid_migration`
- Category: `checkout`
- Severity: `high`
- Title: `Payment not processing`
- Description: `Auth error preventing checkout completion`

### Step 3: Run Agent Analysis

Navigate to `http://localhost:3000/agent`

1. Set time window to `24` hours
2. Click **"Run Agent Analysis"**
3. Observe the agent's REASON and DECIDE phases:
   - **Observations**: Signal count, affected merchants
   - **Hypothesis**: Pattern detected with confidence score
   - **Evidence**: Multiple data points supporting the conclusion
   - **Risk Assessment**: Should show HIGH risk due to checkout involvement

### Step 4: Review Explainability

Navigate to `http://localhost:3000/explain`

Explore the collapsible sections to understand:
- What the agent observed
- How it reasoned about the problem
- Why it reached its conclusions
- Why human approval is required

### Step 5: Approve Actions

Navigate to `http://localhost:3000/actions`

1. Review the **Safety Banner** (should show "Human Approval Required")
2. See the **Risk Summary** (should be HIGH)
3. Review each proposed action:
   - Incident summary creation
   - Support team alert
   - Engineering escalation
   - Documentation suggestion
4. Select actions to approve
5. Click **"Approve Selected Actions"**
6. See execution results

### Step 6: Check Dashboard

Navigate to `http://localhost:3000`

Verify:
- Signal count increased
- Merchant count shows 3+
- System status shows appropriate state
- Agent loop visualization shows all phases

### Step 7: View Incidents

Navigate to `http://localhost:3000/incidents`

See if any incidents were created based on the patterns

## Key Demonstration Points

### For Judges/Engineers

**1. Agent Autonomy**
- System automatically detects patterns across multiple signals
- No human intervention needed for observation and reasoning
- Confidence scores show decision certainty

**2. Safety Constraints**
- HIGH risk situations require human approval
- Checkout-related issues trigger safety gates
- No auto-execution of critical actions

**3. Explainability**
- Every decision shows complete reasoning chain
- Evidence listed for transparency
- Uncertainty explicitly acknowledged

**4. Human-in-the-Loop**
- Clear approval workflow
- Action-by-action review
- Safety warnings prominently displayed

**5. Risk Awareness**
- Multi-factor risk assessment
- Color-coded indicators
- Detailed risk justification

## Testing Different Scenarios

### Low-Risk Scenario

Submit signals with:
- Type: `migration_event` or `support_ticket`
- Category: `general`
- Severity: `low`
- Non-checkout related

Result: Lower risk level, may not require approval

### High-Confidence Pattern

Submit 5+ similar signals:
- Same category
- Same migration stage
- Similar descriptions

Result: Higher confidence score (75%+)

### Uncertain Scenario

Submit mixed signals:
- Different categories
- Different stages
- Different merchants

Result: Lower confidence, recommendation to monitor

## Production Deployment

### Backend

```bash
# Production mode
uvicorn supervisor.api.server:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Build for production
npm run build

# Start production server
npm start
```

Or deploy to Vercel:
```bash
vercel deploy
```

## Architecture Highlights

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  Next.js UI     │────────▶│  FastAPI Backend │
│  (Port 3000)    │         │  (Port 8000)     │
│                 │◀────────│                  │
└─────────────────┘         └──────────────────┘
        │                            │
        │                            │
        ▼                            ▼
  Human Supervisor              AI Agent Loop
  - Reviews decisions          - Observes signals
  - Approves actions           - Detects patterns
  - Provides oversight         - Forms hypotheses
                               - Proposes actions
                               - Explains reasoning
```

## Troubleshooting

### Port Conflicts

If ports 3000 or 8000 are in use:

**Backend:**
```bash
# Edit supervisor/config.py
API_PORT=8001
```

**Frontend:**
```bash
# Run on different port
npm run dev -- -p 3001
```

### API Connection Issues

Check:
1. Backend is running: visit `http://localhost:8000/health`
2. Frontend environment: verify `.env.local` has correct `NEXT_PUBLIC_API_URL`
3. Browser console for CORS errors

### No Data Showing

1. Ingest signals first via `/signals` page
2. Run analysis via `/agent` page
3. Check backend logs for errors

## Next Steps

- Integrate with real ticketing system (Zendesk, Intercom)
- Connect to log aggregation (Datadog, Splunk)
- Add LLM integration for enhanced reasoning
- Deploy to production environment
- Set up monitoring and alerting

## Support

For issues:
1. Check README files in `supervisor/` and `ui/` directories
2. Review API documentation at `/docs` endpoint
3. Examine browser console and backend logs
