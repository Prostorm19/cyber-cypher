"""
API ingestion endpoints for file uploads and external integrations.
"""

from typing import List, Dict, Any
from datetime import datetime
from fastapi import UploadFile, File, HTTPException, status
from pydantic import BaseModel
import csv
import json
import io

from supervisor.models import Signal, SignalType, MigrationStage


class WebhookPayload(BaseModel):
    """Generic webhook payload."""
    event: str
    data: Dict[str, Any]


def parse_csv_signals(content: str) -> List[Signal]:
    """Parse CSV content into Signal objects."""
    signals = []
    reader = csv.DictReader(io.StringIO(content))
    
    for row in reader:
        try:
            signal = Signal(
                id=row.get('id', f"csv_{datetime.utcnow().timestamp()}_{len(signals)}"),
                timestamp=datetime.fromisoformat(row['timestamp']) if 'timestamp' in row else datetime.utcnow(),
                signal_type=SignalType(row['signal_type']),
                merchant_id=row.get('merchant_id'),
                migration_stage=MigrationStage(row['migration_stage']) if 'migration_stage' in row else None,
                description=row['description'],
                severity=row.get('severity'),
                category=row.get('category'),
                metadata={}
            )
            signals.append(signal)
        except Exception as e:
            print(f"Warning: Failed to parse row: {row}. Error: {e}")
            continue
    
    return signals


def parse_json_signals(content: str) -> List[Signal]:
    """Parse JSON content into Signal objects."""
    try:
        data = json.loads(content)
        
        # Handle both single object and array
        if isinstance(data, dict):
            data = [data]
        
        signals = []
        for item in data:
            signal = Signal(**item)
            signals.append(signal)
        
        return signals
    except Exception as e:
        raise ValueError(f"Invalid JSON format: {e}")


def github_issue_to_signal(issue: Dict[str, Any]) -> Signal:
    """Convert GitHub issue webhook to Signal."""
    labels = [label.get('name', '') for label in issue.get('labels', [])]
    
    # Detect signal type from labels
    signal_type = SignalType.SUPPORT_TICKET
    if 'bug' in labels:
        signal_type = SignalType.ERROR_LOG
    if 'checkout' in labels:
        signal_type = SignalType.CHECKOUT_ISSUE
    
    # Detect migration stage
    migration_stage = None
    if 'pre-migration' in labels:
        migration_stage = MigrationStage.PRE_MIGRATION
    elif 'mid-migration' in labels:
        migration_stage = MigrationStage.MID_MIGRATION
    elif 'post-migration' in labels:
        migration_stage = MigrationStage.POST_MIGRATION
    
    return Signal(
        id=f"github_{issue['number']}",
        timestamp=datetime.fromisoformat(issue['created_at'].replace('Z', '+00:00')),
        signal_type=signal_type,
        merchant_id=issue.get('user', {}).get('login'),
        migration_stage=migration_stage,
        description=f"{issue['title']}: {issue.get('body', '')}",
        severity='high' if 'critical' in labels else 'medium',
        category='checkout' if 'checkout' in labels else 'general',
        metadata={
            'source': 'github',
            'issue_number': issue['number'],
            'url': issue.get('html_url')
        }
    )


def sentry_error_to_signal(error: Dict[str, Any]) -> Signal:
    """Convert Sentry error webhook to Signal."""
    return Signal(
        id=f"sentry_{error.get('id', datetime.utcnow().timestamp())}",
        timestamp=datetime.utcnow(),
        signal_type=SignalType.ERROR_LOG,
        merchant_id=error.get('tags', {}).get('merchant_id'),
        migration_stage=None,
        description=error.get('message', 'Unknown error'),
        severity='high' if error.get('level') in ['error', 'fatal'] else 'medium',
        category=error.get('tags', {}).get('category', 'general'),
        metadata={
            'source': 'sentry',
            'error_id': error.get('id'),
            'stack_trace': error.get('exception', {}).get('values', [{}])[0].get('stacktrace')
        }
    )


def generic_webhook_to_signal(payload: Dict[str, Any]) -> Signal:
    """Convert generic webhook payload to Signal."""
    return Signal(
        id=payload.get('id', f"webhook_{datetime.utcnow().timestamp()}"),
        timestamp=datetime.fromisoformat(payload['timestamp']) if 'timestamp' in payload else datetime.utcnow(),
        signal_type=SignalType(payload.get('signal_type', 'support_ticket')),
        merchant_id=payload.get('merchant_id'),
        migration_stage=MigrationStage(payload['migration_stage']) if 'migration_stage' in payload else None,
        description=payload.get('description', payload.get('message', 'No description')),
        severity=payload.get('severity', 'medium'),
        category=payload.get('category', 'general'),
        metadata=payload.get('metadata', {})
    )
