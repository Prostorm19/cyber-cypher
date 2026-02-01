"""
Observation system for ingesting and processing signals.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
from collections import defaultdict
import json

from supervisor.models import (
    Signal, Pattern, SignalType, MigrationStage
)


class ObservationEngine:
    """
    Observes and processes incoming signals from various sources.
    Maintains short-term memory of recent signals.
    """
    
    def __init__(self, memory_retention_days: int = 7):
        self.memory_retention_days = memory_retention_days
        self.signals: Dict[str, Signal] = {}
        self.patterns: Dict[str, Pattern] = {}
        
    def ingest_signal(self, signal: Signal) -> None:
        """Ingest a new signal into the system."""
        # Signal model validator ensures timestamp is timezone-naive
        self.signals[signal.id] = signal
        self._cleanup_old_signals()
        
    def ingest_signals(self, signals: List[Signal]) -> None:
        """Ingest multiple signals."""
        for signal in signals:
            self.ingest_signal(signal)
    
    def get_recent_signals(
        self, 
        hours: int = 24,
        signal_type: Optional[SignalType] = None,
        migration_stage: Optional[MigrationStage] = None,
        merchant_id: Optional[str] = None
    ) -> List[Signal]:
        """Get recent signals with optional filtering."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        print(f"\n[OBSERVATION DEBUG] get_recent_signals called")
        print(f"[OBSERVATION DEBUG] Total signals in memory: {len(self.signals)}")
        print(f"[OBSERVATION DEBUG] Cutoff time: {cutoff}")
        print(f"[OBSERVATION DEBUG] Hours: {hours}")
        
        if len(self.signals) > 0:
            # Show first signal for debugging
            first_signal = list(self.signals.values())[0]
            print(f"[OBSERVATION DEBUG] First signal timestamp: {first_signal.timestamp}")
            print(f"[OBSERVATION DEBUG] First signal timestamp type: {type(first_signal.timestamp)}")
            print(f"[OBSERVATION DEBUG] Comparison: {first_signal.timestamp} >= {cutoff} = {first_signal.timestamp >= cutoff}")
        
        filtered = [
            s for s in self.signals.values()
            if s.timestamp >= cutoff
        ]
        
        print(f"[OBSERVATION DEBUG] Signals after time filter: {len(filtered)}")
        
        if signal_type:
            filtered = [s for s in filtered if s.signal_type == signal_type]
        
        if migration_stage:
            filtered = [s for s in filtered if s.migration_stage == migration_stage]
            
        if merchant_id:
            filtered = [s for s in filtered if s.merchant_id == merchant_id]
        
        print(f"[OBSERVATION DEBUG] Final filtered signals: {len(filtered)}\n")
        
        return sorted(filtered, key=lambda x: x.timestamp, reverse=True)
    
    def get_signal_by_id(self, signal_id: str) -> Optional[Signal]:
        """Retrieve a specific signal by ID."""
        return self.signals.get(signal_id)
    
    def get_signals_by_merchant(self, merchant_id: str, hours: int = 24) -> List[Signal]:
        """Get all signals for a specific merchant."""
        return self.get_recent_signals(hours=hours, merchant_id=merchant_id)
    
    def group_signals_by_attribute(
        self,
        signals: List[Signal],
        attribute: str
    ) -> Dict[Any, List[Signal]]:
        """Group signals by a specific attribute."""
        groups = defaultdict(list)
        for signal in signals:
            if attribute == "merchant_id":
                key = signal.merchant_id
            elif attribute == "signal_type":
                key = signal.signal_type
            elif attribute == "migration_stage":
                key = signal.migration_stage
            elif attribute == "category":
                key = signal.category
            else:
                key = signal.metadata.get(attribute)
            
            if key:
                groups[key].append(signal)
        
        return dict(groups)
    
    def get_signal_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistics about recent signals."""
        recent = self.get_recent_signals(hours=hours)
        
        by_type = self.group_signals_by_attribute(recent, "signal_type")
        by_stage = self.group_signals_by_attribute(recent, "migration_stage")
        by_merchant = self.group_signals_by_attribute(recent, "merchant_id")
        
        return {
            "total_signals": len(recent),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "by_migration_stage": {k: len(v) for k, v in by_stage.items()},
            "unique_merchants": len(by_merchant),
            "time_range_hours": hours,
            "timestamp": datetime.now().isoformat()
        }
    
    def _cleanup_old_signals(self) -> None:
        """Remove signals older than retention period."""
        cutoff = datetime.now() - timedelta(days=self.memory_retention_days)
        
        old_signal_ids = [
            sid for sid, signal in self.signals.items()
            if signal.timestamp < cutoff
        ]
        
        for sid in old_signal_ids:
            del self.signals[sid]
    
    def export_signals(self, filepath: str) -> None:
        """Export signals to a JSON file."""
        data = {
            "signals": [s.model_dump(mode='json') for s in self.signals.values()],
            "exported_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def import_signals(self, filepath: str) -> None:
        """Import signals from a JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for signal_data in data.get("signals", []):
            signal = Signal(**signal_data)
            self.signals[signal.id] = signal
