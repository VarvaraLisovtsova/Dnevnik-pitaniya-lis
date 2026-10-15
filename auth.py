"""Модуль аутентификации."""

import hashlib
from database import DatabaseManager
from models import User


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def register_user(db, login, password, gender, birth_date,
                  height_cm, activity_level) -> bool:
    query = (
        "INSERT INTO Пользователи "
        "(Логин, ХешПароля, Пол, ДатаРождения, РостСм, УровеньАктивности, ДатаРегистрации) "
        "VALUES (?, ?, ?, ?, ?, ?, DATE('now'))"
    )
    result = db.execute(query, (login, hash_password(password),
                                gender, birth_date, height_cm, activity_level))
    return result is None


def login_user(db, login, password):
    query = (
        "SELECT Код_пользователя, Логин, Пол, ДатаРождения, РостСм, УровеньАктивности "
        "FROM Пользователи WHERE Логин = ? AND ХешПароля = ?"
    )
    result = db.execute(query, (login, hash_password(password)))
    if result:
        row = result[0]
        return User(user_id=row[0], login=row[1], gender=row[2],
                    birth_date=row[3], height_cm=row[4], activity_level=row[5])
    return None