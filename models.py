"""Классы-модели."""

from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    login: str
    gender: str
    birth_date: str
    height_cm: int
    activity_level: str