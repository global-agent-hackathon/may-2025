# logging をインポート
import logging
import os
import shutil  # shutil をインポート
import tempfile
from typing import Any, Dict, List, Optional

import pdf2image
import pypandoc  # type: ignore
from agno.embedder.google import GeminiEmbedder  # Gemini Embedder を追加
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from dotenv import load_dotenv  # dotenvをインポート
from PIL import Image

# .env ファイルを読み込む
load_dotenv()

logger = logging.getLogger(__name__)


class PDFSearcher:
    def __init__(self, search_directory: str, recreate_knowledge_base: bool = False):
        """PDFファイルを検索するクラス (DOCXも一時PDFに変換して対応)

        Args:
            search_directory: 検索対象のディレクトリ (PDFおよびDOCXファイルを含む)
            recreate_knowledge_base: Trueの場合、既存のナレッジベースを削除して再構築する
        """

        self.search_directory = os.path.abspath(search_directory)  # search_directory を正規化
        self.recreate_knowledge_base = recreate_knowledge_base
        self.temporary_pdf_files: List[str] = []  # 一時PDFファイルリストを初期化
        self.source_mapping: Dict[str, Dict[str, Any]] = {}  # 一時PDFと元のDOCX情報をマッピング

        if not os.path.isdir(self.search_directory):
            raise ValueError(
                f"指定された検索ディレクトリが見つかりません: {self.search_directory}"
            )

        self.knowledge_base = self._initialize_knowledge_base(
            recreate=self.recreate_knowledge_base
        )

    def _initialize_knowledge_base(self, recreate: bool) -> Optional[PDFKnowledgeBase]:
        """agno の Knowledge Base を初期化し、データをロードする
        指定されたディレクトリ内のPDFとDOCX(一時PDFに変換)を対象とする。
        """
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.error("環境変数 GOOGLE_API_KEY が設定されていません。")
            # Error時はmainなど呼び出し元で処理することも考慮する
            raise ValueError("環境変数 GOOGLE_API_KEY が設定されていません。")

        # 古い一時ディレクトリが残っていれば削除
        for item in os.listdir(self.search_directory):
            item_path = os.path.join(self.search_directory, item)
            if os.path.isdir(item_path) and item.startswith("_temp_docx_conv_"):
                try:
                    shutil.rmtree(item_path)
                    logger.info(f"古い一時ディレクトリを削除しました: {item_path}")
                except Exception as e:
                    logger.error(f"古い一時ディレクトリの削除に失敗 ({item_path}): {e}")

        vector_db = LanceDb(
            uri="tmp/lancedb_pdf_and_docx",
            table_name="docs_gemini_hybrid",
            search_type=SearchType.hybrid,
            embedder=GeminiEmbedder(api_key=google_api_key),
        )

        # 検索対象ディレクトリ内のファイルを探索
        all_files_to_load: List[str] = []  # 実際にKnowledgeBaseにロードするPDFパスのリスト
        self.temporary_pdf_files = []  # 初期化
        self.source_mapping = {}  # 初期化
        self.temp_docx_pdf_subdir: str | None = None

        # 一時ディレクトリを作成して、その中にDOCXから変換したPDFを保存する
        # PDFSearcherのインスタンスが生きている間だけ存在するようにする
        # `PDFSearcher`の終了時に、その一時サブディレクトリを削除する。
        self.temp_docx_pdf_subdir = tempfile.mkdtemp(
            dir=self.search_directory, prefix="_temp_docx_conv_"
        )
        logger.info(f"DOCX変換用の一時サブディレクトリを作成: {self.temp_docx_pdf_subdir}")

        # PDFKnowledgeBaseは一つのディレクトリしか見ないので、元のディレクトリを指定するしかない。

        for root, _, files in os.walk(self.search_directory):
            if (
                self.temp_docx_pdf_subdir in root
            ):  # 一時サブディレクトリ自体はスキャン対象外（無限ループ防止）
                continue
            for file in files:
                original_file_path = os.path.join(root, file)
                if file.lower().endswith(".pdf"):
                    # PDFファイルはそのまま。source_mappingに登録。
                    stem_filename = os.path.splitext(os.path.basename(file))[0]
                    self.source_mapping[stem_filename] = {
                        "original_path": original_file_path,
                        "original_type": "pdf",
                        "is_temporary": False,
                        "display_path": original_file_path,  # 表示用のパス
                        "kb_source_path": original_file_path,  # KBが認識するパス
                    }
                elif file.lower().endswith(".docx"):
                    try:
                        # DOCXを一時サブディレクトリ内のPDFに変換
                        # ファイル名は元のファイル名にサフィックスをつけるなどして一意性を保つ
                        relative_docx_path = os.path.relpath(
                            original_file_path, self.search_directory
                        )
                        safe_pdf_filename = relative_docx_path.replace(os.sep, "-").replace(
                            ".docx", ".pdf"
                        )
                        temp_pdf_path = os.path.join(self.temp_docx_pdf_subdir, safe_pdf_filename)

                        os.makedirs(
                            os.path.dirname(temp_pdf_path), exist_ok=True
                        )  # サブディレクトリ構造を維持

                        logger.info(
                            f"DOCXを一時PDFに変換中: {original_file_path} -> {temp_pdf_path}"
                        )

                        try:
                            # Determine the absolute path to the latex_header_for_lists.tex file
                            current_script_dir = os.path.dirname(os.path.abspath(__file__))
                            header_file_path = os.path.join(
                                current_script_dir, "latex_header_for_lists.tex"
                            )

                            pypandoc.convert_file(
                                original_file_path,
                                "pdf",
                                outputfile=temp_pdf_path,
                                extra_args=[
                                    "--pdf-engine=xelatex",
                                    "-V",
                                    "mainfont=Times New Roman",  # 英語フォント
                                    "-V",
                                    "CJKmainfont=Hiragino Sans",  # 日本語フォント
                                    f"--include-in-header={header_file_path}",
                                ],
                            )
                            logger.info(
                                f"DOCXから一時PDFへの変換成功 (via pypandoc): {temp_pdf_path}"
                            )
                        except RuntimeError as e_runtime_pandoc:
                            # pypandoc.exceptions.PandocNotFoundErrorが
                            # RuntimeError のサブクラスの場合があるためRuntimeErrorをキャッチ
                            logger.error(
                                f"pypandoc実行時エラー ({original_file_path}):"
                                + f"{e_runtime_pandoc}."
                                + "pandocがインストールされ、PATHが通っているか確認してください。"
                            )
                            continue
                        except Exception as e_pandoc:
                            logger.error(
                                "pypandocでのDOCXからPDFへの変換に失敗"
                                + f"({original_file_path}): {e_pandoc}"
                            )
                            continue  # 次のファイルの処理へ

                        all_files_to_load.append(temp_pdf_path)
                        self.temporary_pdf_files.append(temp_pdf_path)
                        stem_filename = os.path.splitext(os.path.basename(safe_pdf_filename))[0]
                        self.source_mapping[stem_filename] = {
                            "original_path": original_file_path,  # 元のDOCXパス
                            "original_type": "docx",
                            "is_temporary": True,
                            "display_path": temp_pdf_path,  # ユーザー変更: 表示は変換後のPDFパス
                            "kb_source_path": temp_pdf_path,  # KBが認識するパス
                            "is_temporary_source": True,  # この結果が一時ファイル由来か
                        }
                    except Exception as e:
                        logger.error(f"DOCXから一時PDFへの変換に失敗 ({original_file_path}): {e}")

        knowledge_base = PDFKnowledgeBase(
            path=self.search_directory,  # 正規化されたsearch_directory を使用
            vector_db=vector_db,
        )
        logger.info(
            f"Agno Knowledge Base (Gemini Embedder, PDF+一時DOCX) のインスタンス作成完了 "
            f"({self.search_directory})"
        )

        try:
            knowledge_base.load(
                recreate=recreate
            )  # ここで search_directory 内のPDFがロードされる（一時PDF含む）
        except Exception as e:
            logger.error(f"ナレッジベースのロード中にエラーが発生しました: {e}")
            self.cleanup_temporary_files()  # エラー時は一時ファイルをクリーンアップ
            raise  # エラーを再送出

        return knowledge_base

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        logger.info(f"'{query}' でナレッジベースを検索中 (取得数={top_k})...")

        if self.knowledge_base is None:
            logger.warning("ナレッジベースが初期化されていません。空の結果を返します。")
            return []

        try:
            search_results = self.knowledge_base.search(query, top_k)
        except Exception as e:
            logger.error(f"ナレッジベース検索中にエラー: {e}")
            return []

        logger.info(f"検索結果 {len(search_results)} 件取得")
        formatted_results = []
        for doc in search_results:
            meta_data = getattr(doc, "meta_data", {})
            page_number = meta_data.get("page", None)
            doc_name = getattr(doc, "name", None)

            raw_source_path = None
            if doc_name:
                source_entry = self.source_mapping.get(doc_name)
                if source_entry:
                    raw_source_path = source_entry.get("kb_source_path")
                    display_path = source_entry.get("display_path", raw_source_path)
                    original_type = source_entry.get("original_type", "unknown")
                    original_path = source_entry.get("original_path", raw_source_path)
                    is_temporary_source = source_entry.get("is_temporary", False)
                else:
                    logger.warning(f"source_mappingにキーが見つかりません (doc_name: {doc_name}")

            formatted_results.append(
                {
                    "text": doc.content or "",
                    "page": page_number,
                    "file_path": display_path,
                    "original_type": original_type,
                    "original_absolute_path": original_path,
                    "doc_name": doc_name,
                    "score": getattr(doc, "score", None),
                    "is_temporary_source": is_temporary_source,
                }
            )
        return formatted_results

    def get_page_image(self, file_path: str, page_index: int) -> Image.Image | None:
        """指定されたファイルの指定ページの画像を取得。
        file_pathがDOCXの場合、一時PDFを経由して画像を取得する。
        """

        if not file_path or not os.path.exists(file_path):
            logger.error(
                "get_page_image: 指定されたPDFファイルが見つかりません:"
                + f"{file_path} (元ファイル: {file_path})"
            )
            return None

        logger.info(
            f"get_page_image: {file_path} の"
            + f"{page_index + 1} ページ目の画像を取得します (元ファイル: {file_path})"
        )
        with tempfile.TemporaryDirectory() as temp_image_dir:
            try:
                images = pdf2image.convert_from_path(
                    file_path,
                    first_page=page_index + 1,
                    last_page=page_index + 1,
                    dpi=150,
                    output_folder=temp_image_dir,
                    fmt="png",
                )
                return images[0] if images else None
            except Exception as e:
                logger.error(f"PDFからの画像変換中にエラー ({file_path}): {e}")
                return None

    def cleanup_temporary_files(self) -> None:
        """DOCXから変換された一時PDFファイルと、それらを格納していた一時サブディレクトリを削除する"""
        logger.info("一時ファイルのクリーンアップを開始します...")
        # 一時ディレクトリ(TemporaryDirectoryオブジェクト)のクリーンアップ

        # search_directory内に作成した一時サブディレクトリを削除
        if (
            hasattr(self, "temp_docx_pdf_subdir")
            and self.temp_docx_pdf_subdir
            and os.path.exists(self.temp_docx_pdf_subdir)
        ):
            try:
                shutil.rmtree(self.temp_docx_pdf_subdir)
                logger.info(f"一時サブディレクトリを削除しました: {self.temp_docx_pdf_subdir}")
            except Exception as e:
                logger.error(
                    f"一時サブディレクトリの削除に失敗 ({self.temp_docx_pdf_subdir}): {e}"
                )
        self.temp_docx_pdf_subdirs = None
        self.temporary_pdf_files = []  # リストもクリア
        self.source_mapping = {}  # マッピングもクリア

    def __del__(self) -> None:
        """PDFSearcherインスタンス破棄時に一時ファイルをクリーンアップ"""
        self.cleanup_temporary_files()
