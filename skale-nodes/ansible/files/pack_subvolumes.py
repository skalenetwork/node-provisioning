import glob
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple


def is_subvolume(path: str) -> bool:
    return not path.endswith('.txt')


def get_subvolumes_from_folder(folder: str) -> bool:
    subvolumes = []
    pattern = os.path.join(folder, '*')
    for dpath in glob.glob(pattern):
        if is_subvolume(dpath):
            subvolumes.append(dpath)
    return subvolumes


def get_schains_snapshot_folder(name: str) -> Tuple[str, int]:
    base_dir = f'/mnt/schains-{name}/snapshots'
    pattern = os.path.join(base_dir, '*')

    snapshot_numbers = []
    for dpath in glob.glob(pattern):
        name = Path(dpath).stem
        try:
            bn = int(Path(name).name)
        except ValueError:
            continue
        snapshot_numbers.append(bn)

    bn = max(snapshot_numbers)
    folder = os.path.join(base_dir, str(bn))
    return folder, bn


def ensure_result_folder(result_folder):
    os.makedirs(result_folder, exist_ok=True)


def main():
    name = sys.argv[1]
    result_folder = sys.argv[2]
    snapshot_folder, block_number = get_schains_snapshot_folder(name)
    print(snapshot_folder, file=sys.stderr)
    subvolumes = get_subvolumes_from_folder(snapshot_folder)
    print(subvolumes, file=sys.stderr)
    ensure_result_folder(result_folder)
    result_path = os.path.join(result_folder, f'{name}-{block_number}.snap')
    subprocess.run(['btrfs', 'send', '-f', result_path, *subvolumes])


if __name__ == '__main__':
    main()
