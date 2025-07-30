import os


def list_mp4_files(path="."):
    """
    List all .mp4 files in the specified directory (default: current directory).
    """
    mp4_files = [f for f in os.listdir(path) if f.endswith('.mp4') and os.path.isfile(os.path.join(path, f))]
    print(f"MP4 files in the directory '{path}':", mp4_files)
    return mp4_files
