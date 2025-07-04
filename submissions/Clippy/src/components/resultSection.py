import flet as ft
from utilities.fileUtils import FileUtils
from states import focusStates, scrollState, componentRef, resultsState
from flet import Ref
from utilities.FocusKeyManagement import generateFocusKey
from utilities.colors import DARKER_BG_ALT3, DARKER_BG_ALT5, DARKER_BG_ALT4, WHITE

scroll_ref = Ref[ft.ListView]()
scrollState.scrollReference = scroll_ref


def resultSection(grouped_path: dict, page: ft.Page):
    focusStates.itemIndex = 0
    focusStates.currentIndex = 0
    group_containers = []
    resultsState.resultPaths = []

    for groups, paths in grouped_path.items():
        resultsState.resultPaths.extend(paths)
        file_items = []

        for path in paths:
            focusStates.itemIndex += 1
            key = generateFocusKey(focusStates.itemIndex, "resultSection")
            file_items.append(
                ft.Container(
                    key=key,
                    bgcolor=DARKER_BG_ALT3 if focusStates.currentIndex != focusStates.itemIndex else DARKER_BG_ALT5,
                    border=ft.border.all(
                        width=1,
                        color="#374151"
                    ),
                    padding=ft.padding.all(16),
                    border_radius=12,
                    width=page.width,
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                name=(
                                    ft.Icons.PLAY_CIRCLE_OUTLINE if groups == "Audio" else
                                    ft.Icons.IMAGE_OUTLINED if groups == "Images" else
                                    ft.Icons.VIDEO_LIBRARY_OUTLINED if groups == "Video" else
                                    ft.Icons.CODE if groups == "Code" else
                                    ft.Icons.TEXT_SNIPPET_OUTLINED if groups == "Text Documents" else
                                    ft.Icons.ARCHIVE_OUTLINED if groups == "Archives" else
                                    ft.Icons.SETTINGS_APPLICATIONS if groups == "Config Data" else
                                    ft.Icons.FONT_DOWNLOAD_OUTLINED if groups == "Fonts" else
                                    ft.Icons.DISC_FULL if groups == "Disk Images" else
                                    ft.Icons.DATASET_OUTLINED if groups == "Executables" else
                                    ft.Icons.HELP_OUTLINED
                                ),
                                color="#0ea5e9",
                                size=30
                            ),
                            ft.Column(
                                expand=False,
                                spacing=2,
                                controls=[
                                    ft.Text(FileUtils.getFilename(path), style=ft.TextStyle(
                                        weight=ft.FontWeight.BOLD, size=14,color=WHITE)),
                                    ft.Text(path, style=ft.TextStyle(
                                        size=10, color=ft.Colors.GREY), width=500)
                                ]
                            )
                        ]
                    )
                )
            )

        result_container_ref = Ref[ft.Column]()

        group_container = ft.Container(
            margin=ft.margin.only(bottom=20),
            padding=ft.padding.all(10),
            width=page.width,
            border=ft.border.all(width=2, color="#0ea5e933"),
            shadow=ft.BoxShadow(
                blur_radius=15,
                spread_radius=-3,
                offset=ft.Offset(0, 0),
                color="#0ea5e933"
            ),
            bgcolor=DARKER_BG_ALT4,
            border_radius=ft.border_radius.all(12),
            content=ft.Column(
                spacing=10,
                ref=result_container_ref,
                controls=[
                    ft.Text(groups, style=ft.TextStyle(
                        size=20, weight=ft.FontWeight.W_600, color="#0ea5e9"))
                ] + file_items
            )
        )
        componentRef.resultContainersRef.append(result_container_ref)

        group_containers.append(group_container)

    lv = ft.ListView(
        expand=True,
        ref=scroll_ref,
        controls=group_containers
    )

    def updatingPage():
        page.update()

    return ft.Column(
        expand=True,
        controls=[
            lv
        ]
    )
