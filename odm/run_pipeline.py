import configparser
import sys
from fivebhist_runner import *
from vae_runner import *


def get_5bhist_args(config_):
    """Get the arguments for the 5BHIST runner.

    Parameters
    config_ : configparser.ConfigParser

    Returns
    args_ : argparse.Namespace
    """
    parser_ = argparse.ArgumentParser(
        description="Stage 1 mammogram Outlier detection task."
    )
    parser_.add_argument(
        "--data_root",
        type=str,
        default=config_["5BHIST"]["data_root"],
        help="Root directory of the data.",
    )
    parser_.add_argument(
        "--log_dir",
        type=str,
        default=config_["DEFAULT"]["log_dir"],
        help="Directory to save the log files.",
    )
    parser_.add_argument(
        "--final_file",
        type=str,
        default=config_["5BHIST"]["final_file"],
        help="Name of the final text file containing paths to good images.",
    )
    parser_.add_argument(
        "--batch_size",
        type=int,
        default=config_["5BHIST"]["batch_size"],
        help="Number of files to load at a time.",
    )
    parser_.add_argument(
        "--ext",
        type=str,
        default=config_["5BHIST"]["ext"],
        help="File extension of the DICOM files.",
    )
    parser_.add_argument(
        "--max_workers",
        type=int,
        default=config_["5BHIST"]["max_workers"],
        help="Number of processes to use.",
    )
    parser_.add_argument(
        "--timing",
        action="store_true",
        default=config_.getboolean("5BHIST", "timing"),
        help="Whether to time the feature extraction process.",
    )
    args_ = parser_.parse_args()
    validate_inputs(**vars(args_))
    print_properties("5BHIST Runner", **vars(args_))
    return args_


def get_vae_args(config_):
    """Gets the arguments for the VAE runner.

    Parameters
    config_ : configparser.ConfigParser

    Returns
    args_ : argparse.Namespace
    """
    parser_ = argparse.ArgumentParser(
        description="Stage 2 mammogram Outlier detection task."
    )
    parser_.add_argument(
        "--caselist",
        type=str,
        default=config_["VAE"]["caselist"],
        help="The path to the text file containing the paths of the DICOM files.",
    )
    parser_.add_argument(
        "--contamination",
        type=float,
        default=config_["VAE"]["contamination"],
        help="The proportion of outliers in the data.",
    )
    parser_.add_argument(
        "--batch_size",
        type=int,
        default=config_["VAE"]["batch_size"],
        help="The number of files to process in each batch.",
    )
    parser_.add_argument(
        "--good_output",
        type=str,
        default=config_["VAE"]["good_output"],
        help="The name of the final file where good paths are saved.",
    )
    parser_.add_argument(
        "--bad_output",
        type=str,
        default=config_["VAE"]["bad_output"],
        help="The name of the final file where bad paths are saved.",
    )
    parser_.add_argument(
        "--timing",
        action="store_true",
        default=config_.getboolean("VAE", "timing"),
        help="Whether to time the execution of the algorithm.",
    )
    parser_.add_argument(
        "--verbose",
        action="store_true",
        default=config_.getboolean("VAE", "verbose"),
        help="Whether to print progress messages to stdout.",
    )
    args_ = parser_.parse_args()
    validate_inputs(**vars(args_))
    print_properties("VAE Runner", **vars(args_))
    return args_


def run_stage1(args_):
    """Runs the 5BHIST runner.

    Parameters
    args_ : argparse.Namespace
    """
    try:
        fivebhist_runner(
            data_root=args_.data_root,
            final_file=args_.final_file,
            log_dir=args_.log_dir,
            ext=args_.ext,
            batch_size=args_.batch_size,
            max_workers=args_.max_workers,
            timing=args_.timing,
        )
    except Exception as e:
        print(e)
        sys.exit(1)


def run_stage2(args_):
    """Runs the VAE runner.

    Parameters
    args_ : argparse.Namespace
    """
    try:
        gp, bp = vae_runner(
            caselist=args_.caselist,
            contamination=args_.contamination,
            batch_size=args_.batch_size,
            verbose=args_.verbose,
            timing=args_.timing,
        )
    except Exception as e:
        print(e)
        sys.exit(1)

    write_to_file(args_.good_output, gp)
    write_to_file(args_.bad_output, bp)
    print(f"Good paths written to {args_.good_output}")
    print(f"Bad paths written to {args_.bad_output}")
    print("number of good paths:", len(gp))
    print("****** Outlier detection complete. ******")


def write_to_file(file_path, paths):
    """Writes the paths to a text file.

    Parameters
    file_path (str) : The path to the text file.
    paths (list) : The list of paths to write to the file.
    """
    try:
        with open(file_path, "w") as f:
            for path in paths:
                f.write(f"{path}\n")
    except Exception as e:
        print(f"Error writing to file {file_path}: {e}")


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")

    args1 = get_5bhist_args(config)
    run_stage1(args1)

    args2 = get_vae_args(config)
    run_stage2(args2)
