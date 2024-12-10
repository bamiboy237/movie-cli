import os
import sys
import json
import click
import requests
import logging
from typing import Dict, List, Optional
from tabulate import tabulate
import google.generativeai as genai
from dotenv import load_dotenv
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('movie_cli.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# API Configuration
TMDB_API_TOKEN = os.getenv('TMDB_API_TOKEN')
GENAI_API_KEY = os.getenv('GENAI_KEY')

if not TMDB_API_TOKEN or not GENAI_API_KEY:
    logger.error("Missing API tokens. Please set TMDB_API_TOKEN and GENAI_KEY in .env file.")
    sys.exit(1)

# Configure Gemini AI
genai.configure(api_key=GENAI_API_KEY)
ai_model = genai.GenerativeModel("gemini-1.5-flash")

class MovieCLI:
    def __init__(self):
        self.watched_list = self._load_watchlist()
        self.tmdb_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {TMDB_API_TOKEN}"
        }
        self.watchlist_file = os.path.expanduser("~/.movie_cli_watchlist.json")

    def _load_watchlist(self) -> List[Dict]:
        """Load user's watchlist from a persistent file."""
        try:
            if os.path.exists(self.watchlist_file):
                with open(self.watchlist_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading watchlist: {e}")
        return []

    def _save_watchlist(self):
        """Save watchlist to a persistent file."""
        try:
            with open(self.watchlist_file, 'w') as f:
                json.dump(self.watched_list, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving watchlist: {e}")

    def movie_list_request(self, query: str, page_number: int = 1, language: str = 'en-US') -> Dict:
        """Fetch movie list from TMDB API with error handling."""
        url = f"https://api.themoviedb.org/3/movie/{query}"
        params = {"language": language, "page": page_number}
        
        try:
            response = requests.get(url, headers=self.tmdb_headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as err:
            logger.error(f"API Request Error: {err}")
            return {"results": [], "total_pages": 0}
        
    def browse_movies(self, category):
        """Interactive browsing of movies."""
        current_page = 1
        total_pages = 1
        def fetch_and_display(page):
            movies = self.movie_list_request(category, page)
            total_pages = movies.get('total_pages', 1)

            movie_list = [
                        [movie['id'], movie['title'], movie['release_date']]
                        for movie in movies.get('results', [])
                    ]
            print(tabulate(movie_list, headers=["ID", "Title", "Release Date"], tablefmt="grid"))

        while True:
            print(f"\nPage {current_page} of {total_pages}")
            fetch_and_display(current_page)
            action = input("Options: (n)ext, (p)revious, (m)enu, (e)xport (s)ee more (q)uit: ").strip().lower()

            if action == "n" and current_page < total_pages:
                current_page += 1
            elif action == "p" and current_page > 1:
                current_page -= 1
            elif action == "m":
                break


    def movie_detail(self, movie_id: int) -> Optional[Dict]:
        """Fetch detailed movie information."""
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        
        try:
            response = requests.get(url, headers=self.tmdb_headers)
            response.raise_for_status()
            movie_data = response.json()
            
            # Use AI to generate additional insights
            try:
                ai_summary = ai_model.generate_content(
                    f"Provide a concise, engaging summary of the movie '{movie_data['title']}'. "
                    f"Highlight key themes, notable performances, and overall cinematic value."
                )
                movie_data['ai_summary'] = ai_summary.text
            except Exception as ai_err:
                logger.warning(f"AI summary generation failed: {ai_err}")
                movie_data['ai_summary'] = "AI summary unavailable."
            
            return movie_data
        except requests.exceptions.RequestException as err:
            logger.error(f"Movie Detail Error: {err}")
            return None

    def add_to_watchlist(self, movie):
        """Add a movie to the user's watchlist."""
        if not any(m['id'] == movie['id'] for m in self.watched_list):
            self.watched_list.append(movie)
            self._save_watchlist()
            print(f"Added {movie['title']} to watchlist")

    def display_watchlist(self):
        """Display the user's watchlist."""
        if not self.watched_list:
            print("Your watchlist is empty.")
            return

        headers = ['ID', 'Title', 'Release Date']
        watchlist_display = [
            [movie['id'], movie['title'], movie.get('release_date', 'Unknown')]
            for movie in self.watched_list
        ]
        print(tabulate(watchlist_display, headers=headers, tablefmt="grid"))

    def export_watchlist(self, path=None):
        """Export watchlist to a JSON file."""
        if not path:
            path = os.path.expanduser("~/movie_watchlist.json")
        
        try:
            with open(path, 'w') as f:
                json.dump(self.watched_list, f, indent=4)
            print(f"Watchlist exported to {path}")
        except Exception as e:
            logger.error(f"Export failed: {e}")

def interactive_menu():
    """Interactive menu-driven interface for the Movie CLI."""
    movie_cli = MovieCLI()

    while True:
        print("\n--- Movie CLI Menu ---")
        print("1. Browse Movies")
        print("2. Movie Details")
        print("3. Add to Watchlist")
        print("4. View Watchlist")
        print("5. Export Watchlist")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == "1":
            # Browse movies
            category = input("Enter category (e.g., popular, top_rated, upcoming): ").strip()
            def browse_movies(category):
                """Interactive browsing of movies."""
                current_page = 1
                total_pages = 1

                def fetch_and_display(page):
                    nonlocal total_pages
                    movies = movie_cli.movie_list_request(category, page)
                    total_pages = movies.get('total_pages', 1)

                    movie_list = [
                        [movie['id'], movie['title'], movie['release_date']]
                        for movie in movies.get('results', [])
                    ]
                    print(tabulate(movie_list, headers=["ID", "Title", "Release Date"], tablefmt="grid"))

                while True:
                    print(f"\nPage {current_page} of {total_pages}")
                    fetch_and_display(current_page)
                    action = input("Options: (n)ext, (p)revious, (m)enu, (s)ee more, (q)uit: ").strip().lower()

                    if action == "n" and current_page < total_pages:
                        current_page += 1
                    elif action == "p" and current_page > 1:
                        current_page -= 1
                    elif action == "m":
                        break
                        '''elif action == "s":
                            # Movie Details

                            print('functionality coming soon')
                            movie_id = input("Enter movie ID: ")
                            try:
                                movie = movie_cli.movie_detail(int(movie_id))
                                if movie:
                                    print(f"🎬 {movie['title']} ({movie.get('release_date', 'Unknown')})")
                                    print(f"Rating: {movie.get('vote_average', 'N/A')}/10")
                                    print(f"Overview: {movie['overview']}")
                                    print(f"\n🤖 AI Insights: {movie.get('ai_summary', 'No AI summary available')}")
                            except ValueError:
                                print("Invalid movie ID. Please enter a number.")'''
                    elif action == "q":
                        print("Exiting browsing.")
                        break
                    else:
                        print("Invalid option. Try again.")
            browse_movies(category)

        elif choice == '2':
            # Movie Details
            movie_id = input("Enter movie ID: ")
            try:
                movie = movie_cli.movie_detail(int(movie_id))
                if movie:
                    print(f"🎬 {movie['title']} ({movie.get('release_date', 'Unknown')})")
                    print(f"Rating: {movie.get('vote_average', 'N/A')}/10")
                    print(f"Overview: {movie['overview']}")
                    print(f"\n🤖 AI Insights: {movie.get('ai_summary', 'No AI summary available')}")
            except ValueError:
                print("Invalid movie ID. Please enter a number.")

        elif choice == '3':
            # Add to Watchlist
            movie_id = input("Enter movie ID to add to watchlist: ")
            try:
                movie = movie_cli.movie_detail(int(movie_id))
                if movie:
                    movie_cli.add_to_watchlist(movie)
            except ValueError:
                print("Invalid movie ID. Please enter a number.")

        elif choice == '4':
            # View Watchlist
            movie_cli.display_watchlist()

        elif choice == '5':
            # Export Watchlist
            path = input("Enter export path (or press Enter for default): ")
            movie_cli.export_watchlist(path if path else None)

        elif choice == '6':
            print("Thank you for using Movie CLI!")
            break

        else:
            print("Invalid choice. Please try again.")

@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Movie CLI: Your personal movie companion."""
    if ctx.invoked_subcommand is None:
        interactive_menu()

@cli.command()
@click.argument('category', default='popular')
def browse(category):
    """Browse movies by category."""
    movie_cli = MovieCLI()
    movies = movie_cli.movie_list_request(category)
    
    for movie in movies.get('results', []):
        print(f"{movie['id']} - {movie['title']} (Released: {movie.get('release_date', 'Unknown')})")
        print(f"Overview: {movie['overview'][:200]}...\n")

@cli.command()
@click.argument('movie_id')
def details(movie_id):
    """Get detailed movie information."""
    movie_cli = MovieCLI()
    movie = movie_cli.movie_detail(int(movie_id))
    
    if movie:
        print(f"🎬 {movie['title']} ({movie.get('release_date', 'Unknown')})")
        print(f"Rating: {movie.get('vote_average', 'N/A')}/10")
        print(f"Overview: {movie['overview']}")
        print(f"\n🤖 AI Insights: {movie.get('ai_summary', 'No AI summary available')}")

@cli.command()
@click.argument('movie_id')
def watchlist(movie_id):
    """Add a movie to your watchlist."""
    movie_cli = MovieCLI()
    movie = movie_cli.movie_detail(int(movie_id))
    
    if movie:
        movie_cli.add_to_watchlist(movie)

@cli.command()
def list_watchlist():
    """Display your watchlist."""
    movie_cli = MovieCLI()
    movie_cli.display_watchlist()

def main():
    cli()

if __name__ == '__main__':
    main()