import flet as ft
from utilities.colors import DARK_BG, PRIMARY_PURPLE, DARKER_BG_ALT2


def SummaryPopup(summary: str, on_close, on_open_file=None, file_path=None, width: int = 500, height: int = 400):
    # Add a cross button and an open file button, make the content scrollable
    action_buttons = [
        ft.IconButton(icon=ft.Icons.CLOSE, on_click=on_close,
                      tooltip="Close", icon_color=PRIMARY_PURPLE)
    ]
    if on_open_file and file_path:
        action_buttons.insert(0, ft.IconButton(icon=ft.Icons.OPEN_IN_NEW, on_click=lambda e: on_open_file(
            file_path), tooltip="Open File", icon_color=PRIMARY_PURPLE))
    return ft.AlertDialog(
        bgcolor=DARK_BG,
        modal=True,
        title=ft.Row([
            ft.Text("File Summary", style=ft.TextStyle(
                size=18, color=PRIMARY_PURPLE), expand=True),
            *action_buttons
        ]),
        content=ft.Container(
            width=width,
            height=height,
            bgcolor=DARKER_BG_ALT2,
            border_radius=12,
            padding=20,
            content=ft.Column([
                ft.ListView(
                    controls=[
                        ft.Markdown(
                            value=summary,
                            selectable=True,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            code_theme=ft.MarkdownCodeTheme.DARCULA,
                        )
                    ],
                    expand=True,
                    spacing=10,
                    padding=0,
                    auto_scroll=False
                ),
                ft.Row([
                    ft.ElevatedButton("Close", on_click=on_close,
                                      bgcolor=PRIMARY_PURPLE, color=ft.Colors.WHITE)
                ], alignment=ft.MainAxisAlignment.END)
            ], expand=True)
        )
    )
