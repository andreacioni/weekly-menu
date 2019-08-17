class BaseRESTException(Exception):
    code = 500
    error = 'GENERIC'
    description = 'generic REST exception raised'
    details = []

    def __init__(self, code=500, error=None, description=None, details=None):
        if code != None:
            self.code = code

        if error != None:
            self.error = error
        
        if description != None:
            self.description = description

        if details != None:
            self.details = details

    def __repr__(self):
        return "<RESTException: error: '{}'; description: '{}', details: '{}'".format(self.error, self.description, self.details)

class BadRequest(BaseRESTException):
    def __init__(self, description=None, details=None):
        super().__init__(400, 'BAD_REQUEST', description, details)

class InvalidPayloadSupplied(BaseRESTException):
    def __init__(self, description=None, details=None):
        super().__init__(400, 'BAD_REQUEST', description, details)

class UserNotFound(BaseRESTException):
    def __init__(self):
        super().__init__(404, 'USER_NOT_FOUND', 'username/email not found') 

class InvalidCredentials(BaseRESTException):
    def __init__(self, description=None):
        super().__init__(401, 'BAD_CREDENTIALS', description) 

class DuplicateEntry(BaseRESTException):
    def __init__(self, description=None, details=None):
        super().__init__(401, 'DUPLICATE_ENTRY', description, details)