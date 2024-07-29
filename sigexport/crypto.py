# Modified from:
# https://gist.github.com/flatz/3f242ab3c550d361f8c6d031b07fb6b1

import json
import subprocess
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Hash import SHA1
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from typer import Exit, colors, secho


def get_key(file: Path) -> str:
    with open(file, encoding="utf-8") as f:
        data = json.loads(f.read())
    if "key" in data:
        return data["key"]
    elif "encryptedKey" in data:
        if sys.platform == "darwin":
            try:
                pw = get_password()
                return decrypt(pw, data["encryptedKey"])
            except Exception:
                secho("Failed to decrypt Signal password", fg=colors.RED)
                raise Exit(1)
        else:
            secho(
                "Your Signal data key is encrypted, and descrypting"
                "it is currently only supported on macOS",
                fg=colors.RED,
            )
            raise Exit(1)

    secho("No Signal decryption key found", fg=colors.RED)
    raise Exit(1)


def get_password() -> str:
    cmd = ["security", "find-generic-password", "-ws", "Signal Safe Storage"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")  # NoQA: S603
    pw = p.stdout
    return pw.strip()


def decrypt(password: str, encrypted_key: str) -> str:
    encrypted_key_b = bytes.fromhex(encrypted_key)
    prefix = b"v10"
    if not encrypted_key_b.startswith(prefix):
        raise
    encrypted_key_b = encrypted_key_b[len(prefix) :]

    salt = b"saltysalt"
    key = PBKDF2(password, salt=salt, dkLen=128 // 8, count=1003, hmac_hash_module=SHA1)
    iv = b" " * 16
    aes_decrypted = AES.new(key, AES.MODE_CBC, iv).decrypt(encrypted_key_b)
    decrypted_key = unpad(aes_decrypted, block_size=16).decode("ascii")
    return decrypted_key
