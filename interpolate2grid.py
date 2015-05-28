# ----------  Import modules ----------
#!/usr/bin/python
import sys
from netCDF4 import Dataset
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import scipy.stats as stats

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ----------  Functions ----------
def processinputfiles( nc_dataname='l3m_data', nc_latname='G3fakeDim0',  \
            nc_lonname='G3fakeDim1', csv_lonname='LONG', csv_latname='LAT', \
            debug=False):
    """ 
    Extract and standardise input data to array form from given NetCDF 
    and CSV files 
    """
    # --- Get Array file (HDF) and file of lats and lons from 1st and 2nd 
    # arguments respectively
    arr_file = sys.argv[1]
    locs_file = sys.argv[2]
    if debug:
        print arr_file, locs_file

    # --- Extract Data, lat and lon from NetCDF
    with  Dataset(arr_file, 'r', format='classic') as f:
        if debug:
            print f
            print f.variables
        lon= f.variables[nc_lonname]
        lat =  f.variables[nc_latname]
        data = f.variables[nc_dataname]
        lon, lat, data = [ np.array(i) for i in  lon, lat, data ]
    if debug:
        print [ [type(i), i.shape] for i in lon, lat, data ]

    # --- Extract Location lat and lons & conv. to DataFrame (LON, LAT)
    df =pd.read_csv( locs_file )
    locs =  pd.DataFrame( [df[csv_lonname], df[csv_latname] ]  )
    del df
    return data.T, lon, lat, locs.values

def interpolate_locs2grid( data, lon, lat, locs  ):
    """ 
    Interpolate over given array (data) for locations (locs) at Lon. and Lat. , 
     returning values 
    """
    # --- Interpolate over given array
    lo,la = np.meshgrid(lon, lat)
    print type( data )
    vals = griddata((lo.ravel(),la.ravel()) , data.ravel(), locs.T, method='linear' )# [0,:], locs[1,:] )
    return vals    

def nan_helper(y):
    """
    Helper to handle indices and logical indices of NaNs.
    Input:
        - y, 1d numpy array with possible NaNs
    Output:
        - nans, logical indices of NaNs
        - index, a function, with signature indices= index(logical_indices),
          to convert logical indices of NaNs to 'equivalent' indices
    credit: http://stackoverflow.com/users/579145/eat
                
                  http://stackoverflow.com/questions/6518811/interpolate-nan-values-in-a-numpy-array
    """
    return np.isnan(y), lambda z: z.nonzero()[0]

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ----------  Driver ----------
def main( nc_dataname='l3m_data', nc_latname='G3fakeDim0',\
        nc_lonname='G3fakeDim1'  ,csv_lonname='LONG', csv_latname='LAT',\
        debug=True):
    """ 
    Setup output here - change variables names to columns headers 
    within given files
    
    Set "debug" to True to output a test plot and information on interpolation.
    
    Variables are:
    nc_dataname : Name of data variable in NetCDF file
    nc_latname : Name of latitude variable in NetCDF file
    nc_lonname : Name of longitude variable in NetCDF file
    csv_lonname : Name of longitude variable in CSV file
    csv_latname : Name of latitude variable in CSV file                 
    """ 

    # ---------- 
    # Get files and process to arrays, then mask for values below 0
    data, lon, lat, locs  = processinputfiles(nc_dataname=nc_dataname,   \
            nc_latname=nc_latname, nc_lonname=nc_lonname,  \
            csv_lonname=csv_lonname, csv_latname=csv_latname)
    print [ 
    [np.ma.min(i), np.ma.max(i), np.ma.mean(i), np.ma.std(i) ] for i in [data] 
    ]

    # Interpolate over given array and create flag array for masked values
    flags  = interpolate_locs2grid( data, lon, lat, locs  )
    flags[flags>0] = 0
    flags[ flags<0] =1

    # Interpolate for masked values (those below zero) and provide values 
    data[data<0]=np.nan
    nans, x= nan_helper(data)
    data[nans]= np.interp(x(nans), x(~nans), data[~nans])
    if debug:
        print [ 
        [np.ma.min(i), np.ma.max(i), np.ma.mean(i), np.ma.std(i) ] 
        for i in [data] ]
        print [ (i.shape, type(i)) for i in data, lon, lat, locs]

    # Interpolate over interpolated array
    vals  = interpolate_locs2grid( data, lon, lat, locs  )

    # Print output to csv
    output_file = './interpolated_values.csv'
    print vals.shape
    lo,la = np.meshgrid(lon, lat)
    print [i.shape for i in  flags, vals, la.ravel(), lo.ravel() ]
    df = pd.DataFrame( {'Interp. Values': vals, 'Lon.':locs[0,:], 
                'Lat.':locs[1,:], 'flag': flags } )
    df.to_csv( output_file )

    # Plot up test plot
    if debug:
        fig = plt.figure(figsize=(20,15), dpi=80, facecolor='w', edgecolor='k')
#    vmin, vmax = data.min(), data.max()
        vmin, vmax = 0, data.max()
        cmap=plt.cm.Greens
        s_z = [ 
        cmap(  (float(i) - vmin) / ( np.array([vmin,vmax]) ).ptp() )  \
        for i in vals ]
        print vmin, vmax
        plt.pcolor( lon, lat, data.T, cmap=plt.cm.Blues, vmin=vmin, vmax=vmax )
        plt.scatter( locs[0,:], locs[1,:] , cmap=plt.cm.Greens, c=vals, \
                vmin=vmin, marker='x', vmax=vmax  )    
        plt.show()
    
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# call to main/driver...
main()
