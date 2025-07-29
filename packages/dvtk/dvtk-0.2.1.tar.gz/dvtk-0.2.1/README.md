# Usage

## 1. Install

```bash
pip install dvtk
```

## 2. Run

Run dvtk to validate audio files in local directories.
```bash
dvtk \
  --paths /path/to/directory/ \
  --ext .wav \
  --metrics dvtk.default_metrics:sr,duration,max_amplitude,dnsmos_speech \
  --output dv_result.csv \
  --parallel \
  --max-workers 8
```

Run dvtk to validate audio files in S3 directories.
```bash
dvtk \
  --paths s3://bucket-name/path/to/directory/ \
  --ext .wav \
  --metrics dvtk.default_metrics:sr,duration,max_amplitude,dnsmos_speech \
  --output dv_result.csv \
  --parallel \
  --max-workers 8
```

Remarks
- You can specify multiple paths and extensions (e.g., `--ext .wav .flac`).
- You can specify the AWS profile to use (`--aws-profile`).
- More default metrics are available in `dvtk.default_metrics` (e.g., reference-free PESQ, reference-free SI-SDR for speech).


### Using Custom Metrics

1. Create a small python module (e.g., `mymetrics.py`) in your working directory:

```python
# mymetrics.py
import numpy as np

def custom_metric(audio: np.ndarray, sr: int) -> float:
    ...  # compute the custom metric
    return metric  # float
```

2. Run the CLI:
```bash
dvtk \
  --paths /path/to/directory/ \
  --ext .wav \
  --metrics dvtk.default_metrics:duration,max_amplitude,dnsmos_speech \
            mymetrics:custom_metric \
  --output dv_result.csv \
  --parallel \
  --max-workers 8
```


[TODOs](https://chatgpt.com/share/684056bd-6d9c-8012-9174-938f44271299)
- [ ] Support more storage backends (e.g., Google Cloud Storage)
- [ ] On-disk caching or cehckpointing
- [ ] Progress bar