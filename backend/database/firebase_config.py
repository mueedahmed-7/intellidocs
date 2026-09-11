"""Safe Firebase credential selection shared by local and hosted startup."""

import json
import os
from pathlib import Path
from typing import Callable, Mapping, TypeVar


Credential = TypeVar("Credential")


class FirebaseConfigurationError(RuntimeError):
    """A credential source is missing or malformed, without exposing secrets."""


def resolve_firebase_credential(
    certificate_factory: Callable[[dict | Path], Credential],
    *,
    environment: Mapping[str, str] | None = None,
    project_root: Path,
) -> Credential:
    """Prefer Render's JSON secret and otherwise use the local key-file path."""
    if environment is None:
        environment = os.environ
    credential_json = (environment.get("FIREBASE_CREDENTIALS_JSON") or "").strip()

    if credential_json:
        try:
            credential_data = json.loads(credential_json)
        except json.JSONDecodeError as error:
            raise FirebaseConfigurationError(
                "FIREBASE_CREDENTIALS_JSON must contain valid JSON."
            ) from error
        if not isinstance(credential_data, dict):
            raise FirebaseConfigurationError(
                "FIREBASE_CREDENTIALS_JSON must contain a Firebase service-account object."
            )
        try:
            return certificate_factory(credential_data)
        except Exception as error:
            raise FirebaseConfigurationError(
                "FIREBASE_CREDENTIALS_JSON is not a valid Firebase service-account credential."
            ) from error

    local_path = (environment.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    if not local_path:
        raise FirebaseConfigurationError(
            "No Firebase credentials configured. Set FIREBASE_CREDENTIALS_JSON for deployment "
            "or GOOGLE_APPLICATION_CREDENTIALS for local development."
        )

    credential_path = Path(local_path).expanduser()
    if not credential_path.is_absolute():
        credential_path = project_root / credential_path
    try:
        return certificate_factory(credential_path)
    except Exception as error:
        raise FirebaseConfigurationError(
            "The local Firebase credential file could not be loaded. Check GOOGLE_APPLICATION_CREDENTIALS."
        ) from error
