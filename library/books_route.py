from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_books = Blueprint("Books", __name__)


@blueprint_books.route("/mybooks")
def my_books():
    connection = get_connection()
    cursor_to_result: CursorResult = connection.execute("""
   SELECT Books.NameBG AS "Заглавие", Books.NameENG AS "Title", Authors.Name AS "Автор", IIF(Books.Read, "прочетена", 
   "нечетена") AS "Статус", Books.ID
   FROM Books
   JOIN Authors ON Authors.ID = Books.AuthorID 
   """)

    books_info: tuple = cursor_to_result.fetchall()

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
    connection = get_connection()
    cursor_to_result = connection.execute("""
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

    single_book_info: tuple = cursor_to_result.fetchone()

    return render_template("mybooks/single_book.html", bg_title=single_book_info[0], eng_title=single_book_info[1],
                           author=single_book_info[2], format=single_book_info[3], location=single_book_info[4],
                           read=single_book_info[5], review=single_book_info[6], series=single_book_info[7],
                           other_books_in_series=single_book_info[8], id=id)



