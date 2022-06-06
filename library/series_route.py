from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_series = Blueprint("Series", __name__)


@blueprint_series.route("/all_series")
def all_series():
    with get_connection() as connection:
        all_series_to_cursor: CursorResult = connection.execute("""
        SELECT DISTINCT Authors.Name AS "author_name", Related.ID AS "series_id", Related.Name AS "series_name", 
        RelationTypes.Type AS "type_of_series", Related.Description AS "series_description", Authors.ID as "author_id"
        FROM Related
        LEFT JOIN RelationTypes ON RelationTypes.ID=Related.RelationTypeID
        LEFT JOIN Books ON Books.RelatedID=Related.ID
        LEFT JOIN Authors ON Books.AuthorID=Authors.ID
        """)

        list_with_series_info: list[dict] = all_series_to_cursor.mappings().all()

        return render_template("series/all_series.html", list_with_dict_with_series_info=list_with_series_info)


@blueprint_series.route("/series")
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

        series_info: list[dict] = series_to_cursor.mappings().all()

        books_in_series_to_cursor: CursorResult = connection.execute("""
        SELECT Books.NameBG AS "title", Books.ID AS "book_id"
        FROM Books
        Where Books.RelatedID = ?
        """, series_id)

        books_in_series: list[dict] = books_in_series_to_cursor.mappings().all()

        return render_template("series/series.html", dict_with_series_info=series_info[0],
                               books_in_series=books_in_series)


@blueprint_series.route("/series_edit", methods=["GET", "POST"])
def series_edit():
    if request.method == "GET":

        series_id = request.args["id"]

        with get_connection() as connection:
            series_to_cursor: CursorResult = connection.execute("""
            SELECT Related.Name AS "name", Related.Description AS "description", RelationTypes.Type AS "type_series",
            Related.RelationTypeID AS "series_type_id"
            FROM Related
            JOIN RelationTypes ON Related.RelationTypeID=RelationTypes.ID
            WHERE Related.ID=?
            """, series_id)

            list_with_series_info: list[dict] = series_to_cursor.mappings().all()

            type_series_to_cursor: CursorResult = connection.execute("""
            SELECT *
            FROM RelationTypes
            """)

            list_with_types_of_series: list[dict] = type_series_to_cursor.mappings().all()

        return render_template("series/series_edit.html", dict_with_series_info=list_with_series_info[0],
                               list_with_dicts_with_type_of_series=list_with_types_of_series, id=series_id)

    else:
        series_id = request.form["series_id"]
        series_name = request.form["name"]
        type_of_series = request.form["type_of_series"]
        series_description = request.form["series_description"]

        with get_connection() as connection:
            connection.execute("""
            UPDATE Related
            SET Name=?, RelationTypeID=?, Description=?
            WHERE ID=?
            """, series_name, type_of_series, series_description, series_id)

        return redirect(f"/series?id={series_id}")


@blueprint_series.route("/delete_series")
def series_delete():
    series_id = request.args["id"]
    with get_connection() as connection:
        connection.execute("""
        DELETE FROM Related
        WHERE ID=?
        """, series_id)

    return redirect("/all_series")


@blueprint_series.route("/redact_series_to_add_a_book", methods=["GET", "POST"])
def redact_series_to_add_a_book():
    if request.method == "GET":
        series_id = request.args["id"]
        with get_connection() as connection:
            related_series_cursor: CursorResult = connection.execute("""
            SELECT ID, Name, Description
            FROM Related
            WHERE ID=?
            """, series_id)

            list_with_series_data: list[tuple] = related_series_cursor.fetchone()

        return render_template("series/add_books_to_series_description.html", series_id=list_with_series_data[0],
                               series_name=list_with_series_data[1], series_description=list_with_series_data[2])

    else:
        series_id = request.form["series_id"]
        series_name = request.form["series_name"]
        series_description = request.form["description_series"]

        with get_connection() as connection:
            connection.execute("""
            UPDATE Related
            SET Name=?, Description=?
            WHERE ID=?
            """, series_name, series_description, series_id)

    return redirect(f"/series?id={series_id}")