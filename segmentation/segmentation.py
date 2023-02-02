import os
import SimpleITK as sitk

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

# Load images
T1 = sitk.ReadImage("../public_images/nac-hncma-atlas/A1_grayT1.nrrd")
T2 = sitk.ReadImage("../public_images/nac-hncma-atlas/A1_grayT2.nrrd")

# Cast to standard rgb ranges for showing
T1_ldr = sitk.Cast(sitk.RescaleIntensity(T1), sitk.sitkUInt8)
T2_ldr = sitk.Cast(sitk.RescaleIntensity(T2), sitk.sitkUInt8)

#sitk.Show(T1_ldr)
#input()
#sitk.Show(T2_ldr)
#input()


# Threshold filter
thresh = 170
seg_mask = T1 > thresh
#sitk.Show(sitk.LabelOverlay(T1_ldr, seg_mask))
#input()

# SITK Binary threshold
seg_mask = sitk.BinaryThreshold(T1,
                                lowerThreshold=100,
                                upperThreshold=400,
                                insideValue=1,
                                outsideValue=0)
#sitk.Show(sitk.LabelOverlay(T1_ldr, seg_mask))
#input()

# Histogram based thresholding
# Otsu's method
otsu_filter = sitk.OtsuThresholdImageFilter()
otsu_filter.SetInsideValue(0)
otsu_filter.SetOutsideValue(1)
seg_mask = otsu_filter.Execute(T1)
#sitk.Show(sitk.LabelOverlay(T1_ldr, seg_mask))
#print(otsu_filter.GetThreshold())

# Region Growing based segmentation
# Connected Threshold
seed = (132, 142, 96)  # Externally determined index that is good for the left lateral ventricle
seg_mask = sitk.Image(T1.GetSize(), sitk.sitkUInt8)
seg_mask.CopyInformation(T1)
seg_mask[seed] = 1
seg_mask = sitk.BinaryDilate(seg_mask, [3, 3, 3])  # Around the seed make every index within 3 voxels also 1
#sitk.Show(sitk.LabelOverlay(T1_ldr, seg_mask))

seg_mask = sitk.ConnectedThreshold(T1,
                                   seedList=[seed],
                                   lower=100,
                                   upper=190)
#sitk.Show(sitk.LabelOverlay(T1_ldr, seg_mask), 'Connected Threshold')

# Confidence Connected
seg_mask = sitk.ConfidenceConnected(T1,
                                    seedList=[seed],
                                    numberOfIterations=1,
                                    multiplier=2.5,
                                    initialNeighborhoodRadius=1,
                                    replaceValue=1)
#sitk.Show(sitk.LabelOverlay(T1_ldr, seg_mask), "Confidence Connected")

# Vector Confidence Connected
composite_image = sitk.Compose(T1, T2)
seg_mask = sitk.VectorConfidenceConnected(composite_image,
                                          seedList=[seed],
                                          numberOfIterations=1,
                                          multiplier=2.5,
                                          initialNeighborhoodRadius=1)
#sitk.Show(T2_ldr, "T2 ldr")
#sitk.Show(sitk.LabelOverlay(T2_ldr, seg_mask), "Vector Confidence Connected")

"""
# Fast marching segmentation
seed = (132, 142, 96)
feature_img = sitk.GradientMagnitudeRecursiveGaussian(T1, sigma=0.5)
speed_img = sitk.BoundedReciprocal(feature_img)
#sitk.Show(speed_img, "speed img")
#sitk.Show(feature_img, "feature_img")

fm_filter = sitk.FastMarchingBaseImageFilter()
fm_filter.SetTrialPoints([seed])
fm_img = fm_filter.Execute(speed_img)

sitk.Show(sitk.Threshold(fm_img,
                         lower=0.0,
                         upper=fm_filter.GetStoppingValue(),
                         outsideValue=fm_filter.GetStoppingValue() + 1))


seg_mask = fm_img < 400
sitk.Show(sitk.LabelOverlay(T2_ldr, seg_mask), "FM segmentation")
"""

# Level set based segmentation
seg_mask = sitk.Image(T1.GetSize(), sitk.sitkUInt8)
seg_mask.CopyInformation(T1)
seg_mask[seed] = 1
seg_mask = sitk.BinaryDilate(seg_mask, [3, 3, 3])

stats = sitk.LabelStatisticsImageFilter()  # This filter computes the distribution of intensity values in masked region
stats.Execute(T1, seg_mask)

# What is 3.5 sigma above and below the mean?
factor = 3.5
lower_thresh = stats.GetMean(1) - factor * stats.GetSigma(1)  # Here the 1 refers to the segmentation label
upper_thresh = stats.GetMean(1) + factor * stats.GetSigma(1)  # i.e. what is 1 sigma for the pixels masked by label 1
print('lower threshold = ', lower_thresh)
print('upper threshold = ', upper_thresh)

init_ls = sitk.SignedMaurerDistanceMap(seg_mask,
                                       insideIsPositive=True,
                                       useImageSpacing=True)

lsFilter = sitk.ThresholdSegmentationLevelSetImageFilter()
lsFilter.SetLowerThreshold(lower_thresh)
lsFilter.SetUpperThreshold(upper_thresh)
lsFilter.SetMaximumRMSError(0.02)
lsFilter.SetNumberOfIterations(1000)
lsFilter.SetCurvatureScaling(0.5)
lsFilter.SetPropagationScaling(1)
lsFilter.ReverseExpansionDirectionOn()
ls = lsFilter.Execute(init_ls, sitk.Cast(T1, sitk.sitkFloat32))

sitk.Show(sitk.LabelOverlay(T1_ldr, ls > 0))
