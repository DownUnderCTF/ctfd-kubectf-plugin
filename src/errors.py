from dataclasses import dataclass


@dataclass
class Error:
    type: str
    message: str
    code: int


ConfigurationError = Error('ConfigurationError',
                           'Please contact the CTF Administrator', 500)

UnknownError = Error('UnknownError', 'Please contact the CTF Administrator',
                     500)

InvalidRequest = Error('InvalidRequest', '', 400)

ValidationError = Error('ValidationError', 'Invalid Challenge', 400)

NotAuthenticatedError = Error('NotAuthenticatedError',
                              'Please log in and join a team', 401)