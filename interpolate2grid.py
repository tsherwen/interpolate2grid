# ----------  Import modules ----------
#!/usr/bin/python
import numpy as np
from interpolate2grid_tools import *

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# ----------  Driver ----------
def main( case='chlorophyll', nc_data=None, nc_lat=None,\
        nc_lon=None, csv_lon=None, csv_lat=None, csv_time=None,\
        multidate=False, debug=True):
    """ 
    This program calls functions to extract data for a given cruise track 
    from a 2D (lon, lat) array. 

    Data is flagged if it is below 0. 
        
    Direct extraction of data, interpolated values, and locations are then  
    saved to CSV ( with dates included in the names if multiple dates
    provided )

    -------- README --------
    Setup output here - change variables names to columns headers 
    within given files
    
    Set "debug" to True to output a test plot and information on interpolation.
    
    Set "multidate" to True to output for multiple days
    
    Set case to be data input (to access stored varible names)
        e.g. 'sea ice' or 'chlorophyll'
    
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
#        pass
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

        # Interpolate, save to csv, and return values
        vals = extract_nearest_point_from_arr( data, lon, lat, locs,  \
            date=date, debug=debug )

        # Plot up test plot
        if debug:
            test_spatial_plot( data, lon, lat, locs, vals )
            
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# call to main/driver...
#debug=True
debug=False

# Setup for multidates/Rosie's data ( unhash to set )
multidate=True
#case='sea ice'
case='sea ice full'
main(multidate=multidate, case=case, debug=debug)

# Setup for single dates/Steve's data ( unhash to set )
#main()