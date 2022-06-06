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

        authors: list[dict] = all_authors_to_cursor.mappings().all()

        return render_template("authors/all_authors.html", list_with_dict_with_authors=authors)


@blueprint_authors.route("/single_author")
def single_author():
    id = request.args["id"]
    with get_connection() as connection:
        single_authors_to_cursor: CursorResult = connection.execute("""
        SELECT Books.NameBG AS "title", Books.ID AS "book_id", Related.Name AS "name_of_series", Related.ID AS "series_id",
        RelationTypes.Type AS "type_of_series"
        FROM Books
        JOIN Authors ON Books.AuthorID = Authors.ID
        LEFT JOIN Related ON Books.RelatedID = Related.ID
        LEFT JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE AuthorID = ?
        """, id)

        authors_books: list[dict] = single_authors_to_cursor.mappings().all()

        author_name_cursor: CursorResult = connection.execute("""
        SELECT Authors.Name 
        FROM Authors
        WHERE ID=?
        """, id)

        author_name: tuple = author_name_cursor.fetchone()

        series_to_cursor: CursorResult = connection.execute("""
        SELECT DISTINCT Related.Name AS "name_of_series", Related.ID AS "series_id"
        FROM Books
        JOIN Authors ON Books.AuthorID = AuthorID
        JOIN Related ON Books.RelatedID = Related.ID
        WHERE AuthorID = ?
        """, id)

        all_series: list[dict] = series_to_cursor.mappings().all()

        return render_template("authors/single_author.html", list_with_dict_with_authors_books=authors_books,
                               author_id=id, author_name=author_name[0], list_with_dict_with_all_series=all_series)


@blueprint_authors.route("/single_author_edit", methods=["GET", "POST"])
def single_author_edit():
    if request.method == "GET":
        id = request.args["id"]
        with get_connection() as connection:
            author_data_cursor: CursorResult = connection.execute("""
            SELECT *
            FROM Authors
            WHERE id = ?
            """, id)

            author_data: list[dict] = author_data_cursor.mappings().all()

            return render_template("authors/single_author_edit.html", dict_with_author_data=author_data[0])

    else:
        id = request.form["id"]
        author_name = request.form["author_name"]
        with get_connection() as connection:
            connection.execute("""
            UPDATE Authors
            SET Name = ?
            WHERE ID = ?
            """, author_name, id)

        return redirect(f"/single_author?id={id}&author_name={author_name}")


