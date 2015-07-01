
Values are ouputted for lon., lat.,  directly extracted data, and interpolated data
for given coordinates. Interpolated values are provided to nearest value and the 
grid is interpolated for missing data.

These values are then saved to CSV, with dates included in the names if multiple
dates are provided.

Three call options ('sea ice', 'sea ice full' & 'chlorophyll') are provided 
within the main programme at the bottom. To use alteratives, just change the input 
variables as described within 'main' or add additional sets of variables to the 
dictionary in interpolate2grid_tools's fucntion named 'var_store'.

interpolate2grid_tools holds fucntions for the main programme interpolate2grid.

--- Advice for use 
 - Data should be dates should be provided in format ( YYYY/MM/DD HH:MM ) to 
   avoid parser errors between date formats
 - Be cautious of oversampling in low resolution inputs are provide compared 
   to requested frequenty of input observations.
