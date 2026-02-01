"""
Demonstration of the Self-Healing Support Supervisor system.

This script simulates a migration scenario with various issues
and shows how the agent detects patterns and recommends actions.
"""

import json
from datetime import datetime, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from supervisor.core.agent import SupervisorAgent
from supervisor.models import (
    Signal, SignalType, MigrationStage
)

console = Console()


def generate_simulated_signals() -> list[Signal]:
    """Generate simulated signals representing a migration crisis."""
    
    base_time = datetime.utcnow()
    signals = []
    
    # Scenario: Checkout auth token issue affecting multiple merchants
    
    # First wave - 3 merchants report checkout issues
    for i in range(3):
        signals.append(Signal(
            id=f"sig_checkout_{i+1}",
            timestamp=base_time - timedelta(hours=2, minutes=i*10),
            signal_type=SignalType.SUPPORT_TICKET,
            merchant_id=f"merchant_{i+1}",
            migration_stage=MigrationStage.MID_MIGRATION,
            title="Checkout page showing blank screen",
            description="Customers report checkout page is blank after migration",
            severity="high",
            category="checkout"
        ))
    
    # Second wave - Error logs appear
    for i in range(4):
        signals.append(Signal(
            id=f"sig_error_{i+1}",
            timestamp=base_time - timedelta(hours=1, minutes=i*15),
            signal_type=SignalType.ERROR_LOG,
            merchant_id=f"merchant_{i+1}",
            migration_stage=MigrationStage.MID_MIGRATION,
            description="Auth token invalid - checkout authentication failed",
            severity="high",
            category="checkout",
            metadata={"error_code": "AUTH_401", "component": "checkout"}
        ))
    
    # Third wave - API errors
    for i in range(2):
        signals.append(Signal(
            id=f"sig_api_{i+1}",
            timestamp=base_time - timedelta(minutes=30 + i*10),
            signal_type=SignalType.API_ERROR,
            merchant_id=f"merchant_{i+5}",
            migration_stage=MigrationStage.MID_MIGRATION,
            description="API error: invalid authentication token",
            severity="medium",
            category="checkout"
        ))
    
    # Some unrelated signals (noise)
    signals.append(Signal(
        id="sig_unrelated_1",
        timestamp=base_time - timedelta(hours=3),
        signal_type=SignalType.SUPPORT_TICKET,
        merchant_id="merchant_99",
        migration_stage=MigrationStage.PRE_MIGRATION,
        title="Question about migration timeline",
        description="When will my migration be scheduled?",
        severity="low",
        category="general"
    ))
    
    return signals


def print_signals(signals: list[Signal]) -> None:
    """Pretty print signals."""
    table = Table(title="📊 Ingested Signals", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Merchant", style="yellow")
    table.add_column("Category", style="green")
    table.add_column("Description", style="white", max_width=40)
    
    for signal in signals[:10]:  # Show first 10
        table.add_row(
            signal.id,
            signal.signal_type if isinstance(signal.signal_type, str) else signal.signal_type.value,
            signal.merchant_id or "N/A",
            signal.category or "N/A",
            signal.description[:40] + "..." if len(signal.description) > 40 else signal.description
        )
    
    console.print(table)
    console.print(f"\n[dim]Total signals: {len(signals)}[/dim]\n")


def print_decision(decision) -> None:
    """Pretty print agent decision."""
    
    # Observations
    console.print(Panel(
        "\n".join(f"• {obs}" for obs in decision.observations),
        title="🔍 OBSERVATIONS",
        border_style="blue"
    ))
    
    # Hypothesis
    console.print(Panel(
        f"[bold]{decision.hypothesis.description}[/bold]\n\n"
        f"[green]Confidence: {decision.hypothesis.confidence:.0%}[/green]\n\n"
        f"[yellow]Evidence:[/yellow]\n" +
        "\n".join(f"  • {ev}" for ev in decision.hypothesis.evidence) +
        f"\n\n[yellow]Potential Causes:[/yellow]\n" +
        "\n".join(f"  • {cause}" for cause in decision.hypothesis.potential_causes),
        title="💡 HYPOTHESIS",
        border_style="yellow"
    ))
    
    # Reasoning
    console.print(Panel(
        decision.reasoning,
        title="🧠 REASONING",
        border_style="cyan"
    ))
    
    # Proposed Actions
    actions_text = ""
    for i, action in enumerate(decision.proposed_actions):
        action_type = action.action_type if isinstance(action.action_type, str) else action.action_type.value
        actions_text += f"\n[bold]{i+1}. {action_type}[/bold]\n"
        actions_text += f"   {action.description}\n"
        actions_text += f"   [dim]Impact: {action.expected_impact}[/dim]\n"
    
    console.print(Panel(
        actions_text,
        title=f"⚡ PROPOSED ACTIONS ({len(decision.proposed_actions)})",
        border_style="green"
    ))
    
    # Risk & Approval
    risk_level = decision.risk_level if isinstance(decision.risk_level, str) else decision.risk_level.value
    risk_color = {
        "low": "green",
        "medium": "yellow",
        "high": "red"
    }.get(risk_level, "white")
    
    console.print(Panel(
        f"[{risk_color}]Risk Level: {risk_level.upper()}[/{risk_color}]\n"
        f"Requires Human Approval: {'✓ YES' if decision.requires_human_approval else '✗ NO'}",
        title="⚠️  RISK ASSESSMENT",
        border_style=risk_color
    ))
    
    # Explainability
    console.print(Panel(
        decision.explainability_notes,
        title="📖 EXPLAINABILITY NOTES",
        border_style="magenta"
    ))


def main():
    """Run the demonstration."""
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold cyan]Self-Healing Support Supervisor[/bold cyan]\n"
        "[dim]Agentic AI Demo - Migration Crisis Scenario[/dim]",
        border_style="cyan"
    ))
    console.print("\n")
    
    # Step 1: Generate signals
    console.print("[bold]Step 1:[/bold] Generating simulated migration signals...\n")
    signals = generate_simulated_signals()
    print_signals(signals)
    
    input("Press Enter to continue...\n")
    
    # Step 2: Initialize agent
    console.print("[bold]Step 2:[/bold] Initializing supervisor agent...\n")
    agent = SupervisorAgent(confidence_threshold=0.75)
    console.print("[green]✓[/green] Agent initialized\n")
    
    input("Press Enter to continue...\n")
    
    # Step 3: Ingest signals
    console.print("[bold]Step 3:[/bold] Ingesting signals...\n")
    agent.ingest_signals(signals)
    console.print(f"[green]✓[/green] Ingested {len(signals)} signals\n")
    
    input("Press Enter to continue...\n")
    
    # Step 4: Run agent cycle
    console.print("[bold]Step 4:[/bold] Running agent analysis cycle...\n")
    console.print("[dim]OBSERVE → REASON → DECIDE → (ACT) → EXPLAIN[/dim]\n")
    
    decision = agent.run_cycle(time_window_hours=24, auto_approve=False)
    
    console.print("\n[green]✓[/green] Analysis complete!\n")
    
    input("Press Enter to see results...\n")
    
    # Step 5: Display decision
    console.print(Panel.fit(
        "[bold]AGENT DECISION REPORT[/bold]",
        border_style="green"
    ))
    console.print("\n")
    
    print_decision(decision)
    
    # Step 6: Export results
    console.print("\n[bold]Step 5:[/bold] Exporting decision to JSON...\n")
    
    output = decision.model_dump(mode='json')
    
    with open("decision_output.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    
    console.print("[green]✓[/green] Decision exported to decision_output.json\n")
    
    # Display JSON snippet
    with open("decision_output.json", "r") as f:
        content = f.read()
    
    syntax = Syntax(content[:800] + "\n  ...", "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="📄 Output Preview", border_style="blue"))
    
    console.print("\n")
    console.print(Panel.fit(
        "[bold green]Demo Complete![/bold green]\n\n"
        "The agent successfully:\n"
        "• Detected patterns across multiple merchants\n"
        "• Formulated a hypothesis about the root cause\n"
        "• Assessed risk and confidence levels\n"
        "• Proposed appropriate actions\n"
        "• Explained its reasoning process\n\n"
        "[dim]Check decision_output.json for full results[/dim]",
        border_style="green"
    ))
    console.print("\n")


if __name__ == "__main__":
    main()
