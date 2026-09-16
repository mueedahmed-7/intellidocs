"""Create the IntelliDocs PostgreSQL tables without changing existing data.

Run once after configuring DATABASE_URL:
    python -m backend.scripts.init_db
"""

from backend.database.postgres import init_database


def main() -> None:
    init_database()
    print("IntelliDocs database tables are ready.")


if __name__ == "__main__":
    main()
