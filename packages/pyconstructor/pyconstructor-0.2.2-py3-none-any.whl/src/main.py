import logging
import shutil
import sys
from pathlib import Path

import click
import pydantic

from .core.dependencies import container
from .core.exceptions import ConfigFileNotFoundError, YamlParseError
from .core.parser import YamlParser
from .generators import ProjectGenerator
from .preview.collector import PreviewCollector

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


logger = logging.getLogger(__name__)


@click.group()
def cli() -> None:
    """Entry point for the PyConstructor command-line tool app.

    This is the main command group that provides access to all available commands.
    """


@click.command()
@click.option("-p", "--preset", default="standard", help="Preset selection.")
@click.option("-f", "--force", is_flag=True, help="Overwrite existing config file.")
def init(preset: str, force: bool) -> None:
    """Generate basic example configuration based on selected preset.

    Args:
        preset: Name of the preset to use
        force: Whether to overwrite an existing config file

    """
    config_path = Path("ddd-config.yaml")
    if config_path.exists() and not force:
        click.secho(
            "✗ Config file already exists. Use --force to overwrite.",
            fg="red",
            err=True,
        )
        return
    if force and config_path.exists():
        click.secho("⚠ Overwriting existing config file", fg="yellow")

    examples_dir = Path(__file__).parent / "templates" / "config_templates"
    source_file = examples_dir / f"ddd-config-{preset}.yaml"

    if not source_file.exists():
        click.secho(f"✗ Unknown preset: {preset}", fg="red", err=True)
        return

    try:
        shutil.copy(source_file, config_path)
        click.secho(f"✓ Generated {preset} config: {config_path}", fg="green")
    except OSError as error:
        click.secho(f"✗ Failed to create config file: {error}", fg="red", err=True)

    except Exception as error:
        click.secho(f"✗ Failed to create config file: {error}", fg="red", err=True)


@click.command()
@click.option("-f", "--file", help="Path to YAML file.")
def validate(file: str | None = None) -> None:
    """Validate the YAML configuration file.

    Args:
        file: Optional path to the configuration file

    """
    click.echo("Starting validation...")
    parser = container.get(YamlParser)
    try:
        if file:
            file_path = Path(file)
            parser.load(file_path)
        else:
            parser.load()
        click.secho(
            "✓ Configuration validated successfully",
            fg="green",
            color=True,
        )
    except YamlParseError as error:
        click.secho(
            f"✗ {error}",
            fg="red",
            err=True,
            color=True,
        )
    except ConfigFileNotFoundError as error:
        click.secho(
            f"✗ {error}",
            fg="red",
            err=True,
            color=True,
        )
    except pydantic.ValidationError as error:
        click.secho(
            f"✗ Configuration invalid: {error}",
            fg="red",
            err=True,
            color=True,
        )
        click.secho(
            "Hint: Check the documentation for correct configuration format",
            fg="red",
            err=True,
            color=True,
        )
    except Exception as error:
        click.secho(f"✗ Error: {error}", fg="red", err=True)


@click.command()
@click.option("-f", "--file", help="Path to YAML file.")
def preview(file: str | None = None) -> None:
    """Preview the project structure without generating files.

    Args:
        file: Optional path to the configuration file

    """
    try:
        path = Path(file) if file else None

        if path and not path.exists():
            click.secho(f"Error: Config file not found: {file}", fg="red", err=True)
            return

        click.echo("Project generation started.", color=True)

        container.provider.set_file_path(path)
        container.provider.set_preview_mode(preview_mode=True)
        generator: ProjectGenerator = container.get(ProjectGenerator)
        generator.generate()

        collector: PreviewCollector = container.get(PreviewCollector)
        collector.display()

    except Exception as error:
        click.secho(f"Error: {error}", fg="red", err=True)


@click.command()
@click.option("-f", "--file", help="Path to YAML file.")
def run(file: str | None = None) -> None:
    """Generate the project structure based on configuration."""
    try:
        path = Path(file) if file else None
        parser = container.get(YamlParser)

        if path and not path.exists():
            click.secho(f"Error: Config file not found: {file}", fg="red", err=True)
            return

        try:
            if file:
                file_path = Path(file)
                parser.load(file_path)
            else:
                parser.load()
        except (
            YamlParseError,
            ConfigFileNotFoundError,
            pydantic.ValidationError,
        ) as error:
            click.secho(f"✗ {error}", fg="red", err=True)
            return

        click.echo("Project generation started.", color=True)

        container.provider.set_file_path(path)
        generator = container.get(ProjectGenerator)
        generator.generate()

        click.secho("Project generation completed successfully.", fg="green")

    except Exception as error:
        click.secho(f"Error: {error}", fg="red", err=True)


cli.add_command(run)
cli.add_command(init)
cli.add_command(validate)
cli.add_command(preview)

if __name__ == "__main__":
    cli()
