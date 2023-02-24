import SimpleITK
import numpy as np


def np_to_sitk_indexing(arr):
    # Changes the indexing of a numpy array to such that the axes match what SimpleITK expects
    # NOTE something about numpy array indexing doesn't work inside this function where it works in place outside the
    # function
    return arr[: [2, 1, 0]]


def normalize_brightness_along_z(img):
    # Given a sitk image return that image with each z slice scaled to have the same mean intensity

    # Get mean intensity of each slice
    arr_view = SimpleITK.GetArrayViewFromImage(img)
    mean_intensity_vec = np.apply_over_axes(np.mean, arr_view, [1, 2])

    # Generate array with the correct scaling values
    inv_mean_int_vec = np.reciprocal(mean_intensity_vec,
                                     where=mean_intensity_vec.astype(np.bool_))
    normalization_arr = np.ones_like(arr_view)
    normalization_arr *= inv_mean_int_vec

    # Convert the scaling array to a sitk image and apply
    output_img = SimpleITK.GetImageFromArray(normalization_arr)
    output_img.SetSpacing(img.GetSpacing())
    output_img.SetOrigin(img.GetOrigin())
    output_img.SetDirection(img.GetDirection())
    output_img *= img

    return output_img
