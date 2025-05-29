from typing import Dict, Generator
from unittest.mock import MagicMock, patch

import numpy as np
import pyaudio
import pytest

from src.audio import AudioInput


@pytest.fixture
def mock_pyaudio() -> Generator[MagicMock, None, None]:
    with patch("pyaudio.PyAudio") as mock:
        # デバイス情報のモックを設定
        mock_device_info = {
            "name": "Test Device",
            "defaultSampleRate": 48000,
            "maxInputChannels": 2,
            "index": 0,
        }
        mock.return_value.get_device_info_by_index.return_value = mock_device_info
        mock.return_value.get_default_input_device_info.return_value = mock_device_info
        mock.return_value.get_device_count.return_value = 1

        # ストリームのモックを設定
        mock_stream = MagicMock()
        mock_stream.is_active.return_value = True
        mock.return_value.open.return_value = mock_stream

        yield mock


@pytest.fixture
def audio_input(mock_pyaudio: MagicMock) -> AudioInput:
    """AudioInputのインスタンスを作成するフィクスチャ"""
    return AudioInput(sample_rate=48000, chunk_size=1024, channels=1)


def test_init(mock_pyaudio: MagicMock) -> None:
    """初期化のテスト"""
    audio = AudioInput()
    assert audio.sample_rate == 48000
    assert audio.chunk_size == 1024
    assert audio.channels == 1
    assert audio.device_index is None
    assert len(audio.available_devices) == 1


def test_callback_normal(audio_input: AudioInput) -> None:
    """コールバック関数の正常系テスト"""
    # テスト用の音声データを作成
    test_data = np.zeros(1024, dtype=np.float32).tobytes()
    frame_count = 1024
    time_info: Dict[str, float] = {}
    status = 0

    # コールバック関数を呼び出し
    result = audio_input._callback(test_data, frame_count, time_info, status)
    assert result[1] == pyaudio.paContinue
    assert audio_input.audio_queue.qsize() == 1  # データがキューに追加されたことを確認


def test_callback_error(audio_input: AudioInput) -> None:
    """コールバック関数のエラー系テスト"""
    # テスト用の音声データを作成（エラー状態をシミュレート）
    test_data = np.zeros(512, dtype=np.float32).tobytes()  # 異なるサイズのデータ
    frame_count = 1024  # 期待されるサイズと異なる
    time_info: Dict[str, float] = {}
    status = 1  # エラー状態

    # コールバック関数を呼び出し
    result = audio_input._callback(test_data, frame_count, time_info, status)
    assert result[1] == pyaudio.paContinue
    assert audio_input.audio_queue.qsize() == 0  # エラー時はデータが追加されないことを確認


def test_get_audio_data(audio_input: AudioInput) -> None:
    """オーディオデータの取得テスト"""
    # テスト用のデータをキューに追加
    test_data = np.zeros(1024, dtype=np.float32).tobytes()
    audio_input.audio_queue.put(test_data)
    audio_input.is_running = True

    # ジェネレータから最初のデータを取得
    generator = audio_input.get_audio_data()
    data = next(generator)

    assert isinstance(data, np.ndarray)
    assert len(data) == 1024


def test_get_available_devices(audio_input: AudioInput) -> None:
    """利用可能なデバイスの取得テスト"""
    devices = audio_input.get_available_devices()
    assert len(devices) == 1
    device_index, device_name = devices[0]
    assert device_index == 0
    assert device_name == "Test Device"


def test_error_handling(mock_pyaudio: MagicMock) -> None:
    """エラーハンドリングのテスト"""
    # PyAudioの初期化でエラーを発生させる
    mock_pyaudio.return_value.get_device_count.side_effect = Exception("Test error")

    with pytest.raises(Exception) as exc_info:
        AudioInput()
    assert str(exc_info.value) == "Test error"
