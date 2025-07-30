import typer

app = typer.Typer()

@app.callback()
def callback():
    pass

@app.command()
def shoot():
    typer.echo("Shoot")


