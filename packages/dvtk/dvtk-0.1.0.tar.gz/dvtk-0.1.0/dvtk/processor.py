"""
Defines a high‐level class (e.g. AudioValidator) that, given a storage backend, 
a list of extensions, and a list of metric‐callback functions, walks over all files and calls each metric.
"""
# audio_data_validator/processor.py

import csv
import os
from typing import Callable, Iterable, Sequence, Union, Optional

from .storage import StorageBackend, LocalStorage, S3Storage
from .utils import safe_apply_metric


class AudioValidator:
    """
    High‐level class that (a) enumerates all files under given paths (local or S3),
    (b) filters by extension, (c) applies user‐provided metric callbacks, 
    (d) writes a CSV of {filename, metric1, metric2, ...}.
    """

    def __init__(
        self,
        paths: Iterable[str],
        extensions: Sequence[str],
        metric_fns: Sequence[Callable[[any, int], Union[float, dict]]],
        aws_profile: Optional[str] = None,
        region_name: Optional[str] = None,
    ):
        """
        :param paths: List of “directories” to scan. Each can be:
                      - a local path (e.g. "/data/audio")
                      - an S3 URI (e.g. "s3://my-bucket/audio_dir")
        :param extensions: List of extensions to include, e.g. [".wav", ".flac"].
        :param metric_fns: List of callables. Each callable must accept
                           (audio_array: np.ndarray, sample_rate: int) and return
                           either a scalar (float/int) or a dict of scalars.
        :param aws_profile: (optional) name of AWS profile for S3 access.
        :param region_name: (optional) AWS region name.
        """
        self.paths = list(paths)
        self.extensions = set(ext.lower() for ext in extensions)
        self.metric_fns = list(metric_fns)

        # Instantiate backends on the fly when listing, to allow mixing local/S3.
        self._aws_profile = aws_profile
        self._region_name = region_name

    def _get_backend(self, path: str) -> StorageBackend:
        if path.lower().startswith("s3://"):
            return S3Storage(
                aws_profile=self._aws_profile, region_name=self._region_name
            )
        else:
            return LocalStorage()

    def gather_all_files(self) -> list[str]:
        """
        Walk all `self.paths` (possibly mixing local & S3), return a flat list
        of audio‐file keys that match one of the extensions.
        """
        all_files: list[str] = []
        for p in self.paths:
            backend = self._get_backend(p)
            files = backend.list_files(p, self.extensions)
            all_files.extend(files)
        return sorted(all_files)

    def run(
        self,
        output_csv: str,
        chunk_size: int = 100,
        skip_missing: bool = True,
        parallel: bool = False,
        max_workers: int = 4,
    ):
        """
        Main entry: find all files, apply each metric, write CSV.

        :param output_csv: local path where results.csv will be written.
        :param chunk_size: flush to disk every `chunk_size` files (to limit memory).
        :param skip_missing: if True, on any error (e.g. file not found or metric error),
                             we write empty or NaN in that cell and continue.
        :param parallel: if True, use ThreadPoolExecutor to process files in parallel.
        :param max_workers: number of threads if parallel=True.
        """
        file_list = self.gather_all_files()
        if not file_list:
            raise RuntimeError("No files found for the given paths + extensions.")

        # Build CSV header: “filename”, then one column per metric. If a metric
        # returns a dict, we expand keys as separate columns. To detect that, run
        # each metric on a dummy silent signal (or we can inspect return type on
        # the first real file). Here, we’ll just inspect the first file:
        first_file = file_list[0]
        first_backend = self._get_backend(first_file)
        first_open = first_backend.open_file

        # Run each metric once to discover output shape
        header_cols = ["filename"]
        example_results = []
        for fn in self.metric_fns:
            result = safe_apply_metric(first_file, first_open, fn)
            example_results.append(result)

            if isinstance(result, dict):
                # Expand each key → column
                for k in result.keys():
                    header_cols.append(f"{fn.__name__}__{k}")
            else:
                header_cols.append(fn.__name__)
        example_results.clear()  # we don't use it beyond discovering headers

        # Open CSV writer
        with open(output_csv, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header_cols)

            # Helper to process one file
            def process_one(fpath: str) -> list:
                backend = self._get_backend(fpath)
                open_fn = backend.open_file
                row = [fpath]
                for fn in self.metric_fns:
                    res = safe_apply_metric(fpath, open_fn, fn)
                    if isinstance(res, dict):
                        # order keys in sorted order so that CSV columns are consistent
                        for k in sorted(res.keys()):
                            val = res.get(k, "")
                            if val is None and skip_missing:
                                row.append("")
                            else:
                                row.append(val)
                    else:
                        if res is None and skip_missing:
                            row.append("")
                        else:
                            row.append(res)
                return row

            if parallel:
                from concurrent.futures import ThreadPoolExecutor, as_completed

                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(process_one, fpath): fpath for fpath in file_list
                    }
                    count = 0
                    for fut in as_completed(futures):
                        row = fut.result()
                        writer.writerow(row)
                        count += 1
                        if count % chunk_size == 0:
                            csvfile.flush()
            else:
                for idx, fpath in enumerate(file_list, start=1):
                    row = process_one(fpath)
                    writer.writerow(row)
                    if idx % chunk_size == 0:
                        csvfile.flush()

        print(f"Wrote results for {len(file_list)} files to: {output_csv}")
