"""module for taking screenshots using OBS WebSocket API."""

from pathlib import Path
from typing import Annotated

import obsws_python as obsws
import typer
from rich.console import Console

from .alias import AliasGroup

app = typer.Typer(cls=AliasGroup)
out_console = Console()
err_console = Console(
    stderr=True,
)


@app.callback()
def main():
    """Take screenshots using OBS."""


@app.command('save | sv')
def save(
    ctx: typer.Context,
    source_name: Annotated[
        str,
        typer.Argument(
            help='Name of the source to take a screenshot of.',
        ),
    ],
    output_path: Annotated[
        Path,
        # Since the CLI and OBS may be running on different platforms,
        # we won't validate the path here.
        typer.Argument(
            ...,
            file_okay=True,
            dir_okay=False,
            help='Path to save the screenshot.',
        ),
    ],
    width: Annotated[
        float,
        typer.Option(
            help='Width of the screenshot.',
        ),
    ] = 1920,
    height: Annotated[
        float,
        typer.Option(
            help='Height of the screenshot.',
        ),
    ] = 1080,
    quality: Annotated[
        float,
        typer.Option(
            min=1,
            max=100,
            help='Quality of the screenshot (1-100).',
        ),
    ] = None,
):
    """Take a screenshot and save it to a file."""
    try:
        ctx.obj.save_source_screenshot(
            name=source_name,
            img_format=output_path.suffix.lstrip('.').lower(),
            file_path=str(output_path),
            width=width,
            height=height,
            quality=quality if quality else -1,  # -1 means default quality
        )
    except obsws.error.OBSSDKRequestError as e:
        match e.code:
            case 403:
                err_console.print(
                    'The image format (file extension) must be included in the file name '
                    "for example: '/path/to/screenshot.png'.",
                )
                raise typer.Exit(1)
            case 600:
                err_console.print(f"No source was found by the name of '{source_name}'")
                raise typer.Exit(1)
            case _:
                raise

    out_console.print(f"Screenshot saved to [bold]'{output_path}'[/bold].")
