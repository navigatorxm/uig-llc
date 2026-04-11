"""Generate a bcrypt hash for the admin password.

Usage:
    python scripts/hash_password.py

Copy the output into your .env as ADMIN_PASSWORD_HASH=<hash>
"""
import getpass
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = getpass.getpass("Enter admin password: ")
confirm = getpass.getpass("Confirm admin password: ")

if password != confirm:
    print("ERROR: Passwords do not match.")
    raise SystemExit(1)

hashed = pwd_context.hash(password)
print(f"\nADMIN_PASSWORD_HASH={hashed}")
