import os
from datetime import datetime
import locale

LOCKFILE_PATH = '.lock'


def create_lock(lockfile_path=LOCKFILE_PATH):
    """
    Create a lock file to signal that a resource or process is locked.
    The file will contain a human-readable, localized timestamp indicating when the lock was set.
    Useful for coordinating access to shared resources or pausing/resuming tasks in distributed systems, scripts, or applications.

    Args:
        lockfile_path (str): Path to the lock file. Defaults to '.lock'.
    """
    # Set locale to the user's default setting
    try:
        locale.setlocale(locale.LC_TIME, '')
    except locale.Error:
        pass  # fallback to default C locale if not available
    now = datetime.now()
    timestamp = now.strftime('%c')  # Locale's appropriate date and time representation
    with open(lockfile_path, 'w', encoding='utf-8') as f:
        f.write(f'Locked at: {timestamp}\n')


def release_lock(lockfile_path=LOCKFILE_PATH):
    """
    Remove the lock file to signal that the resource or process is unlocked.
    This allows other processes or tasks to proceed.

    Args:
        lockfile_path (str): Path to the lock file. Defaults to '.lock'.
    """
    if os.path.exists(lockfile_path):
        os.remove(lockfile_path)


def is_locked(lockfile_path=LOCKFILE_PATH):
    """
    Check if the lock file exists, indicating that the resource or process is currently locked.

    Args:
        lockfile_path (str): Path to the lock file. Defaults to '.lock'.

    Returns:
        bool: True if the lock file exists, False otherwise.
    """
    return os.path.exists(lockfile_path) 