"""
A few example metrics (e.g. duration, sample rate, RMS). 
Users can import these or write their own functions with the same signature.
"""
# audio_data_validator/default_metrics.py

import torch
import numpy as np
from torchmetrics.audio.dnsmos import DeepNoiseSuppressionMeanOpinionScore
from . import squim_objective_model
from dvtk.utils import resample

def sr(audio: np.ndarray, sr: int) -> float:
    """Return sample rate."""
    return sr

def duration(audio: np.ndarray, sr: int) -> float:
    """Return duration in seconds."""
    return len(audio) / float(sr)


def max_amplitude(audio: np.ndarray, sr: int) -> float:
    """Return the maximum absolute amplitude."""
    return float(np.max(np.abs(audio)))


def rms_energy(audio: np.ndarray, sr: int) -> float:
    """Compute root‐mean‐square energy of the entire signal."""
    return float(np.sqrt(np.mean(np.square(audio))))

def dnsmos_speech(audio: np.ndarray, sr: int) -> float:
    """
    DeepNoiseSuppressionMeanOpinionScore
    - https://lightning.ai/docs/torchmetrics/stable/audio/deep_noise_suppression_mean_opinion_score.html
    - speech quality metric

    Args:
        audio: (length,)
        sr: sample rate

    Returns:
        mos_pred: float
    """
    audio = torch.from_numpy(audio)
    mos_model = DeepNoiseSuppressionMeanOpinionScore(sr, False)
    mos_pred = mos_model(audio)[0].item()
    return mos_pred

def rf_pesq_speech(audio: np.ndarray, sr: int) -> float:
    """
    Reference-free Perceptual Evaluation of Speech Quality
    - speech quality metric

    Reference:
    - https://arxiv.org/abs/2304.01448
    - https://docs.pytorch.org/audio/main/tutorials/squim_tutorial.html
    """
    audio = torch.from_numpy(audio).float()  # (length,)
    audio = audio.unsqueeze(0).unsqueeze(0)  # (1 1 l)
    if sr != 16000:  # Currently, Torchaudio-Squim model only supports 16000 Hz sampling rate.
        audio = resample(audio, sr, 16000)
    audio = audio.squeeze(0)
        
    squim_objective_model.eval()
    with torch.no_grad():
        stoi_hyp, pesq_hyp, si_sdr_hyp = squim_objective_model(audio)
    return pesq_hyp.item()


def rf_sisdr_speech(audio: np.ndarray, sr: int) -> float:
    """
    Reference-free Signal-to-Distortion Ratio
    - speech quality metric

    Reference:
    - https://arxiv.org/abs/2304.01448
    - https://docs.pytorch.org/audio/main/tutorials/squim_tutorial.html
    """
    audio = torch.from_numpy(audio).float()  # (length,)
    audio = audio.unsqueeze(0).unsqueeze(0)  # (1 1 l)
    if sr != 16000:  # Currently, Torchaudio-Squim model only supports 16000 Hz sampling rate.
        audio = resample(audio, sr, 16000)
    audio = audio.squeeze(0)
        
    squim_objective_model.eval()
    with torch.no_grad():
        stoi_hyp, pesq_hyp, si_sdr_hyp = squim_objective_model(audio)
    return si_sdr_hyp.item()


if __name__ == "__main__":
    sr = 16000
    audio = np.random.randn(sr)
    mos = dnsmos_speech(audio, sr)
    print('mos:', mos)

    pesq = rf_pesq_speech(audio, sr)
    print('pesq:', pesq)

    sisdr = rf_sisdr_speech(audio, sr)
    print('sisdr:', sisdr)

