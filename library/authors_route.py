from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_authors = Blueprint("Authors", __name__)

@blueprint_authors.route("/all_authors")
def all_authors():
    with get_connection() as connection:
        all_authors_to_cursor: CursorResult = connection.execute("""
        SELECT *
        FROM Authors
        """)

        list_with_authors: list = all_authors_to_cursor.mappings().all()

        return render_template("authors/all_authors.html", list_with_dict_with_authors=list_with_authors)