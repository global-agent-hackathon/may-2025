from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QTextEdit, QGraphicsDropShadowEffect, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QIcon, QColor, QCursor, QKeyEvent, QAction
from ui.thread import STTThread,TTSThread,AgentThread,PDFThread,URLThread
from PyQt6.QtWidgets import QMessageBox, QFrame, QMenu, QInputDialog
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtCore import QTimer
from ui.utils import resource_path
import sys
import os
import re
import ctypes
sys.path.append(os.path.dirname(__file__))
from src.speech.speech_to_text import STT
from src.speech.text_to_speech import TTS
from src.agent import Agent

class ChatUI(QWidget):
    def __init__(self,agent:Agent=None,stt:STT=None,tts:TTS=None):
        """Initialize the chat UI."""
        self.agent=agent
        self.stt=stt
        self.tts=tts
        self.is_recording=False
        self.pdf_thread=None
        self.url_thread=None
        self.tts_thread=None
        self.stt_thread=None
        self.agent_thread=None
        super().__init__()

        self.setWindowTitle("Windows-Use")
        self.setFixedSize(500, 80)  # ✅ Set window size slightly larger for shadow effect
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # ✅ Move to top center
        screen = QApplication.primaryScreen().size()
        x = (screen.width() - self.width()) // 2
        y = -8  # Keep close to top
        self.move(x, y)

        # ✅ Create the main container (with rounded borders)
        self.container = QWidget(self)
        self.container.setFixedSize(450, 45)  # ✅ Slightly smaller than window for padding

        # ✅ Apply Drop Shadow to the container
        self.add_shadow()

        # ✅ Layout inside the container
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)  # ✅ No margins
        layout.setSpacing(0)  # ✅ No spacing between widgets

        # ✅ More Button
        self.more_button = QPushButton()
        self.more_button.setFixedSize(40, 45)
        self.more_button.setIcon(QIcon(resource_path("./ui/assets/more.svg")))  # Add your 3-dot SVG icon here
        self.more_button.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        self.more_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.more_button.clicked.connect(self.dropdown_menu)

        # ✅ Vertical Separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.VLine)
        self.separator.setStyleSheet("color: #D7D8D8;")  # Light gray color
        self.separator.setFixedHeight(45)  # Adjust height to align with buttons
        self.separator.setLineWidth(5)

        # ✅ Mic Button
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(40, 45)
        self.mic_button.setIcon(QIcon(resource_path("./ui/assets/mic.svg")))
        self.mic_button.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        self.mic_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.mic_button.clicked.connect(self.on_mic_clicked)

        # ✅ Text Input (No border, No extra padding)
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("How can I help you?")
        self.text_input.setFixedHeight(45)
        self.text_input.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.text_input.setStyleSheet("""
            QTextEdit {
                background-color: #F1F5F9;
                border: none;
                font-size: 16px;
                font-family: 'Segoe UI', sans-serif;
                color: #1E293B;
                padding: 6px;
                margin: 0;
                outline: none;
            }
            QTextEdit:focus {
                outline: none;
            }
        """)
        self.text_input.textChanged.connect(self.on_text_changed)
        # Override keyPressEvent for the existing QTextEdit instance
        self.text_input.keyPressEvent = self.handle_press

        # ✅ Send Button
        self.send_button = QPushButton()
        self.send_button.setFixedSize(40, 45)
        self.send_button.setIcon(QIcon(resource_path("./ui/assets/send.svg")))
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #E2E8F0;
                border: none;
                border-top-right-radius: 5px;
                border-bottom-right-radius: 5px;
            }
            QPushButton:hover {
                background-color: #CBD5E1;
            }
        """)
        self.send_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.send_button.clicked.connect(self.on_send_clicked)

        # ✅ Add widgets inside the container
        layout.addWidget(self.more_button)
        layout.addWidget(self.separator)  # Add vertical separator
        layout.addWidget(self.mic_button)
        layout.addWidget(self.text_input, 1)  # Expand text input
        layout.addWidget(self.send_button)

        # ✅ Center container inside main window
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # ✅ Space for shadow
        main_layout.addWidget(self.container)

    def handle_press(self,event:QKeyEvent):
        if (event.key() == Qt.Key.Key_Return and not event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.on_send_clicked()
        else:
            QTextEdit.keyPressEvent(self.text_input, event)  # Call default behavior for other keys

    def add_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 30))  # Black shadow with opacity
        self.container.setGraphicsEffect(shadow)  # ✅ Apply shadow to container

    def dropdown_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet('''
            QMenu { 
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                background-color: #F8FAFC; 
            }
            QMenu::item {
                padding: 6px 12px;
                background-color: transparent;
            }
            QMenu::item:selected {
                border-radius: 5px;
                background-color: #E2E8F0;
                color: black;
            }
        ''')
        # No shadow, flat appearance
        # menu.setWindowFlags(menu.windowFlags() | Qt.WindowType.FramelessWindowHint)
        # menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # Add PDF action
        pdf_action = QAction("Knowledge PDF", self)
        pdf_action.triggered.connect(self.on_pdf_clicked)
        menu.addAction(pdf_action)

        # Add URL action
        url_action = QAction("Knowledge URL", self)
        url_action.triggered.connect(self.on_url_clicked)
        menu.addAction(url_action)

        # Position the menu right below the dropdown button
        pos = self.more_button.mapToGlobal(QPoint(0, self.more_button.height()))
        menu.exec(pos)

    def on_pdf_clicked(self):
        file_path, _ = QFileDialog.getOpenFileName(self,"Select a PDF File","","PDF Files (*.pdf)")
        if file_path.strip() == '':
            return None
        self.pdf_thread=PDFThread(agent=self.agent,file_path=file_path)
        self.pdf_thread.pdf_finished.connect(self.on_pdf_finished)
        self.pdf_thread.start()

    def on_url_clicked(self):
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add Knowledge URL")
        dialog.setLabelText("Enter the URL:")
        dialog.setTextValue("")  # Optional: default text
        dialog.setInputMode(QInputDialog.InputMode.TextInput)
        dialog.resize(400, dialog.sizeHint().height())

        if dialog.exec():
            url = dialog.textValue().strip()
            if url.strip():
                self.url_thread=URLThread(agent=self.agent,url=url)
                self.url_thread.url_finished.connect(self.on_url_finished)
                self.url_thread.start()

    def on_pdf_finished(self,content:str):
        QMessageBox.information(self,'PDF Knowledge Base',content)

    def on_url_finished(self,content:str):
        QMessageBox.information(self, "URL Knowledge Base", content)

    def on_mic_clicked(self):
        if self.stt is None:
            return None
        if not self.is_recording:
            self.is_recording=True
            self.update_style(self.mic_button,"background-color","#CBD5E1")
            self.stt.start_recording()
            self.text_input.setPlaceholderText('Listening...')
            self.send_button.setDisabled(True)
            self.text_input.setDisabled(True)
        else:
            self.is_recording=False
            self.update_style(self.mic_button,"background-color","#E2E8F0")
            self.stt.stop_recording()
            self.stt_thread=STTThread(stt=self.stt)
            self.stt_thread.start()
            self.stt_thread.stt_finished.connect(self.on_stt_finished)
            self.text_input.setPlaceholderText('Processing...')

    def on_stt_finished(self,content:str):
        content=content.strip()
        self.text_input.setDisabled(False)
        if len(content):
            self.text_input.setText(content)
            self.send_button.setDisabled(False)
        else:
            self.send_button.setDisabled(True)

    def on_text_changed(self):
        if len(self.text_input.toPlainText().strip()):
            self.send_button.setDisabled(False)
        else:
            self.text_input.setPlaceholderText('How can I help you?')
            self.send_button.setDisabled(True)

    def on_send_clicked(self):
        query=self.text_input.toPlainText().strip()
        if not query:
            return None
        self.text_input.setText('')
        self.text_input.setPlaceholderText('Executing Task...')
        self.mic_button.setDisabled(True)
        self.text_input.setDisabled(True)
        self.agent_thread=AgentThread(agent=self.agent,query=query)
        self.agent_thread.agent_finished.connect(self.on_agent_finished)
        self.agent_thread.start()
        self.send_button.setDisabled(True)

    def on_agent_finished(self,content:str):
        if self.tts is not None:
            self.text_input.setPlaceholderText('Responding...')
            self.tts_thread=TTSThread(self.tts,content)
            self.tts_thread.tts_finished.connect(self.on_tts_finished)
            self.tts_thread.start()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("System Agent: Response")
            msg.setText(content)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.show()
            QTimer.singleShot(0, lambda: msg.move(650, 190))
            self.text_input.setPlaceholderText("How can I help you?")
            self.text_input.setDisabled(False)
            self.send_button.setDisabled(True)
            self.mic_button.setDisabled(False)

    def on_tts_finished(self,content:str):
        self.text_input.setPlaceholderText("How can I help you?")
        self.text_input.setPlaceholderText("How can I help you?")
        self.text_input.setDisabled(False)
        self.send_button.setDisabled(True)
        self.mic_button.setDisabled(False)

    def update_style(self,widget:QWidget, property_name:str, new_value:str):
        """Update a specific CSS property without removing others."""
        style = widget.styleSheet()
        
        # Check if the property exists
        if f"{property_name}:" in style:
            # Replace the existing property
            updated_style = re.sub(f"{property_name}:.*?;", f"{property_name}: {new_value};", style)
        else:
            # Append new property
            updated_style = style + f"\n{property_name}: {new_value};"

        widget.setStyleSheet(updated_style)
        
def launch_ui(agent:Agent=None,stt:STT=None,tts:TTS=None):
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.mycompany.pyqtapp")
    app = QApplication(sys.argv)
    icon = QIcon(resource_path("./ui/assets/icon_transparent.ico"))
    app.setWindowIcon(icon)
    window = ChatUI(agent=agent,stt=stt,tts=tts)
    window.show()
    app.exec()