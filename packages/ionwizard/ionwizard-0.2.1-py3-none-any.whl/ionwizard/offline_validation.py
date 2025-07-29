import os
import sys
import json
import base64
import shutil
import pathlib
import platformdirs
from typing import Any
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError


def get_license_key_path() -> pathlib.Path:
    return (
        pathlib.Path(platformdirs.user_config_dir("ionworks")) / "ionworks_license_key"
    )


class VerifyOfflineLicense:
    @staticmethod
    def install_offline_license(file_name: str):
        if os.path.exists(file_name):
            shutil.copyfile(file_name, get_license_key_path())
        else:
            m = f"{file_name} does not exist"
            raise FileNotFoundError(m)

    @classmethod
    def verify_offline(cls) -> dict[str, Any]:
        return cls.verify_license(
            cls.decode_license(cls.get_license_file(get_license_key_path()))
        )

    @staticmethod
    def verify_license(decoded_license: dict[str, Any]) -> dict[str, Any]:
        try:
            verify_key = VerifyKey(
                bytes.fromhex(os.environ["IONWORKS_OFFLINE_PUBLIC_KEY"]),
            )
            verify_key.verify(
                f"license/{decoded_license['enc']}".encode(),
                base64.b64decode(decoded_license["sig"]),
            )
            return {"success": True, "message": "License key is valid"}
        except (ValueError, AssertionError, BadSignatureError):
            pass
        return {"success": False, "message": "Error: Failed to validate license key"}

    @staticmethod
    def decode_license(license_file: str) -> dict[str, Any]:
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
            raise FileNotFoundError("License key file not found.\n")
        return license_file
