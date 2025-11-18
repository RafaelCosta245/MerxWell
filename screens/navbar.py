import flet as ft

def NavBar(on_nav, selected_nav=None, on_cadastro_option=None):
    nav_items = [
        ("Backoffice", "backoffice"),
        ("Comercialização", "comercializacao"),
        ("Financeiro", "financeiro"),
        ("Banco de dados", "banco_de_dados"),
        ("E-mails", "emails"),
        ("Relatórios", "relatorios"),
        ("Simulador", "simulador"),
        ("Logout", "logout"),
    ]
    def handle_nav(e):
        if on_nav:
            on_nav(e.control.data)
    def handle_cadastro(e):
        if on_nav:
            on_nav("cadastro")
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Row(
                    [
                        ft.Text(
                            "MER",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                        ),
                        ft.Text(
                            "X",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.GREEN,
                        ),
                        ft.Text(
                            " Energia",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLACK,
                        ),
                    ],
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(left=10),
            ),
            ft.Container(expand=True),
            *[
                ft.TextButton(
                    text=label,
                    data=data,
                    on_click=handle_nav,
                    style=ft.ButtonStyle(
                        color=(
                            ft.Colors.BLUE_600
                            if selected_nav == data
                            else ft.Colors.GREY_800
                        ),
                        bgcolor=(
                            ft.Colors.BLUE_50
                            if selected_nav == data
                            else None
                        ),
                        padding=ft.padding.symmetric(horizontal=16, vertical=8),
                    ),
                )
                for label, data in nav_items
            ],
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=0,
    )