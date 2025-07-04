from agno.media import File
import flet as ft
from utilities.debouncer import *
from utilities.fileUtils import *
from utilities.openApp import *
from utilities.listSorter import *
from utilities.searchUtils import *
from components.resultSection import *
from dotenv import dotenv_values
from components.aiResponseContainer import *
from agentTools.agentTools import *
from utilities.checkPermissions import *
from agents.mainAgent import MainAgent
from utilities.getResourcePath import get_asset_path
from states import thinkingStates, focusStates, resultsState
from agents.agentsUtility import AgentsUtility
from components.summaryPopup import SummaryPopup
from agents.multiModalAgent import MultiModalAgent
from utilities.colors import PRIMARY_PURPLE, DARK_BG, DARKER_BG, DARKER_BG_ALT, DARKER_BG_ALT2, DARKER_BG_ALT3, DARKER_BG_ALT4, DARKER_BG_ALT5, BORDER_GREY, TEXT_GREY, BLUE, BLUE_TRANSPARENT, WHITE

#FOR PYINSTALLER NEW VERSION ERROR FIX ON RUNNING EXE
import sys
sys.stdout = open(os.devnull, "w")

def adjust_window_height(mainColumn: ft.Column, page: ft.Page):
    match len(mainColumn.controls):
        case 1:
            page.window.height = 70
            page.title = f"{100}"
        case 2:
            if contains_element(mainColumn, "search_result_container"):
                page.window.height = 450
                page.title = f"{450}"

            if contains_element(mainColumn, "response"):
                page.window.height = 350
                page.title = f"{350}"

        case 3:
            page.window.height = 650
            page.title = f"{650}"


def remove_control_by_key(container: ft.Column, key: str):
    container.controls = [
        c for c in container.controls if getattr(c, "key", None) != key]


def contains_element(mainColumn: ft.Column, key: str):
    for c in mainColumn.controls:
        if getattr(c, "key") == key:
            return True
    return False


def debounced_search(query: str, latest_query: dict, page: ft.Page, mainColum: ft.Column):
    if not query.strip():
        remove_control_by_key(
            key="search_result_container", container=mainColum)
        adjust_window_height(mainColum, page)
        remove_control_by_key(
            key="response", container=mainColum)
        return
    if query != latest_query["value"]:
        return

    results = SearchUtils.search_files(query)
    sortedRes = ListSorter.sortListToDict(results)
    resultsState.previousResult = sortedRes

    if results:
        remove_control_by_key(
            key="search_result_container", container=mainColum)
        results_container = resultSection(sortedRes, page)
        result_main_container = ft.Container(
            key="search_result_container",
            height=370,
            content=results_container
        )
        mainColum.controls.append(result_main_container)
        adjust_window_height(mainColum, page)
        setState(page)
    else:
        remove_control_by_key(
            key="search_result_container", container=mainColum)
        adjust_window_height(mainColum, page)
        setState(page)


def expand_window(e: ft.ControlEvent, debouncer: Debouncer, page: ft.Page, mainColumn: ft.Column):
    query = e.control.value.strip()
    latest_query = {"value": ""}
    latest_query["value"] = query

    if not query:
        remove_control_by_key(
            key="search_result_container", container=mainColumn)
        remove_control_by_key(mainColumn, "response")
        adjust_window_height(mainColumn, page)
        setState(page)
        return
    else:
        if len(query) > 3:
            debouncer.callback = lambda: debounced_search(
                query, latest_query, page, mainColumn
            )
            debouncer.call()


async def searchBarEntered(e: str, mainColumn: ft.Column, page: ft.Page):
    remove_control_by_key(mainColumn, "response")
    mainColumn.controls.insert(1, AIResponseContainer(
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.Text("I am thinking...."),
            ft.ProgressRing(color=PRIMARY_PURPLE)
        ]), width=page.width, key="response", page=page))
    adjust_window_height(mainColumn, page)
    setState(page)
    res = await mainAgent.initiateMainAgent(e or "")

    remove_control_by_key(mainColumn, "response")
    mainColumn.controls.insert(1, AIResponseContainer(
        ft.Markdown(value=res, selectable=True,
                    shrink_wrap=True,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB, code_theme=ft.MarkdownCodeTheme.DARCULA),
        width=page.width, key="response", res=res, page=page))  # type: ignore
    adjust_window_height(mainColumn, page)
    setState(page)


keys = dotenv_values(dotenv_path=get_asset_path(".env"))
mainAgent = MainAgent(apiKey=keys["GEMINI_API_KEY"]
                      or "", model="gemini-2.0-flash")
fileSummarizeAgent = AgentsUtility.fileSummarizeAgent(apiKey=keys["GEMINI_API_KEY"]
                                                      or "", id="gemini-2.0-flash")

# --- MultiModalAgent instance ---
multiModalAgent = MultiModalAgent.create(
    apiKey=keys["GEMINI_API_KEY"] or "", model="gemini-2.0-flash")

# --- Summary Popup State ---
summary_dialog = None

# --- Loading Overlay State ---
loading_overlay = None


def show_loading_overlay(page: ft.Page, message: str = "Summarizing file..."):
    global loading_overlay
    loading_overlay = ft.Container(
        ft.Column([
            ft.ProgressRing(color=PRIMARY_PURPLE, width=60, height=60),
            ft.Text(message, color=PRIMARY_PURPLE, size=18)
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        alignment=ft.alignment.center,
        bgcolor=DARK_BG,  # solid dark color
        expand=True,
        key="loading_overlay",
        visible=True,
    )
    if loading_overlay not in page.overlay:
        page.overlay.append(loading_overlay)
    loading_overlay.visible = True
    page.update()


def hide_loading_overlay(page: ft.Page):
    global loading_overlay
    if loading_overlay and loading_overlay in page.overlay:
        loading_overlay.visible = False
        page.update()


def show_summary_popup(page: ft.Page, summary: str, file_path: str = None):
    global summary_dialog

    def close_popup(e=None):
        summary_dialog.open = False
        page.update()

    def open_file_handler(path):
        from utilities.openApp import OpenApp
        OpenApp.open(path)

    summary_dialog = SummaryPopup(
        summary,
        on_close=close_popup,
        on_open_file=open_file_handler if file_path else None,
        file_path=file_path
    )
    if summary_dialog not in page.overlay:
        page.overlay.append(summary_dialog)
    summary_dialog.open = True
    page.update()


async def summarizeFile(filePath: str, page: ft.Page):
    show_loading_overlay(page)
    summary = await multiModalAgent.summarize(filePath)
    hide_loading_overlay(page)
    # Show summary.content if present, else show summary
    summary_text = getattr(summary, "content", summary)
    show_summary_popup(page, summary_text, file_path=filePath)


def onWindowEvent(event: ft.WindowEvent):
    if event.type == ft.WindowEventType.FOCUS:
        return
    if event.type == ft.WindowEventType.BLUR:
        return


def setState(page: ft.Page):
    page.update(page)


def update_focus_and_scroll(direction: str, page: ft.Page):
    if direction == "up":
        focusStates.currentIndex -= 1
    elif direction == "down":
        focusStates.currentIndex += 1

    for ref in componentRef.resultContainersRef:
        if ref:
            for c in ref.current.controls:
                key = getattr(c, "key", None)
                if key == generateFocusKey(focusStates.currentIndex, "resultSection"):
                    if hasattr(c, "bgcolor"):
                        c.bgcolor = DARKER_BG_ALT5
                elif key is not None and "resultSection" in key:
                    if hasattr(c, "bgcolor"):
                        c.bgcolor = DARKER_BG_ALT3
    setState(page)
    if scrollState.scrollReference is not None:
        key = generateFocusKey(focusStates.currentIndex, "resultSection")
        scrollState.scrollReference.current.scroll_to(
            key=key, duration=200)
        if focusStates.currentIndex == 1:
            scrollState.scrollReference.current.scroll_to(
                offset=0, duration=200)
        setState(page)


def handleKeyboardEvent(page: ft.Page, event: ft.KeyboardEvent, container: ft.Column):
    if event.key == "Enter" and event.ctrl == True and event.shift == False:
        page.run_task(
            summarizeFile, resultsState.resultPaths[focusStates.currentIndex-1], page)
    if (event.key == "Enter" and event.shift == True and event.ctrl == False):
        if focusStates.currentIndex > 0:
            OpenApp.open(resultsState.resultPaths[focusStates.currentIndex-1])
    if (event.key == "Enter" and event.shift == False and event.ctrl == False):
        page.run_task(
            searchBarEntered, componentRef.searchBarRef.current.value or "", container, page)

    if (event.key == "Arrow Up"):
        if focusStates.currentIndex > 1:
            update_focus_and_scroll("up", page)

    if (event.key == "Arrow Down"):
        if focusStates.itemIndex > focusStates.currentIndex:
            update_focus_and_scroll("down", page)

    # Add Escape key handler for closing summary popup
    global summary_dialog
    if event.key == "Escape" and summary_dialog and getattr(summary_dialog, 'open', False):
        summary_dialog.open = False
        page.update()
        return


async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.window.on_event = onWindowEvent
    page.window.width = 620
    page.window.max_width = 620
    page.window.min_width = 620
    page.window.min_height = 70
    page.window.height = 100
    page.window.resizable = True
    page.window.frameless = True
    page.window.always_on_top = True
    page.title = f"{100}"
    page.bgcolor = DARKER_BG
    debouncer = Debouncer(1, None)
    mainColumn = ft.Column()
    search_bar_ref = Ref[ft.TextField]()

    page.on_keyboard_event = lambda event: handleKeyboardEvent(
        page, event, mainColumn)

    search = ft.TextField(
        hint_text="Search something...",
        ref=search_bar_ref,
        border_color=BORDER_GREY,
        bgcolor=DARKER_BG_ALT,
        on_change=lambda e: expand_window(e, debouncer, page, mainColumn),
        border_radius=12,
        color=WHITE,
        hint_style=ft.TextStyle(color=PRIMARY_PURPLE),
        suffix_icon=ft.Icon(ft.Icons.SEARCH, size=30, color=PRIMARY_PURPLE),

    )
    componentRef.searchBarRef = search_bar_ref
    mainColumn.controls.append(search)

    page.add(mainColumn)

    CheckPermission.checkDiskPermission()


ft.app(target=main, view=None, port=8550)
# ft.app(target=main)
