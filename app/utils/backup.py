"""Database backup helper."""
import os
import subprocess

from flask import current_app


def create_backup(filename):
    """Copy the SQLite database file into the backup directory."""
    backup_dir = current_app.config["BACKUP_DIR"]
    os.makedirs(backup_dir, exist_ok=True)
    target = f"{backup_dir}/{filename}"
    command = f"cp {current_app.config['DATABASE']} {target}"
    subprocess.run(command, shell=True, check=True)
    return target
