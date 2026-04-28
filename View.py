import os
import sys
import time
from pathlib import Path
from typing import List, Optional

import cv2
import imageio_ffmpeg as ffmpeg
import numpy as np
import sounddevice as sd
import soundfile as sf
import subprocess
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QListWidget,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
class KaraokeView(QWidget):
    """View layer that displays the song list, video widget, and player controls."""

    play_pressed = pyqtSignal()
    record_pressed = pyqtSignal()
    stop_pressed = pyqtSignal()
    playback_pressed = pyqtSignal()
    song_selected = pyqtSignal(str)

def __init__(self, model: KaraokeModel):
        """Initialize the karaoke view with the model.

        Args:
            model (KaraokeModel): The model instance for the view.

        Returns:
            None
        """
        super().__init__()
        self.model = model
        self.setWindowTitle("Mister Microphone")
        self.setGeometry(100, 100, 1200, 900)
        self.video_label = QLabel("Select a song to load video")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: black; color: white;")
        self._build_ui()
        self.timer = QTimer(self)
