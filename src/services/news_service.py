import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class NewsService:
    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY', 'demo_key')
        self.base_url = 'https://api.thenewsapi.com/v1/news'
        
    def get_sports_headlines(self, locale: str = 'us', language: str = 'en', limit: int = 10) -> List[Dict]:
        """
        Fetch sports headlines from The News API
        """
        try:
            url = f"{self.base_url}/headlines"
            params = {
                'api_token': self.api_key,
                'locale': locale,
                'language': language,
                'categories': 'sports',
                'limit': limit
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract sports articles from the response
            articles = []
            if 'data' in data:
                # The News API returns data organized by category
                if 'sports' in data['data']:
                    articles = data['data']['sports']
                elif 'general' in data['data']:
                    # Sometimes sports news appears in general category
                    articles = data['data']['general']
                    # Filter for sports-related content
                    articles = [article for article in articles if self._is_sports_related(article)]
            
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news from API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_sports_headlines: {e}")
            return []
    
    def get_all_sports_news(self, locale: str = 'us', language: str = 'en', limit: int = 20) -> List[Dict]:
        """
        Fetch all sports news using the all news endpoint with sports filtering
        """
        try:
            url = f"{self.base_url}/all"
            params = {
                'api_token': self.api_key,
                'locale': locale,
                'language': language,
                'categories': 'sports',
                'limit': limit,
                'search': 'sports OR football OR basketball OR soccer OR tennis OR baseball OR hockey'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            articles = []
            if 'data' in data:
                articles = data['data']
                # Additional filtering for sports content
                articles = [article for article in articles if self._is_sports_related(article)]
            
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching all sports news: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in get_all_sports_news: {e}")
            return []
    
    def _is_sports_related(self, article: Dict) -> bool:
        """
        Check if an article is sports-related based on title, description, and categories
        """
        sports_keywords = [
            'sports', 'football', 'basketball', 'soccer', 'tennis', 'baseball', 
            'hockey', 'golf', 'olympics', 'fifa', 'nfl', 'nba', 'mlb', 'nhl',
            'championship', 'tournament', 'league', 'match', 'game', 'player',
            'team', 'coach', 'stadium', 'score', 'goal', 'touchdown', 'victory'
        ]
        
        # Check categories first
        if 'categories' in article:
            categories = article['categories']
            if isinstance(categories, list) and 'sports' in categories:
                return True
        
        # Check title and description for sports keywords
        text_to_check = []
        if 'title' in article:
            text_to_check.append(article['title'].lower())
        if 'description' in article:
            text_to_check.append(article['description'].lower())
        if 'snippet' in article:
            text_to_check.append(article['snippet'].lower())
        
        combined_text = ' '.join(text_to_check)
        
        # Check if any sports keywords are present
        return any(keyword in combined_text for keyword in sports_keywords)
    
    def get_demo_articles(self) -> List[Dict]:
        """
        Return demo articles for testing when API key is not available
        """
        return [
            {
                'uuid': 'demo-1',
                'title': 'Local Football Team Wins Championship',
                'description': 'The hometown heroes defeated their rivals 3-1 in an exciting match.',
                'snippet': 'In a thrilling championship match, the local football team secured victory...',
                'url': 'https://example.com/news/football-championship',
                'image_url': 'https://example.com/images/football.jpg',
                'language': 'en',
                'published_at': datetime.utcnow().isoformat() + 'Z',
                'source': 'demo-sports.com',
                'categories': ['sports']
            },
            {
                'uuid': 'demo-2',
                'title': 'Basketball Season Kicks Off',
                'description': 'The new basketball season starts with high expectations.',
                'snippet': 'Teams are preparing for what promises to be an exciting basketball season...',
                'url': 'https://example.com/news/basketball-season',
                'image_url': 'https://example.com/images/basketball.jpg',
                'language': 'en',
                'published_at': (datetime.utcnow() - timedelta(hours=2)).isoformat() + 'Z',
                'source': 'demo-sports.com',
                'categories': ['sports']
            },
            {
                'uuid': 'demo-3',
                'title': 'Tennis Tournament Results',
                'description': 'Latest results from the international tennis tournament.',
                'snippet': 'The tennis tournament concluded with surprising upsets and great matches...',
                'url': 'https://example.com/news/tennis-results',
                'image_url': 'https://example.com/images/tennis.jpg',
                'language': 'en',
                'published_at': (datetime.utcnow() - timedelta(hours=4)).isoformat() + 'Z',
                'source': 'demo-sports.com',
                'categories': ['sports']
            }
        ]

