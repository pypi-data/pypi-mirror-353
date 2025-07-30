import typer
app = typer.Typer()


@app.command()
def predict(path: str):
    print("Here are your input files: " + path)

    # for filename in os.listdir(file_path):
    #     print("Type: " + type(filename) + ", " + "Name: " + filename)