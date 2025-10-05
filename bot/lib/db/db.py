from .users import UsersServiceImpl

class DbServiceImpl():
    users: UsersServiceImpl = UsersServiceImpl()
