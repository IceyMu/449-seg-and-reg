import os
import subprocess
import SimpleITK as sitk

#file = '/run/media/marcus/c0b18950-d75e-4fd2-a761-e3fdc1e863ec/Github/449-seg-and-reg/patient_data/BK02_HSC_BB2_C1_Rt1/DTI_MD_BK02_HSC_BB2_C1_Rt1.nii.gz'
#file = '/run/media/marcus/c0b18950-d75e-4fd2-a761-e3fdc1e863ec/Github/449-seg-and-reg/patient_data/BK02_HSC_BB2_C1_Rt1/DKI_RD_BK02_HSC_BB2_C1_Rt1.nii.gz'
file = '/run/media/marcus/c0b18950-d75e-4fd2-a761-e3fdc1e863ec/Github/449-seg-and-reg/patient_data/BK02_HSC_BB2_C1_Rt1/ActiveAx_AxonDiam_BK02_HSC_BB2_C1_Rt1.nii.gz'
sct_path = r'/home/marcus/sct_5.8/bin/'
os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

# Run deepseg gm segementation
#subprocess.call('{}sct_deepseg_gm -i {} -o output.nii.gz -qc ./qc/ -m large'.format(sct_path, file), shell=True)

# Run exvivo_gm-wm_t2
# A pre-req is to run sct_deepseg -install-task seg_exvivo_gm-wm_t2
#subprocess.call('{}sct_deepseg -task seg_exvivo_gm-wm_t2 -i {} -o output.nii.gz'.format(sct_path, file))

# Show results
img = sitk.ReadImage(file)
img_ldr = sitk.RescaleIntensity(img)
img_ldr = sitk.Cast(img_ldr, sitk.sitkUInt8)

#seg = sitk.ReadImage('output.nii.gz')
seg = sitk.ReadImage('output_gmseg.nii.gz')
seg = sitk.Cast(seg, sitk.sitkUInt8)

sitk.Show(sitk.LabelOverlay(img_ldr, seg))
