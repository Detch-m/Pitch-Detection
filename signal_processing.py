"""
The goal of this algorithm is to find the pitch and sync it to a file.
"""

import numpy as np
import librosa
import matplotlib.pyplot as plt


class File_processing:
    """
    File processing
    """

    def __init__(self, ref_file, user_file):
        self.ref_file = ref_file
        self.user_file = user_file
        self.ref_pitch = None
        self.user_pitch = None
        self.alignment_path = None

    def extract_pitch(self, audio_file, sensitivity=0.1):
        """
        It recieves the file name of the audio and returns a nparray of the pitches.
        This program ses a sample rate of 22050 and other defaults to Librosa's piptrack
        method. It has a frequency range of 60 to 1000, which is the human vocal range.
        It uses a threshold to identifying singing moments at 0.1 for voice probability.
        It implments the probalistic yin algorithm to detect pitch. This method is highly
        resistant to octave error making it ideal for extracting karaoke singing.

        Args:
            audio_file, a String representing the name of the audiofile
            sensitivity, an float representing the sensitivity of the pyin() algorithm
                        by default this value is set to 0.1

        Returns:
            pitch_track, a numpy array of the pitches in the track
        """

        audio, sample_rate = librosa.load(audio_file)
        pitch_track, voiced_flag, voiced_probs = librosa.pyin(
            y=audio, sr=sample_rate, fmin=60.0, fmax=1000.0
        )
        pitch_track[~voiced_flag] = np.nan
        pitch_track[voiced_probs < 0.1] = np.nan

        return pitch_track

    def process_files(self):
        """
        Processes the files for both the reference and the user
        """
        self.ref_pitch = self.extract_pitch(self.ref_file)
        self.user_pitch = self.extract_pitch(self.user_file)

    def align_tracks(self):
        """
        Ensures both the reference and user audio have equal frames.
        If the user or the reference has more frames than the other,
        the minimum frames is used to ensure consistency between both audios.
        """
        min_frames = min(len(self.ref_pitch), len(self.user_pitch))
        self.ref_pitch = self.ref_pitch[0:min_frames]
        self.user_pitch = self.user_pitch[0:min_frames]

    def hz_to_midi(self, f):
        """
        It takes in a frequency and returns the midi score for that frequency.
        A midi score is a semitone unit of measurement with A4 (440 Hz) equalling
        69 midi score as a standard

        Args:
            f, a np

        Returns:
            midi, representing the midi score
        """
        return 12 * np.log2(f / 440) + 69

    def pitch_score(self, level=0):
        """
        A pitch based scoring system where there is two sensitivies for two levels of users.
        The easy level allows for 1, 2, 5, 12 MIDI-score as error ranges for score deductions. 
        This is very generous and meant to exist for beginner karaoke users. 
        The hard level allows for 0.25, 0.5, 1, 2 MIDI-score as error ranges, which are meant for
        quarter, half, a full-semitone, or two semitones or errors. This is meant for very confident
        singers in their pitch.

        Args:
            level, an integer 0 or 1, which represents the sensitivity of the scoring system
                and harshness of the program. With 0 being easy and 1 being for expert singers.
                By default is is 0, which is for easy.

        Returns:
            A float representing the mean score within the audioframe
        """
        scores = []  # pylint: disable=redefined-outer-name
        sensitivity_hard = [0.25, 0.5, 1, 2]
        sensitivity_easy = [1, 2, 5, 12]
        sensitivity_level = [sensitivity_easy, sensitivity_hard]
        for i, reference_pitch in enumerate(self.ref_pitch):
            user_pitch = self.user_pitch[i]
            if np.isnan(reference_pitch) or np.isnan(user_pitch):
                continue
            error = abs(self.hz_to_midi(reference_pitch) - self.hz_to_midi(user_pitch))
            if error < sensitivity_level[level][0]:
                score = 100  # basically perfect
            elif error < sensitivity_level[level][1]:
                score = 90  # great
            elif error < sensitivity_level[level][2]:
                score = 85  # good
            elif error < sensitivity_level[level][3]:
                score = 75  # solid
            else:
                score = 50  # off
            scores.append(score)
        return float(np.mean(scores))

    # ---------------------------
    # 6. Final score
    # ---------------------------
    def final_score(self):
        pitch = self.pitch_score()
        print("pitch", self.pitch_score())
        final = pitch
        return final

    # ---------------------------
    # 7. Graphing function
    # ---------------------------
    def plot_results(self):
        # if self.alignment_path is None:
        #    raise ValueError("Run align_tracks() first.")
        """
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
        """

        time = np.arange(len(self.user_pitch)) * (265) / (len(self.user_pitch))
        # ---- Plot 1: Pitch comparison ----
        plt.figure()
        plt.plot(
            time, np.array(self.hz_to_midi(self.ref_pitch)), label="Reference Pitch"
        )
        plt.plot(time, np.array(self.hz_to_midi(self.user_pitch)), label="User Pitch")
        plt.title("Pitch Comparison Over Time")
        plt.xlabel("Time (seconds)")
        plt.ylabel("Midi Score")
        plt.legend()
        plt.grid()
        plt.show()

        # ---- Plot 2: Score in frames ----
        # plt.figure()
        # plt.plot(time, frame_scores)
        # plt.title("Score Over Time")
        # plt.xlabel("Time (frames)")
        # plt.ylabel("Score (0-100)")
        # plt.grid()
        # plt.show()
        # reference           # user

        # print(len(user_aligned))


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