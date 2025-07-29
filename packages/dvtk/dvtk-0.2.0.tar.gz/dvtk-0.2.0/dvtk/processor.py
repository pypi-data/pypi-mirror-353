"""
Defines a high‐level class (e.g. AudioValidator) that, given a storage backend, 
a list of extensions, and a list of metric‐callback functions, processes files in a streaming manner.
"""
# audio_data_validator/processor.py

import csv
import os
from typing import Callable, Iterable, Sequence, Union, Optional, Iterator
import multiprocessing as mp

from .storage import StorageBackend, LocalStorage, S3Storage
from .utils import safe_apply_metric


class AudioValidator:
    """
    High‐level class that (a) streams files under given paths (local or S3),
    (b) filters by extension, (c) applies user‐provided metric callbacks, 
    (d) writes results to CSV in a streaming manner.
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
        :param paths: List of "directories" to scan. Each can be:
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

    def stream_files(self) -> Iterator[str]:
        """
        Stream files from all paths (possibly mixing local & S3) one at a time.
        """
        for p in self.paths:
            backend = self._get_backend(p)
            yield from backend.iter_files(p, self.extensions)

    # def _apply_single_metric(self, args):
    #     """
    #     Helper method to apply a single metric function.
    #     Args:
    #         args: tuple of (metric_fn, waveform, sample_rate, fpath)
    #     Returns:
    #         List containing either the metric result or error message
    #     """
    #     fn, waveform, sample_rate, fpath = args
    #     try:
    #         res = fn(waveform, sample_rate)
    #         if isinstance(res, dict):
    #             # Order keys in sorted order for consistent CSV columns
    #             return [res.get(k, "") for k in sorted(res.keys())]
    #         return [res]
    #     except Exception as e:
    #         print(f"Error applying metric {fn.__name__} to {fpath}: {e}")
    #         return ["ERROR"]

    def _apply_single_metric(self, args):
        """
        Helper method to apply a single metric function.
        Args:
            args: tuple of (metric_fn, waveform, sample_rate, fpath)
        Returns:
            List containing either the metric result or error message
        """
        fpath, fn = args
        backend = self._get_backend(fpath)
        waveform, sample_rate = backend.open_file(fpath)
        try:
            res = fn(waveform, sample_rate)
            if isinstance(res, dict):
                # Order keys in sorted order for consistent CSV columns
                return [res.get(k, "") for k in sorted(res.keys())]
            return [res]
        except Exception as e:
            print(f"Error applying metric {fn.__name__} to {fpath}: {e}")
            return ["ERROR"]
        
    def process_file(self, fpath: str, writer, lock=None, multiprocessing:bool=False) -> None:
        """
        Process a single file and return its metrics.
        Returns a tuple of (filepath, list of metric results).

        :param fpath: file path
        :param writer: csv writer
        :param lock: lock for thread-safe csv writing
        :param multiprocessing: if True, use multiprocessing to apply metrics in parallel; I only recommend this if the metric computation is heavy. Otherwise, the overhead will hinder the overall speed.
        """
        # backend = self._get_backend(fpath)
        results = []
        
        try:
            # waveform, sample_rate = backend.open_file(fpath)
            
            # Create arguments for each metric function
            # metric_args = [(fn, waveform, sample_rate, fpath) for fn in self.metric_fns]
            metric_args = [(fpath, fn) for fn in self.metric_fns]
            
            if not multiprocessing:
                # vanila
                results = [self._apply_single_metric(args)[0] for args in metric_args]
            else:
                # Use multiprocessing to apply metrics in parallel
                with mp.Pool() as pool:
                    metric_results = pool.map(self._apply_single_metric, metric_args)
                # Flatten results list
                results = [item for sublist in metric_results for item in sublist]
            
            if lock is not None:
                with lock:
                    writer.writerow([fpath] + results)
            else:
                writer.writerow([fpath] + results)
        except Exception as e:
            print(f"Error processing {fpath}: {e}")
            results = ["ERROR"] * len(self.metric_fns)
            if lock is not None:
                with lock:
                    writer.writerow([fpath] + results)
            else:
                writer.writerow([fpath] + results)

    def get_header_cols(self) -> list[str]:
        """
        Determine CSV header columns by running metrics on the first file.
        """
        header_cols = ["filename"]
        
        # Get the first file to determine metric output structure
        try:
            first_file = next(self.stream_files())
        except StopIteration:
            raise RuntimeError("No files found for the given paths + extensions.")
        first_backend = self._get_backend(first_file)
        waveform, sample_rate = first_backend.open_file(first_file)

        # Run each metric once to discover output shape
        for fn in self.metric_fns:
            result = fn(waveform, sample_rate)
            if isinstance(result, dict):
                # Expand each key → column
                for k in sorted(result.keys()):
                    header_cols.append(f"{fn.__name__}__{k}")
            else:
                header_cols.append(fn.__name__)

        return header_cols

    def run(
        self,
        output_csv: str,
        chunk_size: int = 100,
        parallel: bool = False,
        max_workers: int = 4,
        verbose_step_interval:Optional[int]=None
    ):
        """
        Main entry: stream files, apply metrics, write CSV.

        :param output_csv: local path where results.csv will be written.
        :param chunk_size: flush to disk every `chunk_size` files.
        :param parallel: if True, use ThreadPoolExecutor for parallel processing.
        :param max_workers: number of threads if parallel=True.
        """
        print('run...')
        if verbose_step_interval is None:
            verbose_step_interval = chunk_size
        header_cols = self.get_header_cols()
        processed_count = 0

        with open(output_csv, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header_cols)

            if parallel:
                import threading
                from concurrent.futures import ThreadPoolExecutor, as_completed
                
                def process_chunk(files, writer, lock: threading.Lock) -> None:
                    for f in files:
                        self.process_file(f, writer, lock)      # return just the metrics/row data

                lock = threading.Lock()  # create a lock for thread-safe csv writing
                chunk = []
                printed = False
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    print('start streaming...')
                    for file in self.stream_files():
                        chunk.append(file)
                        
                        if len(chunk) >= chunk_size:
                            chunk_to_process = chunk.copy()
                            
                            threads = []
                            for f in chunk_to_process:
                                t = threading.Thread(target=self.process_file, args=(f, writer, lock))
                                t.start()
                                threads.append(t)
                            # Wait for all threads to finish
                            for t in threads:
                                t.join()

                            chunk = []
                            processed_count += len(chunk_to_process)
                            csvfile.flush()
                            printed = False

                        if processed_count % verbose_step_interval == 0 and not printed:
                            print(f'processed {processed_count} files so far')
                            printed = True
                    
                    # Process remaining files
                    if chunk:
                        future = executor.submit(process_chunk, chunk.copy(), writer, lock)
                        future.result()

                        processed_count += len(chunk)
                        csvfile.flush()
            else:
                for file in self.stream_files():
                    self.process_file(file, writer)
                    processed_count += 1
                    if processed_count % verbose_step_interval == 0:
                        print(f'processed {processed_count} files so far')
                    
                    if processed_count % chunk_size == 0:
                        csvfile.flush()

        print(f"Wrote results for {processed_count} files to: {output_csv}")
