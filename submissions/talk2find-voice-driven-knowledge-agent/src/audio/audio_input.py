import logging
import queue
import time
from typing import Any, Generator, List, Mapping, Optional, Tuple, cast

import numpy as np
import pyaudio
from pyaudio import Stream

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class AudioInput:
    def __init__(
        self,
        sample_rate: int = 48000,
        chunk_size: int = 1024,
        channels: int = 1,
        device_index: Optional[int] = None,
    ):
        logger.debug(
            f"Initializing AudioInput: sample_rate={sample_rate}, "
            f"chunk_size={chunk_size}, channels={channels}, "
            f"device_index={device_index}"
        )
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.channels = channels
        self.device_index = device_index
        self.audio = pyaudio.PyAudio()
        self.stream: Optional[Stream] = None
        self.buffer_size = 4096  # Increased buffer size
        self.audio_queue: queue.Queue[bytes] = queue.Queue()
        self.is_running = False
        self.available_devices: List[Tuple[int, str]] = []

        # 利用可能なデバイスを表示する
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if int(device_info["maxInputChannels"]) > 0:
                logger.debug(
                    f"Input device {i}: {device_info['name']} "
                    f"(Sample rate: {device_info['defaultSampleRate']})"
                )
                self.available_devices.append((i, str(device_info["name"])))

    def get_available_devices(self) -> List[Tuple[int, str]]:
        return self.available_devices

    def start(self) -> None:
        try:
            logger.debug("Starting audio stream")
            # デバイス情報を取得する
            if self.device_index is not None:
                device_info = self.audio.get_device_info_by_index(self.device_index)
                logger.debug(
                    f"Using selected device: {device_info['name']} "
                    f"(Sample rate: {device_info['defaultSampleRate']})"
                )

                if device_info["defaultSampleRate"] != self.sample_rate:
                    logger.warning(
                        f"Device sample rate ({device_info['defaultSampleRate']}) "
                        f"differs from requested rate ({self.sample_rate})"
                    )
            else:
                device_info = self.audio.get_default_input_device_info()
                logger.debug(
                    f"Using default device: {device_info['name']} "
                    f"(Sample rate: {device_info['defaultSampleRate']})"
                )
                self.device_index = cast(int, device_info["index"])

            # デバイスの設定を確認する
            logger.debug(
                f"Opening stream with: rate={self.sample_rate}, "
                f"channels={self.channels}, chunk_size={self.chunk_size}"
            )

            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=self.device_index,
                stream_callback=self._callback,
            )
            self.is_running = True
            logger.debug("Audio stream started successfully")
        except Exception as e:
            logger.error(f"Error starting audio stream: {e}")
            raise

    def stop(self) -> None:
        if self.stream:
            try:
                logger.debug("Stopping audio stream")
                self.is_running = False
                self.stream.stop_stream()
                self.stream.close()
                logger.debug("Audio stream stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping audio stream: {e}")
        self.audio.terminate()

    def _callback(
        self,
        in_data: bytes | None,
        frame_count: int,
        time_info: Mapping[str, float],
        status: int,
    ) -> Tuple[bytes | None, int]:
        if status:
            logger.warning(f"Audio stream status: {status}")
            return (in_data, pyaudio.paContinue)  # エラー状態の場合はデータを追加しない
        try:
            if in_data is None:
                logger.warning("Received None data in callback")
                return (None, pyaudio.paContinue)

            # 音声データをキューに追加する
            audio_array = np.frombuffer(in_data, dtype=np.float32)
            # 音量を調整する
            audio_array = audio_array * 4.0  # 音量を4倍に増加
            # クリッピングを防ぐ
            audio_array = np.clip(audio_array, -1.0, 1.0)

            self.audio_queue.put(audio_array.tobytes())
            return (in_data, pyaudio.paContinue)
        except Exception as e:
            logger.error(f"Error in audio callback: {e}")
            return (in_data, pyaudio.paAbort)

    def get_audio_data(
        self,
    ) -> Generator[np.ndarray[Any, np.dtype[np.float32]], None, None]:
        while self.is_running:
            try:
                data = self.audio_queue.get(timeout=1.0)  # 1秒のタイムアウト
                audio_array = np.frombuffer(data, dtype=np.float32)

                yield audio_array
            except queue.Empty:
                logger.debug("Audio queue is empty")
                time.sleep(0.1)
                continue
            except Exception as e:
                logger.error(f"Error processing audio data: {e}")
                time.sleep(0.1)
                continue
