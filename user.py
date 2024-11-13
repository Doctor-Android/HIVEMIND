import hashlib
import os

class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = self._hash_password(password)
        self.profile_data = {}
        self.privacy_settings = {
            "visibility": "private",
            "data_sharing": False
        }
        self.friends = set()

    def _hash_password(self, password):
        salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return salt + pwd_hash

    def authenticate(self, password):
        salt = self.password_hash[:16]
        stored_hash = self.password_hash[16:]
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return pwd_hash == stored_hash

    def update_profile(self, profile_data):
        self.profile_data.update(profile_data)
        print(f"Profile updated for {self.username}")

    def set_privacy_settings(self, visibility=None, data_sharing=None):
        if visibility:
            self.privacy_settings["visibility"] = visibility
        if data_sharing is not None:
            self.privacy_settings["data_sharing"] = data_sharing
        print(f"Privacy settings updated for {self.username}")

    def get_profile(self, requester=None):
        if self.privacy_settings["visibility"] == "private":
            return {"username": self.username}
        elif self.privacy_settings["visibility"] == "friends-only":
            if requester in self.friends:
                return {"username": self.username, "profile_data": self.profile_data}
            else:
                return {"username": self.username, "profile_data": "Limited data"}
        else:
            return {"username": self.username, "profile_data": self.profile_data}

    def add_friend(self, friend_username):
        self.friends.add(friend_username)
        print(f"{friend_username} added as a friend.")

    def remove_friend(self, friend_username):
        if friend_username in self.friends:
            self.friends.remove(friend_username)
            print(f"{friend_username} removed from friends.")
        else:
            print(f"{friend_username} is not in the friend list.")

    def list_friends(self):
        return list(self.friends)