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
        SELECT Books.NameBG AS "title", Books.ID AS "book_id", Related.Name AS "name_of_series", Related.ID AS "series_id",
        RelationTypes.Type AS "type_of_series"
        FROM Books
        JOIN Authors ON Books.AuthorID = AuthorID
        JOIN Related ON Books.RelatedID = Related.ID
        JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE AuthorID = ?
        """, id)

        list_with_dict_with_authors_books: list = single_authors_to_cursor.mappings().all()

        series_to_cursor: CursorResult = connection.execute("""
        SELECT DISTINCT Related.Name AS "name_of_series", Related.ID AS "series_id"
        FROM Books
        JOIN Authors ON Books.AuthorID = AuthorID
        JOIN Related ON Books.RelatedID = Related.ID
        WHERE AuthorID = ?
        """, id)

        list_with_dict_with_all_series = series_to_cursor.mappings().all()

        return render_template("authors/single_author.html", list_with_dict_with_authors_books=list_with_dict_with_authors_books,
                               author_id=id, author_name=author_name, list_with_dict_with_all_series=list_with_dict_with_all_series)


@blueprint_authors.route("/single_author_edit", methods=["GET", "POST"])
def single_author_edit():
    if request.method == "GET":
        id= request.args["id"]
        with get_connection() as connection:
            author_data_cursor: CursorResult = connection.execute("""
            SELECT *
            FROM Authors
            WHERE id = ?
            """, id)

            list_with_dict_with_author_data = author_data_cursor.mappings().all()

            return render_template("authors/single_author_edit.html", dict_with_author_data=list_with_dict_with_author_data[0])

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


@blueprint_authors.route("/series")
def series():
    series_id = request.args["id"]
    with get_connection() as connection:
        series_to_cursor: CursorResult = connection.execute("""
        SELECT Related.ID AS "series_id", Related.Name AS "series_name", Related.Description AS "series_description", 
        RelationTypes.Type AS "series_type"
        FROM Related
        JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE Related.ID = ?
        """, series_id)

        list_with_dict_with_series_info = series_to_cursor.mappings().all()

        books_in_series_to_cursor: CursorResult = connection.execute("""
        SELECT Books.NameBG AS "title", Books.ID AS "book_id"
        FROM Books
        Where Books.RelatedID = ?
        """, series_id)

        books_in_series: list[dict] = books_in_series_to_cursor.mappings().all()

        return render_template("authors/series.html", dict_with_series_info=list_with_dict_with_series_info[0],
                               books_in_series=books_in_series)

