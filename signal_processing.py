"""
The goal of this algorithm is to find the pitch and sync it to a file.

"""

import numpy as np
import librosa
from librosa.sequence import dtw
import matplotlib.pyplot as plt

from scipy.signal import medfilt
from scipy.signal import butter, filtfilt


class File_processing:
    def __init__(self, ref_file, user_file):
        self.ref_file = ref_file
        self.user_file = user_file

        self.ref_pitch = None
        self.user_pitch = None
        self.alignment_path = None

    def extract_pitch(self, audio_file):
        y, sr = librosa.load(audio_file)

        pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.2)

        pitch_track = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            pitch_track.append(pitch if pitch > 0 else np.nan)

        pitch_track = np.array(pitch_track)
        print(len(pitch_track))

        return pitch_track

    def extract_pitch_2(self, audio_file):
        y, sr = librosa.load(audio_file)
        f0 = librosa.yin(
            y,
            sr=sr,
            fmin=60.0,
            fmax=1000.0,
        )
        print(len(f0))
        return f0

    def process_files(self):
        self.ref_pitch = self.extract_pitch_2(self.ref_file)
        self.user_pitch = self.extract_pitch_2(self.user_file)

    def align_tracks(self):
        # Replace NaNs with 0 for DTW (not perfect, but workable baseline)
        ref = np.nan_to_num(self.ref_pitch)
        user = np.nan_to_num(self.user_pitch)

        D, wp = dtw(ref.reshape(1, -1), user.reshape(1, -1), metric="euclidean")
        self.alignment_path = wp[::-1]  # reverse to chronological order

    def hz_to_cents(self, f):
        return 1200 * np.log2(f / 440.0)

    def pitch_score(self):
        ref_aligned = []
        user_aligned = []

        for i, j in self.alignment_path:
            ref_aligned.append(self.ref_pitch[i])
            user_aligned.append(self.user_pitch[j])

        ref_aligned = np.array(ref_aligned)
        user_aligned = np.array(user_aligned)

        mask = ~np.isnan(ref_aligned) & ~np.isnan(user_aligned)
        if np.sum(mask) == 0:
            return 0

        error = np.abs(
            self.hz_to_cents(ref_aligned[mask]) - self.hz_to_cents(user_aligned[mask])
        )

        score = np.exp(-error / 50)
        return float(np.mean(score) * 100)

    def pitch_score_generous(self):
        ref_aligned = []
        user_aligned = []

        for i, j in self.alignment_path:
            ref_aligned.append(self.ref_pitch[i])
            user_aligned.append(self.user_pitch[j])

        ref_aligned = np.array(ref_aligned)
        user_aligned = np.array(user_aligned)

        scores = []

        for ref_p, user_p in zip(ref_aligned, user_aligned):
            if np.isnan(ref_p) or np.isnan(user_p):
                continue

            error = abs(self.hz_to_cents(ref_p) - self.hz_to_cents(user_p))

            # --- GENEROUS TOLERANCE MODEL ---
            if error < 50 * 4:

                score = 100  # basically perfect

            elif error < 75 * 4:

                score = 90  # still very good

            elif error < 100 * 4:

                score = 85  # acceptable

            elif error < 125 * 4:

                score = 75  # noticeably off

            else:
                score = 50  # very off

            scores.append(score)

        return float(np.mean(scores)) if len(scores) > 0 else 0

    # ---------------------------
    # 6. Final score
    # ---------------------------
    def final_score(self):
        pitch = self.pitch_score_generous()
        print("pitch", self.pitch_score_generous())
        final = pitch
        return final

    # ---------------------------
    # 7. Graphing function
    # ---------------------------
    def plot_results(self):
        if self.alignment_path is None:
            raise ValueError("Run align_tracks() first.")

        ref_aligned = []
        user_aligned = []
        frame_scores = []

        # cum_scores = []

        for i, j in self.alignment_path:
            ref_p = self.ref_pitch[i]
            user_p = self.user_pitch[j]

            ref_aligned.append(ref_p)
            user_aligned.append(user_p)

            # Compute per-frame pitch score
            if not np.isnan(ref_p) and not np.isnan(user_p):
                error = abs(self.hz_to_cents(ref_p) - self.hz_to_cents(user_p))
                score = np.exp(-error / 50) * 100
            else:
                score = 0

            frame_scores.append(score)

        ref_aligned = np.array(ref_aligned)
        user_aligned = np.array(user_aligned)
        frame_scores = np.array(frame_scores)
        time = np.arange(len(ref_aligned))

        # ---- Plot 1: Pitch comparison ----
        plt.figure()
        plt.plot(time, ref_aligned, label="Reference Pitch")
        plt.plot(time, user_aligned, label="User Pitch")
        plt.title("Pitch Comparison Over Time")
        plt.xlabel("Time (frames)")
        plt.ylabel("Frequency (Hz)")
        plt.legend()
        plt.grid()

        # ---- Plot 2: Score in frames ----
        plt.figure()
        plt.plot(time, frame_scores)
        plt.title("Score Over Time")
        plt.xlabel("Time (frames)")
        plt.ylabel("Score (0-100)")
        plt.grid()
        plt.show()

        # reference           # user


processor = File_processing(
    "I Can't Help Falling In Love With You - Elvis Presley.mp4", "Recording.wav"
)

processor = File_processing("PerfectVocals_2.wav", "Itim_Perfect.wav")

# processor = File_processing("Perfect_Vocals.wav", "PerfectVocals_2.wav")
processor.process_files()
processor.align_tracks()
scores = processor.final_score()
print(scores)
processor.plot_results()
