import requests
import asyncio

class Song:
    """
    Represents a song with its title, artist, album cover URL, and lyrics.
    """

    def __init__(self, title, artist, album_cover=None, lyrics=None):
        """
        Initializes a new Song instance.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.
            album_cover (str, optional): The URL of the album cover. Defaults to None.
            lyrics (str, optional): The lyrics of the song. Defaults to None.
        """
        self.title = title
        self.artist = artist
        self.album_cover = album_cover
        self.lyrics = lyrics

    def __repr__(self):
        """
        Returns a string representation of the Song object for debugging.
        """
        return (f"Song(title='{self.title}', artist='{self.artist}', "
                f"album_cover={'<set>' if self.album_cover else '<not set>'}, "
                f"lyrics={'<set>' if self.lyrics else '<not set>'})")

    @classmethod
    async def create(cls, title: str, artist: str):
        """
        Asynchronously creates a new Song instance, fetching its album cover and lyrics.

        Args:
            title (str): The song's title.
            artist (str): The song's artist.

        Returns:
            Song: A fully initialized Song instance.
        """
        # Run fetching tasks concurrently
        album_cover_task = fetch_album_cover_url(artist, title)
        lyrics_task = fetch_lyrics(artist, title)

        album_cover, lyrics = await asyncio.gather(album_cover_task, lyrics_task)

        return cls(title, artist, album_cover, lyrics)

async def fetch_album_cover_url(artist: str, album: str):
    """
    Fetches the album cover URL from MusicBrainz and Cover Art Archive.

    Args:
        artist (str): The artist's name.
        album (str): The album's title (used as song title for search consistency).

    Returns:
        str or None: The URL of the album cover, or None if not found or an error occurs.
    """
    # MusicBrainz expects artist and album.
    # In your JS, you used 'title' for album in the create method for fetchAlbumCoverURL.
    # We'll stick to that consistency here.
    musicbrainz_url = (
        f"https://musicbrainz.org/ws/2/release/?query=album:\"{album}\" "
        f"AND artist:\"{artist}\"&fmt=json"
    )
    headers = {'User-Agent': 'Bytes Music Python Library / 1.0.0 ( YourContactInfo@example.com )'}

    print(f"Searching MusicBrainz for album release: {musicbrainz_url}")

    try:
        response = requests.get(musicbrainz_url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        mb_data = response.json()

        if mb_data.get('releases') and len(mb_data['releases']) > 0:
            first_release = mb_data['releases'][0]
            release_mbid = first_release['id']
            cover_art_url = f"https://coverartarchive.org/release/{release_mbid}/front"
            return cover_art_url
        else:
            print(f"No releases found for album \"{album}\" by \"{artist}\"")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching album from MusicBrainz: {e}")
        return None

async def fetch_lyrics(artist: str, title: str):
    """
    Fetches lyrics from the lyrics.ovh API.

    Args:
        artist (str): The artist's name.
        title (str): The song's title.

    Returns:
        str or None: The song lyrics, or None if not found or an error occurs.
    """
    lyrics_url = f"https://api.lyrics.ovh/v1/{artist}/{title}"

    print(f"Searching Lyrics.ovh for lyrics: {lyrics_url}")

    try:
        response = requests.get(lyrics_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        return data.get('lyrics')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching lyrics: {e}")
        return None

# --- Example Usage (similar to your module.exports) ---
if __name__ == "__main__":
    async def main():
        print("--- Testing Song Creation with Async Fetches ---")

        # Example 1: Song that should find an album cover and lyrics
        print("\nCreating 'Bohemian Rhapsody' by 'Queen'...")
        song1 = await Song.create("Bohemian Rhapsody", "Queen")
        print(f"Song 1 Title: {song1.title}")
        print(f"Song 1 Artist: {song1.artist}")
        print(f"Song 1 Album Cover: {song1.album_cover}")
        print(f"Song 1 Lyrics (first 100 chars): {song1.lyrics[:100]}..." if song1.lyrics else "Not found")

        # Example 2: Song that might not find lyrics or cover easily
        print("\nCreating 'NonExistentSong' by 'UnknownArtist'...")
        song2 = await Song.create("NonExistentSong", "UnknownArtist")
        print(f"Song 2 Title: {song2.title}")
        print(f"Song 2 Artist: {song2.artist}")
        print(f"Song 2 Album Cover: {song2.album_cover}")
        print(f"Song 2 Lyrics: {'<set>' if song2.lyrics else 'Not found'}")

        # Example 3: Song with a tricky title/artist combo
        print("\nCreating 'Shape of You' by 'Ed Sheeran'...")
        song3 = await Song.create("Shape of You", "Ed Sheeran")
        print(f"Song 3 Title: {song3.title}")
        print(f"Song 3 Artist: {song3.artist}")
        print(f"Song 3 Album Cover: {song3.album_cover}")
        print(f"Song 3 Lyrics (first 100 chars): {song3.lyrics[:100]}..." if song3.lyrics else "Not found")

    # Run the main asynchronous function
    asyncio.run(main())