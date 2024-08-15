import typer

app = typer.Typer()


@app.command()
def run(a: str, b: int, c: float | None = None, d: bool = True):
    print(a, b, c, d)


if __name__ == "__main__":
    app()
