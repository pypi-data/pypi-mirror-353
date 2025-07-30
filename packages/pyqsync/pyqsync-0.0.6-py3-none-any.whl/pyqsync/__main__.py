import argparse
import logging
import sys
from .syncer import Syncer
from .client_adb import AdbFileTransfer
from .client_lft import LocalFileTransfer
from .client_sftp import SFTPFileTransfer


def parse_arguments():
    parser = argparse.ArgumentParser(description="Sync files between local and remote systems")
    parser.add_argument("local_path", help="Path one the local machine")
    parser.add_argument("remote_path", help="Path on the remote machine")

    # Sync options
    parser.add_argument(
        "-u",
        "--update",
        choices=["ask", "local", "remote", "skip", "auto"],
        default="skip",
        help="How to handle updated files (default: skip)",
    )
    parser.add_argument(
        "-m",
        "--move",
        choices=["ask", "local", "remote", "skip"],
        default="skip",
        help="How to handle moved files (default: skip)",
    )

    parser.add_argument(
        "-D",
        "--delete",
        choices=["ask", "local", "remote", "skip", "sync"],
        default="sync",
        help="How to handle deleted files (default: sync)",
    )
    parser.add_argument(
        "--suppress-conflicts", action="store_true", help="Ask when there's a size conflict during update or not"
    )

    # Technical options
    parser.add_argument("-c", "--checksum", action="store_true", help="Use MD5 checksums for file comparison")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without actually doing it")
    parser.add_argument("--cache", action="store_true", help="Use cached file lists if available")
    parser.add_argument("--csv", metavar="FILE", default=None, help="Generate CSV diff report to specified file")
    parser.add_argument("--progress", action="store_true", help="Show md5 remote progress")

    parser.add_argument("--adb", action="store_true", help="Generate CSV diff report to specified file")
    parser.add_argument("--sftp", metavar="USER@HOST", default=None, help="SFTP target in the form user@host")
    parser.add_argument("--port", type=int, default=22, help="SSH port")
    parser.add_argument("--key", default=None, help="SSH key")
    parser.add_argument("--password", default=None, help="SSH password")

    # ["path", "path", "-u", "remote", "-m", "remote", "-D", "remote", "--suppress-conflicts", "-c", "--dry-run", "--progress", "--csv", "output.csv"]
    return parser.parse_args()


def main():
    args = parse_arguments()
    print(vars(args).items())

    local_client = LocalFileTransfer()
    remote_client = LocalFileTransfer(md5sum_progress=args.checksum)
    if args.adb:
        remote_client = AdbFileTransfer(md5sum_progress=args.checksum)
    elif args.sftp:
        user = args.sftp.split("@")[0]
        host = args.sftp.split("@")[1]
        port = args.port
        key = args.key
        password = args.password
        remote_client = SFTPFileTransfer(user, host, port, password, key, md5sum_progress=args.checksum)

    # Create syncer instance
    syncer = Syncer(local_client, remote_client)

    if args.csv:
        # Generate CSV diff report
        syncer.diff_to_csv(args.local_path, args.remote_path, args.csv, use_md5sum=args.checksum)
    else:
        # Perform sync
        syncer.sync(
            args.local_path,
            args.remote_path,
            move_on=args.move,
            update_on=args.update,
            delete_on=args.delete,
            suppress_conflicts=args.suppress_conflicts,
            use_md5sum=args.checksum,
            dry_run=args.dry_run,
            use_cache=args.cache,
        )


if __name__ == "__main__":
    main()
