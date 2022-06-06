from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_series = Blueprint("Series", __name__)


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
