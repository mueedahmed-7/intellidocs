import re

from passlib.context import CryptContext

from database.mongodb import users_collection


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


class AuthService:

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )

    @staticmethod
    def register_user(
        name: str,
        email: str,
        password: str,
    ):

        email = AuthService.normalize_email(email)

        # Check whether user already exists
        existing_user = users_collection.find_one(
            {"email": email}
        )

        if existing_user:
            raise ValueError(
                "User with this email already exists."
            )

        hashed_password = AuthService.hash_password(
            password
        )

        user = {
            "name": name.strip(),
            "email": email,
            "password": hashed_password,
        }

        result = users_collection.insert_one(user)

        return {
            "id": str(result.inserted_id),
            "name": user["name"],
            "email": user["email"],
        }