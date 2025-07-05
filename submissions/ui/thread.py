from PyQt6.QtCore import QThread, pyqtSignal
import sys
import os
sys.path.append(os.path.dirname(__file__))
from src.speech.speech_to_text import STT
from src.speech.text_to_speech import TTS
from src.agent import Agent

class STTThread(QThread):
    stt_finished = pyqtSignal(str)
    def __init__(self, stt:STT=None):
        super().__init__()
        self.stt = stt

    def run(self):
        response = self.stt.process_audio()
        self.stt_finished.emit(response.text)

class TTSThread(QThread):
    tts_finished = pyqtSignal(str)
    def __init__(self, tts:TTS=None, text:str=''):
        super().__init__()
        self.tts = tts
        self.text=text

    def run(self):
        self.tts.invoke(self.text)
        self.tts_finished.emit("Operation Finished")

class PDFThread(QThread):
    pdf_finished = pyqtSignal(str)
    def __init__(self, agent:Agent, file_path:str=None):
        super().__init__()
        self.agent = agent
        self.file_path=file_path

    def run(self):
        self.agent.add_pdf_knowledge(self.file_path)
        filename=os.path.basename(self.file_path)
        msg=f'{filename} loaded to Knowledge Base.'
        self.pdf_finished.emit(msg)

class URLThread(QThread):
    url_finished = pyqtSignal(str)
    def __init__(self, agent:Agent, url:str=None):
        super().__init__()
        self.agent = agent
        self.url=url

    def run(self):
        self.agent.add_url_knowledge(self.url)
        msg=f'{self.url} content loaded to Knowledge Base.'
        self.url_finished.emit(msg)

class AgentThread(QThread):
    agent_finished = pyqtSignal(str)
    def __init__(self, agent:Agent=None,query:str=''):
        super().__init__()
        self.agent = agent
        self.query=query

    def run(self):
        response=self.agent.invoke(self.query)
        content=response.get_content_as_string()
        self.agent_finished.emit(content.strip())