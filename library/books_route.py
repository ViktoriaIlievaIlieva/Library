from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_books = Blueprint("Books", __name__)


@blueprint_books.route("/mybooks")
def my_books():
    with get_connection() as connection:
        cursor_to_result: CursorResult = connection.execute("""
       SELECT Books.NameBG AS "Заглавие", Books.NameENG AS "Title", Authors.Name AS "Автор", IIF(Books.Read, "прочетена", 
       "нечетена") AS "Статус", Books.ID
       FROM Books
       JOIN Authors ON Authors.ID = Books.AuthorID 
       """)

        books_info: list = cursor_to_result.fetchall()

    list_with_dict_book_info: list = []

    for book_info in books_info:
        bg_name = book_info[0]
        eng_name = book_info[1]
        author = book_info[2]
        read = book_info[3]
        id = book_info[4]

        book_info: dict = {"bg_name": bg_name, "eng_name": eng_name, "author": author, "read": read, "id": id}
        list_with_dict_book_info.append(book_info)

    return render_template("mybooks/all_books.html", books_info=list_with_dict_book_info)


@blueprint_books.route("/single_book")
def single_book():
    id = request.args["id"]
    with get_connection() as connection:
        single_book_cursor: CursorResult = connection.execute("""
        SELECT Books.NameBG , Books.NameENG, Authors.Name, Formats.Format, Locations.Location, 
        IIF(Books.Read, "прочетена", "нечетена"), Books.Info, RelationTypes.Type||" - "||Related.Name, Related.Description
        FROM Books
        JOIN Authors ON Authors.ID = Books.AuthorID 
        JOIN Formats ON Formats.ID = Books.FormatID
        JOIN Locations ON Locations.ID = Books.LocationID
        JOIN Related ON Related.ID = Books.RelatedID
        JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE Books.ID = ?
            """, id)

        single_book_info: tuple = single_book_cursor.fetchone()

    return render_template("mybooks/single_book.html", bg_title=single_book_info[0], eng_title=single_book_info[1],
                           author=single_book_info[2], format=single_book_info[3], location=single_book_info[4],
                           read=single_book_info[5], review=single_book_info[6], series=single_book_info[7],
                           other_books_in_series=single_book_info[8], id=id)


@blueprint_books.route("/single_book_update", methods=["GET", "POST"])
def single_book_update():
    title = request.args["bg_title"]
    if request.method == "GET":
        id = request.args["id"]
        with get_connection() as connection:
            single_book_cursor: CursorResult = connection.execute("""
                SELECT NameBG , NameENG, AuthorID, FormatID, LocationID, Read, Info, RelatedID
                FROM Books
                WHERE Books.ID = ?
                    """, id)

            single_book_info: tuple = single_book_cursor.fetchone()

            authors_cursor: CursorResult = connection.execute("""
            SELECT * 
            FROM Authors
            """)

            tuple_list_authors: list = authors_cursor.fetchall()

            formats_cursor: CursorResult = connection.execute("""
            SELECT * 
            FROM Formats
            """)

            tuple_list_formats: list = formats_cursor.fetchall()

            locations_cursor: CursorResult = connection.execute("""
            SELECT * 
            FROM Locations
            """)

            tuple_list_locations: list = locations_cursor.fetchall()

            series_type_cursor: CursorResult = connection.execute("""
            SELECT *
            FROM RelationTypes
            """)

            tuple_list_series_types: list = series_type_cursor.fetchall()

            related_cursor: CursorResult = connection.execute("""
                        SELECT ID, Name
                        FROM Related
                        """)

            tuple_list_related: list = related_cursor.fetchall()

            return render_template("mybooks/single_book_update.html", bg_title=single_book_info[0],
                                   eng_title=single_book_info[1],
                                   author=single_book_info[2], format=single_book_info[3], location=single_book_info[4],
                                   read=single_book_info[5], review=single_book_info[6], series=single_book_info[7],
                                   other_books_in_series=single_book_info[8], id=id,
                                   list_with_authors=tuple_list_authors, list_with_formats=tuple_list_formats,
                                   list_with_locations=tuple_list_locations,
                                   list_with_series_types=tuple_list_series_types, list_with_related=tuple_list_related)
