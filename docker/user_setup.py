#!/usr/bin/env python3

"""
Set up users for website container.

This was a bit too much logic to jam inline into a Dockerfile, so it’s been
wrapped in a script.
"""
import os.path
import subprocess
from argparse import ArgumentParser
from pwd import getpwnam
from subprocess import check_call, check_output


def create_group(group_name, gid):
    check_call(["addgroup", "--gid", str(gid), group_name])


def create_user(username, uid, extra_group_names=None):
    if extra_group_names is None:
        extra_group_names = []

    home = f"/home/{username}"

    if os.path.exists("/usr/sbin/useradd"):
        check_call(
            [
                "useradd",
                "--create-home",
                "--home-dir",
                home,
                "--uid",
                str(uid),
                username,
            ]
        )
        for g in extra_group_names:
            check_call(["usermod", "-aG", g, username])
    elif "BusyBox" in check_output(
        ["adduser", "--help"], stderr=subprocess.STDOUT, encoding="UTF-8"
    ):
        # -D means don’t prompt for a password
        check_call(["adduser", "-D", "-h", home, "-u", str(uid), username])
        for g in extra_group_names:
            check_call(["addgroup", username, g])
    else:
        raise Exception("Couldn’t find supported useradd/adduser")

    if getpwnam(username).pw_uid != uid:
        raise Exception(f"{username} got wrong uid")


def main():
    parser = ArgumentParser()
    parser.add_argument("--build-user", required=True)
    parser.add_argument("--build-uid", type=int, required=True)
    parser.add_argument("--run-user", required=True)
    parser.add_argument("--run-uid", type=int, required=True)
    parser.add_argument("--data-group", required=True)
    parser.add_argument("--data-gid", type=int, required=True)
    args = parser.parse_args()

    create_group(args.data_group, args.data_gid)
    create_user(args.build_user, args.build_uid)
    create_user(args.run_user, args.run_uid, extra_group_names=[args.data_group])


if __name__ == "__main__":
    main()
