from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Tuple, Union

    VERSION_TUPLE = Tuple[Union[int, str], ...]

    version: str
    __version__: str
    __version_tuple__: VERSION_TUPLE
    version_tuple: VERSION_TUPLE

__version__ = version = '0.6.2'
__version_tuple__ = version_tuple = tuple(map(int, version.split('.')))

__all__ = ['__version__', 'version']
