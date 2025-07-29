import requests
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

def create_spotify_client(client_id, client_secret):
    if not client_id or not client_secret:
        raise ValueError("You must provide both client_id and client_secret.")

    credentials = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(auth_manager=credentials)

def get_preview_urls_from_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        preview_urls = set()

        for tag in soup.find_all():
            for attr in tag.attrs.values():
                if isinstance(attr, str) and 'p.scdn.co' in attr:
                    preview_urls.add(attr)

        return list(preview_urls)
    except Exception as e:
        raise RuntimeError(f"Error fetching preview URLs: {e}")

def search_and_get_links(song_name, client_id, client_secret, limit=5):
    try:
        if not song_name:
            raise ValueError("Song name is required")

        spotify = create_spotify_client(client_id, client_secret)
        results = spotify.search(q=song_name, limit=limit, type='track')

        if not results['tracks']['items']:
            return {
                "success": False,
                "error": "No songs found",
                "results": []
            }

        final_results = []

        for track in results['tracks']['items']:
            name = track['name']
            artist = ', '.join([a['name'] for a in track['artists']])
            album_name = track['album']['name']
            album_art = track['album']['images'][0]['url'] if track['album']['images'] else None
            spotify_url = track['external_urls']['spotify']
            preview_url = track.get('preview_url')

            # Fallback to scraping if preview_url not provided
            if not preview_url:
                preview_urls = get_preview_urls_from_html(spotify_url)
                preview_url = preview_urls[0] if preview_urls else None

            final_results.append({
                "name": name,
                "artist": artist,
                "album": album_name,
                "albumArt": album_art,
                "previewUrl": preview_url,
                "spotifyUrl": spotify_url
            })

        return {
            "success": True,
            "results": final_results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "results": []
        }