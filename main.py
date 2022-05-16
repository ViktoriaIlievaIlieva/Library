from library.app import create_app

app = create_app()
app.run("localhost", 80, True)

