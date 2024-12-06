#cluster_and_visualize(principal_components, "pca_results_keyword_count.csv")
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

def cluster_and_visualize(principal_components, sample_matrix_file, output_file="combined_clustered_descriptions.csv"):
    sample_matrix = pd.read_csv(sample_matrix_file).values
    sample_matrix = sample_matrix[:, :2]

    combined_matrix = np.vstack((sample_matrix, principal_components))

    n_clusters = 3
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    kmeans.fit(combined_matrix)

    combined_labels = kmeans.labels_

    result_df = pd.DataFrame(combined_matrix, columns=["PC1", "PC2"])
    result_df["Cluster"] = combined_labels

    num_existing_samples = len(sample_matrix)
    result_df["Type"] = ["Existing"] * num_existing_samples + ["New"] * len(principal_components)
    result_df.to_csv(output_file, index=False, encoding="utf-8")

    plt.figure(figsize=(10, 7))

    existing_data = result_df[result_df["Type"] == "Existing"]
    plt.scatter(existing_data["PC1"], existing_data["PC2"], c=existing_data["Cluster"], cmap='viridis', alpha=0.5, label="Existing Data")

    new_data = result_df[result_df["Type"] == "New"]
    plt.scatter(new_data["PC1"], new_data["PC2"], c='red', label="New Data", edgecolor='black', s=100)

    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], s=50, c='blue', label='Centroids', marker='X')

    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("Cluster Analysis with Highlighted New Data")
    plt.legend()
    plt.show()
