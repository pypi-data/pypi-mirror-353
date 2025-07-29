"""
Contains an abstract "Storage" interface plus two concrete implementations:
one for local filesystem and one for S3.

Updated to allow passing either a single path (string) or a list of paths.
"""

import os
from abc import ABC, abstractmethod
from urllib.parse import urlparse
from typing import Optional, Union, List, Set

import boto3
from botocore.exceptions import ClientError
from io import BytesIO


class StorageBackend(ABC):
    """Abstract base class: any storage must implement `list_files()` and `open_file()`."""

    @abstractmethod
    def list_files(self, paths: Union[str, List[str]], extensions: Set[str]) -> List[str]:
        """
        Return a list of "file keys" (URIs) under each path in `paths` (including subdirs)
        whose filenames end with one of `extensions`.

        `paths` can be a single string or a list of strings.
        """
        raise NotImplementedError

    @abstractmethod
    def open_file(self, key: str):
        """
        Open a file for reading, given its "key" (which might be a local path or an S3 URI).
        Return a file‐like object (binary) or a tuple (waveform, sample_rate) depending on the backend.
        """
        raise NotImplementedError


class LocalStorage(StorageBackend):
    """Walk local filesystem (os.walk) and return all matching files."""

    def list_files(self, paths: Union[str, List[str]], extensions: Set[str]) -> List[str]:
        if isinstance(paths, str):
            paths_to_search = [paths]
        else:
            paths_to_search = paths

        matches: List[str] = []
        for path in paths_to_search:
            for root, _dirs, files in os.walk(path):
                for fn in files:
                    if any(fn.lower().endswith(ext.lower()) for ext in extensions):
                        matches.append(os.path.join(root, fn))
        return matches

    def open_file(self, key: str, mode: str = "rb"):
        # key is a normal local path
        return open(key, mode)


class S3Storage(StorageBackend):
    """
    List objects under an S3 URI prefix (e.g. "s3://bucket-name/path/to/dir").
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

    def list_files(self, paths: Union[str, List[str]], extensions: Set[str]) -> List[str]:
        if isinstance(paths, str):
            prefixes = [paths]
        else:
            prefixes = paths

        matches: List[str] = []
        for path in prefixes:
            bucket_name, prefix = self._parse_s3_uri(path)
            bucket = self.s3.Bucket(bucket_name)

            for obj in bucket.objects.filter(Prefix=prefix):
                key_name = obj.key
                if any(key_name.lower().endswith(ext.lower()) for ext in extensions):
                    matches.append(f"s3://{bucket_name}/{key_name}")
        return matches

    def open_file(self, key: str, mode: str = "rb"):
        """
        Returns a file-like object. For large files, boto3 does not support streaming
        as a file-like directly, so we read into BytesIO. If files are huge, you may want 
        to download to a temp file instead.
        """
        bucket_name, key_name = self._parse_s3_uri(key)
        obj = self.client.get_object(Bucket=bucket_name, Key=key_name)
        return BytesIO(obj["Body"].read())


if __name__ == '__main__':
    # Example usage of LocalStorage with a list of paths
    local_storage = LocalStorage()
    test_paths = [
        "/media/daesoo/Expansion/IRs/microphones/MicIRP_vintage_mic/",
        "/media/daesoo/Expansion/IRs/microphones/Telephone 90_s model mono/"
    ]
    extensions = {".wav", }
    files = local_storage.list_files(test_paths, extensions)
    print(f"Found {len(files)} files with extensions {extensions}:")
    for file in files:
        print(f"- {file}")

    # Try opening and reading one of the found files
    if files:
        print("\nTrying to open first file:")
        first_file = files[0]
        print(f"Opening {first_file}")
        try:
            obj = local_storage.open_file(first_file)

            print(f"Successfully loaded audio file with the shape of {wav.shape} samples at {sr}Hz")
        except Exception as e:
            print(f"Error opening file: {e}")

    # ---------------------------------------------------------------------------
    # Example usage of S3Storage with a single prefix and a list of prefixes
    s3_storage = S3Storage(aws_profile="default", region_name="eu-north-1")
    # single_prefix = "s3://speech-hance/background_noise/Ambience/Air/"
    multiple_prefixes = [
        "s3://speech-hance/background_noise/Ambience/Air/",
        "s3://speech-hance/background_noise/Ambience/Desert/"
    ]
    # s3_files_single = s3_storage.list_files(single_prefix, extensions)
    s3_files_multiple = s3_storage.list_files(multiple_prefixes, extensions)

    # print(f"S3 (single prefix) found {len(s3_files_single)} files.")
    print(f"S3 (multiple prefixes) found {len(s3_files_multiple)} files.")

    # Try opening and reading one of the found S3 files
    if s3_files_multiple:
        print("\nTrying to open first S3 file:")
        first_s3_file = s3_files_multiple[0]
        print(f"Opening {first_s3_file}")
        try:
            obj = s3_storage.open_file(first_s3_file)
            print(f"Successfully loaded S3 audio file with shape {wav.shape} at {sr}Hz")
        except Exception as e:
            print(f"Error opening S3 file: {e}")
