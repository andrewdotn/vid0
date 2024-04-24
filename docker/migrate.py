#!/usr/bin/env python

"""
Script for:
  - Ensuring database is in WAL mode (see https://sqlite.org/wal.html)
  - Backing up the database before:
  - Running migrations.
"""

import hashlib
import os
import shutil
import sqlite3
import subprocess
import time
from argparse import ArgumentParser
from glob import glob
from pathlib import Path


def main():
    parser = ArgumentParser()
    parser.add_argument("--db-file", default="db/prod.sqlite3")
    args = parser.parse_args()

    db_file = Path(args.db_file)

    set_wal_mode(db_file)
    backup_database(db_file)
    subprocess.check_call(["./manage.py", "check", "--deploy", "--fail-level=WARNING"])
    subprocess.check_call(["./manage.py", "migrate"])


def set_wal_mode(db_file):
    with sqlite3.Connection(db_file) as db:
        set_journal_mode(db, "wal")


def set_journal_mode(db, journal_mode):
    r = db.execute(f"PRAGMA journal_mode={journal_mode}")
    resulting_mode = r.fetchall()
    if resulting_mode != [(journal_mode,)]:
        raise Exception(f"journal mode came out {resulting_mode!r} not {journal_mode}")


def backup_database(db_file):
    """Make a copy of db_file, but only keep if different from previous backup.

    Uses sqlite3 APIs to ensure copy is consistent.
    """
    time_str = time.strftime("%Y%m%d_%H%M%S_%z")
    backup_file = db_file.with_suffix(f".~bak.{time_str}.sqlite3")

    most_recent_backup = get_most_recent_backup(db_file.with_suffix(".~bak.*.sqlite3"))

    tmp_backup_file = backup_file.with_suffix(".inprogress")
    _do_backup(db_file, tmp_backup_file)

    if most_recent_backup is None or file_hash(most_recent_backup) != file_hash(
        tmp_backup_file
    ):
        shutil.move(tmp_backup_file, backup_file)
        print(f"Backed up to {backup_file}")
    else:
        tmp_backup_file.unlink()


def get_most_recent_backup(glob_pattern):
    existing_backup_files = [Path(f) for f in glob(str(glob_pattern))]

    if len(existing_backup_files) == 0:
        return None

    def by_mtime(path):
        return path.stat().st_mtime

    existing_backup_files.sort(key=by_mtime)
    return existing_backup_files[-1]


def _do_backup(db_file, backup_file):
    "Backup from db_file to backup_file"
    with sqlite3.Connection(db_file) as db:
        with sqlite3.Connection(backup_file) as backup_db:
            # If this is taking a long time, you can hook up a progress meter
            # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup
            db.backup(backup_db)


def file_hash(path):
    ONE_MEGABYTE = 1024**2

    hash = hashlib.sha256()
    with open(os.fspath(path), "rb") as f:
        while 1:
            chunk = f.read(ONE_MEGABYTE)
            if chunk == b"":
                break
            hash.update(chunk)
    return hash.hexdigest()


if __name__ == "__main__":
    main()
