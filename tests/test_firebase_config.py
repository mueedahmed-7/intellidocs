"""Credential-source tests that never load or expose a real Firebase key."""

import unittest
from pathlib import Path

from backend.database.firebase_config import FirebaseConfigurationError, resolve_firebase_credential


class FirebaseConfigurationTests(unittest.TestCase):
    def test_environment_json_is_preferred_for_hosted_deployments(self):
        received = []
        result = resolve_firebase_credential(
            lambda value: received.append(value) or "environment-credential",
            environment={
                "FIREBASE_CREDENTIALS_JSON": '{"type":"service_account","project_id":"safe-test"}',
                "GOOGLE_APPLICATION_CREDENTIALS": "ignored-local-key.json",
            },
            project_root=Path("C:/project"),
        )
        self.assertEqual(result, "environment-credential")
        self.assertEqual(received, [{"type": "service_account", "project_id": "safe-test"}])

    def test_local_file_path_is_used_when_environment_json_is_absent(self):
        received = []
        result = resolve_firebase_credential(
            lambda value: received.append(value) or "local-credential",
            environment={"GOOGLE_APPLICATION_CREDENTIALS": "private/service-account.json"},
            project_root=Path("C:/project"),
        )
        self.assertEqual(result, "local-credential")
        self.assertEqual(received, [Path("C:/project/private/service-account.json")])

    def test_malformed_environment_json_is_safe_configuration_error(self):
        with self.assertRaisesRegex(FirebaseConfigurationError, "must contain valid JSON") as error:
            resolve_firebase_credential(
                lambda value: value,
                environment={"FIREBASE_CREDENTIALS_JSON": "{not-valid-json"},
                project_root=Path("C:/project"),
            )
        self.assertNotIn("{not-valid-json", str(error.exception))

    def test_missing_credential_sources_are_rejected(self):
        with self.assertRaisesRegex(FirebaseConfigurationError, "No Firebase credentials configured"):
            resolve_firebase_credential(
                lambda value: value,
                environment={},
                project_root=Path("C:/project"),
            )
