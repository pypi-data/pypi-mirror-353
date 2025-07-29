"""
A small command‐line entry point (e.g. using argparse or click) so that end users can run something like:
```
adv-validate \
  --paths /data/audio s3://my-bucket/raw_audio \
  --ext .wav \
  --metrics mymodule.metrics:rms,myother:snr \
  --output results.csv
```
"""
import argparse
import importlib
import sys

from .processor import AudioValidator

def parse_metrics_arg(raw_list: list[str]) -> list:
    """
    Expect metrics specified as module_path:fnname, or module_path:fn1,fn2,fn3
    E.g. `mymod.metrics:duration,rms`.
    Returns a flat list of callables.
    """
    metric_fns = []
    for raw in raw_list:
        if ":" not in raw:
            raise ValueError(f"Invalid metric specification: {raw}")
        module_path, fn_list = raw.split(":", 1)
        try:
            module = importlib.import_module(module_path)
        except ImportError as e:
            print(f"Error importing module `{module_path}`: {e}", file=sys.stderr)
            sys.exit(1)
        for fn_name in fn_list.split(","):
            fn = getattr(module, fn_name, None)
            if fn is None:
                print(f"Module `{module_path}` has no attribute `{fn_name}`", file=sys.stderr)
                sys.exit(1)
            metric_fns.append(fn)
    return metric_fns

def main():
    parser = argparse.ArgumentParser(
        prog="dvtk",
        description="Recursively find audio files and compute metrics, logging results to CSV."
    )
    parser.add_argument(
        "--paths",
        "-p",
        nargs="+",
        required=True,
        help="One or more paths or S3 URIs (e.g. /data/audio s3://my-bucket/files).",
    )
    parser.add_argument(
        "--ext",
        "-e",
        nargs="+",
        required=True,
        help="Audio extensions to include (e.g. .wav .flac).",
    )
    parser.add_argument(
        "--metrics",
        "-m",
        nargs="+",
        required=True,
        help="One or more metric specs in form module:fn1,fn2 (e.g. audio_data_validator.default_metrics:duration,rms).",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Local output CSV path (e.g. results.csv).",
    )
    parser.add_argument(
        "--aws-profile",
        default=None,
        help="(optional) AWS profile name to use for S3.",
    )
    parser.add_argument(
        "--region-name",
        default=None,
        help="(optional) AWS region name (e.g. us-east-1).",
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="If set, process files in parallel using threads.",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Number of threads to use if --parallel is set.",
    )

    args = parser.parse_args()
    try:
        metric_fns = parse_metrics_arg(args.metrics)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    validator = AudioValidator(
        paths=args.paths,
        extensions=args.ext,
        metric_fns=metric_fns,
        aws_profile=args.aws_profile,
        region_name=args.region_name,
    )
    validator.run(
        output_csv=args.output,
        parallel=args.parallel,
        max_workers=args.max_workers,
    )

if __name__ == "__main__":
    main()
