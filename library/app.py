from flask import Flask

from library.home_route import blueprint_home
from library.wishlist_route import blueprint_wishlist


def create_app() -> Flask:
    app = Flask("Library", template_folder="library/templates")

    app.register_blueprint(blueprint_home)
    app.register_blueprint(blueprint_wishlist)

    return app
