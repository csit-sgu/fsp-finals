from enum import Enum


class AuthRoutes(Enum):
    REGISTER = "/register"
    AUTH = "/auth"
    REFRESH = "/refresh"
