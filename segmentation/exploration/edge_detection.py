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

#sitk.Show(clipped_img)

# Approximate crop of the sphere
roi = [(280, 320), (65, 90), (8, 30)]

# Make mask of the cropped region
crop_mask = sitk.Image(spheres_img.GetSize(), sitk.sitkUInt8)
crop_mask.CopyInformation(spheres_img)
crop_mask[roi[0][0]:roi[0][1] + 1, roi[1][0]:roi[1][1] + 1, roi[2][0]:roi[2][1]] = 1


# Make histogram of the bright region
roi_intensity_values = arr[roi[2][0]:roi[2][1], roi[1][0]:roi[1][1], roi[0][0]:roi[0][1]]

plt.hist(roi_intensity_values.flatten(), bins=100)
plt.title("Intensity in ROI")
#plt.show()

# This is a bimodal distribution where the really bright parts correspond to the sphere
# Use otsu method to automatically choose a threshold to separate the sphere from the background
inside_value = 0
outside_value = 1
num_bins = 100
mask_output = True
mask_value = 1
seg_mask = sitk.OtsuThreshold(spheres_img,
                              crop_mask,
                              inside_value,
                              outside_value,
                              num_bins,
                              mask_output,
                              mask_value)

#sitk.Show(sitk.LabelOverlay(clipped_img, seg_mask))

# Edge detection approach
cropped_img = spheres_img[roi[0][0]:roi[0][1] + 1, roi[1][0]:roi[1][1] + 1, roi[2][0]:roi[2][1]]

edges = sitk.CannyEdgeDetection(sitk.Cast(cropped_img, sitk.sitkFloat32),
                                lowerThreshold=0.,
                                upperThreshold=200.,
                                variance=[5., 5., 5.])

#sitk.Show(edges)

# Transform an edge mask to a list of points in physical space
edge_indexes = np.where(sitk.GetArrayViewFromImage(edges) == 1.)


def get_physical_point(n):
    x = int(edge_indexes[2][n])
    y = int(edge_indexes[1][n])
    z = int(edge_indexes[0][n])
    return edges.TransformIndexToPhysicalPoint([x, y, z])


physical_points = list(map(get_physical_point,
                           range(len(edge_indexes[0]))))

# Determine the sphere that minimizes the distance from the points to the sphere
A = np.ones((len(physical_points), 4))
b = np.zeros(len(physical_points))

from scipy import linalg
for row, point in enumerate(physical_points):
    A[row, 0:3] = -2 * np.array(point)
    b[row] = -linalg.norm(point) ** 2

result = linalg.lstsq(A, b)[0]

center = result[0:3]
size = np.sqrt(linalg.norm(center)**2 - result[-1])
print('Center: ', center)
print('Radius: ', size)
