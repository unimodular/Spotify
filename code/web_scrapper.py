import pandas as pd
import time
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import os

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="cf66d17bc81344338b463aa9968574fe",
                                                           client_secret="d2281332006e46c3b093d7a4dc222291"))

def get_all_episodes(show_id, limit=50):
    episodes = []
    offset = 0
    while True:
        try:
            results = sp.show_episodes(show_id=show_id, limit=limit, offset=offset)
            if results and 'items' in results:
                episodes.extend(results['items'])
                if len(results['items']) < limit:
                    break
                offset += limit
            else:
                break
            time.sleep(0.5)
        except Exception as e:
            print(f"Error fetching episodes for show_id {show_id}: {e}")
            break
    return episodes

def save_to_csv(data, filename="podcast_episodes.csv"):
    df = pd.DataFrame([data])
    df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False, encoding='utf-8')

def process_keyword(keyword, filename="podcast_episodes.csv", max_items=1000, max_items_per_show=20):
    total_count = 0
    try:
        shows = sp.search(q=keyword, type='show', limit=50)['shows']['items']
        for show in shows:
            if total_count >= max_items:
                print(f"Reached maximum number of items ({max_items}) for keyword {keyword}, stopping...")
                break
            print(f"Processing Show: {show['name']} (ID: {show['id']})")
            episodes = get_all_episodes(show['id'])
            if not episodes:
                print(f"Show {show['name']} (ID: {show['id']}) has no episodes, skipping...")
                continue
            show_count = 0
            for episode in episodes:
                if not episode:
                    continue
                if show_count >= max_items_per_show:
                    print(f"Reached maximum number of episodes ({max_items_per_show}) for Show {show['name']}, skipping remaining episodes...")
                    break
                data = {
                    'keyword': keyword,
                    'show_name': show['name'],
                    'episode_name': episode.get('name', 'N/A'),
                    'description': episode.get('description', 'N/A'),
                    'release_date': episode.get('release_date', 'N/A'),
                    'duration_ms': episode.get('duration_ms', 0),
                    'id': episode.get('id', 'N/A')
                }
                save_to_csv(data, filename)
                total_count += 1
                show_count += 1
                print(f"Saved Episode: {data['episode_name']} (Keyword total: {total_count}/{max_items}, Show total: {show_count}/{max_items_per_show})")
                if total_count >= max_items:
                    print(f"Reached maximum number of items ({max_items}) for keyword {keyword}, stopping...")
                    break
            if total_count >= max_items:
                break
    except Exception as e:
        print(f"Error processing keyword {keyword}: {e}")

KEYWORDS = ['education', 'science', 'technology', 'comedy', 'history', 'health', 'sports', 'economics', 'business', 'entertainment', 'lifestyle', 'philosophy', 'psychology', 'news', 'culture', 'art']
output_file = "628_version2_2.csv"
max_items_per_keyword = 1000
max_items_per_show = 20

for keyword in KEYWORDS:
    print(f"Fetching keyword: {keyword}")
    process_keyword(keyword, output_file, max_items=max_items_per_keyword, max_items_per_show=max_items_per_show)

print(f"All data has been saved to {output_file}")
