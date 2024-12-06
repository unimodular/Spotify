from shiny import App, ui, render, reactive
from web import search_podcasts, get_episodes
import re
import pandas as pd
import numpy as np
from generate_principal_components_v2 import generate_principal_components
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os 

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

def find_nearest_points(input_vector, sample_matrix, top_n=10):
    """
    计算输入向量到样本矩阵中最近的点。
    Args:
        input_vector (numpy.array): 输入的主成分向量。
        sample_matrix (numpy.array): 样本矩阵。
        top_n (int): 返回的最近点数量。
    Returns:
        list[int]: 最近点的索引列表。
    """
    distances = np.sqrt(np.sum((sample_matrix - input_vector) ** 2, axis=1))
    nearest_indices = np.argsort(distances)[:top_n]
    return nearest_indices




b64_file = "b64_image.txt"
with open(b64_file, "r") as file:
    base64_image = file.read().strip()

# 创建 Shiny 应用的 UI
app_ui = ui.page_fluid(
    ui.HTML(
        f"""
        <style>
            body {{
                background-image: url('data:image/jpeg;base64,{base64_image}');
                background-size: cover;
                background-attachment: fixed;
                color: #212529;  /* 全局文字颜色 */
            }}
            .shiny-input-container {{
                background: rgba(255, 255, 255, 0.9);  /* 半透明背景 */
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .btn {{
                background-color: black;  /* 按钮背景颜色 */
                color: white;  /* 按钮文字颜色 */
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                cursor: pointer;
                margin-bottom: 20px;
            }}
            .btn:hover {{
                background-color: #333;  /* 鼠标悬停时按钮颜色 */
            }}
            .center-container {{
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;  /* 内容居中 */
                height: 100vh;  /* 占满可视窗口高度 */
                padding-left: 50px;  /* 在右侧留出空白 */
                margin-left: 50px;  /* 右侧边距，额外留空 */
                padding-right: 50px;  /* 在右侧留出空白 */
                margin-right: 50px;  /* 右侧边距，额外留空 */
            }}
        </style>
        """
    ),
    ui.row(
        ui.column(
            2,
            ui.input_text("key_words_input", "Enter search keyword", ""),  # 输入关键词
            ui.div(
                ui.input_action_button("search_button", "Search", class_="btn"),  # 搜索按钮
                ui.input_action_button("cluster_button", "Cluster", class_="btn"),  # 聚类按钮
                style="display: flex; align-items: center; gap: 10px;"  # 水平排列
            ),
            ui.output_ui("podcast_ui"),  # Podcast 下拉选择框
            ui.output_ui("episode_ui"),  # Episode 下拉选择框
            ui.output_text("description_output")  # 显示 Episode 描述
        ),
        ui.column(
            8,  # 中间宽度调整为 8 栅格
            ui.div(
                ui.output_plot("cluster_plot"),  # 聚类图像显示区域
                class_="center-container"
            )
        ),
        ui.column(
            2,
            ui.output_ui("nearest_button_ui"),  # 动态控制 Find Nearest Points 按钮
            ui.output_ui("nearest_points_display") # 最近点打印框
        )
    )
)

###########################################################################
# 定义 Shiny 应用的逻辑
def server(input, output, session):
    # 全局变量存储 Podcast 和 Episode 数据
    podcasts = reactive.Value([])  # 使用 reactive 存储动态数据
    episodes = reactive.Value([])
    nearest_indices = reactive.Value([])
    principal_components = reactive.Value([])  # 主成分矩阵
    cluster_clicked = reactive.Value(False)  # 创建一个 reactive 值，记录是否点击过 Cluster 按钮

    @reactive.Effect
    @reactive.event(input.cluster_button)  # 当点击 Cluster 按钮时触发
    def _():
        cluster_clicked.set(True)  # 标记为已点击

    # 动态生成 Find Nearest Points 按钮
    @output
    @render.ui
    def nearest_button_ui():
        if cluster_clicked():
            return ui.input_action_button("find_nearest_points", "Find Nearest Points", class_="btn btn-primary")
        return None  # 不显示按钮

    @reactive.Effect
    def update_podcasts():
        """在点击搜索按钮后触发搜索功能"""
        if input.search_button():
            keyword = input.key_words_input()
            if keyword:
                search_results = search_podcasts(keyword)
                if search_results:
                    podcasts.set(search_results)
                else:
                    podcasts.set([])
                    print("No matching podcasts found.")
            else:
                podcasts.set([])  # 清空结果
                print("Please enter a search keyword.")

    @output
    @render.ui
    def podcast_ui():
        """动态生成 Podcast 下拉框"""
        if podcasts.get():
            return ui.input_select(
                "selected_podcast",
                "Choose a podcast",
                {podcast['id']: podcast['name'] for podcast in podcasts.get()},
            )
        return ui.div("No matching podcasts found. Please search again.")
    ##############################################################################
    @reactive.Effect
    def update_episodes():
        """当选择 Podcast 后，动态更新 Episode 列表"""
        selected_podcast_id = input.selected_podcast()
        if selected_podcast_id:
            episodes.set(get_episodes(selected_podcast_id))
        else:
            episodes.set([])  # 清空结果
    
    ############
    @output
    @render.ui
    def episode_ui():
        """动态生成 Episode 下拉框"""
        if episodes.get():
            return ui.input_select(
                "selected_episode",
                "Choose an episode",
                {ep['id']: remove_emojis(ep.get('name', 'N/A')) for _, ep in enumerate(episodes.get()[:10])},
            )
        return ui.div("Please wait for searching.")
    #############
    @output
    @render.text
    def description_output():
        """
        显示选中 Episode 的描述，限制描述长度至最多 20 个单词，
        并保存完整描述及相关信息到 CSV 文件。
        """
        selected_episode_id = input.selected_episode()
        if selected_episode_id:
            selected_podcast_id = input.selected_podcast()
            selected_episode = next(
                (ep for ep in episodes.get() if ep['id'] == selected_episode_id), None
            )
            selected_podcast = next(
                (pod for pod in podcasts.get() if pod['id'] == selected_podcast_id), None
            )
            if selected_episode and selected_podcast:
                # 获取完整描述和相关信息
                podcast_name = selected_podcast.get('name', 'Unknown Podcast')
                podcast_id = selected_podcast_id
                episode_name = selected_episode.get('name', 'Unknown Episode')
                episode_id = selected_episode_id
                full_description = selected_episode.get('description', 'No description available.')

                # 保存到 CSV 文件
                df = pd.DataFrame([{
                    "Podcast Name": podcast_name,
                    "Podcast ID": podcast_id,
                    "Episode Name": episode_name,
                    "Episode ID": episode_id,
                    "Description": full_description
                }])
                df.to_csv("selected_descriptions.csv", index=False)

                # 截断描述至最多 20 个单词
                truncated_description = " ".join(full_description.split()[:20])
                if len(full_description.split()) > 20:
                    truncated_description += "..."

                return f"Description: {truncated_description}"
        return "Please select an episode to see the description."
        
    @output
    @render.plot
    def cluster_plot():
        if input.cluster_button():
            keywords_file = "words_BTM.txt"
            pca_matrix_file = "pca_matrix.csv"
            selected_descriptions_file = "selected_descriptions.csv"
            sample_matrix_file = "pca_results_keyword_count.csv"

            # 检查所有必要文件是否存在
            if not all(map(os.path.exists, [keywords_file, pca_matrix_file, selected_descriptions_file, sample_matrix_file])):
                print("Required files are missing!")
                return None

            # 初始化变量
            nearest_indices = []

            # 确保生成主成分结果
            try:
                principal_components_result = generate_principal_components(keywords_file, pca_matrix_file, selected_descriptions_file)
            except Exception as e:
                print(f"Error generating principal components: {e}")
                return None

            # 加载样本矩阵
            try:
                sample_matrix = pd.read_csv(sample_matrix_file)[['PC1','PC2']].values
            except Exception as e:
                print(f"Error loading sample matrix: {e}")
                return None

            # 合并数据
            combined_matrix = np.vstack((sample_matrix, principal_components_result))

            # 聚类分析
            try:
                kmeans = KMeans(n_clusters=15, random_state=42)
                kmeans.fit(combined_matrix)

                # 创建聚类结果 DataFrame
                result_df = pd.DataFrame(combined_matrix, columns=["PC1", "PC2"])
                result_df["Cluster"] = kmeans.labels_
                result_df["Type"] = ["Existing"] * len(sample_matrix) + ["New"] * len(principal_components_result)
            except Exception as e:
                print(f"Error during KMeans clustering: {e}")
                return None

            # 计算最近的10个点
            input_vector = principal_components_result[0]  # 假设用户输入为第一行
            print(f'principal_components_result = {principal_components_result}')
            distances = np.sqrt(np.sum((sample_matrix - input_vector) ** 2, axis=1))
            print(distances)
            nearest_indices = np.argsort(distances)[:10]

            # 保存最近点索引到文本文件
            with open("nearest_points_indices.txt", "w") as file:
                for idx in nearest_indices:
                    file.write(f"{idx}\n")

            # 绘制聚类图
            try:
                plt.figure(figsize=(10, 10))
                existing_data = result_df[result_df["Type"] == "Existing"]
                new_data = result_df[result_df["Type"] == "New"]

                # 绘制现有数据
                plt.scatter(existing_data["PC1"], existing_data["PC2"], c=existing_data["Cluster"], cmap='viridis', alpha=0.5, label="Existing Data", s=5)

                # 绘制新加入的数据
                plt.scatter(new_data["PC1"], new_data["PC2"], c='red', label="New Data", edgecolor='black', s=50)

                # 绘制聚类中心
                plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=20, c='blue', label='Centroids', marker='X')

                # 图例和标题
                plt.xlabel("PC1")
                plt.ylabel("PC2")
                plt.title("Cluster Analysis with Highlighted New Data")
                plt.legend()
                return plt.gcf()
            except Exception as e:
                print(f"Error during plot generation: {e}")
                return None
        return None
    #########################################################################3
    @output
    @render.ui
    def nearest_points_display():
        """
        打印最近的Podcast/Episode名称，并截断为不超过20个字符，仅显示最近10个点。
        """
        sample_csv = "sample.csv"
        indices_file = "nearest_points_indices.txt"
        if input.find_nearest_points():
            # 检查文件是否存在
            if not os.path.exists(indices_file):
                return ui.div("No nearest points data found. Please click 'Cluster' first.")

            if not os.path.exists(sample_csv):
                return ui.div("Sample data file not found.")

            # 读取数据
            try:
                with open('sample.csv', 'r', encoding='utf-8', errors='ignore') as file:
                    sample_data = pd.read_csv(file)

                print(sample_data)
            except Exception as e:
                return ui.div(f"Error loading sample data: {e}")

            # 读取最近点索引
            try:
                with open(indices_file, "r") as file:
                    nearest_indices = [int(line.strip()) for line in file.readlines()]  # 从文件中加载行号
            except Exception as e:
                return ui.div(f"Error reading nearest indices file: {e}")

            # 使用行号提取对应的Episode数据
            try:
                nearest_data = sample_data.iloc[nearest_indices[:10]]  # 获取最近10个点
            except Exception as e:
                return ui.div(f"Error extracting data by indices: {e}")

            # 构造打印框内容
            content = []
            for idx, row in enumerate(nearest_data.itertuples(index=False), start=1):
                episode_name = row.episode_name  # 假定 CSV 中有 episode_name 列

                # 忽略所有特殊字符，保留字母、数字、空格和常见符号
                cleaned_name = re.sub(r'[^a-zA-Z0-9\s.,!?\'-]', '', episode_name)

                # 截断名称为不超过20个字符
                truncated_name = cleaned_name if len(cleaned_name) <= 30 else cleaned_name[:30] + "..."
                
                content.append(ui.div(f"{idx}. {truncated_name}", style="margin-bottom: 5px;"))

            return ui.div(
                *content,
                style="padding: 10px; border: 1px solid #ddd; background-color: #f9f9f9; border-radius: 5px; max-height: 1300px; overflow-y: auto; font-size: 12px;"
            )
                

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()
