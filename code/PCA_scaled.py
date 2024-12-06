import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import joblib  # For saving and loading models


description_file = "628_preprocessing_cleaned_output.csv"
keywords_file = "words_BTM.txt"
output_file = "pca_results_keyword_count.csv"
scaler_model_file = "scaler_model.pkl"
scaled_matrix_file = "scaled_matrix.csv"


print("Loading description file...")
descriptions_df = pd.read_csv(description_file)
if 'cleaned_description' not in descriptions_df.columns:
    raise ValueError("The 'cleaned_description' column is missing in the file!")


print("Loading keyword file...")
with open(keywords_file, "r", encoding="utf-8") as file:
    keywords = [line.strip() for line in file.readlines()]

print(f"Loaded {len(keywords)} keywords:", keywords[:10])


print("Building matrix...")
matrix = np.zeros((len(descriptions_df), len(keywords)))


for i, description in enumerate(descriptions_df['cleaned_description'].fillna("")):
    for j, keyword in enumerate(keywords):
        matrix[i, j] = description.lower().count(keyword)


additional_column = np.where(matrix.sum(axis=1) == 0, 1, 0)
matrix = np.hstack([matrix, additional_column.reshape(-1, 1)])

print(f"Matrix shape: {matrix.shape}")
print("First 5 rows of the matrix:")
print(matrix[:5])


print("Standardizing the matrix...")
scaler = StandardScaler()
matrix_scaled = scaler.fit_transform(matrix)


joblib.dump(scaler, scaler_model_file)
print(f"StandardScaler model parameters saved to: {scaler_model_file}")


scaled_matrix_df = pd.DataFrame(matrix_scaled)
scaled_matrix_df.to_csv(scaled_matrix_file, index=False, encoding="utf-8")
print(f"Standardized matrix saved to: {scaled_matrix_file}")

print("Performing PCA...")
pca = PCA(n_components=2)
pca_result = pca.fit_transform(matrix_scaled)


explained_variance = pca.explained_variance_ratio_
print(f"PCA explained variance ratio: {explained_variance}")


pca_df = pd.DataFrame(pca_result, columns=["PC1", "PC2"])
pca_df["description_index"] = descriptions_df.index
pca_df.to_csv(output_file, index=False, encoding="utf-8")
print(f"PCA results saved to: {output_file}")


assert np.all(matrix.sum(axis=1) > 0), "There are still rows with all zeros in the matrix!"


import matplotlib.pyplot as plt

plt.figure(figsize=(10, 7))
plt.scatter(pca_df["PC1"], pca_df["PC2"], alpha=0.7)
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.title("PCA Result of Keyword Counts")
plt.show()


components_matrix = pca.components_.T
print(components_matrix)
print(components_matrix.shape)


keywords_with_additional = keywords + ["Additional"]
pca_matrix_df = pd.DataFrame(components_matrix, index=keywords_with_additional, columns=["PC1", "PC2"])
pca_matrix_df.to_csv("pca_matrix.csv", index=True, encoding="utf-8")
print("PCA keyword matrix saved to: pca_matrix.csv")
