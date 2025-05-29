from typing import Generator
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from azure.cognitiveservices.speech import (  # type: ignore
    CancellationReason,
)

from src.audio import AzureSpeechService, SpeechResult, SpeechToText


@pytest.fixture
def mock_speech_config() -> Generator[MagicMock, None, None]:
    with patch("azure.cognitiveservices.speech.SpeechConfig") as mock:
        yield mock


@pytest.fixture
def mock_speech_recognizer() -> Generator[MagicMock, None, None]:
    with patch("azure.cognitiveservices.speech.SpeechRecognizer") as mock:
        yield mock


@pytest.fixture
def azure_service(
    mock_speech_config: MagicMock, mock_speech_recognizer: MagicMock
) -> AzureSpeechService:
    """AzureSpeechServiceのインスタンスを作成するフィクスチャ"""
    service = AzureSpeechService("dummy_key", "dummy_region")
    return service


def test_azure_service_init(azure_service: AzureSpeechService) -> None:
    """AzureSpeechServiceの初期化テスト"""
    assert azure_service.speech_key == "dummy_key"
    assert azure_service.service_region == "dummy_region"
    assert azure_service.speech_recognizer is None


def test_azure_service_create_recognizer(
    azure_service: AzureSpeechService, mock_speech_recognizer: MagicMock
) -> None:
    """音声認識器の作成テスト"""
    azure_service.create_recognizer()
    assert azure_service.speech_recognizer is not None


def test_azure_service_start_stop_recognition(
    azure_service: AzureSpeechService,
) -> None:
    """音声認識の開始と停止のテスト"""
    # 開始のテスト
    azure_service.start_recognition()
    assert azure_service.speech_recognizer is not None

    # 停止のテスト
    azure_service.stop_recognition()


def test_azure_service_handle_result(azure_service: AzureSpeechService) -> None:
    """認識結果のハンドリングテスト"""
    # モックイベントの作成
    mock_event = MagicMock()
    mock_event.result.text = "テストテキスト"

    azure_service._handle_result(mock_event)
    assert azure_service.get_result() == "テストテキスト"


def test_azure_service_handle_recognizing(azure_service: AzureSpeechService) -> None:
    """中間認識結果のハンドリングテスト"""
    # モックイベントの作成
    mock_event = MagicMock()
    mock_event.result.text = "中間テキスト"

    azure_service._handle_recognizing(mock_event)
    assert azure_service.get_intermediate_result() == "中間テキスト"


def test_azure_service_handle_canceled(azure_service: AzureSpeechService) -> None:
    """キャンセルイベントのハンドリングテスト"""
    # モックイベントの作成
    mock_event = MagicMock()
    mock_event.reason = CancellationReason.Error
    mock_event.error_details = "エラー詳細"
    mock_event.error_code = 1

    # エラーケースのテスト
    azure_service._handle_canceled(mock_event)

    # EndOfStreamケースのテスト
    mock_event.reason = CancellationReason.EndOfStream
    azure_service._handle_canceled(mock_event)


def test_speech_to_text_init() -> None:
    """SpeechToTextの初期化テスト"""
    mock_service = MagicMock()
    # 変数を使用するため、アサーションの前に保持
    SpeechToText(mock_service)
    mock_service.start_recognition.assert_called_once()


def test_speech_to_text_process_audio() -> None:
    """音声処理テスト"""
    mock_service = MagicMock()
    mock_service.get_intermediate_result.return_value = "中間テキスト"
    mock_service.get_result.return_value = "最終テキスト"

    stt = SpeechToText(mock_service)

    # テスト用の音声データ
    audio_data = np.zeros(1024, dtype=np.float32)

    # 中間結果のテスト
    result = stt.process_audio(audio_data)
    assert isinstance(result, SpeechResult)
    assert result.text == "中間テキスト"
    assert result.is_final is False

    # 最終結果のテスト
    mock_service.get_intermediate_result.return_value = ""
    result = stt.process_audio(audio_data)
    assert result.text == "最終テキスト"
    assert result.is_final is True


def test_speech_to_text_cleanup() -> None:
    """クリーンアップのテスト"""
    mock_service = MagicMock()
    stt = SpeechToText(mock_service)
    del stt
    mock_service.stop_recognition.assert_called_once()
