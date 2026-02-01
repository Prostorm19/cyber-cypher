"""
LLM-powered reasoning for hypothesis generation and pattern analysis.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from supervisor.models import Signal, Pattern, Hypothesis
from supervisor.reasoning.llm_client import LLMClient


class LLMReasoner:
    """
    Uses LLM to generate hypotheses and analyze patterns.
    Provides chain-of-thought reasoning and better explanations.
    """
    
    def __init__(self):
        self.llm = LLMClient()
    
    def is_enabled(self) -> bool:
        """Check if LLM reasoning is available."""
        return self.llm.is_enabled()
    
    def generate_hypothesis(
        self,
        signals: List[Signal],
        detected_patterns: List[Pattern]
    ) -> Optional[Hypothesis]:
        """
        Use LLM to generate hypothesis from signals and patterns.
        
        Returns:
            Hypothesis with LLM-generated description and reasoning
        """
        if not self.is_enabled():
            return None
        
        # Build context for LLM
        signal_summary = self._summarize_signals(signals)
        pattern_summary = self._summarize_patterns(detected_patterns)
        
        prompt = self._build_hypothesis_prompt(signal_summary, pattern_summary)
        
        # Get LLM response
        response = self.llm.generate(prompt, temperature=0.7, max_tokens=800)
        
        if not response:
            return None
        
        # Parse response into hypothesis
        return self._parse_hypothesis_response(response, signals, detected_patterns)
    
    def assess_confidence(
        self,
        hypothesis: str,
        evidence: List[str],
        signals: List[Signal]
    ) -> float:
        """
        Use LLM to assess confidence in hypothesis.
        
        Returns:
            Confidence score 0-1
        """
        if not self.is_enabled():
            return 0.5  # Default fallback
        
        prompt = f"""You are analyzing a support incident hypothesis.

**Hypothesis:** {hypothesis}

**Evidence:**
{chr(10).join(f"- {e}" for e in evidence)}

**Signal Count:** {len(signals)}

Based on the evidence, rate your confidence in this hypothesis on a scale of 0-100.

Consider:
- Strength and consistency of evidence
- Number of affected instances
- Clarity of the pattern
- Likelihood of the root cause

Respond with ONLY a number between 0 and 100, nothing else."""

        response = self.llm.generate(prompt, temperature=0.3, max_tokens=10)
        
        if response:
            try:
                confidence = float(response.strip()) / 100.0
                return max(0.0, min(1.0, confidence))  # Clamp to 0-1
            except ValueError:
                pass
        
        return 0.5
    
    def identify_root_causes(
        self,
        signals: List[Signal],
        hypothesis: str
    ) -> List[str]:
        """
        Use LLM to identify potential root causes.
        
        Returns:
            List of potential root causes
        """
        if not self.is_enabled():
            return []
        
        signal_details = self._get_signal_details(signals[:10])  # Limit to 10 for context
        
        prompt = f"""You are a technical support analyst investigating an incident.

**Hypothesis:** {hypothesis}

**Recent Signals:**
{signal_details}

List 3-5 most likely root causes for this issue. Be specific and technical.

Format your response as a numbered list:
1. [First root cause]
2. [Second root cause]
..."""

        response = self.llm.generate(prompt, temperature=0.7, max_tokens=400)
        
        if response:
            return self._parse_list_response(response)
        
        return []
    
    def analyze_pattern_significance(
        self,
        pattern: Pattern,
        all_signals: List[Signal]
    ) -> Dict[str, Any]:
        """
        Use LLM to analyze whether a pattern is significant.
        
        Returns:
            Analysis with significance score and reasoning
        """
        if not self.is_enabled():
            return {"significant": True, "reasoning": "LLM disabled"}
        
        pattern_desc = f"{pattern.category} pattern: {len(pattern.signal_ids)} signals"
        total_signals = len(all_signals)
        
        prompt = f"""Analyze this support signal pattern:

**Pattern:** {pattern_desc}
**Total Signals (24h):** {total_signals}
**Occurrence Rate:** {len(pattern.signal_ids)/total_signals*100:.1f}%

Is this pattern significant enough to investigate? Consider:
- How common is this issue type normally?
- Is the occurrence rate unusual?
- Does it warrant proactive action?

Respond in this format:
SIGNIFICANT: [Yes/No]
REASONING: [1-2 sentence explanation]"""

        response = self.llm.generate(prompt, temperature=0.5, max_tokens=200)
        
        if response:
            lines = response.strip().split('\n')
            significant = 'yes' in lines[0].lower() if lines else True
            reasoning = lines[1].replace('REASONING:', '').strip() if len(lines) > 1 else ""
            
            return {
                "significant": significant,
                "reasoning": reasoning,
                "llm_powered": True
            }
        
        return {"significant": True, "reasoning": "LLM analysis failed"}
    
    # Helper methods
    
    def _summarize_signals(self, signals: List[Signal]) -> str:
        """Create concise signal summary for LLM."""
        by_type = {}
        by_stage = {}
        
        for signal in signals:
            by_type[signal.signal_type] = by_type.get(signal.signal_type, 0) + 1
            by_stage[signal.migration_stage] = by_stage.get(signal.migration_stage, 0) + 1
        
        summary = f"**Total Signals:** {len(signals)}\n\n"
        summary += f"**By Type:**\n"
        for sig_type, count in sorted(by_type.items(), key=lambda x: -x[1])[:5]:
            summary += f"- {sig_type}: {count}\n"
        
        summary += f"\n**By Migration Stage:**\n"
        for stage, count in by_stage.items():
            summary += f"- {stage}: {count}\n"
        
        summary += f"\n**Sample Descriptions:**\n"
        for signal in signals[:5]:
            summary += f"- {signal.description[:100]}\n"
        
        return summary
    
    def _summarize_patterns(self, patterns: List[Pattern]) -> str:
        """Summarize detected patterns."""
        if not patterns:
            return "No specific patterns detected yet."
        
        summary = f"**Patterns Detected:** {len(patterns)}\n\n"
        for i, pattern in enumerate(patterns[:3], 1):
            summary += f"{i}. {pattern.category}: {len(pattern.signal_ids)} signals\n"
        
        return summary
    
    def _build_hypothesis_prompt(self, signal_summary: str, pattern_summary: str) -> str:
        """Build prompt for hypothesis generation."""
        return f"""You are a technical support supervisor analyzing a potential incident during an e-commerce platform migration.

{signal_summary}

{pattern_summary}

Based on these signals, formulate a clear hypothesis about what is happening.

Your hypothesis should:
1. Identify the core issue
2. Explain the likely cause
3. Connect it to the migration context
4. Be specific and actionable

Format your response as:
HYPOTHESIS: [Your hypothesis in 1-2 sentences]
EVIDENCE: [3-5 key pieces of evidence]
AFFECTED_AREA: [Which part of the system]"""
    
    def _parse_hypothesis_response(
        self,
        response: str,
        signals: List[Signal],
        patterns: List[Pattern]
    ) -> Hypothesis:
        """Parse LLM response into Hypothesis object."""
        lines = response.strip().split('\n')
        
        hypothesis_text = ""
        evidence = []
        
        for line in lines:
            if line.startswith('HYPOTHESIS:'):
                hypothesis_text = line.replace('HYPOTHESIS:', '').strip()
            elif line.startswith('EVIDENCE:'):
                evidence.append(line.replace('EVIDENCE:', '').strip())
            elif line.startswith('-') or line.startswith('•'):
                evidence.append(line.lstrip('-•').strip())
        
        if not hypothesis_text:
            hypothesis_text = lines[0] if lines else "Platform instability detected"
        
        if not evidence:
            evidence = [f"{len(signals)} signals detected", f"{len(patterns)} patterns found"]
        
        # Use LLM to assess confidence
        confidence = self.assess_confidence(hypothesis_text, evidence, signals)
        
        # Get root causes from LLM
        potential_causes = self.identify_root_causes(signals, hypothesis_text)
        
        # Get affected merchants
        affected_merchants = list(set(s.merchant_id for s in signals if s.merchant_id))[:20]
        
        return Hypothesis(
            description=hypothesis_text,
            confidence=confidence,
            evidence=evidence[:5],  # Limit to top 5
            potential_root_causes=potential_causes[:5],
            affected_merchants=affected_merchants,
            timestamp=datetime.utcnow(),
            pattern_ids=[p.id for p in patterns],
            llm_generated=True  # Mark as LLM-powered
        )
    
    def _get_signal_details(self, signals: List[Signal]) -> str:
        """Get detailed signal info for prompts."""
        details = ""
        for i, signal in enumerate(signals, 1):
            details += f"{i}. [{signal.signal_type}] {signal.description[:80]}...\n"
        return details
    
    def _parse_list_response(self, response: str) -> List[str]:
        """Parse numbered list from LLM response."""
        items = []
        for line in response.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering
                clean_line = line.lstrip('0123456789.-•) ').strip()
                if clean_line:
                    items.append(clean_line)
        return items
