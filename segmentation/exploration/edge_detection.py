# Edge detection
import os
import SimpleITK as sitk
import numpy as np
import matplotlib.pyplot as plt


os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

spheres_img = sitk.ReadImage("../../public_images/spherical_fiducials.mha")

arr = sitk.GetArrayViewFromImage(spheres_img)
#plt.hist(arr.flatten(), bins=200)
#plt.title("Intensity values")
#plt.show()

# Clip extremely bright spots
clipped_img = sitk.Cast(sitk.IntensityWindowing(spheres_img,
                                                windowMinimum=float(arr.min()),
                                                windowMaximum=-30000.,
                                                outputMinimum=0.,
                                                outputMaximum=255.),
                        sitk.sitkUInt8)

sitk.Show(clipped_img)

roi = [(280, 320), (65, 90), (8, 30)]

# Make histogram of the bright region
roi_intensity_values = arr[roi[2][0] : roi[2][1], roi[1][0] : roi[1][1], roi[0][0] : roi[0][1]]

plt.hist(roi_intensity_values.flatten(), bins=100)
plt.title("Intensity in ROI")
plt.show()
