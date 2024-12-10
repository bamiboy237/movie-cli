# 🎬 Movie CLI: Your Personal Movie Companion

## Overview

Movie CLI is a powerful, interactive command-line tool for movie enthusiasts. Seamlessly browse movies, get AI-powered insights, manage your watchlist, and explore cinematic treasures—all from your terminal!

## Features 🌟

- **Browse Movies**: Explore popular, top-rated, and upcoming movies
- **Detailed Movie Information**: Get comprehensive movie details
- **AI-Powered Insights**: Receive concise, engaging movie summaries
- **Personal Watchlist**: 
  - Add movies you want to watch
  - View and manage your watchlist
  - Export your watchlist for safekeeping

## Prerequisites 📋

- Python 3.8+
- TMDB API Token
- Google Generative AI API Key

## Installation 🚀

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/movie-cli.git
   cd movie-cli
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   TMDB_API_TOKEN=your_tmdb_api_token
   GENAI_KEY=your_google_generative_ai_key
   ```

## Usage 🖥️

### Interactive Mode
```bash
python movie_cli.py
```

### CLI Commands

- Browse Movies:
  ```bash
  python movie_cli.py browse [category]
  ```
  Categories: `popular`, `top_rated`, `upcoming`

- Movie Details:
  ```bash
  python movie_cli.py details <movie_id>
  ```

- Add to Watchlist:
  ```bash
  python movie_cli.py watchlist <movie_id>
  ```

- List Watchlist:
  ```bash
  python movie_cli.py list_watchlist
  ```

## Configuration 🔧

- Watchlist is saved in `~/.movie_cli_watchlist.json`
- Logs are written to `movie_cli.log`

## Technologies 💡

- Python
- TMDB API
- Google Generative AI
- Click (CLI Framework)
- Prompt Toolkit
- Tabulate

## Contributing 🤝

1. Fork the repository
2. Create your feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License 📄

[Your License Here - e.g., MIT]

## Disclaimer 📢

Movie data and AI summaries are generated from TMDB and Google Generative AI. Always verify information.
