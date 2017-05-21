

import scipy.ndimage.filters as flt

import numpy as np

import pandas as pd







def gaussian(dataSet,args):

    dataTemp = np.asarray(dataSet)

    dataGaussian = flt.gaussian_filter(dataTemp,int(args[0]))



    return dataGaussian



def variance(dataSet,args):



    dataTemp = np.asarray(dataSet)

    dataVariance = dataTemp.var(axis=0)



    return dataVariance





def stddev(dataSet,args):



    dataTemp = np.asarray(dataSet)

    dataStdDev = dataTemp.std(axis=0)



    return dataStdDev