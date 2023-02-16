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
import  matplotlib.pyplot as plt
import SimpleITK as sitk

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'
path_prefix = '../patient_data/BK02_HSC_BB2_C1_Rt1/'

# Load in the images
fixed_image = sitk.ReadImage(path_prefix + 'DBSI_ADC_BK02_HSC_BB2_C1_Rt1.nii')
moving_image_1 = sitk.ReadImage(path_prefix + 'ihMT_ihMTRex_cosmod_exp19_BK02_HSC_BB2_C1_Rt1.nrrd')
moving_image_2 = sitk.ReadImage(path_prefix + 'qT2_medium_gmT2_fixed_BK02_HSC_BB2_C1_Rt1.nrrd')

moving_image_1 = sitk.Cast(moving_image_1, sitk.sitkFloat32)
moving_image_2 = sitk.Cast(moving_image_2, sitk.sitkFloat32)


"""
img1 and 2 have basically the same spacing and the same number of pixels and are situated similarly whereas the fixed
image has a much different origin and a much different spacing

(0.15000000596046448, 0.15000000596046448, 1.0)
(0.3125001375567697, 0.31249990761118634, 1.4999995284335927)
"""

# Start with translation only transform
translation_transform = sitk.TranslationTransform(fixed_image.GetDimension())

# Create registration method
trans_registration = sitk.ImageRegistrationMethod()
trans_registration.SetMetricAsCorrelation()
trans_registration.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=200)
trans_registration.SetOptimizerScalesFromPhysicalShift()
trans_registration.SetInterpolator(sitk.sitkLinear)
trans_registration.SetInitialTransform(translation_transform, inPlace=False)

# Capture metric value to measure convergence
metric_values = []


def append_metric_value(value):
    metric_values.append(value)


trans_registration.AddCommand(sitk.sitkIterationEvent, lambda: append_metric_value(trans_registration.GetMetricValue()))

reg_transform_1 = trans_registration.Execute(fixed_image, moving_image_1)
output_1 = sitk.Resample(moving_image_1, fixed_image, reg_transform_1, sitk.sitkLinear, 0.0, moving_image_1.GetPixelID())

# Plot the metric values
plt.plot(metric_values, label='ihMT_ihMTRex')

# Repeat
metric_values = []
reg_transform_2 = trans_registration.Execute(fixed_image, moving_image_2)
output_2 = sitk.Resample(moving_image_2, fixed_image, reg_transform_2, sitk.sitkLinear, 0.0, moving_image_2.GetPixelID())
plt.plot(metric_values, label='qT2_medium_gmT2_fixed')

plt.legend()
plt.title('Translation Registration Convergence')
plt.ylabel('Correlation Metric')
plt.xlabel('Iteration step')
plt.tight_layout()
#plt.show()
plt.close()

# Save images for comparison in 3d slicer
sitk.WriteImage(output_1, 'output/ihMT_ihMTRex_cosmod_exp19_BK02_HSC_BB2_C1_Rt1_(registered).nrrd')
sitk.WriteImage(output_2, 'output/qT2_medium_gmT2_fixed_BK02_HSC_BB2_C1_Rt1_(registered).nrrd')

# Overlay the two images as different colours
fixed_image_ldr = sitk.RescaleIntensity(fixed_image)
output_1_ldr = sitk.RescaleIntensity(output_1)
output_2_ldr = sitk.RescaleIntensity(output_2)

composite_1 = sitk.Cast(sitk.Compose(fixed_image_ldr, output_1_ldr, fixed_image_ldr), sitk.sitkVectorUInt8)
composite_2 = sitk.Cast(sitk.Compose(fixed_image_ldr, output_2_ldr, fixed_image_ldr), sitk.sitkVectorUInt8)
sitk.Show(composite_1)
sitk.Show(composite_2)

"""
Visually these give pretty good agreement in the alignment and the butterfly so this will probably suffice for now I
will probably compose this translation with the non rigid transform used to register the atlas to the other images
"""
