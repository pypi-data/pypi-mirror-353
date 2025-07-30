from .schemas import MovieSimple, MovieDetailed, RatingSimple, TagSimple, LinkSimple, Analytics
from .cineapp_config import CineConfig

import httpx
from typing import Optional, List, Literal, Union
import pandas as pd

class CineClient:
    """
    Main SDK client to interact with the CineAPP API.
    Provides methods to access movies, ratings, tags, links, and analytics.
    """

    def __init__(self, config: Optional[CineConfig] = None):
        """
        Initializes the CineClient with a configuration.
        If no config is provided, the default CineConfig will be used.
        """
        self.config = config or CineConfig()
        self.cine_base_url = self.config.cine_base_url

    def _format_output(self, data, model, output_format: Literal["pydantic", "dict", "pandas"]):
        """
        Internal helper to format the API response into the desired output type.

        Args:
            data (list): Raw JSON data from API response.
            model (BaseModel): Pydantic model to apply if needed.
            output_format (str): One of 'pydantic', 'dict', or 'pandas'.

        Returns:
            Formatted response.
        """
        if output_format == "pydantic":
            return [model(**item) for item in data]
        elif output_format == "dict":
            return data
        elif output_format == "pandas":
            return pd.DataFrame(data)
        else:
            raise ValueError("Invalid output_format. Choose from 'pydantic', 'dict', or 'pandas'.")

    def health_check(self) -> dict:
        """
        Checks if the CineAPP API is reachable.

        Returns:
            dict: JSON response from the root endpoint.
        """
        url = f"{self.cine_base_url}/"
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()

    def get_movie(self, movieId: int) -> MovieDetailed:
        """
        Retrieves detailed information about a specific movie by ID.

        Args:
            movieId (int): The ID of the movie to retrieve.

        Returns:
            MovieDetailed: Movie data as a Pydantic object.
        """
        url = f"{self.cine_base_url}/movies/{movieId}"
        response = httpx.get(url)
        response.raise_for_status()
        return MovieDetailed(**response.json())

    def list_movies(
        self,
        skip: int = 0,
        limit: int = 100,
        title: Optional[str] = None,
        genre: Optional[str] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[MovieSimple], List[dict], "pd.DataFrame"]:
        """
        Returns a paginated list of movies, optionally filtered by title or genre.

        Args:
            skip (int): Number of items to skip (for pagination).
            limit (int): Max number of movies to return.
            title (str, optional): Filter by movie title.
            genre (str, optional): Filter by movie genre.
            output_format (str): Desired output format.

        Returns:
            List of MovieSimple objects, dicts, or a DataFrame.
        """
        url = f"{self.cine_base_url}/movies"
        params = {"skip": skip, "limit": limit}
        if title:
            params["title"] = title
        if genre:
            params["genre"] = genre
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), MovieSimple, output_format)

    def get_rating(self, userId: int, movieId: int) -> RatingSimple:
        """
        Retrieves a user's rating for a specific movie.

        Args:
            userId (int): The user's ID.
            movieId (int): The movie's ID.

        Returns:
            RatingSimple: Rating data.
        """
        url = f"{self.cine_base_url}/ratings/{userId}/{movieId}"
        response = httpx.get(url)
        response.raise_for_status()
        return RatingSimple(**response.json())

    def list_ratings(
        self,
        skip: int = 0,
        limit: int = 100,
        movieId: Optional[int] = None,
        userId: Optional[int] = None,
        min_rating: Optional[float] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[RatingSimple], List[dict], "pd.DataFrame"]:
        """
        Retrieves a list of ratings with optional filters.

        Args:
            skip (int): Number of items to skip.
            limit (int): Max number of items to return.
            movieId (int, optional): Filter by movie ID.
            userId (int, optional): Filter by user ID.
            min_rating (float, optional): Minimum rating threshold.
            output_format (str): Desired output format.

        Returns:
            List of RatingSimple, dicts, or DataFrame.
        """
        url = f"{self.cine_base_url}/ratings"
        params = {"skip": skip, "limit": limit}
        if movieId:
            params["movieId"] = movieId
        if userId:
            params["userId"] = userId
        if min_rating:
            params["min_rating"] = min_rating
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), RatingSimple, output_format)

    def get_tag(self, userId: int, movieId: int, tag_text: str) -> TagSimple:
        """
        Fetches a specific tag applied to a movie by a user.

        Args:
            userId (int): The user's ID.
            movieId (int): The movie's ID.
            tag_text (str): The tag text.

        Returns:
            TagSimple: Tag data.
        """
        url = f"{self.cine_base_url}/tags/{userId}/{movieId}/{tag_text}"
        response = httpx.get(url)
        response.raise_for_status()
        return TagSimple(**response.json())

    def list_tags(
        self,
        skip: int = 0,
        limit: int = 100,
        movieId: Optional[int] = None,
        userId: Optional[int] = None,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[TagSimple], List[dict], "pd.DataFrame"]:
        """
        Returns a list of user-applied tags, with optional filtering.

        Args:
            skip (int): Number of items to skip.
            limit (int): Number of items to return.
            movieId (int, optional): Filter by movie.
            userId (int, optional): Filter by user.
            output_format (str): Format of returned data.

        Returns:
            List of TagSimple, dicts, or DataFrame.
        """
        url = f"{self.cine_base_url}/tags"
        params = {"skip": skip, "limit": limit}
        if movieId:
            params["movieId"] = movieId
        if userId:
            params["userId"] = userId
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), TagSimple, output_format)

    def get_link(self, movieId: int) -> LinkSimple:
        """
        Retrieves external IDs (IMDB, TMDB) for a specific movie.

        Args:
            movieId (int): Movie ID.

        Returns:
            LinkSimple: External links info.
        """
        url = f"{self.cine_base_url}/links/{movieId}"
        response = httpx.get(url)
        response.raise_for_status()
        return LinkSimple(**response.json())

    def list_links(
        self,
        skip: int = 0,
        limit: int = 100,
        output_format: Literal["pydantic", "dict", "pandas"] = "pydantic"
    ) -> Union[List[LinkSimple], List[dict], "pd.DataFrame"]:
        """
        Returns a list of external links (IMDB, TMDB) for multiple movies.

        Args:
            skip (int): Number of items to skip.
            limit (int): Max number of links to return.
            output_format (str): Desired data format.

        Returns:
            List of LinkSimple, dicts, or DataFrame.
        """
        url = f"{self.cine_base_url}/links"
        params = {"skip": skip, "limit": limit}
        response = httpx.get(url, params=params)
        response.raise_for_status()
        return self._format_output(response.json(), LinkSimple, output_format)

    def get_analytics(self) -> Analytics:
        """
        Retrieves global analytics and statistics from the API.

        Returns:
            Analytics: Aggregated stats as a Pydantic model.
        """
        url = f"{self.cine_base_url}/analytics"
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()
