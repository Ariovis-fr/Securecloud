import uuid
from services.database import db
import datetime

class File(db.Model):
    __tablename__ = "files"

    id = db.Column(db.String(128), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(128), db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now())
    path = db.Column(db.String(128), nullable=False)
    
    def __init__(self, user_id, name, size, type, path):
        self.user_id = user_id
        self.name = name
        self.size = size
        self.type = type
        self.path = path

    def __repr__(self):
        return "<id {}>".format(self.id)
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "size": self.size,
            "type": self.type,
            "created_at": self.created_at,
            "url": 'download/' + self.id
        }

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(128), primary_key=True, default=uuid.uuid4)
    active = db.Column(db.Boolean)
    userName = db.Column(db.String(128), nullable=False, unique=True)
    name_givenName = db.Column(db.String(64))
    name_middleName = db.Column(db.String(64))
    name_familyName = db.Column(db.String(64))
    displayName = db.Column(db.String(64))
    locale = db.Column(db.String(64))
    files = db.relationship("File", backref="user", lazy=True)
    externalId = db.Column(db.String(64))

    def __init__(
        self,
        active,
        userName,
        givenName,
        middleName,
        familyName,
        displayName,
        locale,
        externalId,
    ):
        self.active = active
        self.userName = userName
        self.name_givenName = givenName
        self.name_middleName = middleName
        self.name_familyName = familyName
        self.displayName = displayName
        self.locale = locale
        self.externalId = externalId

    def __repr__(self):
        return "<id {}>".format(self.id)

    def serialize(self):
        return {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
            ],
            "id": self.id,
            "userName": self.userName,
            "name": {
                "givenName": self.name_givenName,
                "middleName": self.name_middleName,
                "familyName": self.name_familyName,
            },
            "displayName": self.displayName,
            "locale": self.locale,
            "externalId": self.externalId,
            "active": self.active,
            "meta": {
                "resourceType": "User",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2011-05-13T04:42:34Z",
            },
        }