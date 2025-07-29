# locktools

A simple file-based lock utility for Python applications. Useful for pausing/resuming processes using a lock file, with human-readable timestamps.

## Features
- Create a lock file with a localized timestamp
- Release (remove) the lock file
- Check if the lock file exists

## Installation

```sh
pip install locktools
```

## Usage

```python
from locktools import create_lock, release_lock, is_locked

# Create the lock file
create_lock()

# Check if locked
if is_locked():
    print("Locked!")

# Release the lock
release_lock()
```

## License
MIT
