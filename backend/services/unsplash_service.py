"""
Unsplash Service
Fetches place-specific images from Unsplash API
"""
import os
import requests
from loguru import logger
from typing import List, Optional


class UnsplashService:
    def __init__(self):
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        self.base_url = "https://api.unsplash.com"
        
        if not self.access_key:
            logger.warning("UNSPLASH_ACCESS_KEY not found in environment variables")
    
    def search_photos(self, query: str, per_page: int = 5) -> List[str]:
        """
        Search for photos on Unsplash
        
        Args:
            query: Search query (e.g., "Baga Beach Goa")
            per_page: Number of results to return (default: 5)
        
        Returns:
            List of image URLs
        """
        if not self.access_key:
            logger.error("Cannot search photos: Unsplash access key not configured")
            return []
        
        try:
            url = f"{self.base_url}/search/photos"
            params = {
                "query": query,
                "per_page": per_page,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": f"Client-ID {self.access_key}"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                # Extract regular quality image URLs
                image_urls = [
                    result["urls"]["regular"] 
                    for result in data["results"] 
                    if "urls" in result and "regular" in result["urls"]
                ]
                logger.info(f"Found {len(image_urls)} images for query: {query}")
                return image_urls
            else:
                logger.warning(f"No images found for query: {query}")
                return []
        
        except requests.RequestException as e:
            logger.error(f"Error fetching images from Unsplash: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Unsplash search: {str(e)}")
            return []
    
    def get_image_for_place(self, place_name: str, destination: str = "") -> Optional[str]:
        """
        Get a single high-quality image for a specific place
        
        Args:
            place_name: Name of the place (e.g., "Baga Beach")
            destination: Destination context (e.g., "Goa, India")
        
        Returns:
            Image URL or None if not found
        """
        # Combine place name with destination for better results
        query = f"{place_name} {destination}".strip()
        images = self.search_photos(query, per_page=1)
        
        if images:
            return images[0]
        
        # Fallback: try with just place name
        if destination:
            images = self.search_photos(place_name, per_page=1)
            if images:
                return images[0]
        
        return None
    
    def get_destination_images(self, destination: str, count: int = 5) -> List[str]:
        """
        Get multiple images for a destination
        
        Args:
            destination: Destination name (e.g., "Goa, India")
            count: Number of images to fetch
        
        Returns:
            List of image URLs
        """
        return self.search_photos(destination, per_page=count)


# Create a singleton instance
unsplash_service = UnsplashService()
