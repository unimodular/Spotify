# principal_components = generate_principal_components("words_BTM.txt", "pca_matrix.csv", "selected_descriptions.csv")

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import pickle

def generate_principal_components(keywords_file, pca_matrix_file, selected_description_file, scaler_model_file="scaler_model.pkl"):
    with open(keywords_file, "r", encoding="utf-8") as file:
        keywords = [line.strip() for line in file.readlines()]

    pca_matrix = pd.read_csv(pca_matrix_file, index_col=0).values

    selected_df = pd.read_csv(selected_description_file)
    if 'Description' not in selected_df.columns:
        raise ValueError("The 'Description' column is missing in the file!")

    descriptions = selected_df['Description'].fillna("").tolist()

    vectors = np.zeros((len(descriptions), len(keywords)))

    for i, description in enumerate(descriptions):
        for j, keyword in enumerate(keywords):
            vectors[i, j] = description.lower().count(keyword)

    logical_column = (vectors.sum(axis=1) == 0).astype(int).reshape(-1, 1)
    vectors = np.hstack((vectors, logical_column))

    scaler = StandardScaler()
    vectors_scaled = scaler.fit_transform(vectors)

    with open(scaler_model_file, "wb") as file:
        pickle.dump(scaler, file)

    principal_components = np.dot(vectors_scaled, pca_matrix)

    return principal_components

