import os
from datetime import datetime, timedelta, timezone
from typing import Iterable, NamedTuple

import boto3
from dotenv import load_dotenv
from mypy_boto3_s3 import S3Client
from mypy_boto3_s3.type_defs import ObjectTypeDef

from target_dirs import TargetDir, target_dirs

UTC = timezone.utc
JST = timezone(timedelta(hours=+9), 'JST')

class FileInfo(NamedTuple):
    bytes: int
    last_modified: datetime
    path: str


def get_target_dirs()-> Iterable[str]:
    for target_dir in target_dirs:
        dirname = target_dir.full_path.strip()
        if dirname.endswith('/'):
            dirname = dirname[:-1]
        yield dirname


def get_local_files(directory: str) -> Iterable[str]:
    for p, ds, fs in os.walk(directory):
        for f in fs:
            yield f'{p}/{f}'


def get_s3_file_list(target_dir: TargetDir) -> Iterable[FileInfo]:
    s3: S3Client = boto3.client('s3')

    file_list: list[ObjectTypeDef] = []
    is_truncated = True
    last_key = ''
    prefix = ''
    while is_truncated:
        res = s3.list_objects_v2(Bucket=target_dir.bucket, Prefix=prefix, MaxKeys=1000, StartAfter=last_key)
        contents = res['Contents']
        is_truncated = res['IsTruncated']
        last_key = contents[-1]['Key']
        file_list.extend(contents)

    for f in file_list:
        if not f['Size']:
            continue
        yield FileInfo(f['Size'], f['LastModified'].astimezone(JST), target_dir.bucket + '/' + f['Key'])


def get_local_file_list(target_dir: TargetDir) -> Iterable[FileInfo]:
    d = target_dir.full_path
    while d.endswith('/'):
        d = d[:-1]

    for fpath in get_local_files(d):
        stat = os.stat(fpath)
        yield FileInfo(stat.st_size, datetime.fromtimestamp(stat.st_mtime).astimezone(JST), fpath.replace(target_dir.full_path, target_dir.dirname))


def compare(remote: list[FileInfo], local: list[FileInfo]) -> tuple[list[FileInfo], list[FileInfo]]:
    """
    Compare file lists (remote and local), and list files to be uploaded or deleted.

    * Files to be uploaded:
        * Files that exist only locally
        * Files where the local file's modification date is newer than the remote file's modification date
    * Files to be deleted:
        * Files that exist only remotely

    Args:
        remote: The list of remote files
        local: The list of local files

    Returns:
        (List of files to be uploaded, List of files to be deleted)
    """
    to_be_uploaded: list[FileInfo] = []
    to_be_deleted: list[FileInfo] = []

    remote = list(sorted(remote, key=lambda f: f.path))
    local = list(sorted(local, key=lambda f: f.path))

    re_count = len(remote)
    lo_count = len(local)

    re_idx = 0
    lo_idx = 0

    while True:
        if re_idx >= re_count or lo_idx >= lo_count:
            break

        re_ = remote[re_idx]
        lo_ = local[lo_idx]

        if re_.path == lo_.path:
            if re_.last_modified < lo_.last_modified:
                to_be_uploaded.append(lo_)
            re_idx += 1
            lo_idx += 1
            continue

        if re_.path < lo_.path:
            to_be_deleted.append(re_)
            re_idx += 1
            continue

        if re_.path > lo_.path:
            to_be_uploaded.append(lo_)
            lo_idx += 1
            continue

    return to_be_uploaded, to_be_deleted

def main():
    load_dotenv()
    for target_dir in target_dirs:
        print(f'## {target_dir.dirname}')
        rf = list(get_s3_file_list(target_dir))
        lf = list(get_local_file_list(target_dir))
        to_be_uploaded, to_be_deleted = compare(rf, lf)
        print('to be uploaded:')
        for f in to_be_uploaded:
            print(f'\t{f}')
        print('to be deleted :')
        for f in to_be_deleted:
            print(f'\t{f}')


if __name__ == '__main__':
    main()
