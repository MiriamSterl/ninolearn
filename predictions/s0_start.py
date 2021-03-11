"""
STEP 0: START
Define the base folder as well as the current month and year.
Do not commit this file to your public repository!
"""

# =============================================================================
# FILL IN THE FOLLOWING
# =============================================================================

# directories
basedir = "C:/Users/miria/Documents/Studie/Ninolearn project/ninolearn" # full path to the root directory of the ninolearn folder
datadir = "C:/Users/miria/Documents/Studie/Ninolearn project/Data" # full path to the directory where you want to save data

# the month (1-12) and year where you want the prediction to start, as int
# if you want to make a new prediction, fill in the current month and year.
start_pred_m = 1
start_pred_y = 2021

# =============================================================================
# Determining start of prediction period
# =============================================================================

if not isinstance(start_pred_y,int):
    raise TypeError('start_pred_y must be int')
    
if not isinstance(start_pred_m,int):
    raise TypeError('start_pred_m must be int')
    
if start_pred_m<1 or start_pred_m>12:
    raise ValueError('start_pred_m must be a number between 1 and 12')


# the month and year for which the prediction starts
# if current_month < 12:
#     start_pred_m = current_month + 1
#     start_pred_y = current_year
# else:
#     start_pred_m = 1
#     start_pred_y = current_year + 1

#print("Step 0 finished, continue to step 1!")