import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from typing import Dict, Set
import umap



import os
os.environ['LOKY_MAX_CPU_COUNT'] = '4'

def cluster_arrays(data_input, n_clusters, seed = 42):
    """
    Simple clustering of 1D arrays with key tracking.
    
    Parameters:
    -----------
    data_input : dict or List[List[float]]
        Dictionary {key: array} or list of arrays to cluster
    n_clusters : int  
        How many groups you want
        
    Returns:
    --------
    dict: {cluster_id: {'keys': [keys], 'arrays': [arrays]}}
    """
    
    # Handle both dict and list inputs
    if isinstance(data_input, dict):
        keys = list(data_input.keys())
        array_values = list(data_input.values())  # Use .values() to get the arrays
    else:
        keys = list(range(len(data_input)))  # Use indices as keys for lists
        array_values = data_input
    
    # Convert to numpy and cluster
    data = np.array(array_values)
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed)
    labels = kmeans.fit_predict(data)
    

    clusters = [[] for _ in range(n_clusters)]

    for i, label in enumerate(labels):
        clusters[label].append(keys[i])

    return clusters
    
def plot_dict_heatmap(unsorted_data_dict, id_set, figsize=(12, 8), title="Neighborhood Heatmap"):
    """
    Create a heatmap from a dictionary of numpy arrays.
    
    Parameters:
    -----------
    data_dict : dict
        Dictionary where keys are identifiers and values are 1D numpy arrays of floats (0-1)
    id_set : list
        List of strings describing what each index in the numpy arrays represents
    figsize : tuple, optional
        Figure size (width, height)
    title : str, optional
        Title for the heatmap
    
    Returns:
    --------
    fig, ax : matplotlib figure and axes objects
    """
    
    data_dict = {k: unsorted_data_dict[k] for k in sorted(unsorted_data_dict.keys())}

    # Convert dict to 2D array for heatmap
    # Each row represents one key from the dict
    keys = list(data_dict.keys())
    data_matrix = np.array([data_dict[key] for key in keys])
    
    # Create the plot
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create heatmap with white-to-red colormap
    im = ax.imshow(data_matrix, cmap='Reds', aspect='auto', vmin=0, vmax=1)
    
    # Set ticks and labels
    ax.set_xticks(np.arange(len(id_set)))
    ax.set_yticks(np.arange(len(keys)))
    ax.set_xticklabels(id_set)
    ax.set_yticklabels(keys)
    
    # Rotate x-axis labels for better readability
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations showing the actual values
    for i in range(len(keys)):
        for j in range(len(id_set)):
            text = ax.text(j, i, f'{data_matrix[i, j]:.3f}',
                          ha="center", va="center", color="black", fontsize=8)
    
    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Intensity', rotation=-90, va="bottom")
    
    # Set labels and title
    ax.set_xlabel('Proportion of Node Type')
    ax.set_ylabel('Neighborhood')
    ax.set_title(title)
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    plt.show()


def visualize_cluster_composition_umap(cluster_data: Dict[int, np.ndarray], 
                                     class_names: Set[str],
                                     label = False,
                                     n_components: int = 2,
                                     random_state: int = 42):
    """
    Convert cluster composition data to UMAP visualization.
    
    Parameters:
    -----------
    cluster_data : dict
        Dictionary where keys are cluster IDs (int) and values are 1D numpy arrays
        representing the composition of each cluster
    class_names : set
        Set of strings representing the class names (order corresponds to array indices)
    n_components : int
        Number of UMAP components (default: 2 for 2D visualization)
    random_state : int
        Random state for reproducibility
    
    Returns:
    --------
    embedding : numpy.ndarray
        UMAP embedding of the cluster compositions
    """
    
    # Convert set to sorted list for consistent ordering
    class_labels = sorted(list(class_names))
    
    # Extract cluster IDs and compositions
    cluster_ids = list(cluster_data.keys())
    compositions = np.array([cluster_data[cluster_id] for cluster_id in cluster_ids])
    
    # Create UMAP reducer
    reducer = umap.UMAP(n_components=n_components, random_state=random_state)
    
    # Fit and transform the composition data
    embedding = reducer.fit_transform(compositions)
    
    # Create visualization
    plt.figure(figsize=(10, 8))
    
    if n_components == 2:
        scatter = plt.scatter(embedding[:, 0], embedding[:, 1], 
                            c=cluster_ids, cmap='viridis', s=100, alpha=0.7)
        
        if label:
            # Add cluster ID labels
            for i, cluster_id in enumerate(cluster_ids):
                plt.annotate(f'{cluster_id}', 
                            (embedding[i, 0], embedding[i, 1]),
                            xytext=(5, 5), textcoords='offset points',
                            fontsize=9, alpha=0.8)
        
        plt.colorbar(scatter, label='Community ID')
        plt.xlabel('UMAP Component 1')
        plt.ylabel('UMAP Component 2')
        plt.title('UMAP Visualization of Community Compositions')
        
    elif n_components == 3:
        fig = plt.figure(figsize=(12, 9))
        ax = fig.add_subplot(111, projection='3d')
        scatter = ax.scatter(embedding[:, 0], embedding[:, 1], embedding[:, 2],
                           c=cluster_ids, cmap='viridis', s=100, alpha=0.7)
        
        # Add cluster ID labels
        for i, cluster_id in enumerate(cluster_ids):
            ax.text(embedding[i, 0], embedding[i, 1], embedding[i, 2],
                   f'C{cluster_id}', fontsize=8)
        
        ax.set_xlabel('UMAP Component 1')
        ax.set_ylabel('UMAP Component 2')
        ax.set_zlabel('UMAP Component 3')
        ax.set_title('3D UMAP Visualization of Cluster Compositions')
        plt.colorbar(scatter, label='Cluster ID')
    
    plt.tight_layout()
    plt.show()
    
    # Print composition details
    print("Cluster Compositions:")
    print(f"Classes: {class_labels}")
    for i, cluster_id in enumerate(cluster_ids):
        composition = compositions[i]
        print(f"Cluster {cluster_id}: {composition}")
        # Show which classes dominate this cluster
        dominant_indices = np.argsort(composition)[::-1][:2]  # Top 2
        dominant_classes = [class_labels[idx] for idx in dominant_indices]
        dominant_values = [composition[idx] for idx in dominant_indices]
        print(f"  Dominant: {dominant_classes[0]} ({dominant_values[0]:.3f}), {dominant_classes[1]} ({dominant_values[1]:.3f})")
    
    return embedding



# Example usage:
if __name__ == "__main__":
    # Sample data for demonstration
    sample_dict = {
        'category_A': np.array([0.1, 0.5, 0.8, 0.3, 0.9]),
        'category_B': np.array([0.7, 0.2, 0.6, 0.4, 0.1]),
        'category_C': np.array([0.9, 0.8, 0.2, 0.7, 0.5])
    }
    
    sample_id_set = ['feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5']
    
    # Create the heatmap
    fig, ax = plot_dict_heatmap(sample_dict, sample_id_set, 
                               title="Sample Heatmap Visualization")
    
    plt.show()

