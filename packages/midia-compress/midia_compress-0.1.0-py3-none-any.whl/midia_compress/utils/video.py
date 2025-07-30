import subprocess
import shutil
import sys

from pathlib import Path


def check_ffmpeg() -> bool:
    """Check if FFmpeg is installed and working by testing 'ffmpeg -version'."""
    return (shutil.which("ffmpeg") is not None
            and subprocess.run(["ffmpeg", "-version"],
                             capture_output=True,
                             text=True).returncode == 0)


def compress_video(
    input_file: str,
    output_file: str = '',
    crf: int = 23,
    force_overwrite: bool = False,
    verbose: bool = False
) -> bool:
    """
    Compress video using FFmpeg with libx264 codec

    Args:
        input_file: Path to input video file
        output_file: Path for output video
        crf: Quality factor (18-28, lower=better quality)
        force_overwrite: If True, pass '-y' to FFmpeg to overwrite output file
        verbose: If True, show FFmpeg output; if False, suppress output

    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Validate input file exists
        if not Path(input_file).is_file():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if not output_file or output_file == input_file:
            # Default output file name
            output_file = f"compressed_{Path(input_file).stem}.mp4"

        # Build FFmpeg command
        cmd = ["ffmpeg"]
        if force_overwrite:
            cmd.append("-y")
        cmd += [
            "-i", input_file,
            "-vcodec", "libx264",
            "-crf", str(crf),
            output_file
        ]

        # Run FFmpeg command
        if verbose:
            print("\nRunning command:", " ".join(cmd))
            result = subprocess.run(
                cmd,
                stdout=sys.stdout,
                stderr=sys.stderr,
                check=True
            )
        else:
            result = subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )

        # Verify output was created
        if not Path(output_file).is_file():
            raise RuntimeError("FFmpeg ran but output file wasn't created")

        return True

    except subprocess.CalledProcessError as e:
        if verbose:
            print(f"FFmpeg error: {e.stderr}")
        else:
            print("FFmpeg error (run with verbose=True for details)")
    except Exception as e:
        print(f"Error: {str(e)}")

    return False
