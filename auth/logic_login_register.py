import json
import os

from auth.validators import validate_username, validate_email, validate_password

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'users_db.json')


def load_users():
    """Baca data user dari file JSON. Jika file belum ada, kembalikan dict kosong."""
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users):
    """Simpan data user ke file JSON."""
    with open(DB_PATH, 'w') as f:
        json.dump(users, f, indent=2)


def register_user(username, email, password):
    """Daftarkan user baru setelah lolos validasi dan pengecekan duplikat."""
    if not validate_username(username):
        return False, "Username harus 3-20 karakter"
    if not validate_email(email):
        return False, "Format email tidak valid"
    if not validate_password(password):
        return False, "Password minimal 6 karakter"

    users = load_users()

    if username in users:
        return False, "Username sudah terdaftar"

    for user_data in users.values():
        if user_data.get('email') == email:
            return False, "Email sudah digunakan"

    users[username] = {"email": email, "password": password}
    save_users(users)
    return True, "Registrasi berhasil"


def login_user(identifier, password):
    """
    Login dengan username ATAU email.
    `identifier` bisa berupa username atau email.
    """
    users = load_users()
    print(f"[DEBUG LOGIN] Mencari identifier: '{identifier}'")
    print(f"[DEBUG LOGIN] Daftar username: {list(users.keys())}")

    if identifier in users:
        user = users[identifier]
        if user['password'] == password:
            return True, "Login berhasil"
        else:
            return False, "Password salah"

    for username, user_data in users.items():
        if user_data.get('email') == identifier:
            if user_data['password'] == password:
                return True, "Login berhasil"
            else:
                return False, "Password salah"

    return False, "Username atau email tidak ditemukan"
