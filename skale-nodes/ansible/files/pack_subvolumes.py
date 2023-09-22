#   -*- coding: utf-8 -*-
#
#   This file is part of node-provisoning
#
#   Copyright (C) 2023 SKALE Labs
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.

import glob
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Tuple


logger = logging.getLogger(__name__)


def run_cmd(
    cmd,
    env={},
    shell=False,
    secure=False,
    check_code=True,
    separate_stderr=False
):
    if not secure:
        logger.debug('Running: %s', cmd)
    else:
        logger.debug('Running some secure command')
    stdout, stderr = subprocess.PIPE, subprocess.PIPE
    if not separate_stderr:
        stderr = subprocess.STDOUT
    res = subprocess.run(
        cmd,
        shell=shell,
        stdout=stdout,
        stderr=stderr,
        env={**env, **os.environ}
    )
    if check_code:
        output = res.stdout.decode('utf-8')
        if res.returncode:
            if separate_stderr:
                output = res.stderr.decode('utf-8')
            logger.error('Error during shell execution: %s', output)
            res.check_returncode()
        else:
            logger.debug('Command is executed successfully. Command log:')
            logger.debug(res.stdout.decode('UTF-8').rstrip())
    return res


def get_mountpoint(name: str) -> str:
    return f'/mnt/schains-{name}'


def get_device(name: str) -> str:
    bd_name = name.replace('-', '--')
    return f'/dev/mapper/schains-{bd_name}'


def is_subvolume(path: str) -> bool:
    return not path.endswith('.txt')


def get_subvolumes_from_folder(folder: str) -> bool:
    subvolumes = []
    pattern = os.path.join(folder, '*')
    for dpath in glob.glob(pattern):
        if is_subvolume(dpath):
            subvolumes.append(dpath)
    return subvolumes


def umount(name):
    run_cmd(['umount', get_mountpoint(name)])


def cleanup(name):
    umount(name)
    shutil.rmtree(get_mountpoint(name))


def ensure_mountpoint(name: str) -> None:
    mountpoint = get_mountpoint(name)
    bd_name = get_device(name)
    os.makedirs(mountpoint, exist_ok=True)

    if not os.path.ismount(mountpoint):
        run_cmd(['mount', bd_name, mountpoint])


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


def pack(result_path, subvolumes):
    run_cmd(['btrfs', 'send', '-f', result_path, *subvolumes])


def main():
    name = sys.argv[1]
    result_folder = sys.argv[2]
    try:
        ensure_mountpoint(name)
        snapshot_folder, block_number = get_schains_snapshot_folder(name)
        print(snapshot_folder, file=sys.stderr)
        subvolumes = get_subvolumes_from_folder(snapshot_folder)
        print(subvolumes, file=sys.stderr)
        ensure_result_folder(result_folder)
        result_path = os.path.join(
            result_folder,
            f'{name}-{block_number}.snap'
        )
        pack(result_path, subvolumes)

    finally:
        cleanup(name)


if __name__ == '__main__':
    main()
