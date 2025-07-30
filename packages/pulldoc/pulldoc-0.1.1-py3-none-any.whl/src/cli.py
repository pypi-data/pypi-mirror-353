import typer

from src.logger import get_project_logger
from src.service.collector import fetch_prs
from src.service.summarizer import create_final_summary, summarize_prs

logger = get_project_logger("cli")
app = typer.Typer(
    add_completion=False,
)


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def collect(
    ctx: typer.Context,
    repo: str = typer.Argument(..., help="org/repo format"),
    start: int = typer.Option(None, "--start", help="Start PR number"),
    end: int = typer.Option(None, "--end", help="End PR number"),
):
    """Collect PR data and save to file"""
    logger.info(f"Starting: PR data collection - Repository: {repo}")
    if start is not None or end is not None:
        logger.info(f"Range specified: PR#{start or 'start'} to PR#{end or 'end'}")

    try:
        fetch_prs(
            org_repo=repo,
            start=start,
            end=end,
        )
        logger.info("Completed: PR data collection")

    except Exception as e:
        logger.error(f"Error: PR data collection failed - {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def summarize(
    ctx: typer.Context,
    repo: str = typer.Argument(..., help="org/repo format"),
    model: str = typer.Option("gpt-4o-mini", "--model", help="LLM model name to use"),
    custom_prompt: str = typer.Option("", "--custom-prompt", help="Custom prompt"),
    language: str = typer.Option("en", "--lang", help="Summary language"),
    only_total: bool = typer.Option(
        False, "--only-total", help="Generate only the final summary"
    ),
) -> dict:
    """Summarize PR data"""
    logger.info(
        f"Starting: Summary generation - Repository: {repo}, Model: {model}, Language: {language}"
    )

    try:
        if only_total:
            logger.info("Executing: Final summary only generation")
            usage = create_final_summary(
                repo_name=repo,
                model=model,
                custom_prompt=custom_prompt,
                language=language,
            )
            logger.info("Completed: Final summary generation")
        else:
            logger.info("Executing: Individual PR summary generation")
            usage = summarize_prs(
                repo_name=repo,
                model=model,
                custom_prompt=custom_prompt,
                language=language,
                batch_size=10,
            )
            logger.info("Completed: Individual PR summary generation")

            logger.info("Executing: Final summary generation")
            final_usage = create_final_summary(
                repo_name=repo,
                model=model,
                custom_prompt=custom_prompt,
                language=language,
            )
            logger.info("Completed: Final summary generation")

            for key in usage:
                usage[key] += final_usage[key]

        logger.info(f"Completed: Summary generation - Token usage: {usage}")
        return usage

    except Exception as e:
        logger.error(f"Error: Summary generation failed - {e}", exc_info=True)
        raise typer.Exit(1)


@app.command(
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
    },
)
def run(
    ctx: typer.Context,
    repo: str = typer.Argument(..., help="org/repo format"),
    start: int = typer.Option(None, "--start", help="Start PR number"),
    end: int = typer.Option(None, "--end", help="End PR number"),
    model: str = typer.Option("gpt-4o-mini", "--model", help="LLM model name to use"),
    custom_prompt: str = typer.Option("", "--custom-prompt", help="Custom prompt"),
    language: str = typer.Option("en", "--lang", help="Summary language"),
):
    """Execute PR data collection and summarization in one go (individual summaries + final summary)"""
    logger.info("=" * 50)
    logger.info("Starting: Batch execution (data collection + summary generation)")
    logger.info("=" * 50)

    try:
        # Collect PRs
        logger.info("Step 1/2: PR data collection")
        collect(
            ctx=ctx,
            repo=repo,
            start=start,
            end=end,
        )

        # Generate summaries
        logger.info("Step 2/2: Summary generation")
        usage = summarize(
            ctx=ctx,
            repo=repo,
            model=model,
            custom_prompt=custom_prompt,
            language=language,
            only_total=False,
        )

        logger.info("=" * 50)
        logger.info("Completed: Batch execution")
        logger.info(f"Final usage: {usage}")
        logger.info("=" * 50)

    except Exception as e:
        logger.error(f"Error: Batch execution failed - {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
