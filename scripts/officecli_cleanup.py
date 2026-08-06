#!/usr/bin/env python3
"""officecli_cleanup.py - shared Windows cleanup helpers for officecli runs.

Regression runs that drive the resident officecli.exe process leak artifacts in
%TEMP% on Windows:

  * rrcat_reg_* temp dirs survive shutil.rmtree(path, ignore_errors=True)
    because officecli still holds file handles briefly after `officecli close`
    (close is async-ish on Windows) - ignore_errors swallows the failure.
  * officecli-*.lock files from killed sessions are never swept.

This module provides the two helpers every caller should share:

  rmtree_retry(path)  - shutil.rmtree with a retry loop; returns bool, never
                        raises. Use it in finally blocks right after close.
  clean_stale(...)    - sweep %TEMP% for rrcat_* dirs and officecli-*.lock
                        files older than max_age_hours. Entries younger than
                        the cutoff are NEVER touched (another run may be
                        active). Returns the number of entries removed.
"""

import os
import shutil
import tempfile
import time

__all__ = ["rmtree_retry", "clean_stale"]


def rmtree_retry(path, attempts=3, delay=1.0):
    """Remove directory tree, retrying on transient Windows handle locks.

    shutil.rmtree(path, ignore_errors=True) fails silently when the resident
    officecli.exe still holds a handle inside the tree right after close.
    This variant retries `attempts` times with `delay` seconds between tries.

    Returns True if the tree is gone (or never existed), False if it still
    exists after the final attempt. Never raises.
    """
    if not os.path.exists(path):
        return True
    for i in range(attempts):
        try:
            shutil.rmtree(path)
        except OSError:
            pass
        if not os.path.exists(path):
            return True
        if i < attempts - 1:
            time.sleep(delay)
    return not os.path.exists(path)


def clean_stale(temp_root=None, max_age_hours=1.0):
    """Delete stale rrcat_* dirs and officecli-*.lock files from a temp dir.

    Scans temp_root (default: tempfile.gettempdir()) for:
      - directories whose name starts with "rrcat_" (regression temp dirs)
      - files whose name starts with "officecli-" and ends with ".lock"

    Only entries whose mtime is OLDER than max_age_hours are deleted; anything
    younger is left untouched because another run may be active right now.

    Returns the number of entries removed.
    """
    temp_root = temp_root or tempfile.gettempdir()
    cutoff = time.time() - max_age_hours * 3600.0
    removed = 0
    try:
        entries = os.listdir(temp_root)
    except OSError:
        return 0
    for name in entries:
        full = os.path.join(temp_root, name)
        try:
            is_dir = os.path.isdir(full)
        except OSError:
            continue
        is_target = (is_dir and name.startswith("rrcat_")) or (
            not is_dir
            and os.path.isfile(full)
            and name.startswith("officecli-")
            and name.endswith(".lock")
        )
        if not is_target:
            continue
        try:
            mtime = os.path.getmtime(full)
        except OSError:
            continue
        if mtime >= cutoff:
            continue  # too young - another run may be active
        try:
            if is_dir:
                shutil.rmtree(full)
            else:
                os.remove(full)
            removed += 1
        except OSError:
            pass
    return removed
