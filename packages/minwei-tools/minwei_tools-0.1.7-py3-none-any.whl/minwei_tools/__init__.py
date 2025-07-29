
import sys
if '-m' not in sys.argv:
    from .dotter import Dotter, piano, slash
    from .async_dotter import AsyncDotter

    import minwei_tools.rs_result as rs_result
    import minwei_tools.server as server

__all__ = [
    "AsyncDotter",
    "Dotter",
    "piano",
    "slash",
    "rs_result",
    "server",
]