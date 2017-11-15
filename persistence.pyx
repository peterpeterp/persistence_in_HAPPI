from __future__ import division
from numpy cimport ndarray
import numpy as np
cimport numpy as np
cimport cython

ctypedef np.int32_t np_int_t
ctypedef np.float64_t np_float_t

def period_identifier_cy(np.ndarray[np_int_t, ndim=1] ind):
  cdef int Ni=ind.shape[0]
  cdef np.ndarray[np_int_t, ndim=1] pers = np.zeros([Ni], dtype=np.int32)
  cdef int state=ind[0]
  cdef int count=1

  for i in range(1,Ni):
    if ind[i]==state:
      count+=1
    if ind[i]!=state:
      pers[i-count//2-1]=state*count
      count=0
      if ind[i]!=99:
        state*=-1
        count=1

  # still an issue with last spell??
  if state==1:	pers[i-count/2]=state*count
  if state==-1:	pers[i-count/2]=state*count

  return pers
