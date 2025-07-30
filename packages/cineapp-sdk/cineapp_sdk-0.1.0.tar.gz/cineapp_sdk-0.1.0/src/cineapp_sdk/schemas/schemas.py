from pydantic import BaseModel
from typing import Optional, List

#This file defines the data schemas used by the API

class RatingBase(BaseModel):
    """
    it represente the rating of a movie by a user
    """
    userId: int
    movieId: int
    rating: float
    timestamp: int
    
    class Config:
        #This schema can be created from an SQLAlchemy object
        orm_mode = True



class TagBase(BaseModel):
    """
    it represente the tag added by a user to a movie
    """
    userId: int
    movieId: int
    tag: str
    timestamp: int
    
    class Config:
        orm_mode = True
        
class LinkBase(BaseModel):
    """
    external links to the movie
    """
    imdbId: Optional[str]
    tmdbId: Optional[int]
    
    class Config:
        orm_mode = True        
        

#Class for the movies
class MovieBase(BaseModel):
    """
    Principal schema for the movies
    it contains only the basic information about the movie
    """
    movieId: int
    title: str
    genres: Optional[str] = None
    
    class Config:
        orm_mode = True
        
class MovieDetailed(MovieBase):
    """
    it heritates the principal schema for the movies and adds the ratings, tags and links
    """
    ratings: List[RatingBase] = []
    tags: List[TagBase] = []
    link: Optional[LinkBase] = None
    
    

class MovieSimple(BaseModel):
    """
    it's similar to the MovieBase schema but it doesn't contain the added information (ratings, tags, links)
    """
    movieId: int
    title: str
    genres: Optional[str]
    
    class Config:
        orm_mode = True


# Read Only : For Ratings anf Tags endpoints
class RatingSimple(BaseModel):
    """
    it represente the rating of a movie by a user
    """
    userId: int
    movieId: int
    rating: float
    timestamp: int
    
    class Config:
        orm_mode = True


class TagSimple(BaseModel):
    """
    it represente the tag added by a user to a movie
    """
    userId: int
    movieId: int
    tag: str
    timestamp: int
    class Config:
        orm_mode = True


class LinkSimple(BaseModel):
    """
    it represente the link to the movie
    """
    movieId: int
    imdbId: Optional[str]
    tmdbId: Optional[int]
    class Config:
        orm_mode = True    
        
class Analytics(BaseModel):
    """
    it represente the statistics of the database
    """
    movie_count: int
    rating_count: int
    tag_count: int
    link_count: int

    class Config:
        orm_mode = True