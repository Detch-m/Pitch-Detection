# Karaoke Machine Project Description
By: Detch M. and Liam B. 
It uses a pitch detection algorithm to score karaoke singing. It requires .wav or .mp4 files from the user, specifically covering the vocal tracks of the song to test (reference audio) and the user's singing (user audio). It will score them from 50 to 100, purely on pitch. It uses the MIDI scale and has two levels of sensitivity, with one meant for beginners and another for those who are confident at singing. The sensitivity of the model and scoring system can be changed in signal_process.py. It also has a GUI to browse all tracks loaded into the program, as well as built-in recording, scoring, MIDI score over time, and playback features. 

# Instructions
(1) Python 3.13.0
(2) pip install -r requirements.txt

# Testing
- Download perfect_vocals2.wav (reference audio) and itim_perfect.wav (sample user audio) needed to test and play around with signal_processing.
- You can record your own audio using Karaoke_Clean_Gui.py, which will save a file named "recording.wav" in your folder.
- You can run the various Karaoke_Clean_Gui.py tests
