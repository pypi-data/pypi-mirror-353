#%% Imports

# Dependencies
import os
import pandas as pd, numpy as np
import nibabel as nib
from scipy import stats
import scipy.spatial.distance as sp_distance
from joblib import Parallel, delayed
from tqdm import tqdm
from collections import namedtuple
from nilearn.image import resample_to_img
from simplyRSA.searchlight import rsm, minmaxscl

#%% Defining functions

# Function for Fisher z test to compare correlations (1925)

def fisherZ(r1, r2, n1, n2):
    """Calculate Fisher's Z test (1925) for the comparison of two correlations
    from independent samples

    Args:
        r1 (float): R value for sample 1
        r2 (float): R value for sample 2
        n1 (int): Size of sample 1
        n2 (int): Size of sample 2

    Returns:
        tuple(int,int): A tuple with Z value, p-value
    """
    # Fisher transform the correlation values
    z1 = np.arctanh(r1)
    z2 = np.arctanh(r2)

    # Calculate Fisher's Z test

    fisherz = (z1-z2)/np.sqrt(1/(n1-3)+1/(n2-3))
    pval = 1 - stats.norm.cdf(fisherz)

    return fisherz, pval

# Function for bootstrap 

def bootstrap_rdm(brain_rdm, model, bts_iters=100000, corr_method="spearman", jobs=5):
    """Calculates a bootstrap of random permutations from given model and brain RDMs.
    The brain RDM is kept fixed, while the model RDM is randomly permutated with a 
    given random state.

    Args:
        brain_rdm (DataFrame): A Dataframe with 1 ROI RDM (of dimensions (trials,trials))
        model (DataFrame): A Dataframe with an estimated model. Same dimensions than brain_rdm
        bts_iters (int, optional): N of iterations. Defaults to 100.000.
        corr_method (str, optional): Method to compute similarities. Defaults to "spearman".
        jobs (int, optional): N of CPUs used (jobs). Defaults to 5.

    Returns:
        DataFrame: A Dataframe with iterations, with "r_val" and "p_val" as columns
    """
    corr_map = {
        "pearson": stats.pearsonr,
        "spearman": stats.spearmanr,
        "kendall": stats.kendalltau
    }

    if corr_method in corr_map:
        method = corr_map.get(corr_method)
    else:
        print(f"ERROR: Invalid method. Possible methods are {list(corr_map.keys())}")
        return
    
    def bootstrap_iter(iter):
        
        iter_results = {}
        # Shuffle the matrix with random state
        shuff = model.sample(frac=1,axis=1, random_state=iter).sample(frac=1,random_state=iter)    

        # Flatten the brain RDM and the shuffled model
        flat_brain = brain_rdm.values.flatten()
        flat_shuff = shuff.values.flatten()
        
        # Calculate correlation with given model and extract values
        corr = method(flat_brain, flat_shuff)
        r_val = corr.statistic
        p_val = corr.pvalue

        iter_results["r_val"] = r_val
        iter_results["p_val"] = p_val

        iter_df = pd.DataFrame(iter_results,index=[iter])   # Build df with results

        return iter_df
    
    # Prallelise the function
    results = Parallel(n_jobs=jobs)(delayed(
        bootstrap_iter)(iter) for iter in tqdm(range(bts_iters), desc="Computing permutations")
        )

    bootstrap_df = pd.concat(results)   # df with bootstrap results
    return bootstrap_df

# Function to extract dict of ROIs from folder

def getROIs(roidir,func_path):
    """Given a directory with binary ROIs in Nifti format, reads them, resamples them
    to the functional space, and creates a boolean mask for the ROI.

    Args:
        roidir (str): FULL path to the ROI directory
        func_path (str): FULL path to the functional image

    Returns:
        dict: Dictionary with ROI labels as keys, and boolean masks (np.array) as 
            values. Note: labels are extracted from the filename:
                inferior_frontal.nii = inferior_frontal
    """

    roifiles = os.listdir(roidir)
    def readROI(roifile):
        roilabel = roifile.split(".")[0]    # Extract ROI name from filename
        # Read images
        func = nib.load(func_path)
        roi = nib.load(os.path.join(roidir,roifile))

        # Resample the ROI to match functional image grid
        roi = resample_to_img(roi, func, interpolation="nearest")

        # Create output boolean mask 
        roimask = roi.get_fdata() != 0

        return roilabel, roimask
    
    results = Parallel(n_jobs=5)(delayed(
        readROI)(file) for file in tqdm(roifiles, desc="Getting ROI masks")
        )
    
    roimasks = {label:roimask for label, roimask in results}

    return roimasks


# Function to get ROI RDMs

def get_roi_RDMs(brain_data, roi_masks, labels_data, jobs=5, dist_method="cosine"):
    """Gets the RDM for each of the ROIs in your study. Runs after getROIs. 

    Args:
        brain_data (ndarray): A 4D array with 3 spatial dimensions, and 1 temporal 
            dimension (volumes/trials). Volumes should be the last dimension.
        roi_masks (dict): A dict of boolean masks previously defined. You can use
            getROIs for this
        labels_data (list): A list of labels for your trials. Can provide a range of
            ints if you don't have labels (e.g., np.arange(nTrials))
        jobs (int, optional): Number of CPUs used (jobs). Defaults to 5.
        dist_method (str, optional): Method to compute distances. Defaults to "cosine".

    Returns:
        dict: A dict with ROIs as keys, and RDMs as values
    """


    # Define inner function to process values for each sphere
    def process_roi_values(current_roi):
        current_mask = roi_masks.get(current_roi)  # Coordinates of the neighbors of the current sphere

        roi_values = {}  # Empty dictionary for the values of the current ROI

        # Extract the voxel values for each trial within the current ROI
        for vol, label in zip(range(brain_data.shape[-1]), labels_data):
            current_vol = brain_data[..., vol]  # Extract the current volume (3D array) from the 4D brain_data
            vol_values = current_vol[current_mask]  # Get the values for the ROI
            roi_values[label] = vol_values

        # Convert sphere values into a DataFrame
        roi_df = pd.DataFrame.from_dict(roi_values)

        # Compute dissimilarity matrix for the sphere based on the method
        return current_roi, rsm(roi_df,dist_method)

    # Parallelize the processing of sphere values
    results = Parallel(n_jobs=jobs)(
        delayed(process_roi_values)(
            current_roi) for current_roi in tqdm(roi_masks.keys(), desc="Processing ROIs")
    )

    # Create dictionary containing RDMs for each sphere
    rdm_values = {roi: rdm for roi, rdm in results}

    return rdm_values

# Function to get similarities with a given model

def roi_model_similarities(brain_rdms, model, jobs=5, dist_method="spearman"):
    """Given a dict of brain RDMs and a model, computes Brain-Model similarities.

    Args:
        brain_rdms (dict): A dict with ROI brain RDMs. 
        model (DataFrame): A df with an estimated model, with same dimensions than
            the brain RDM (i.e., (nTrials,nTrials))
        jobs (int, optional): Number of CPUs used (jobs). Defaults to 5.
        dist_method (str, optional): Method to compute similarities. Defaults to "spearman".

    Returns:
        DataFrame: A df with model similarities with each ROI, with "r_val" and "p_val" as
            columns
    """

    # Mapper of possible distance functions 
    dists_map = {
        "pearson":stats.pearsonr,
        "spearman":stats.spearmanr,
        "kendall":stats.kendalltau
    }

    if dist_method in dists_map:
        method = dists_map.get(dist_method)
    else:
        print(f"ERROR: Invalid method. Possible methods are {list(dists_map.keys())}")
        return
    
    def compute_roi(roi):
        roi_rdm = brain_rdms[roi]   # ROI selector

        roi_results = {}

        # Get the minmax scaled matrix before computing similarity
        norm_roi = minmaxscl(roi_rdm)

        # Flatten the sphere and model matrices so that they are 1D
        flat_roi = norm_roi.values.flatten()
        flat_model = model.values.flatten()

        # Compute brain-model distance
        similarity = method(flat_roi, flat_model)
        
        roi_results["roi"] = roi
        roi_results["r_val"] = similarity.statistic
        roi_results["p_val"] = similarity.pvalue

        roi_df = pd.DataFrame([roi_results],index=[roi])

        return roi_df

    # Parallelize the processing of spheres
    results = Parallel(n_jobs=jobs)(
        delayed(compute_roi)(roi) for roi in tqdm(brain_rdms.keys(), desc="Calculating similarities"))

    # Create a dictionary with sphere center coordinates as keys and similarity values as values
    similarity_values = pd.concat(results)

    return similarity_values
