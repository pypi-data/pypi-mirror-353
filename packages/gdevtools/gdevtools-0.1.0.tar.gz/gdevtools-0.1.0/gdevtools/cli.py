import typer

from gdevtools.commands import gitlab

app = typer.Typer()
app.add_typer(gitlab.app, name="gitlab")

if __name__ == "__main__":
    app()
