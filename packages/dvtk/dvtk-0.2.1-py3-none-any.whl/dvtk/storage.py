"""
Contains an abstract "Storage" interface plus two concrete implementations:
one for local filesystem and one for S3.

Updated to allow streaming file paths instead of collecting all at once.
"""

import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Optional, Union, List, Set, Generator, Iterator, Tuple
import numpy as np

import librosa
import boto3
from botocore.exceptions import ClientError
from io import BytesIO


class StorageBackend(ABC):
    """Abstract base class: any storage must implement `iter_files()` and `open_file()`."""

    @abstractmethod
    def iter_files(self, paths: Union[str, List[str]], extensions: Set[str]) -> Iterator[str]:
        """
        Yield file paths (URIs) under each path in `paths` (including subdirs)
        whose filenames end with one of `extensions`.

        `paths` can be a single string or a list of strings.
        """
        raise NotImplementedError

    @abstractmethod
    def open_file(self, key: str) -> Tuple[np.ndarray, int]:
        """
        Open a file for reading, given its "key" (which might be a local path or an S3 URI).
        Returns a tuple of (audio_array: np.ndarray, sample_rate: int).
        The audio array will be shape (n_samples,) for mono or (n_samples, n_channels) for stereo.
        """
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Walk local filesystem (os.walk) and yield matching files."""

    def iter_files(self, paths: Union[str, List[str]], extensions: Set[str]) -> Iterator[str]:
        if isinstance(paths, str):
            paths_to_search = [paths]
        else:
            paths_to_search = paths

        for path in paths_to_search:
            for root, _dirs, files in os.walk(path):
                for fn in files:
                    if any(fn.lower().endswith(ext.lower()) for ext in extensions):
                        yield os.path.join(root, fn)

    def open_file(self, key: str) -> Tuple[np.ndarray, int]:
        """
        Load audio file using librosa.
        Returns (audio_array, sample_rate) where audio_array is a numpy array of shape:
        - (n_samples,) for mono
        - (n_samples, n_channels) for stereo
        """
        # librosa.load by default:
        # - Converts to mono (mono=True)
        # - Resamples to 22050 Hz (sr=22050)
        # - Returns float32 array normalized to [-1, 1]
        audio_array, sample_rate = librosa.load(key, sr=None, mono=True)  # sr=None to preserve original sample rate
            
        return audio_array, sample_rate


class S3Storage(StorageBackend):
    """
    Stream objects under an S3 URI prefix (e.g. "s3://bucket-name/path/to/dir").
    """

    def __init__(self, aws_profile: Optional[str] = None, region_name: Optional[str] = None):
        session_kwargs = {}
        if aws_profile:
            session_kwargs["profile_name"] = aws_profile
        if region_name:
            session_kwargs["region_name"] = region_name

        self.session = boto3.Session(**session_kwargs)
        self.s3 = self.session.resource("s3")
        self.client = self.session.client("s3")

    def _parse_s3_uri(self, uri: str) -> tuple[str, str]:
        parsed = urlparse(uri)
        bucket = parsed.netloc
        prefix = parsed.path.lstrip("/")
        return bucket, prefix

    def iter_files(self, paths: Union[str, List[str]], extensions: Set[str]) -> Iterator[str]:
        if isinstance(paths, str):
            prefixes = [paths]
        else:
            prefixes = paths

        for path in prefixes:
            bucket_name, prefix = self._parse_s3_uri(path)
            bucket = self.s3.Bucket(bucket_name)

            # Use paginator for efficient streaming of S3 objects
            paginator = self.client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    key_name = obj['Key']
                    if any(key_name.lower().endswith(ext.lower()) for ext in extensions):
                        yield f"s3://{bucket_name}/{key_name}"

    def open_file(self, key: str) -> Tuple[np.ndarray, int]:
        """
        Load audio from S3 using librosa.
        Returns (audio_array, sample_rate) where audio_array is a numpy array of shape:
        - (n_samples,) for mono
        - (n_samples, n_channels) for stereo
        """
        bucket_name, key_name = self._parse_s3_uri(key)
        obj = self.client.get_object(Bucket=bucket_name, Key=key_name)
        audio_bytes = BytesIO(obj["Body"].read())
        
        # Load audio data using librosa
        audio_array, sample_rate = librosa.load(audio_bytes, sr=None, mono=True)  # sr=None to preserve original sample rate
        
        return audio_array, sample_rate


if __name__ == '__main__':
    # Example usage of LocalStorage with streaming
    local_storage = LocalStorage()
    test_paths = [
        "/media/daesoo/Expansion/IRs/microphones/MicIRP_vintage_mic/",
        "/media/daesoo/Expansion/IRs/microphones/Telephone 90_s model mono/"
    ]
    extensions = {".wav", }
    
    print(f"Streaming files with extensions {extensions}:")
    file_count = 0
    for file in local_storage.iter_files(test_paths, extensions):
        print(f"- {file}")
        file_count += 1
        
        # Try opening the first file we find
        if file_count == 1:
            print(f"\nTrying to open first file: {file}")
            try:
                audio, sr = local_storage.open_file(file)
                print(f"Successfully loaded audio file:")
                print(f"- Shape: {audio.shape}")
                print(f"- Sample rate: {sr} Hz")
                print(f"- Duration: {len(audio)/sr:.2f} seconds")
                print(f"- Channels: {'Stereo' if audio.ndim == 2 else 'Mono'}")
            except Exception as e:
                print(f"Error opening file: {e}")

    print(f"\nTotal files found: {file_count}")

    # Example usage of S3Storage with streaming
    s3_storage = S3Storage(aws_profile="default", region_name="eu-north-1")
    s3_paths = [
        "s3://speech-hance/background_noise/Ambience/Air/",
        "s3://speech-hance/background_noise/Ambience/Desert/"
    ]
    
    print("\nStreaming S3 files:")
    s3_count = 0
    for s3_file in s3_storage.iter_files(s3_paths, extensions):
        print(f"- {s3_file}")
        s3_count += 1
        
        # Try opening the first S3 file
        if s3_count == 1:
            try:
                audio, sr = s3_storage.open_file(s3_file)
                print(f"\nSuccessfully loaded S3 audio file:")
                print(f"- Shape: {audio.shape}")
                print(f"- Sample rate: {sr} Hz")
                print(f"- Duration: {len(audio)/sr:.2f} seconds")
                print(f"- Channels: {'Stereo' if audio.ndim == 2 else 'Mono'}")
            except Exception as e:
                print(f"Error opening S3 file: {e}")
    
    print(f"Total S3 files found: {s3_count}")
