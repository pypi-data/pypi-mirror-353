import typer

from gdevtools.commands.gitlab import variables

app = typer.Typer()
app.add_typer(variables.app, name="variables")
