# Test that the pycharm environment works

import numpy
import matplotlib
import scipy
import pandas
import numba
import multiprocess
import SimpleITK as sitk

import os
os.environ['SITK_SHOW_COMMAND'] = '/usr/bin/fiji'

sitk.Show(sitk.ReadImage('public_images/external-content.duckduckgo.com.jpg'))
