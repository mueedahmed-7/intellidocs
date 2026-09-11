# import re

# from passlib.context import CryptContext

# from database.mongodb import users_collection


# pwd_context = CryptContext(
#     schemes=["bcrypt"],
#     deprecated="auto",
# )


# class AuthService:

#     @staticmethod
#     def normalize_email(email: str) -> str:
#         return email.strip().lower()

#     @staticmethod
#     def hash_password(password: str) -> str:
#         return pwd_context.hash(password)

#     @staticmethod
#     def verify_password(
#         plain_password: str,
#         hashed_password: str,
#     ) -> bool:
#         return pwd_context.verify(
#             plain_password,
#             hashed_password,
#         )

#     @staticmethod
#     def register_user(
#         name: str,
#         email: str,
#         password: str,
#     ):

#         email = AuthService.normalize_email(email)

#         # Check whether user already exists
#         existing_user = users_collection.find_one(
#             {"email": email}
#         )

#         if existing_user:
#             raise ValueError(
#                 "User with this email already exists."
#             )

#         hashed_password = AuthService.hash_password(
#             password
#         )

#         user = {
#             "name": name.strip(),
#             "email": email,
#             "password": hashed_password,
#         }

#         result = users_collection.insert_one(user)

#         return {
#             "id": str(result.inserted_id),
#             "name": user["name"],
#             "email": user["email"],
#         }
#     @staticmethod
#     def login_user(
#         email: str,
#         password: str,
#     ):
#         email = AuthService.normalize_email(email)

#         # Find user
#         user = users_collection.find_one(
#             {"email": email}
#         )

#         if not user:
#             raise ValueError(
#                 "Invalid email or password."
#             )

#         # Verify password
#         password_valid = AuthService.verify_password(
#             password,
#             user["password"],
#         )

#         if not password_valid:
#             raise ValueError(
#                 "Invalid email or password."
#             )

#         return {
#             "id": str(user["_id"]),
#             "name": user["name"],
#             "email": user["email"],
#         }
import bcrypt

from backend.database.firebase_db import users_collection


MAX_BCRYPT_PASSWORD_BYTES = 72


class DuplicateEmailError(ValueError):
    """Raised when an account already uses the requested email."""


class InvalidCredentialsError(ValueError):
    """Raised for either an unknown email or an invalid password."""


class AuthStorageError(RuntimeError):
    """Raised when Firestore cannot complete an authentication operation."""


class AuthService:

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def hash_password(password: str) -> str:
        if len(password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            raise ValueError(
                "Password must be 72 bytes or fewer when UTF-8 encoded."
            )
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    @staticmethod
    def verify_password(
        plain_password: str,
        hashed_password: str,
    ) -> bool:
        if len(plain_password.encode("utf-8")) > MAX_BCRYPT_PASSWORD_BYTES:
            return False
        try:
            return bcrypt.checkpw(
                plain_password.encode("utf-8"),
                hashed_password.encode("utf-8"),
            )
        except ValueError:
            return False

    @staticmethod
    def register_user(
        name: str,
        email: str,
        password: str,
    ):

        email = AuthService.normalize_email(email)

        try:
            existing = list(
                users_collection.where("email", "==", email).limit(1).stream()
            )
        except Exception as error:
            raise AuthStorageError("Authentication service is temporarily unavailable.") from error

        if existing:
            raise DuplicateEmailError("An account with this email already exists.")

        hashed_password = AuthService.hash_password(password)

        user = {
            "name": name.strip(),
            "email": email,
            "password": hashed_password,
        }

        try:
            doc_ref = users_collection.document()
            doc_ref.set(user)
        except Exception as error:
            raise AuthStorageError("Authentication service is temporarily unavailable.") from error

        return {
            "id": doc_ref.id,
            "name": user["name"],
            "email": user["email"],
        }

    @staticmethod
    def login_user(
        email: str,
        password: str,
    ):
        email = AuthService.normalize_email(email)

        try:
            results = list(
                users_collection.where("email", "==", email).limit(1).stream()
            )
        except Exception as error:
            raise AuthStorageError("Authentication service is temporarily unavailable.") from error

        if not results:
            raise InvalidCredentialsError("Invalid email or password.")

        doc = results[0]
        user = doc.to_dict()

        password_valid = AuthService.verify_password(
            password,
            user["password"],
        )

        if not password_valid:
            raise InvalidCredentialsError("Invalid email or password.")

        return {
            "id": doc.id,
            "name": user["name"],
            "email": user["email"],
        }

    @staticmethod
    def get_user_by_id(user_id: str):
        try:
            doc = users_collection.document(user_id).get()
        except Exception as error:
            raise AuthStorageError("Authentication service is temporarily unavailable.") from error

        if not doc.exists:
            return None

        user = doc.to_dict()

        return {
            "id": doc.id,
            "name": user["name"],
            "email": user["email"],
        }
