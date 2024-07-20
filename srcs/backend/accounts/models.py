from django.db import models
from dataclasses import dataclass

# Create your models here.

@dataclass
class OauthTokenResponse:
    access_token: str
    token_type: str
    expires_in: int
    scope: str
    created_at: int

    def to_dict(self):
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'expires_in': self.expires_in,
            'scope': self.scope,
            'created_at': self.created_at,
        }
