# import pandas as pd
# import numpy as np

# def generate_principal_components(keywords_file, pca_matrix_file, selected_description_file):
#     #调用：principal_components = generate_principal_components("words_BTM.txt", "pca_matrix.csv", "selected_descriptions.csv")
#     """
#     将 selected_descriptions.csv 转换为 n × 2 的主成分向量矩阵。
#     """
#     # 读取关键词
#     print("加载关键词文件...")
#     with open(keywords_file, "r", encoding="utf-8") as file:
#         keywords = [line.strip() for line in file.readlines()]
#     print(f"加载了 {len(keywords)} 个关键词：{keywords[:10]}")

#     # 加载 PCA 矩阵 (601, 2)
#     print("加载 PCA 关键词主成分关系矩阵...")
#     pca_matrix = pd.read_csv(pca_matrix_file, index_col=0).values  # Shape: (601, 2)
#     print(f"PCA 矩阵维度: {pca_matrix.shape}")

#     # 读取 selected_descriptions.csv
#     print("加载描述文件...")
#     selected_df = pd.read_csv(selected_description_file)
#     if 'Description' not in selected_df.columns:
#         raise ValueError("文件中缺少 'Description' 列！")

#     # 提取所有描述
#     descriptions = selected_df['Description'].fillna("").tolist()
#     print(f"处理的描述数量: {len(descriptions)}")

#     # 初始化关键词向量矩阵
#     print("生成关键词向量矩阵...")
#     vectors = np.zeros((len(descriptions), len(keywords)))  # Shape: (N, 600)

#     # 遍历每条描述，计算关键词频数
#     for i, description in enumerate(descriptions):
#         for j, keyword in enumerate(keywords):
#             vectors[i, j] = description.lower().count(keyword)

#     # 添加逻辑列
#     print("添加逻辑列...")
#     logical_column = (vectors.sum(axis=1) == 0).astype(int).reshape(-1, 1)  # 如果前 600 列全为 0，则为 1，否则为 0
#     vectors = np.hstack((vectors, logical_column))  # 合并逻辑列
#     print(f"最终关键词向量矩阵维度: {vectors.shape}")

#     # 计算主成分向量矩阵
#     print("计算主成分向量矩阵...")
#     principal_components = np.dot(vectors, pca_matrix)  # 包括逻辑列在内
#     print(f"主成分向量矩阵维度: {principal_components.shape}")

#     return principal_components
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle

def generate_principal_components(keywords_file, pca_matrix_file, selected_description_file, scaler_model_file="scaler_model.pkl"):
    # 调用：principal_components = generate_principal_components("words_BTM.txt", "pca_matrix.csv", "selected_descriptions.csv")
    """
    将 selected_descriptions.csv 转换为 n × 2 的主成分向量矩阵，并使用 StandardScaler 标准化数据。
    """

    # 读取关键词
    print("加载关键词文件...")
    with open(keywords_file, "r", encoding="utf-8") as file:
        keywords = [line.strip() for line in file.readlines()]
    print(f"加载了 {len(keywords)} 个关键词：{keywords[:10]}")

    # 加载 PCA 矩阵 (601, 2)
    print("加载 PCA 关键词主成分关系矩阵...")
    pca_matrix = pd.read_csv(pca_matrix_file, index_col=0)[['PC1','PC2']].values  # Shape: (601, 2)
    print(f"PCA 矩阵维度: {pca_matrix.shape}")

    # 读取 selected_descriptions.csv
    print("加载描述文件...")
    selected_df = pd.read_csv(selected_description_file)
    if 'Description' not in selected_df.columns:
        raise ValueError("文件中缺少 'Description' 列！")

    # 提取所有描述
    descriptions = selected_df['Description'].fillna("").tolist()
    print(f"处理的描述数量: {len(descriptions)}")

    # 初始化关键词向量矩阵
    print("生成关键词向量矩阵...")
    vectors = np.zeros((len(descriptions), len(keywords)))  # Shape: (N, 600)

    # 遍历每条描述，计算关键词频数
    for i, description in enumerate(descriptions):
        for j, keyword in enumerate(keywords):
            vectors[i, j] = description.lower().count(keyword)

    # 添加逻辑列
    print("添加逻辑列...")
    logical_column = (vectors.sum(axis=1) == 0).astype(int).reshape(-1, 1)  # 如果前 600 列全为 0，则为 1，否则为 0
    vectors = np.hstack((vectors, logical_column))  # 合并逻辑列
    print(f"最终关键词向量矩阵维度: {vectors.shape}")

    # 标准化关键词向量矩阵
    print("标准化关键词向量矩阵...")
    # 加载保存的 scaler 模型
    with open(scaler_model_file, 'rb') as file:
        scaler = pickle.load(file)
    vectors_scaled = scaler.transform(vectors)

    # 计算主成分向量矩阵
    print("计算主成分向量矩阵...")
    principal_components = np.dot(vectors_scaled, pca_matrix)  # 使用标准化后的矩阵进行 PCA 映射
    print(f"主成分向量矩阵维度: {principal_components.shape}")

    return principal_components
