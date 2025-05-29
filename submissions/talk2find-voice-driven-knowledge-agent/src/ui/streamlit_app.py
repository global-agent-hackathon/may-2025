import logging
import os
import queue
import re
import sys
import threading
import time
from typing import Any, Dict, List, Tuple, cast

import pyaudio
import streamlit as st
import yaml
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 親ディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

load_dotenv()

from src.audio import AudioInput  # noqa: E402
from src.audio.speech_to_text import (  # noqa: E402
    AzureSpeechService,
    SpeechToText,
)
from src.search.search_pdf import PDFSearcher  # noqa: E402
from src.search.search_web import WebSearcher  # noqa: E402
from src.summarization import Summarizer  # noqa: E402

# Localization dictionaries
TRANSLATIONS = {
    "en": {
        "title": "Ambient Agent",
        "recording": "🎤 Recording in progress. Recognizing speech. (Recording time: {duration})",
        "not_recording": "⏹️ Recording is stopped.",
        "select_device": "Select Audio Input Device",
        "start_recording": "Start Recording",
        "stop_recording": "Stop Recording",
        "refresh_pdf": "Refresh PDF Index",
        "pdf_refreshed": "PDF index refreshed successfully!",
        "transcription": "Transcription",
        "transcription_help": "You can select text here and use it for search",
        "transcription_label": "Transcription content (you can select text for search)",
        "transcription_placeholder": "Speech recognition results will appear here...",
        "search_input": "Enter or paste text to search",
        "search_button": "Search with Text",
        "summary": "Summary",
        "web_search": "Web Search",
        "related_info": "Related Information",
        "related_pdf_found": "Related PDF: {count} found",
        "filename": "Filename",
        "page_number": "Page Number",
        "prev_pdf": "Previous PDF",
        "next_pdf": "Next PDF",
        "pdf_error": "Could not retrieve PDF page image",
        "no_related_info": "No related information found. Continue the conversation.",
        "language": "Language",
    },
    "ja": {
        "title": "Ambient Agent",
        "recording": "🎤 録音中です。音声を認識しています。 (録音時間: {duration})",
        "not_recording": "⏹️ 録音は停止中です。",
        "select_device": "音声入力デバイスを選択",
        "start_recording": "録音開始",
        "stop_recording": "録音停止",
        "refresh_pdf": "PDF索引を更新",
        "pdf_refreshed": "PDF索引が正常に更新されました！",
        "transcription": "文字起こし",
        "transcription_help": "テキストを選択してコピーし、検索ボックスに貼り付けることができます",
        "transcription_label": "書き起こし内容 (テキストを選択して検索に利用できます)",
        "transcription_placeholder": "音声認識結果がここに表示されます...",
        "search_input": "検索するテキストを入力または貼り付け",
        "search_button": "テキストで検索",
        "summary": "要約",
        "web_search": "Web検索",
        "related_info": "関連情報",
        "related_pdf_found": "関連PDF: {count}件見つかりました",
        "filename": "ファイル名",
        "page_number": "ページ番号",
        "prev_pdf": "前のPDF",
        "next_pdf": "次のPDF",
        "pdf_error": "PDFページ画像を取得できませんでした",
        "no_related_info": "関連する情報が見つかりません。会話を続けてください。",
        "language": "言語",
    },
}


def load_config() -> Dict[str, Any]:
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "config",
        "config.yaml",
    )
    with open(config_path, "r") as f:
        config = cast(Dict[str, Any], yaml.safe_load(f))

    return config


def get_audio_devices() -> List[Tuple[int, str]]:
    p = pyaudio.PyAudio()
    devices: List[Tuple[int, str]] = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if int(device_info["maxInputChannels"]) > 0:
            devices.append((i, str(device_info["name"])))
    p.terminate()
    return devices


def get_text(key: str, lang: str, **kwargs: Any) -> str:
    """Get localized text based on the selected language"""
    text = TRANSLATIONS.get(lang, {}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


def process_summary_and_search_async(
    full_transcription: str,
    current_language: str,
    summarizer_config: dict,
    pdf_searcher_instance: PDFSearcher | None,
    web_searcher_instance: WebSearcher | None,
    results_queue: queue.Queue,
) -> None:
    """Processes summary and PDF search in a background thread."""
    logger.info(f"Background task started for transcription: {full_transcription[:50]}...")
    summary_text = ""
    generated_summary_for_search = ""  # Separate variable for what's used in search

    try:
        temp_summarizer = Summarizer(
            interval_seconds=summarizer_config["interval_seconds"],
            max_length=summarizer_config["max_length"],
            language=current_language,
        )
        if full_transcription.strip():
            summary_text = temp_summarizer.generate_summary(full_transcription)
            generated_summary_for_search = summary_text  # Use the generated summary for search
            logger.info(f"Background task: Summary generated: {summary_text[:50]}...")
        else:
            logger.info("Background task: Transcription was empty, skipping summary.")

        pdf_pages = []
        if generated_summary_for_search.strip() and pdf_searcher_instance is not None:
            cleaned_query = re.sub(
                r"^[-\s\*\n]+", "", generated_summary_for_search, flags=re.MULTILINE
            )
            cleaned_query = cleaned_query.replace("\n", " ").strip()
            if cleaned_query:
                logger.info(f"Background task: Searching PDFs with query: {cleaned_query[:50]}...")
                pdf_pages = pdf_searcher_instance.search(cleaned_query, top_k=5)
                logger.info(f"Background task: PDF search found {len(pdf_pages)} items.")
            else:
                logger.info(
                    "Background task: Cleaned summary query was empty, skipping PDF search."
                )

        if web_searcher_instance and generated_summary_for_search.strip():
            logger.info(
                f"Background task: Searching web with query: \
                    {generated_summary_for_search[:50]}..."
            )
            web_search_results = web_searcher_instance.search(generated_summary_for_search)
            web_search_results_length = len(web_search_results or "")
            logger.info(f"Background task: Web search found {web_search_results_length} items.")
            # You can also put web_search_results into the queue if needed

        if not pdf_searcher_instance:
            logger.warning("Background task: PDFSearcher instance is None, skipping PDF search.")

        if not generated_summary_for_search.strip():
            logger.info("Background task: Summary was empty, skipping PDF search.")

        results_queue.put(
            {
                "summary": summary_text,
                "related_pdf_pages": pdf_pages,
                "web_search_results": web_search_results,
            }
        )
        logger.info("Background task: Results put into queue.")
    except Exception as e:
        logger.error(f"Background task: Error during summary/search: {e}", exc_info=True)
        # Optionally, put an error state into the queue
        results_queue.put(
            {
                "summary": "Error generating summary.",
                "related_pdf_pages": [],
                "web_search_results": "Error Web search",
                "error": str(e),
            }
        )


def main() -> None:
    st.set_page_config(layout="wide")
    config = load_config()

    # セッション状態を初期化する
    if "audio_input" not in st.session_state:
        st.session_state.audio_input = None
    if "speech_to_text" not in st.session_state:
        st.session_state.speech_to_text = None
    if "summarizer" not in st.session_state:
        st.session_state.summarizer = None
    if "pdf_searcher" not in st.session_state:
        st.session_state.pdf_searcher = None
    if "web_searcher" not in st.session_state:
        st.session_state.web_searcher = None
    if "transcription_history" not in st.session_state:
        st.session_state.transcription_history = []
    if "is_recording" not in st.session_state:
        st.session_state.is_recording = False
    if "current_text" not in st.session_state:
        st.session_state.current_text = ""

    if "recording_start_time" not in st.session_state:
        st.session_state.recording_start_time = None
    if "summary" not in st.session_state:
        st.session_state.summary = ""
    if "web_search_results" not in st.session_state:
        st.session_state.web_search_results = ""
    if "related_pdf_pages" not in st.session_state:
        st.session_state.related_pdf_pages = []
    if "selected_pdf_index" not in st.session_state:
        st.session_state.selected_pdf_index = 0
    if "transcription_display_text" not in st.session_state:
        st.session_state.transcription_display_text = ""

    if "custom_search_query" not in st.session_state:
        st.session_state.custom_search_query = ""

    if "task_results_queue" not in st.session_state:
        st.session_state.task_results_queue = queue.Queue()

    # Add language selection to session state
    if "language" not in st.session_state:
        st.session_state.language = "en"  # Default to English

    # Language selector in the upper left
    lang_container = st.container()
    with lang_container:
        # Use columns to control the width of the language selector
        lang_col1, lang_col2 = st.columns([1, 3])
        with lang_col1:
            lang_options = {"English": "en", "日本語": "ja"}
            selected_lang_display = st.selectbox(
                get_text("language", st.session_state.language),
                options=list(lang_options.keys()),
                index=0 if st.session_state.language == "en" else 1,
                key="lang_selector",
            )

        # Update the language in session state
        selected_lang_code = lang_options[selected_lang_display]
        if selected_lang_code != st.session_state.language:
            st.session_state.language = selected_lang_code
            st.rerun()

    # Use the current language for all UI elements
    lang = st.session_state.language

    main_col1, main_col2 = st.columns(2)

    with main_col1:
        # --- 左ペインにタイトルとステータス表示を移動 --- #
        st.title(get_text("title", lang))

        # 録音状態を表示する
        status_area = st.empty()
        if st.session_state.is_recording and st.session_state.recording_start_time is not None:
            # 録音時間を計算して表示を更新
            recording_duration = int(time.time() - st.session_state.recording_start_time)
            minutes = recording_duration // 60
            seconds = recording_duration % 60
            duration_str = f"{minutes:02d}:{seconds:02d}"
            status_area.info(get_text("recording", lang, duration=duration_str))
        else:
            status_area.info(get_text("not_recording", lang))
        # --- 移動ここまで --- #

        # 音声入力デバイスを選択する
        temp_audio = AudioInput()
        available_devices = temp_audio.get_available_devices()
        device_names = [name for _, name in available_devices]
        device_indices = [idx for idx, _ in available_devices]

        if not device_names:
            st.error("No audio devices available")
        else:
            selected_device_name = st.selectbox(
                get_text("select_device", lang),
                options=device_names,
                index=0,
            )

            # --- ボタンエリア --- #
            button_cols = st.columns([1, 1, 2])  # ボタン用に3列確保 (Start, Stop, Refresh)

            # Start ボタン (1列目)
            with button_cols[0]:
                start_button = st.button(
                    get_text("start_recording", lang),
                    disabled=st.session_state.is_recording,
                    use_container_width=True,
                )
                if start_button:
                    st.session_state.is_recording = True
                    st.session_state.recording_start_time = time.time()
                    # 既存のspeech_to_textとaudio_inputをクリア
                    if st.session_state.speech_to_text is not None:
                        st.session_state.speech_to_text = None
                    if st.session_state.audio_input is not None:
                        st.session_state.audio_input.stop()
                        st.session_state.audio_input = None

                    # transcription_historyとcurrent_textとsummaryをクリア
                    st.session_state.transcription_history = []
                    st.session_state.current_text = ""
                    st.session_state.summary = ""

                    st.session_state.transcription_display_text = ""

                    if selected_device_name is None:
                        raise ValueError("No audio device selected")
                    device_index = device_indices[device_names.index(selected_device_name)]
                    st.session_state.audio_input = AudioInput(device_index=device_index)
                    st.session_state.audio_input.start()

                    speech_key = os.getenv("AZURE_SPEECH_KEY")
                    service_region = os.getenv("AZURE_SPEECH_REGION")

                    if not speech_key or not service_region:
                        raise ValueError(
                            "Azure Speech Service credentials not found "
                            "in environment variables"
                        )

                    # Set Azure Speech Service language based on the selected UI language
                    speech_language = "en-US" if lang == "en" else "ja-JP"

                    azure_service = AzureSpeechService(
                        speech_key=speech_key, service_region=service_region
                    )
                    # Set the speech recognition language
                    azure_service.speech_config.speech_recognition_language = speech_language

                    st.session_state.speech_to_text = SpeechToText(azure_service)
                    st.session_state.summarizer = Summarizer(
                        interval_seconds=config["summarization"]["interval_seconds"],
                        max_length=config["summarization"]["max_length"],
                        language=lang,
                    )

                    logger.info(
                        f"Initializing PDFSearcher with directories: "
                        f"{config['search']['directories']} (recreate=False)"
                    )
                    docs_dir = config["search"]["directories"][0]
                    st.session_state.pdf_searcher = PDFSearcher(
                        docs_dir,
                        recreate_knowledge_base=False,
                    )

                    # Initialize web searcher if needed
                    st.session_state.web_searcher = WebSearcher(language=lang)

                    st.rerun()

            # Stop ボタン (2列目)
            with button_cols[1]:
                stop_button = st.button(
                    get_text("stop_recording", lang),
                    disabled=not st.session_state.is_recording,
                    use_container_width=True,
                )
                if stop_button:
                    st.session_state.is_recording = False
                    st.session_state.recording_start_time = None
                    if st.session_state.audio_input is not None:
                        st.session_state.audio_input.stop()

                    st.rerun()

            # Refresh PDF Index ボタン (3列目)
            with button_cols[2]:
                if st.button(
                    get_text("refresh_pdf", lang), key="refresh_pdfs", use_container_width=True
                ):
                    logger.info(
                        "Refresh PDF Index button clicked. " "Recreating knowledge base..."
                    )

                    docs_dir = config["search"]["directories"][0]
                    # recreate=Trueで再初期化
                    st.session_state.pdf_searcher = PDFSearcher(
                        docs_dir,
                        recreate_knowledge_base=True,
                    )
                    st.success(get_text("pdf_refreshed", lang))

            # --- ボタンエリアここまで --- #

        # 文字起こしエリアを配置する
        st.subheader(get_text("transcription", lang))

        # トランスクリプションを準備
        # Always rebuild transcription_text from history and current_text for rendering
        all_texts_for_render = list(
            st.session_state.transcription_history
        )  # Start with a copy of history
        if st.session_state.current_text:  # Add current (intermediate) text if any
            all_texts_for_render.append(st.session_state.current_text)
        transcription_text_to_display = "\n".join(all_texts_for_render)
        # The st.session_state.transcription_display_text is still updated by the recording loop,
        # but here we use a freshly built version for the text_area value.

        # テキストエリアでトランスクリプションを表示（選択可能）
        # st.text_area(  # COMMENTED OUT
        #     get_text("transcription_label", lang),
        #     value=transcription_text_to_display,
        #     key="transcription_viewer",
        #     disabled=False,
        #     on_change=None,
        #     label_visibility="visible",
        #     placeholder=get_text("transcription_placeholder", lang),
        #     help=get_text("transcription_help", lang),
        # )
        # Replace with st.markdown
        st.markdown(transcription_text_to_display, help=get_text("transcription_help", lang))

    with main_col2:
        # --- Add Custom Search UI Here ---
        st.subheader(get_text("search_input", lang))  # Or a more general subheader if preferred
        custom_search_cols = st.columns([3, 1])
        with custom_search_cols[0]:
            st.session_state.custom_search_query = st.text_input(
                label=get_text("search_input", lang),  # Using label parameter for clarity
                value=st.session_state.custom_search_query,
                key="custom_search_input_main_col2",  # Ensure unique key if old one might persist
                label_visibility="collapsed",  # Collapse label if subheader is used
            )
        with custom_search_cols[1]:
            search_button_main_col2 = st.button(
                get_text("search_button", lang),
                key="search_button_main_col2",
                use_container_width=True,
            )
            if search_button_main_col2 and st.session_state.custom_search_query:
                if st.session_state.pdf_searcher is not None:
                    search_query_col2 = st.session_state.custom_search_query
                    cleaned_query_col2 = re.sub(
                        r"^[-\s\*\n]+",
                        "",
                        search_query_col2,
                        flags=re.MULTILINE,
                    )
                    cleaned_query_col2 = cleaned_query_col2.replace("\n", " ").strip()
                    if cleaned_query_col2:
                        logger.info(
                            f"Custom query (main_col2) '{cleaned_query_col2}' "
                            "searching PDF knowledge base..."
                        )
                        related_pdf_pages_col2 = st.session_state.pdf_searcher.search(
                            cleaned_query_col2,
                            top_k=5,
                        )
                        st.session_state.related_pdf_pages = (
                            related_pdf_pages_col2  # Update main state
                        )
                        st.session_state.selected_pdf_index = 0
                        logger.info(
                            f"PDF search results (main_col2): {len(related_pdf_pages_col2)} items"
                        )
                        st.rerun()
        # --- End of Custom Search UI ---

        # --- Add Summary Section Here ---
        st.subheader(get_text("summary", lang))
        summary_area = (
            st.empty()
        )  # Use st.empty() if you plan to update it frequently, otherwise st.markdown directly
        if st.session_state.summary:
            # Display as markdown, consider if ``` backticks are needed based on summary content
            summary_area.markdown(st.session_state.summary)
        # --- End of Summary Section ---

        # Web検索エイラを配置する
        st.subheader(get_text("web_search", lang))
        # TODO: Implement Web search functionality
        web_search_area = (
            st.empty()
        )  # Use st.empty() if you plan to update it frequently, otherwise st.markdown directly
        if st.session_state.web_search_results:
            # Web検索クエリを入力する
            web_search_area.markdown(st.session_state.web_search_results)
        # --- End of Web Search UI ---

        # 関連情報エリアを配置する
        st.subheader(get_text("related_info", lang))
        related_info_area = st.container()

        # スライドまたはPDFがある場合に表示 -> PDFがある場合のみ表示に変更
        has_pdfs = len(st.session_state.related_pdf_pages) > 0

        if has_pdfs:
            with related_info_area:
                st.info(
                    get_text(
                        "related_pdf_found", lang, count=len(st.session_state.related_pdf_pages)
                    )
                )
                selected_pdf = st.session_state.related_pdf_pages[
                    st.session_state.selected_pdf_index
                ]
                file_path = selected_pdf.get("file_path")
                doc_name = selected_pdf.get("doc_name", "N/A")
                display_name = os.path.basename(file_path) if file_path else doc_name
                st.markdown(f"**{get_text('filename', lang)}**: {display_name}")
                st.markdown(
                    f"**{get_text('page_number', lang)}**: {selected_pdf.get('page', 'N/A')}"
                )

                page_number = selected_pdf.get("page")

                page_index = int(page_number) - 1
                # Add null check for pdf_searcher
                if st.session_state.pdf_searcher is not None:
                    pdf_image = st.session_state.pdf_searcher.get_page_image(file_path, page_index)
                    if pdf_image:
                        st.image(
                            pdf_image,
                            caption=f"Page {selected_pdf.get('page', 'N/A')}",
                        )
                    else:
                        st.error(get_text("pdf_error", lang))
                else:
                    st.error(get_text("pdf_error", lang))

                # PDFナビゲーションボタン
                col1_pdf, col2_pdf = st.columns(2)
                with col1_pdf:
                    prev_pdf_disabled = st.session_state.selected_pdf_index <= 0

                    if st.button(
                        get_text("prev_pdf", lang),
                        key="prev_pdf_standalone",
                        disabled=prev_pdf_disabled,  # キーを調整
                    ):
                        st.session_state.selected_pdf_index -= 1

                        st.rerun()
                with col2_pdf:
                    num_related_pdfs = len(st.session_state.related_pdf_pages)
                    next_pdf_disabled = st.session_state.selected_pdf_index >= num_related_pdfs - 1
                    if st.button(
                        get_text("next_pdf", lang),
                        key="next_pdf_standalone",
                        disabled=next_pdf_disabled,  # キーを調整
                    ):
                        st.session_state.selected_pdf_index += 1

                        st.rerun()
        else:
            related_info_area.info(get_text("no_related_info", lang))

    # 音声認識を処理する
    if (
        st.session_state.is_recording
        and st.session_state.speech_to_text is not None
        and st.session_state.audio_input is not None
        and st.session_state.recording_start_time is not None
    ):
        while st.session_state.is_recording:
            # Check for results from background tasks first
            try:
                task_results = st.session_state.task_results_queue.get_nowait()
                if task_results:
                    logger.info(f"Background task results received: {task_results.keys()}")
                    st.session_state.summary = task_results.get(
                        "summary", st.session_state.summary
                    )  # Keep old if new is missing
                    st.session_state.related_pdf_pages = task_results.get(
                        "related_pdf_pages", st.session_state.related_pdf_pages
                    )
                    st.session_state.selected_pdf_index = 0

                    st.session_state.web_search_results = task_results.get(
                        "web_search_results", st.session_state.web_search_results
                    )

                    if "error" in task_results:
                        logger.error(f"Error from background task: {task_results['error']}")
                        # Optionally, display a user-facing error message
                        # st.error(f"Error processing transcription: {task_results['error']}")
                    st.rerun()  # Rerun to display new summary/PDFs
            except queue.Empty:
                pass  # No new results, continue

            # 録音時間を計算して表示を更新
            recording_duration = int(time.time() - st.session_state.recording_start_time)
            minutes = recording_duration // 60
            seconds = recording_duration % 60
            duration_str = f"{minutes:02d}:{seconds:02d}"
            status_area.info(get_text("recording", lang, duration=duration_str))

            # 音声データを取得する
            audio_data = next(st.session_state.audio_input.get_audio_data(), None)
            if audio_data is not None:
                # 音声データを処理する
                result = st.session_state.speech_to_text.process_audio(audio_data)
                if result.text:
                    # 最終結果の場合、transcription_historyを更新する
                    if result.is_final:
                        st.session_state.transcription_history.append(result.text)
                        st.session_state.current_text = ""

                        # 全てのテキストをStreamlitに表示する
                        all_texts = st.session_state.transcription_history
                        transcription_text = "\n".join(all_texts)
                        st.session_state["transcription_display_text"] = transcription_text

                        # 表示を更新（リアルタイム更新）
                        logger.info(f"Display text: {all_texts}")

                        # --- Start: Modified section for background processing ---
                        # Prepare data for background task
                        current_full_transcription_for_tasks = "\n".join(all_texts)
                        summarizer_config_for_task = config["summarization"]
                        pdf_searcher_for_task = st.session_state.pdf_searcher
                        web_searcher_for_task = st.session_state.web_searcher
                        results_queue_for_task = st.session_state.task_results_queue
                        current_lang_for_task = st.session_state.language

                        # Run summary and PDF search in a background thread
                        thread = threading.Thread(
                            target=process_summary_and_search_async,
                            args=(
                                current_full_transcription_for_tasks,
                                current_lang_for_task,
                                summarizer_config_for_task,
                                pdf_searcher_for_task,
                                web_searcher_for_task,
                                results_queue_for_task,
                            ),
                        )
                        thread.daemon = (
                            True  # Allows main program to exit even if thread is running
                        )
                        thread.start()
                        logger.info("Background thread for summary and PDF search started.")

                        # UI Update for transcription happens after starting the thread
                        st.rerun()
                        # --- End: Modified section for background processing ---

                    else:
                        # 中間結果の場合はcurrent_textのみを更新
                        st.session_state.current_text = result.text

                        # 全てのテキストをStreamlitに表示する
                        all_texts = st.session_state.transcription_history
                        if st.session_state.current_text:
                            all_texts = all_texts + [st.session_state.current_text]

                        # 現在のトランスクリプションをセッション状態に保存
                        transcription_text = "\n".join(all_texts)
                        st.session_state["transcription_display_text"] = transcription_text

                        st.rerun()

            # StreamlitのUIを更新するために少し待機する
            time.sleep(0.01)


if __name__ == "__main__":
    main()
