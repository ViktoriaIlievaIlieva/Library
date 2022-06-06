from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

from library.new_book import new_book

blueprint_books = Blueprint("Books", __name__)


@blueprint_books.route("/mybooks")
def my_books():
    with get_connection() as connection:
        all_books_cursor: CursorResult = connection.execute("""
       SELECT Books.NameBG AS "bg_title", Books.NameENG AS "eng_title", Authors.Name AS "author_name",
        Books.AuthorID AS "author_id", IIF(Books.Read, 'прочетена','нечетена') AS "read", Books.ID AS "book_id"
       FROM Books
       JOIN Authors ON Authors.ID = Books.AuthorID 
       """)

        books_info: list[dict] = all_books_cursor.mappings().all()

        count_cursor: CursorResult = connection.execute("""
        SELECT COUNT(*) FROM Books
        """)

        count: tuple = count_cursor.fetchone()

    return render_template("mybooks/all_books.html", list_with_dict_with_books_info=books_info, count=count[0])


@blueprint_books.route("/single_book")
def single_book():
    id = request.args["id"]
    with get_connection() as connection:
        single_book_cursor: CursorResult = connection.execute("""
        SELECT Books.NameBG , Books.NameENG, Authors.Name, Formats.Format, Locations.Location, 
        IIF(Books.Read, 'прочетена', 'нечетена'), Books.Info, RelationTypes.Type||' - '||Related.Name, Related.Description, 
        Books.RelatedID
        FROM Books
        JOIN Authors ON Authors.ID = Books.AuthorID 
        JOIN Formats ON Formats.ID = Books.FormatID
        JOIN Locations ON Locations.ID = Books.LocationID
        LEFT JOIN Related ON Related.ID = Books.RelatedID
        LEFT JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE Books.ID = ?
            """, id)

        single_book_info: tuple = single_book_cursor.fetchone()

        author_id_cursor: CursorResult = connection.execute("""
        SELECT Books.AuthorID
        FROM Books
        WHERE id=?
        """, id)

        author_id = author_id_cursor.fetchone()

    return render_template("mybooks/single_book.html", bg_title=single_book_info[0], eng_title=single_book_info[1],
                           author=single_book_info[2], format=single_book_info[3], location=single_book_info[4],
                           read=single_book_info[5], review=single_book_info[6], series=single_book_info[7],
                           other_books_in_series=single_book_info[8], series_id=single_book_info[9], id=id, author_id=author_id[0])


@blueprint_books.route("/single_book_update", methods=["GET", "POST"])
def single_book_update():
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

            list_authors: list[dict] = authors_cursor.mappings().all()

            formats_cursor: CursorResult = connection.execute("""
            SELECT * 
            FROM Formats
            """)

            list_formats: list[dict] = formats_cursor.mappings().all()

            locations_cursor: CursorResult = connection.execute("""
            SELECT * 
            FROM Locations
            """)

            list_locations: list[dict] = locations_cursor.mappings().all()

            series_type_cursor: CursorResult = connection.execute("""
            SELECT *
            FROM RelationTypes
            """)

            list_series_types: list[dict] = series_type_cursor.mappings().all()

            related_cursor: CursorResult = connection.execute("""
                        SELECT ID, Name
                        FROM Related
                        """)

            list_related: list[dict] = related_cursor.mappings().all()

        return render_template("mybooks/single_book_update.html", bg_title=single_book_info[0],
                               eng_title=single_book_info[1],
                               author=single_book_info[2], format=single_book_info[3], location=single_book_info[4],
                               read=single_book_info[5], review=single_book_info[6],
                               part_of_the_series=single_book_info[7], id=id,
                               list_with_authors=list_authors, list_with_formats=list_formats,
                               list_with_locations=list_locations,
                               list_with_series_types=list_series_types, list_with_related=list_related)

    else:
        id = request.form["id"]
        if "read" in request.form:
            read = 1
        else:
            read = 0
        bg_title = request.form["bg_title"]
        eng_title = request.form["eng_title"]
        author = request.form["author"]
        format = request.form["format"]
        location = request.form["location"]
        info = request.form["info"]
        part_of_the_series = request.form["part_of_the_series"]

        with get_connection() as connection:
            connection.execute("""
            UPDATE Books
            SET NameBG=?, NameENG=?, AuthorID=?, FormatID=?, LocationID=?, RelatedID=?, Info=?, Read=?
            WHERE id=?
            """, bg_title, eng_title, author, format, location, part_of_the_series, info, read, id)

    return redirect(f"/single_book?id={id}")


@blueprint_books.route("/add_new_book", methods=["GET", "POST"])
def add_new_book():
    if request.method == "GET":

        with get_connection() as connection:

            authors_cursor: CursorResult = connection.execute("""
                   SELECT * 
                   FROM Authors
                   """)

            list_with_authors: list[dict] = authors_cursor.mappings().all()

            formats_cursor: CursorResult = connection.execute("""
                   SELECT * 
                   FROM Formats
                   """)

            list_with_formats: list[dict] = formats_cursor.mappings().all()

            locations_cursor: CursorResult = connection.execute("""
                   SELECT * 
                   FROM Locations
                   """)

            list_with_locations: list[dict] = locations_cursor.mappings().all()

            series_type_cursor: CursorResult = connection.execute("""
                   SELECT *
                   FROM RelationTypes
                   """)

            list_with_series_types: list[dict] = series_type_cursor.mappings().all()

            related_series_cursor: CursorResult = connection.execute("""
                               SELECT Related.ID, Related.Name, Related.Description, RelationTypes.Type
                               FROM Related
                               JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
                               """)

            list_with_related: list[dict] = related_series_cursor.mappings().all()

        return render_template("mybooks/add_new_book_to_library.html",
                               list_of_dict_with_authors=list_with_authors,
                               list_of_dict_with_formats=list_with_formats,
                               list_of_dict_with_locations=list_with_locations,
                               list_of_dict_with_series_types=list_with_series_types,
                               list_of_dict_with_related=list_with_related)

    else:

        new_book_id = new_book()
        return redirect(f"/single_book?id={new_book_id}")


@blueprint_books.route("/delete_single_book")
def delete_single_book():
    id = request.args["id"]
    with get_connection() as connection:
        connection.execute("""
        DELETE FROM Books
        WHERE ID=?
        """, id)

    return redirect("/mybooks")


@blueprint_books.route("/wishlist_bought", methods=["GET", "POST"])
def wishlist_bought():

    if request.method == "GET":
        id_wishlist_book = request.args["id"]
        title_new_book = request.args["title"]

        with get_connection() as connection:

            authors_cursor: CursorResult = connection.execute("""
                    SELECT * 
                    FROM Authors
                    """)

            list_with_authors: list[dict] = authors_cursor.mappings().all()

            formats_cursor: CursorResult = connection.execute("""
                    SELECT * 
                    FROM Formats
                    """)

            list_with_formats: list[dict] = formats_cursor.mappings().all()

            locations_cursor: CursorResult = connection.execute("""
                    SELECT * 
                    FROM Locations
                    """)

            list_with_locations: list[dict] = locations_cursor.mappings().all()

            series_type_cursor: CursorResult = connection.execute("""
                    SELECT *
                    FROM RelationTypes
                    """)

            list_with_series_types: list[dict] = series_type_cursor.mappings().all()

            related_series_cursor: CursorResult = connection.execute("""
                                SELECT Related.ID, Related.Name, Related.Description, RelationTypes.Type
                                FROM Related
                                JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
                                """)

            list_with_related: list[dict] = related_series_cursor.mappings().all()

        return render_template("mybooks/new_book_from_wishlist.html",
                               list_of_dict_with_authors=list_with_authors,
                               list_of_dict_with_formats=list_with_formats,
                               list_of_dict_with_locations=list_with_locations,
                               list_of_dict_with_series_types=list_with_series_types,
                               list_of_dict_with_related=list_with_related, title_new_book=title_new_book,
                               wishlist_id=id_wishlist_book)

    else:
        wishlist_book_id = request.form["wishlist_book_id"]
        new_book_id = new_book()

        with get_connection() as connection:
            connection.execute("""
            DELETE FROM Wishlists
            WHERE ID=?
            """, wishlist_book_id)

        return redirect(f"/single_book?id={new_book_id}")
