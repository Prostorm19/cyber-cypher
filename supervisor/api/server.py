"""
FastAPI server for the supervisor system.
"""

from typing import List, Optional
from fastapi import FastAPI, HTTPException, status, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from supervisor.models import (
    Signal, AgentDecision
)
from supervisor.core.agent import SupervisorAgent
from supervisor.memory.manager import MemoryManager
from supervisor.config import settings
from supervisor.api.ingestion import (
    parse_csv_signals, parse_json_signals,
    github_issue_to_signal, sentry_error_to_signal,
    generic_webhook_to_signal, WebhookPayload
)
from supervisor.api import demo

# Initialize FastAPI app
app = FastAPI(
    title="Self-Healing Support Supervisor",
    description="Agentic AI system for proactive issue detection and resolution",
    version="0.1.0"
)

# Include demo router
app.include_router(demo.router, prefix="/api", tags=["demo"])

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent and memory
agent = SupervisorAgent()
memory = MemoryManager()


# ===== Request/Response Models =====

class SignalInput(BaseModel):
    """Input model for creating signals."""
    signals: List[Signal]


class AnalysisRequest(BaseModel):
    """Request for running analysis."""
    time_window_hours: Optional[int] = 24
    auto_approve: Optional[bool] = False


class ActionApprovalRequest(BaseModel):
    """Request for approving actions."""
    action_indices: List[int]  # Indices of actions to approve


# ===== Health Check =====

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "timestamp": agent.observation.get_signal_statistics()["timestamp"]
    }


# ===== Signal Management =====

@app.post("/signals/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_signals(signal_input: SignalInput):
    """Ingest new signals into the system."""
    try:
        print(f"Received {len(signal_input.signals)} signals for ingestion")
        agent.ingest_signals(signal_input.signals)
        
        return {
            "status": "success",
            "message": f"Ingested {len(signal_input.signals)} signals",
            "signal_ids": [s.id for s in signal_input.signals]
        }
    except Exception as e:
        import traceback
        print(f"ERROR in signal ingestion: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest signals: {str(e)}"
        )


@app.post("/signals/webhook", status_code=status.HTTP_201_CREATED)
async def webhook_ingest(request: Request):
    """
    Webhook endpoint for external signal ingestion.
    Supports GitHub issues, Sentry errors, and generic webhooks.
    """
    try:
        body = await request.json()
        signals = []
        
        # Detect webhook type and convert to signals
        if 'issue' in body and 'repository' in body:
            # GitHub issue webhook
            signal = github_issue_to_signal(body['issue'])
            signals.append(signal)
        elif 'event' in body and 'sentry' in body.get('event', '').lower():
            # Sentry error webhook
            signal = sentry_error_to_signal(body.get('data', {}))
            signals.append(signal)
        elif 'signals' in body:
            # Batch of signals
            for sig_data in body['signals']:
                signal = generic_webhook_to_signal(sig_data)
                signals.append(signal)
        else:
            # Generic single signal
            signal = generic_webhook_to_signal(body)
            signals.append(signal)
        
        # Ingest signals
        agent.ingest_signals(signals)
        
        return {
            "status": "success",
            "message": f"Webhook processed: ingested {len(signals)} signals",
            "signal_ids": [s.id for s in signals],
            "source": signals[0].metadata.get('source', 'unknown') if signals else 'unknown'
        }
    except Exception as e:
        import traceback
        print(f"ERROR in webhook ingestion: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


@app.post("/signals/upload/csv", status_code=status.HTTP_201_CREATED)
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV file containing signals."""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a CSV file"
            )
        
        content = await file.read()
        content_str = content.decode('utf-8')
        
        signals = parse_csv_signals(content_str)
        
        if not signals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid signals found in CSV file"
            )
        
        agent.ingest_signals(signals)
        
        return {
            "status": "success",
            "message": f"CSV uploaded: ingested {len(signals)} signals",
            "filename": file.filename,
            "signal_ids": [s.id for s in signals]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in CSV upload: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV upload failed: {str(e)}"
        )


@app.post("/signals/upload/json", status_code=status.HTTP_201_CREATED)
async def upload_json(file: UploadFile = File(...)):
    """Upload JSON file containing signals."""
    try:
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a JSON file"
            )
        
        content = await file.read()
        content_str = content.decode('utf-8')
        
        signals = parse_json_signals(content_str)
        
        if not signals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid signals found in JSON file"
            )
        
        agent.ingest_signals(signals)
        
        return {
            "status": "success",
            "message": f"JSON uploaded: ingested {len(signals)} signals",
            "filename": file.filename,
            "signal_ids": [s.id for s in signals]
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"ERROR in JSON upload: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"JSON upload failed: {str(e)}"
        )


@app.get("/signals/statistics")
async def get_signal_statistics(hours: int = 24):
    """Get signal statistics."""
    try:
        stats = agent.observation.get_signal_statistics(hours=hours)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


@app.get("/signals/recent")
async def get_recent_signals(
    hours: int = 24,
    signal_type: Optional[str] = None,
    merchant_id: Optional[str] = None
):
    """Get recent signals with optional filtering."""
    try:
        signals = agent.observation.get_recent_signals(
            hours=hours,
            signal_type=signal_type,
            merchant_id=merchant_id
        )
        
        return {
            "count": len(signals),
            "signals": [s.model_dump() for s in signals]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get signals: {str(e)}"
        )


# ===== Agent Operations =====

@app.post("/agent/analyze", response_model=AgentDecision)
async def run_analysis(request: AnalysisRequest):
    """Run a full agent analysis cycle."""
    try:
        decision = agent.run_cycle(
            time_window_hours=request.time_window_hours,
            auto_approve=request.auto_approve
        )
        
        return decision
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@app.post("/agent/approve-actions")
async def approve_actions(request: ActionApprovalRequest):
    """Approve and execute specific actions from the last decision."""
    try:
        if not agent.decision_history:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No decisions available to approve"
            )
        
        last_decision = agent.decision_history[-1]
        
        results = []
        for idx in request.action_indices:
            if idx >= len(last_decision.proposed_actions):
                continue
            
            action = last_decision.proposed_actions[idx]
            result = agent.executor.execute_action(action, approved=True)
            results.append(result)
        
        return {
            "status": "success",
            "approved_count": len(results),
            "results": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Action approval failed: {str(e)}"
        )


@app.get("/agent/decisions")
async def get_decision_history(limit: Optional[int] = None):
    """Get decision history."""
    try:
        decisions = agent.get_decision_history(limit=limit)
        
        return {
            "count": len(decisions),
            "decisions": [d.model_dump() for d in decisions]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get decision history: {str(e)}"
        )


# ===== Memory/Knowledge Base =====

@app.get("/incidents/open")
async def get_open_incidents():
    """Get all open incidents."""
    try:
        incidents = memory.get_open_incidents()
        
        return {
            "count": len(incidents),
            "incidents": [inc.model_dump() for inc in incidents]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get incidents: {str(e)}"
        )


@app.get("/knowledge/search")
async def search_knowledge(query: str, tags: Optional[str] = None):
    """Search knowledge base."""
    try:
        tag_list = tags.split(",") if tags else None
        results = memory.search_knowledge(query, tags=tag_list)
        
        return {
            "count": len(results),
            "results": [entry.model_dump() for entry in results]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Knowledge search failed: {str(e)}"
        )


# ===== Execution Log =====

@app.get("/execution-log")
async def get_execution_log(limit: Optional[int] = None):
    """Get action execution log."""
    try:
        log = agent.executor.get_execution_log(limit=limit)
        
        return {
            "count": len(log),
            "log_entries": log
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution log: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )
