import json, os, time, requests
from selenium import webdriver
from selenium.webdriver.common.by import By


def get_total_episodes(anime_id):
    try:
        url = "https://graphql.anilist.co"
        query = {
            "query": """
            query ($id: Int) {
              Media(id: $id, type: ANIME) {
                title {
                  romaji
                }
                episodes
              }
            }
            """,
            "variables": {"id": anime_id}
        }

        response = requests.post(url, json=query)

        if response.status_code == 200:
            data = response.json()
            print("✅ Fetched total episodes")
            return data['data']['Media']['episodes'], data['data']['Media']['title']['romaji']
        else:
            print(f"❌ Error fetching episodes: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Exception in get_total_episodes: {e}")
        return None, None


class WebDriverManager:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=options)

    def get_video_url(self, url):
        self.driver.get(url)

        for attempt in range(3):
            try:
                time.sleep(5)
                video_element = self.driver.find_element(By.TAG_NAME, 'source')
                video_url = video_element.get_attribute("src")

                if video_url and '[object' not in video_url:
                    return video_url
                else:
                    print(f"⚠️ Invalid video URL on attempt {attempt + 1}")
            except Exception as e:
                print(f"❌ Exception on attempt {attempt + 1}: {e}")

        print("🚫 Failed to fetch valid video URL after 3 attempts.")
        return None

    def close(self):
        self.driver.quit()


def fetch_episode_data_for_single_anime(anime_id):
    try:
        print(f"🔍 Fetching data for anime ID: {anime_id}")
        total_episodes, title = get_total_episodes(anime_id)

        if total_episodes is None:
            print("⚠️ Episodes not found, exiting.")
            return

        print(f"📺 Anime: {title}")
        print(f"🎞️ Total episodes: {total_episodes}\n")

        driver_manager = WebDriverManager()
        video_urls = []

        for episode_num in range(1, total_episodes + 1):
            try:
                episode_url = f"https://www.miruro.tv/watch?id={anime_id}&ep={episode_num}"
                print(f"➡️ Episode {episode_num}: Checking URL {episode_url}")
                video_src = driver_manager.get_video_url(episode_url)

                if video_src:
                    print(f"✅ Episode {episode_num} URL: {video_src}")
                    video_urls.append({"episode": episode_num, "video_url": video_src})
                else:
                    print(f"⚠️ No video URL for episode {episode_num}")
            except Exception as ep_err:
                print(f"❌ Error processing episode {episode_num}: {ep_err}")

        driver_manager.close()

        print("\n📦 All Episodes Data:")
        print(json.dumps(video_urls, indent=2))

    except Exception as e:
        print(f"❌ Unexpected error: {e}")


# === RUN ENTRY POINT ===
if __name__ == "__main__":
    anime_id_input =  '7791'
    if anime_id_input.isdigit():
        fetch_episode_data_for_single_anime(int(anime_id_input))
    else:
        print("❌ Invalid Anime ID.")
