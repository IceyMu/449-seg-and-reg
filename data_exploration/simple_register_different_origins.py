"""
Register two of the images with different origins together to see how similar the groups are

images to register

DBSI_ADC_BK02_HSC_BB2_C1_Rt1.nii
ihMT_ihMTRex_cosmod_exp19_BK02_HSC_BB2_C1_Rt1.nrrd
qT2_medium_gmT2_fixed_BK02_HSC_BB2_C1_Rt1.nrrd

Using DBSI_ADC_BK02_HSC_BB2_C1_Rt1.nii as the fixed image
"""

import os
import numpy as np
import SimpleITK as sitk

path_prefix = '../patient_data/BK02_HSC_BB2_C1_Rt1/'

# Load in the images
fixed_image = sitk.ReadImage(path_prefix + 'DBSI_ADC_BK02_HSC_BB2_C1_Rt1.nii')
img1 = sitk.ReadImage(path_prefix + 'ihMT_ihMTRex_cosmod_exp19_BK02_HSC_BB2_C1_Rt1.nrrd')
img2 = sitk.ReadImage(path_prefix + 'qT2_medium_gmT2_fixed_BK02_HSC_BB2_C1_Rt1.nrrd')

"""
img1 and 2 have basically the same spacing and the same number of pixels and are situated similarly whereas the fixed
image has a much different origin and a much different spacing

(0.15000000596046448, 0.15000000596046448, 1.0)
(0.3125001375567697, 0.31249990761118634, 1.4999995284335927)
"""

# Start with translation only transform
translation_transform = sitk.CenteredTransformInitializer(fixed_image,
                                                          img1,
                                                          sitk.TranslationTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)

# Create registration method
reg_method = sitk.ImageRegistrationMethod()
reg_method.SetMetricAsCorrelation()
reg_method.SetMetricSamplingStrategy(reg_method.RANDOM)

reg_method.SetInterpolator(sitk.sitkLinear)
reg_method.SetOptimizerAsGradientDescent(learningRate=1,
                                         numberOfIterations=50)




