from flask import Blueprint, render_template, request, redirect
from library.database import get_connection
from sqlalchemy.engine import CursorResult

blueprint_books = Blueprint("Books", __name__)


@blueprint_books.route("/mybooks", methods=["GET", "POST"])
def my_books():
    connection = get_connection()
    cursor_to_result: CursorResult = connection.execute("""
   SELECT Books.NameBG AS "Заглавие", Books.NameENG AS "Title", Authors.Name AS "Автор", IIF(Books.Read, "прочетена", 
   "нечетена") AS "Статус"
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

        book_info: dict = {"bg_name": bg_name, "eng_name": eng_name, "author": author, "read": read}
        list_with_dict_book_info.append(book_info)

    return render_template("all_books.html", books_info=list_with_dict_book_info)

