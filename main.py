import flet as ft
from app.main_view import main_view

def main(page: ft.Page):
    main_view(page)

if __name__ == "__main__":
    ft.app(main)