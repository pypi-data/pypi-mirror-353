import typer
from src.renpy_assets.commands import scan, generate


app = typer.Typer()    
app.add_typer(scan.app)
app.add_typer(generate.app)


if __name__ == '__main__':
    app()