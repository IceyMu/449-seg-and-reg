import numpy as np
import SimpleITK as sitk

image = sitk.ReadImage('../../patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz')
arr = sitk.GetArrayViewFromImage(image)

mean_vector = np.apply_over_axes(np.mean, arr, [1, 2])

#mean_arr = np.zeros_like(arr)
#non_empty_slices = np.where(mean_vector.flatten())
#mean_arr[non_empty_slices] = 1

mean_arr = np.ones_like(arr)
inv_mean_vector = np.reciprocal(mean_vector, where=mean_vector.astype(np.bool_))
mean_arr *= inv_mean_vector

# Make a dummy image with the normalization intensities
brightness_image = sitk.GetImageFromArray(mean_arr)
brightness_image.SetSpacing(image.GetSpacing())
brightness_image.SetOrigin(image.GetOrigin())
brightness_image.SetDirection(image.GetDirection())

import os
os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'
sitk.Show(image * brightness_image)
