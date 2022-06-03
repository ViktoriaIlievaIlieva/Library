from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_books = Blueprint("Books", __name__)


@blueprint_books.route("/mybooks")
def my_books():
    with get_connection() as connection:
        all_books_cursor: CursorResult = connection.execute("""
       SELECT Books.NameBG AS "bg_title", Books.NameENG AS "eng_title", Authors.Name AS "author_name",
        Books.AuthorID AS "author_id", IIF(Books.Read, "прочетена", "нечетена") AS "read", Books.ID AS "book_id"
       FROM Books
       JOIN Authors ON Authors.ID = Books.AuthorID 
       """)

        books_info: list[dict] = all_books_cursor.mappings().all()

        count_cursor: CursorResult = connection.execute("""
        SELECT COUNT(*) FROM Books
        """)

        count = count_cursor.fetchone()

    return render_template("mybooks/all_books.html", list_with_dict_with_books_info=books_info, count=count[0])


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
        LEFT JOIN Related ON Related.ID = Books.RelatedID
        LEFT JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
        WHERE Books.ID = ?
            """, id)

        single_book_info: tuple = single_book_cursor.fetchone()

    return render_template("mybooks/single_book.html", bg_title=single_book_info[0], eng_title=single_book_info[1],
                           author=single_book_info[2], format=single_book_info[3], location=single_book_info[4],
                           read=single_book_info[5], review=single_book_info[6], series=single_book_info[7],
                           other_books_in_series=single_book_info[8], id=id)


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
                               read=single_book_info[5], review=single_book_info[6],
                               part_of_the_series=single_book_info[7], id=id,
                               list_with_authors=tuple_list_authors, list_with_formats=tuple_list_formats,
                               list_with_locations=tuple_list_locations,
                               list_with_series_types=tuple_list_series_types, list_with_related=tuple_list_related)

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

            list_of_dict_with_authors: list = authors_cursor.mappings().all()

            formats_cursor: CursorResult = connection.execute("""
                   SELECT * 
                   FROM Formats
                   """)

            list_of_dict_with_formats: list = formats_cursor.mappings().all()

            locations_cursor: CursorResult = connection.execute("""
                   SELECT * 
                   FROM Locations
                   """)

            list_of_dict_with_locations: list = locations_cursor.mappings().all()

            series_type_cursor: CursorResult = connection.execute("""
                   SELECT *
                   FROM RelationTypes
                   """)

            list_of_dict_with_series_types: list = series_type_cursor.mappings().all()

            related_series_cursor: CursorResult = connection.execute("""
                               SELECT Related.ID, Related.Name, Related.Description, RelationTypes.Type
                               FROM Related
                               JOIN RelationTypes ON RelationTypes.ID = Related.RelationTypeID
                               """)

            list_of_dict_with_related: list = related_series_cursor.mappings().all()

        return render_template("mybooks/add_new_book_to_library.html",
                               list_of_dict_with_authors=list_of_dict_with_authors,
                               list_of_dict_with_formats=list_of_dict_with_formats,
                               list_of_dict_with_locations=list_of_dict_with_locations,
                               list_of_dict_with_series_types=list_of_dict_with_series_types,
                               list_of_dict_with_related=list_of_dict_with_related)

    else:
        bg_title: str = request.form["bg_title"]
        eng_title: str = request.form["eng_title"]
        format: str = request.form["format"]
        location: str = request.form["location"]
        author_of_list: str = request.form["author_of_list"]
        new_author: str = request.form["new_author"]
        related_series_list: str = request.form["related_series"]
        new_series_name: str = request.form["name_new_related_series"]
        new_series_description: str = request.form["description_new_related_series"]
        type_series: str = request.form["series_type"]
        info: str = request.form["info"]

        if author_of_list == "":
            with get_connection() as connection:
                author_id = connection.execute("""
                INSERT INTO "Authors"("Name")
                VALUES (?)
                """, new_author).lastrowid
        else:
            author_id = author_of_list

        if related_series_list == "single_book":
            related_series_id = None
        elif related_series_list == "":
            with get_connection() as connection:
                related_series_id = connection.execute("""
                INSERT INTO "Related"("Name", "RelationTypeID", "Description")
                VALUES (?, ?, ?)
                """, new_series_name, type_series, new_series_description).lastrowid
        else:
            related_series_id = related_series_list

        if "read_status" in request.form:
            read_status = 1
        else:
            read_status = 0

        with get_connection() as connection:
            new_book_id = connection.execute("""
                INSERT INTO Books (NameBG, NameENG, AuthorID, FormatID, RelatedID, LocationID, Read, Info)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, bg_title, eng_title, author_id, format, related_series_id, location, read_status, info).lastrowid

        return redirect(f"/single_book?id={new_book_id}")
