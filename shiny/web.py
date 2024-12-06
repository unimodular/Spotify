import time
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import re

def remove_emojis(text):
    """
    移除文本中的所有表情符号。

    Args:
        text (str): 输入的字符串。

    Returns:
        str: 移除了表情符号后的字符串。
    """
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # 表情符号 (例如：😀, 😂, 😅)
        "\U0001F300-\U0001F5FF"  # 符号和图片 (例如：🌈, 🌍, ⛄)
        "\U0001F680-\U0001F6FF"  # 交通工具和符号 (例如：🚀, ✈️, 🚦)
        "\U0001F700-\U0001F77F"  # Alchemical Symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"  # Dingbats (例如：✂️, ✅, ☎️)
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)


# 初始化 Spotify 客户端
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id="cf66d17bc81344338b463aa9968574fe",
                                                           client_secret="d2281332006e46c3b093d7a4dc222291"))

def search_podcasts(keyword):
    """根据关键词搜索 podcast"""
    try:
        results = sp.search(q=keyword, type='show', limit=10)['shows']['items']
        if results:
            print("搜索结果如下：")
            for idx, show in enumerate(results, 1):
                print(f"{idx}. {show['name']} (ID: {show['id']})")
            return results
        else:
            print("未找到任何相关的 podcasts。")
            return []
    except Exception as e:
        print(f"搜索失败：{e}")
        return []

def get_episodes(show_id):
    """获取指定 podcast 的所有 episodes"""
    try:
        episodes = []
        offset = 0
        while True:
            results = sp.show_episodes(show_id=show_id, limit=50, offset=offset)
            if results and 'items' in results:
                episodes.extend(results['items'])
                if len(results['items']) < 50:
                    break
                offset += 50
            else:
                break
            time.sleep(0.5)
        return episodes
    except Exception as e:
        print(f"获取 episodes 失败：{e}")
        return []

# def display_episodes(episodes):
#     """显示 episodes"""
#     print("以下是该 podcast 的 episodes：")
#     for idx, episode in enumerate(episodes, 1):
#         print(f"{idx}. {episode.get('name', 'N/A')} (发布日期: {episode.get('release_date', 'N/A')})")

def display_episodes(episodes, max_display=10):
    """显示 episodes，限制显示的数量"""
    print("以下是该 podcast 的部分 episodes：")
    for idx, episode in enumerate(episodes[:max_display], 1):  # 限制显示数量
        if episode:  # 过滤掉 None 值
            name = remove_emojis(episode.get('name', 'N/A'))
            print(f"{idx}. {name} (发布日期: {episode.get('release_date', 'N/A')})")
        else:
            print(f"{idx}. 无效的 episode 数据")



def main():
    keyword = input("请输入搜索关键词：")
    podcasts = search_podcasts(keyword)
    if not podcasts:
        return

    try:
        podcast_choice = int(input("请选择一个 podcast 的编号："))
        selected_podcast = podcasts[podcast_choice - 1]
        print(f"您选择的 podcast 是：{selected_podcast['name']} (ID: {selected_podcast['id']})")
    except (IndexError, ValueError):
        print("无效的选择。")
        return

    episodes = get_episodes(selected_podcast['id'])
    if not episodes:
        print("未找到任何 episodes。")
        return

    display_episodes(episodes, max_display=10)


    try:
        episode_choice = int(input("请选择一个 episode 的编号："))
        selected_episode = episodes[episode_choice - 1]
        name = remove_emojis(selected_episode.get('name', 'N/A'))
        print(f"您选择的 episode 是：{name} (发布日期: {selected_episode.get('release_date', 'N/A')})")
        print(f"Episode 描述：{selected_episode.get('description', '无描述')}\n")
    except (IndexError, ValueError):
        print("无效的选择。")
        return

if __name__ == "__main__":
    main()
