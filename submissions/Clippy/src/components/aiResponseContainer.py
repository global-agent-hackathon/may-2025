import flet as ft
import pyperclip
from utilities.colors import DARKER_BG_ALT2


def AIResponseContainer(content: ft.Control, width: ft.OptionalNumber, key: int, page: ft.Page, res=None) -> ft.Container:
    def copy_to_clipboard(e):
        if res:
            pyperclip.copy(res)
            page.open(ft.SnackBar(ft.Text(f"Copied to Clipboard!"), duration=2))
            page.update()

    return ft.Container(
        key=key,  # type: ignore
        height=250,
        bgcolor=DARKER_BG_ALT2,
        width=width,
        border_radius=12,
        border=ft.border.all(width=2, color="#2d314a"),
        shadow=ft.BoxShadow(
            blur_radius=15,
            spread_radius=-3,
            color="#2d314a",
            offset=ft.Offset(0, 0)
        ),
        padding=24,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "Clippy Response",
                    style=ft.TextStyle(color="#9b87f5", size=20)
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        scroll=ft.ScrollMode.ALWAYS,
                        controls=[
                            content
                        ]
                    )
                ),
                ft.Container(
                    alignment=ft.alignment.bottom_right,
                    content=ft.IconButton(
                        icon=ft.Icons.COPY_ALL, icon_color="#9b87f5", on_click=copy_to_clipboard)
                )
            ]
        )
    )
