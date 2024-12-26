from models.models import User
from services.database import db

def create_user(user: dict) -> User:
    User(
            active=True,
            userName=user["preferred_username"],
            givenName=user["given_name"],
            middleName=user["middle_name"],
            familyName=user["family_name"],
            displayName=user["name"],
            locale=user["locale"],
            externalId=user["sub"],
    ).save()

def create_user_from_profile_token(token: dict) -> User:
    user = User(
            active=True,
            userName=token.get("preferred_username") or token.get("email"),
            givenName=token.get("given_name"),
            middleName=token.get("middle_name"),
            familyName=token.get("family_name"),
            displayName=token.get("name"),
            locale=token.get("locale"),
            externalId=token.get("sub"),
    )
    db.session.add(user)
    db.session.commit()

    return user


def get_user_by_id(id: str) -> User:
    return User.query.get(id)