from flask_login import UserMixin
import os
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, username, email, dn=None, profile_image=None):
        self.id = username
        self.username = username
        self.email = email
        self.dn = dn  # Active Directory Distinguished Name
        self.profile_image = profile_image
        self._password = None  # Şifre değişikliği için geçici alan
    
    def set_password(self, password):
        """Şifreyi hash'leyerek saklar (Active Directory şifre değişikliği için)"""
        self._password = generate_password_hash(password)
    
    def check_password(self, password):
        """Şifre kontrolü (yerel doğrulama için)"""
        if self._password:
            return check_password_hash(self._password, password)
        return False
    
    def get_id(self):
        """Flask-Login için kullanıcı ID'sini döndürür"""
        return self.id

class UserRepository:
    """Kullanıcı verilerini yönetmek için repository sınıfı"""
    _users = {}  # Kullanıcıları bellekte saklamak için sözlük (gerçek uygulamada veritabanı kullanılmalı)
    
    @classmethod
    def add_user(cls, user):
        """Kullanıcıyı repository'ye ekler"""
        cls._users[user.id] = user
    
    @classmethod
    def get_user(cls, user_id):
        """Kullanıcı ID'sine göre kullanıcıyı getirir"""
        return cls._users.get(user_id)
    
    @classmethod
    def update_user(cls, user):
        """Kullanıcı bilgilerini günceller"""
        if user.id in cls._users:
            cls._users[user.id] = user
            return True
        return False