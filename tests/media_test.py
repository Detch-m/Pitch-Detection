"""Test audio extraction from MP4 file using soundfile."""

from pathlib import Path
import soundfile as sf

target = Path(
    "C:/Users/lbennicoff1/.vscode/YIN-Pitch/Figures/Never Gonna Give You Up - Rick Astley.mp4"
)
print("exists", target.exists())
try:
    data, rate = sf.read(str(target), dtype="float32")
    print("soundfile read ok", data.shape, rate)
except Exception as e:  # pylint: disable=broad-exception-caught
    print("soundfile error", repr(e))
