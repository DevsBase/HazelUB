from .repeatMethods import RepeatMethods
from .sudoMethods import SudoMethods
from .afkMethods import AFKMethods
from .pmpermitMethods import PMPermitMethods

class Methods(
    RepeatMethods,
    SudoMethods,
    AFKMethods,
    PMPermitMethods
):
    pass
