from enum import Enum
from rest_framework import status
from rest_framework.exceptions import APIException as RestAPIException


class APIExceptionCode(Enum):
    GAME_ALREADY_STARTED = 1000
    GAME_NOT_YET_STARTED = 1001
    GAME_ALREADY_ENDED = 1002
    GAME_MAX_PLAYERS_REACHED = 1003
    GAME_INSUFFICIENT_PLAYERS = 1004
    GAME_INCORRECT_RESIDENT_COUNT = 1005
    GAME_MAX_RESIDENT_FOR_ROLE_REACHED = 1006

    PLAYER_ALREADY_JOINED = 2000
    PLAYER_ALREADY_LEFT = 2001


class APIException(RestAPIException):
    def __init__(self, message, code, http_code=None):
        if not http_code:
            self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            self.status_code = http_code

        self.code = code
        self.message = message
        self.http_code = code

        super(APIException, self).__init__(detail=message)
