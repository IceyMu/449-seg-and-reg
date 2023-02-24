"""
Perform a segmentation on a single image by growing from a provided seed region
"""

import os
import SimpleITK as sitk

from segmentation import *

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'
"""
Near future
Write a script that does the registration from standard variables
The steps are
    - Define those variables
    - If an exclude mask is provided prevent the segmentation from growing into that region
    - If necessary convert a seed mask image into a list of seeds
    - Grow the seeds into a segmentation
    - Do edge removal if desired
    - Close holes
    - Remove islands
    - Define the white matter as the pixels in the object and not in the grey matter
    - Save the mask
    
Wrap it in a function that accepts a dictionary

Add some visualization options
"""

# Default values
gm_value = 2
wm_value = 1

# Seed growing parameters
multiplier = 2
neighbourhood_radius = 1
num_iterations = 3

exclude_mask = '/run/media/marcus/c0b18950-d75e-4fd2-a761-e3fdc1e863ec/Github/449-seg-and-reg/segmentation/exclude_masks/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1_exclude_mask.nrrd'
excluded_region_value = -1000

# Segmentation cleanup parameters
erode_radius = 3
closing_radius = 0
opening_radius = 0

# Load in values
file_name = '../patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz'
#seeds = (59, 64, 32)
seeds = '/run/media/marcus/c0b18950-d75e-4fd2-a761-e3fdc1e863ec/Github/449-seg-and-reg/segmentation/seed_masks/ActiveAx_AxonDensity_BK02_HSC_BB5_R1_Rt1_seed_mask.nrrd'

seed_dilate_radius = 0
exclude_dilate_radius = [0, 0, 2]


img = sitk.ReadImage(file_name)
img_ldr = sitk.Cast(sitk.RescaleIntensity(img), sitk.sitkUInt8)

# Make each slice have about the same average brightness
#img = normalize_brightness_along_z(img)
#img_ldr = sitk.Cast(sitk.RescaleIntensity(img), sitk.sitkUInt8)

#sitk.Show(img, 'normalized image')

# Make pixels in the exclude mask a large value so they aren't grown into
if exclude_mask:
    excluded_region = sitk.ReadImage(exclude_mask)
    if exclude_dilate_radius:
        excluded_region = sitk.BinaryDilate(excluded_region, exclude_dilate_radius)

    img = sitk.Mask(img,
                    maskImage=excluded_region,
                    maskingValue=1,
                    outsideValue=excluded_region_value)


# If seeds is a mask convert it to a list of seed points
if type(seeds) == str:
    seed_mask = sitk.ReadImage(seeds)
    if seed_dilate_radius:
        seed_mask = sitk.BinaryDilate(seed_mask, seed_dilate_radius)

    seed_array = np.argwhere(sitk.GetArrayViewFromImage(seed_mask))

    # Convert from numpy's z, y, x indexing to SimpleITK's x, y, z indexing
    seeds = seed_array[:, [2, 1, 0]]

gm_mask = sitk.ConfidenceConnected(img,
                                   seedList=seeds.tolist(),
                                   numberOfIterations=num_iterations,
                                   multiplier=multiplier,
                                   initialNeighborhoodRadius=neighbourhood_radius,
                                   replaceValue=gm_value)

# Remove voxels outside or on the edge of the object
object_mask = img != 0

if erode_radius:
    erode_filter = sitk.BinaryErodeImageFilter()
    erode_filter.SetKernelRadius([erode_radius, erode_radius, 0])
    erode_filter.SetForegroundValue(1)
    erode_mask = erode_filter.Execute(object_mask)
else:
    erode_mask = object_mask

gm_mask = erode_mask * gm_mask

# Remove islands
if opening_radius:
    opening_filter = sitk.BinaryMorphologicalOpeningImageFilter()
    opening_filter.SetKernelRadius([opening_radius]*3)
    opening_filter.SetForegroundValue(gm_value)
    gm_mask = opening_filter.Execute(gm_mask)

# Close holes
if closing_radius:
    closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
    closing_filter.SetKernelRadius([closing_radius]*3)
    closing_filter.SetForegroundValue(gm_value)
    gm_mask = closing_filter.Execute(gm_mask)

"""
# Create white matter and grey matter mask
# White matter mask is the object minus the gray matter
wm_mask = sitk.Mask(object_mask,
                    maskImage=gm_mask,
                    maskingValue=gm_value)

# TODO we need to save the gm_mask if we are only going to run segmentation on a few images since the shape of the whole object is different between images
seg_mask = wm_mask + gm_mask

# Save the mask to disk
file_name_parts = os.path.basename(file_name).split('.')
sitk.WriteImage(seg_mask, 'output/' + '.'.join([file_name_parts[0] + '_seg', *file_name_parts[1:]]))
"""

sitk.Show(sitk.LabelOverlay(img_ldr, gm_mask), 'no normalization')
