#%% Imports

# Dependencies
import pandas as pd, numpy as np
import nibabel as nib
from scipy import stats
import scipy.spatial.distance as sp_distance
from joblib import Parallel, delayed
from tqdm import tqdm
import gc
from collections import namedtuple


#%% Define basic functions

# MinMax scaler function for correlation matrix
def minmaxscl(matrix):
    """Applies Min-Max scaling to whole flat DataFrame (not row-wise,
    not column-wise)

    Args:
        matrix (DataFrame): DataFrame (matrix) to be scaled

    Returns:
        DataFrame: Min-Max scaled DataFrame
    """

    n = matrix.shape[0]
    flat = matrix.values.flatten()

    scaled_mat = (flat - flat.min()) / (flat.max() - flat.min())
    finalscl = pd.DataFrame(scaled_mat.reshape(n,n), index=matrix.index, columns=matrix.columns)

    return finalscl

# Function to obtain the RDM
def rsm(matrix, dist_method):
    """Given a DataFrame with trials as columns and voxels as rows,
    computes a representational dissimilarity matrix (RDM), using the
    given method.

    Args:
        matrix (DatFrame): Trial by trial DF with a voxel value per row
        dist_method (_type_): Method to compute dissimilarity: 'correlation',
            'euclidean', 'cosine', 'mahalanobis', 'minkowski'

    Returns:
        DataFrame: A symmetric correlation matrix (n,n), where n is number of
            trials
    """

    # Mapper of possible distance functions 
    dists_map = {
        "correlation":sp_distance.correlation,
        "euclidean":sp_distance.euclidean,
        "cosine":sp_distance.cosine,
        "mahalanobis":sp_distance.mahalanobis,
        "minkowski":sp_distance.minkowski
    }

    if dist_method in dists_map:
        method = dists_map.get(dist_method)
    else:
        print(f"ERROR: Invalid method. Possible methods are {list(dists_map.keys())}")
        return


    mat = matrix.to_numpy()  # Convert to NumPy array
    labs = matrix.columns   # Get labels for later use

    num_trials = len(labs)
    dists = np.zeros((num_trials, num_trials))  # Preallocate distance array

    # Compute pairwise distances using vectorized operations
    dists = sp_distance.squareform(sp_distance.pdist(matrix.T, metric=dist_method))

    dists = pd.DataFrame(dists, index=labs, columns=labs)

    return dists

# Function to shrink RDM into smaller components
def shrink_rdm(mat, block_size):
    """Given a RDM, reduces it to smaller components by averaging cells 
    within a block of given size. It assumes that trials are ordered around 
    a sensible property that is theoretically relevant.

    Args:
        mat (DatFrame): Ordered RDM (be it brain or empirical RDM)
        block_size (_type_): N of trials to average.

    Returns:
        DataFrame: A reduced RDM of size N of trials / block size. Each column/row
        represents the average of N(block_size) trials
    """

    # We  first extract the numeric part of the matrix.
    df_numeric = mat.to_numpy()  # Convert DataFrame to NumPy array

    # Find the number of blocks along each dimension
    n_blocks = df_numeric.shape[0] // block_size

    # Reshape the matrix into blocks of nxn and compute the mean for each block
    reduced_matrix = df_numeric.reshape(n_blocks, block_size, n_blocks, block_size).mean(axis=(1, 3))

    # Convert the reduced matrix back into a DataFrame
    reduced_df = pd.DataFrame(reduced_matrix)

    return reduced_df


#%% Define core functions

# Utility function to get one center and neighbours
def get_spheres(center, indices, voxel_size_mm, sphere_radius):
    """Gets the possible sphere of a given coordinate, for the given
    voxel size and sphere radius. Typically called by 
    searchlight_spheres_parallel.

    Args:
        center (tuple): A 3 item tuple with the 3 coordinates/indices
        indices (array): All indices of the array containing the brain image
        voxel_size_mm (float): cubic voxel size in mm
        sphere_radius (float): sphere radius in mm

    Returns:
        dict: a dictionary containing the center and neighbours of
        the sphere. This is used in parallel by searchlight_spheres_parallel
        to get all possible spheres.
    """
    x, y, z = center

    # Generate sphere coordinates within the brain mask
    distances = np.sqrt(((indices[0] - x) * voxel_size_mm)**2 + ((indices[1] - y) * voxel_size_mm)**2 + ((indices[2] - z) * voxel_size_mm)**2)
    sphere_indices = distances <= sphere_radius

    # Extract the indices of the neighboring voxels within the sphere
    sphere_neighbors = np.array(np.where(sphere_indices)).T

    # Calculate the center of mass of the sphere
    sphere_center = np.mean(sphere_neighbors, axis=0).astype(int)

    return {
        'center': tuple(sphere_center),
        'neighbors': sphere_neighbors
    }


# To get all possible searchlights within the brain image
def searchlight_spheres_parallel(mask, sphere_radius, voxel_size_mm, jobs,  brain_voxel_threshold=0.5):
    """Processes each sphere in parallel by calling get_spheres

    Args:
        mask (boolean array): an array with the dimensions of the volumes to be
            analysed, where True means "brain voxel" and False means "non-brain 
            voxel".  
        sphere_radius (float): _description_
        voxel_size_mm (float): _description_
        jobs (int): number of CPUs to use during parallelisation
        brain_voxel_threshold (float): ratio of brain voxels that should be
            included in the sphere. Defaults to 0.5. 

    Returns:
        list of SphereInfo objects: a list of items containing all possible brain 
        voxels that allow to build a sphere containing at least 50% of brian 
        voxels (default). Access the centers and neighbors as follows:
            SphereInfo[i].center = tuple of coordinates of the sphere center 
            SphereInfo[i].neighbors = array of coordinates of neighboring voxels
    """
    # Find the coordinates of the brain voxels
    brain_coordinates = np.array(np.where(mask)).T

    # Create a grid of indices covering the entire spatial dimensions
    indices = np.indices(mask.shape)

    # Parallelize the loop over sphere coordinates
    sphere_info_list = Parallel(n_jobs=jobs)(
        delayed(get_spheres)(
            center, 
            indices, 
            voxel_size_mm, 
            sphere_radius) for center in tqdm(brain_coordinates, desc="Searching spheres")
    )

    # Filter spheres based on the criterion of having at least min_brain_voxels_ratio of their voxels within the brain mask
    SphereInfo = namedtuple('SphereInfo', ['center', 'neighbors'])
    filtered_spheres = [SphereInfo(**sphere_info) for sphere_info in sphere_info_list if
                        np.count_nonzero(mask[tuple(np.array(sphere_info['neighbors']).T)]) / len(
                            sphere_info['neighbors']) >= brain_voxel_threshold]

    return filtered_spheres


# To get brain RDMs for each sphere
def get_brain_RDMs(brain_data, spheres_data, labels_data, dist_method="cosine", jobs=5):
    """Generate representational dissimilarity matrices (RDMs) based on sphere values for each trial.

    Args:
        brain_data (ndarray): a 4-dimensional ndarray with 3 spatial dimensions and 1 temporal dimension (volumes).
        spheres_data (list of dicts): the spheres info provided by searchlight_spheres_parallel.
        labels_data (array): list of labels for the trials.
        jobs (int): number of CPUs used during parallelisation. Defaults to 5 (A number most PCs will have).
        dist_method (str, optional): Method to compute distances. Defaults to "cosine".

    Returns:
        dict: A dictionary containing center:RDM for each sphere.
    """

    # Define inner function to process values for each sphere
    def process_sphere_values(current_sphere_info):
        center = current_sphere_info.center        # Coordinates of the center of the current sphere
        neighbors = current_sphere_info.neighbors  # Coordinates of the neighbors of the current sphere

        sphere_values = {}  # Empty dictionary for the values of the current sphere

        # Extract the voxel values for each trial within the current sphere
        for vol, label in zip(range(brain_data.shape[-1]), labels_data):
            current_vol = brain_data[..., vol]  # Extract the current volume (3D array) from the 4D brain_data
            vol_values = current_vol[tuple(neighbors.T)]  # Get the values for the neighbors coordinates
            sphere_values[label] = vol_values

        # Convert sphere values into a DataFrame
        sphere_df = pd.DataFrame.from_dict(sphere_values)

        # Compute dissimilarity matrix for the sphere based on the method
        return center, rsm(sphere_df,dist_method)

    # Parallelize the processing of sphere values
    results = Parallel(n_jobs=jobs)(
        delayed(process_sphere_values)(
            current_sphere_info) for current_sphere_info in tqdm(spheres_data, desc="Processing spheres")
    )

    # Create dictionary containing RDMs for each sphere
    rdm_values = {center: rdm for center, rdm in results}

    return rdm_values


def get_model_similarities(brain_rdms, model, dist_method="spearman", jobs=5):
    """Given a dict with brain RDMs obtained in the spheres, and a model as DataFrame,
    computes the dissimilarity between brain and model for each sphere. 

    Args:
        brain_rdms (dict): Dictionary with the brain RDM (DataFrame) for each sphere (3D indices)
        model (DataFrame): A DataDrame with any model (has to be prepared before-hand)
        jobs (int, optional): N of CPUs to parallelise. Defaults to 5.
        dist_method (str, optional): Method to compute distances. Defaults to "Spearman".

    Returns:
        dict: A dictionary with sphere center coordinates as keys, and the corr distance as values
            if kendall or spearman is passed, then it outputs center:(r/t,p-value)
    """
    # Mapper of possible distance functions 
    dists_map = {
        "correlation":sp_distance.correlation,
        "euclidean":sp_distance.euclidean,
        "cosine":sp_distance.cosine,
        "mahalanobis":sp_distance.mahalanobis,
        "minkowski":sp_distance.minkowski,
        "pearson": stats.pearsonr,
        "spearman":stats.spearmanr,
        "kendall":stats.kendalltau
    }

    if dist_method in dists_map:
        method = dists_map.get(dist_method)
    else:
        print(f"ERROR: Invalid method. Possible methods are {list(dists_map.keys())}")
        return
    
    def compute_sphere(sphere_coords):
        sphere_rdm = brain_rdms[sphere_coords]

        # Get the minmax scaled matrix before computing dissimilarity
        norm_sphere = minmaxscl(sphere_rdm)

        # Flatten the sphere and model matrices so that they are 1D
        flat_sphere = norm_sphere.values.flatten()
        flat_model = model.values.flatten()

        # Compute brain-model distance
        dissimilarity = method(flat_sphere, flat_model)

        return sphere_coords, dissimilarity

    # Parallelize the processing of spheres
    results = Parallel(n_jobs=jobs)(
        delayed(compute_sphere)(sphere_coords) for sphere_coords in tqdm(brain_rdms.keys(), desc="Processing spheres"))

    # Create a dictionary with sphere center coordinates as keys and dissimilarity values as values
    dissimilarity_values = {center: dist for center, dist in results}

    return dissimilarity_values
    


def get_model_sim_allin(brain_data, spheres_data, model, labels_data, dist_method="cosine", sim_method="spearman", jobs=5):
    """Given brain data, spheres info, a model DataFrame, and labels for trials, computes the dissimilarity
    between brain data and the model for each sphere. If you do not need to perform extra steps before getting model
    similarities, this is the recommended way, since it is the most efficient.

    Args:
        brain_data (ndarray): 4D array with brain data (3D spatial dimensions and 1D temporal dimension).
        spheres_data (list of dicts): Spheres info provided by searchlight_spheres_parallel.
        model (DataFrame): A DataFrame with the model data. *Note: the model should follow the same order
            than that of the volumes in the functional image
        labels_data (array): List of labels for the trials.
        dist_method (str, optional): Method to compute distances. Defaults to "spearman".
        jobs (int, optional): Number of CPUs to parallelize. Defaults to 5.

    Returns:
        dict: A dictionary with sphere center coordinates as keys and the correlation distance as values.
    """
    # Function to compute brain RDM and model similarity for a single sphere
    def compute_similarity(center, neighbors):
        # Extract brain data for the sphere
        sphere_data = [brain_data[..., vol][tuple(neighbors.T)] for vol in range(brain_data.shape[-1])]
        
        # Convert to DataFrame
        sphere_df = pd.DataFrame(np.array(sphere_data).T, columns=labels_data)
        
        # Compute brain RDM for the sphere
        sphere_rdm = rsm(sphere_df, dist_method)
        
        # Compute model similarity
        model_similarity = method_sim(sphere_rdm.values.flatten(), model.values.flatten())
        
        return center, model_similarity
    
    # Mapper of possible distance functions
    dists_map = {
        "correlation": sp_distance.correlation,
        "euclidean": sp_distance.euclidean,
        "cosine": sp_distance.cosine,
        "mahalanobis": sp_distance.mahalanobis,
        "minkowski": sp_distance.minkowski,
        "pearson": stats.pearsonr,
        "spearman": stats.spearmanr,
        "kendall": stats.kendalltau
    }
    
    if sim_method in dists_map:
        method_sim = dists_map.get(sim_method)
    else:
        print(f"ERROR: Invalid distance method. Possible methods are {list(dists_map.keys())}")
        return

    # Parallelize the computation of model similarities for each sphere
    results = Parallel(n_jobs=jobs)(
        delayed(compute_similarity)(sphere.center, sphere.neighbors) for sphere in tqdm(spheres_data, desc="Computing similarities")
    )
    
    # Create a dictionary with sphere center coordinates as keys and similarity values as values
    similarity_values = {center: similarity for center, similarity in results}

    return similarity_values


# Standalone Function to compute brain RDM for a single sphere
def get_sphere_RDM(brain_data, labels_data, center, neighbors, dist_method="cosine"):
    """Given a single sphere within the brain mask, computes the brain RDM 
    according to the labels given for the trials. This is intended for doing
    operations with the RDM and not run out of memory

    Args:
        brain_data (ndarray): 4D array with brain data (3D spatial dimensions and 1D temporal dimension).
        labels_data (array): list of labels for the trials
        center (list): coordinates of the center of the sphere
        neighbors (ndarray): neighbor voxels of the sphere
        dist_method (str, optional): method to compute the RDM. Defaults to "cosine".

    Returns:
        center, sphere RDM: Returns the center and the resulting RDM 
    """
    # Extract brain data for the sphere
    sphere_data = [brain_data[..., vol][tuple(neighbors.T)] for vol in range(brain_data.shape[-1])]
    
    # Convert to DataFrame
    sphere_df = pd.DataFrame(np.array(sphere_data).T, columns=labels_data)
    
    # Compute brain RDM for the sphere
    sphere_rdm = rsm(sphere_df, dist_method)
    
    # Cleanup to free memory
    del sphere_data, sphere_df
    gc.collect()

    return center, sphere_rdm

# Standalone Function to compute model similarity for a single sphere
def get_sphere_similarity(sphere_RDM, model, sim_method="spearman"):
    """Compute similarity for just 1 sphere. It's meant for doing further
    computations, along with "get_sphere_RDM". 

    Args:
        sphere_RDM (DataFrame): a pandas dataframe with the sphere RDM
        model (DataFrame): a pandas dataframe expressing an empirical model 
        sim_method (str, optional): method to compute similarity. Defaults to "spearman".

    Returns:
        float: a similarity value according to the selected method
    """
    # Mapper of possible distance functions
    dists_map = {
        "correlation": sp_distance.correlation,
        "euclidean": sp_distance.euclidean,
        "cosine": sp_distance.cosine,
        "mahalanobis": sp_distance.mahalanobis,
        "minkowski": sp_distance.minkowski,
        "pearson": stats.pearsonr,
        "spearman": stats.spearmanr,
        "kendall": stats.kendalltau
    }
    
    if sim_method in dists_map:
        method_sim = dists_map.get(sim_method)
    else:
        print(f"ERROR: Invalid distance method. Possible methods are {list(dists_map.keys())}")
        return

    # Compute model similarity
    model_similarity = method_sim(sphere_RDM.values.flatten(), model.values.flatten())
    
    return model_similarity


def sims_to_nifti(img_path,similarities,prefix):
    """Given a path to the functional image and the similarities dict obtained
    from get_model_similarities, or get_model_sim_allin, converts the resulting 
    map of correlations with the model to a nifti 3d image, and saves it to the
    specified path

    Args:
        img_path (str): Path to the original functional image (the same one you used
            to create the mask)
        similarities (dict): Dictionary with center indices as keys, and similarity
            values as values. 
        prefix (str): Path to which the image is saved
    """
    # Load the original brain image
    brain_img = nib.load(img_path)

    # Create an empty array with the same shape as the brain image
    empty_data = np.zeros(brain_img.shape[:3])

    # Iterate over the dictionary and assign correlation values to the empty array
    for center_coords, correlation_value in similarities.items():
        empty_data[center_coords] = correlation_value[0]

    # Create a new NIfTI image using the empty array and affine from the original image
    new_img = nib.Nifti1Image(empty_data, affine=brain_img.affine)

    # Save the new image
    nib.save(new_img, f'{prefix}.nii')
    print(f"Nifti image saved as {prefix}.nii")

