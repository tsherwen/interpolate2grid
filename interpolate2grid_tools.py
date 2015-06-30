# ----------  Import modules ----------
#!/usr/bin/python
import sys
from netCDF4 import Dataset
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import scipy.stats as stats

# time processing
import datetime
from datetime import datetime as datetime_
import dateutil
import time
from time import mktime

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ----------  Functions ----------

def get_input_files(debug=False):
    """
    Get Array file (NC) and file of lats and lons from 1st and 2nd 
    arguments respectively
    """
    arr_file = sys.argv[1]
    locs_file = sys.argv[2]
    if debug:
        print arr_file, locs_file
    return  arr_file, locs_file

def extract_NetCDF( arr_file, date=None, format='classic',\
            nc_lat='G3fakeDim0', nc_data='l3m_data',\
            nc_lon='G3fakeDim1', nc_time='time', debug=False):
    """ 
    Extract and standardise input data to array form from given NetCDF 
    and CSV files 
    """
    # --- Extract Data, lat and lon from NetCDF
    with  Dataset(arr_file, 'r', format=format) as f:
        if debug:
            print f
            print f.variables

        # extract data for a given date or assume single dataset if no
        # date given
        if isinstance(date, type(None) ):
            lon= f.variables[nc_lon]
            lat =  f.variables[nc_lat]
            data = f.variables[nc_data]
        else:
            lon= f.variables[nc_lon]
            lat =  f.variables[nc_lat]
            data = f.variables[nc_data] 
            dates = f.variables[nc_time]
                        
            # convert (NetCDF) time to datetime
            ANSI = time.strptime(dates.units[11:], '%Y-%m-%d %H:%M:%S')
            ANSI = datetime.datetime( *ANSI[:6] )
            dates = [ add_days( ANSI, i ) for i in dates ]
            dates = np.array([
            datetime.datetime(*i.timetuple()[:3]) for i in dates
            ] )
            # Select given date 
            if debug:
                print dates
                print date
                print data.shape
            if date in dates:
                data = data[dates==date,...][0,...]
            else:
                print 'ERROR: obs. date not in NetCDF dates: {}'.format( date, dates )
                print 'STOPPING PROGRAMME, USE SINGLE DATE VERSION OR ADD DATE TO NETCDF'
                sys.exit( 0)
            if debug:
                print [ i.shape for i in data, lon, lat ]

        lon, lat, data = [ np.array(i) for i in  lon, lat, data ]
    if debug:
        print [ [type(i), i.shape] for i in lon, lat, data ]
    return data.T, lon, lat

def extract_CSV( locs_file, csv_lon='LONG', csv_lat='LAT',  \
            csv_time=None, date=None, debug=False):
    """
        Extract Location lat and lons & conv. to DataFrame (LON, LAT)
        
        If date is given, only return data for this date
    """
    df =pd.read_csv( locs_file )
    if isinstance(date, type(None)):
        locs =  pd.DataFrame( [df[csv_lon], df[csv_lat] ] ).values
    else:
        # retrieve dates and only consdier daily resolution
        dates =  df[csv_time].apply(dateutil.parser.parse)
        dates = [datetime.datetime(*i.timetuple()[:3]) for i in dates] 
        if debug:
            print [type(i) for i in df[csv_lon], df[csv_lat], dates ]
        locs =  pd.DataFrame( {csv_lon:df[csv_lon].values, 
                        csv_lat:df[csv_lat].values, csv_time:dates} )    
        if debug:
            print 'all locs:',  locs
        locs = locs[locs[csv_time]==date]
        locs = np.array( [ locs[csv_lon].values, locs[csv_lat].values] )
        if debug:
            print 'locs for given date: {}'.format( date ), locs
        
    del df
    return locs

def get_obs_dates( locs_file, csv_time='yyyy-mm-ddThh24:mi[GMT/UT]' ,\
            debug=False):
    """
        Extract Location lat and lons & conv. to DataFrame (LON, LAT)
    """
    df =pd.read_csv( locs_file )
    dates =  df[csv_time].apply(dateutil.parser.parse)    
    del df
    # get unique list of days
    dates = sorted( set( [ 
    datetime.datetime(*i.timetuple()[:3]) for i in dates 
    ] ))

    return dates

def interpolate_locs2grid( data, lon, lat, locs, debug=False ):
    """ 
        Interpolate over given array (data) for locations (locs) at Lon. 
        and Lat. , returning values 
    """
    # --- Interpolate over given array
    lo,la = np.meshgrid(lon, lat)
    if debug:
        print '>'*5, type( data ), locs.shape
    vals = griddata((lo.ravel(),la.ravel()) , data.ravel(),    \
                        locs.T, method='linear' )# [0,:], locs[1,:] )
    return vals

def add_days(sourcedate,days_):
    """
        Incremental increase datetime by given days
    """
    sourcedate += datetime.timedelta(days=days_)
    return sourcedate

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

def var_store( case='sea ice'):
    """
        Store of variables name for data extractions, e.g. Sea Ice/Chlorophyll
    """

    # Translate case
    case = {
    'chlorophyll' : 0,    
    'sea ice' : 1 ,
    'sea ice full' : 2
    }[case]

    if case == 0:
        nc_data='l3m_data'
        nc_lat='G3fakeDim0'
        nc_lon='G3fakeDim1'
        csv_lon='LONG'
        csv_lat='LAT'
        csv_time=None
#        format='classic'

    if case == 1:
        nc_data='Sea_Ice_Concentration_with_Final_Version'
        nc_lat='latitude'
        nc_lon='longitude'
#        csv_lon='seatex-gga-lon (degrees)'
#        csv_time='Timestamp'
#        csv_lat=' seatex-gga-lat (degrees)'
        csv_lat='Latitude[deg+veN]'
        csv_lon='Longitude[deg+veE]'
        csv_time='yyyy-mm-ddThh24:mi[GMT/UT]'
#        format='classic'

    if case == 2:
        nc_data='Sea_Ice_Concentration_with_Final_Version'
        nc_lat='latitude'
        nc_lon='longitude'

        csv_lat=' seatex-gga-lat (degrees)'
        csv_lon=' seatex-gga-lon (degrees)'
#        csv_time='dd/mm/yyyy  hh24:mi:ss'
        csv_time='Timestamp'
#        format='classic'

    return nc_data, nc_lat, nc_lon, csv_lon, csv_lat, csv_time

def test_spatial_plot( data, lon, lat, locs, vals, cmap=plt.cm.Greens ):
    """
        Plot up a surface of grided data given with extracted values overlaid
    """
    fig = plt.figure(figsize=(20,15), dpi=80, facecolor='w', edgecolor='k')
    vmin, vmax = data.min(), data.max()
    #    vmin, vmax = 0, data.max()
    s_z = [ 
    cmap(  (float(i) - vmin) / ( np.array([vmin,vmax]) ).ptp() )  \
    for i in vals ]
#    s_z = np.array( s_z )
    print vmin, vmax, s_z
    plt.pcolor( lon, lat, data.T, cmap=plt.cm.Blues, vmin=vmin, vmax=vmax )
    plt.scatter( locs[0,:], locs[1,:], cmap=plt.cm.Greens, c=s_z, \
                            vmin=vmin, marker='x', vmax=vmax  )    
    plt.show()


def extract_nearest_point_from_arr( data, lon, lat, locs, date=None, \
            output_filename='./interpolated_values', debug=False ):
    """
        Interpolate data to grid to account for missing data.
        
        Data is flagged if it is below 0. 
        
        Direct extraction of data, interpolated values, and locations are then  
        saved to CSV ( with dates included in the names if multiple dates
        provided )

    """
    # Is location within provided grid?
    out_lon = [ n for n, i in  enumerate( locs[0,:] ) if 
            ( ( i<np.min(lon) ) or (i>np.max(lon) ) ) ]
    out_lat =  [ n for n, i in  enumerate( locs[1,:] ) if 
                ( ( i<np.min(lat) ) or (i>np.max(lat) ) ) ]
    indexs =sorted( set(out_lon+out_lat ) )
    
    print '!'*100, 'REMOVED: CRUISE POINT(s) OUT OF PROVIDED GRID WITH  \
LAT+LON: {} '.format( [ list(locs[:,i]) for i in indexs] )
    if debug:
        print [ (i, type(i), i.shape) for i in [locs] ]
    for index in indexs[::-1]:
        locs = np.delete( locs, index, 1)
    if debug:
        print [ (i, type(i), i.shape) for i in [locs] ]
    print locs

    # Interpolate over given array and create flag array for masked values
    flags  = interpolate_locs2grid( data, lon, lat, locs )
    raw_extract = flags.copy()
    if debug:
        print flags
    flags[flags>0] = 0
    flags[ flags<0] =1
    if debug:
        print flags
    
    # Interpolate for masked values (those below zero) and provide values 
    if len(data[data<0]) > 0:
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
    if not isinstance( date, type(None) ): 
        output_filename=output_filename+'{}_{}_{}'.format( date.year, \
            date.month, date.day )

    print vals.shape
    lo,la = np.meshgrid(lon, lat)
    print [i.shape for i in  flags, vals, la.ravel(), lo.ravel() ]
    df = pd.DataFrame( {
    'Interpolated values': vals, 
    'Longitude':locs[0,:], 
    'Latitude':locs[1,:], 
    'Raw extracted values': raw_extract,
    'Flag': flags, } )
    df.to_csv( output_filename+'.csv' )
    return vals



