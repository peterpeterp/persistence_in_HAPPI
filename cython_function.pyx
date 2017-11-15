from __future__ import division
from numpy cimport ndarray
import numpy as np
cimport numpy as np
cimport cython

ctypedef np.int32_t np_int_t
ctypedef np.float64_t np_float_t

def period_analysis_cy(np.ndarray[np_int_t, ndim=3] ll, np.ndarray[np_int_t, ndim=3] mm, np.ndarray[np_int_t, ndim=3] sea, np.ndarray[np_int_t, ndim=2] mask, np.ndarray[np_float_t, ndim=3] tt, int Ni, int Nx, int Ny):
  cdef np.ndarray[np_int_t, ndim=3] ho = np.zeros([Ni,Ny,Nx], dtype=np.int32)
  cdef np.ndarray[np.float_t, ndim=3] cu = np.zeros([Ni,Ny,Nx], dtype=np.float64)
  for x in range(Nx):
    for y in range(Ny):
      for i in range(Ni):
        if sea[i,y,x]==1 and mask[y,x]==1:
          days=range(mm[i,y,x]-int(abs(ll[i,y,x])/2.),mm[i,y,x]+int(round(abs(ll[i,y,x])/2.)))
          cu[i,y,x]=np.nansum(tt[days,y,x])
          ho[i,y,x]=days[np.argmax(tt[days,y,x])]-mm[i,y,x]
  return  cu,ho

def period_analysis_full(np.ndarray[np_int_t, ndim=1] ids, np.ndarray[np_int_t, ndim=2] coord, np.ndarray[np_int_t, ndim=3] ll, np.ndarray[np_int_t, ndim=3] mm, np.ndarray[np_float_t, ndim=3] tt, int nx, int ny):
  cdef int N = ids.shape[0]
  cdef int Ncoord = coord.shape[0]
  cdef np.ndarray[np_int_t, ndim=3] ho = np.zeros([N,ny,nx], dtype=np.int32)
  cdef np.ndarray[np.float_t, ndim=3] cu = np.zeros([N,ny,nx], dtype=np.float64)
  for co in range(Ncoord):
    for i in range(N):
      days=range(mm[i,coord[co,0],coord[co,1]]-int(abs(ll[i,coord[co,0],coord[co,1]])/2.),mm[i,coord[co,0],coord[co,1]]+int(round(abs(ll[i,coord[co,0],coord[co,1]])/2.)))
      cu[i,coord[co,0],coord[co,1]]=np.nansum(tt[days,coord[co,0],coord[co,1]])
      ho[i,coord[co,0],coord[co,1]]=days[np.argmax(tt[days,coord[co,0],coord[co,1]])]-mm[i,coord[co,0],coord[co,1]]
  return  cu,ho


# def period_analysis_single(np.ndarray[np_int_t, ndim=1] ll, np.ndarray[np_int_t, ndim=1] mm, np.ndarray[np_float_t, ndim=1] tt):
#   cdef int n_per = ll.shape[0]
#   cdef np.ndarray[np_int_t, ndim=1] ho = np.zeros([n_per], dtype=np.int32)
#   cdef np.ndarray[np.float_t, ndim=1] cu = np.zeros([n_per], dtype=np.float64)
#
#   for i in range(n_per):
#     days=range(mm[i]-int(abs(ll[i])/2.),mm[i]+int(round(abs(ll[i])/2.)))
#     cu[i]=np.nansum(tt[days])
#     ho[i]=days[np.argmax(tt[days])]-mm[i]
#
#   return cu,ho
