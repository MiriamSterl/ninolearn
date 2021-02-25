"""
STEP 0: START
Define the base folder as well as the current month and year.
Do not commit this file to your public repository!
"""

# =============================================================================
# FILL IN THE FOLLOWING
# =============================================================================

# directories
datadir = "" # full path to the directory where you want to save data
plotdir = "" # full path to the directory where you want to save plots
basedir = "" # full path to the root directory of the ninolearn package

# the current month (1-12) and year, as int
current_month = 0
current_year = 0


# =============================================================================
# Determining start of prediction period
# =============================================================================

if not isinstance(current_year,int):
    raise TypeError('current_year must be int')
    
if not isinstance(current_month,int):
    raise TypeError('current_month must be int')
    
if current_month<1 or current_month>12:
    raise ValueError('current_month must be a number between 1 and 12')


# the month and year for which the prediction starts
if current_month < 12:
    start_pred_m = current_month + 1
    start_pred_y = current_year
else:
    start_pred_m = 1
    start_pred_y = current_year + 1