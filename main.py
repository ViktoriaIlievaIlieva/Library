from library.app import create_app

app = create_app()
app.run("0.0.0.0", 80, True)

