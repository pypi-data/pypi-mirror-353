"""kit Command Line Interface."""

import json
import os
from pathlib import Path
from typing import Optional

import typer

from . import __version__


def version_callback(value: bool):
    if value:
        typer.echo(f"kit version {__version__}")
        raise typer.Exit()


app = typer.Typer(help="A modular toolkit for LLM-powered codebase understanding.")


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit."
    ),
):
    """A modular toolkit for LLM-powered codebase understanding."""
    pass


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Run the kit REST API server."""
    try:
        import uvicorn

        from kit.api import app as fastapi_app
    except ImportError:
        typer.secho(
            "Error: FastAPI or Uvicorn not installed. Please reinstall kit: `pip install cased-kit`",
            fg=typer.colors.RED,
        )
        raise typer.Exit(code=1)

    typer.echo(f"Starting kit API server on http://{host}:{port}")
    uvicorn.run(fastapi_app, host=host, port=port, reload=reload)


# File Operations
@app.command("file-tree")
def file_tree(
    path: str = typer.Argument(..., help="Path to the local repository."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Git ref (SHA, tag, or branch) to checkout for remote repositories."
    ),
):
    """Get the file tree structure of a repository."""
    from kit import Repository

    try:
        repo = Repository(path, ref=ref)
        tree = repo.get_file_tree()

        if output:
            Path(output).write_text(json.dumps(tree, indent=2))
            typer.echo(f"File tree written to {output}")
        else:
            for file_info in tree:
                indicator = "📁" if file_info.get("is_dir") else "📄"
                size = f" ({file_info.get('size', 0)} bytes)" if not file_info.get("is_dir") else ""
                typer.echo(f"{indicator} {file_info['path']}{size}")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("file-content")
def file_content(
    path: str = typer.Argument(..., help="Path to the local repository."),
    file_path: str = typer.Argument(..., help="Relative path to the file within the repository."),
):
    """Get the content of a specific file in the repository."""
    from kit import Repository

    try:
        repo = Repository(path)
        content = repo.get_file_content(file_path)
        typer.echo(content)
    except FileNotFoundError:
        typer.secho(f"Error: File not found: {file_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("index")
def index(
    path: str = typer.Argument(..., help="Path to the local repository."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
):
    """Build and return a comprehensive index of the repository."""
    from kit import Repository

    try:
        repo = Repository(path)
        index_data = repo.index()

        if output:
            Path(output).write_text(json.dumps(index_data, indent=2))
            typer.echo(f"Repository index written to {output}")
        else:
            typer.echo(json.dumps(index_data, indent=2))
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# Symbol Operations
@app.command("symbols")
def extract_symbols(
    path: str = typer.Argument(..., help="Path to the local repository."),
    file_path: Optional[str] = typer.Option(None, "--file", "-f", help="Extract symbols from specific file only."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
    format: str = typer.Option("table", "--format", help="Output format: table, json, or names"),
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Git ref (SHA, tag, or branch) to checkout for remote repositories."
    ),
):
    """Extract code symbols (functions, classes, etc.) from the repository."""
    from kit import Repository

    try:
        repo = Repository(path, ref=ref)
        symbols = repo.extract_symbols(file_path)

        if output:
            Path(output).write_text(json.dumps(symbols, indent=2))
            typer.echo(f"Symbols written to {output}")
        elif format == "json":
            typer.echo(json.dumps(symbols, indent=2))
        elif format == "names":
            for symbol in symbols:
                typer.echo(symbol["name"])
        else:  # table format
            if symbols:
                typer.echo(f"{'Name':<30} {'Type':<15} {'File':<40} {'Lines'}")
                typer.echo("-" * 95)
                for symbol in symbols:
                    file_rel = symbol.get("file", "").replace(str(repo.local_path), "").lstrip("/")
                    lines = f"{symbol.get('start_line', 'N/A')}-{symbol.get('end_line', 'N/A')}"
                    typer.echo(f"{symbol['name']:<30} {symbol['type']:<15} {file_rel:<40} {lines}")
            else:
                typer.echo("No symbols found.")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("usages")
def find_symbol_usages(
    path: str = typer.Argument(..., help="Path to the local repository."),
    symbol_name: str = typer.Argument(..., help="Name of the symbol to find usages for."),
    symbol_type: Optional[str] = typer.Option(None, "--type", "-t", help="Symbol type filter (function, class, etc.)."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Git ref (SHA, tag, or branch) to checkout for remote repositories."
    ),
):
    """Find definitions and references of a specific symbol."""
    from kit import Repository

    try:
        repo = Repository(path, ref=ref)
        usages = repo.find_symbol_usages(symbol_name, symbol_type)

        if output:
            Path(output).write_text(json.dumps(usages, indent=2))
            typer.echo(f"Symbol usages written to {output}")
        else:
            if usages:
                typer.echo(f"Found {len(usages)} usage(s) of '{symbol_name}':")
                for usage in usages:
                    file_rel = usage.get("file", "").replace(str(repo.local_path), "").lstrip("/")
                    line = usage.get("line_number", usage.get("line", "N/A"))
                    context = usage.get("line_content") or usage.get("context") or ""
                    if context:
                        context = str(context).strip()
                    typer.echo(f"{file_rel}:{line}: {context}")
            else:
                typer.echo(f"No usages found for symbol '{symbol_name}'.")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# Search Operations
@app.command("search")
def search_text(
    path: str = typer.Argument(..., help="Path to the local repository."),
    query: str = typer.Argument(..., help="Text or regex pattern to search for."),
    pattern: str = typer.Option("*", "--pattern", "-p", help="Glob pattern for files to search."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Git ref (SHA, tag, or branch) to checkout for remote repositories."
    ),
):
    """Perform a textual search in a local repository."""
    from kit import Repository

    try:
        repo = Repository(path, ref=ref)
        results = repo.search_text(query, file_pattern=pattern)

        if output:
            Path(output).write_text(json.dumps(results, indent=2))
            typer.echo(f"Search results written to {output}")
        else:
            if results:
                for res in results:
                    file_rel = res["file"].replace(str(repo.local_path), "").lstrip("/")
                    typer.echo(f"{file_rel}:{res['line_number']}: {res['line'].strip()}")
            else:
                typer.echo("No results found.")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# Context Operations
@app.command("context")
def extract_context(
    path: str = typer.Argument(..., help="Path to the local repository."),
    file_path: str = typer.Argument(..., help="Relative path to the file within the repository."),
    line: int = typer.Argument(..., help="Line number to extract context around."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
):
    """Extract surrounding code context for a specific line."""
    from kit import Repository

    try:
        repo = Repository(path)
        context = repo.extract_context_around_line(file_path, line)

        if output:
            Path(output).write_text(json.dumps(context, indent=2) if context else "null")
            typer.echo(f"Context written to {output}")
        else:
            if context:
                typer.echo(f"Context for {file_path}:{line}")
                typer.echo(f"Symbol: {context.get('name', 'N/A')} ({context.get('type', 'N/A')})")
                typer.echo(f"Lines: {context.get('start_line', 'N/A')}-{context.get('end_line', 'N/A')}")
                typer.echo("Code:")
                typer.echo(context.get("code", ""))
            else:
                typer.echo(f"No context found for {file_path}:{line}")
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("chunk-lines")
def chunk_by_lines(
    path: str = typer.Argument(..., help="Path to the local repository."),
    file_path: str = typer.Argument(..., help="Relative path to the file within the repository."),
    max_lines: int = typer.Option(50, "--max-lines", "-n", help="Maximum lines per chunk."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
):
    """Chunk a file's content by line count."""
    from kit import Repository

    try:
        repo = Repository(path)
        chunks = repo.chunk_file_by_lines(file_path, max_lines)

        if output:
            Path(output).write_text(json.dumps(chunks, indent=2))
            typer.echo(f"File chunks written to {output}")
        else:
            for i, chunk in enumerate(chunks, 1):
                typer.echo(f"--- Chunk {i} ---")
                typer.echo(chunk)
                if i < len(chunks):
                    typer.echo()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command("chunk-symbols")
def chunk_by_symbols(
    path: str = typer.Argument(..., help="Path to the local repository."),
    file_path: str = typer.Argument(..., help="Relative path to the file within the repository."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
):
    """Chunk a file's content by symbols (functions, classes)."""
    from kit import Repository

    try:
        repo = Repository(path)
        chunks = repo.chunk_file_by_symbols(file_path)

        if output:
            Path(output).write_text(json.dumps(chunks, indent=2))
            typer.echo(f"Symbol chunks written to {output}")
        else:
            for chunk in chunks:
                typer.echo(f"--- {chunk.get('type', 'Symbol')}: {chunk.get('name', 'N/A')} ---")
                typer.echo(chunk.get("code", ""))
                typer.echo()
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# Export Operations
@app.command("export")
def export_data(
    path: str = typer.Argument(..., help="Path to the local repository."),
    data_type: str = typer.Argument(..., help="Type of data to export: index, symbols, file-tree, or symbol-usages."),
    output: str = typer.Argument(..., help="Output file path."),
    symbol_name: Optional[str] = typer.Option(
        None, "--symbol", help="Symbol name (required for symbol-usages export)."
    ),
    symbol_type: Optional[str] = typer.Option(
        None, "--symbol-type", help="Symbol type filter (for symbol-usages export)."
    ),
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Git ref (SHA, tag, or branch) to checkout for remote repositories."
    ),
):
    """Export repository data to JSON files."""
    from kit import Repository

    try:
        repo = Repository(path, ref=ref)

        if data_type == "index":
            repo.write_index(output)
            typer.echo(f"Repository index exported to {output}")
        elif data_type == "symbols":
            repo.write_symbols(output)
            typer.echo(f"Symbols exported to {output}")
        elif data_type == "file-tree":
            repo.write_file_tree(output)
            typer.echo(f"File tree exported to {output}")
        elif data_type == "symbol-usages":
            if not symbol_name:
                typer.secho("Error: --symbol is required for symbol-usages export", fg=typer.colors.RED)
                raise typer.Exit(code=1)
            repo.write_symbol_usages(symbol_name, output, symbol_type)
            typer.echo(f"Symbol usages for '{symbol_name}' exported to {output}")
        else:
            typer.secho(
                f"Error: Unknown data type '{data_type}'. Use: index, symbols, file-tree, or symbol-usages",
                fg=typer.colors.RED,
            )
            raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# Git Operations
@app.command("git-info")
def git_info(
    path: str = typer.Argument(..., help="Path to the local repository."),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output to JSON file instead of stdout."),
    ref: Optional[str] = typer.Option(
        None, "--ref", help="Git ref (SHA, tag, or branch) to checkout for remote repositories."
    ),
):
    """Show git repository metadata (current SHA, branch, remote URL)."""
    from kit import Repository

    try:
        repo = Repository(path, ref=ref)

        git_data = {
            "current_sha": repo.current_sha,
            "current_sha_short": repo.current_sha_short,
            "current_branch": repo.current_branch,
            "remote_url": repo.remote_url,
        }

        if output:
            import json

            Path(output).write_text(json.dumps(git_data, indent=2))
            typer.echo(f"Git info exported to {output}")
        else:
            # Human-readable format
            typer.echo("Git Repository Information:")
            typer.echo("-" * 30)
            if git_data["current_sha"]:
                typer.echo(f"Current SHA:     {git_data['current_sha']}")
                typer.echo(f"Short SHA:       {git_data['current_sha_short']}")
            if git_data["current_branch"]:
                typer.echo(f"Current Branch:  {git_data['current_branch']}")
            else:
                typer.echo("Current Branch:  (detached HEAD)")
            if git_data["remote_url"]:
                typer.echo(f"Remote URL:      {git_data['remote_url']}")

            # Check if any git info is missing
            if not any(git_data.values()):
                typer.echo("Not a git repository or no git metadata available.")

    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# PR Review Operations
@app.command("review")
def review_pr(
    init_config: bool = typer.Option(False, "--init-config", help="Create a default configuration file and exit"),
    pr_url: str = typer.Argument("", help="GitHub PR URL (https://github.com/owner/repo/pull/123)"),
    config: Optional[str] = typer.Option(
        None, "--config", "-c", help="Path to config file (default: ~/.kit/review-config.yaml)"
    ),
    model: Optional[str] = typer.Option(
        None,
        "--model",
        "-m",
        help="Override LLM model (validated against supported models: e.g., gpt-4.1-nano, gpt-4.1, claude-sonnet-4-20250514)",
    ),
    plain: bool = typer.Option(False, "--plain", "-p", help="Output raw review content for piping (no formatting)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Don't post comment, just show what would be posted"),
    agentic: bool = typer.Option(
        False, "--agentic", help="Use multi-turn agentic analysis (more thorough but expensive)"
    ),
    agentic_turns: int = typer.Option(
        15, "--agentic-turns", help="Number of analysis turns for agentic mode (default: 15)"
    ),
):
    """Review a GitHub PR using kit's repository intelligence and AI analysis.

    MODES:
    • Standard (~$0.01-0.05): kit review <pr-url>
    • Agentic (~$0.36-2.57): kit review --agentic <pr-url>

    EXAMPLES:
    kit review --init-config                                      # Setup
    kit review --dry-run https://github.com/owner/repo/pull/123   # Preview
    kit review --plain https://github.com/owner/repo/pull/123     # Pipe-friendly
    kit review https://github.com/owner/repo/pull/123             # Standard
    kit review --model gpt-4.1-nano <pr-url>                      # Ultra budget
    kit review --model claude-opus-4-20250514 <pr-url>            # Premium
    kit review --agentic --agentic-turns 8 <pr-url>               # Budget agentic
    """
    from kit.pr_review.config import ReviewConfig
    from kit.pr_review.reviewer import PRReviewer

    if init_config:
        try:
            # Create default config without needing ReviewConfig.from_file()
            config_path = config or "~/.kit/review-config.yaml"
            config_path = str(Path(config_path).expanduser())

            # Create a temporary ReviewConfig just to use the create_default_config_file method
            from kit.pr_review.config import GitHubConfig, LLMConfig, LLMProvider

            temp_config = ReviewConfig(
                github=GitHubConfig(token="temp"),
                llm=LLMConfig(provider=LLMProvider.ANTHROPIC, model="temp", api_key="temp"),
            )

            created_path = temp_config.create_default_config_file(config_path)
            typer.echo(f"✅ Created default config file at: {created_path}")
            typer.echo("\n📝 Next steps:")
            typer.echo("1. Edit the config file to add your tokens")
            typer.echo(
                "2. Set KIT_GITHUB_TOKEN and either KIT_ANTHROPIC_TOKEN or KIT_OPENAI_TOKEN environment variables, or"
            )
            typer.echo("3. Update the config file with your actual tokens")
            typer.echo("\n💡 Then try: kit review --dry-run https://github.com/owner/repo/pull/123")
            return
        except Exception as e:
            typer.secho(f"❌ Failed to create config: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    if not pr_url:
        typer.secho("❌ PR URL is required", fg=typer.colors.RED)
        typer.echo("\n💡 Example: kit review https://github.com/owner/repo/pull/123")
        typer.echo("💡 Or run: kit review --help")
        raise typer.Exit(code=1)

    try:
        # Load configuration
        review_config = ReviewConfig.from_file(config)

        # Override model if specified
        if model:
            # Auto-detect provider from model name
            from kit.pr_review.config import _detect_provider_from_model

            detected_provider = _detect_provider_from_model(model)

            if detected_provider and detected_provider != review_config.llm.provider:
                # Switch provider and update API key
                from kit.pr_review.config import LLMProvider

                old_provider = review_config.llm.provider.value
                review_config.llm.provider = detected_provider

                # Update API key for new provider
                if detected_provider == LLMProvider.ANTHROPIC:
                    new_api_key = os.getenv("KIT_ANTHROPIC_TOKEN") or os.getenv("ANTHROPIC_API_KEY")
                    if not new_api_key:
                        typer.secho(
                            f"❌ Model {model} requires Anthropic API key. Set KIT_ANTHROPIC_TOKEN.",
                            fg=typer.colors.RED,
                        )
                        raise typer.Exit(code=1)
                else:  # OpenAI
                    new_api_key = os.getenv("KIT_OPENAI_TOKEN") or os.getenv("OPENAI_API_KEY")
                    if not new_api_key:
                        typer.secho(
                            f"❌ Model {model} requires OpenAI API key. Set KIT_OPENAI_TOKEN.", fg=typer.colors.RED
                        )
                        raise typer.Exit(code=1)

                review_config.llm.api_key = new_api_key
                typer.echo(f"🔄 Switched provider: {old_provider} → {detected_provider.value}")

            review_config.llm.model = model
            if not plain:  # Only show this message if not in plain mode
                typer.echo(f"🎛️  Overriding model to: {model}")

        # Validate model exists
        from kit.pr_review.cost_tracker import CostTracker

        if not CostTracker.is_valid_model(review_config.llm.model):
            suggestions = CostTracker.get_model_suggestions(review_config.llm.model)
            typer.secho(f"❌ Invalid model: {review_config.llm.model}", fg=typer.colors.RED)
            typer.echo("\n💡 Did you mean one of these?")
            for suggestion in suggestions:
                typer.echo(f"   • {suggestion}")
            typer.echo("\n📋 All available models:")
            available = CostTracker.get_available_models()
            for provider, models in available.items():
                typer.echo(f"   {provider.upper()}:")
                for m in models[:5]:  # Show first 5 per provider
                    typer.echo(f"     • {m}")
                if len(models) > 5:
                    typer.echo(f"     ... and {len(models) - 5} more")
            raise typer.Exit(code=1)

        # Override comment posting if dry run or plain mode
        if dry_run or plain:
            review_config.post_as_comment = False
            if not plain:  # Only show this message if not in plain mode
                typer.echo("🔍 Dry run mode - will not post comments")

        # Set quiet mode for plain output
        if plain:
            # Set quiet mode to suppress all status output
            review_config.quiet = True

        # Configure agentic settings if requested
        if agentic:
            review_config.agentic_max_turns = agentic_turns
            if not plain:  # Only show this message if not in plain mode
                print(f"🤖 Agentic mode configured - max turns: {agentic_turns}")
                if agentic_turns <= 8:
                    print("💰 Expected cost: ~$0.36-0.80 (budget mode)")
                elif agentic_turns <= 15:
                    print("💰 Expected cost: ~$0.80-1.50 (standard mode)")
                else:
                    print("💰 Expected cost: ~$1.50-2.57 (extended mode)")
        else:
            if not plain:  # Only show this message if not in plain mode
                print("🛠️ Standard mode configured - repository intelligence enabled")

        # Create reviewer and run review
        if agentic:
            from kit.pr_review.agentic_reviewer import AgenticPRReviewer

            agentic_reviewer = AgenticPRReviewer(review_config)
            comment = agentic_reviewer.review_pr_agentic(pr_url)
        else:
            standard_reviewer = PRReviewer(review_config)
            comment = standard_reviewer.review_pr(pr_url)

        # Handle output based on mode
        if plain:
            # Plain mode: just output the review content for piping
            typer.echo(comment)
        elif dry_run:
            # Dry run mode: show formatted preview
            typer.echo("\n" + "=" * 60)
            typer.echo("REVIEW COMMENT THAT WOULD BE POSTED:")
            typer.echo("=" * 60)
            typer.echo(comment)
            typer.echo("=" * 60)
        else:
            # Normal mode: post comment and show success
            typer.echo("✅ Review completed and comment posted!")

    except ValueError as e:
        typer.secho(f"❌ Configuration error: {e}", fg=typer.colors.RED)
        typer.echo("\n💡 Try running: kit review --init-config")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.secho(f"❌ Review failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


# Cache Management
@app.command("review-cache")
def review_cache(
    action: str = typer.Argument(..., help="Action: status, cleanup, clear"),
    max_size: Optional[float] = typer.Option(None, "--max-size", help="Maximum cache size in GB (for cleanup)"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Path to config file"),
):
    """Manage repository cache for PR reviews.

    Actions:
    - status: Show cache size and location
    - cleanup: Remove old cached repositories (optionally with --max-size)
    - clear: Remove all cached repositories

    Examples:

    # Show cache status
    kit review-cache status

    # Clean up cache to max 2GB
    kit review-cache cleanup --max-size 2.0

    # Clear all cache
    kit review-cache clear
    """
    from kit.pr_review.cache import RepoCache
    from kit.pr_review.config import ReviewConfig

    try:
        # Load configuration
        review_config = ReviewConfig.from_file(config)
        cache = RepoCache(review_config)

        if action == "status":
            if cache.cache_dir.exists():
                # Calculate cache size
                total_size = sum(f.stat().st_size for f in cache.cache_dir.rglob("*") if f.is_file()) / (
                    1024**3
                )  # Convert to GB

                # Count repositories
                repo_count = 0
                for owner_dir in cache.cache_dir.iterdir():
                    if owner_dir.is_dir():
                        repo_count += len([d for d in owner_dir.iterdir() if d.is_dir()])

                typer.echo(f"📁 Cache location: {cache.cache_dir}")
                typer.echo(f"📊 Cache size: {total_size:.2f} GB")
                typer.echo(f"📦 Cached repositories: {repo_count}")
                typer.echo(f"⏰ TTL: {review_config.cache_ttl_hours} hours")
            else:
                typer.echo("📭 No cache directory found")

        elif action == "cleanup":
            cache.cleanup_cache(max_size)
            typer.echo("✅ Cache cleanup completed")

        elif action == "clear":
            cache.clear_cache()
            typer.echo("✅ Cache cleared")

        else:
            typer.secho(f"❌ Unknown action: {action}. Use: status, cleanup, clear", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    except Exception as e:
        typer.secho(f"❌ Cache operation failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
