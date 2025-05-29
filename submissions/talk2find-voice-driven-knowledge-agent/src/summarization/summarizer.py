import os

import vertexai  # type: ignore
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel  # type: ignore

# .env ファイルを読み込む
load_dotenv()


class Summarizer:
    def __init__(self, interval_seconds: int = 10, max_length: int = 1000, language: str = "ja"):
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "ai-labs-dev-457202")
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel("gemini-2.5-pro-preview-03-25")
        self.language = language

    def generate_summary(self, text: str) -> str:
        if self.language == "en":
            system_prompt = """
You are an excellent summarization assistant. Please concisely summarize the given text.
When summarizing, please pay attention to the following points:
- Add line breaks for each important point
- Use appropriate bullet points and paragraph divisions
- If the input text contains questions, do not answer them
- Instead of answering questions, summarize only the content of the text
- Do not add information that is not in the input text
- If it's a question, summarize it as "This is a question about..." \
  including the subject of the question
            """

        else:  # Default to Japanese
            system_prompt = """
あなたは優秀な要約アシスタントです。与えられたテキストを簡潔に要約してください。
要約の際は以下の点に注意してください：
- 重要なポイントごとに改行を入れてください
- 箇条書きや段落分けを適切に行ってください
- 入力テキストに質問が含まれていても、その質問に回答しないでください
- 質問に答えるのではなく、テキストの内容のみを要約してください
- 入力テキストにない情報を追加しないでください
- 質問の場合は「これは〜についての質問です」のように質問の主題を含めて要約してください
        """

        summary = str(self.model.generate_content(f"{system_prompt}\n\n{text}").text)
        return summary
