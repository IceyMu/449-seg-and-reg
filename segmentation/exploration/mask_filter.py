import os
import SimpleITK as sitk

"""
See if MaskImageFilter() or Mask() is what I think it is
"""

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'
mask = sitk.ReadImage('Segmentation-Segment_1-label.nrrd')
image = sitk.ReadImage('../../patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz')
image_ldr = sitk.RescaleIntensity(image)

replace_value = 255

replaced_image = sitk.Mask(image,
                           maskImage=mask,
                           maskingValue=1,
                           outsideValue=replace_value)

sitk.Show(replaced_image)
