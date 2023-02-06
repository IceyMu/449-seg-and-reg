"""
Compose many images to see if they could all use the same registration or need to be registered separately
"""

import os
import SimpleITK as sitk

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

patient_data_path = '../patient_data/BK02_HSC_BB2_C1_Rt1'

os.chdir(patient_data_path)
file_list = os.listdir()

#composite = sitk.Cast(sitk.ReadImage(file_list[0]), sitk.sitkFloat32)

# The images do not occupy the same physical space so they will at least need a translation only registration
# Most are located at (-4.855913162231445, -9.360203742980957, -27.477598190307617) units

"""
for image in file_list[0:5]:
    break
    if image.split('.')[-1] == 'mat':
        continue
    next_image = sitk.Cast(sitk.ReadImage(image), sitk.sitkFloat32)
    print(next_image.GetOrigin())
    try:
        #composite = sitk.Compose(composite, next_image)
    except RuntimeError as E:
        print(image)
        raise E
"""

#sitk.Show(composite)

# Alpha blending the images rather than compositing them into a vector image
img1 = sitk.ReadImage(file_list[0])
img2 = sitk.ReadImage(file_list[1])

# Get a simple foreground mask
outside = 0
inside = 1
mask1 = sitk.OtsuThreshold(img1, outside, inside)
mask2 = sitk.OtsuThreshold(img2, outside, inside)

fg1 = sitk.Cast(sitk.RescaleIntensity(img1), sitk.sitkUInt8) * mask1
fg2 = sitk.Cast(sitk.RescaleIntensity(img2), sitk.sitkUInt8) * mask2

#sitk.Show(fg1)
#sitk.Show(fg2)

# The second image has a spacing difference along z of about 1.2e-6
sitk.ProcessObject_SetGlobalDefaultCoordinateTolerance(1e-5)

intersection = mask1 * mask2
alpha = 0.5
# alpha blend is probably all zero because were a multiplying everything by 0.5 and casting it to an int
alpha_blend = alpha * intersection * fg1 + (1 - alpha) * intersection * fg2

sitk.Show(sitk.RescaleIntensity(intersection), 'intersection')
sitk.Show(sitk.RescaleIntensity(alpha_blend))
