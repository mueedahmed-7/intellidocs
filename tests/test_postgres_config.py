"""Configuration tests for the SQLAlchemy PostgreSQL connection URL."""

import unittest

from backend.database.postgres import database_url


class DatabaseUrlTests(unittest.TestCase):
    def test_postgresql_url_is_normalized_for_psycopg(self):
        value = database_url({"DATABASE_URL": "postgresql://user:password@db.example/app"})
        self.assertEqual(value, "postgresql+psycopg://user:password@db.example/app")

    def test_driver_qualified_url_is_preserved(self):
        value = database_url({"DATABASE_URL": "postgresql+psycopg://user:password@db.example/app"})
        self.assertEqual(value, "postgresql+psycopg://user:password@db.example/app")

    def test_missing_database_url_is_a_safe_configuration_error(self):
        with self.assertRaisesRegex(RuntimeError, "DATABASE_URL") as error:
            database_url({})
        self.assertNotIn("password", str(error.exception).lower())
