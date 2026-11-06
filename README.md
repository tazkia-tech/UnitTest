# Unit Test & Integration Test — Login/Register (Flask)

Contoh praktik pengujian perangkat lunak untuk materi **Uji Unit dan Uji Integrasi**.

## Struktur

```
.
├── app.py
├── auth
│   ├── __init__.py
│   ├── logic_login_register.py
│   └── validators.py
├── templates
│   ├── login.html
│   └── register.html
├── tests
│   ├── __init__.py
│   ├── test_auth_logic.py
│   └── test_validation.py
└── users_db.json
```

| Kode yang diuji | Jenis pengujian | File test |
|---|---|---|
| `auth/validators.py` | Unit test | `tests/test_validation.py` |
| `auth/logic_login_register.py` (+ validators + file JSON) | Integration test | `tests/test_auth_logic.py` |

## Menjalankan

```bash
pip install -r requirements.txt

# Unit test
python3 -m unittest tests.test_validation -v

# Integration test
python3 -m unittest tests.test_auth_logic -v

# Semua test
python3 -m unittest discover -s tests -t . -v

# Jalankan aplikasi web
python3 app.py   # buka http://127.0.0.1:5000
```

Integration test memakai `unittest.mock.patch` untuk mengganti `DB_PATH` ke `test_users_db.json`,
sehingga data asli di `users_db.json` tidak tersentuh. File sementara dihapus di `setUp`/`tearDown`.

## Skenario Pengujian

### Unit test — `tests/test_validation.py`

Menguji fungsi di `auth/validators.py` secara terpisah (tanpa file JSON, tanpa Flask).

| Fungsi | Input | Hasil yang diharapkan | Jenis skenario |
|---|---|---|---|
| `validate_username` | `"uwais_alqarni"` | `True` | ✅ Sukses |
| `validate_username` | `"ab"` (2 karakter) | `False` | ❌ Gagal — terlalu pendek |
| `validate_username` | `"a" * 21` (21 karakter) | `False` | ❌ Gagal — terlalu panjang |
| `validate_username` | `123` (bukan string) | `False` | ❌ Gagal — tipe data salah |
| `validate_email` | `"test@example.com"` | `True` | ✅ Sukses |
| `validate_email` | `"invalid-email"` | `False` | ❌ Gagal — tanpa `@` |
| `validate_email` | `"test@"` | `False` | ❌ Gagal — tanpa domain |
| `validate_email` | `123` | `False` | ❌ Gagal — tipe data salah |
| `validate_password` | `"123456"` | `True` | ✅ Sukses |
| `validate_password` | `"12345"` (5 karakter) | `False` | ❌ Gagal — kurang dari 6 karakter |
| `validate_password` | `""` | `False` | ❌ Gagal — kosong |
| `validate_password` | `123` | `False` | ❌ Gagal — tipe data salah |

> Skenario "gagal" di atas artinya **input ditolak oleh validator**. Test-nya sendiri tetap **lulus (ok)**,
> karena memang itu perilaku yang diharapkan (`assertFalse`).

### Integration test — `tests/test_auth_logic.py`

Menguji `auth/logic_login_register.py` bersama validator dan file JSON.

| Test | Langkah | Hasil yang diharapkan | Jenis skenario |
|---|---|---|---|
| `test_register_success` | Register `alice` / `alice@example.com` / `123456` | `(True, "Registrasi berhasil")` | ✅ Sukses |
| `test_register_duplicate_username` | Register `bob`, lalu register `bob` lagi dengan email lain | `(False, "Username sudah terdaftar")` | ❌ Gagal — username duplikat |
| `test_register_duplicate_email` | Register `charlie`, lalu `dave` dengan email yang sama | `(False, "Email sudah digunakan")` | ❌ Gagal — email duplikat |
| `test_login_success` | Register `eve`, lalu login `eve` / `123456` | `(True, "Login berhasil")` | ✅ Sukses |
| `test_login_wrong_password` | Register `frank`, lalu login dengan `wrongpass` | `(False, "Password salah")` | ❌ Gagal — password salah |
| `test_login_user_not_found` | Login `nonexistent` tanpa register | `(False, "Username atau email tidak ditemukan")` | ❌ Gagal — user tidak ada |

### Contoh output saat semua test lulus

```
test_validate_email (tests.test_validation.TestValidators.test_validate_email) ... ok
test_validate_password (tests.test_validation.TestValidators.test_validate_password) ... ok
test_validate_username (tests.test_validation.TestValidators.test_validate_username) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.000s

OK
```

## Cara Membuat Test Gagal (Simulasi)

Untuk melihat bagaimana unit test **mendeteksi bug**, ubah sementara salah satu kode di bawah,
jalankan test, lalu **kembalikan seperti semula**.

> Tips: jalankan dengan `python3 -B ...` atau hapus folder `__pycache__` setelah mengubah kode,
> supaya Python tidak memakai cache lama.

### Simulasi 1 — Bug di validator (unit test gagal)

Ubah aturan password di `auth/validators.py` dari minimal 6 menjadi minimal 8 karakter:

```python
# sebelum
return isinstance(password, str) and len(password) >= 6
# sesudah (bug disengaja)
return isinstance(password, str) and len(password) >= 8
```

Jalankan `python3 -B -m unittest tests.test_validation -v`:

```
test_validate_email ... ok
test_validate_password ... FAIL
test_validate_username ... ok

======================================================================
FAIL: test_validate_password (tests.test_validation.TestValidators.test_validate_password)
----------------------------------------------------------------------
Traceback (most recent call last):
  File ".../tests/test_validation.py", line 21, in test_validate_password
    self.assertTrue(validate_password("123456"))
AssertionError: False is not true

----------------------------------------------------------------------
Ran 3 tests in 0.000s

FAILED (failures=1)
```

**Artinya:** password `"123456"` seharusnya valid, tapi validator menolaknya.

Bug yang sama juga membuat **integration test** ikut gagal (5 dari 6), karena semua test di sana
mendaftarkan user dengan password `"123456"`. Ini contoh bagaimana bug di satu unit
merambat ke modul lain yang memakainya:

```
AssertionError: 'Password minimal 6 karakter' != 'Username sudah terdaftar'
...
FAILED (failures=5)
```

### Simulasi 2 — Pesan error berubah (integration test gagal)

Ubah pesan di `auth/logic_login_register.py` (ada 2 tempat):

```python
return False, "Password salah"    # sebelum
return False, "Password keliru"   # sesudah (bug disengaja)
```

Jalankan `python3 -B -m unittest tests.test_auth_logic -v`:

```
======================================================================
FAIL: test_login_wrong_password (tests.test_auth_logic.TestAuthLogic.test_login_wrong_password)
----------------------------------------------------------------------
  File ".../tests/test_auth_logic.py", line 51, in test_login_wrong_password
    self.assertEqual(msg, "Password salah")
AssertionError: 'Password keliru' != 'Password salah'
- Password keliru
+ Password salah

----------------------------------------------------------------------
Ran 6 tests in 0.002s

FAILED (failures=1)
```

**Artinya:** baris `-` adalah nilai yang **dihasilkan kode**, baris `+` adalah nilai yang **diharapkan test**.

### Simulasi 3 — Ekspektasi test yang salah

Bisa juga test-nya yang dibuat salah, misalnya di `tests/test_validation.py`:

```python
self.assertTrue(validate_username("ab"))   # seharusnya assertFalse
```

Hasilnya `AssertionError: False is not true`. Jadi saat test gagal, periksa dua kemungkinan:
**kodenya yang salah**, atau **ekspektasi test-nya yang salah**.

### Ringkasan status hasil test

| Status | Arti |
|---|---|
| `ok` | Hasil sesuai ekspektasi |
| `FAIL` | Assertion tidak terpenuhi (hasil ≠ ekspektasi) |
| `ERROR` | Terjadi exception tak terduga (mis. `ImportError`, `KeyError`) sebelum assertion selesai |
