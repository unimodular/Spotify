import pandas as pd

pca_matrix_file = "pca_matrix.csv"

print("Loading PCA matrix...")
pca_df = pd.read_csv(pca_matrix_file)

if 'PC1' not in pca_df.columns or 'PC2' not in pca_df.columns:
    raise ValueError("Missing PC1 or PC2 columns in the PCA matrix file.")

print("Sorting PC1 and PC2 by absolute values...")
pc1_sorted = pca_df.loc[:, ['PC1']].apply(lambda x: x.abs()).sort_values(by='PC1', ascending=False)
pc2_sorted = pca_df.loc[:, ['PC2']].apply(lambda x: x.abs()).sort_values(by='PC2', ascending=False)

pc1_ranked = pd.concat([pca_df['Parameters'], pc1_sorted['PC1']], axis=1).sort_values(by='PC1', ascending=False)
pc2_ranked = pd.concat([pca_df['Parameters'], pc2_sorted['PC2']], axis=1).sort_values(by='PC2', ascending=False)

output_file = "pca_rank.txt"
print(f"Saving sorted results to {output_file}...")
with open(output_file, "w") as file:
    file.write("PC1 Sorted Results:\n")
    pc1_ranked.to_string(file, index=False, header=["Parameter", "PC1"])
    file.write("\n\n")
    file.write("PC2 Sorted Results:\n")
    pc2_ranked.to_string(file, index=False, header=["Parameter", "PC2"])

print("Results saved.")
