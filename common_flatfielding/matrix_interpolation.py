import numpy as np
import numba as nb
from numba import prange

@nb.njit(nb.float64[:,:,:](nb.float64[:,:,:],nb.float64[:,:,:],nb.float64[:]))
def interpolate_matrix_3d(x_arr, xf_matrix, y_frames):
    T, W, H = x_arr.shape
    result = np.zeros(shape=(T,W,H))
    for i in range(W):
        for j in range(H):
            x = x_arr[:,i,j]
            xf = xf_matrix[:,i,j]
            yf = y_frames
            result[:,i,j] = np.interp(x,xf,yf)
    return result

@nb.njit(nb.float64[:,:](nb.float64[:,:],nb.float64[:,:,:],nb.float64[:]))
def interpolate_matrix_2d(x_arr, xf_matrix, y_frames):
    W, H = x_arr.shape
    result = np.zeros(shape=(W,H))
    for i in range(W):
        for j in range(H):
            x = x_arr[i,j]
            xf = xf_matrix[:,i,j]
            yf = y_frames
            result[i,j] = np.interp(x,xf,yf)
    return result

def interpolate_matrix(x_arr, xf_matrix, y_frames):
    if len(x_arr.shape)==3:
        return interpolate_matrix_3d(x_arr, xf_matrix, y_frames)
    else:
        return interpolate_matrix_2d(x_arr, xf_matrix, y_frames)