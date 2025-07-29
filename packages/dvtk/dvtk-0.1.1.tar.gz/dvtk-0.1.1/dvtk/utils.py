"""
Miscellaneous helpers (e.g. loading an audio file with librosa or soundfile, simple error handling).
"""
# audio_data_validator/utils.py

import tempfile
import warnings
import typing as tp
import numpy as np
# We’ll import at runtime to avoid making librosa a hard requirement if someone
# wants only local‐filesystem listing.
try:
    import librosa
except ImportError:
    librosa = None
import torch
import soxr


def load_audio_bytes(file_obj: tp.Any, sr: tp.Optional[int] = None) -> tuple[np.ndarray, int]:
    """
    Given a file‐like object (BytesIO or an open file), use librosa to load
    audio into a NumPy array. Returns (samples, sample_rate).
    """
    if librosa is None:
        raise ImportError("librosa is required to load audio.")

    # 1) If it’s an open file with a real path (and extension), let librosa load it directly.
    if hasattr(file_obj, "read") and hasattr(file_obj, "name"):
        path = file_obj.name
        y, sr_loaded = librosa.load(path, sr=sr)
        return y, sr_loaded

    # 2) If it’s just a BytesIO (no .name), try to infer extension first:
    if hasattr(file_obj, "read") and not hasattr(file_obj, "name"):
        # You could try to sniff the header or let the caller provide the extension:
        #   (a) Caller could do: load_audio_bytes(my_bytes_io, ext=".mp3")
        #   (b) Or sniff manually via python‐mimetypes or sox/header inspection.
        # For simplicity, let’s say the caller appends ".mp3" or ".flac" to .name
        ext = getattr(file_obj, "ext", ".wav")  # default to .wav if no ext attribute

        with tempfile.NamedTemporaryFile(suffix=ext) as tf:
            tf.write(file_obj.read())
            tf.flush()
            y, sr_loaded = librosa.load(tf.name, sr=sr)
        return y, sr_loaded

    # 3) If the user literally passed a string path (e.g., "song.mp3"), treat it as a path:
    if isinstance(file_obj, str):
        y, sr_loaded = librosa.load(file_obj, sr=sr)
        return y, sr_loaded

    raise ValueError("Unsupported file_obj type—must be path, open file, or BytesIO.")

def safe_apply_metric(
    filepath: str, open_fn: tp.Any, metric_fn: tp.Any
) -> tp.Union[float, dict, None]:
    """
    Tries to open the file, run metric_fn(audio_array, sample_rate) → scalar or dict.
    Catches exceptions and returns None (or a dict with error info) on failure.
    """
    try:
        with open_fn(filepath) as f:
            audio, sr = load_audio_bytes(f, sr=None)
        result = metric_fn(audio, sr)
        return result
    except Exception as e:
        warnings.warn(f"Metric {metric_fn.__name__} failed on `{filepath}`: {e}")
        return None

def resample(waveform: torch.Tensor, current_sr: int, new_sr: int) -> torch.Tensor:
    """
    Resample the audio waveform to a new sample rate using SOXR.

    params
    ---
    waveform: torch.Tensor, (b c l)
        The audio waveform to resample.
    """
    b = waveform.shape[0]
    waveform_resampled = []
    for i in range(b):
        wav = waveform[i]  # (c l)
        wav = wav.T.numpy()  # (l c)
        wav_resampled = soxr.resample(wav, current_sr, new_sr, quality="hq")
        wav_resampled = wav_resampled.T  # (c l)
        waveform_resampled.append(torch.from_numpy(wav_resampled))
    waveform_resampled = torch.stack(waveform_resampled, dim=0)
    return waveform_resampled  # (b c l)


if __name__ == '__main__':
    # Test load_audio_bytes with different input types
    import io
    import os
    
    # Test case 1: Loading from a local file path
    test_wav_path = "/media/daesoo/Expansion/IRs/microphones/MicIRP_vintage_mic/Altec_639.wav"
    if os.path.exists(test_wav_path):
        print("\nTest 1: Loading from file path")
        try:
            audio, sr = load_audio_bytes(test_wav_path)
            print(f"Successfully loaded audio: shape={audio.shape}, sr={sr}")
        except Exception as e:
            print(f"Error loading from path: {e}")

    # Test case 2: Loading from an open file
    if os.path.exists(test_wav_path):
        print("\nTest 2: Loading from open file")
        try:
            with open(test_wav_path, 'rb') as f:
                audio, sr = load_audio_bytes(f)
                print(f"Successfully loaded audio: shape={audio.shape}, sr={sr}")
        except Exception as e:
            print(f"Error loading from open file: {e}")

    # Test case 3: Loading from BytesIO
    if os.path.exists(test_wav_path):
        print("\nTest 3: Loading from BytesIO")
        try:
            with open(test_wav_path, 'rb') as f:
                bytes_data = f.read()
            bytes_io = io.BytesIO(bytes_data)
            bytes_io.ext = '.wav'  # Set extension attribute
            audio, sr = load_audio_bytes(bytes_io)
            print(f"Successfully loaded audio: shape={audio.shape}, sr={sr}")
        except Exception as e:
            print(f"Error loading from BytesIO: {e}")

    # Test safe_apply_metric
    print("\nTest 4: Testing safe_apply_metric")
    def dummy_metric(audio, sr):
        return {'duration': len(audio) / sr, 'max_amp': audio.max()}

    if os.path.exists(test_wav_path):
        try:
            from dvtk.storage import LocalStorage
            storage = LocalStorage()
            result = safe_apply_metric(test_wav_path, storage.open_file, dummy_metric)
            print(f"Metric results: {result}")
        except Exception as e:
            print(f"Error in safe_apply_metric: {e}")

