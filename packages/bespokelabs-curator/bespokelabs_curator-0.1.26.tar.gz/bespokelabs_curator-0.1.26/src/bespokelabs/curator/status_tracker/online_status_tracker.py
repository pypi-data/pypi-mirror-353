import time
import typing as t
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional

import tqdm
from litellm import model_cost
from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table

from bespokelabs.curator import _CONSOLE
from bespokelabs.curator.client import Client
from bespokelabs.curator.constants import PUBLIC_CURATOR_VIEWER_HOME_URL
from bespokelabs.curator.cost import external_model_cost
from bespokelabs.curator.log import USE_RICH_DISPLAY, logger
from bespokelabs.curator.status_tracker.tqdm_constants.colors import COST, DIM, END, ERROR, HEADER, METRIC, MODEL, SUCCESS, WARNING
from bespokelabs.curator.telemetry.client import TelemetryEvent, telemetry_client
from bespokelabs.curator.types.generic_response import _TokenUsage

_TOKEN_LIMIT_STRATEGY_DESCRIPTION = {
    "combined": "combined input/output",
    "seperate": "separate input/output",
}

# Weight factor for successful tasks vs estimates to converge to average actual cost quicker
_SUCCESS_WEIGHT_FACTOR = 5

# Time between status updates in seconds
_STATUS_UPDATE_INTERVAL = 5


class TokenLimitStrategy(str, Enum):
    """Token limit Strategy enum."""

    combined = "combined"
    seperate = "seperate"
    default = "combined"


@dataclass
class OnlineStatusTracker:
    """Tracks the status of all requests."""

    num_tasks_started: int = 0
    num_tasks_in_progress: int = 0
    num_tasks_succeeded: int = 0
    num_tasks_failed: int = 0
    num_tasks_already_completed: int = 0
    num_api_errors: int = 0
    num_other_errors: int = 0
    num_rate_limit_errors: int = 0
    num_parsed_responses: int = 0
    available_request_capacity: float = 1.0
    available_token_capacity: float | _TokenUsage = 0
    last_update_time: float = field(default_factory=time.time)
    max_requests_per_minute: int = 0
    max_tokens_per_minute: int | _TokenUsage = 0
    max_concurrent_requests: int | None = None
    max_tokens_per_minute: int = 0
    pbar: Optional[tqdm.tqdm] = field(default=None, repr=False, compare=False)
    response_cost: float = 0
    time_of_last_rate_limit_error: float = field(default=0.0)

    # Stats tracking
    total_requests: int = 0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    total_cost: float = 0

    # Cost per million tokens
    input_cost_per_million: Optional[float] = None
    output_cost_per_million: Optional[float] = None
    compatible_provider: Optional[str] = None

    start_time: float = field(default_factory=time.time, init=False)

    model: str = ""
    token_limit_strategy: TokenLimitStrategy = TokenLimitStrategy.default

    # Add client field and exclude from serialization
    viewer_client: Optional[Client] = field(default=None, repr=False, compare=False)

    max_concurrent_requests_seen: int = 0

    # New fields for cost tracking
    projected_remaining_cost: float = 0.0
    estimated_cost_average: float = 0.0
    num_estimates: int = 0

    def __post_init__(self):
        """Post init."""
        if self.token_limit_strategy == TokenLimitStrategy.combined:
            self.available_token_capacity = t.cast(float, self.available_token_capacity)
        else:
            self.available_token_capacity = t.cast(_TokenUsage, self.available_token_capacity)
            self.available_token_capacity = _TokenUsage()
            if not self.max_tokens_per_minute:
                self.max_tokens_per_minute = _TokenUsage()

        # Initialize cost strings
        if self.model in model_cost:
            model_pricing = model_cost[self.model]
            if model_pricing.get("input_cost_per_token") is not None:
                self.input_cost_per_million = model_pricing.get("input_cost_per_token", 0) * 1_000_000
            else:
                self.input_cost_per_million = None
            if model_pricing.get("output_cost_per_token") is not None:
                self.output_cost_per_million = model_pricing.get("output_cost_per_token", 0) * 1_000_000
            else:
                self.output_cost_per_million = None
        else:
            try:
                external_pricing = external_model_cost(self.model, provider=self.compatible_provider)
                self.input_cost_per_million = (
                    external_pricing.get("input_cost_per_token", 0) * 1_000_000 if external_pricing.get("input_cost_per_token") is not None else None
                )
                self.output_cost_per_million = (
                    external_pricing.get("output_cost_per_token", 0) * 1_000_000 if external_pricing.get("output_cost_per_token") is not None else None
                )
            except (KeyError, TypeError):
                self.input_cost_per_million = None
                self.output_cost_per_million = None

        # Handle None values for cost per million tokens
        self.input_cost_str = f"[red]${self.input_cost_per_million:.3f}[/red]" if self.input_cost_per_million is not None else "[dim]N/A[/dim]"
        if not USE_RICH_DISPLAY:
            self.input_cost_str = f"${self.input_cost_per_million:.3f}" if self.input_cost_per_million is not None else "N/A"

        self.output_cost_str = f"[red]${self.output_cost_per_million:.3f}[/red]" if self.output_cost_per_million is not None else "[dim]N/A[/dim]"
        if not USE_RICH_DISPLAY:
            self.output_cost_str = f"${self.output_cost_per_million:.3f}" if self.output_cost_per_million is not None else "N/A"

    def __str__(self):
        """String representation of the token limit strategy."""
        return (
            f"Tasks - Started: {self.num_tasks_started}, "
            f"In Progress: {self.num_tasks_in_progress}, "
            f"Succeeded: {self.num_tasks_succeeded}, "
            f"Failed: {self.num_tasks_failed}, "
            f"Already Completed: {self.num_tasks_already_completed}\n"
            f"Errors - API: {self.num_api_errors}, "
            f"Rate Limit: {self.num_rate_limit_errors}, "
            f"Other: {self.num_other_errors}, "
            f"Total: {self.num_other_errors + self.num_api_errors + self.num_rate_limit_errors}"
        )

    def start_tracker(self, console: Optional[Console] = None):
        """Start the tracker."""
        if USE_RICH_DISPLAY:
            self._start_rich_tracker(console)
        else:
            self._start_tqdm_tracker()

    def _start_rich_tracker(self, console: Optional[Console] = None):
        """Start the rich progress tracker."""
        self._console = _CONSOLE if console is None else console

        # Safety check: ensure any existing live display is stopped
        if hasattr(self._console, "_live") and self._console._live is not None:
            try:
                self._console._live.stop()
                self._console._live = None
            except Exception:
                # If stopping fails, just set to None
                self._console._live = None

        # Create progress bar display
        self._progress = Progress(
            BarColumn(bar_width=None),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("[bold white]•[/bold white] Time Elapsed"),
            TimeElapsedColumn(),
            TextColumn("[bold white]•[/bold white] Time Remaining"),
            TimeRemainingColumn(),
            console=self._console,
        )

        # Create stats display with just text columns
        self._stats = Progress(
            TextColumn("{task.description}"),
            console=self._console,
        )

        # Add tasks
        self._task_id = self._progress.add_task(
            description="",
            total=self.total_requests,
            completed=self.num_tasks_already_completed,
        )

        self._stats_task_id = self._stats.add_task(
            total=None,
            description=(
                f"Preparing to generate [blue]{self.total_requests}[/blue] responses "
                f"using [blue]{self.model}[/blue] with [blue]{self.token_limit_strategy}[/blue] "
                "token limiting strategy"
            ),
        )

        # Create Live display with both progress and stats in one panel
        self._live = Live(
            Panel(
                Group(
                    self._progress,
                    self._stats,
                ),
                title="",
                box=box.ROUNDED,
            ),
            console=self._console,
            refresh_per_second=4,
            transient=True,
        )
        self._live.start()

    def _start_tqdm_tracker(self):
        """Start the tqdm progress tracker."""
        self.pbar = tqdm.tqdm(
            total=self.total_requests,
            initial=self.num_tasks_already_completed,
            desc=f"Processing {self.model}",
            unit="req",
        )
        # Initialize last update time for periodic updates
        self._last_stats_update = time.time()
        self._last_display_update = time.time()
        # Log initial stats
        self._log_stats()

    def _update_tqdm_description(self):
        """Update the tqdm description."""
        if not USE_RICH_DISPLAY and self.pbar:
            self.pbar.set_description(
                f"Processing {MODEL}{self.model}{END} "
                f"[{SUCCESS}{self.num_tasks_succeeded} succeeded{END} • "
                f"{WARNING}{self.num_tasks_in_progress} in progress{END} • "
                f"{ERROR}{self.num_tasks_failed} failed{END} • "
                f"{COST}${self.total_cost:.3f} spent{END} • "
                f"{METRIC}{self.num_tasks_started / max(0.001, (time.time() - self.start_time) / 60):.1f} req/min{END} • "
                f"{METRIC}{self.num_tasks_succeeded / max(0.001, (time.time() - self.start_time) / 60):.1f} res/min{END}]"
            )

    def _log_stats(self):
        """Log current statistics when using tqdm mode."""
        if not USE_RICH_DISPLAY:
            elapsed_minutes = (time.time() - self.start_time) / 60
            input_tpm = self.total_prompt_tokens / max(0.001, elapsed_minutes)
            output_tpm = self.total_completion_tokens / max(0.001, elapsed_minutes)
            req_per_min = self.num_tasks_started / max(0.001, elapsed_minutes)
            res_per_min = self.num_tasks_succeeded / max(0.001, elapsed_minutes)

            # Calculate averages based on completed tasks or in-progress tasks
            total_tasks = max(1, self.num_tasks_succeeded + self.num_tasks_in_progress)
            avg_prompt = self.total_prompt_tokens / total_tasks
            avg_completion = self.total_completion_tokens / total_tasks
            projected_total = self.total_cost + self.projected_remaining_cost
            cost_per_minute = self.total_cost / max(0.01, elapsed_minutes)

            # Update TQDM description
            self._update_tqdm_description()

            # Add curator viewer link if available
            viewer_msg = ""
            if self.viewer_client and self.viewer_client.hosted and self.viewer_client.curator_viewer_url:
                viewer_msg = f"\n{HEADER}Curator Viewer:{END} {self.viewer_client.curator_viewer_url}"
            else:
                viewer_msg = f"\n{HEADER}Curator Viewer:{END} Disabled (Set CURATOR_VIEWER=1 to view at {PUBLIC_CURATOR_VIEWER_HOME_URL})"

            stats_msg = (
                f"{viewer_msg}\n"
                f"{HEADER}Requests:{END} Total: {METRIC}{self.total_requests}{END} • "
                f"Cached: {SUCCESS}{self.num_tasks_already_completed}✓{END} • "
                f"Success: {SUCCESS}{self.num_tasks_succeeded}✓{END} • "
                f"Failed: {ERROR}{self.num_tasks_failed}✗{END} • "
                f"In Progress: {WARNING}{self.num_tasks_in_progress}⋯{END} • "
                f"Req/min: {METRIC}{req_per_min:.1f}{END} • "
                f"Res/min: {METRIC}{res_per_min:.1f}{END}\n"
                f"{HEADER}Tokens:{END} Avg Input: {METRIC}{avg_prompt:.0f}{END} • "
                f"Input TPM: {METRIC}{input_tpm:.0f}{END} • "
                f"Avg Output: {METRIC}{avg_completion:.0f}{END} • "
                f"Output TPM: {METRIC}{output_tpm:.0f}{END}\n"
                f"{HEADER}Cost:{END} Current: {COST}${self.total_cost:.3f}{END} • "
                f"Est. Total: {COST}${projected_total:.3f}{END} {DIM}(${self.projected_remaining_cost:.3f} remaining){DIM}{END} • "
                f"Rate: {COST}${cost_per_minute:.3f}/min{END}\n"
                f"{HEADER}Rate Limits:{END} RPM: {METRIC}{self.max_requests_per_minute}{END} • "
                f"TPM: {METRIC}{self.max_tokens_per_minute}{END} • "
                f"TPM Strategy: {METRIC}{self.token_limit_strategy} token limit{END}\n"
                f"{HEADER}Model:{END} Name: {MODEL}{self.model}{END}\n"
                f"{HEADER}Model Pricing:{END} Per 1M tokens: "
                f"Input: {COST}{self.input_cost_str}{END} • "
                f"Output: {COST}{self.output_cost_str}{END}"
            )
            logger.info(stats_msg)

    def update_display(self):
        """Update the display based on current mode."""
        current_time = time.time()

        if USE_RICH_DISPLAY:
            self._refresh_console()
        else:
            if self.pbar:
                # Always update progress bar position
                self.pbar.n = self.num_tasks_succeeded + self.num_tasks_already_completed
                self.pbar.refresh()
                self._update_tqdm_description()

                # Update stats in any of these conditions:
                # 1. When tasks change state (in_progress, succeeded, failed)
                # 2. Every _STATUS_UPDATE_INTERVAL seconds
                # 3. When costs or tokens change
                should_update = (
                    current_time - self._last_stats_update >= _STATUS_UPDATE_INTERVAL  # Time-based update
                    and (
                        self.num_tasks_in_progress != getattr(self, "_last_in_progress", -1)  # Task state change
                        or self.num_tasks_succeeded != getattr(self, "_last_succeeded", -1)
                        or self.num_tasks_failed != getattr(self, "_last_failed", -1)
                        or self.total_tokens != getattr(self, "_last_total_tokens", -1)  # Token/cost changes
                        or self.total_cost != getattr(self, "_last_total_cost", -1)
                    )
                )

                if should_update:
                    self._log_stats()
                    self._last_stats_update = current_time
                    # Store current values for next comparison
                    self._last_in_progress = self.num_tasks_in_progress
                    self._last_succeeded = self.num_tasks_succeeded
                    self._last_failed = self.num_tasks_failed
                    self._last_total_tokens = self.total_tokens
                    self._last_total_cost = self.total_cost

    def _refresh_console(self):
        """Refresh the console display with latest stats."""
        # Calculate stats
        elapsed_minutes = (time.time() - self.start_time) / 60
        req_per_min = self.num_tasks_started / max(0.001, elapsed_minutes)
        res_per_min = self.num_tasks_succeeded / max(0.001, elapsed_minutes)
        input_tpm = self.total_prompt_tokens / max(0.001, elapsed_minutes)
        output_tpm = self.total_completion_tokens / max(0.001, elapsed_minutes)
        avg_prompt = self.total_prompt_tokens / max(1, self.num_tasks_succeeded)
        avg_completion = self.total_completion_tokens / max(1, self.num_tasks_succeeded)

        # Calculate projected total
        projected_total = self.total_cost + self.projected_remaining_cost

        # Update max concurrent requests seen
        self.max_concurrent_requests_seen = max(self.max_concurrent_requests_seen, self.num_tasks_in_progress)

        # Format stats text
        stats_text = (
            f"[bold white]Requests:[/bold white] "
            f"[white]Total:[/white] [blue]{self.total_requests}[/blue] "
            f"[white]•[/white] "
            f"[white]Cached:[/white] [green]{self.num_tasks_already_completed}✓[/green] "
            f"[white]•[/white] "
            f"[white]Success:[/white] [green]{self.num_tasks_succeeded}✓[/green] "
            f"[white]•[/white] "
            f"[white]Failed:[/white] [red]{self.num_tasks_failed}✗[/red] "
            f"[white]•[/white] "
            f"[white]In Progress:[/white] [yellow]{self.num_tasks_in_progress}⋯[/yellow] "
            f"[white]•[/white] "
            f"[white]Req/min:[/white] [blue]{req_per_min:.1f}[/blue] "
            f"[white]•[/white] "
            f"[white]Res/min:[/white] [blue]{res_per_min:.1f}[/blue]\n"
            f"[bold white]Tokens:[/bold white] "
            f"[white]Avg Input:[/white] [blue]{avg_prompt:.0f}[/blue] "
            f"[white]•[/white] "
            f"[white]Input TPM:[/white] [blue]{input_tpm:.0f}[/blue] "
            f"[white]•[/white] "
            f"[white]Avg Output:[/white] [blue]{avg_completion:.0f}[/blue] "
            f"[white]•[/white] "
            f"[white]Output TPM:[/white] [blue]{output_tpm:.0f}[/blue]\n"
            f"[bold white]Cost:[/bold white] "
            f"[white]Current:[/white] [magenta]${self.total_cost:.3f}[/magenta] "
            f"[white]•[/white] "
            f"[white]Est. Total:[/white] [magenta]${projected_total:.3f}[/magenta] [dim](${self.projected_remaining_cost:.3f} remaining)[/dim] "
            f"[white]•[/white] "
            f"[white]Rate:[/white] [magenta]${self.total_cost / max(0.01, elapsed_minutes):.3f}/min[/magenta]\n"
            f"[bold white]Rate Limits:[/bold white] "
            f"[white]RPM:[/white] [blue]{self.max_requests_per_minute}[/blue] "
            f"[white]•[/white] "
            f"[white]TPM:[/white] [blue]{self.max_tokens_per_minute}[/blue] "
            f"[white]•[/white] "
            f"[white]TPM Strategy:[/white] [blue]{self.token_limit_strategy} token limit[/blue]\n"
            f"[bold white]Model:[/bold white] "
            f"[white]Name:[/white] [blue]{self.model}[/blue]\n"
            f"[bold white]Model Pricing:[/bold white] "
            f"[white]Per 1M tokens:[/white] "
            f"[white]Input:[/white] {self.input_cost_str} "
            f"[white]•[/white] "
            f"[white]Output:[/white] {self.output_cost_str}"
        )

        # Add curator viewer link if client is available and hosted
        if self.viewer_client and self.viewer_client.hosted and self.viewer_client.curator_viewer_url:
            viewer_text = (
                f"[bold white]Curator Viewer:[/bold white] "
                f"[blue][link={self.viewer_client.curator_viewer_url}]:sparkles: Open Curator Viewer[/link] :sparkles:[/blue]\n"
                f"[dim]{self.viewer_client.curator_viewer_url}[/dim]\n"
            )
        else:
            viewer_text = (
                "[bold white]Curator Viewer:[/bold white] [yellow]Disabled[/yellow]\n"
                "Set [yellow]CURATOR_VIEWER=[cyan]1[/cyan][/yellow] to view your data live at "
                f"[blue]{PUBLIC_CURATOR_VIEWER_HOME_URL}[/blue]\n"
            )
        stats_text = viewer_text + stats_text

        # Update main progress bar
        self._progress.update(
            self._task_id,
            completed=self.num_tasks_succeeded + self.num_tasks_already_completed,
        )

        # Update stats display
        self._stats.update(
            self._stats_task_id,
            description=stats_text,
        )

    def update_stats(self, token_usage: _TokenUsage, cost: float):
        """Update statistics in the tracker with token usage and cost."""
        if token_usage:
            self.total_prompt_tokens += token_usage.input
            self.total_completion_tokens += token_usage.output
            self.total_tokens += token_usage.total
        if cost:
            self.total_cost += cost

        self.update_display()

    def stop_tracker(self):
        """Stop the tracker."""
        if USE_RICH_DISPLAY:
            if hasattr(self, "_live"):
                # Stop the live display
                self._live.stop()
                # Print the final progress state
                self._console.print(self._progress)
                self._console.print(self._stats)
        else:
            if self.pbar:
                self.pbar.close()
                # Log final stats
                self._log_stats()

        # Display final statistics table
        self.display_final_stats()

        # Clean up non-serializable fields before telemetry
        self.viewer_client = None
        temp_pbar = self.pbar
        self.pbar = None
        metadata = asdict(self)
        metadata.pop("viewer_client", None)
        metadata.pop("pbar", None)
        # Restore pbar if needed
        self.pbar = temp_pbar

        telemetry_client.capture(
            TelemetryEvent(
                event_type="OnlineRequest",
                metadata=metadata,
            )
        )

    def display_final_stats(self):
        """Display final statistics."""
        if USE_RICH_DISPLAY:
            self._display_rich_final_stats()
        else:
            self._display_simple_final_stats()

    def _display_rich_final_stats(self):
        """Display final statistics using rich table."""
        table = Table(title="Final Curator Statistics", box=box.ROUNDED)
        table.add_column("Section/Metric", style="cyan")
        table.add_column("Value", style="yellow")

        # Model Information
        table.add_row("Model", "", style="bold magenta")
        table.add_row("Name", f"[blue]{self.model}[/blue]")
        table.add_row("Rate Limit (RPM)", f"[blue]{self.max_requests_per_minute}[/blue]")
        table.add_row("Rate Limit (TPM)", f"[blue]{self.max_tokens_per_minute}[/blue]")

        # Request Statistics
        table.add_row("Requests", "", style="bold magenta")
        table.add_row("Total Processed", str(self.num_tasks_succeeded + self.num_tasks_failed))
        table.add_row("Successful", f"[green]{self.num_tasks_succeeded}[/green]")
        table.add_row("Failed", f"[red]{self.num_tasks_failed}[/red]")

        # Token Statistics
        table.add_row("Tokens", "", style="bold magenta")
        table.add_row("Total Tokens Used", f"{self.total_tokens:,}")
        table.add_row("Total Input Tokens", f"{self.total_prompt_tokens:,}")
        table.add_row("Total Output Tokens", f"{self.total_completion_tokens:,}")
        if self.num_tasks_succeeded > 0:
            table.add_row(
                "Average Tokens per Request",
                f"{int(self.total_tokens / self.num_tasks_succeeded)}",
            )
            table.add_row(
                "Average Input Tokens",
                f"{int(self.total_prompt_tokens / self.num_tasks_succeeded)}",
            )
            table.add_row(
                "Average Output Tokens",
                f"{int(self.total_completion_tokens / self.num_tasks_succeeded)}",
            )
        # Cost Statistics
        table.add_row("Costs", "", style="bold magenta")
        table.add_row("Total Cost", f"[red]${self.total_cost:.3f}[/red]")
        table.add_row(
            "Average Cost per Request",
            f"[red]${self.total_cost / max(1, self.num_tasks_succeeded):.3f}[/red]",
        )
        table.add_row("Input Cost per 1M Tokens", self.input_cost_str)
        table.add_row("Output Cost per 1M Tokens", self.output_cost_str)

        # Performance Statistics
        table.add_row("Performance", "", style="bold magenta")
        elapsed_time = time.time() - self.start_time
        elapsed_minutes = elapsed_time / 60
        req_per_min = self.num_tasks_started / max(0.001, elapsed_minutes)
        res_per_min = self.num_tasks_succeeded / max(0.001, elapsed_minutes)
        input_tpm = self.total_prompt_tokens / max(0.001, elapsed_minutes)
        output_tpm = self.total_completion_tokens / max(0.001, elapsed_minutes)

        table.add_row("Total Time", f"{elapsed_time:.2f}s")
        table.add_row(
            "Average Time per Request",
            f"{elapsed_time / max(1, self.num_tasks_succeeded):.2f}s",
        )
        table.add_row("Requests per Minute", f"{req_per_min:.1f}")
        table.add_row("Responses per Minute", f"{res_per_min:.1f}")
        table.add_row("Max Concurrent Requests", str(self.max_concurrent_requests_seen))
        table.add_row("Input Tokens per Minute", f"{input_tpm:.1f}")
        table.add_row("Output Tokens per Minute", f"{output_tpm:.1f}")

        self._console.print(table)

    def _display_simple_final_stats(self):
        """Display final statistics in plain text format."""
        elapsed_time = time.time() - self.start_time
        elapsed_minutes = elapsed_time / 60
        rpm = self.num_tasks_succeeded / max(0.001, elapsed_minutes)
        input_tpm = self.total_prompt_tokens / max(0.001, elapsed_minutes)
        output_tpm = self.total_completion_tokens / max(0.001, elapsed_minutes)

        stats = [
            f"\n{HEADER}Final Statistics:{END}",
            f"{HEADER}Model Information:{END}",
            f"  Model: {MODEL}{self.model}{END}",
            f"  Rate Limit (RPM): {METRIC}{self.max_requests_per_minute}{END}",
            f"  Rate Limit (TPM): {METRIC}{self.max_tokens_per_minute}{END}",
            "",
            f"{HEADER}Request Statistics:{END}",
            f"  Total Requests: {METRIC}{self.total_requests}{END}",
            f"  Cached: {SUCCESS}{self.num_tasks_already_completed}{END}",
            f"  Successful: {SUCCESS}{self.num_tasks_succeeded}{END}",
            f"  Failed: {ERROR}{self.num_tasks_failed}{END}",
            "",
            f"{HEADER}Token Statistics:{END}",
            f"  Total Tokens Used: {METRIC}{self.total_tokens:,}{END}",
            f"  Total Input Tokens: {METRIC}{self.total_prompt_tokens:,}{END}",
            f"  Total Output Tokens: {METRIC}{self.total_completion_tokens:,}{END}",
            f"  Average Tokens per Request: {METRIC}{int(self.total_tokens / max(1, self.num_tasks_succeeded))}{END}",
            f"  Average Input Tokens: {METRIC}{int(self.total_prompt_tokens / max(1, self.num_tasks_succeeded))}{END}",
            f"  Average Output Tokens: {METRIC}{int(self.total_completion_tokens / max(1, self.num_tasks_succeeded))}{END}",
            "",
            f"{HEADER}Cost Statistics:{END}",
            f"  Total Cost: {COST}${self.total_cost:.3f}{END}",
            f"  Average Cost per Request: {COST}${self.total_cost / max(1, self.num_tasks_succeeded):.3f}{END}",
            f"  Input Cost per 1M Tokens: {COST}{self.input_cost_str}{END}",
            f"  Output Cost per 1M Tokens: {COST}{self.output_cost_str}{END}",
            "",
            f"{HEADER}Performance Statistics:{END}",
            f"  Total Time: {METRIC}{elapsed_time:.2f}s{END}",
            f"  Average Time per Request: {METRIC}{elapsed_time / max(1, self.num_tasks_succeeded):.2f}s{END}",
            f"  Requests per Minute: {METRIC}{rpm:.1f}{END}",
            f"  Max Concurrent Requests: {METRIC}{self.max_concurrent_requests_seen}{END}",
            f"  Input Tokens per Minute: {METRIC}{input_tpm:.1f}{END}",
            f"  Output Tokens per Minute: {METRIC}{output_tpm:.1f}{END}",
        ]
        logger.info("\n".join(stats))

    def update_capacity(self):
        """Update available capacity based on time elapsed."""
        current_time = time.time()
        seconds_since_update = current_time - self.last_update_time
        if self.max_requests_per_minute is not None:
            self.available_request_capacity = min(
                self.available_request_capacity + self.max_requests_per_minute * seconds_since_update / 60.0,
                self.max_requests_per_minute,
            )

        if self.token_limit_strategy == TokenLimitStrategy.combined:
            if self.max_tokens_per_minute is not None:
                self.available_token_capacity = t.cast(int, self.available_token_capacity)
                self.max_tokens_per_minute = t.cast(int, self.max_tokens_per_minute)
                self.available_token_capacity = min(
                    self.available_token_capacity + self.max_tokens_per_minute * seconds_since_update / 60.0,
                    self.max_tokens_per_minute,
                )
        else:
            self.available_token_capacity = t.cast(_TokenUsage, self.available_token_capacity)
            self.max_tokens_per_minute = t.cast(_TokenUsage, self.max_tokens_per_minute)
            if self.max_tokens_per_minute.input is not None:
                self.available_token_capacity.input = min(
                    self.available_token_capacity.input + self.max_tokens_per_minute.input * seconds_since_update / 60.0,
                    self.max_tokens_per_minute.input,
                )
            if self.max_tokens_per_minute.output is not None:
                self.available_token_capacity.output = min(
                    self.available_token_capacity.output + self.max_tokens_per_minute.output * seconds_since_update / 60.0,
                    self.max_tokens_per_minute.output,
                )

        self.last_update_time = current_time

    def has_capacity(self, token_estimate: _TokenUsage) -> bool:
        """Check if there's enough capacity for a request."""
        self.update_capacity()
        if self.token_limit_strategy == TokenLimitStrategy.combined:
            has_capacity = self._check_combined_capacity(token_estimate)
        else:
            has_capacity = self._check_seperate_capacity(token_estimate)

        # This is a very loud log, enable only when needed
        # if not has_capacity:
        #     logger.debug(
        #         f"No capacity for request with {token_estimate} tokens."
        #         f"Available capacity: {self.available_token_capacity} tokens, "
        #         f"{int(self.available_request_capacity)} requests."
        #     )
        return has_capacity

    def _check_combined_capacity(self, token_estimate: _TokenUsage):
        self.available_token_capacity = t.cast(int, self.available_token_capacity)
        if self.max_requests_per_minute is None and self.max_tokens_per_minute is None:
            return True

        token_estimate = token_estimate.total
        has_capacity = self.available_request_capacity >= 1 and self.available_token_capacity >= token_estimate
        return has_capacity

    def _check_seperate_capacity(self, token_estimate: _TokenUsage):
        self.available_token_capacity = t.cast(_TokenUsage, self.available_token_capacity)
        if self.max_tokens_per_minute.total is None and self.max_requests_per_minute is None:
            return True

        has_capacity = (
            self.available_request_capacity >= 1
            and self.available_token_capacity.input >= token_estimate.input
            and self.available_token_capacity.output >= token_estimate.output
        )
        return has_capacity

    def consume_capacity(self, token_estimate: _TokenUsage):
        """Consume capacity for a request."""
        if self.max_requests_per_minute is not None:
            self.available_request_capacity -= 1
        if self.token_limit_strategy == TokenLimitStrategy.combined:
            if self.max_tokens_per_minute is not None:
                self.available_token_capacity = t.cast(float, self.available_token_capacity)
                self.available_token_capacity -= token_estimate.total
        else:
            self.available_token_capacity = t.cast(_TokenUsage, self.available_token_capacity)

            if self.max_tokens_per_minute is not None:
                self.available_token_capacity.input -= token_estimate.input
                self.available_token_capacity.output -= token_estimate.output

    def free_capacity(self, used: _TokenUsage, blocked: _TokenUsage):
        """Free extra consumed capacity.

        Note: This can be a negative number
        incase of under estimation of consumed capacity.
        """
        if self.token_limit_strategy == TokenLimitStrategy.seperate:
            input_free = blocked.input - used.input
            output_free = blocked.output - used.output
            self.available_token_capacity.input += input_free
            self.available_token_capacity.output += output_free
        else:
            free = blocked.total - used.total
            self.available_token_capacity += free

    def __del__(self):
        """Ensure live display is stopped on deletion."""
        if hasattr(self, "_live"):
            self._live.stop()

    def estimate_request_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for a request based on token counts."""
        input_cost = (input_tokens * (self.input_cost_per_million or 0)) / 1_000_000
        output_cost = (output_tokens * (self.output_cost_per_million or 0)) / 1_000_000
        return input_cost + output_cost

    def update_cost_projection(self, token_count: _TokenUsage | None, pre_request: bool = False):
        """Update cost projections based on token estimates or actual usage."""
        # Calculate estimated cost
        if token_count is None:
            estimated_cost = 0
        else:
            estimated_cost = self.estimate_request_cost(token_count.input, token_count.output)

        if pre_request:
            # This is a new estimate before API call
            # Update moving average of estimates
            self.num_estimates += 1
            self.estimated_cost_average = (self.estimated_cost_average * (self.num_estimates - 1) + estimated_cost) / self.num_estimates
        else:
            # Decrement estimate count since we're getting actual results (success or failure)
            if self.num_estimates > 0:
                self.num_estimates -= 1

        # Calculate remaining cost using current estimates and remaining requests
        remaining_requests = self.total_requests - (self.num_tasks_succeeded + self.num_tasks_failed + self.num_tasks_already_completed)
        if self.num_estimates > 0:
            in_flight_cost = self.estimated_cost_average * self.num_estimates

            if self.num_tasks_succeeded > 0:
                # Calculate weighted average between actual and in-flight costs
                avg_actual_cost = self.total_cost / self.num_tasks_succeeded

                total_weight = (self.num_tasks_succeeded * _SUCCESS_WEIGHT_FACTOR) + self.num_estimates
                weighted_avg_cost = ((avg_actual_cost * (self.num_tasks_succeeded * _SUCCESS_WEIGHT_FACTOR)) + in_flight_cost) / total_weight

                # Calculate remaining cost using weighted average
                self.projected_remaining_cost = weighted_avg_cost * remaining_requests
            else:
                # If no successful requests, use average of in-flight estimates
                self.projected_remaining_cost = self.estimated_cost_average * remaining_requests

        else:
            # No in-flight requests, use actual average if available
            if self.num_tasks_succeeded > 0:
                avg_actual_cost = self.total_cost / self.num_tasks_succeeded
                self.projected_remaining_cost = avg_actual_cost * remaining_requests
            else:
                # Fallback to the current estimate
                self.projected_remaining_cost = estimated_cost * remaining_requests

        self.update_display()

    def cost_info(self):
        """Get cost information for the current request."""
        return {
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_prompt_tokens,
            "total_output_tokens": self.total_completion_tokens,
            "total_cost_milli_dollars": self.total_cost * 1000,
        }
