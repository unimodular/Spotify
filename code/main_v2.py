from generate_principal_components_v2 import generate_principal_components


from cluster_and_visualize_v2 import cluster_and_visualize


principal_components = generate_principal_components("words_BTM.txt", "pca_matrix.csv", "selected_descriptions.csv")




cluster_and_visualize(principal_components, "pca_results_keyword_count.csv")
