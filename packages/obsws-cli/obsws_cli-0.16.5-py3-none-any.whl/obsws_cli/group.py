"""module containing commands for manipulating groups in scenes."""

from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from . import validate
from .alias import AliasGroup
from .protocols import DataclassProtocol

app = typer.Typer(cls=AliasGroup)
out_console = Console()
err_console = Console(stderr=True, style='bold red')


@app.callback()
def main():
    """Control groups in OBS scenes."""


@app.command('list | ls')
def list_(
    ctx: typer.Context,
    scene_name: Annotated[
        Optional[str],
        typer.Argument(
            show_default='The current scene',
            help='Scene name to list groups for',
        ),
    ] = None,
):
    """List groups in a scene."""
    if not scene_name:
        scene_name = ctx.obj.get_current_program_scene().scene_name

    if not validate.scene_in_scenes(ctx, scene_name):
        err_console.print(f"Scene '{scene_name}' not found.")
        raise typer.Exit(1)

    resp = ctx.obj.get_scene_item_list(scene_name)
    groups = [
        (item.get('sceneItemId'), item.get('sourceName'), item.get('sceneItemEnabled'))
        for item in resp.scene_items
        if item.get('isGroup')
    ]

    if not groups:
        out_console.print(f"No groups found in scene '{scene_name}'.")
        raise typer.Exit()

    table = Table(title=f'Groups in Scene: {scene_name}', padding=(0, 2))

    for column in ('ID', 'Group Name', 'Enabled'):
        table.add_column(
            column, justify='left' if column == 'Group Name' else 'center', style='cyan'
        )

    for item_id, group_name, is_enabled in groups:
        table.add_row(
            str(item_id),
            group_name,
            ':white_heavy_check_mark:' if is_enabled else ':x:',
        )

    out_console.print(table)


def _get_group(group_name: str, resp: DataclassProtocol) -> dict | None:
    """Get a group from the scene item list response."""
    group = next(
        (
            item
            for item in resp.scene_items
            if item.get('sourceName') == group_name and item.get('isGroup')
        ),
        None,
    )
    return group


@app.command('show | sh')
def show(
    ctx: typer.Context,
    scene_name: Annotated[
        str,
        typer.Argument(..., show_default=False, help='Scene name the group is in'),
    ],
    group_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Group name to show')
    ],
):
    """Show a group in a scene."""
    if not validate.scene_in_scenes(ctx, scene_name):
        err_console.print(f"Scene '{scene_name}' not found.")
        raise typer.Exit(1)

    resp = ctx.obj.get_scene_item_list(scene_name)
    if (group := _get_group(group_name, resp)) is None:
        err_console.print(
            f'Group [yellow]{group_name}[/yellow] not found in scene [yellow]{scene_name}[/yellow].'
        )
        raise typer.Exit(1)

    ctx.obj.set_scene_item_enabled(
        scene_name=scene_name,
        item_id=int(group.get('sceneItemId')),
        enabled=True,
    )

    out_console.print(f'Group [green]{group_name}[/green] is now visible.')


@app.command('hide | h')
def hide(
    ctx: typer.Context,
    scene_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Scene name the group is in')
    ],
    group_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Group name to hide')
    ],
):
    """Hide a group in a scene."""
    if not validate.scene_in_scenes(ctx, scene_name):
        err_console.print(f'Scene [yellow]{scene_name}[/yellow] not found.')
        raise typer.Exit(1)

    resp = ctx.obj.get_scene_item_list(scene_name)
    if (group := _get_group(group_name, resp)) is None:
        err_console.print(
            f'Group [yellow]{group_name}[/yellow] not found in scene [yellow]{scene_name}[/yellow].'
        )
        raise typer.Exit(1)

    ctx.obj.set_scene_item_enabled(
        scene_name=scene_name,
        item_id=int(group.get('sceneItemId')),
        enabled=False,
    )

    out_console.print(f'Group [green]{group_name}[/green] is now hidden.')


@app.command('toggle | tg')
def toggle(
    ctx: typer.Context,
    scene_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Scene name the group is in')
    ],
    group_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Group name to toggle')
    ],
):
    """Toggle a group in a scene."""
    if not validate.scene_in_scenes(ctx, scene_name):
        err_console.print(f'Scene [yellow]{scene_name}[/yellow] not found.')
        raise typer.Exit(1)

    resp = ctx.obj.get_scene_item_list(scene_name)
    if (group := _get_group(group_name, resp)) is None:
        err_console.print(
            f'Group [yellow]{group_name}[/yellow] not found in scene [yellow]{scene_name}[/yellow].'
        )
        raise typer.Exit(1)

    new_state = not group.get('sceneItemEnabled')
    ctx.obj.set_scene_item_enabled(
        scene_name=scene_name,
        item_id=int(group.get('sceneItemId')),
        enabled=new_state,
    )

    if new_state:
        out_console.print(f'Group [green]{group_name}[/green] is now visible.')
    else:
        out_console.print(f'Group [green]{group_name}[/green] is now hidden.')


@app.command('status | ss')
def status(
    ctx: typer.Context,
    scene_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Scene name the group is in')
    ],
    group_name: Annotated[
        str, typer.Argument(..., show_default=False, help='Group name to check status')
    ],
):
    """Get the status of a group in a scene."""
    if not validate.scene_in_scenes(ctx, scene_name):
        err_console.print(f'Scene [yellow]{scene_name}[/yellow] not found.')
        raise typer.Exit(1)

    resp = ctx.obj.get_scene_item_list(scene_name)
    if (group := _get_group(group_name, resp)) is None:
        err_console.print(
            f'Group [yellow]{group_name}[/yellow] not found in scene [yellow]{scene_name}[/yellow].'
        )
        raise typer.Exit(1)

    enabled = ctx.obj.get_scene_item_enabled(
        scene_name=scene_name,
        item_id=int(group.get('sceneItemId')),
    )

    if enabled.scene_item_enabled:
        out_console.print(f'Group [green]{group_name}[/green] is now visible.')
    else:
        out_console.print(f'Group [green]{group_name}[/green] is now hidden.')
