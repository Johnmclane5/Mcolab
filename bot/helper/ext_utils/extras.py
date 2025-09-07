import re
import aiohttp
from ...core.config_manager import Config
from logging import getLogger

LOGGER = getLogger(__name__)

def remove_redandent(filename):
    """
    Remove common username patterns from a filename while preserving the content title.

    Args:
        filename (str): The input filename

    Returns:
        str: Filename with usernames removed
    """
    filename = filename.replace("\n", "\\n")

    patterns = [
        r"^@[\w\.-]+?(?=_)",
        r"_@[A-Za-z]+_|@[A-Za-z]+_|[\[\]\s@]*@[^.\s\[\]]+[\]\[\s@]*",  
        r"^[\w\.-]+?(?=_Uploads_)",  
        r"^(?:by|from)[\s_-]+[\w\.-]+?(?=_)",  
        r"^\[[\w\.-]+?\][\s_-]*",  
        r"^\([\w\.-]+?\)[\s_-]*",  
    ]

    result = filename
    for pattern in patterns:
        match = re.search(pattern, result)
        if match:
            result = re.sub(pattern, " ", result)
            break  

    
    result = re.sub(r"^[_\s-]+|[_\s-]+$", " ", result)

    return result

async def remove_extension(caption):
    try:
        # Remove .mkv and .mp4 extensions if present
        cleaned_caption = re.sub(r'\.mkv|\.mp4|\.webm', '', caption)
        return cleaned_caption
    except Exception as e:
        LOGGER.error(e)
        return None
    

async def get_movie_poster(movie_name, release_year=None):
    tmdb_search_url = f'https://api.themoviedb.org/3/search/movie?api_key={Config.TMDB_API_KEY}&query={movie_name}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(tmdb_search_url) as search_response:
                search_data = await search_response.json()
                if search_data.get('results'):
                    results = search_data['results']
                    if release_year:
                        # Filter by release year if provided
                        results = [
                            result for result in results
                            if 'release_date' in result and result['release_date'] and result['release_date'][:4] == str(release_year)
                        ]
                    if results:
                        result = results[0]
                        poster_path = result.get('poster_path', None)
                        return f"https://image.tmdb.org/t/p/original{poster_path}"
        return None
    except Exception as e:
        LOGGER.error(f"Error fetching TMDb movie by name: {e}")
        return

async def get_tv_poster(tv_name, first_air_year=None):
    tmdb_search_url = f'https://api.themoviedb.org/3/search/tv?api_key={Config.TMDB_API_KEY}&query={tv_name}'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(tmdb_search_url) as search_response:
                search_data = await search_response.json()
                if search_data.get('results'):
                    results = search_data['results']
                    if first_air_year:
                        # Filter by first air year if provided
                        results = [
                            result for result in results
                            if 'first_air_date' in result and result['first_air_date'] and result['first_air_date'][:4] == str(first_air_year)
                        ]
                    if results:
                        result = results[0]
                        poster_path = result.get('poster_path', None)
                        return f"https://image.tmdb.org/t/p/original{poster_path}"
        return None
    except Exception as e:
        LOGGER.error(f"Error fetching TMDb TV by name: {e}")
        return
