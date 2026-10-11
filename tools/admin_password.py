#!/usr/bin/env python3
"""Make the ADMIN_USERS entry for an admin account of the photo admin page.

Prints one JSON object with a scrypt hash of the password (the password itself is never
stored). Put the objects for both accounts in a JSON list and paste it into the
ADMIN_USERS environment variable of the gallery-api Catalyst function, e.g.

    [{"username": "developer", ...}, {"username": "cutelook", ...}]

Usage: python3 tools/admin_password.py <username> <developer|client> "<Display name>"
       (the password is asked for and not shown)
"""
import getpass
import hashlib
import json
import os
import sys


def main():
    if len(sys.argv) != 4 or sys.argv[2] not in ("developer", "client"):
        sys.exit(__doc__)
    username, role, name = sys.argv[1].strip().lower(), sys.argv[2], sys.argv[3]
    password = getpass.getpass("Password (12+ characters): ")
    if len(password) < 12:
        sys.exit("Use at least 12 characters.")
    if password != getpass.getpass("Repeat password: "):
        sys.exit("Passwords do not match.")
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1, dklen=64)
    print(json.dumps({"username": username, "name": name, "role": role,
                      "salt": salt.hex(), "hash": digest.hex()}))


if __name__ == "__main__":
    main()
