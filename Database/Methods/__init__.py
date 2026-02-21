from .repeatMethods import RepeatMethods
from .sessionMethods import SessionMethods
from .afkMethods import AFKMethods

class Methods(
    RepeatMethods,
    SessionMethods,
    AFKMethods
):
    pass