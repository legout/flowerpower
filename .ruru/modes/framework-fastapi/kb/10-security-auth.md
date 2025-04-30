# 10. Security & Authentication

## Core Concept: Protecting API Endpoints

Securing an API involves verifying the identity of the client (**Authentication**) and controlling what actions the authenticated client is allowed to perform (**Authorization**). FastAPI provides tools and leverages dependency injection to implement various security schemes.

**Key Security Areas:**

-   **Authentication:** Verifying who the user is (e.g., via username/password, API keys, tokens like JWT or OAuth2).
-   **Authorization:** Determining if the authenticated user has permission to perform the requested action.
-   **Data Validation:** Preventing invalid or malicious data injection (handled well by Pydantic - see `02-pydantic-models.md`).
-   **HTTPS:** Encrypting communication between client and server (typically handled at the deployment layer - Nginx, Load Balancer, etc.).
-   **Rate Limiting:** Preventing abuse by limiting request frequency (often via middleware or reverse proxy).
-   **CORS:** Configure `CORSMiddleware` correctly to restrict which origins can access your API (see `08-middleware.md`).
-   **Secrets Management:** Never hardcode secrets (`SECRET_KEY`, database passwords, API keys). Use environment variables or a secrets management system.
-   **Dependency Security:** Keep FastAPI and all dependencies updated (`pip list --outdated`, `pip install -U ...`).
-   **Input Sanitization:** Although Pydantic handles validation, be mindful of how data is used (e.g., avoid raw SQL queries if possible, use ORM parameterization).
-   **Password Hashing:** Always hash passwords using a strong, salted algorithm (e.g., bcrypt via `passlib`).

## Authentication with Dependency Injection

FastAPI typically handles authentication using its dependency injection system (`Depends`).

1.  **Define Security Scheme:** Import and instantiate a security scheme class from `fastapi.security` (e.g., `OAuth2PasswordBearer`, `HTTPBasic`, `APIKeyHeader`). This tells FastAPI how to find the credentials in the request and integrates with OpenAPI docs.
2.  **Create Dependency Function:** Write a dependency function (often `async def`) that takes the security scheme instance as its *own* dependency. This function contains the logic to validate the credentials (e.g., decode JWT, verify password, lookup API key) and fetch the user. It should raise `HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, ...)` if validation fails.
3.  **Inject Dependency:** Add the dependency function to path operations or routers that require authentication using `Depends`.

**Example: OAuth2 Password Bearer Flow (JWT)**

This is a common flow where a user exchanges username/password for a short-lived JWT access token, which is then sent in the `Authorization: Bearer <token>` header for subsequent requests.

```python
# --- Setup (e.g., in security.py) ---
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt # Using python-jose for JWT handling (pip install python-jose[cryptography])
from passlib.context import CryptContext # For password hashing (pip install passlib[bcrypt])
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
import os

# Configuration (Use environment variables!)
SECRET_KEY = os.environ.get("SECRET_KEY", "a_very_secret_key") # CHANGE THIS!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # Points to the /token login endpoint

# Helper Functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to decode token and get user (simplified)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub") # 'sub' is standard claim for subject (username)
        if username is None:
            raise credentials_exception
        # In real app: Fetch user from DB based on username
        # user = await crud.get_user_by_username(db_session, username=username)
        # if user is None: raise credentials_exception
        # return user # Return DB model or Pydantic schema instance
        return {"username": username} # Simplified return
    except JWTError:
        raise credentials_exception

CurrentUserDep = Annotated[dict, Depends(get_current_user)] # Use your User schema

# --- Login Endpoint (e.g., in routers/auth.py) ---
# Assume schemas.Token exists: class Token(BaseModel): access_token: str; token_type: str
# Assume schemas.User exists
# Assume crud.authenticate_user(db, username, password) exists and returns User or None

# @router.post("/token", response_model=schemas.Token)
# async def login_for_access_token(
#     form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
#     db: SessionDep # Assuming DB session dependency
# ):
#     user = await crud.authenticate_user(db, username=form_data.username, password=form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Incorrect username or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token = create_access_token(data={"sub": user.username})
#     return {"access_token": access_token, "token_type": "bearer"}

# --- Protecting Endpoints ---
# @app.get("/users/me", response_model=schemas.User)
# async def read_users_me(current_user: CurrentUserDep):
#     # If token is invalid/missing, get_current_user raises HTTPException
#     return current_user
```

## Authorization

Authorization (checking *permissions*) is typically handled *after* authentication, often within the same dependency or a separate one that depends on `get_current_user`.

-   **Inside Path Operations:** Check user roles/permissions within the path operation function after getting the `current_user`.
-   **In Dependencies:** Create dependencies that check for specific roles or permissions and raise `HTTPException(status.HTTP_403_FORBIDDEN)` if the check fails. Apply these dependencies to relevant path operations or routers.

```python
async def require_admin(current_user: CurrentUserDep):
    # In real app, check user.role or user.permissions from the user object
    if current_user.get("username") != "admin": # Simplified check
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user

AdminDep = Annotated[dict, Depends(require_admin)] # Use User schema

# @app.delete("/admin/resource")
# async def delete_resource(admin_user: AdminDep):
#     # This endpoint requires admin privileges via the dependency
#     return {"message": "Resource deleted"}
```

## General Security Best Practices

-   **HTTPS:** Always use HTTPS in production.
-   **Input Validation:** Use Pydantic models rigorously.
-   **Authentication:** Implement robust authentication (e.g., OAuth2 Bearer with JWT).
-   **Authorization:** Implement checks for permissions/roles.
-   **Password Hashing:** Use `passlib` with bcrypt.
-   **Secrets Management:** Use environment variables or a secrets manager.
-   **Rate Limiting:** Protect against brute-force attacks.
-   **CORS:** Configure `CORSMiddleware` appropriately.
-   **SQL Injection:** Use ORMs (like SQLModel) with parameterized queries. Avoid raw SQL if possible.
-   **Keep Dependencies Updated.**
-   **Error Handling:** Don't expose sensitive information in error messages.

FastAPI's security tools and dependency injection make implementing authentication and authorization straightforward. Define security schemes, create dependencies to verify credentials/tokens and check permissions, and apply these dependencies to your path operations or routers.