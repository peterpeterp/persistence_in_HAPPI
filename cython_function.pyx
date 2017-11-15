from __future__ import division
from numpy cimport ndarray
import numpy as np
cimport numpy as np
cimport cython

ctypedef np.int32_t np_int_t
ctypedef np.float64_t np_float_t

def period_analysis(np.ndarray[np_int_t, ndim=1] ll, np.ndarray[np_int_t, ndim=1] mm, np.ndarray[np_float_t, ndim=1] tt):
  # cdef int n_per = ll.shape[0]
  n_per = ll.shape[0]
  cdef np.ndarray[np_int_t, ndim=1] ho = np.zeros([n_per], dtype=np.int32)
  cdef np.ndarray[np.float_t, ndim=1] cu = np.zeros([n_per], dtype=np.float64)

  for i in range(n_per):
    days=range(mm[i]-int(abs(ll[i])/2.),mm[i]+int(round(abs(ll[i])/2.)))
    cu[i]=np.nansum(tt[days])
    ho[i]=days[np.argmax(tt[days])]-mm[i]

  return cu,ho
