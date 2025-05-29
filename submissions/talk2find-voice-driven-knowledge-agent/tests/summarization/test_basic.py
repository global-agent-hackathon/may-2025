import os
from unittest.mock import MagicMock, patch

import pytest

from src.summarization import Summarizer


@pytest.fixture
def summarizer() -> Summarizer:
    """テスト用のSummarizerインスタンスを作成するフィクスチャ"""
    # 環境変数設定
    os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-project"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

    # vertexaiとGenerativeModelをモック化して使用
    with patch("vertexai.init"), patch("vertexai.generative_models.GenerativeModel"):
        summarizer = Summarizer(interval_seconds=1, max_length=100)
        return summarizer


def test_generate_summary(summarizer: Summarizer) -> None:
    """要約生成機能のテスト"""
    # テスト用のテキスト
    texts = "これはテストの文章です。要約が必要な文章です。"
    expected_summary = "- これはテストの文章です。\n- 要約が必要な文章です。"

    # Geminiモデルのレスポンスをモック
    mock_response = MagicMock()
    mock_response.text = expected_summary

    # モデルのgenerate_contentメソッドをモック
    summarizer.model = MagicMock()
    summarizer.model.generate_content.return_value = mock_response

    summary = summarizer.generate_summary(texts)
    assert summary == expected_summary

    # APIが正しく呼び出されたことを確認
    summarizer.model.generate_content.assert_called_once()
