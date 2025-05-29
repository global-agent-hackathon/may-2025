import datetime

# logging をインポート
import logging
from textwrap import dedent
from typing import Optional

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.exa import ExaTools
from dotenv import load_dotenv  # dotenvをインポート

# .env ファイルを読み込む
load_dotenv()

logger = logging.getLogger(__name__)

# 初期プロンプトを言語別に定義する。Constantとして定義する。
DESCRIPTION = {
    "ja": dedent("""
        あなたはトピック分析と検索に優れた調査員です。
        要約や短文から主要な検索キーワードを抽出し、それぞれについて意味・根拠を調査できます。
    """),
    "en": dedent("""
        You are an excellent researcher skilled in topic analysis and search.
        You can extract key search terms from summaries and short texts,
        and investigate their meanings and justifications.
    """),
}

INSTRUCTIONS = {
    "ja": dedent("""
        1. 入力文を読んで、3〜5個の主要な検索キーワードを抽出してください。
        2. 各キーワードに対して Exa を使ってWeb検索を行ってください。
        3. 各キーワードがなぜ重要か、何を示唆するかを検索結果に基づいて簡潔に説明してください。
    """),
    "en": dedent("""
        1. Read the input text and extract 3-5 key search terms.
        2. For each keyword, perform a web search using Exa.
        3. Provide a concise explanation of why each keyword is important and what it suggests,
          based on the search results.
    """),
}

EXPECTED_OUTPUT = {
    "ja": dedent("""
        以下の形式で出力してください：

        #### 抽出キーワードと解説

        - キーワード: xxx
        - 解説: xxx（100文字以内）
        - 出典: タイトル + URL

        - キーワード: yyy
        - 解説: yyy
        - 出典: ...
    """),
    "en": dedent("""
        Please output in the following format:
        #### Extracted Keywords and Explanations
        - Keyword: xxx
        - Explanation: xxx (within 100 characters)
        - Source: Title + URL

        - Keyword: yyy
        - Explanation: yyy
        - Source: ...
    """),
}

QUERY_TEMPLATE = {
    "ja": dedent("""
        あなたは優秀な調査員です。
        以下に関連したキーワードの抽出・検索・要約を行ってください。
        {query}


    """),
    "en": dedent("""
        You are an excellent researcher.
        Please extract, search, and summarize keywords related to the following:
        {query}

    """),
}


class WebSearcher:
    def __init__(self, language: str = "ja", include_domains: list[str] | None = None):
        """Web検索するクラス"""

        model = Gemini(id="gemini-2.5-pro-preview-03-25", temperature=0.25)
        self.research_scholar = Agent(
            model=model,
            tools=[
                ExaTools(
                    # get the last 365 days of information
                    start_published_date=(
                        datetime.datetime.now() - datetime.timedelta(days=365)
                    ).strftime("%Y-%m-%d"),
                    text=True,
                )
            ],
            description=DESCRIPTION[language],
            instructions=INSTRUCTIONS[language],
            expected_output=EXPECTED_OUTPUT[language],
        )
        self.language = language
        self.include_domains = include_domains

    def search(self, query: str) -> Optional[str]:
        """Web検索を実行するメソッド
        Args:
            query: 検索クエリ
            max_results: 最大検索結果数
        Returns:
            検索結果のリスト
        """
        logger.info(f"'{query}' でWeb検索中...")

        query = QUERY_TEMPLATE[self.language].format(query=query)
        result = self.research_scholar.run(query)

        logger.info(f"Web検索結果: {result.content}")

        return result.content
