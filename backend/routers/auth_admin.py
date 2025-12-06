# -----------------------------------------
# IMPORTS
# -----------------------------------------
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from passlib.hash import pbkdf2_sha256
import jwt, datetime
from db import get_conn

SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"

router = APIRouter(prefix="/admin/auth", tags=["Admin Auth"])

security = HTTPBearer()

# -----------------------------------------
# MODELS
# -----------------------------------------
class RegisterAdmin(BaseModel):
    name: str
    email: str
    password: str

class LoginAdmin(BaseModel):
    email: str
    password: str


# -----------------------------------------
# REGISTER ADMIN API
# -----------------------------------------
@router.post("/register")
def register_admin(data: RegisterAdmin):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id FROM admin_users WHERE email=%s", (data.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Admin already exists")

    hash_pw = pbkdf2_sha256.hash(data.password)

    cur.execute("""
        INSERT INTO admin_users (name, email, password_hash, role)
        VALUES (%s, %s, %s, 'ADMIN')
    """, (data.name, data.email, hash_pw))

    conn.commit()
    cur.close()
    conn.close()

    return {"success": True, "message": "Admin registered successfully"}


# -----------------------------------------
# LOGIN ADMIN API
# -----------------------------------------
@router.post("/login")
def login_admin(data: LoginAdmin):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM admin_users WHERE email=%s", (data.email,))
    admin = cur.fetchone()

    if not admin or not pbkdf2_sha256.verify(data.password, admin["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = jwt.encode({
        "id": admin["id"],
        "email": admin["email"],
        "role": admin["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, SECRET_KEY, algorithm="HS256")

    return {
        "success": True,
        "token": token,
        "admin": {
            "id": admin["id"],
            "name": admin["name"],
            "email": admin["email"],
            "role": admin["role"]
        }
    }


# =========================================================
# ✅ STEP 1.4 → Add get_current_admin HERE (under login API)
# =========================================================
def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, name, email, role FROM admin_users WHERE id=%s", (payload["id"],))
    admin = cur.fetchone()
    cur.close()
    conn.close()

    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin


# =========================================================
# ✅ STEP 1.5 → Protected Endpoint /admin/auth/me
# =========================================================
@router.get("/me")
def get_me(current_admin: dict = Depends(get_current_admin)):
    return {
        "success": True,
        "admin": current_admin
    }
