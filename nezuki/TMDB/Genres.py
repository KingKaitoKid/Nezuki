from . import __version__
from versioning import deprecated
from .TMDB import TMDB

class Genres(TMDB):
    """
        Class to perform a search on TMDB Database and retrieve some general informations
    """
    
    __version__ = __version__

    def tv(self, **kwargs)->dict:
        """
            Get the list of official genres for TV shows

            Args:
                language (string, optional): Defaults to en, language of results
        """
        return self._handle_genres_call("GET", **kwargs)
    
    def movie(self, **kwargs)->dict:
        """
            Get the list of official genres for movies

            Args:
                language (string, optional): Defaults to en, language of results
        """
        return self._handle_genres_call("GET", **kwargs)
    
    def _handle_genres_call(self,method: str, **kwargs):
        """
            Internal function to make request to API TMDB
        """
        return self._make_request(method, kwargs)