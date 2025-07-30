# pyqsync

**pyqsync** is a command-line tool for synchronizing files between local and remote systems. It supports local-to-local, ADB-connected Android devices, and SFTP targets.

## Features

- Two-way file synchronization
- Support for moved, updated, and deleted file detection
- Conflict resolution options
- Dry-run mode
- Optional MD5 checksum comparison
- CSV diff reporting
- Caching for faster comparisons
- Support for ADB and SFTP (with SSH key/password)

## Installation

```bash
pip install pyqsync
```

## Usage

```bash
pyqsync [OPTIONS] LOCAL_PATH REMOTE_PATH
```

### Positional Arguments

- `LOCAL_PATH`: Path on the local machine
- `REMOTE_PATH`: Path on the remote or target system

### Sync Options

| Option                  | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `-u`, `--update`       | How to handle updated files: `ask`, `local`, `remote`, `skip`, `auto`       |
| `-m`, `--move`         | How to handle moved files: `ask`, `local`, `remote`, `skip`                 |
| `-D`, `--delete`       | How to handle deleted files: `ask`, `local`, `remote`, `skip`, `sync`       |
| `--suppress-conflicts` | Suppress prompt on size conflicts during update                             |

### Technical Options

| Option          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `-c`, `--checksum`     | Use MD5 checksums for file comparison                           |
| `--dry-run`            | Show what actions would be taken without executing them         |
| `--cache`              | Use cached file lists if available                              |
| `--csv FILE`           | Write CSV diff report to `FILE`                                 |
| `--progress`           | Show MD5 computation progress on remote                         |

### Remote Target Options

| Option          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `--adb`                | Use Android device via ADB as remote target                    |
| `--sftp USER@HOST`     | Use SFTP connection to specified user and host                 |
| `--port PORT`          | SSH port (default: 22)                                         |
| `--key PATH`           | Path to SSH private key                                        |
| `--password STRING`    | SSH password                                                   |

### Example

```bash
pyqsync ./local_dir /sdcard/remote_dir --adb -u remote -m remote -D sync -c --dry-run
```

This will simulate syncing a local directory with an Android device over ADB using MD5 checksums.

---

## CSV Report Example

```bash
pyqsync ./src_dir ./dst_dir --csv diff.csv
```

Generates a diff report between `src_dir` and `dst_dir` without syncing.
