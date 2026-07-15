#%%
# ------------------------------------------------------------
# Unit 7 - Secure Coding Practice
# ------------------------------------------------------------

"""
This task looks at a simple authentication system and the security
issues in the original design.

The original version:
- stores passwords in plaintext
- does not validate input
- does not enforce complexity rules
- does not limit failed login attempts
- does not log authentication attempts

"""


import hashlib
import hmac
import os
import re

# ------------------------------------------------------------
# Original Version
# ------------------------------------------------------------

class User:
    def __init__(self, username, password):
         self.username = username
         self.password = password


class AuthenticationSystem:
    def __init__(self):
        self.users = []

    def add_user(self, username, password):
        self.users.append(User(username, password))

    def authenticate(self, username, password):
        for user in self.users:
            if user.username == username and user.password == password:
                return True
        return False


# Usage
auth_system = AuthenticationSystem()
auth_system.add_user("admin", "admin123") # Weak password
auth_system.add_user("user1", "password") # Weak password

# Simulate an injection attack
malicious_input = "admin' OR '1'='1"

print(auth_system.authenticate(malicious_input, "anything"))
# Output: True (Vulnerable to SQL injection)


# ------------------------------------------------------------
# Refactored Version
# ------------------------------------------------------------

class SecureUser:
    def __init__(self, username, password_hash, salt):
        self.username = username
        self.password_hash = password_hash
        self.salt = salt


class AuthenticationSystem:
    def __init__(self):
        self.users = {}
        self.failed_attempts = {}

    def username_is_valid(self, username):
        return re.match(r"^[a-zA-Z0-9_]{3,20}$", username) is not None

    def password_is_valid(self, password):
        weak_passwords = ["password", "admin123", "letmein"]

        if len(password) < 9:
            return False

        if password.lower() in weak_passwords:
            return False

        has_letter = any(character.isalpha() for character in password)
        has_number = any(character.isdigit() for character in password)

        return has_letter and has_number

    def hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            310000
        )

    def add_user(self, username, password):
        if not self.username_is_valid(username):
            raise ValueError("Invalid username")

        if not self.password_is_valid(password):
            raise ValueError("Password does not meet policy requirements")

        salt = os.urandom(16)
        password_hash = self.hash_password(password, salt)

        self.users[username] = SecureUser(username, password_hash, salt)

    def authenticate(self, username, password):
        if not self.username_is_valid(username):
            print("SECURITY LOG: invalid username rejected")
            return False

        if self.failed_attempts.get(username, 0) >= 3:
            print(f"SECURITY LOG: login blocked for {username}")
            return False

        user = self.users.get(username)

        if user is None:
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            print(f"SECURITY LOG: failed login for unknown user {username}")
            return False

        entered_hash = self.hash_password(password, user.salt)

        if hmac.compare_digest(entered_hash, user.password_hash):
            self.failed_attempts[username] = 0
            print(f"SECURITY LOG: successful login for {username}")
            return True

        self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
        print(f"SECURITY LOG: failed login for {username}")
        return False


secure_auth = AuthenticationSystem()

try:
    secure_auth.add_user("admin", "admin123")
except ValueError as error:
    print(error)

secure_auth.add_user("admin_user", "Secure123")

print()
print("Secure version")
print("--------------")
print(secure_auth.authenticate("admin_user", "Secure123"))
print(secure_auth.authenticate("admin_user", "wrong"))
print(secure_auth.authenticate("admin_user", "wrong"))
print(secure_auth.authenticate("admin_user", "wrong"))
print(secure_auth.authenticate("admin_user", "Secure123"))

print()
print("Injection-style input test")
print("--------------------------")
print(secure_auth.authenticate("admin' OR '1'='1", "anything"))

# %%