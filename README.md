
Return values in a provided lon. and lat. data grid for given coordinates, 
interpolating to nearest value and interpolating for missing data within grid.

Direct extraction of data, interpolated values, and locations are then  
saved to CSV ( with dates included in the names if multiple dates
provided 

Three call options ('sea ice', 'sea ice full' & 'chlorophyll') are provided 
within the main programme at the end. To usealteratives, just change the input 
vaiables as described within the main oradd additional sets of variables to the 
dictionary in interpolate2grid_tools'sfucntion named "var_store"

interpolate2grid_tools holds fucntions for the main programme interpolate2grid.

--- Advice for use 
 - Data should be dates should be provided in format ( YYYY/MM/DD HH:MM ) to 
   guarantee avoiding parser errors
 - Be cautious of oversampling in low resolution inputs are provide compared 
   to requested frequenty of input observations.
