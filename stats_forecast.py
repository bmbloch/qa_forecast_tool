import pandas as pd
import numpy as np
import itertools
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
import time
from scipy.stats import zscore
from IPython.core.display import display, HTML
from pathlib import Path
import math

# Function that drops columns of the dataframe that will be recalculated each time a sub is examined for flags
def drop_cols(data_in):

    dataframe = data_in.copy()

    cols = dataframe.columns
    index = list(dataframe.columns).index("Recalc Insert")
    drop_list = cols[index :]
    dataframe = dataframe.drop(columns = drop_list, axis = 1)
        
    return dataframe

# Function that calculates the percentage change for select variables, to handle the need to calculate year over year in some cases and quarter over quarter in others
def calc_chg(data_in, variable, variable_name, curryr, currqtr, sector_val):

    data = data_in.copy()

    if currqtr == 4:
        period = 1
    else:
        period = currqtr + 1

    data[variable_name] = np.where((data['yr'] < curryr) & (data['qtr'] != 5) & (data['identity'] == data['identity'].shift(1)), data[variable] - data[variable].shift(1), np.nan)
    data[variable_name] = np.where((data['yr'] < curryr) & (data['qtr'] == 5) & (data['identity'] == data['identity'].shift(5)), data[variable] - data[variable].shift(5), data[variable_name])
    data[variable_name] = np.where((data['yr'] < curryr) & (data['qtr'] == 5) & (data['identity'] == data['identity'].shift(1)) & (((data['qtr'].shift(2) == 5) | (data['identity'] != data['identity'].shift(2)))), data[variable] - data[variable].shift(1), data[variable_name])
    data[variable_name] = np.where((data['yr'] == curryr) & (data['qtr'] != 5), data[variable] - data[variable].shift(1), data[variable_name])
    data[variable_name] = np.where((data['yr'] == curryr) & (data['qtr'] == 5), data[variable] - data[variable].shift(period), data[variable_name])
    data[variable_name] = np.where((data['yr'] > curryr) & (data['qtr'] == 5), data[variable] - data[variable].shift(1), data[variable_name])

    return data

# Function to calculate the min and max historical point for key metrics
def min_max(data_in, variable, curryr):

    data = data_in.copy()

    col_name_min = "min_" + variable
    col_name_max = "max_" + variable
    if variable == 'vac' or variable == 'gap_chg' or variable == 'gap':
        data[col_name_min] = data[(data['forecast_tag'] == 0) & (data['yr'] >= curryr - 10)].groupby('identity')[variable].transform('min')
        data[col_name_max] = data[(data['forecast_tag'] == 0) & (data['yr'] >= curryr - 10)].groupby('identity')[variable].transform('max')
    elif variable == 'G_mrent':
        data[col_name_min] = data[(data['forecast_tag'] == 0) & (data['qtr'] == 5) & (data['yr'] >= curryr - 10)].groupby('identity')[variable].transform('min')
        data[col_name_max] = data[(data['forecast_tag'] == 0) & (data['qtr'] == 5) & (data['yr'] >= curryr - 10)].groupby('identity')[variable].transform('max')
    
    data = fill_forward(data, col_name_min, 'identity_fill_1')
    data = fill_forward(data, col_name_max, 'identity_fill_1')

    return data

# Function that will "drag down" the applicable stat into subsequent periods when neccesary
def fill_forward(data_in, variable, get_row):

    data = data_in.copy()

    data[variable] = np.where((data['forecast_tag'] != 0), data.loc[data[get_row]][variable], data[variable])
    if get_row == 'identity_fill_2':
        data[variable] = np.where(data['forecast_tag'] == 1, data[variable], np.nan)

    return data

# Function that will determine how much construction stock has not yet been absorbed
def calc_missing_cons_abs(data_in, curryr, currqtr):

    data = data_in.copy()

    # First, identify if a year has construction that wasnt absorbed
    # If there is no cons in the year in question, then the missing abs is not related to construction absorption
    if currqtr != 4:
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] >= data['curr_yr_trend_cons']), data['implied_cons'], np.nan)
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] < data['curr_yr_trend_cons']) & (data['total_trend_abs'] >= 0), data['implied_cons'] + (data['curr_yr_trend_cons'] - data['total_trend_abs']), data['cons_use'])
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] < data['curr_yr_trend_cons']) & (data['total_trend_abs'] < 0), data['cons'], data['cons_use'])
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] == 0), data['cons'], data['cons_use'])
        data['missing_abs'] = np.where((data['yr'] >= curryr - 3) & (data['qtr'] == 5) & (data['forecast_tag'] != 1), data['cons'] - data['abs'], 0)
        data['missing_abs'] = np.where((data['yr'] >= curryr - 3) & (data['qtr'] == 5) & (data['forecast_tag'] == 1), data['cons_use'] - data['implied_abs'], data['missing_abs'])
    elif currqtr == 4:
        data['missing_abs'] = np.where((data['yr'] >= curryr - 3) & (data['qtr'] == 5), data['cons'] - data['abs'], 0)        
    
    data['missing_abs'] = np.where(data['missing_abs'] > 0, data['missing_abs'], 0)
    data['missing_abs'] = np.where(data['cons'] == 0, 0, data['missing_abs'])

    # Cap missing abs at max of cons, as any negative abs above that level is not related to construction absorption
    data['missing_abs'] = np.where((data['missing_abs'] > 0) & (data['missing_abs'] > data['cons']), data['cons'], data['missing_abs'])

    # Then, identify if a year has extra abs that can be used to help absorb the prior years' construction if it was unabsorbed
    data['extra_abs'] = np.where((data['cons'] < data['abs']) & (data['qtr'] == 5), data['abs'] - data['cons'], 0)
    
    # Iterate over the forecast year range, each time determining how much absorption can be attributed to the missing abs from prior periods. Remove that amount from the total missing abs if there is extra abs in the row being evaluated
    for x in range(0, 10):
        if x == 0:
            data['extra_used'] = 0
            data['extra_used_act'] = 0
            data['missing_abs_after_coverage'] = 0
        for y in range(curryr + x - 2, curryr + x + 1):
            if y <= curryr:
                if currqtr == 4 and y == curryr:
                    extra = -4
                elif currqtr != 4 and y == curryr:
                    extra = currqtr - 4
                else:
                    extra = 0
                shift_to_target = y - (curryr + x - 3) + ((y - (curryr + x - 3)) * 4) + extra
            elif y == curryr + 1:
                if currqtr == 4 and curryr + x - 3 < curryr - 1:
                    extra = 4
                elif currqtr != 4 and curryr + x - 3 < curryr - 1:
                    extra = 4 + currqtr
                elif currqtr != 4 and curryr + x - 3 < curryr:
                    extra = 0 + currqtr
                else:
                    extra = 0
                shift_to_target = y - (curryr + x - 3) + extra
            elif y == curryr + 2:
                if currqtr != 4 and curryr + x - 3 == curryr - 1:
                    extra = currqtr
                else:
                    extra = 0
                shift_to_target = y - (curryr + x - 3) + extra
            else:
                shift_to_target = y - (curryr + x - 3)
            
            shift_to_helper = shift_to_target *-1
            
            if currqtr == 4:
                extra = -1
            else:
                extra = currqtr - 1
            
            if curryr + x - 2 < curryr + 3:
                shift_to_update = ((curryr - (curryr + x - 5)) * 4) + extra
            else:
                shift_to_update = 3

            data['extra_used_act_orig'] = data['extra_used_act']
            data['extra_used_act'] = np.where((data['yr'] == y) & (data['qtr'] == 5) & (data['missing_abs'].shift(shift_to_target) > 0) & (data['extra_abs'] > 0) & (data['extra_abs'] <= data['missing_abs'].shift(shift_to_target)), data['extra_used_act'] + data['extra_abs'], data['extra_used_act'])
            data['extra_used_act'] = np.where((data['yr'] == y) & (data['qtr'] == 5) & (data['missing_abs'].shift(shift_to_target) > 0) & (data['extra_abs'] > 0) & (data['extra_abs'] > data['missing_abs'].shift(shift_to_target)), data['extra_used_act'] + data['missing_abs'].shift(shift_to_target), data['extra_used_act'])
            data['extra_abs'] = np.where((data['yr'] == y) & (data['extra_used_act'] != data['extra_used_act_orig']), data['extra_abs'] - (data['extra_used_act'] - data['extra_used_act_orig']), data['extra_abs'])
            data['missing_abs'] = np.where((data['yr'] == curryr + x - 3) & (data['extra_used_act'].shift(shift_to_helper) != data['extra_used_act_orig'].shift(shift_to_helper)), data['missing_abs'] - (data['extra_used_act'].shift(shift_to_helper) - data['extra_used_act_orig'].shift(shift_to_helper)), data['missing_abs']) 

            if y == curryr + x - 2 and y == curryr + x - 2 >= curryr:
                data['missing_abs_after_coverage'] = np.where((data['yr'] == curryr + x - 2) & (data['qtr'] == 5), data['missing_abs'].shift(shift_to_update), data['missing_abs_after_coverage'])
        
            data['extra_used'] = 0
            data = data.drop(['extra_used_act_orig'], axis=1)
    
    data = data.drop(['extra_abs', 'extra_used', 'missing_abs'], axis=1)
    if currqtr != 4:
        data = data.drop(['cons_use'], axis=1)

    return data

def quart_calc(data, variable, variable_name, curryr, currqtr, quartiles, quart_names):
    oob_quarts = data.copy()

    if variable == "vac_chg_inverse":
        variable_imp = "implied_vac_chg_inverse"
    elif variable == "G_mrent":
        variable_imp = "implied_G_mrent"
    elif variable == "gap_chg_inverse":
        variable_imp = "implied_gap_chg_inverse"
    for x, y in zip(quartiles, quart_names):
        if currqtr != 4:
            quarts = pd.DataFrame(oob_quarts[(oob_quarts['yr'] == curryr) & (oob_quarts['qtr'] == 5)].groupby(['yr', 'subsector'])[variable_imp].quantile(x))
            quarts.columns = [y + 'temp']
            data = data.join(quarts, on=['yr', 'subsector'])
        elif currqtr == 4:
            quarts = pd.DataFrame(oob_quarts[(oob_quarts['yr'] == curryr) & (oob_quarts['qtr'] == 5)].groupby(['yr', 'subsector'])[variable].quantile(x))
            quarts.columns = [y + 'temp']
            data = data.join(quarts, on=['yr', 'subsector'])
        quarts = pd.DataFrame(oob_quarts[(oob_quarts['yr'] > curryr) & (oob_quarts['qtr'] == 5)].groupby(['yr', 'subsector'])[variable].quantile(x))
        quarts.columns = [y]
        data = data.join(quarts, on=['yr', 'subsector'])
        data[y] = np.where((data['yr'] == curryr) & (data['qtr'] == 5), data[y + 'temp'], data[y])
        data = data.drop([y + 'temp'], axis=1)
    if currqtr != 4:
        data[variable_name] = np.where((data[variable_imp] < data['25']) & (data['forecast_tag'] == 1), 4, 1)
        data[variable_name] = np.where((data[variable_imp] < data['50']) & (data[variable_imp] >= data['25']) & (data['forecast_tag'] == 1), 3, data[variable_name])
        data[variable_name] = np.where((data[variable_imp] < data['75']) & (data[variable_imp] >= data['50']) & (data['forecast_tag'] == 1), 2, data[variable_name])
        data[variable_name] = np.where((data[variable] < data['25']) & (data['forecast_tag'] == 2), 4, data[variable_name])
        data[variable_name] = np.where((data[variable] < data['50']) & (data[variable] >= data['25']) & (data['forecast_tag'] == 2), 3, data[variable_name])
        data[variable_name] = np.where((data[variable] < data['75']) & (data[variable] >= data['50']) & (data['forecast_tag'] == 2), 2, data[variable_name])
    elif currqtr == 4:
        data[variable_name] = np.where(data[variable] < data['25'], 4, 1)
        data[variable_name] = np.where((data[variable] < data['50']) & (data[variable] >= data['25']), 3, data[variable_name])
        data[variable_name] = np.where((data[variable] < data['75']) & (data[variable] >= data['50']), 2, data[variable_name])
    data[variable_name] = np.where((data['forecast_tag'] == 0), np.nan, data[variable_name])

    data = data.drop(quart_names, axis=1)

    return data

def sub_variance(data_in, variable, variable_name, col_name, curryr, currqtr):
    
    dataframe = data_in.copy()

    dataframe['identity_met_yr'] = dataframe['metcode'] + dataframe['subsector'] + dataframe['yr'].astype(str) + dataframe['qtr'].astype(str)
    if currqtr == 4:
        yr_list = range(curryr, curryr + 10)
    else:
        yr_list = range(curryr + 1, curryr + 10)
    for yr in yr_list:
        variable_name_1 = variable_name + "_" + str(yr)
        f_var_chg = pd.DataFrame(dataframe[(dataframe['yr'] == yr) & (dataframe['qtr'] == 5)].groupby('identity_met_yr')[variable].var(ddof=0))
        f_var_chg.columns = [variable_name_1]
        f_var_chg.sort_values(by=[variable_name_1], ascending = False, inplace = True)
        f_var_chg = f_var_chg.head(3)
        dataframe = dataframe.join(f_var_chg, on='identity_met_yr')
        if yr == yr_list[0]:
            dataframe[col_name] = np.where((np.isnan(dataframe[variable_name_1]) == False), dataframe[variable_name_1], 0)
        else:
            dataframe[col_name] = np.where((np.isnan(dataframe[variable_name_1]) == False), dataframe[variable_name_1], dataframe[col_name])
        dataframe = dataframe.drop([variable_name_1], axis=1)
    dataframe = dataframe.drop(['identity_met_yr'], axis=1)

    return dataframe

def gen_variability_metrics(data_in, curryr, currqtr, sector_val):
    
    data = data_in.copy()

    for var_name in ['vac_chg', 'cons', 'G_mrent', 'gap_chg']:
        col_name = 'f_var_' + var_name
        if var_name != "cons":
            data['var_scaled'] = data[var_name] * 100
            if var_name == "vac_chg":
                data['var_scaled'] = abs(data['var_scaled'])
            if currqtr == 4:
                data[col_name] = data[(data['forecast_tag'] != 0)].groupby('identity')['var_scaled'].transform('var', ddof=0)
            else:
                data[col_name] = data[(data['yr'] >= curryr + 1)].groupby('identity')['var_scaled'].transform('var', ddof=0)
            data = data.drop(['var_scaled'], axis=1)
        elif var_name == "cons":
            data['count_cons'] = data[(data['forecast_tag'] != 0) & (data['cons'] != 0) & (data['h'] == 0)].groupby('identity')['cons'].transform('count')
            data[col_name] = data[(data['h'] == 0) & (data['cons'] != 0) & (data['count_cons'] > 1)].groupby('identity')['cons'].transform('var', ddof=0)
        
        if var_name == "cons":
            data[col_name] = round(data[col_name], 0)

    return data

# If this is the first time the stats will be calculated, determine the overall variance for the forecast series for each sub and get the national average and standard dev
# This will be used to evaluate the submarket cases where there is low variability
def calc_hist_stats(data_in, curryr, currqtr, sector_val, pre_recalc_cols, post_recalc_cols):
    
    data = data_in.copy()

    for var_name in ['vac_chg', 'cons', 'G_mrent', 'gap_chg']:
        col_name = 'f_var_' + var_name
        if var_name != "cons":  
            if currqtr == 4:
                data['f_5_var_' + var_name] = data[(data['yr'] >= curryr) & (data['qtr'] == 5)][col_name].quantile(0.05)
                data['f_95_var_' + var_name] = data[(data['yr'] >= curryr) & (data['qtr'] == 5)][col_name].quantile(0.95)
            elif currqtr != 4:
                data['f_5_var_' + var_name] = data[(data['yr'] > curryr) & (data['qtr'] == 5)][col_name].quantile(0.05)
                data['f_95_var_' + var_name] = data[(data['yr'] > curryr) & (data['qtr'] == 5)][col_name].quantile(0.95)
        if var_name == "cons":
            data['f_5_var_' + var_name] = data[(data['yr'] == curryr + 2) & (data['qtr'] == 5) & (data['cons'] != 0) & (data['count_cons'] > 1)][col_name].quantile(0.05)
            data['f_95_var_' + var_name] = data[(data['yr'] == curryr + 2) & (data['qtr'] == 5) & (data['cons'] != 0) & (data['count_cons'] > 1)][col_name].quantile(0.95)
            data = data.drop(['count_cons'], axis=1)

    # Calculate the number of times a sub has seen new construction in the past 5 years
    data['five_yr_count_cons'] = data[(data['yr'] > curryr - 5) & (data['forecast_tag'] == 0) & (data['qtr'] == 5) & (data['cons'] > 0)].groupby('identity')['cons'].transform('count')
    data = fill_forward(data, 'five_yr_count_cons', 'identity_fill_1')

    # Calculate the 5th and 95th percentile for gap level on the national level by subsector
    gap_quarts = data.copy()
    if currqtr == 4:
        quarts = pd.DataFrame(gap_quarts[(gap_quarts['yr'] == curryr) & (gap_quarts['qtr'] == 5)].groupby('subsector')['gap'].quantile(0.95))
    else:
        quarts = pd.DataFrame(gap_quarts[(gap_quarts['yr'] == curryr) & (gap_quarts['qtr'] == currqtr)].groupby('subsector')['gap'].quantile(0.95))
    quarts.columns = ['gap_5']
    data = data.join(quarts, on=['subsector'])
    if currqtr == 4:
        quarts = pd.DataFrame(gap_quarts[(gap_quarts['yr'] == curryr) & (gap_quarts['qtr'] == 5)].groupby('subsector')['gap'].quantile(0.05))
    else:
        quarts = pd.DataFrame(gap_quarts[(gap_quarts['yr'] == curryr) & (gap_quarts['qtr'] == currqtr)].groupby('subsector')['gap'].quantile(0.05))
    quarts.columns = ['gap_95']
    data = data.join(quarts, on=['subsector'])

    # Calculate the average US vac level by subsector    
    data['us_vac_level_avg'] = data[(data['yr'] == curryr - 1) & (data['qtr'] == 5)].groupby(['subsector'])['vac'].transform('mean')
    data['us_vac_level_avg'] = data['us_vac_level_avg'].fillna(method='ffill')

    # Calculate the historical average vacancy change
    data['absolute_vac_chg'] = abs(data['vac_chg'])
    data['avg_vac_chg'] = data[(data['qtr'] == 5) & (data['yr'] < curryr)].groupby('identity')['absolute_vac_chg'].transform('mean')
    data = fill_forward(data, 'avg_vac_chg', 'identity_fill_1')
    data['std_dev_vac_chg'] = data[(data['qtr'] == 5) & (data['yr'] < curryr)].groupby('identity')['absolute_vac_chg'].transform('std', ddof=0)
    data['std_dev_vac_chg'] = np.where((data['std_dev_vac_chg'] < 0.000005) & (data['std_dev_vac_chg'] > 0), 0, data['std_dev_vac_chg'])
    data = fill_forward(data, 'std_dev_vac_chg', 'identity_fill_1')
    data['avg_vac_chg'] = round(data['avg_vac_chg'], 3)
    data['std_dev_vac_chg'] = round(data['std_dev_vac_chg'], 3)
    data = data.drop(['absolute_vac_chg'], axis=1)

    # Calculate the trend construction for the current year that has already been built and join it to the main dataframe, as well as the implied construction
    if currqtr != 4:
        data['curr_yr_trend_cons'] = data[(data['yr'] == curryr) & (data['qtr'] <= currqtr)].groupby('identity')['cons'].transform('sum')
        data = fill_forward(data, 'curr_yr_trend_cons', 'identity_fill_2')
        data['implied_cons'] = np.where(data['forecast_tag'] == 1, data['cons'] - data['curr_yr_trend_cons'], np.nan)
    
    # Calculate the trend absorption for the current year and join it to the main dataframe, as well as the implied absorption
    if currqtr != 4:
        data['total_trend_abs'] = data[(data['yr'] == curryr) & (data['forecast_tag'] != 1)].groupby('identity')['abs'].transform('sum')
        data = fill_forward(data, 'total_trend_abs', 'identity_fill_2')
        data['implied_abs'] = np.where(data['forecast_tag'] == 1, data['abs'] - data['total_trend_abs'], np.nan)

    # Calculate the historical average market rent change
    data['avg_G_mrent_chg'] = data[(data['qtr'] == 5) & (data['yr'] < curryr)].groupby('identity')['G_mrent'].transform('mean')
    data = fill_forward(data, 'avg_G_mrent_chg', 'identity_fill_1')
    data['avg_G_mrent_chg'] = round(data['avg_G_mrent_chg'], 3)
    data['std_dev_G_mrent_chg'] = data[(data['qtr'] == 5) & (data['yr'] < curryr)].groupby('identity')['G_mrent'].transform('std', ddof=0)
    data['std_dev_G_mrent_chg'] = np.where((data['std_dev_G_mrent_chg'] < 0.000005) & (data['std_dev_G_mrent_chg'] > 0), 0, data['std_dev_G_mrent_chg'])
    data = fill_forward(data, 'std_dev_G_mrent_chg', 'identity_fill_1')
    data['avg_G_mrent_chg'] = round(data['avg_G_mrent_chg'], 3)
    data['std_dev_G_mrent_chg'] = round(data['std_dev_G_mrent_chg'], 3)

    # Determine the submarket construction rent premium, and assign the average premium when there is low sample
    data['gmnc_tag'] = np.where((data['forecast_tag'] == 0) & (data['qtr'] != 5) & (data['cons'] / data['inv'] >= 0.015), 1, 0)
    
    avg_G_mrent_qtr_nc = pd.DataFrame(data[(data['gmnc_tag'] == 1)].groupby('identity')['G_mrent'].mean())
    avg_G_mrent_qtr_nc.columns = ['avg_G_mrent_qtr_nc']
    data = data.join(avg_G_mrent_qtr_nc, on='identity')
    avg_G_mrent_qtr_nonc = pd.DataFrame(data[(data['gmnc_tag'] == 0) & (data['qtr'] != 5) & (data['forecast_tag'] == 0)].groupby('identity')['G_mrent'].mean())
    avg_G_mrent_qtr_nonc.columns = ['avg_G_mrent_qtr_nonc']        
    data = data.join(avg_G_mrent_qtr_nonc, on='identity')    

    temp = data.copy()
    temp = temp[(temp['gmnc_tag'] == 1)]
    temp['cons_perc_inv'] = temp['cons'] / temp['inv']
    temp['avg_cons_perc_inv'] = temp.groupby('identity')['cons_perc_inv'].transform('mean')
    temp = temp.drop_duplicates('identity')
    temp = temp.set_index('identity')
    temp = temp[['avg_cons_perc_inv']]
    data = data.join(temp, on='identity')

    temp = data.copy()
    temp = temp[(temp['gmnc_tag'] == 1)]
    temp['cons_perc_inv'] = temp['cons'] / temp['inv']
    temp['us_avg_cons_perc_inv'] = temp.groupby('identity_us_notier')['cons_perc_inv'].transform('mean')
    temp = temp.drop_duplicates('identity_us_notier')
    temp = temp.set_index('identity_us_notier')
    temp = temp[['us_avg_cons_perc_inv']]
    data = data.join(temp, on='identity_us_notier')

    data['cons_prem_temp'] = data['avg_G_mrent_qtr_nc'] - data['avg_G_mrent_qtr_nonc']
    data['cons_prem_temp'] = round(data['cons_prem_temp'],3)
    
    data['count_obs'] = data.groupby('identity')['gmnc_tag'].transform('sum')
    avg_prem = pd.DataFrame(data[data['count_obs'] >= 5].groupby('identity_us_notier')['cons_prem_temp'].mean())
    avg_prem.columns = ['us_avg_prem']
    avg_prem['us_avg_prem'] = np.where((avg_prem['us_avg_prem'] < 0), 0, avg_prem['us_avg_prem'])
    data = data.join(avg_prem, on='identity_us_notier')
    data['us_avg_prem'] = round(data['us_avg_prem'],3)

    data['cons_prem'] = np.where((data['cons_prem_temp'] >= 0) & (data['count_obs'] >= 5), data['cons_prem_temp'], np.nan)
    data['cons_prem'] = np.where((data['cons_prem_temp'] >= 0) & (data['count_obs'] < 5) & (data['cons_prem_temp'] > data['us_avg_prem']), data['us_avg_prem'], data['cons_prem'])
    data['cons_prem'] = np.where((data['cons_prem_temp'] >= 0) & (data['count_obs'] < 5) & (data['cons_prem_temp'] <= data['us_avg_prem']), data['cons_prem_temp'], data['cons_prem'])
    data['cons_prem'] = np.where((data['cons_prem_temp'] <= 0) & (data['count_obs'] >= 5), 0, data['cons_prem'])
    data['cons_prem'] = np.where((data['cons_prem_temp'] <= 0) & (data['count_obs'] < 5), data['us_avg_prem'], data['cons_prem'])
    data['cons_prem'] = np.where((np.isnan(data['cons_prem_temp']) == True), data['us_avg_prem'], data['cons_prem'])
    data['avg_cons_perc_inv'] = np.where(data['cons_prem_temp'] == data['cons_prem'], data['avg_cons_perc_inv'], np.nan)

    data = data.drop(['gmnc_tag', 'avg_G_mrent_qtr_nc', 'avg_G_mrent_qtr_nonc', 'cons_prem_temp', 'count_obs'], axis = 1)

    # Determine the adjusted market rent change adjusted for construction for trend periods
    
    # First determine what the average and standard deviation rent change is for each submarket
    avg_G_mrent_qtr = pd.DataFrame(data[(data['qtr'] != 5) & (data['forecast_tag'] == 0)].groupby('identity')['G_mrent'].mean())
    avg_G_mrent_qtr.columns = ['avg_G_mrent_qtr']
    data = data.join(avg_G_mrent_qtr, on="identity")
    std_dev_G_mrent_qtr = pd.DataFrame(data[(data['qtr'] != 5) & (data['forecast_tag'] == 0)].groupby('identity')['G_mrent'].std(ddof=0))
    std_dev_G_mrent_qtr.columns = ['std_dev_G_mrent_qtr']
    std_dev_G_mrent_qtr['std_dev_G_mrent_qtr'] = np.where((std_dev_G_mrent_qtr['std_dev_G_mrent_qtr'] < 0.000005) & (std_dev_G_mrent_qtr['std_dev_G_mrent_qtr'] > 0), 0, std_dev_G_mrent_qtr['std_dev_G_mrent_qtr'])
    data = data.join(std_dev_G_mrent_qtr, on="identity")
    
    # For any trend periods that are not year end, if a period has low cons relative to inventory, then assume there was no construction premium and use the unadjusted rent growth as G_mrent_nonc
    # Otherwise, use the average submarket rent growth as G_mrent_nonc, which will remove the rent premium but still keep the period at least at the average rent change
    data['G_mrent_nonc'] = np.where(((data['cons'] / data['inv'] < 0.015) | (data['G_mrent'] < data['avg_G_mrent_qtr'] + (data['std_dev_G_mrent_qtr']*1.5))) & (data['forecast_tag'] == 0) & (data['qtr'] != 5), data['G_mrent'], np.nan)
    data['G_mrent_nonc'] = np.where((data['qtr'] != 5) & (data['forecast_tag'] == 0) & (data['G_mrent'] >= data['avg_G_mrent_qtr'] + (data['std_dev_G_mrent_qtr']*1.5)) & (data['cons'] / data['inv'] >= 0.015), data['avg_G_mrent_qtr'], data['G_mrent_nonc'])

    # Determine if a year period has a full set of trend periods (Qs 1-4 and year end)
    data['full_test'] = data.groupby(['identity', 'yr'])['qtr'].transform('count')

    # For all periods that do not have a full set of trend periods, apply the same criteria to the year end period for determining adjusted G_mrent_nonc that we did above in the quarter period section, but annualize the avg and standard deviation benchmarks
    data['G_mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['full_test'] != 5) & (np.isnan(data['mrent']) == False) & ((data['cons'] / data['inv'] < 0.015) | (data['G_mrent'] < (data['avg_G_mrent_qtr']*4) + ((data['std_dev_G_mrent_qtr']*4)*1.5))), data['G_mrent'], data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['full_test'] != 5) & (np.isnan(data['mrent']) == False) & (data['cons'] / data['inv'] >= 0.015) & (data['G_mrent'] >= (data['avg_G_mrent_qtr']*4) + ((data['std_dev_G_mrent_qtr']*4)*1.5)), data['avg_G_mrent_qtr'] * 4, data['G_mrent_nonc'])
    # Now that we have the new values for quarterly G_mrent_nonc, we need to recalculate the mrent level and G_mrent_nonc in the trend periods that have a quarterly trend breakout for the year end period, since the level and growth will now be different with the new growth figures

    # Begin by setting the mrent in the first trend period for each sub as the original mrent
    # Identify the first row by comparing the identity to the preceding row
    # For the tier 2 markets Providence and Westchester, as well as some other smaller markets, the first row is actually blank for all variables, so we need to handle those cases slightly differently
    data['mrent_nonc'] = np.where((data['identity'] != data['identity'].shift(1)), data['mrent'], np.nan)
    data['mrent_nonc'] = np.where((data['identity'] != data['identity'].shift(2)) & (data['identity'] == data['identity'].shift(1)) & (np.isnan(data['mrent'].shift(1)) == True), data['mrent'], data['mrent_nonc'])

    # If a sub begins with a non year end row, fill in the first year end row by copying down the level in the Q4 period preceding it
    data['mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['full_test'] != 5) & (data['qtr'].shift(1) == 4) & (np.isnan(data['mrent_nonc'] == True)), data['mrent_nonc'].shift(1), data['mrent_nonc'])

    # Handle the special case of NO 9 in Apt, where there is no G_mrent in the 2009 year end row due to the series beginning there
    data['mrent_nonc'] = np.where((sector_val == "apt") & (data['metcode'] == "NO") & (data['subid'] == 9) & (data['yr'] == 2009) & (data['qtr'] == 5), data['mrent_nonc'].shift(1), data['mrent_nonc'])

    # Identify annual only periods
    data['annual_only'] = np.where((data['identity'] == data['identity'].shift(1)) & (data['qtr'] == 5) & (data['qtr'].shift(1) == 5) & (data['forecast_tag'] == 0), 1, 0)

    # Identify the first year end row that will be followed by a trend with quarterly breakouts
    data['first'] = np.where((data['qtr'].shift(-1) == 1) & (data['qtr'].shift(1) == 5), 1, np.nan)

    # Now loop through the rows of the dataframe, generating the new mrent levels for all non annual rows (or annual only rows) based on the G_mrent_nonc variable.
    def calc_subsequent(G_mrent, G_mrent_nonc, mrent_nonc, qtr, annual_only):
        global prev_mrent_nonc

        if np.isnan(G_mrent) == True and np.isnan(mrent_nonc) == True and qtr != 5:
            new_mrent_nonc = np.nan
        elif np.isnan(mrent_nonc) == False:
            new_mrent_nonc = mrent_nonc
            prev_mrent_nonc = mrent_nonc
        elif qtr != 5 or annual_only == 1:
            new_mrent_nonc = (1 + G_mrent_nonc) * prev_mrent_nonc
            prev_mrent_nonc = new_mrent_nonc
        else:
            new_mrent_nonc = np.nan
            
        return new_mrent_nonc

    data['mrent_nonc'] = data.apply(lambda row: calc_subsequent(row['G_mrent'], row['G_mrent_nonc'], row['mrent_nonc'], row['qtr'], row['annual_only']), axis=1)

    # Fill in the year end row for mrent for periods that have a trend breakout by copying down what is in the Q4 row that precedes it
    data['mrent_nonc'] = np.where((data['qtr'] == 5) & (data['annual_only'] == 0) & (data['forecast_tag'] == 0) & (data['first'] != 1), data['mrent_nonc'].shift(1), data['mrent_nonc'])
    data['mrent_nonc'] = round(data['mrent_nonc'], 2)

    # Now that we have all the mrent levels, calculate the new G_mrent_nonc variable for the year end rows where there is a quarterly trend breakout
    data['G_mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['qtr'].shift(5) == 5), (data['mrent_nonc'] - data['mrent_nonc'].shift(5)) / data['mrent_nonc'].shift(5), data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['qtr'].shift(5) != 5), np.nan, data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['qtr'].shift(1) == 5) & (np.isnan(data['mrent']) == False) & ((data['cons'] / data['inv'] < 0.01) | (data['G_mrent'] < (data['avg_G_mrent_qtr']*4) + ((data['std_dev_G_mrent_qtr']*4)*1.5))), data['G_mrent'], data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['qtr'] == 5) & (data['forecast_tag'] == 0) & (data['qtr'].shift(1) == 5) & (np.isnan(data['mrent']) == False) & (data['cons'] / data['inv'] >= 0.01) & (data['G_mrent'] >= (data['avg_G_mrent_qtr']*4) + ((data['std_dev_G_mrent_qtr']*4)*1.5)), data['avg_G_mrent_qtr'] * 4, data['G_mrent_nonc'])        

    # Cap this at a min of zero growth or G_mrent if it is below zero
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] == 0) & (data['G_mrent_nonc'] < 0) & (data['G_mrent'] >=0), 0, data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] == 0) & (data['G_mrent_nonc'] < 0) & (data['G_mrent'] < 0), data['G_mrent'], data['G_mrent_nonc'])

    data['G_mrent_nonc'] = round(data['G_mrent_nonc'], 3)
    data = data.drop(['avg_G_mrent_qtr', 'std_dev_G_mrent_qtr', 'full_test', 'first', 'annual_only'], axis=1)

    # Calculate the average NC adjusted market rent change for each submarket
    data['avg_G_mrent_chg_nonc'] = data[(data['qtr'] == 5) & (data['yr'] < curryr)].groupby('identity')['G_mrent_nonc'].transform('mean')
    data = fill_forward(data, 'avg_G_mrent_chg_nonc', 'identity_fill_1')
    data['avg_G_mrent_chg_nonc'] = round(data['avg_G_mrent_chg_nonc'], 3)

    # For forecast years, fill in the G_mrent_nonc variable by subtracting a portion of the avg nc premium for the sub's trend based on the cons percentage of inventory, otherwise just fill in the G_mrent
    # Cap this at a min of zero growth or G_mrent if it is below zero.
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.015) & (data['cons'] / data['inv'] < 0.025), data['G_mrent'] - (data['cons_prem'] * 0.25), data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.025) & (data['cons'] / data['inv'] < 0.05), data['G_mrent'] - (data['cons_prem'] * 0.75), data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.05), data['G_mrent'] - data['cons_prem'], data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] < 0.015), data['G_mrent'], data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.015) & (data['G_mrent_nonc'] < 0) & (data['G_mrent'] >=0), 0, data['G_mrent_nonc'])
    data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.015) & (data['G_mrent_nonc'] < 0) & (data['G_mrent'] < 0), data['G_mrent'], data['G_mrent_nonc'])
    
    # Call the function to calculate how much construction stock has not yet been absorbed
    data = calc_missing_cons_abs(data, curryr, currqtr)
    
    # Calculate an adjusted abs that discounts for nc absorption
    data['abs_nonc'] = np.where((data['yr'] <= curryr) & (data['qtr'] != 5) & (data['identity'] == data['identity'].shift(5)) & (data['qtr'] == data['qtr'].shift(5)), data['abs'] - (data['cons'] * 0.60) - (data['cons'].shift(5) * 0.40), np.nan)
    data['abs_nonc'] = np.where((data['yr'] <= curryr) & (data['qtr'] != 5) & (((data['identity'] != data['identity'].shift(5)) | (data['qtr'] != data['qtr'].shift(5)))), data['abs'] - (data['cons'] * 0.60), data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] < curryr) & (data['qtr'] == 5) & (data['identity'] == data['identity'].shift(5)) & (data['qtr'] == data['qtr'].shift(5)), data['abs'] - (data['cons'] * 0.60) - (data['cons'].shift(5) * 0.40), data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] < curryr) & (data['qtr'] == 5) & (data['identity'] == data['identity'].shift(5)) & (data['qtr'] == data['qtr'].shift(5)) & (np.isnan(data['abs'].shift(5)) == True), data['abs'] - (data['cons'] * 0.60), data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] < curryr) & (data['qtr'] == 5) & (data['identity'] == data['identity'].shift(1)) & (data['qtr'] == data['qtr'].shift(1)), data['abs'] - (data['cons'] * 0.60) - (data['cons'].shift(1) * 0.40), data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] < curryr) & (data['qtr'] == 5) & (data['identity'] == data['identity'].shift(1)) & (data['qtr'] == data['qtr'].shift(1)) & (np.isnan(data['abs'].shift(1)) == True), data['abs'] - (data['cons'] * 0.60), data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] == curryr - 1) & (data['abs'] < 0), data['abs'], data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] == curryr - 1) & (data['abs'] < data['cons']) & (data['abs'] >= 0), 0, data['abs_nonc'])
    data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 4) & (data['qtr'] == 5), data['abs'] - (data['cons'] * 0.60) - (data['extra_used_act']), data['abs_nonc'])
    # abs nonc variable for non q4 periods in curryr will be calculated after we calculate the implied absorption later on in the code
    data['abs_nonc'] = np.where((data['yr'] > curryr), data['abs'] - (data['cons'] * 0.60) - data['extra_used_act'], data['abs_nonc'])
    if sector_val != "apt":
        data['abs_nonc'] = round(data['abs_nonc'], -3)
    elif sector_val == "apt":
        data['abs_nonc'] = round(data['abs_nonc'], 0)
        
    # Calculate the z-score for market rent change for each submarket's forecast  
    data['G_mrent_z'] = (data['G_mrent'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg']
    data['G_mrent_z'] = round(data['G_mrent_z'], 2)

    # Calculate the annual three year trend average for key metrics
    if currqtr != 4:
        data['cons_use'] = np.where(data['forecast_tag'] == 1, data['h'], data['cons'])
        data['three_yr_avg_cons'] = data[(data['yr'] > curryr - 3) & (data['yr'] <= curryr) & (data['qtr'] == 5)].groupby('identity')['cons_use'].transform('mean')
        data['five_yr_avg_cons'] = data[(data['yr'] > curryr - 5) & (data['yr'] <= curryr) & (data['qtr'] == 5)].groupby('identity')['cons_use'].transform('mean')
        data = fill_forward(data, 'three_yr_avg_cons', 'identity_fill_1')
        data = fill_forward(data, 'five_yr_avg_cons', 'identity_fill_1')
        data = data.drop(['cons_use'], axis=1)
    elif currqtr == 4:
        data['three_yr_avg_cons'] = data[(data['yr'] > curryr - 4) & (data['yr'] < curryr) & (data['qtr'] == 5)].groupby('identity')['cons'].transform('mean')
        data['five_yr_avg_cons'] = data[(data['yr'] > curryr - 6) & (data['yr'] < curryr) & (data['qtr'] == 5)].groupby('identity')['cons'].transform('mean')
        data = fill_forward(data, 'three_yr_avg_cons', 'identity_fill_1')
        data = fill_forward(data, 'five_yr_avg_cons', 'identity_fill_1')

    col_list = ['abs', 'abs_nonc', 'G_mrent', 'G_mrent_nonc', 'emp_chg']
    for var in col_list:
        data['three_yr_avg_' + var] = data[(data['yr'] > curryr - 4) & (data['yr'] < curryr) & (data['qtr'] == 5)].groupby('identity')[var].transform('mean')
        data = fill_forward(data, 'three_yr_avg_' + var, 'identity_fill_1')
    
    data['five_yr_avg_G_mrent'] = data[(data['yr'] > curryr - 6) & (data['yr'] < curryr) & (data['qtr'] == 5)].groupby('identity')['G_mrent'].transform('mean')
    data = fill_forward(data, 'five_yr_avg_G_mrent', 'identity_fill_1')

    if sector_val != "apt":
        data['three_yr_avg_cons'] = round(data['three_yr_avg_cons'], -3)
        data['three_yr_avg_abs'] = round(data['three_yr_avg_abs'], -3)
        data['three_yr_avg_abs_nonc'] = round(data['three_yr_avg_abs_nonc'], -3)
    elif sector_val == "apt":
        data['three_yr_avg_cons'] = round(data['three_yr_avg_cons'], 0)
        data['three_yr_avg_abs'] = round(data['three_yr_avg_abs'], 0)
        data['three_yr_avg_abs_nonc'] = round(data['three_yr_avg_abs_nonc'], 0)
    data['three_yr_avg_G_mrent'] = round(data['three_yr_avg_G_mrent'], 3)
    data['three_yr_avg_G_mrent_nonc'] = round(data['three_yr_avg_G_mrent_nonc'], 3)
    data['three_yr_avg_emp_chg'] = round(data['three_yr_avg_emp_chg'], 3)
    
    # Calculate the abs/cons ratio
    if currqtr != 4:
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] >= data['curr_yr_trend_cons']), data['implied_cons'], np.nan)
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] < data['curr_yr_trend_cons']) & (data['total_trend_abs'] >= 0), data['implied_cons'] + (data['curr_yr_trend_cons'] - data['total_trend_abs']), data['cons_use'])
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] < data['curr_yr_trend_cons']) & (data['total_trend_abs'] < 0), data['cons'], data['cons_use'])
        data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] == 0), data['cons'], data['cons_use'])
        data['abs_cons_r'] = np.where((data['forecast_tag'] != 1), data['abs'] / data['cons'], np.nan)
        data['abs_cons_r'] = np.where((data['forecast_tag'] == 1), data['implied_abs'] / data['cons_use'], data['abs_cons_r'])
        data = data.drop(['cons_use'], axis=1)
    else:
        data['abs_cons_r'] = data['abs'] / data['cons']
    data['abs_cons_r'] = round(data['abs_cons_r'], 2)
    data = data.replace([np.inf, -np.inf], np.nan)
    

    # Calculate the 5 year historical avg abs/cons ratio for each submarket, where cons was at least 1% of total inventory
    avg_abs_cons = data.copy()
    avg_abs_cons = pd.DataFrame(avg_abs_cons[(avg_abs_cons['forecast_tag'] == 0) & (avg_abs_cons['qtr'] == 5) & (avg_abs_cons['cons'] / avg_abs_cons['inv'] >= 0.01) & (curryr - avg_abs_cons['yr'] <= 5)].groupby('identity')['abs_cons_r'].mean())
    avg_abs_cons.columns = ['avg_abs_cons']
    data = data.join(avg_abs_cons, on='identity')
    data['avg_abs_cons'] = round(data['avg_abs_cons'], 2)

    # Calculate the min and max levels for each submarket's trend history for the last 10 years for vac, market rent growth, and effective rent growth
    data = min_max(data, 'vac', curryr)
    data = min_max(data, 'G_mrent', curryr)
    data = min_max(data, 'gap', curryr)
    data = min_max(data, 'gap_chg', curryr)

    # Calculate the z-score for vacancy change for each submarket's trend years  
    data['vac_z'] = np.where((data['forecast_tag'] == 0) & (data['qtr'] == 5), (abs(data['vac_chg']) - data['avg_vac_chg']) / data['std_dev_vac_chg'], np.nan)
    data['vac_z'] = round(data['vac_z'], 2)
    # Handle cases of 2020Q2 subs, who only have one year of history and therefore have no std dev to devide by
    data['vac_z'] = np.where((data['lim_hist'] <= 5) & (data['std_dev_vac_chg'] == 0), 1, data['vac_z'])


    # Calculate the z-score for rent change for each submarket's trend years 
    data['G_mrent_z'] = np.where((data['forecast_tag'] == 0) & (data['qtr'] == 5), (data['G_mrent'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg'], np.nan)
    data['G_mrent_z'] = round(data['G_mrent_z'], 2)
    # Handle cases of 2020Q2 subs, who only have one year of history and therefore have no std dev to devide by
    data['G_mrent_z'] = np.where((data['lim_hist'] <= 5) & (data['std_dev_G_mrent_chg'] == 0), 1, data['G_mrent_z'])

    # Calculate the typical absorption observed for future quarters in the past five trend years
    if currqtr != 4:
        data['hist_trend_abs_sum'] = data[(data['yr'] >= curryr - 5) & (data['forecast_tag'] == 0) & (data['yr'] < curryr) & (data['qtr'] <= currqtr)].groupby(['identity', 'yr'])['abs_nonc'].transform('sum')
        data['hist_trend_abs_avg'] = data[(data['qtr'] == currqtr)].groupby(['identity'])['abs_nonc'].transform('mean')
        data['hist_implied_abs'] = np.where((data['forecast_tag'] == 1), data['hist_trend_abs_avg'].shift(1), np.nan)
        data = data.drop(['hist_trend_abs_sum', 'hist_trend_abs_avg'], axis=1)
        if sector_val != "apt":
            data['hist_implied_abs'] = round(data['hist_implied_abs'], -3)
        elif sector_val == "apt":
            data['hist_implied_abs'] = round(data['hist_implied_abs'], 0)
        
    # Calculate the typical G_mrent observed for future quarters in the past five trend years, taking into account cases where there is significant construction
    if currqtr != 4:
        data['hist_trend_G_mrent'] = np.where((data['qtr'] == 5), (data['mrent_nonc'] - data['mrent_nonc'].shift(periods=5-currqtr)) / data['mrent_nonc'].shift(periods=5-currqtr), np.nan)
        data['hist_trend_G_mrent_avg'] =  data[(data['yr'] >= curryr - 5) & (data['forecast_tag'] == 0) & (data['yr'] < curryr) & (data['qtr'] == 5)].groupby('identity')['hist_trend_G_mrent'].transform('mean')
        data['hist_implied_G_mrent'] = np.where((data['forecast_tag'] == 1), data['hist_trend_G_mrent_avg'].shift(currqtr + 1), np.nan)
        data = data.drop(['hist_trend_G_mrent', 'hist_trend_G_mrent_avg', 'mrent_nonc'], axis=1)
        data['hist_implied_G_mrent'] = round(data['hist_implied_G_mrent'], 3)

    # Calculate the average yearly construction on a national level by subsector when there is construction built
    data['cons_per_inv'] = data['cons'] / data['inv']
    avg_us_cons_inv = pd.DataFrame(data[(data['forecast_tag'] == 0) & (data['qtr'] == 5) & (data['cons'] != 0)].groupby('subsector')['cons_per_inv'].mean())
    avg_us_cons_inv.columns = ['avg_us_cons_inv']
    data = data.join(avg_us_cons_inv, on='subsector')
    data['avg_us_cons_inv'] = round(data['avg_us_cons_inv'], 3)
    data = data.drop(['cons_per_inv'], axis=1)

    # Calculate the 10 year average historical vacancy for the submarket, as well as the 35th percentile to represent a better than average level (since vac is a good when low, use the 35th percentile)
    data['10_yr_vac'] = data[(data['forecast_tag'] == 0) & (data['yr'] >= curryr - 10) & (data['qtr'] == 5)].groupby('identity')['vac'].transform('mean')
    data['10_yr_vac'] = round(data['10_yr_vac'], 4)
    data = fill_forward(data, '10_yr_vac', 'identity_fill_1')
    temp =  pd.DataFrame(data[(data['forecast_tag'] == 0) & (data['qtr'] == 5) & (data['yr'] >= curryr - 10)].groupby('identity')['vac'].quantile(0.35))
    temp.columns = ['10_yr_35p_vac']
    data = data.join(temp, on='identity')

    # Calculate the variance in absorption, market rent, and gap change accross the submarkets of each metro
    data['vac_chg_sub_var'] = np.nan
    data['G_mrent_sub_var'] = np.nan
    data = sub_variance(data, 'vac_chg', 'vac_chg_svar', 'vac_chg_sub_var', curryr, currqtr)
    data = sub_variance(data, 'G_mrent_nonc', 'G_mrent_nonc_svar', 'G_mrent_sub_var', curryr, currqtr)

    # Calculate rol occupied stock
    data['rolocc'] = (1 - data['rolsvac']) * data['rolsinv']
    if sector_val != "apt":
        data['rolocc'] = round(data['rolocc'], -3)
    elif sector_val == "apt":
        data['rolocc'] = round(data['rolocc'], 0)

    all_cols = list(data.columns)
    
    new_cols = [x for x in all_cols if x not in pre_recalc_cols and x not in post_recalc_cols and x != 'Recalc Insert']
    orig_cols = [x for x in pre_recalc_cols if x != 'Recalc Insert']
    
    data = data[orig_cols + new_cols + ['Recalc Insert'] + post_recalc_cols]

    return data

# This function will calculate the key metrics needed to assess viability of oob forecast
def calc_stats(data_in, curryr, currqtr, first, sector_val):
    print("start calc stats")

    data = data_in.copy()

    if first == False:
        data = drop_cols(data)

    # Use these identities to "drag down" the values into subsequent periods when necessary
    data['identity_fill_1'] = data['identity'] + str(curryr - 1) + "5"
    data['identity_fill_2'] = data['identity'] + str(curryr) + str(currqtr)
    data['identity_fill_3'] = data['identity'] + str(curryr - 1) + str(currqtr + 1)

    # Create a column called Recalc Insert, so that we can drop everything created after it from the dataframe and the stats can be recalculated after a fix is entered
    data['Recalc Insert'] = np.nan
    if first == True:
        pre_recalc_cols = list(data.columns)    
    else:
        cols = list(data.columns)
        recalc_index = list(data.columns).index('Recalc Insert')
        pre_recalc_cols = cols[:recalc_index + 1]
    
    
    # Calculate vacancy change and rol vac chg
    data = calc_chg(data, 'vac', 'vac_chg', curryr, currqtr, sector_val)
    data = calc_chg(data, 'rolsvac', 'rolsvac_chg', curryr, currqtr, sector_val)
    data['vac_chg'] = round(data['vac_chg'], 4)
    data['rolsvac_chg'] = round(data['rolsvac_chg'], 4)

    # Calculate gap change and rol gap chg
    data = calc_chg(data, 'gap', 'gap_chg', curryr, currqtr, sector_val)
    data = calc_chg(data, 'rolsgap', 'rolsgap_chg', curryr, currqtr, sector_val)
    data['gap_chg'] = round(data['gap_chg'], 4)
    data['rolsgap_chg'] = round(data['rolsgap_chg'], 4)
    
    # Calculate forecast variability metrics for the key metrics
    data = gen_variability_metrics(data, curryr, currqtr, sector_val)

    # Calculate a number of key metrics that only need to be calculated on the first ingestion (as they will not change with updates made by shim)
    if first == True:
        post_recalc_cols = [x for x in data.columns if x not in pre_recalc_cols and x != 'count_cons' and x != 'Recalc Insert']
        data = calc_hist_stats(data, curryr, currqtr, sector_val, pre_recalc_cols, post_recalc_cols)
    
    if first == False:
        # Calculate the abs/cons ratio for forecast years if this is not the first calc stats
        if currqtr != 4:
            data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] >= data['curr_yr_trend_cons']), data['implied_cons'], np.nan)
            data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] < data['curr_yr_trend_cons']) & (data['total_trend_abs'] >= 0), data['implied_cons'] + (data['curr_yr_trend_cons'] - data['total_trend_abs']), data['cons_use'])
            data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] > 0) & (data['abs'] < data['curr_yr_trend_cons']) & (data['total_trend_abs'] < 0), data['cons'], data['cons_use'])
            data['cons_use'] = np.where((data['forecast_tag'] == 1) & (data['curr_yr_trend_cons'] == 0), data['cons'], data['cons_use'])
            data['abs_cons_r'] = np.where((data['forecast_tag'] != 1), data['abs'] / data['cons'], np.nan)
            data['abs_cons_r'] = np.where((data['forecast_tag'] == 1), data['implied_abs'] / data['cons_use'], data['abs_cons_r'])
            data = data.drop(['cons_use'], axis=1)
        else:
            data['abs_cons_r'] = data['abs'] / data['cons']
        data['abs_cons_r'] = round(data['abs_cons_r'], 2)
        data = data.replace([np.inf, -np.inf], np.nan)

        # Call the function to calculate construction stock that has not been absorbed, since the forecast year data may have changed and it needs to be recalculated
        data = calc_missing_cons_abs(data, curryr, currqtr)
    
    # Calculate the implied construction for the current forecast year
    if currqtr != 4:
        data['implied_cons'] = np.where(data['forecast_tag'] == 1, data['cons'] - data['curr_yr_trend_cons'], np.nan)

    # Calculate the implied vac chg for the current forecast year
    if currqtr != 4:
        data['implied_vac_chg'] = np.where(data['forecast_tag'] == 1, data['vac'] - data['vac'].shift(1), np.nan)
        data['implied_vac_chg'] = round(data['implied_vac_chg'], 3)

    # Calculate the z-score for vacancy change for each submarket's forecast periods
    if currqtr != 4:
        data['vac_z'] = np.where((data['forecast_tag'] == 1), (abs(data['implied_vac_chg']) - (data['avg_vac_chg'] * ((4 - currqtr) / 4))) / data['std_dev_vac_chg'], data['vac_z'])
        data['vac_z'] = np.where((data['forecast_tag'] == 2), (abs(data['vac_chg']) - data['avg_vac_chg']) / data['std_dev_vac_chg'], data['vac_z'])
    elif currqtr == 4:
        data['vac_z'] = np.where(data['forecast_tag'] != 0, (abs(data['vac_chg']) - data['avg_vac_chg']) / data['std_dev_vac_chg'], data['vac_z'])
    data['vac_z'] = round(data['vac_z'], 2)
    # Handle cases of 2020Q2 subs, who only have one year of history and therefore have no std dev to devide by
    data['vac_z'] = np.where((data['lim_hist'] <= 5) & (data['std_dev_vac_chg'] == 0), 1, data['vac_z'])
    
    
    # Calculate the implied absorption for the current forecast year, and finish the calculation for nc adjusted abs now that we have that variable
    if currqtr != 4:
        data['implied_abs'] = np.where(data['forecast_tag'] == 1, data['abs'] - data['total_trend_abs'], np.nan)
        data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 1) & (data['qtr'] == 5), data['implied_abs'] - (data['implied_cons'] * 0.60) - data['extra_used_act'] + data['abs_nonc'].shift(1), data['abs_nonc'])
        data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 2) & (data['qtr'] == 5), data['implied_abs'] - (data['implied_cons'] * 0.60) - data['extra_used_act'] + data['abs_nonc'].shift(1) + data['abs_nonc'].shift(2), data['abs_nonc'])
        data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 3) & (data['qtr'] == 5), data['implied_abs'] - (data['implied_cons'] * 0.60) - data['extra_used_act'] + data['abs_nonc'].shift(1) + data['abs_nonc'].shift(2) + data['abs_nonc'].shift(3), data['abs_nonc'])
        if sector_val != "apt":
            data['abs_nonc'] = round(data['abs_nonc'], -3)
        elif sector_val == "apt":
            data['abs_nonc'] = round(data['abs_nonc'], 0)
    
    # Recalculate nc adjusted abs for forecast years if this is not the first run of calc stats, since the data may have been updated with a shim adjustment        
    if first == False:
        data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 4) & (data['qtr'] == 5), data['abs'] - (data['cons'] * 0.60) - (data['extra_used_act']), data['abs_nonc'])
        data['abs_nonc'] = np.where((data['yr'] > curryr), data['abs'] - (data['cons'] * 0.60) - data['extra_used_act'], data['abs_nonc'])
        if currqtr != 4:
            data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 1) & (data['qtr'] == 5), data['implied_abs'] - (data['implied_cons'] * 0.60) - data['extra_used_act'] + data['abs_nonc'].shift(1), data['abs_nonc'])
            data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 2) & (data['qtr'] == 5), data['implied_abs'] - (data['implied_cons'] * 0.60) - data['extra_used_act'] + data['abs_nonc'].shift(1) + data['abs_nonc'].shift(2), data['abs_nonc'])
            data['abs_nonc'] = np.where((data['yr'] == curryr) & (currqtr == 3) & (data['qtr'] == 5), data['implied_abs'] - (data['implied_cons'] * 0.60) - data['extra_used_act'] + data['abs_nonc'].shift(1) + data['abs_nonc'].shift(2) + data['abs_nonc'].shift(3), data['abs_nonc'])
        if sector_val != "apt":
            data['abs_nonc'] = round(data['abs_nonc'], -3)
        elif sector_val == "apt":
            data['abs_nonc'] = round(data['abs_nonc'], 0)

        # Recalculate the nc adjusted market rent growth For forecast years if this is not the first run of calc stats, since the data may hav been updated with a shim adjustment
        data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.015) & (data['cons'] / data['inv'] < 0.025), data['G_mrent'] - (data['cons_prem'] * 0.25), data['G_mrent_nonc'])
        data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.025) & (data['cons'] / data['inv'] < 0.05), data['G_mrent'] - (data['cons_prem'] * 0.75), data['G_mrent_nonc'])
        data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.05), data['G_mrent'] - data['cons_prem'], data['G_mrent_nonc'])
        data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] < 0.015), data['G_mrent'], data['G_mrent_nonc'])
        data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.015) & (data['G_mrent_nonc'] < 0) & (data['G_mrent'] >=0), 0, data['G_mrent_nonc'])
        data['G_mrent_nonc'] = np.where((data['forecast_tag'] != 0) & (data['cons'] / data['inv'] >= 0.015) & (data['G_mrent_nonc'] < 0) & (data['G_mrent'] < 0), data['G_mrent'], data['G_mrent_nonc'])
            

    # Calculate the implied gap chg for the current forecast year
    if currqtr != 4:
        data['implied_gap_chg'] = np.where(data['forecast_tag'] == 1, data['gap'] - data['gap'].shift(1), np.nan)
        data['implied_gap_chg'] = round(data['implied_gap_chg'], 3)

    # Calculate the implied gap chg if we had stuck with ROL gap
    if currqtr != 4:
        data['implied_using_rolsgap_chg'] = np.where(data['forecast_tag'] == 1, data['rolsgap'] - data['gap'].shift(1), np.nan)
    
    # Calculate the implied absorption if we had stuck with ROL abs
    if currqtr != 4:
        data['implied_rolsabs'] = np.where(data['forecast_tag'] == 1, data['rolsabs'] - data['total_trend_abs'] , np.nan)
    
    # Calculate the implied g_mrent for the current forecast year
    if currqtr != 4:
        data['implied_G_mrent'] = np.where(data['forecast_tag'] == 1, (data['mrent'] - data['mrent'].shift(1)) / data['mrent'].shift(1), np.nan)
        data['implied_G_mrent'] = round(data['implied_G_mrent'], 3)
        data['total_trend_G_mrent'] = np.where((data['forecast_tag'].shift(-1) == 1), (data['mrent'] - data['mrent'].shift(periods=currqtr)) / data['mrent'].shift(periods=currqtr), np.nan)
        data['total_trend_G_mrent'] = np.where(data['forecast_tag'] == 1, data['total_trend_G_mrent'].shift(1), np.nan)
    
    # Calculate the implied g_mrent if we had stuck with rol g_mrent
    if currqtr != 4:
        data['implied_using_grolsmre'] = np.where(data['forecast_tag'] == 1, (data['rolmrent'] - data['mrent'].shift(1)) / data['mrent'].shift(1), np.nan)
        data['implied_using_grolsmre'] = round(data['implied_using_grolsmre'], 3)

    # Calculate the z-score for market rent change for each submarket's forecast periods
    if currqtr != 4:
        data['G_mrent_z'] = np.where(data['forecast_tag'] == 1, (data['implied_G_mrent'] - (data['avg_G_mrent_chg'] * ((4 - currqtr) / 4))) / data['std_dev_G_mrent_chg'], data['G_mrent_z'])
        data['G_mrent_z'] = np.where(data['forecast_tag'] == 2, (data['G_mrent'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg'], data['G_mrent_z'])
    elif currqtr == 4:
        data['G_mrent_z'] = np.where(data['forecast_tag'] != 0, (data['G_mrent'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg'], data['G_mrent_z'])
    data['G_mrent_z'] = round(data['G_mrent_z'], 2)
    # Handle cases of 2020Q2 subs, who only have one year of history and therefore have no std dev to devide by
    data['G_mrent_z'] = np.where((data['lim_hist'] <= 5) & (data['std_dev_G_mrent_chg'] == 0), 1, data['G_mrent_z'])

    # Calculate the implied g_merent for the current forecast year
    if currqtr != 4:
        data['implied_G_merent'] = np.where(data['forecast_tag'] == 1, (data['merent'] - data['merent'].shift(1)) / data['merent'].shift(1), np.nan)
        data['implied_G_merent'] = round(data['implied_G_merent'], 3)
    
    # Count the number of consecutive negative absorptions in each submarket's forecast series
    data['cons_neg_abs'] = np.where((data['yr'] > curryr + 1) & (data['abs'] < 0) & (data['abs'].shift(1) < 0) & (data['abs'].shift(2) < 0), 1, 0)
    if currqtr == 4:
        data['cons_neg_abs'] = np.where((data['yr'] == curryr + 1) & (data['abs'] < 0) & (data['abs'].shift(1) < 0) & (data['abs'].shift(2) < 0), 1, data['cons_neg_abs'])
        data['cons_neg_abs'] = np.where((data['yr'] == curryr) & (data['abs'] < 0) & (data['abs'].shift(periods=1) < 0) & (data['abs'].shift(periods=6) < 0), 1, data['cons_neg_abs'])
    else:
        data['cons_neg_abs'] = np.where((data['yr'] == curryr + 1) & (data['abs'] < 0) & (data['abs'].shift(1) < 0) & (data['abs'].shift(periods=(2+currqtr)) < 0), 1, data['cons_neg_abs']) 
        data['cons_neg_abs'] = np.where((data['yr'] == curryr) & (data['abs'] < 0) & (data['abs'].shift(periods=(1+currqtr)) < 0) & (data['abs'].shift(periods=(6+currqtr)) < 0), 1, data['cons_neg_abs'])
    data['cons_neg_abs'] = data['cons_neg_abs'].fillna(0)
    data['cons_neg_abs'] = data['cons_neg_abs'].astype(int)
    
    # Count the number of consecutive rent growths that are below historical average in each submarket's forecast series
    data['cons_low_G_mrent'] = np.where((data['yr'] > curryr + 1) & (data['G_mrent_nonc'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(1) < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(2) < data['avg_G_mrent_chg_nonc']), 1, 0)
    if currqtr == 4:
        data['cons_low_G_mrent'] = np.where((data['yr'] == curryr + 1) & (data['G_mrent_nonc'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(1) < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(2) < data['avg_G_mrent_chg_nonc']), 1, data['cons_low_G_mrent'])
        data['cons_low_G_mrent'] = np.where((data['yr'] == curryr) & (data['G_mrent_nonc'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(periods=1) < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(periods=6) < data['avg_G_mrent_chg_nonc']), 1, data['cons_low_G_mrent'])
    else:
        data['cons_low_G_mrent'] = np.where((data['yr'] == curryr + 1) & (data['G_mrent_nonc'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(1) < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(periods=(2+currqtr)) < data['avg_G_mrent_chg_nonc']), 1, data['cons_low_G_mrent']) 
        data['cons_low_G_mrent'] = np.where((data['yr'] == curryr) & (data['G_mrent_nonc'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(periods=(1+currqtr)) < data['avg_G_mrent_chg_nonc']) & (data['G_mrent_nonc'].shift(periods=(6+currqtr)) < data['avg_G_mrent_chg_nonc']), 1, data['cons_low_G_mrent'])
    data['cons_low_G_mrent'] = data['cons_low_G_mrent'].fillna(0)
    data['cons_low_G_mrent'] = data['cons_low_G_mrent'].astype(int)

    # Calculate the quartile for vacancy change, market rent change, and gap change for each forecast year row, using the implied change if in curryr row and not Q4
    data['vac_chg_inverse'] = data['vac_chg'] * -1
    data['gap_chg_inverse'] = data['gap_chg'] * -1
    if currqtr != 4:
        data['implied_vac_chg_inverse'] = data['implied_vac_chg'] * -1
        data['implied_gap_chg_inverse'] = data['implied_gap_chg'] * -1
    data = quart_calc(data, 'vac_chg_inverse', 'vac_quart', curryr, currqtr, [0.25, 0.50, 0.75], ['25', '50', '75'])
    data = quart_calc(data, 'G_mrent', 'G_mrent_quart', curryr, currqtr, [0.25, 0.50, 0.75], ['25', '50', '75'])
    data = quart_calc(data, 'gap_chg_inverse', 'gap_quart', curryr, currqtr, [0.25, 0.50, 0.75], ['25', '50', '75'])
    
    if currqtr != 4:
        data = data.drop(['vac_chg_inverse', 'gap_chg_inverse', 'implied_vac_chg_inverse', 'implied_gap_chg_inverse'], axis=1)
    elif currqtr == 4:
        data = data.drop(['vac_chg_inverse', 'gap_chg_inverse'], axis=1)

    # Identify the previous year cons, emp_chg, and g_mrent for each forecast year
    if currqtr == 4:
        period = 1
    else:
        period = currqtr + 1
    if sector_val == "apt" or sector_val == "ret":
        emp_chg_use = 'emp_chg'
    elif sector_val == "off":
        emp_chg_use = 'off_emp_chg'
    elif sector_val == "ind":
        emp_chg_use = 'ind_emp_chg'
    data['prev_G_mrent'] = np.where((data['yr'] == curryr), data['G_mrent'].shift(periods=period), data['G_mrent'].shift(1))
    data['prev_cons'] = np.where((data['yr'] == curryr), data['cons'].shift(periods=period), data['cons'].shift(1))
    data['prev_emp_chg'] = np.where((data['yr'] == curryr), data[emp_chg_use].shift(periods=period), data[emp_chg_use].shift(1))
    data['prev_G_mrent'] = np.where(data['forecast_tag'] == 0, np.nan, data['prev_G_mrent'])
    data['prev_cons'] = np.where(data['forecast_tag'] == 0, np.nan, data['prev_cons'])
    data['prev_emp_chg'] = np.where(data['forecast_tag'] == 0, np.nan, data['prev_emp_chg']) 

    data = data.drop(['identity_fill_1', 'identity_fill_2', 'identity_fill_3'], axis=1)

    print("end calc stats")

    return data

    