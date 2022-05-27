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


@blueprint_authors.route("/single_author")
def single_author():
    id = request.args["id"]
    author_name = request.args["author_name"]
    with get_connection() as connection:

        single_authors_to_cursor: CursorResult = connection.execute("""
        SELECT Books.NameBG AS "title", Books.ID AS "book_id", Related.Name AS "name_of_series", 
        RelationTypes.Type AS "type_of_series"
        FROM Books
        JOIN Authors ON Books.AuthorID = AuthorID
        JOIN Related ON Books.RelatedID = Related.ID
        JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE AuthorID = ?
        """, id)

        list_with_dict_with_authors_books: list = single_authors_to_cursor.mappings().all()

        return render_template("authors/single_author.html", list_with_dict_with_authors_books=list_with_dict_with_authors_books,
                               author_id=id, author_name=author_name)

