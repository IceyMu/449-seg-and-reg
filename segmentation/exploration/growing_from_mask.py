"""
Can you provide many seed points for growing by providing a mask or at least convert that mask into a large list of points?
"""

import os
import numpy as np
import SimpleITK as sitk

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'
mask = sitk.ReadImage('Segmentation-Segment_1-label.nrrd')
image = sitk.ReadImage('../../patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz')
image_ldr = sitk.Cast(sitk.RescaleIntensity(image), sitk.sitkUInt8)

#sitk.Show(sitk.LabelOverlay(image_ldr, mask), 'initial mask')

"""
Looking at the documentation it probably easiest to use np.argwhere to convert the mask into a list of indicies
"""

index_array = np.argwhere(sitk.GetArrayViewFromImage(mask))

# Still need to convert from numpy's z, y, x to SimpleITK's x, y, z
index_array = index_array[:, [2, 1, 0]]

# Now just grow
multiplier = 7
seg = sitk.ConfidenceConnected(image,
                               seedList=index_array.tolist(),
                               numberOfIterations=1,
                               multiplier=multiplier,
                               initialNeighborhoodRadius=1,
                               replaceValue=255)

object_mask = image != 0
seg *= object_mask

sitk.Show(sitk.LabelOverlay(image_ldr, seg), 'Grow from mask')
