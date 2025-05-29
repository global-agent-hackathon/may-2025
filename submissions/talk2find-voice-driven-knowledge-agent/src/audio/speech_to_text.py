import logging
import queue
from dataclasses import dataclass
from typing import Any, Optional, Protocol, cast

import azure.cognitiveservices.speech as speechsdk  # type: ignore
import numpy as np
from dotenv import load_dotenv

# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 環境変数を読み込む
load_dotenv()


@dataclass
class SpeechResult:
    text: str
    is_final: bool


class SpeechToTextService(Protocol):
    def start_recognition(self) -> None:
        """音声認識を開始する"""
        pass

    def stop_recognition(self) -> None:
        """音声認識を停止する"""
        pass

    def get_result(self) -> str:
        """最終結果を取得する"""
        pass

    def get_intermediate_result(self) -> str:
        """中間結果を取得する"""
        pass


class AzureSpeechService:
    def __init__(self, speech_key: str, service_region: str) -> None:
        logger.debug(f"Initializing AzureSpeechService with region: {service_region}")
        logger.debug(f"Speech_key: {speech_key[:4]}...{speech_key[-4:]}")

        self.speech_key = speech_key
        self.service_region = service_region
        self.speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

        # 日本語認識を有効にする
        self.speech_config.speech_recognition_language = "ja-JP"

        # キューを初期化する
        self.result_queue: queue.Queue[str] = queue.Queue()
        self.intermediate_result_queue: queue.Queue[str] = queue.Queue()
        self.audio_queue: queue.Queue[np.ndarray[Any, np.dtype[np.float32]]] = queue.Queue()
        self.audio_stream = None
        self.push_stream = None
        self.speech_recognizer: Optional[speechsdk.SpeechRecognizer] = None

        # 音声認識の設定を調整する
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs, "5000"
        )
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs, "1000"
        )
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EnableAudioLogging, "true"
        )

    def create_recognizer(self) -> None:
        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        self.speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=self.speech_config, audio_config=audio_config
        )

    def start_recognition(self) -> None:
        """音声認識を開始する"""
        logger.debug("Starting recognition")
        try:
            self.create_recognizer()
            recognizer = self.speech_recognizer
            if recognizer is not None:
                recognizer.recognized.connect(self._handle_result)
                recognizer.recognizing.connect(self._handle_recognizing)
                recognizer.canceled.connect(self._handle_canceled)
                recognizer.session_started.connect(
                    lambda evt: logger.debug("Speech recognition session started")
                )
                recognizer.session_stopped.connect(
                    lambda evt: logger.debug("Speech recognition session stopped")
                )
                recognizer.start_continuous_recognition()
                logger.debug("Recognition started successfully")
            else:
                logger.error("Failed to create speech recognizer")
        except Exception as e:
            logger.error(f"Failed to start recognition: {str(e)}")
            raise

    def _handle_result(self, evt: Any) -> None:
        if evt.result.text:
            self.result_queue.put(evt.result.text)

    def _handle_recognizing(self, evt: Any) -> None:
        if evt.result.text:
            self.intermediate_result_queue.put(evt.result.text)

    def _handle_canceled(self, evt: Any) -> None:
        if evt.reason == speechsdk.CancellationReason.Error:
            logger.error(f"Error details: {evt.error_details}")
            logger.error(f"Error code: {evt.error_code}")
        elif evt.reason == speechsdk.CancellationReason.EndOfStream:
            logger.debug("End of stream reached")
        else:
            logger.warning(f"Recognition canceled: {evt.reason}")

    def start_continuous_recognition(self) -> None:
        self.create_recognizer()
        recognizer = self.speech_recognizer
        if recognizer is not None:
            recognizer.start_continuous_recognition()
        else:
            logger.error("Failed to create speech recognizer")

    def stop_continuous_recognition(self) -> None:
        if self.speech_recognizer is not None:
            self.speech_recognizer.stop_continuous_recognition()

    def recognize_once(self, audio_data: np.ndarray[Any, np.dtype[np.float32]]) -> Optional[str]:
        try:
            if self.speech_recognizer is None:
                self.create_recognizer()
                if self.speech_recognizer is None:
                    return None

            result = self.speech_recognizer.recognize_once(audio_data)
            if result.text:
                return cast(str, result.text)
            return None
        except Exception as e:
            logger.error(f"Error in recognize_once: {e}")
            return None

    def stop_recognition(self) -> None:
        """音声認識を停止する"""
        logger.debug("Stopping recognition")
        try:
            if self.speech_recognizer is not None:
                self.speech_recognizer.stop_continuous_recognition()
                logger.debug("Recognition stopped successfully")
            else:
                logger.warning("Speech recognizer is not initialized")
        except Exception as e:
            logger.error(f"Failed to stop recognition: {str(e)}")
            raise

    def get_result(self) -> str:
        """認識結果を取得する"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return ""
        except Exception as e:
            logger.error(f"Error getting result: {str(e)}")
            return ""

    def get_intermediate_result(self) -> str:
        """中間認識結果を取得する"""
        try:
            # キューから中間結果を取得する（待機しない）
            result = self.intermediate_result_queue.get_nowait()
            return result
        except queue.Empty:
            return ""


class SpeechToText:
    def __init__(self, speech_service: SpeechToTextService) -> None:
        logger.debug("Initializing SpeechToText")
        self.speech_service = speech_service
        self.speech_service.start_recognition()

    def __del__(self) -> None:
        self.speech_service.stop_recognition()

    def process_audio(self, audio_data: np.ndarray[Any, np.dtype[np.float32]]) -> SpeechResult:
        """音声データを処理して認識結果を返す"""
        try:
            # 中間結果を取得する
            intermediate_text = self.speech_service.get_intermediate_result()
            if intermediate_text:
                return SpeechResult(text=intermediate_text, is_final=False)

            # 最終結果を取得する
            final_text = self.speech_service.get_result()
            if final_text:
                return SpeechResult(text=final_text, is_final=True)

            return SpeechResult(text="", is_final=False)

        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return SpeechResult(text="", is_final=False)
