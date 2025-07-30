import os
import sys
import json
import base64
import shutil
import pathlib
import platformdirs
import ionwizard
import datetime as dt
import dateutil.parser as du
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey, InvalidTag


def get_license_key_path() -> pathlib.Path:
    return (
        pathlib.Path(platformdirs.user_config_dir("ionworks")) / "ionworks_license_key"
    )


def get_signing_key() -> str:
    return ionwizard.validate.read_config_file().get("signature", "")


class VerifyOfflineLicense:
    @staticmethod
    def install_offline_license(file_name: str):
        if os.path.exists(file_name):
            shutil.copyfile(file_name, get_license_key_path())
        else:
            sys.tracebacklimit = 0
            print("")
            m = f"{file_name} does not exist"
            raise FileNotFoundError(m)

    @classmethod
    def validate_offline(cls, library_name: str) -> dict[str, bool | str]:
        if not cls.verify_offline():
            return {
                "success": False,
                "message": "Error: Failed to validate license key.",
            }
        license_data = cls.decrypt_license_data_for(library_name)
        if not license_data:
            return {"success": False, "message": "Error: Could not decrypt license."}
        elif cls.check_for_expiration(license_data):
            return {"success": False, "message": "Error: License is expired."}
        else:
            return {"success": True, "message": "License key is valid."}

    @classmethod
    def verify_offline(cls) -> bool:
        return cls.verify_license(
            cls.decode_license(cls.get_license_file(get_license_key_path()))
        )

    @staticmethod
    def verify_license(decoded_license: dict[str, str | bool | dict]) -> bool:
        signing_key = get_signing_key()
        try:
            verify_key = VerifyKey(bytes.fromhex(signing_key))
            verify_key.verify(
                f"license/{decoded_license['enc']}".encode(),
                base64.b64decode(decoded_license["sig"]),
            )
            return True
        except (ValueError, AssertionError, BadSignatureError):
            return False

    @staticmethod
    def decode_license(license_file: str) -> dict[str, str | bool | dict]:
        payload = license_file.replace("-----BEGIN LICENSE FILE-----\n", "")
        payload.replace("-----END LICENSE FILE-----\n", "")
        data = json.loads(base64.b64decode(payload))
        alg = data["alg"]
        if alg != "aes-256-gcm+ed25519":
            sys.tracebacklimit = 0
            print("")
            raise RuntimeError("License must be encoded with the ED25519 algorithm.")
        return data

    @staticmethod
    def get_license_file(license_path: str | pathlib.Path) -> str:
        if pathlib.Path(license_path).exists():
            with open(license_path) as f:
                license_file = f.read()
        else:
            sys.tracebacklimit = 0
            print("")
            raise FileNotFoundError(
                "License key file not found.\n"
                "Please check that the offline license key file was installed with the library.\n"
            )
        return license_file

    @classmethod
    def decrypt_license_data_for(
        cls, library_name: str
    ) -> dict[str, str | bool | dict]:
        decoded_license_file = cls.decode_license(
            cls.get_license_file(get_license_key_path())
        )
        license_key = ionwizard.validate.get_library_key(library_name)
        if not license_key:
            sys.tracebacklimit = 0
            print("")
            raise FileNotFoundError(
                "License key not found.\n"
                "Please check that license key was included in the licence YAML file.\n"
            )
        return cls.decrypt_license_data(decoded_license_file, license_key)

    @classmethod
    def decrypt_license_data(cls, decoded_license_file, license_key):
        key = cls.process_key(license_key)
        return cls.decode_license_data(decoded_license_file, key)

    @classmethod
    def check_for_expiration(cls, plaintext: dict[str, str | bool | dict]) -> bool:
        expiration_date = plaintext["data"]["attributes"].get("expiry")
        if expiration_date:
            current_date = dt.datetime.now(tz=dt.timezone.utc)
            expiration_date = du.parse(expiration_date)
            return current_date > expiration_date
        return False

    @classmethod
    def process_key(cls, license_key: str) -> bytes:
        digest = hashes.Hash(hashes.SHA256(), default_backend())
        digest.update(license_key.encode())
        key = digest.finalize()
        return key

    @classmethod
    def decode_license_data(
        cls, decoded_license_file: dict[str, str | bool | dict], key: bytes
    ) -> dict[str, str | bool | dict]:
        try:
            ciphertext, iv, tag = map(
                lambda p: base64.b64decode(p),
                decoded_license_file["enc"].split("."),
            )
            aes = Cipher(
                algorithms.AES(key),
                modes.GCM(iv, None, len(tag)),
                default_backend(),
            )
            dec = aes.decryptor()
            plaintext = dec.update(ciphertext) + dec.finalize_with_tag(tag)
            plaintext = json.loads(plaintext.decode())
            return plaintext
        except (InvalidKey, InvalidTag):
            return {}
