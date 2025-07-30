import typer

app = typer.Typer()

@app.callback()
def callback():
    pass

@app.command()
def shoot(file_path: str):
    print(file_path)


