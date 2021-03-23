"""
STEP 0: START
Define the base folder as well as the current month and year.
Do not commit this file to your public repository!
"""

# =============================================================================
# FILL IN THE FOLLOWING
# =============================================================================

# directories
basedir = "" # full path to the root directory of the ninolearn folder
datadir = "" # full path to the directory where you want to save data

# the month (1-12) and year where you want to start a 9-month prediction, as int
start_pred_m = 
start_pred_y = 

# =============================================================================
# Determining start of prediction period
# =============================================================================

if not isinstance(start_pred_y,int):
    raise TypeError('start_pred_y must be int')
    
if not isinstance(start_pred_m,int):
    raise TypeError('start_pred_m must be int')
    
if start_pred_m<1 or start_pred_m>12:
    raise ValueError('start_pred_m must be a number between 1 and 12')

