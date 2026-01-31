"""
Memory management for short-term and long-term state.
"""

import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pathlib import Path

from supervisor.models import (
    Incident, KnowledgeEntry, Pattern, Signal
)


class MemoryManager:
    """
    Manages short-term incident tracking and long-term knowledge base.
    """
    
    def __init__(self, storage_path: str = "./data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.incidents: Dict[str, Incident] = {}
        self.knowledge_base: Dict[str, KnowledgeEntry] = {}
        
        self._load_state()
    
    # ===== Incident Management =====
    
    def create_incident(
        self,
        title: str,
        description: str,
        pattern_ids: List[str],
        signal_ids: List[str]
    ) -> Incident:
        """Create a new incident."""
        incident_id = f"INC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        incident = Incident(
            id=incident_id,
            title=title,
            description=description,
            status="open",
            pattern_ids=pattern_ids,
            signal_ids=signal_ids
        )
        
        self.incidents[incident_id] = incident
        self._save_incidents()
        
        return incident
    
    def update_incident(
        self,
        incident_id: str,
        status: Optional[str] = None,
        resolution: Optional[str] = None
    ) -> Optional[Incident]:
        """Update an existing incident."""
        incident = self.incidents.get(incident_id)
        
        if not incident:
            return None
        
        if status:
            incident.status = status
            
        if resolution:
            incident.resolution = resolution
            if status == "resolved":
                incident.resolved_at = datetime.utcnow()
        
        incident.updated_at = datetime.utcnow()
        self._save_incidents()
        
        return incident
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID."""
        return self.incidents.get(incident_id)
    
    def get_open_incidents(self) -> List[Incident]:
        """Get all open incidents."""
        return [
            inc for inc in self.incidents.values()
            if inc.status in ["open", "investigating"]
        ]
    
    def get_recent_incidents(self, days: int = 7) -> List[Incident]:
        """Get incidents from last N days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        return [
            inc for inc in self.incidents.values()
            if inc.created_at >= cutoff
        ]
    
    # ===== Knowledge Base Management =====
    
    def add_knowledge(
        self,
        title: str,
        issue_pattern: str,
        root_cause: str,
        resolution: str,
        tags: List[str],
        confidence: float = 1.0,
        related_incidents: Optional[List[str]] = None
    ) -> KnowledgeEntry:
        """Add entry to knowledge base."""
        entry_id = f"KB-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        entry = KnowledgeEntry(
            id=entry_id,
            title=title,
            issue_pattern=issue_pattern,
            root_cause=root_cause,
            resolution=resolution,
            tags=tags,
            related_incidents=related_incidents or [],
            confidence=confidence
        )
        
        self.knowledge_base[entry_id] = entry
        self._save_knowledge_base()
        
        return entry
    
    def search_knowledge(
        self,
        query: str,
        tags: Optional[List[str]] = None
    ) -> List[KnowledgeEntry]:
        """Search knowledge base."""
        results = []
        query_lower = query.lower()
        
        for entry in self.knowledge_base.values():
            # Tag filter
            if tags and not any(tag in entry.tags for tag in tags):
                continue
            
            # Text search
            if (query_lower in entry.title.lower() or
                query_lower in entry.issue_pattern.lower() or
                query_lower in entry.root_cause.lower()):
                results.append(entry)
        
        # Sort by confidence and times validated
        return sorted(
            results,
            key=lambda x: (x.confidence, x.times_validated),
            reverse=True
        )
    
    def validate_knowledge(self, entry_id: str) -> bool:
        """Mark knowledge as validated (increases confidence)."""
        entry = self.knowledge_base.get(entry_id)
        
        if not entry:
            return False
        
        entry.times_validated += 1
        entry.confidence = min(1.0, entry.confidence + 0.05)  # Slight confidence boost
        
        self._save_knowledge_base()
        return True
    
    # ===== Persistence =====
    
    def _load_state(self) -> None:
        """Load persisted state from disk."""
        # Load incidents
        incidents_file = self.storage_path / "incidents.json"
        if incidents_file.exists():
            with open(incidents_file, 'r') as f:
                data = json.load(f)
                self.incidents = {
                    k: Incident(**v) for k, v in data.items()
                }
        
        # Load knowledge base
        kb_file = self.storage_path / "knowledge_base.json"
        if kb_file.exists():
            with open(kb_file, 'r') as f:
                data = json.load(f)
                self.knowledge_base = {
                    k: KnowledgeEntry(**v) for k, v in data.items()
                }
    
    def _save_incidents(self) -> None:
        """Save incidents to disk."""
        incidents_file = self.storage_path / "incidents.json"
        
        data = {
            k: v.model_dump(mode='json')
            for k, v in self.incidents.items()
        }
        
        with open(incidents_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _save_knowledge_base(self) -> None:
        """Save knowledge base to disk."""
        kb_file = self.storage_path / "knowledge_base.json"
        
        data = {
            k: v.model_dump(mode='json')
            for k, v in self.knowledge_base.items()
        }
        
        with open(kb_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def export_all(self, output_dir: str) -> None:
        """Export all memory to a directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export incidents
        with open(output_path / "incidents.json", 'w') as f:
            json.dump(
                [inc.model_dump(mode='json') for inc in self.incidents.values()],
                f, indent=2, default=str
            )
        
        # Export knowledge base
        with open(output_path / "knowledge_base.json", 'w') as f:
            json.dump(
                [kb.model_dump(mode='json') for kb in self.knowledge_base.values()],
                f, indent=2, default=str
            )
