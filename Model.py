# -*- coding: utf-8 -*-
"""
Karaoke app model and audio capture helpers.

This module provides the karaoke data model for song selection,
audio extraction, recording persistence, and microphone capture.
"""
# pylint: disable=invalid-name,import-error

from pathlib import Path
from typing import List, Optional
import subprocess

import imageio_ffmpeg as ffmpeg
import numpy as np
import sounddevice as sd
import soundfile as sf

from karaoke_scorer import PitchScoring

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "Pitch-Detection" / "Songs"
RECORDING_FILE = PROJECT_ROOT / "recording.wav"
SUPPORTED_EXTENSIONS = [".mp4"]


class KaraokeModel:  # pylint: disable=too-many-instance-attributes
    """Model that tracks song selection, audio data, and recorded vocals."""

    def __init__(self, figures_dir: Path = FIGURES_DIR):
        """
        Initialize the karaoke model with the figures directory.

        Args:
            figures_dir (Path): The directory containing MP4 files. Defaults to FIGURES_DIR.
        """
        self.figures_dir = Path(figures_dir)
        self.songs: List[str] = self.list_songs()
        self.selected_song: Optional[str] = None
        self.selected_path: Optional[Path] = None
        self.audio_data: Optional[np.ndarray] = None
        self.sample_rate: int = 0
        self.recorded_audio: Optional[np.ndarray] = None
        self.recording_rate: int = 44100

    def list_songs(self) -> List[str]:
        """
        Return the list of available MP4 song files.

        Returns:
            A sorted list of MP4 filenames found in the figures directory.
        """
        if not self.figures_dir.exists():
            return []
        return sorted(
            [
                entry.name
                for entry in self.figures_dir.iterdir()
                if entry.is_file() and entry.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
        )

    def set_selected_song(self, song_name: str) -> bool:
        """
        Select the named song if the file exists.

        Args:
            song_name (str): The filename of the song to select.

        Returns:
            True if the song exists and was selected; otherwise False.
        """
        candidate = self.figures_dir / song_name
        if candidate.is_file():
            self.selected_song = song_name
            self.selected_path = candidate
            self.audio_data = None
            self.sample_rate = 0
            return True
        return False

    def load_audio_track(self) -> bool:
        """
        Extract the MP4 audio track using FFmpeg and cache it as stereo audio.

        Returns:
            True if audio was extracted successfully; otherwise False.
        """
        if self.selected_path is None:
            return False
        try:
            ffmpeg_exe = ffmpeg.get_ffmpeg_exe()
            command = [
                ffmpeg_exe,
                "-i",
                str(self.selected_path),
                "-vn",
                "-ac",
                "2",
                "-ar",
                str(self.recording_rate),
                "-f",
                "f32le",
                "-",
            ]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if result.returncode != 0 or not result.stdout:
                self.audio_data = None
                self.sample_rate = 0
                return False
            audio = np.frombuffer(result.stdout, dtype=np.float32)
            if audio.size % 2 == 0:
                audio = audio.reshape(-1, 2)
            self.audio_data = audio
            self.sample_rate = self.recording_rate
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            self.audio_data = None
            self.sample_rate = 0
            return False

    def save_recording(
        self, recording: np.ndarray, path: Optional[Path] = None
    ) -> bool:
        """
        Save the recorded vocals to a WAV file and cache the data.

        Args:
            recording (np.ndarray): The recorded waveform.
            path (Optional[Path]): Optional output path. Uses RECORDING_FILE if omitted.

        Returns:
            True if the file saved successfully; otherwise False.
        """
        target_path = Path(path) if path is not None else RECORDING_FILE
        try:
            sf.write(str(target_path), recording, self.recording_rate)
            self.recorded_audio = recording
            return True
        except Exception:  # pylint: disable=broad-exception-caught
            return False

    def has_recording(self) -> bool:
        """
        Return True when a recording is available.

        Returns:
            True if a recording exists; otherwise False.
        """
        return self.recorded_audio is not None and len(self.recorded_audio) > 0
    
    def calculate_score(self, level = 0) -> Optional[float]:
        """
        Executes the pitch analysis pipeline to score the user's vocal performance.

        Args:
            level (int): The difficulty level for scoring (0 for easy, 1 for hard).

        Returns:
            The calculated score as a float, or None if the calculation fails.
        """
        try:
            scorer = PitchScoring(str(self.selected_path),str(RECORDING_FILE))

            scorer.process_files("pYIN")
            scorer.align_tracks()
            self.last_score = scorer.pitch_score(level)
            return self.last_score

        except Exception: # pylint: disable=broad-exception-caught
            self.last_score = None
            return None
    
    def generate_pitch_plot(self) -> bool:
        """
        Generates a matplotlib window comparing the reference and user pitch tracks.

        Returns:
            True if the plot was generated successfully; otherwise False.
        """
        if self.selected_path is None or not self.has_recording():
            return False

        try:
            scorer = PitchScoring(str(self.selected_path),str(RECORDING_FILE))
            scorer.plot_results()
            return True
            
        except Exception: # pylint: disable=broad-exception-caught
            return False

class AudioRecorder:
    """Helper that records microphone input until stopped or paused."""

    def __init__(self, sample_rate: int = 44100, channels: int = 1):
        """
        Initialize the audio recorder with sample rate and channels.

        Args:
            sample_rate (int): The sample rate for recording. Defaults to 44100.
            channels (int): The number of audio channels. Defaults to 1.
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self._frames: List[np.ndarray] = []
        self._stream = None
        self._paused = False

    def start(self) -> None:
        """
        Open the input stream and begin recording immediately.
        """
        self._frames = []
        self._paused = False
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            callback=self._callback,
        )
        self._stream.start()

    def pause(self) -> None:
        """
        Pause incoming recording without losing captured audio.
        """
        if self._stream is not None:
            self._paused = True

    def resume(self) -> None:
        """
        Resume recording after a pause.
        """
        if self._stream is not None:
            self._paused = False

    def stop(self) -> np.ndarray:
        """
        Summary:
            Stop recording and return the captured audio.

        Returns:
            The captured audio as a numpy array.
        """
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        self._paused = False
        if not self._frames:
            return np.empty((0, self.channels), dtype="float32")
        return np.concatenate(self._frames, axis=0)

    def _callback(self, indata, _frames, _time, _status) -> None:
        if not self._paused:
            self._frames.append(np.copy(indata))