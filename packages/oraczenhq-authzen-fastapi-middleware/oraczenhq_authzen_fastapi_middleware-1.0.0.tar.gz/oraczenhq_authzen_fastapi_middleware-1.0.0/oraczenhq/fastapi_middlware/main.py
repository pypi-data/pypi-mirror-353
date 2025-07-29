import base64
import time

import httpx
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from fastapi import Request
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from pydantic import BaseModel


class JWTUser(BaseModel):
    iss: str
    role: str
    sessionId: str
    sub: str
    type: str


class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        jwks_url: str,
        cookie_name: str = "access_token",
        audience: str = None,
        issuer: str = None,
    ):
        super().__init__(app)
        self.jwks_url = jwks_url
        self.audience = audience
        self.issuer = issuer
        self.jwks = None
        self.cookie_name = cookie_name
        self.expiration_grace_period = 300  # 5 minutes

    async def get_jwks(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            return response.json()

    def get_key(self, kid=None):
        """
        Get key by key ID if provided, otherwise return the first key
        """
        if not self.jwks:
            return None

        if kid:
            for key in self.jwks["keys"]:
                if key["kid"] == kid:
                    return key

        # Fallback to first key if no matching kid or kid wasn't provided
        return self.jwks["keys"][0] if self.jwks["keys"] else None

    def construct_rsa_public_key(self, jwk):
        """
        Construct RSA public key from JWK
        """
        if jwk["kty"] != "RSA":
            raise ValueError("Not an RSA key")

        # Base64url decode the modulus and exponent
        def base64url_to_int(val):
            padded = val + "=" * (4 - len(val) % 4) if len(val) % 4 else val
            decoded = base64.urlsafe_b64decode(padded)
            return int.from_bytes(decoded, byteorder="big")

        n = base64url_to_int(jwk["n"])
        e = base64url_to_int(jwk["e"])

        # Create RSA public numbers and public key
        public_numbers = RSAPublicNumbers(e=e, n=n)
        public_key = public_numbers.public_key(default_backend())

        # Return key in PEM format as expected by jose.jwt
        from cryptography.hazmat.primitives import serialization

        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return pem.decode("utf-8")

    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        request.state.authenticated = False

        token = request.cookies.get(self.cookie_name)

        # Optional: also check Authorization header if cookie is missing
        if not token and "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix

        if not token:
            # No token provided, continue without authentication
            return await call_next(request)

        try:
            # Load JWKS once and reuse
            if not self.jwks:
                self.jwks = await self.get_jwks()

            # Extract the header without verification to get the kid
            header = jwt.get_unverified_header(token)
            kid = header.get("kid")

            # Get the key corresponding to the kid in the token
            jwk = self.get_key(kid)

            if not jwk:
                return JSONResponse(
                    status_code=401, content={"detail": "Invalid token: Key not found"}
                )

            # Construct the public key from JWK
            public_key = self.construct_rsa_public_key(jwk)

            current_time = int(time.time())

            # Decode and verify the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_exp": False,
                    "verify_aud": bool(self.audience),
                    "verify_iss": bool(self.issuer),
                },
            )

            if "exp" in payload:
                expiration_time = payload["exp"]
                time_since_expiration = current_time - expiration_time

                if time_since_expiration > self.expiration_grace_period:
                    return await call_next(request)

            # Store user information in request state for access in route handlers
            request.state.user = JWTUser(**payload)
            request.state.authenticated = True

        except Exception:
            return await call_next(request)

        # Proceed to the route handler with authenticated request
        return await call_next(request)
