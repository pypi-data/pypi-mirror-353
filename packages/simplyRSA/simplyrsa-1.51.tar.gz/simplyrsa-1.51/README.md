# simplyRSA
Simple package to run RSA analyses on fMRI data.
Currently, it only contains 2 modules for RSA searhclight, and ROI-based RSA.

## Setup

__Before installation__

The package uses the following dependencies:

pandas, numpy, nibabel, scipy, joblib, tqdm, collections

If you don't have them installed, simply run:

```pip install pandas numpy nibabel scipy joblib tqdm collections```

__Installation__

1. Download the tar.gz file
2. Go to the directory in which it was downloaded
3. Run ```pip install simplyRSA-[ver].tar.gz```

## Usage

Here is a simple example on how to use the _searchlight_ module:

__Imports__
```
import pandas as pd, numpy as np
import nibabel as nib
from simplyRSA.searchlight import *
```

1. Read your functional images and create a brain mask.
Here, I'm reading a .BRIK file from AFNI, but you can read other files (like Nifti).
The important thing is that the resulting brain image is a 4d image with 3 spatial dimensions
and a 4th dimensions representing volumes (or trials)

```
brikpath = [path to my .BRIK file]  # Define image path
brikdata = nib.load(brikpath).get_fdata()  # Read and extract the data from the image
```
My .BRIK file is a 4d image, with volumes (or trials) as the last dimension

So I isolate 1 volume, and create a binary brain mask, with _True_ where there is a value in the image,
and _False_ where there is no value (i.e. 0) 

```
onevol = brikdata[...,0]  # Isolate 1 volume
mask = onevol!=0  # Binary mask
```
2. Create all possible spheres within the mask

We need 2 important values: _voxel size_ (you can check that on your image header), and _sphere radius_.
My voxel size is 2x2x2, and I want 5mm radius spheres 

```
sphere_radius = 5  # Adjust the radius as needed
voxel_size_mm = 2  # Adjust the voxel size if it's different
```
Then we call the first function, which is _searchlight_spheres_parallel_ as it follows: 

```
spheres_info = searchlight_spheres_parallel(mask, sphere_radius, voxel_size_mm, jobs=36)
```

The _jobs_ argument specifies how many CPUs are used in parallel for this (hence the name)

If you are unsure of how many CPUs your PC has, by providing _-1_ you tell the function to use ALL (the merrier the better). 
It defaults to 5, which is a number most PCs will have. 

The function will return a list of sphereInfo objects, containing _center_ and _neighbours_ indices. We just need to have the 
variable saved to pass it to the next step

3. Get brain RDMs by calling _get_brain_RDMs_

We need to pass the brain data we loaded earlier, the spheres extracted in step 2, and labels for the trials. 
In some instances, you can extract the labels from the header, as it is my case. 
But you can prepare the labels before-hand and load them

```
headpath = [path to my header]

labels = nib.brikhead.parse_AFNI_header(headpath)["BRICK_LABS"].split("~")[1:960:2]  # Extract labels
labels = [element.replace("#", "").replace("_Coef", "") for element in labels]  # Beautify labels
```
If you don't have the labels, or especially if you don't care about them, simply pass a range of numbers
as long as your number of trials:

```
labels = np.arange(brikdata.shape[-1])
```

And now we can run the function
```
all_rdms = get_brain_RDMs(
    brikdata,
    spheres_info,
    labels,
    jobs=36

)
```

4. Get model similarities

Now we feed the _all_rdms_ variable we just created to the function _get_model_similarities_ 

We also need a model in pandas DataFrame format, read from whatever source. In my case, I have an excel file:

```
modelpath = [path to my model]

model = pd.read_excel(modelpath)
```
IMPORTANT: the model should be a n X n where n is your number of trials. The columns and rows should be ordered
as they were ordered in the functional image. 

```
model_simil = get_model_similarities(
    brain_rdms, model,
    jobs=5,
    dist_method="correlation"
)
```

5. Save the output to a Nifti file

Finally, we save the image in the original space (MNI conversion is not implemented yet)

Here we need to provide 1 volume of the original image. For this, we only need again the path to the image
(the function already manages the extraction of the dimensions), provided the image is 4-dimensional.
In this example, we can use the variable _brikpath_ we defined earlier. 

```
sims_to_nifti(
    brikpath
    model_simil,
    prefix=[output_filename]
    )
```

3.a. Alternatively, you can run steps 3 and 4 all in one by using _get_model_sim_allin_. This is the recommended way of
running it, since it is way more efficient, and consumes way less memory. 

In this case, we need the brain data, and spheres info. Other than that, it runs like in the 2 steps above. 

```
model_simil = get_model_sim_allin(
    brikdata,
    spheres_info,
    model,
    labels,
    jobs=36
)
```
