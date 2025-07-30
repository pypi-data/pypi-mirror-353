from pathlib import Path
import typer
from typing_extensions import Annotated
from readme_generator.readme_builder import build_readme


def generate(
    repo_path: Annotated[
        str,
        typer.Option(
            help="Path to the repository.",
        ),
    ] = "",
    overview: Annotated[
        str,
        typer.Option(
            help="Overview text for the README.",
        ),
    ] = "",
    exclude_dirs: Annotated[
        list[str],
        typer.Option(
            help="Directories to exclude from the folder tree. Can be used multiple times.",
            show_default=False,
            rich_help_panel="Folder Tree Options",
        ),
    ] = [],
    exclude_files: Annotated[
        list[str],
        typer.Option(
            help="Files to exclude from the folder tree. Can be used multiple times.",
            show_default=False,
            rich_help_panel="Folder Tree Options",
        ),
    ] = [],
) -> None:
    """
    Generate README.md for a repository.

    Args:
        repo_path (str): Path to the repository.
        overview (str): Overview text for the README.
        exclude_dirs (list[str]): Directories to exclude from the folder tree.
        exclude_files (list[str]): Files to exclude from the folder tree.
    """
    if not repo_path:
        repo_path = str(Path.cwd())
    readme_content = build_readme(
        repo_path,
        overview_text=overview,
        exclude_dirs=set(exclude_dirs),
        exclude_files=set(exclude_files),
    )
    readme_path = Path(repo_path) / "README.md"
    if readme_path.exists():
        try:
            typer.echo(
                f"⚠️ README.md already exists at {readme_path.resolve()}. Saving as README_generated.md instead."
            )
        except:
            typer.echo(
                f"WARNING: README.md already exists at {readme_path.resolve()}. Saving as README_generated.md instead."
            )
        readme_path = readme_path.with_name("README_generated.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    try:
        typer.echo(f"✅ README.md generated at {readme_path.resolve()}")
    except:
        typer.echo(f"README.md generated at {readme_path.resolve()}.")


if __name__ == "__main__":
    typer.run(generate)
