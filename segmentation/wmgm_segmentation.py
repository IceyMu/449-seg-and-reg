import os
import numpy as np
import matplotlib.pyplot as plt
import SimpleITK as sitk

"""
Probably order of operations
Load seed points
Grow
Load exclusion mask
Subtract
Remove islands
Close holes
"""

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

img = sitk.ReadImage('../patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz')
img_ldr = sitk.Cast(sitk.RescaleIntensity(img), sitk.sitkUInt8)

"""
# Version that probably includes the exactly 0 voxels (voxels with a value of exactly 0 are automatically excluded from the threshold calculation)
otsu_filter = sitk.OtsuThresholdImageFilter()
otsu_filter.SetInsideValue(1)
otsu_filter.SetOutsideValue(0)
seg = otsu_filter.Execute(img)

# mask the segmentation mask
mask = img != 0
seg = seg * mask

sitk.Show(sitk.LabelOverlay(img_ldr, seg), 'masking')
print('No mask: ', otsu_filter.GetThreshold())

The problem with the simple thresholding method is the rim of the image is dark, there are holes, and the whole butterfly isn't captured well for most z values
"""

seed_point = (59, 64, 32)

multiplier = 5
seg_mask = sitk.ConfidenceConnected(img,
                                    seedList=[seed_point],
                                    numberOfIterations=1,
                                    multiplier=multiplier,
                                    initialNeighborhoodRadius=1,
                                    replaceValue=255)

# Explicitly exclude pixels that are too close to the edge in x and y

"""
closing_filter = sitk.BinaryMorphologicalClosingImageFilter()t
closing_filter.SetKernelRadius(3)
closing_filter.SetForegroundValue(1)
closed_mask = closing_filter.Execute(seg_mask)

sitk.Show(closed_mask, 'closed_mask')
"""

# Remove pixels that are too close to the edge from the mask
object_mask = img != 0
#object_mask *= 255

radius = (3, 3, 0)
erode_filter = sitk.BinaryErodeImageFilter()
erode_filter.SetKernelRadius(radius)
erode_filter.SetForegroundValue(1)
erode_filter.SetBackgroundValue(0)

erode_mask = erode_filter.Execute(object_mask)
seg_mask = erode_mask * seg_mask
#erode_mask = sitk.Cast(erode_mask, sitk.sitkUInt8)
#composite = sitk.Compose(erode_mask, seg_mask, object_mask)
#sitk.Show(composite, 'erode')

# Close holes

closing_filter = sitk.BinaryMorphologicalClosingImageFilter()
closing_radius = 1
closing_filter.SetKernelRadius([1]*3)
closing_filter.SetForegroundValue(255)
closed_mask = closing_filter.Execute(seg_mask)

#closed_mask = sitk.BinaryClosingByReconstruction(seg_mask, [5, 5, 5])


composite = sitk.Compose(closed_mask, seg_mask, closed_mask)
#sitk.Show(composite, 'hole closing')

"""
closing_radius = 3
closed_mask = sitk.BinaryOpeningByReconstruction(seg_mask, [closing_radius]*3)
closed_mask = sitk.BinaryClosingByReconstruction(closed_mask, [closing_radius]*3)

closed_mask = sitk.BinaryDilate(closed_mask, [closing_radius]*3)
"""
#composite = sitk.Compose(closed_mask, seg_mask, closed_mask)
#sitk.Show(composite, 'hole closing')

#sitk.Show(sitk.LabelOverlay(img_ldr, seg_mask), 'cc')
sitk.Show(sitk.LabelOverlay(img_ldr, closed_mask), 'cc')
#sitk.Show(sitk.LabelOverlay(img_ldr, sitk.BinaryDilate(seg_mask, [5]*3)), 'dilate')
