"""
Pattern detection and root cause analysis engine.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import hashlib

from supervisor.models import (
    Signal, Pattern, Hypothesis, MigrationStage, SignalType
)
from supervisor.core.observation import ObservationEngine


class ReasoningEngine:
    """
    Analyzes signals to detect patterns and formulate hypotheses
    about root causes.
    """
    
    def __init__(self, observation_engine: ObservationEngine):
        self.observation = observation_engine
        self.detected_patterns: Dict[str, Pattern] = {}
        
    def detect_patterns(
        self,
        time_window_hours: int = 24,
        min_frequency: int = 2
    ) -> List[Pattern]:
        """
        Detect patterns across recent signals.
        
        A pattern is detected when:
        - Multiple merchants experience similar issues
        - Issues cluster in time
        - Common attributes exist across signals
        """
        recent_signals = self.observation.get_recent_signals(hours=time_window_hours)
        
        if len(recent_signals) < min_frequency:
            return []
        
        patterns = []
        
        # Pattern 1: Same category and migration stage
        patterns.extend(
            self._detect_category_migration_patterns(recent_signals, min_frequency)
        )
        
        # Pattern 2: Same error type across merchants
        patterns.extend(
            self._detect_error_patterns(recent_signals, min_frequency)
        )
        
        # Pattern 3: Same signal type clustering
        patterns.extend(
            self._detect_signal_type_patterns(recent_signals, min_frequency)
        )
        
        # Store detected patterns
        for pattern in patterns:
            self.detected_patterns[pattern.id] = pattern
        
        return patterns
    
    def _detect_category_migration_patterns(
        self,
        signals: List[Signal],
        min_frequency: int
    ) -> List[Pattern]:
        """Detect patterns based on category and migration stage."""
        patterns = []
        
        # Group by (category, migration_stage)
        groups: Dict[Tuple[Optional[str], Optional[str]], List[Signal]] = {}
        
        for signal in signals:
            key = (signal.category, signal.migration_stage)
            if key not in groups:
                groups[key] = []
            groups[key].append(signal)
        
        for (category, stage), group_signals in groups.items():
            if len(group_signals) >= min_frequency and category:
                merchant_ids = list(set([s.merchant_id for s in group_signals if s.merchant_id]))
                
                if len(merchant_ids) >= min_frequency:  # Multiple merchants affected
                    pattern_id = self._generate_pattern_id(
                        f"category_{category}_stage_{stage}"
                    )
                    
                    pattern = Pattern(
                        id=pattern_id,
                        pattern_type="category_migration_cluster",
                        affected_merchants=merchant_ids,
                        signal_ids=[s.id for s in group_signals],
                        first_seen=min(s.timestamp for s in group_signals),
                        last_seen=max(s.timestamp for s in group_signals),
                        frequency=len(group_signals),
                        description=f"{len(merchant_ids)} merchants experiencing {category} issues in {stage} stage",
                        common_attributes={
                            "category": category,
                            "migration_stage": stage
                        }
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_error_patterns(
        self,
        signals: List[Signal],
        min_frequency: int
    ) -> List[Pattern]:
        """Detect patterns based on error messages."""
        patterns = []
        error_signals = [s for s in signals if s.signal_type in [
            SignalType.ERROR_LOG, SignalType.API_ERROR, SignalType.WEBHOOK_FAILURE
        ]]
        
        # Extract error keywords
        error_groups: Dict[str, List[Signal]] = {}
        
        for signal in error_signals:
            keywords = self._extract_error_keywords(signal.description)
            for keyword in keywords:
                if keyword not in error_groups:
                    error_groups[keyword] = []
                error_groups[keyword].append(signal)
        
        for keyword, group_signals in error_groups.items():
            if len(group_signals) >= min_frequency:
                merchant_ids = list(set([s.merchant_id for s in group_signals if s.merchant_id]))
                
                pattern_id = self._generate_pattern_id(f"error_{keyword}")
                
                pattern = Pattern(
                    id=pattern_id,
                    pattern_type="error_cluster",
                    affected_merchants=merchant_ids,
                    signal_ids=[s.id for s in group_signals],
                    first_seen=min(s.timestamp for s in group_signals),
                    last_seen=max(s.timestamp for s in group_signals),
                    frequency=len(group_signals),
                    description=f"Error pattern detected: {keyword} ({len(group_signals)} occurrences)",
                    common_attributes={
                        "error_keyword": keyword,
                        "error_type": "api" if any(s.signal_type == SignalType.API_ERROR for s in group_signals) else "general"
                    }
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_signal_type_patterns(
        self,
        signals: List[Signal],
        min_frequency: int
    ) -> List[Pattern]:
        """Detect temporal clustering of signal types."""
        patterns = []
        
        by_type = self.observation.group_signals_by_attribute(signals, "signal_type")
        
        for signal_type, group_signals in by_type.items():
            if len(group_signals) >= min_frequency:
                # Check if signals are temporally clustered (within 2 hours)
                timestamps = sorted([s.timestamp for s in group_signals])
                if len(timestamps) >= 2:
                    time_span = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
                    
                    if time_span <= 2:  # Clustered within 2 hours
                        merchant_ids = list(set([s.merchant_id for s in group_signals if s.merchant_id]))
                        
                        pattern_id = self._generate_pattern_id(f"type_{signal_type}_cluster")
                        
                        pattern = Pattern(
                            id=pattern_id,
                            pattern_type="temporal_signal_cluster",
                            affected_merchants=merchant_ids,
                            signal_ids=[s.id for s in group_signals],
                            first_seen=timestamps[0],
                            last_seen=timestamps[-1],
                            frequency=len(group_signals),
                            description=f"Spike in {signal_type} signals: {len(group_signals)} occurrences in {time_span:.1f} hours",
                            common_attributes={
                                "signal_type": signal_type,
                                "time_span_hours": time_span
                            }
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def formulate_hypothesis(
        self,
        patterns: List[Pattern],
        signals: List[Signal]
    ) -> Optional[Hypothesis]:
        """
        Formulate a hypothesis about root cause based on patterns.
        
        This is a rule-based implementation. In production, this could
        use LLM-based reasoning for more sophisticated analysis.
        """
        if not patterns:
            return None
        
        # Analyze the most significant pattern
        primary_pattern = max(patterns, key=lambda p: p.frequency)
        
        evidence = []
        potential_causes = []
        confidence = 0.5  # Base confidence
        
        # Evidence 1: Pattern frequency
        evidence.append(
            f"{primary_pattern.frequency} similar signals detected across "
            f"{len(primary_pattern.affected_merchants)} merchants"
        )
        
        # Evidence 2: Migration stage correlation
        migration_stages = [
            s.migration_stage for s in signals
            if s.id in primary_pattern.signal_ids and s.migration_stage
        ]
        if migration_stages:
            stage_counts = Counter(migration_stages)
            most_common_stage, count = stage_counts.most_common(1)[0]
            if count >= len(migration_stages) * 0.7:  # 70% in same stage
                evidence.append(
                    f"{count}/{len(migration_stages)} affected merchants are in {most_common_stage} stage"
                )
                confidence += 0.15
                potential_causes.append("Migration stage-specific issue")
        
        # Evidence 3: Temporal clustering
        time_span = (primary_pattern.last_seen - primary_pattern.first_seen).total_seconds() / 3600
        if time_span <= 2:
            evidence.append(f"All occurrences within {time_span:.1f} hour window")
            confidence += 0.1
            potential_causes.append("Recent platform change or deployment")
        
        # Evidence 4: Category-specific if available
        if "category" in primary_pattern.common_attributes:
            category = primary_pattern.common_attributes["category"]
            evidence.append(f"All issues relate to {category} functionality")
            confidence += 0.1
            potential_causes.append(f"{category.title()} component issue")
        
        # Evidence 5: Error pattern if available
        if "error_keyword" in primary_pattern.common_attributes:
            error = primary_pattern.common_attributes["error_keyword"]
            evidence.append(f"Common error signature: '{error}'")
            confidence += 0.15
            potential_causes.append(f"Technical issue: {error}")
        
        # Cap confidence at 0.95 (never 100% certain without human verification)
        confidence = min(confidence, 0.95)
        
        # Generate hypothesis description
        description = self._generate_hypothesis_description(
            primary_pattern, potential_causes
        )
        
        uncertainty_notes = self._identify_uncertainty(patterns, signals)
        
        return Hypothesis(
            description=description,
            confidence=confidence,
            evidence=evidence,
            affected_patterns=[p.id for p in patterns],
            potential_causes=potential_causes,
            uncertainty_notes=uncertainty_notes
        )
    
    def _generate_pattern_id(self, base: str) -> str:
        """Generate a unique pattern ID."""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{base}_{timestamp}"
        hash_short = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"pattern_{hash_short}"
    
    def _extract_error_keywords(self, description: str) -> List[str]:
        """Extract key error terms from description."""
        keywords = []
        description_lower = description.lower()
        
        # Common error patterns
        error_terms = [
            "auth", "authentication", "token", "invalid", "expired",
            "checkout", "payment", "webhook", "timeout", "connection",
            "404", "500", "403", "401", "blank", "loading", "crash"
        ]
        
        for term in error_terms:
            if term in description_lower:
                keywords.append(term)
        
        return keywords if keywords else ["unknown_error"]
    
    def _generate_hypothesis_description(
        self,
        pattern: Pattern,
        potential_causes: List[str]
    ) -> str:
        """Generate a human-readable hypothesis description."""
        if potential_causes:
            cause_str = " or ".join(potential_causes[:2])  # Top 2 causes
            return f"Likely {cause_str} affecting multiple merchants"
        else:
            return f"Pattern detected: {pattern.description}"
    
    def _identify_uncertainty(
        self,
        patterns: List[Pattern],
        signals: List[Signal]
    ) -> str:
        """Identify areas of uncertainty in the analysis."""
        uncertainties = []
        
        # Check if we have conflicting patterns
        if len(patterns) > 1:
            uncertainties.append(
                f"Multiple patterns detected ({len(patterns)}), relationships unclear"
            )
        
        # Check if we have limited data
        if len(signals) < 5:
            uncertainties.append(
                "Limited signal data - pattern may not be statistically significant"
            )
        
        # Check migration stage diversity
        stages = [s.migration_stage for s in signals if s.migration_stage]
        if len(set(stages)) > 1:
            uncertainties.append(
                "Merchants in different migration stages affected - root cause may vary"
            )
        
        return "; ".join(uncertainties) if uncertainties else "No major uncertainties identified"
