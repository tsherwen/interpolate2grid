# ----------  Import modules ----------
#!/usr/bin/python
import numpy as np
from interpolate2grid_tools import *

# --- Set debug/output setting
VERBOSE=False
DEBUG=False

# -- Settings for direct call to driver ('main')
# Setup for multidates/Rosie's data ( unhash to set )
#multidate=True
#case='sea ice full'

# Setup for single dates/Steve's data ( unhash to set )
#multidate=False
#case='sea ice'

# Setup for Sea surface temperature (SST) for Sina
multidate=True                                                                                                                                                                               
case='SST' 


# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ----------  Driver ----------
def main( case='chlorophyll', nc_data=None, nc_lat=None,\
        nc_lon=None, csv_lon=None, csv_lat=None, csv_time=None,\
        multidate=False, verbose=False, debug=True):
    """ 
    This program calls functions to extract data for a given cruise track 
    from a 2D (lon, lat) array. 

    Data is flagged if it is below 0. 
        
    Direct extraction of data, interpolated values, and locations are then  
    saved to CSV ( with dates included in the names if multiple dates
    provided )

    -------- README --------
    Output is set by arguement variables ( but these are expected to be updated in call. )

    Setup driver call using a new case (add to 'var_store' in  'interpolate2grid_tools.py' ), 
    ( e.g. change variables names to columns headers within given files)
    
    Set "debug" to True to output a test plot and provide information on interpolation.
    
    Set "multidate" to True to output for multiple days
    
    Set case to be data input (to access stored variable names)
        e.g. 'sea ice' or 'chlorophyll' or 'SST' ...
    
    Variables are:
    nc_data : Name of data variable in NetCDF file
    nc_lat : Name of latitude variable in NetCDF file
    nc_lon : Name of longitude variable in NetCDF file
    csv_lon : Name of longitude variable in CSV file
    csv_lat : Name of latitude variable in CSV file                 
    """ 
    
    # Get files containing data
    arr_file, locs_file = get_input_files()
    
    # Retrieve variables for data files  (Unless these are given)
    vars = nc_data, nc_lat, nc_lon, csv_lon, csv_lat, csv_time
    if any( [ isinstance( i, type(None) ) for i in vars ] ):
        vars = var_store(case)
        nc_data, nc_lat, nc_lon, csv_lon, csv_lat, csv_time = vars
    if debug:
        print vars

    # Extract and give output data on a day by day basis ( if mulitdate==True) 
    if multidate:
        dates = get_obs_dates( locs_file, csv_time=csv_time) 
        dates= dates[1:] # Kludge to test for 1st date prior to NetCDF array.
    else:
        # Only process for the single date
        dates = [None]  

    # ----------         
    for date in dates:

        # Get locations of cruise from CSV
        locs = extract_CSV( locs_file, date=date, csv_lon=csv_lon, \
                csv_lat=csv_lat, csv_time=csv_time,debug=debug )

        # Get NetCDF data to extract from
        data, lon, lat = extract_NetCDF(arr_file, date=date,\
                nc_data=nc_data, format=format,\
                nc_lat=nc_lat, nc_lon=nc_lon, debug=debug)

        if debug:
            print '>'*10, [   [i.min(), i.max(), i.mean(), i.std() ] for i in\
                [np.ma.array(ii) for ii in lat, lon, data, locs ]  ]

        # Extract, interpolate, save to csv, and return values
        vals = extract_nearest_point_from_arr( data, lon, lat, locs,  \
            date=date, case=case, debug=debug )

        # Plot up test plot
        if debug:
            test_spatial_plot( data, lon, lat, locs, vals )
            
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Call main driver?
if __name__ == "__main__":
    main(multidate=multidate, case=case, verbose=VERBOSE, debug=DEBUG)
