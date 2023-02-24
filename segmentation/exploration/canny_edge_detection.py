import os
import SimpleITK as sitk

os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'
file_name = '../../patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDensity_BK02_HSC_BB2_C1_Rt1.nii.gz'

img = sitk.ReadImage(file_name)
img_ldr = sitk.RescaleIntensity(img)

edge_filter = sitk.CannyEdgeDetectionImageFilter()
edge_filter.SetLowerThreshold(0.)
edge_filter.SetUpperThreshold(0.)
edge_filter.SetVariance(0.1)
edge_filter.SetMaximumError(0.1)

edges = edge_filter.Execute(img)

sitk.Show(edges, 'Canny Edges')
