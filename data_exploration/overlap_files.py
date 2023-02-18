"""
Compose many images to see if they could all use the same registration or need to be registered separately
"""

import os
import SimpleITK as sitk

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

patient_data_path = '../patient_data/BK02_HSC_BB2_C1_Rt1/'

os.chdir(patient_data_path)
file_list = os.listdir()

#composite = sitk.Cast(sitk.ReadImage(file_list[0]), sitk.sitkFloat32)

# The images do not occupy the same physical space so they will at least need a translation only registration
# Most are located at (-4.855913162231445, -9.360203742980957, -27.477598190307617) units

"""
for image in file_list[0:5]:
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
#img1 = sitk.ReadImage('ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz')
#img2 = sitk.ReadImage('ActiveAx_AxonDiam_BK02_HSC_BB2_C1_Rt1.nii.gz')


# Get a simple foreground mask
outside = 0
inside = 1
mask1 = sitk.Cast(sitk.OtsuThreshold(img1, outside, inside), sitk.sitkFloat32)
mask2 = sitk.Cast(sitk.OtsuThreshold(img2, outside, inside), sitk.sitkFloat32)
# This was probably unecessary all of the images already seem to be masked

fg1 = img1 * mask1
fg2 = img2 * mask2

#sitk.Show(fg1)
#sitk.Show(fg2)

# The second image has a spacing difference along z of about 1.2e-6
sitk.ProcessObject_SetGlobalDefaultCoordinateTolerance(1e-5)

intersection = mask1 * mask2
alpha = 0.5
# alpha blend is probably all zero because were a multiplying everything by 0.5 and casting it to an int
alpha_blend = alpha * intersection * fg1 + (1 - alpha) * intersection * fg2

#sitk.Show(sitk.RescaleIntensity(intersection), 'intersection')
sitk.Show(sitk.RescaleIntensity(alpha_blend), 'alpha blend group A')

# They seem to overlap pretty well but do have spacing differences

for image in file_list:
    if image.split('.')[-1] == 'mat':
        continue
    print(image, ': \t', sitk.ReadImage(image).GetOrigin())

"""
qT2_medium_gmT2_fixed_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)
ihMT_ihMTR_T1d_exp18_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.634784, -11.783104, -27.958477) x 
ihMT_ihMTRex_cosmod_exp19_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.634784, -11.783104, -27.958477) x
qT2_T2cutoff_fixed_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)  0.024 everywhere
qT2_short_gmT2_fixed_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)
ihMT_ihMTR_cosmod_exp19_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.634784, -11.783104, -27.958477) x
qT2_medium_gmT2_exp17_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271) all nan
ihMT_ihMTRex_T1d_exp18_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.634784, -11.783104, -27.958477) x
qT2_MWF_exp17_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)
qT2_MWF_fixed_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)
qT2_alpha_exp17_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)
qT2_T2cutoff_exp17_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)
qT2_short_gmT2_exp17_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271) all nan
qT2_FNR_exp17_BK02_HSC_BB2_C1_Rt1.nrrd : 			 (-2.287872, -12.153952, -27.955271)

Ones marked with x's are even more differently located
"""

# Alpha blend together two of the above images
img1 = sitk.ReadImage('qT2_medium_gmT2_fixed_BK02_HSC_BB2_C1_Rt1.nrrd')
img2 = sitk.ReadImage('qT2_FNR_exp17_BK02_HSC_BB2_C1_Rt1.nrrd')

mask1 = img1 != 0
mask2 = img2 != 0

intersection = mask1 * mask2
intersection = sitk.Cast(intersection, sitk.sitkFloat64)


alpha_blend = alpha * intersection * img1 + (1 - alpha) * intersection * img2

#sitk.Show(sitk.RescaleIntensity(intersection), 'intersection')
sitk.Show(sitk.RescaleIntensity(alpha_blend), 'alpha blend group B')

