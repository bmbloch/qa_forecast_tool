import pandas as pd
import numpy as np
from IPython.core.display import display, HTML
from pathlib import Path

from support_functions_forecast import get_issue

# Function that "unflags" when value is close to rol value
def rol_close(dataframe_in, flag_name, var, rol_var, var_2, rol_var_2, type_filt, cons_check, cons_check_rol, sector_val, curryr, currqtr):
    
    dataframe = dataframe_in.copy()

    if currqtr == 4:
        period = 1
    else:
        period = currqtr + 1

    if flag_name == "g_flag_nc" or flag_name == "g_flag_vac" or flag_name == "e_flag_market":
        yr_thresh = curryr + 1
    else:
        yr_thresh = curryr

    # If the key to the flag is based primairly on only one variable, the test is:
    if type_filt == 1:
        # Testing for values that are close
        dataframe[flag_name] = np.where((dataframe['yr'] >= yr_thresh) & (np.isnan(dataframe[rol_var]) == False) & (((abs((dataframe[cons_check] - dataframe[cons_check_rol]) / dataframe[cons_check_rol]) < 0.05) | (dataframe[cons_check] == dataframe[cons_check_rol]))) & (((abs((dataframe[var] - dataframe[rol_var]) / dataframe[rol_var]) <= 0.05) | (abs(dataframe[var] - dataframe[rol_var]) < 0.002))) & (dataframe[flag_name] != 0), 7777, dataframe[flag_name])

        # Additional test for values that are close but at low levels, which may not trigger in the first test
        # Construction level needs slightly different low threshold
        if flag_name[0] == "c" or var == "abs":
            dataframe[flag_name] = np.where((dataframe['yr'] >= yr_thresh) & (np.isnan(dataframe[rol_var]) == False) & (abs((dataframe[var] - dataframe[rol_var]) / dataframe['inv']) <= 0.01) &  (dataframe[var] * dataframe[rol_var] >= 0) & (dataframe[flag_name] != 0), 7777, dataframe[flag_name])
        else:
            dataframe[flag_name] = np.where((dataframe['yr'] >= yr_thresh) & (np.isnan(dataframe[rol_var]) == False) & (abs(dataframe[var] - dataframe[rol_var]) < 0.003) & (((abs((dataframe[cons_check] - dataframe[cons_check_rol]) / dataframe[cons_check_rol]) < 0.05) | (dataframe[cons_check] == dataframe[cons_check_rol]))) & (dataframe[var] * dataframe[rol_var] >= 0) & (dataframe[flag_name] != 0), 7777, dataframe[flag_name])
        
    # If the key to the flag is based on two key variables, the test is below
    elif type_filt == 2:
        # Test the first and second vars for closeness
        dataframe[flag_name] = np.where((dataframe['yr'] >= yr_thresh) & (np.isnan(dataframe[rol_var]) == False) & (((abs((dataframe[cons_check] - dataframe[cons_check_rol]) / dataframe[cons_check_rol]) < 0.05) | (dataframe[cons_check] == dataframe[cons_check_rol]))) & (((abs((dataframe[var] - dataframe[rol_var]) / dataframe[rol_var]) <= 0.05) | (abs(dataframe[var] - dataframe[rol_var]) < 0.002))) & (((abs((dataframe[var_2] - dataframe[rol_var_2]) / dataframe[rol_var_2]) <= 0.05) | (abs(dataframe[var_2] - dataframe[rol_var_2]) < 0.002))) & (dataframe[flag_name] != 0), 7777, dataframe[flag_name])
        
        # Second test for different type of closeness for first var, if close, set to dummy var
        if flag_name[0] == "c" or var == "abs":
            dataframe[flag_name] = np.where((dataframe['yr'] >= yr_thresh) & (np.isnan(dataframe[rol_var]) == False) & (abs((dataframe[var] - dataframe[rol_var]) / dataframe['inv']) <= 0.01) & (((abs((dataframe[cons_check] - dataframe[cons_check_rol]) / dataframe[cons_check_rol]) < 0.05) | (dataframe[cons_check] == dataframe[cons_check_rol]))) &  (dataframe[var] * dataframe[rol_var] >= 0) & (dataframe[flag_name] != 0), 8888, dataframe[flag_name])
        else:
            dataframe[flag_name] = np.where((dataframe['yr'] >= yr_thresh) & (np.isnan(dataframe[rol_var]) == False) & (abs(round(dataframe[var],3) - round(dataframe[rol_var],3)) < 0.003) & (((abs((dataframe[cons_check] - dataframe[cons_check_rol]) / dataframe[cons_check_rol]) < 0.05) | (dataframe[cons_check] == dataframe[cons_check_rol]))) & (dataframe[var] * dataframe[rol_var] >= 0) & (dataframe[flag_name] != 0), 8888, dataframe[flag_name])
        # Second test for different type of closeness for second var, and if it is, change the dummy number set in the first var test to another dummy var to indicate it passed, otherwise change it back to 1
        dataframe[flag_name] = np.where((dataframe[flag_name] == 8888) & (abs(round(dataframe[var_2],3) - round(dataframe[rol_var_2],3)) < 0.003) & (dataframe[var_2] * dataframe[rol_var_2] >= 0), 7777, dataframe[flag_name])
        dataframe[flag_name] = np.where((dataframe[flag_name] == 8888), 1, dataframe[flag_name])

    # There are some flags that need to be checked to ensure that the rol value wasnt within a threshold and now the value is outside the threshold, even if it is close. For those vars, leave the dummy 7777 so it can be checked "locally", otherwise, change it to a 0 to remove the flag
    thresh_list = ['c_flag_t', 'v_flag_min', 'v_flag_max', 'v_flag_level', 'v_flag_cons_neg', 'g_flag_max', 'e_flag_min_chg', 'e_flag_max_chg', 'e_flag_min', 'e_flag_max', 'e_flag_market']
    if flag_name in thresh_list:
        False
    else:
        dataframe[flag_name] = np.where((dataframe[flag_name] == 7777), 0, dataframe[flag_name])

    return dataframe

# Flag if construction is below already completed stock in the current forecast year
def c_comp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:
        data['c_flag_comp'] = np.where((data['yr'] == curryr) & (data['qtr'] == 5) &
                                      (data['cons'] < data['curr_yr_trend_cons']),
                                      1, 0)

        data['calc_ccomp'] = np.where((data['c_flag_comp'] == 1), (data['cons'] - data['curr_yr_trend_cons']) * -1, np.nan)
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['c_flag_comp'] = 0

        data['calc_ccomp'] = 0
        calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if construction is below h stock in any forecast year
def c_h(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['c_flag_h'] = np.where((data['yr'] >= curryr) & (data['qtr'] == 5) & 
                                   (data['cons'] < data['round_h_temp']),
                                   1, 0)

    data['calc_ch'] = np.where((data['c_flag_h'] == 1), (data['cons'] - data['round_h_temp']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if construction is above t stock in the most recent two forecast years
def c_t(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['c_flag_t'] = np.where((data['yr'] == curryr) & (data['qtr'] == 5) & (data['forecast_tag'] != 0) &
                                   (data['cons'] > data['round_t_temp']),
                                   1, 0)
    
    data['unused_t'] = data['round_t_temp'].shift(1) - data['cons'].shift(1)
    data['unused_t'] = np.where(data['unused_t'] < 0, 0, data['unused_t'])
    data['c_flag_t'] = np.where((data['yr'] == curryr + 1) & (data['qtr'] == 5) & (data['forecast_tag'] != 0) &
                                   (data['cons'] > (data['round_t_temp'] + (data['unused_t']*0.25))),
                                   1, data['c_flag_t'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'c_flag_t', 'cons', 'rolscon', False, False, 1, 't', 'rol_t', sector_val, curryr, currqtr)
        data['c_flag_t'] = np.where((data['c_flag_t'] == 7777) & (data['rolscon'] > data['rol_t']), 0, data['c_flag_t'])
        data['c_flag_t'] = np.where((data['c_flag_t'] == 7777), 1, data['c_flag_t'])
        data['c_flag_t'] = np.where((data['c_flag_t'] == 1) & ((data['cons'] - data['t']) / data['t'] < (data['rolscon'] - data['rol_t']) / data['rol_t']), 0, data['c_flag_t'])

    data['calc_ct'] = np.where((data['c_flag_t'] == 1), abs(data['cons'] - data['round_t_temp']), np.nan)
    calc_names.append(list(data.columns)[-1])
    
    return data, calc_names

# Flag if construction is higher than h stock and greater than either: the three year historical average for all non current forecast years in the near term forecast years, or greater than the three year rolling average for all years in the long term forecast years 
def c_sup(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['three_yr_roll_cons'] = np.where((data['yr'] >= curryr + 3), ((data['h'].shift(1) + data['e'].shift(1) * 0.2) + (data['h'].shift(2) + data['e'].shift(2) * 0.2) + (data['h'].shift(3) +  + data['e'].shift(3) * 0.2)) / 3, np.nan)

    data['t_thresh'] = np.where((data['five_yr_avg_cons'] == 0), 0.25, 0.5)

    data['cons_cumcount'] = data[(data['forecast_tag'] > 0) & (data['cons'] > 0)].groupby('identity')['cons'].transform('cumcount')
    data['cons_cumcount'] = data['cons_cumcount'] + 1

    data['c_flag_sup'] = np.where((data['forecast_tag'] == 2) & (data['yr'] < curryr + 3) & 
                        (data['cons'] > data['round_h_temp']) & 
                        ((data['cons'] - data['three_yr_avg_cons']) / data['inv'] >= 0.01) &
                        (((data['cons'] - data['round_h_temp']) / (data['t'] - data['round_h_temp']) >= 0.50) | (data['t'] == 0)),
                        1, 0)

    data['c_flag_sup'] = np.where((data['forecast_tag'] == 2) & (data['yr'] >= curryr + 3) & 
                        (data['cons'] > data['round_h_temp']) & 
                        ((data['cons'] - data['three_yr_roll_cons']) / data['inv'] >= 0.01) &
                        ((data['cons'] - data['three_yr_avg_cons']) / data['inv'] >= 0.01) &
                        (((data['cons'] - data['round_h_temp']) / (data['t'] - data['round_h_temp']) >= 0.50) | (data['t'] == 0)),
                        1, data['c_flag_sup'])

    # Additional flag that is not based on diff as percentage of inventory to handle cases where there is cons forecasted with no history to support any completions
    data['c_flag_sup'] = np.where((data['forecast_tag'] == 2) & ((data['yr'] >= curryr + 3) | (data['h'] == 0)) & (data['cons'] > 0) & (data['h'] == 0) & (data['five_yr_avg_cons'] == 0) & (((data['cons'] - data['round_h_temp']) / (data['t'] - data['round_h_temp']) >= data['t_thresh']) | (data['t'] == 0)), 1, data['c_flag_sup'])
    
    # Additional flag testing if high level of cons is justifiable given the lagged vac rate, even if supported by three year average cons
    data['c_flag_sup'] = np.where((data['forecast_tag'] == 2) & (data['cons'] / data['inv'] > data['avg_us_cons_inv']) & (data['vac'].shift(1) > data['10_yr_vac']) & (data['cons'] > data['round_h_temp']) & (data['lim_hist'] > 5) & ((data['cons'] - data['round_h_temp']) >= (data['t'] - data['round_h_temp']) * data['t_thresh']), 1, data['c_flag_sup'])
    
    # Additional flag for outer years to ensure that there is not too many individual forecast years with construction that are unsupported by trend history
    data['c_flag_sup'] = np.where((data['forecast_tag'] == 2) & (data['yr'] >= curryr + 3) & ((data['cons'] - data['three_yr_avg_cons']) / (data['inv']) >= 0.01) & (data['cons_cumcount'] > 1), 1, data['c_flag_sup'])
    
    # Dont flag if there is some t stock in the prior year to support the cons figure
    data['c_flag_sup'] = np.where((data['c_flag_sup'] == 1) & ((data['cons'] - data['h'] <= data['unused_t'] * 0.25) + ((data['t'] - data['round_h_temp']) * data['t_thresh'])), 0, data['c_flag_sup'])

    # Dont flag if the vacancy level is well below the 10 year historical average for the submarket. Here we can assume that there can be some cons, as long as the level is reasonable
    data['c_flag_sup'] = np.where((data['yr'] >= curryr + 3) & (data['vac'].shift(1) <= data['10_yr_35p_vac']) & (data['c_flag_sup'] == 1) & (data['cons'] / data['inv'] < (data['avg_us_cons_inv']) * 0.5) & (data['lim_hist'] > 5), 0, data['c_flag_sup'])
    
    # Dont flag if the employment forecast for the year is significantly better than the historical performance at the metro                    
    data['c_flag_sup'] = np.where((data['c_flag_sup'] == 1) & (data['emp_chg_z'] >= 1.5), 999999999, data['c_flag_sup'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['c_flag_sup'] = np.where((data['c_flag_sup'] == 999999999) & (data['forecast_tag'] == 2) & (data['yr'] < curryr + 3) & 
                        (data['cons'] > data['round_h_temp']) & 
                        ((data['cons'] - data['three_yr_avg_cons']) / (data['three_yr_avg_cons'] + 1) >= 0.75) &
                        ((data['cons'] - data['round_h_temp']) / (data['t'] - data['round_h_temp']) >= 0.50),
                        1, data['c_flag_sup'])

    data['c_flag_sup'] = np.where((data['c_flag_sup'] == 999999999) & (data['forecast_tag'] == 2) & (data['yr'] >= curryr + 3) & 
                        (data['cons'] > data['round_h_temp']) & 
                        ((data['cons'] - data['three_yr_roll_cons']) / (data['three_yr_roll_cons'] + 1) >= 0.75) &
                        ((data['cons'] - data['three_yr_avg_cons']) / (data['three_yr_avg_cons'] + 1) >= 0.75) &
                        ((data['cons'] - data['round_h_temp']) / (data['t'] - data['round_h_temp']) >= 0.50),
                        1, data['c_flag_sup'])

    data['c_flag_sup'] = np.where((data['c_flag_sup'] == 999999999), 0, data['c_flag_sup'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'c_flag_sup', 'cons', 'rolscon', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        
        if currqtr != 4:
            data['c_flag_sup'] = np.where((data['c_flag_sup'] == 1) & ((data['cons'] - data['three_yr_avg_cons']) / (data['three_yr_avg_cons'] + 1) < (data['rolscon'] - data['three_yr_avg_cons']) / (data['three_yr_avg_cons'] + 1)) & (data['yr'] < curryr + 3), 0, data['c_flag_sup'])
            data['c_flag_sup'] = np.where((data['c_flag_sup'] == 1) & ((data['cons'] - data['three_yr_roll_cons']) / (data['three_yr_roll_cons'] + 1) < (data['rolscon'] - data['three_yr_roll_cons']) / (data['three_yr_roll_cons'] + 1)) & (data['yr'] >= curryr + 3), 0, data['c_flag_sup'])

    data['calc_csup'] = np.where((data['c_flag_sup'] == 1), abs((data['cons'] - data['three_yr_avg_cons']) / data['inv']), np.nan)
    data['calc_csup'] = np.where((data['yr'] >= curryr + 3) & (data['c_flag_sup'] == 1), abs((data['cons'] - data['three_yr_roll_cons']) / data['inv']), data['calc_csup'])
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['three_yr_roll_cons', 'unused_t', 't_thresh', 'cons_cumcount'], axis=1)

    return data, calc_names
    
# Flag if construction is higher than h stock plus a reasonable amount of e stock in the current forecast year.
def c_e(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr == 1:
        e_stock_thresh = 0.25
    elif currqtr == 2:
        e_stock_thresh = 0.20
    elif currqtr == 3:
        e_stock_thresh = 0.10
    elif currqtr == 4:
        e_stock_thresh = 0.30

    data['c_flag_e'] = np.where((data['forecast_tag'] == 1) & (data['qtr'] == 5) & 
                                          (data['cons'] > (data['round_h_temp'] + (data['e'] * e_stock_thresh))) & (data['cons'] > data['three_yr_avg_cons']),
                                          1, 0)

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        if currqtr != 3:
            data = rol_close(data, 'c_flag_e', 'cons', 'rolscon', False, False, 1, 't', 'rol_t', sector_val, curryr, currqtr)
            data['c_flag_e'] = np.where((data['c_flag_e'] == 1) & ((data['cons'] - data['e']) / data['e'] < (data['rolscon'] - data['rol_e']) / data['rol_e']), 0, data['c_flag_e'])
    
    data['calc_ce'] = np.where((data['c_flag_e'] == 1), abs(data['cons'] - (data['round_h_temp'] + (data['e'] * e_stock_thresh))), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names
    
# Flag if forecast construction is very low compared to the three year historical average and this is not the current forecast year
def c_hist(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['three_yr_avg_inv'] = data[(data['yr'] > curryr - 4) & (data['yr'] < curryr) & (data['qtr'] == 5)].groupby('identity')['inv'].transform('mean')
    data.fillna({'three_yr_avg_inv' : data['three_yr_avg_inv'].ffill()}, inplace=True)
    
    data['threshold'] = -0.50
    if currqtr == 4: 
        shift_period = 1
    else:
        shift_period = currqtr + 1
    data['three_yr_trail_abs'] = np.where((data['yr'] == curryr + 1), data['abs'].shift(1) +  data['abs'].shift(periods=shift_period + 1) + data['abs'].shift(periods=shift_period + 6), np.nan)
    data['three_yr_trail_cons'] = np.where((data['yr'] == curryr + 1), data['cons'].shift(1) + data['cons'].shift(periods=shift_period + 1) + data['cons'].shift(periods=shift_period + 6), np.nan)
    data['three_yr_trail_abs'] = np.where((data['yr'] == curryr + 2), data['abs'].shift(1) +  data['abs'].shift(2) + data['abs'].shift(periods=shift_period + 2), data['three_yr_trail_abs'])
    data['three_yr_trail_cons'] = np.where((data['yr'] == curryr + 2), data['cons'].shift(1) + data['cons'].shift(2)+ data['cons'].shift(periods=shift_period + 2), data['three_yr_trail_cons'])
    data['three_yr_trail_abs'] = np.where((data['yr'] >= curryr + 3), data['abs'].shift(1) +  data['abs'].shift(2) + data['abs'].shift(3), data['three_yr_trail_abs'])
    data['three_yr_trail_cons'] = np.where((data['yr'] >= curryr + 3), data['cons'].shift(1) + data['cons'].shift(2)+ data['cons'].shift(3), data['three_yr_trail_cons'])
    
    data['threshold'] = np.where(data['three_yr_trail_abs'] / data['three_yr_trail_cons'] >= 0.90, -0.30, data['threshold'])
    data['threshold'] = np.where(data['three_yr_avg_cons'] / data['three_yr_avg_inv'] < data['avg_us_cons_inv'], -0.50, data['threshold'])
    data['threshold'] = np.where((data['emp_chg'] - data['three_yr_avg_emp_chg'] <= -0.01), -0.75, data['threshold'])

    data['count_cons'] = data[(data['yr'] >= curryr - 5) & (data['forecast_tag'] == 0) & (data['qtr'] == 5) & (data['cons'] != 0)].groupby('identity')['cons'].transform('count')
    data['sum_cons'] = data[(data['yr'] >= curryr - 5) & (data['forecast_tag'] == 0) & (data['qtr'] == 5)].groupby('identity')['cons'].transform('sum')
    data.fillna({'count_cons' : data['count_cons'].ffill()}, inplace=True)
    data.fillna({'sum_cons' : data['sum_cons'].ffill()}, inplace=True)
    data['count_cons'] = np.where((data['sum_cons'] == 0), 0, data['count_cons'])
    
    data['c_flag_hist'] = np.where((data['forecast_tag'] == 2) & 
                        ((data['cons'] - data['three_yr_avg_cons']) / (data['three_yr_avg_cons'] + 1) < data['threshold']) & (data['count_cons'] >= 2),
                        1, 0)
    
    # Dont flag if the forecast is for no construction and the prior year has cons if there is no stock in the pipeline to support it
    data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & (data['cons'] == 0) & (data['cons'] >= data['t']) & (data['cons'].shift(1) != 0), 0, data['c_flag_hist'])
    
    # Dont flag if the sub is above the 10 year avg vac rate and cons isnt zero
    data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & (data['cons'] > 0) & (data['vac'] > data['10_yr_vac']), 0, data['c_flag_hist'])

    # Dont flag if the prior year row has cons above the historical average and there is no pipeline stock to support in this year
    data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & (data['yr'] > curryr) & (data['cons'].shift(1) >= data['three_yr_avg_cons']) & (data['cons'] >= data['t']), 0, data['c_flag_hist'])
    
    # Dont flag if there is not enough t stock in curryr + 1 to build - if not in the pipeline, hard to say we will reach three year average at this point
    data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & (data['yr'] == curryr + 1) & (data['cons'] >= data['t']), 0, data['c_flag_hist'])

    # Dont flag if the first year of the forecast is below the three year average (and that should be consistent with what is in the pipeline, which could justify a slowdown from trend history)
    data['first_yr_tag'] = np.where((data['forecast_tag'] == 1) & (data['cons'] < data['three_yr_avg_cons']), 1, 0)
    data['first_yr_tag'] = np.where((data['forecast_tag'] != 1), np.nan, data['first_yr_tag'])
    data.fillna({'first_yr_tag' : data['first_yr_tag'].ffill()}, inplace=True)
    data['first_yr_val'] = np.where((data['forecast_tag'] == 1) & (data['cons'] < data['three_yr_avg_cons']), data['cons'], 0)
    data['first_yr_val'] = np.where((data['forecast_tag'] != 1), np.nan, data['first_yr_val'])
    data.fillna({'first_yr_val' : data['first_yr_val'].ffill()}, inplace=True)
    data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & (data['first_yr_tag'] == 1) & ((data['cons'] - data['first_yr_val']) / data['first_yr_val'] > -0.10), 0, data['c_flag_hist'])

    data = data.drop(['three_yr_avg_inv', 'threshold', 'first_yr_tag', 'first_yr_val', 'count_cons', 'sum_cons', 'three_yr_trail_abs', 'three_yr_trail_cons'], axis=1)

    # Dont flag if the employment forecast for the year is significantly worse than the historical performance at the metro
    data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & (data['emp_chg_z'] <= -1.5), 0, data['c_flag_hist'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'c_flag_hist', 'cons', 'rolscon', False, False, 1, 't', 'rol_t', sector_val, curryr, currqtr)
        if currqtr != 4:
            data['c_flag_hist'] = np.where((data['c_flag_hist'] == 1) & ((data['cons'] - data['three_yr_avg_cons']) / data['three_yr_avg_cons'] > (data['rolscon'] - data['three_yr_avg_cons']) / data['three_yr_avg_cons']), 0, data['c_flag_hist'])
    
    data['calc_chist'] = np.where((data['c_flag_hist'] == 1), ((data['cons'] - data['three_yr_avg_cons']) / (data['three_yr_avg_cons'] + 1)) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names
    

# Flag if construction is different than ROL and there was no significant change in the pipeline
def c_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['c_flag_rol'] = np.where((data['forecast_tag'] != 0) & (abs((data['cons'] - data['rolscon']) / (data['rolscon'] + 1)) > 0.2) & (data['cons'] != data['rolscon']) &
                                    (((abs(data['cons'] - data['rolscon']) > abs(data['round_h_temp'] - data['round_rol_h_temp'])) | ((data['cons'] - data['rolscon']) * (data['round_h_temp'] - data['round_rol_h_temp']) < 0))),
                                    1, 0)

    # Dont flag if the change is support by a change in t stock
    data['c_flag_rol'] = np.where((data['c_flag_rol'] == 1) & (data['cons'] - data['rolscon'] < data['t'] - data['rol_t']) & (data['cons'] - data['rolscon'] > 0), 0, data['c_flag_rol'])
    data['c_flag_rol'] = np.where((data['c_flag_rol'] == 1) & (data['cons'] - data['rolscon'] > data['t'] - data['rol_t']) & (data['cons'] - data['rolscon'] < 0), 0, data['c_flag_rol'])

    data['calc_crol'] = np.where((data['c_flag_rol'] == 1), abs((data['cons'] - data['rolscon']) / (data['rolscon'] + 1)), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names
    
# Flag if construction is lower than an average size building
def c_size(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "ind":
        data['threshold'] = np.where(data['subsector'] == "DW", 50000, 20000)
    elif sector_val == "apt":
        data['threshold'] = 20
    elif sector_val == "off":
        data['threshold'] = 20000
    elif sector_val == "ret":
        data['threshold'] = 10000

    data['c_flag_size'] = np.where((data['forecast_tag'] != 0) & (data['cons'] != 0) & (data['cons'] - data['round_h_temp'] != 0) &
                                      (data['cons'] < data['threshold']),
                                      1, 0)

    # Dont flag if the size was already below the threshold in rol
    data['c_flag_size'] = np.where((data['c_flag_size'] == 1) & ((data['rolscon'] <= data['threshold']) | (data['cons'] >= data['rolscon'])), 0, data['c_flag_size'])
    
    data['calc_csize'] = np.where((data['c_flag_size'] == 1), (data['cons'] - data['threshold']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names
    
# Flag if construction exhibits low variabilty across the submarket forecast series
def c_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):
    
    data['c_flag_lowv'] = np.where((data['forecast_tag'] != 0) & (data['qtr'] == 5) & 
                    (data['f_var_cons'] <= data['f_5_var_cons']) & (data['f_var_cons'].shift(1).isnull() == True),
                    1, 0)

    data = data.drop(['round_h_temp', 'round_rol_h_temp', 'round_t_temp', 'threshold'], axis=1)

    data['calc_clowv'] = np.where((data['c_flag_lowv'] == 1), (data['f_var_cons'] - data['f_5_var_cons']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names
    
# Flag if a vacancy level is below 2 percent and there is significant decline in vacancy rate, or if the vacancy rate is below zero
def v_low(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_low'] = np.where((data['forecast_tag'] != 0) &
                                     ((data['vac'] < 0) |
                                     ((data['vac'] < 0.02) & (data['vac_chg'] < -0.003) & (data['vac'] < data['min_vac']))),
                                     1, 0)
    
    data['calc_vlow'] = np.where((data['v_flag_low'] == 1), (data['vac']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])
    
    return data, calc_names

# Flag if vacancy level is above one hundred percent
def v_high(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_high'] = np.where((data['forecast_tag'] != 0) & (data['vac'] > 1), 1,0)
    
    data['calc_vhigh'] = np.where((data['v_flag_high'] == 1), data['vac'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if absorption construction ratio for all forecast years is too low or too high
def v_ratio(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    # Set the threshold for abs of construction being too low. Use the historical average for the sub if it is in a reasonable range, otherwise use a default of 0.6
    baseline = 0.5
    data['low_r_threshold'] = np.where((data['avg_abs_cons'] >= 0.2) & (data['avg_abs_cons'].isnull() == False) & (data['avg_abs_cons'] < baseline),
                                          data['avg_abs_cons'], baseline)

    data['high_r_threshold'] = np.where((data['vac'] > data['10_yr_vac']), 1.5, 1.2)

    data['rol_abs_cons_r'] = round(data['rolsabs'] / data['rolscon'],2)
    
    if currqtr == 4:
        data['below_three_avg'] = np.where((data['abs'] - data['cons'] < data['three_yr_avg_abs_nonc']), 1, 0)
        data['above_three_avg'] = np.where((data['abs'] - data['cons'] > data['three_yr_avg_abs_nonc']), 1, 0)
    elif currqtr != 4:
        data['below_three_avg'] = np.where((data['forecast_tag'] == 1) & (data['implied_abs'] - data['implied_cons'] < (data['three_yr_avg_abs_nonc'] * ((4 - currqtr) / 4))), 1, 0)
        data['above_three_avg'] = np.where((data['forecast_tag'] == 1) & (data['implied_abs'] - data['implied_cons'] > (data['three_yr_avg_abs_nonc'] * ((4 - currqtr) / 4))), 1, 0)
        data['below_three_avg'] = np.where((data['forecast_tag'] == 2) & (data['abs'] - data['cons'] < data['three_yr_avg_abs_nonc']), 1, data['below_three_avg'])
        data['above_three_avg'] = np.where((data['forecast_tag'] == 2) & (data['abs'] - data['cons'] > data['three_yr_avg_abs_nonc']), 1, data['above_three_avg'])

    data['v_flag_ratio'] = np.where((data['cons'] / data['inv'] >= 0.01) & (data['forecast_tag'] != 0) &
            (data['abs_cons_r'] < data['low_r_threshold']) & (data['vac'] >= 0.03) & 
            (data['below_three_avg'] == 1), 
            1, 0)
    
    data['v_flag_ratio'] = np.where((data['cons'] / data['inv'] >= 0.01) & (data['forecast_tag'] != 0) &
            (data['abs_cons_r'] > data['high_r_threshold']) & (data['extra_used_act'] == 0) & 
            (data['above_three_avg'] == 1),
            1, data['v_flag_ratio'])

    data = data.drop(['below_three_avg', 'above_three_avg'], axis=1)

    # Dont flag if the vac level is above the 10 year avg vac level and the extra abs is not a significant portion of inventory
    if currqtr != 4:
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['forecast_tag'] == 1) & (data['vac'] > data['10_yr_vac'] + 0.01) & ((data['implied_abs'] - data['implied_cons']) / data['inv'] <= 0.01) & (data['abs_cons_r'] > 1), 0, data['v_flag_ratio'])
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['forecast_tag'] == 2) & (data['vac'] > data['10_yr_vac'] + 0.01) & ((data['abs'] - data['cons']) / data['inv'] <= 0.02) & (data['abs_cons_r'] > 1), 0, data['v_flag_ratio'])
    elif currqtr == 4:
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['vac'] > data['10_yr_vac'] + 0.01) & ((data['abs'] - data['cons']) / data['inv'] <= 0.02) & (data['abs_cons_r'] > 1), 0, data['v_flag_ratio'])
    
    # Dont flag if the vac level is below the 10 year avg vac level and the missing abs is not a significant portion of inventory
    if currqtr != 4:
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['forecast_tag'] == 1) & (data['vac'] < data['10_yr_vac'] - 0.01) & ((data['implied_cons'] - data['implied_abs']) / data['inv'] <= 0.01) & (data['abs_cons_r'] < 1), 0, data['v_flag_ratio'])
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['forecast_tag'] == 2) & (data['vac'] < data['10_yr_vac'] - 0.01) & ((data['cons'] - data['abs']) / data['inv'] <= 0.02) & (data['abs_cons_r'] < 1), 0, data['v_flag_ratio'])
    elif currqtr == 4:
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['vac'] < data['10_yr_vac'] - 0.01) & ((data['cons'] - data['abs']) / data['inv'] <= 0.02) & (data['abs_cons_r'] < 1), 0, data['v_flag_ratio'])
    
    # Dont flag if the vac level is in line with the current trend vac and abs cons ratio is not causing a large decrease in vac
    data['curr_trend_vac'] = np.where((data['yr'] == curryr) & (data['qtr'] == currqtr), data['vac'], np.nan)
    data['curr_trend_vac'] = data.groupby('identity')['curr_trend_vac'].ffill()
    data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['vac'] > data['curr_trend_vac'] - 0.01) & (data['vac_chg'] > -0.01) & (data['abs_cons_r'] > 1), 0, data['v_flag_ratio'])
    if sector_val != "ind":
        data = data.drop(['curr_trend_vac'],axis=1)

    # Dont flag if employment change indicates large departure from history
    data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['abs_cons_r'] < data['low_r_threshold']) & (data['emp_chg_z'] <= -1.5), 999999999, data['v_flag_ratio'])
                
    data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['abs_cons_r'] > data['low_r_threshold']) & (data['emp_chg_z'] >= 1.5), 999999999, data['v_flag_ratio'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 999999999) & (data['cons'] / data['inv'] >= 0.01) & (data['forecast_tag'] != 0) &
            (data['abs_cons_r'] > 2.5) &
            (data['abs'] - data['cons'] - data['extra_used_act'] > data['three_yr_avg_abs_nonc']),
            1, data['v_flag_ratio'])

    data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 999999999), 0, data['v_flag_ratio'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_ratio', 'abs_cons_r', 'rol_abs_cons_r', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['abs_cons_r'] > data['rol_abs_cons_r']) & (data['abs_cons_r'] < 1) & (data['rolscon'] != 0), 0, data['v_flag_ratio'])
        data['v_flag_ratio'] = np.where((data['v_flag_ratio'] == 1) & (data['abs_cons_r'] < data['rol_abs_cons_r']) & (data['abs_cons_r'] > 1), 0, data['v_flag_ratio'])

    data = data.drop(['rol_abs_cons_r'], axis=1)

    if currqtr == 4:
        data['calc_vratio'] = np.where((data['v_flag_ratio'] == 1), abs((data['abs'] - data['cons']) / data['inv']), np.nan)
        calc_names.append(list(data.columns)[-1])
    elif currqtr != 4:
        data['calc_vratio'] = np.where((data['forecast_tag'] == 1) & (data['v_flag_ratio'] == 1), abs((data['implied_abs'] - data['implied_cons']) / data['inv']), np.nan)
        data['calc_vratio'] = np.where((data['forecast_tag'] != 1) & (data['v_flag_ratio'] == 1), abs((data['abs'] - data['cons']) / data['inv']), data['calc_vratio'])
        calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if construction from prior years is not getting absorbed in subsequent years
def v_roll(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['vac_to_recover'] = 0
    data['vac_recovered'] = 0
    data['cons_inv_perc'] = 0

    for x in range(0, 10):
        if currqtr == 4: 
            extra = 0
        elif currqtr != 4:
            extra = currqtr
        if x == 0:
            period = 16 + extra
            period2 = 11 + extra
        elif x == 1:
            period = 12 + extra
            period2 = 7 + extra
        elif x == 2:
            period = 8 + extra
            period2 = 3 + extra
        elif x == 3 and currqtr != 4:
            period = 4 + currqtr
            period2 = 3
        else:
            period = 4
            period2 = 3

        data['cons_unabs'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5) & (data['cons'].shift(periods=period2) > 0) & (data['cons'].shift(periods=period2) > data['abs'].shift(periods=period2)) & (data['abs'].shift(periods=period2) >= 0), data['cons'].shift(periods=period2) - data['abs'].shift(periods=period2), np.nan)
        data['cons_unabs'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5) & (data['cons'].shift(periods=period2) > 0) & (data['cons'].shift(periods=period2) <= data['abs'].shift(periods=period2)), 0, data['cons_unabs'])
        data['cons_unabs'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5) & (data['cons'].shift(periods=period2) > 0) & (data['abs'].shift(periods=period2) < 0), data['cons'].shift(periods=period2), data['cons_unabs'])
        data['vac_to_recover'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5), ((data['avail'].shift(periods=period) + data['cons_unabs']) / data['inv'].shift(periods=period2)) - data['vac'].shift(periods=period), data['vac_to_recover'])
        data['vac_recovered'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5), data['vac'] - data['vac'].shift(periods=period2), data['vac_recovered'])
        data['cons_inv_perc'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5), data['cons'].shift(periods=period2) / data['inv'].shift(periods=period2), data['cons_inv_perc'])
        
        data['vac_to_recover'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5) & (data['vac_to_recover'] < 0), 0, data['vac_to_recover'])
        data['vac_recovered'] = np.where((data['yr'] == curryr + x) & (data['qtr'] == 5) & (data['vac_to_recover'] <= 0), 0, data['vac_recovered'])
        
        data['vac_to_recover'] = np.where((data['identity'] != data['identity'].shift(periods=period)), 0, data['vac_to_recover'])
        data['vac_recovered'] = np.where((data['identity'] != data['identity'].shift(periods=period)), 0, data['vac_recovered'])

    
    data['v_flag_roll'] = np.where((data['forecast_tag'] == 2) &
                                                (data['vac_to_recover'] > (data['vac_recovered'] - 0.01) * -1) &
                                                (data['v_flag_ratio'] == 0) &
                                                (data['cons_inv_perc'] >= 0.01),
                                                1, 0)
    
    data['vac_recovered'] = np.where(data['vac_recovered'] > 0, 0, data['vac_recovered'])

    # Dont flag if the submarket is both below the sub's 10 year vac avg and the below or close to the national vac avg
    data['v_flag_roll'] = np.where((data['v_flag_roll'] == 1) & (data['vac'] <= data['10_yr_vac']) & (data['vac'] < data['us_vac_level_avg'] + 0.025) & (data['vac_to_recover'] + data['vac_recovered']< 0.035), 0, data['v_flag_roll'])

    # Dont flag if employment change in the second year of the three year period indicates that the economic conditions were very poor, so we would not expect all the cons to be absorbed.
    data['v_flag_roll'] = np.where((data['v_flag_roll'] == 1) & (data['emp_chg_z'].shift(1) <= -1.5) & (data['vac_to_recover'] + data['vac_recovered'] < 0.035), 0, data['v_flag_roll'])
    
    # Dont flag if employment change indicates that the economic conditions are poor in the third year of the three year period
    data['v_flag_roll'] = np.where((data['v_flag_roll'] == 1) & (data['emp_chg_z'] <= -1.5), 0, data['v_flag_roll'])
    
    data['calc_vroll'] = np.where((data['v_flag_roll'] == 1), abs(data['vac_to_recover'] - data['vac_recovered']), np.nan)
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['vac_to_recover', 'vac_recovered', 'cons_unabs', 'cons_inv_perc'], axis=1)

    return data, calc_names

# Flag if vac forecast in the curr year forecast row results in a change from ROL absorption and the change increases the implied level
def v_improls(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    
    if currqtr != 4:
        
        data['v_flag_improls'] = np.where((data['forecast_tag'] == 1) &
            (abs(((data['implied_abs'] - data['implied_cons']) - data['hist_implied_abs'])) > abs(((data['implied_rolsabs'] - data['implied_cons']) - data['hist_implied_abs']))) & 
            (abs(((data['implied_abs'] - data['implied_cons']) - data['hist_implied_abs']) - ((data['implied_rolsabs'] - data['implied_cons']) - data['hist_implied_abs'])) / data['inv'] >= 0.0015),
            1, 0)
    
        # Dont flag if the employment forecast has changed significantly from ROL
        data['emp_chg_test'] = np.where((abs(((data['implied_abs'] - data['implied_cons']) - (data['implied_rolsabs'] - data['implied_cons'])) / data['prev_occ']) < abs(data['emp_chg_diff'] * 3)), 1, 0)
        data['v_flag_improls'] = np.where((data['v_flag_improls'] == 1) & (((data['implied_abs'] - data['implied_cons']) - data['hist_implied_abs']) > ((data['implied_rolsabs'] - data['implied_cons']) - data['hist_implied_abs'])) & (data['emp_chg_diff'] > 0) & (data['emp_chg_test'] == 1), 0, data['v_flag_improls'])
        data['v_flag_improls'] = np.where((data['v_flag_improls'] == 1) & (((data['implied_abs'] - data['implied_cons']) - data['hist_implied_abs']) < ((data['implied_rolsabs'] - data['implied_cons']) - data['hist_implied_abs'])) & (data['emp_chg_diff'] < 0) & (data['emp_chg_test'] == 1), 0, data['v_flag_improls'])
    
        
        data['calc_vimprols'] = np.where((data['v_flag_improls'] == 1), abs((data['implied_abs'] - data['implied_cons']) - data['hist_implied_abs']) - abs((data['implied_rolsabs'] - data['implied_cons']) - data['hist_implied_abs']), np.nan)
        data['calc_vimprols'] = np.where((data['v_flag_improls'] == 1), abs(data['calc_vimprols']), data['calc_vimprols'])
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['calc_vimprols'] = 0
        calc_names.append(list(data.columns)[-1])
        data['v_flag_improls'] = 0
    
    return data, calc_names

# Flag if abs is very different than rol and the cause is not a change in cons
def v_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_rol'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['forecast_tag'] == 2)) &
                                    (abs(((data['abs'] - data['rolsabs']) - (data['cons'] - data['rolscon'])) / data['inv']) > 0.01),
                                     1, 0)

    # Dont flag if the change in abs is less severe than the change in cons, even if the difference is a large portion of inv. If this is the case, it will be handled by other flags like v_flag_ratio
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & ((data['abs'] - data['rolsabs']) < (data['cons'] - data['rolscon'])) & ((data['abs'] - data['rolsabs']) * (data['cons'] - data['rolscon']) > 0) & (data['abs'] - data['rolsabs'] > 0), 0, data['v_flag_rol'])
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & ((data['abs'] - data['rolsabs']) > (data['cons'] - data['rolscon'])) & ((data['abs'] - data['rolsabs']) * (data['cons'] - data['rolscon']) > 0) & (data['abs'] - data['rolsabs'] < 0), 0, data['v_flag_rol'])
    
    # Dont flag if the change in abs from rol is due to the need to absorb prior year construction in the rolling 3 period
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & (data['abs'] > data['rolsabs']) & (data['extra_used_act'] > 0) & (data['extra_used_act'] >= data['abs'] - data['rolsabs']), 0, data['v_flag_rol'])
    
    # Dont flag if the abs/cons ratio is still similar
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & (data['cons'] > 0) & (data['rolscon'] > 0) & (abs((data['abs'] / data['cons']) - (data['rolsabs'] / data['rolscon'])) < 0.2) & ((data['abs'] / data['cons']) * (data['rolsabs'] / data['rolscon']) > 0), 0, data['v_flag_rol'])

    # Dont flag if the prior year trend row had an unanticipated reset of the vac level, which would support a change in the forecasted abs
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & (data['vac'] < data['rolsvac']) & (data['abs'] < data['rolsabs']), 0, data['v_flag_rol'])
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & (data['vac'] > data['rolsvac']) & (data['abs'] > data['rolsabs']), 0, data['v_flag_rol'])

    # Dont flag if the employment forecast has changed significantly from ROL
    data['emp_chg_test'] = np.where((abs(((data['abs'] - data['rolsabs'])- (data['cons'] - data['rolscon'])) / data['inv']) < abs(data['emp_chg_diff'] * 3)), 1, 0)
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & (((data['abs'] - data['rolsabs'])- (data['cons'] - data['rolscon'])) / data['inv'] > 0) & (data['emp_chg_diff'] > 0) & (data['emp_chg_test'] == 1), 0, data['v_flag_rol'])
    data['v_flag_rol'] = np.where((data['v_flag_rol'] == 1) & (((data['abs'] - data['rolsabs'])- (data['cons'] - data['rolscon'])) / data['inv'] < 0) & (data['emp_chg_diff'] < 0) & (data['emp_chg_test'] == 1), 0, data['v_flag_rol'])

    data['calc_vrol'] = np.where((data['v_flag_rol'] == 1), abs(((data['abs'] - data['rolsabs'])- (data['cons'] - data['rolscon'])) / data['inv']), np.nan)
    calc_names.append(list(data.columns)[-1])
    
    return data, calc_names

# Flag if the vacancy change is in the opposite direction from ROL
def v_switch(data, curryr, currqtr, sector_val, calc_names, use_rol_close):
    
    data['v_flag_switch'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['forecast_tag'] == 2)) & 
                                        (round(data['vac_chg'],3) * round(data['rolsvac_chg'],3) < 0),
                                         1, 0)

    # Dont flag if the change is due to new cons causing a justifiable increase and the abs/cons ratio is acceptable
    data['v_flag_switch'] = np.where((data['v_flag_switch'] == 1) & (data['cons'] > data['rolscon']) & (data['vac_chg'] > 0) & (data['abs_cons_r'] >= 0.6), 0, data['v_flag_switch'])
    
    # Dont flag if the change is due to new cons in a prior year and the increase in abs is to help absorb it
    data['v_flag_switch'] = np.where((data['v_flag_switch'] == 1) & (data['extra_used_act'] > (data['abs'] - data['rolsabs']) * 0.5) & (data['abs'] > data['rolsabs']), 0, data['v_flag_switch'])

    # Dont flag if the change is due to removal of cons causing a removal of a vac increase, so long as the new vac decrease is reasonable
    data['v_flag_switch'] = np.where((data['v_flag_switch'] == 1) & (data['cons'] == 0) & (data['rolscon'] > 0) & (data['vac_chg'] < 0) & (data['vac_chg'] >= -0.003), 0, data['v_flag_switch'])

    # Dont flag if using rol abs would push vac level very low, and the 10 year vac level avg doesnt support it
    data['vac_w_rolsabs'] = 1 - ((data['prev_occ'] + data['rolsabs']) / data['inv'])
    data['v_flag_switch'] = np.where((data['v_flag_switch'] == 1) & (data['vac_w_rolsabs'] < 0.04) & (data['10_yr_vac'] > data['vac_w_rolsabs']), 0, data['v_flag_switch'])
    data = data.drop(['vac_w_rolsabs'], axis=1)

    # Dont flag if employment change is significantly different than what it as in ROL 
    data['emp_chg_test'] = np.where((abs(data['vac_chg'] - data['rolsvac_chg']) < abs(data['emp_chg_diff'] * 3)), 1, 0)
    data['v_flag_switch'] = np.where((data['v_flag_switch'] == 1) & (data['emp_chg_diff'] < 0) & (data['vac_chg'] > 0) & (data['emp_chg_test'] == 1), 0, data['v_flag_switch'])
    data['v_flag_switch'] = np.where((data['v_flag_switch'] == 1) & (data['emp_chg_diff'] > 0) & (data['vac_chg'] < 0) & (data['emp_chg_test'] == 1), 0, data['v_flag_switch'])
    
    data = data.drop(['emp_chg_test'], axis=1)
    
    data['calc_vswitch'] = np.where((data['v_flag_switch'] == 1), abs(abs(data['vac_chg']) - abs(data['rolsvac_chg'])), np.nan)
    calc_names.append(list(data.columns)[-1])
    
    return data, calc_names

# Flag if vac forecast in the curr year forecast row is leaving a large amount of implied absorption
def v_imp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:    

        data['v_flag_imp'] = np.where((data['forecast_tag'] == 1) & 
            (abs(((data['implied_abs'] - (data['implied_cons'] * 0.8)) - data['hist_implied_abs']) / (data['hist_implied_abs']+1)) >= 0.25) &
            (abs(((data['implied_abs'] - (data['implied_cons'] * 0.8)) - data['hist_implied_abs']) / data['inv'])>= 0.01),
            1, 0)

        # Dont flag if this is Q3 and the implied abs is close to the avg quarterly trend abs for the year
        if currqtr == 3:
            data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & (abs((data['implied_abs'] - (data['total_trend_abs'] / 3)) / (data['total_trend_abs'] / 3)) < 0.25) & (data['implied_abs'] * data['total_trend_abs'] >= 0), 0, data['v_flag_imp'])
            data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & (data['implied_abs'] < (data['total_trend_abs'] / 3)) & (data['hist_implied_abs'] < data['total_trend_abs'] / 3) & (data['implied_abs'] * data['total_trend_abs'] >= 0), 0, data['v_flag_imp'])
        
        # Dont flag if the abs is due to absorption of construction
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & (data['implied_cons'] >= data['implied_abs']) & (data['implied_abs'] > 0) & (data['hist_implied_abs'] < data['implied_abs']), 0, data['v_flag_imp'])
        
        # Dont flag if the extra abs is due to helping absorb prior year cons
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & ((data['implied_abs'] - (data['implied_cons'] * 0.8)) - data['hist_implied_abs'] > 0) & ((data['implied_abs'] - (data['implied_cons'] * 0.8)) - data['hist_implied_abs'] <= data['extra_used_act'] * 2), 0, data['v_flag_imp'])

        # Dont flag if employment chg z score indicates that this is an outlier year for emp chg, causing us to rely less on the historical performance
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & ((data['implied_abs'] - (data['implied_cons'] * 0.8)) > data['hist_implied_abs']) & (data['emp_chg_z'] >= 1.5), 999999999, data['v_flag_imp'])
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & ((data['implied_abs'] - (data['implied_cons'] * 0.8)) < data['hist_implied_abs']) & (data['emp_chg_z'] <= -1.5), 999999999, data['v_flag_imp'])

        # Dont flag if the sub does not have a long trend history, and the implied abs is in same direction as historical implied abs and less in magnitude
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & (data['lim_hist'] <= 5) & (abs(data['implied_abs']) < abs(data['hist_implied_abs'])) & (data['implied_abs'] * data['hist_implied_abs'] > 0), 0, data['v_flag_imp'])
        
        # Dont flag if the implied vac chg is negligible and there has been positive trend abs and the submarket vac level is well below the 10 year average for the sub
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 1) & (data['total_trend_abs'] > 0) & (abs(data['implied_vac_chg']) < 0.002) & ((data['vac'] < data['10_yr_vac'] / 1.5) | (data['vac'] < 0.04)) & (data['hist_implied_abs'] > 0), 0, data['v_flag_imp'])
        
        # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 999999999) & (abs(((data['implied_abs'] - (data['implied_cons'] * 0.8)) - data['hist_implied_abs']) / data['inv']) >= 0.05), 1, data['v_flag_imp'])

        data['v_flag_imp'] = np.where((data['v_flag_imp'] == 999999999), 0, data['v_flag_imp'])

        data['calc_vimp'] = np.where((data['v_flag_imp'] == 1), abs(((data['implied_abs'] - (data['implied_cons'] * 0.8)) - data['hist_implied_abs']) / (data['hist_implied_abs']+1)), np.nan)
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['calc_vimp'] = 0
        data['v_flag_imp'] = 0
        calc_names.append(list(data.columns)[-1])
    
    return data, calc_names

# Flag if a vac forecast is greater than a z-score of 1.5 for the submarket
def v_z(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr == 4:
        period = 1
    else:
        period = currqtr + 1
    data['prev_avail'] = np.where(data['yr'] > curryr, data['avail'].shift(1), data['avail'].shift(periods=period))

    data['v_flag_z'] = np.where((data['forecast_tag'] != 0) & (((data['avail'] - data['prev_avail'] > data['cons'])) | (data['vac_chg'] <= 0)) & 
                                    (data['vac_z'] > 1.5),
                                    1, 0)                        

    data['v_flag_z'] = np.where((data['forecast_tag'] != 0) & 
                                    (data['vac_z'] < -1.5), 1, data['v_flag_z'])

    # Dont flag if the submarket has a limited trend history to draw z score from and vac change is within reasonable bound
    if currqtr != 4:
        data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['forecast_tag'] == 1) & (data['lim_hist'] <= 5) & (abs(data['implied_vac_chg']) < (data['avg_vac_chg'] * ((4 - currqtr) / 4))), 0, data['v_flag_z'])
        data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['forecast_tag'] == 2) & (data['lim_hist'] <= 5) & ((abs(data['vac_chg']) < data['avg_vac_chg']) | (abs(data['vac_chg']) < 0.01)), 0, data['v_flag_z'])
    elif currqtr == 4:
        data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['lim_hist'] <= 5) & ((abs(data['vac_chg']) < data['avg_vac_chg']) | (abs(data['vac_chg']) < 0.01)), 0, data['v_flag_z'])

    # Dont flag if construction is the cause for a vac increase, as long as abs cons is reasonable
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac_chg'] > 0) & (data['cons'] > 0) & (data['abs_cons_r'] >= data['low_r_threshold']), 0, data['v_flag_z'])

    # Dont flag if the vac chg is negligible and the submarket is close to its historical min
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac'] < data['min_vac'] + 0.01) & (((data['vac_chg'] <= 0.002) & (data['vac_chg'] >= 0)) | ((data['vac_chg'] >= -0.002) & (data['vac'] >= data['min_vac']))) & (data['min_vac'] < data['us_vac_level_avg']) & (data['lim_hist'] > 5), 0, data['v_flag_z'])

    # Dont flag if abs of prior year cons is the cause for vac decrease
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['extra_used_act'] > 0) & (data['abs'] - data['rolsabs'] <= data['extra_used_act'] * 2), 0, data['v_flag_z'])

    # Dont flag if the submarket is trying to return to a long term vac level by declining in vac
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac_chg'] < 0) & (data['vac_chg'] > -0.07) & (abs(data['vac_chg']) > data['avg_vac_chg']) & (data['vac'] >= data['10_yr_vac']) & (data['lim_hist'] > 5), 0, data['v_flag_z'])

    # Dont flag if the submarket vac chg is lower in mag than the avg chg, and the submarket is near the long term avg and the long term avg is below the us avg
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (abs(data['vac_chg']) < data['avg_vac_chg']) & (data['vac'] < data['10_yr_vac'] + 0.01) & (data['vac'] < data['us_vac_level_avg'] - 0.01), 0, data['v_flag_z'])

    # Dont flag if change in employment is very different than the historical emp chg
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac_chg'] > 0) & (data['emp_chg_z'] <= -1.5), 999999999, data['v_flag_z'])
    data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac_chg'] < 0) & (data['emp_chg_z'] >= 1.5), 999999999, data['v_flag_z'])
    
    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['v_flag_z'] = np.where((data['v_flag_z'] == 999999999) & (data['forecast_tag'] != 0) & (abs(data['vac_z']) > 3),
                                    1, data['v_flag_z'])
    
    data['v_flag_z'] = np.where((data['v_flag_z'] == 999999999), 0, data['v_flag_z'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_z', 'vac_chg', 'rolsvac_chg', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac_z'] < (abs(data['rolsvac_chg']) - data['avg_vac_chg']) / data['std_dev_vac_chg']) & (data['vac_z'] > 0), 0, data['v_flag_z'])
        data['v_flag_z'] = np.where((data['v_flag_z'] == 1) & (data['vac_z'] > (abs(data['rolsvac_chg']) - data['avg_vac_chg']) / data['std_dev_vac_chg']) & (data['vac_z'] < 0), 0, data['v_flag_z'])

    data = data.drop(['low_r_threshold', 'high_r_threshold', 'prev_avail'], axis=1)

    data['calc_vz'] = np.where((data['v_flag_z'] == 1), abs(data['vac_z']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if a vac forecast is a new 10 year low for the submarket
def v_min(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_min'] = np.where((data['forecast_tag'] != 0) &
                                     (round(data['vac'],3) < round(data['min_vac'],3) - 0.001),
                                     1, 0)

    # Dont flag if the sub is within 1% of the min and the vac is above the US average, or vac chg is not severe and the vac is well above the US average
    data['v_flag_min'] = np.where((data['v_flag_min'] == 1) & ((data['vac'] > data['min_vac'] - 0.01) | (data['vac_chg'] > -0.02)) & (data['vac'] > data['us_vac_level_avg']), 0, data['v_flag_min'])
    
    # Dont flag if the sub has a limited trend history and the vacancy level is above the US average
    data['v_flag_min'] = np.where((data['v_flag_min'] == 1) & (data['lim_hist'] <= 5) & (data['vac'] > data['us_vac_level_avg']), 0, data['v_flag_min'])
    
    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_min', 'vac', 'rolsvac', 'vac_chg', 'rolsvac_chg', 2, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['v_flag_min'] = np.where((data['v_flag_min'] == 7777) & (round(data['rolsvac'],3) <= round(data['min_vac'],3)), 0, data['v_flag_min'])
        data['v_flag_min'] = np.where((data['v_flag_min'] == 7777), 1, data['v_flag_min'])
        data['v_flag_min'] = np.where((data['v_flag_min'] == 1) & (round(data['vac'],3) > round(data['rolsvac'],3)), 0, data['v_flag_min'])

    data['calc_vmin'] = np.where((data['v_flag_min'] == 1), (data['vac'] - data['min_vac']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if a vac forecast is a new 10 year high for the submarket, and construction is within a reasonable bound
def v_max(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_max'] = np.where((data['forecast_tag'] != 0) & 
                                      (data['vac'] > data['max_vac'] + 0.001),
                                      1, 0)

    # Dont flag if employment indicates that an unprecented high vac level is reasonable
    data['v_flag_max'] = np.where((data['v_flag_max'] == 1) & (data['emp_chg_z'] <= -2), 999999999, data['v_flag_max'])
    
    # Dont flag if absorption of construction is within a reasonable bound and the cons is the cause of the high vac rate
    data['v_flag_max'] = np.where((data['forecast_tag'] != 0) & 
                                      (data['v_flag_max'] == 1) & 
                                      (data['abs_cons_r'] > 0.4),
                                      0, data['v_flag_max'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['v_flag_max'] = np.where((data['v_flag_max'] == 999999999) & (data['forecast_tag'] != 0) & 
                                      ((data['vac'] - data['max_vac']) / data['max_vac'] > 0.15),
                                      1, data['v_flag_max'])

    data['v_flag_max'] = np.where((data['v_flag_max'] == 999999999), 0, data['v_flag_max'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_max', 'vac', 'rolsvac', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['v_flag_max'] = np.where((data['v_flag_max'] == 7777) & (data['rolsvac'] >= data['max_vac']), 0, data['v_flag_max'])
        data['v_flag_max'] = np.where((data['v_flag_max'] == 7777), 1, data['v_flag_max'])
        data['v_flag_max'] = np.where((data['v_flag_max'] == 1) & (data['vac'] < data['rolsvac']), 0, data['v_flag_max'])

    data['calc_vmax'] = np.where((data['v_flag_max'] == 1), data['vac'] - data['max_vac'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if there is low vacancy variability in the forecast of a sub
# Only flag it in the most recent full forecast year, as that will be enough of an alert and will minimize sum of flags and need to skip etc
def v_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    
    data['v_flag_lowv'] = np.where((data['yr'] == curryr + 1) & 
                                         ((data['f_var_vac_chg'] < data['f_5_var_vac_chg']) | (round(data['f_var_vac_chg'],3) == 0)) & (data['f_var_vac_chg'].shift(1).isnull() == True),
                                         1, 0)
    
    data['calc_vlowv'] = np.where((data['v_flag_lowv'] == 1), (data['f_var_vac_chg'] - data['f_5_var_vac_chg']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if vacancy level is well off the 10 year vac trend level, and this is a five outer year row
def v_level(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_level'] = np.where((data['yr'] >= curryr + 5) & (abs((data['vac'] - data['10_yr_vac']) / data['10_yr_vac']) > 0.20) & (abs(data['vac'] - data['10_yr_vac']) > 0.01), 1, 0)

    # Dont flag if the submarket has a limited trend history and vac chg is reasonable
    data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['lim_hist'] <= 5) & (abs(data['vac_chg']) < 0.005), 0, data['v_flag_level'])

    # Dont flag if the vac chg is moving closer to the 10 year vac avg
    data['v_flag_level'] = np.where(((data['vac'] > data['10_yr_vac']) & (data['vac_chg'] < 0)) | ((data['vac'] < data['10_yr_vac']) & (data['vac_chg'] > 0)), 0, data['v_flag_level']) 

    # Dont flag if the vac is rising negligibly and the prior year vac and following year vac is decreasing
    data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['vac_chg'] < 0.0005) & (data['vac_chg'] > 0) & (data['vac_chg'].shift(1) < -0.002) & (((data['vac_chg'].shift(-1) < -0.002) & (data['identity'] == data['identity'].shift(-1))) | (data['yr'] == curryr + 9)), 0, data['v_flag_level'])

    # Dont flag if the sector is industrial and the 10 year vacancy level is high and the decrease in vac is reasonable.
    # Since Ind subs typically had inflated vac levels compared to what other market providers published, moving away from a high ten year vac level is understandable
    if sector_val == "ind":
        data['outer_vac_chg'] = np.where((data['yr'] == curryr + 5), data['vac'] - data['vac'].shift(5), np.nan)
        data['outer_vac_chg'] = data.groupby('identity')['outer_vac_chg'].ffill()
        data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['vac'] < data['10_yr_vac']) & (data['10_yr_vac'] >= data['us_vac_level_avg'] - 0.005) & ((data['outer_vac_chg'] > -0.01) | ((data['outer_vac_chg'] > -0.025) & (data['vac'] > data['10_yr_vac'] - 0.025))), 0, data['v_flag_level'])
        data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['vac'] < data['10_yr_vac']) & (data['10_yr_vac'] >= data['us_vac_level_avg'] - 0.005) & (data['lim_hist'] < 5) & (data['vac'] > data['us_vac_level_avg'] - 0.025), 0, data['v_flag_level'])
        data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['vac'] < data['10_yr_vac']) & (data['10_yr_vac'] >= data['us_vac_level_avg'] + 0.025) & (data['outer_vac_chg'] > -0.05) & ((data['vac'] > data['10_yr_vac'] - 0.04) | (data['vac'] > data['us_vac_level_avg'] - 0.02)), 0, data['v_flag_level'])
        data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['vac'] < data['10_yr_vac']) & (data['10_yr_vac'] >= data['us_vac_level_avg'] + 0.075) & ((data['vac'] >= 0.1) | ((data['curr_trend_vac'] < data['10_yr_vac']) & (data['vac'] >= data['curr_trend_vac']))), 0, data['v_flag_level'])
        data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (data['vac'] >= data['curr_trend_vac'] - 0.01) & (data['vac'] < data['10_yr_vac']) & (data['outer_vac_chg'] > -0.01), 0, data['v_flag_level'])
        data = data.drop(['curr_trend_vac', 'outer_vac_chg'], axis=1)

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_level', 'vac', 'rolsvac', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['v_flag_level'] = np.where((((data['v_flag_level'] == 7777) | (data['v_flag_level'] == 1))) & ((abs(data['rolsvac'] - data['10_yr_vac']) > abs(data['vac'] - data['10_yr_vac'])) | (abs(data['vac_chg'] - data['rolsvac_chg']) < 0.002)), 0, data['v_flag_level'])
        data['v_flag_level'] = np.where((data['v_flag_level'] == 7777), 1, data['v_flag_level'])
        if currqtr != 4:
            data['v_flag_level'] = np.where((data['v_flag_level'] == 1) & (abs((data['vac'] - data['10_yr_vac']) / data['10_yr_vac']) < abs((data['rolsvac'] - data['10_yr_vac']) / data['10_yr_vac'])), 0, data['v_flag_level'])

    data['calc_vlevel'] = np.where((data['v_flag_level'] == 1), abs((data['vac'] - data['10_yr_vac']) / data['10_yr_vac']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if absorption forecast is different than the three year trend
def v_3trend(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_3_trend'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['yr'] == curryr + 1)) & 
                                        (((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1) > 0.20) & 
                                        (abs(((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / data['inv'])>0.015), 
                                        1, 0)

    data['v_flag_3_trend'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['yr'] == curryr + 1)) & 
                                        (((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1) < -0.20) & 
                                        (abs(((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / data['inv'])>0.015), 
                                        2, data['v_flag_3_trend'])

    
    # Dont flag in cases where the extra abs is to absorb nc space that wasnt absorbed
    data['v_flag_3_trend'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['yr'] == curryr + 1)) & 
                                        (data['v_flag_3_trend'] != 0) & 
                                        ((data['abs'] - data['cons']) - data['extra_used_act'] < data['three_yr_avg_abs_nonc']) & ((data['abs'] - data['cons']) - data['extra_used_act'] > 0),
                                        0, data['v_flag_3_trend'])

    # Dont flag if the sub is close to the min historical vac or historical max, even if three year trend indicates vac should move in that direction
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['abs'] - data['cons']) > data['three_yr_avg_abs_nonc']) & (data['vac'].shift(1) > data['max_vac'] - 0.01), 0, data['v_flag_3_trend'])
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['abs'] - data['cons']) < data['three_yr_avg_abs_nonc']) & (data['vac'].shift(1) < data['min_vac'] + 0.01), 0, data['v_flag_3_trend'])

    # Dont flag if the sub has a limited trend history and the vacancy level is above the US average
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & (data['lim_hist'] <= 3) & (data['vac'] > data['us_vac_level_avg']) & (data['vac_chg'] < 0), 0, data['v_flag_3_trend'])
    
    # Dont flag if the sub is very different than the 10 year vacancy level average for the sub, and vac is moving back towards the ten year average
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['vac'].shift(1) - data['10_yr_vac']) * data['vac_chg'] < 0) & (abs(data['vac_chg']) / abs(data['vac'].shift(1) - data['10_yr_vac']) <= 0.5) & (data['lim_hist'] > 5), 0, data['v_flag_3_trend'])

    # Dont flag if this would be the third straight year of negative abs, even if the three year trend indicates vac should rise
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & (data['yr'] == curryr) & ((data['abs'] - data['cons']) > data['three_yr_avg_abs_nonc']) & (data['abs'].shift(1) < 0) & (data['abs'].shift(6) < 0), 0, data['v_flag_3_trend'])
    if currqtr != 4:
        data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & (data['yr'] == curryr + 1) & ((data['abs'] - data['cons']) > data['three_yr_avg_abs_nonc']) & (data['abs'].shift(1) < 0) & (data['abs'].shift(2 + currqtr) < 0), 0, data['v_flag_3_trend'])
    elif currqtr == 4:
         data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & (data['yr'] == curryr + 1) & ((data['abs'] - data['cons']) > data['three_yr_avg_abs_nonc']) & (data['abs'].shift(1) < 0) & (data['abs'].shift(2) < 0), 0, data['v_flag_3_trend'])

    # Dont flag if employment change indicates big change from history, either in curryr or the prior year
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['abs'] - data['cons']) > data['three_yr_avg_abs_nonc']) & (data['emp_chg_z'] >= 1.5), 0, data['v_flag_3_trend'])
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['abs'] - data['cons']) < data['three_yr_avg_abs_nonc']) & (data['emp_chg_z'] <= -1.5), 0, data['v_flag_3_trend'])
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['abs'] - data['cons']) > data['three_yr_avg_abs_nonc']) & (data['emp_chg_z'].shift(1) >= 2) & (data['abs'] > data['abs'].shift(1)), 0, data['v_flag_3_trend'])
    data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] != 0) & ((data['abs'] - data['cons']) < data['three_yr_avg_abs_nonc']) & (data['emp_chg_z'].shift(1) <= -2) & (data['abs'] > data['abs'].shift(1)), 0, data['v_flag_3_trend'])
        
    data['v_flag_3_trend'] = np.where(data['v_flag_3_trend'] == 2, 1, data['v_flag_3_trend'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_3_trend', 'abs', 'rolsabs', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        if currqtr != 4:
            data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] == 1) & (((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1) < ((data['rolsabs'] - data['rolscon']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1)) & (((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1) > 0), 0, data['v_flag_3_trend'])
            data['v_flag_3_trend'] = np.where((data['v_flag_3_trend'] == 1) & (((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1) > ((data['rolsabs'] - data['rolscon']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1)) & (((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / (data['three_yr_avg_abs_nonc'] + 1) < 0), 0, data['v_flag_3_trend'])

    data['calc_v3trend'] = np.where((data['v_flag_3_trend'] == 1), abs(((data['abs'] - data['cons']) - data['three_yr_avg_abs_nonc']) / data['inv']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if there are three consecutive years of negative absorption in the submarket forecast
def v_cons_neg(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr == 4:
        shift_period = 1
    else:
        shift_period = currqtr + 1
    
    data['v_flag_cons_neg'] = np.where((data['forecast_tag'] != 0) & (data['cons_neg_abs'] == 1), 1, 0)

    # Dont flag if the sub is still below the 10 year vac average
    data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 1) & (data['vac'] < data['10_yr_vac'] + 0.005) & (data['vac'] < data['us_vac_level_avg']), 0, data['v_flag_cons_neg'])
    
    # Dont flag if the submarket is close to the min vac and vac chg is negligible
    data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 1) & (data['vac'] < data['min_vac'] + 0.01) & (data['min_vac'] < data['us_vac_level_avg'] / 1.5) & (data['vac_chg'] <= 0.002), 0, data['v_flag_cons_neg'])

    # Dont flag if this is the curryr forcast row and the implied abs is positive
    if currqtr != 4:
        data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 1) & (data['implied_abs'] > 0) & (data['yr'] == curryr), 0, data['v_flag_cons_neg'])
    
    # Dont flag if employment change indicates big change from history
    data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 1) & (data['emp_chg_z'] <= -1.5), 0, data['v_flag_cons_neg'])
    data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 1) & (data['yr'] == curryr) & (data['emp_chg_z'].shift(periods=shift_period) <= -2) & (data['vac_chg'] < data['vac_chg'].shift(periods=shift_period)), 0, data['v_flag_cons_neg'])
    data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 1) & (data['yr'] > curryr) & (data['emp_chg_z'].shift(1) <= -2) & (data['vac_chg'] < data['vac_chg'].shift(1)), 0, data['v_flag_cons_neg'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'v_flag_cons_neg', 'abs', 'rolsabs', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 7777) & (data['rolsabs'] < 0), 0, data['v_flag_cons_neg'])
        data['v_flag_cons_neg'] = np.where((data['v_flag_cons_neg'] == 7777), 1, data['v_flag_cons_neg'])
        data['v_flag_cons_neg'] = np.where((data['yr'] == curryr) & (data['v_flag_cons_neg'] == 1) & (data['abs'] + data['abs'].shift(periods=period) + data['abs'].shift(periods=period + 5) > data['rolsabs'] + data['rolsabs'].shift(periods=period) + data['rolsabs'].shift(periods=period + 5)), 0, data['v_flag_cons_neg'])
        data['v_flag_cons_neg'] = np.where((data['yr'] == curryr + 1) & (data['v_flag_cons_neg'] == 1) & (data['abs'] + data['abs'].shift(1) + data['abs'].shift(periods=period + 1) > data['rolsabs'] + data['rolsabs'].shift(1) + data['rolsabs'].shift(periods=period + 1)), 0, data['v_flag_cons_neg'])
        data['v_flag_cons_neg'] = np.where((data['yr'] > curryr + 1) & (data['v_flag_cons_neg'] == 1) & (data['abs'] + data['abs'].shift(1) + data['abs'].shift(2) > data['rolsabs'] + data['rolsabs'].shift(1) + data['rolsabs'].shift(2)), 0, data['v_flag_cons_neg'])

    
    data['calc_vconsneg'] = np.where((data['v_flag_cons_neg'] == 1), (data['abs'] + data['abs'].shift(periods=shift_period) + data['abs'].shift(periods=shift_period + 5)) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if the vacancy change has high variability across the submarkets within a metro for a particular year
def v_subv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['v_flag_subv'] = np.where((data['vac_chg_sub_var'] > 0), 1, 0)

    data['calc_vsubv'] = np.where((data['v_flag_subv'] == 1), data['vac_chg_sub_var'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if the vacancy change quartile is at the opposite end of the employment chg quartile
def v_emp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "apt" or sector_val == "ret":
        quart_use = 'emp_quart'
        chg_use = 'emp_chg'
    elif sector_val == "off":
        quart_use = 'off_emp_quart'
        chg_use = 'off_emp_chg'
    elif sector_val == "ind":
        quart_use = "ind_emp_quart"
        chg_use = 'ind_emp_chg'
    
    data['v_flag_emp'] = np.where((abs(data[quart_use] - data['vac_quart']) == 3) & (data['forecast_tag'] == 1), 1, 0)
    
    data['v_flag_emp'] = np.where((data['vac_quart'] == 1) & (data['forecast_tag'] == 2) & (data[chg_use] <= data['emp_5']), 1, data['v_flag_emp'])
    data['v_flag_emp'] = np.where((data['vac_quart'] == 4) & (data['forecast_tag'] == 2) & (data[chg_use] >= data['emp_95']), 1, data['v_flag_emp'])
    data['v_flag_emp'] = np.where((data['vac_quart'] == 1) & (data['forecast_tag'] == 2) & (data[chg_use] <= data['hist_emp_10']), 1, data['v_flag_emp'])
    data['v_flag_emp'] = np.where((data['vac_quart'] == 4) & (data['forecast_tag'] == 2) & (data[chg_use] >= data['hist_emp_90']), 1, data['v_flag_emp'])
    
    # Dont flag if the vac is ending up in a lower quartile than emp chg would indicate if nc is the cause
    if currqtr != 4:
        data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['forecast_tag'] == 1) & (data['implied_abs'] > 0) & (data['implied_cons'] > 0) & (data['implied_abs'] < data['implied_cons']) & (data['vac_quart'] > data[quart_use]), 0, data['v_flag_emp'])
        data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['forecast_tag'] == 2) & (data['abs'] > 0) & (data['cons'] > 0) & (data['abs'] < data['cons']) & (data['vac_quart'] > data[quart_use]), 0, data['v_flag_emp'])
    elif currqtr == 4:
        data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['abs'] > 0) & (data['cons'] > 0) & (data['abs'] < data['cons']) & (data['abs_cons_r'] >= 0.4) & (data['vac_quart'] > data[quart_use]), 0, data['v_flag_emp'])
    
    # Dont flag if the vac is ending up in a higher quartile than emp chg would indicate if absorption of unabsorbed nc from prior years or curryr trend periods is the cause
    data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & ((data['abs'] - data['extra_used_act'] - data['cons']) / data['inv'] <= 0.01) & (data['extra_used_act'] > 0) & (data['abs'] > 0) & (data['vac_quart'] < data[quart_use]), 0, data['v_flag_emp'])
    
    if currqtr != 4:
        data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['forecast_tag'] == 1) & (data['vac_quart'] == 1) & (data['vac_chg'] > -0.002) & (data['vac_chg'] < 0.002) & (data['curr_yr_trend_cons'] > 0), 0, data['v_flag_emp'])

    # Dont flag if the vac is far from its long term average and it is moving in that direction
    data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['vac'] - data['10_yr_vac'] < -0.02) & (data['vac_quart'] == 4) & (abs(data['vac_z']) < 2), 0, data['v_flag_emp'])
    data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['vac'] - data['10_yr_vac'] > 0.02) & (data['vac_quart'] == 1) & (abs(data['G_mrent_z']) < 2), 0, data['v_flag_emp'])
    
    # Dont flag if the vac is at a low level and the 10 year vac doesnt support it
    data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['vac'] < data['10_yr_vac']) & (data['vac'] < data['us_vac_level_avg'] / 2) & (data['vac_quart'] == 4) & (abs(data['vac_z']) < 2), 0, data['v_flag_emp'])

    # Dont flag if the emp_95 is too low and vac is falling and we are in the five outer years, since ecca's outer year forecast is typically too flat to impact our movements
    data['v_flag_emp'] = np.where((data['v_flag_emp'] == 1) & (data['yr'] >= curryr + 5) & (data['emp_95'] < 0.01) & (data['vac_quart'] == 1) & (abs(data['vac_z']) < 2), 0, data['v_flag_emp'])

    data['calc_vemp'] = np.where((data['v_flag_emp'] == 1), abs(data[quart_use] - data['vac_quart']), np.nan)
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['prev_occ'], axis=1)

    
    return data, calc_names

# Flag if there is a large change in the employment forecast from ROL, but not a commensurate reponse in vacancy chg
def v_emp_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "apt" or sector_val == "ret":
        quart_use = 'emp_quart'
        chg_use = 'emp_chg'
        rol_use = 'rol_emp_chg'
    elif sector_val == "off":
        quart_use = 'off_emp_quart'
        chg_use = 'off_emp_chg'
        rol_use = 'rol_off_emp_chg'
    elif sector_val == "ind":
        quart_use = "ind_emp_quart"
        chg_use = 'ind_emp_chg'
        rol_use = 'rol_ind_emp_chg'

    data['target_chg'] = (data[chg_use] - data[rol_use]) * -0.5
    data['v_flag_emp_rol'] = np.where((((data['forecast_tag'] == 2) & (data['yr'] <= curryr + 4)) | ((data['forecast_tag'] == 1) & (currqtr == 4))) & 
                                       (abs(data['target_chg']) > 0.005) & ((data['vac_chg'] - data['rolsvac_chg']) * data['target_chg'] < 0)
                                       , 1, 0)
    data['v_flag_emp_rol'] = np.where(((data['forecast_tag'] == 2) | ((data['forecast_tag'] == 1) & (currqtr == 4))) & 
                                       (abs(data['target_chg']) > 0.005) & ((data['vac_chg'] - data['rolsvac_chg']) - data['target_chg'] > 0.002) & (abs(data['vac_chg'] - data['rolsvac_chg']) < abs(data['target_chg']))
                                       , 1, data['v_flag_emp_rol'])
    
    data['calc_vemp_rol'] = np.where((data['v_flag_emp_rol'] == 1), abs((data['vac_chg'] - data['rolsvac_chg']) - data['target_chg']), np.nan)
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['target_chg'], axis=1)

    return data, calc_names

# Flag if market rent growth is less than 1% in a future forecast year or in the current forecast year if this is Q4 and the three year average doesnt support the low figure
def g_low(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_low'] = np.where(((data['forecast_tag'] == 2) | ((data['forecast_tag'] == 1) & (currqtr == 4))) &
                                     (data['G_mrent'] < 0.01) & 
                                     (data['G_mrent'] < data['three_yr_avg_G_mrent_nonc'] - 0.003) & (data['lim_hist'] > 3),
                                     1, 0)
    data['g_flag_low'] = np.where(((data['forecast_tag'] == 2) | ((data['forecast_tag'] == 1) & (currqtr == 4))) &
                                     (data['G_mrent'] < 0.01) & (data['lim_hist'] < 3),
                                     1, data['g_flag_low'])

    # Dont flag if employment change indicates large change from history, or if the prior year employment change is also a large outlier
    data['g_flag_low'] = np.where((data['g_flag_low'] == 1) & (data['emp_chg_z'] <= -1.5), 0, data['g_flag_low'])
    data['g_flag_low'] = np.where((data['g_flag_low'] == 1) & (data['emp_chg_z'].shift(1) <= -2) & (((data['G_mrent'] > data['G_mrent'].shift(1)) | (data['emp_chg_z'] < data['emp_chg_z'].shift(1)))), 0, data['g_flag_low'])
    
    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_low', 'G_mrent', 'grolsmre', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['g_flag_low'] = np.where((data['g_flag_low'] == 1) & (data['G_mrent'] > data['grolsmre']), 0, data['g_flag_low'])

    data['calc_glow'] = np.where((data['g_flag_low'] == 1), data['G_mrent'] * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if market rent growth is below the three year sub average and construction is at a significant portion of the total inventory
def g_nc(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:
        data['cons_prem_mod'] = np.where((data['avg_cons_perc_inv'].isnull() == False) & (data['forecast_tag'] == 2), 1 - ((((data['cons'] / data['inv']) - data['avg_cons_perc_inv']) / data['avg_cons_perc_inv']) * -1), np.nan)
        data['cons_prem_mod'] = np.where((data['avg_cons_perc_inv'].isnull() == True) & (data['forecast_tag'] == 2), 1 - ((((data['cons'] / data['inv']) - data['us_avg_cons_perc_inv']) / data['us_avg_cons_perc_inv']) * -1), data['cons_prem_mod'])
        data['cons_prem_mod'] = np.where((data['avg_cons_perc_inv'].isnull() == False) & (data['forecast_tag'] == 1), 1 - ((((data['implied_cons'] / data['inv']) - data['avg_cons_perc_inv']) / data['avg_cons_perc_inv']) * -1), data['cons_prem_mod'])
        data['cons_prem_mod'] = np.where((data['avg_cons_perc_inv'].isnull() == True) & (data['forecast_tag'] == 1), 1 - ((((data['implied_cons'] / data['inv']) - data['us_avg_cons_perc_inv']) / data['us_avg_cons_perc_inv']) * -1), data['cons_prem_mod'])
        data['cons_prem_mod'] = np.where(data['cons_prem_mod'] > 1, 1, data['cons_prem_mod'])
    
        data['g_flag_nc'] = np.where((data['forecast_tag'] == 1) & 
                                    (round(data['implied_G_mrent'],3) < round((data['three_yr_avg_G_mrent_nonc'] * ((4 - currqtr) / 4)) + (data['cons_prem'] * data['cons_prem_mod']),3)) & 
                                    (data['implied_cons'] / data['inv'] >= 0.015), 
                                    1, 0)
        data['g_flag_nc'] = np.where((data['forecast_tag'] == 2) & 
                                    (round(data['G_mrent'],3) < round(data['three_yr_avg_G_mrent_nonc'] + (data['cons_prem'] * data['cons_prem_mod']),3)) & 
                                    (data['cons'] / data['inv'] >= 0.015), 
                                    1, data['g_flag_nc'])

    elif currqtr == 4:
        data['cons_prem_mod'] = np.where((data['avg_cons_perc_inv'].isnull() == False), 1 - ((((data['cons'] / data['inv']) - data['avg_cons_perc_inv']) / data['avg_cons_perc_inv']) * -1), np.nan)
        data['cons_prem_mod'] = np.where((data['avg_cons_perc_inv'].isnull() == True), 1 - ((((data['cons'] / data['inv']) - data['us_avg_cons_perc_inv']) / data['us_avg_cons_perc_inv']) * -1), data['cons_prem_mod'])
        data['cons_prem_mod'] = np.where(data['cons_prem_mod'] > 1, 1, data['cons_prem_mod'])
        
        data['g_flag_nc'] = np.where((data['forecast_tag'] != 0) &
                                     (round(data['G_mrent'],3) < round(data['three_yr_avg_G_mrent_nonc'] + (data['cons_prem'] * data['cons_prem_mod']),3)) &
                                     (data['cons'] / data['inv'] >= 0.015),
                                     1, 0)

    # Dont flag if employment change indicates large departure from history, so long as the rent growth is in the first or second quartile
    if currqtr == 4:
        data['g_flag_nc'] = np.where((data['yr'] > curryr) & (data['g_flag_nc'] == 1) & (data['emp_chg_z'] < -2) & (((data['G_mrent_quart'] <= 2) | (data['cons'] / data['inv'] < 0.03))), 0, data['g_flag_nc'])
        data['g_flag_nc'] = np.where((data['yr'] > curryr) & (data['g_flag_nc'] == 1) & (data['emp_chg_z'].shift(1) < -2) & (((data['G_mrent_quart'] <= 2) | (data['cons'] / data['inv'] < 0.03))), 0, data['g_flag_nc'])
    elif currqtr != 4:
        data['g_flag_nc'] = np.where((data['yr'] == curryr) & (data['g_flag_nc'] == 1) & (data['emp_chg_z'] < -2) & (((data['G_mrent_quart'] <= 2) | (data['implied_cons'] / data['inv'] < 0.03))), 0, data['g_flag_nc'])
        data['g_flag_nc'] = np.where((data['yr'] == curryr) & (data['g_flag_nc'] == 1) & (data['emp_chg_z'].shift(periods=currqtr+1) < -2) & (((data['G_mrent_quart'] <= 2) | (data['implied_cons'] / data['inv'] < 0.03))), 0, data['g_flag_nc'])
   
    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_nc', 'G_mrent', 'grolsmre', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['g_flag_nc'] = np.where((data['forecast_tag'] == 2) & (data['g_flag_nc'] == 1) & (data['G_mrent'] > data['grolsmre']) & (data['cons'] <= data['rolscon']), 0, data['g_flag_nc'])

    if currqtr != 4:
        data['calc_gnc'] = np.where((data['forecast_tag'] == 2) & (data['g_flag_nc'] == 1), (data['G_mrent'] - (data['three_yr_avg_G_mrent_nonc'] + (data['cons_prem'] * data['cons_prem_mod']))) * -1, np.nan)
        data['calc_gnc'] = np.where((data['forecast_tag'] == 1) & (data['g_flag_nc'] == 1), (data['implied_G_mrent'] - (data['three_yr_avg_G_mrent_nonc'] + (data['cons_prem'] * data['cons_prem_mod']))) * -1, data['calc_gnc'])
        calc_names.append(list(data.columns)[-1])
    elif currqtr == 4:
        data['calc_gnc'] = np.where((data['g_flag_nc'] == 1), data['G_mrent'] - (data['three_yr_avg_G_mrent_nonc'] + (data['cons_prem'] * data['cons_prem_mod'])), np.nan)

    return data, calc_names


# Flag if a market rent growth forecast is greater than a z-score of 1.5 for the submarket
def g_z(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_z'] = np.where((data['forecast_tag'] != 0) & 
                                   ((data['G_mrent_z'] > 1.5) | (data['G_mrent_z'] < -1.5)) & 
                                   (data['G_mrent_z'] != np.inf) & (data['G_mrent_z'] != -np.inf),
                                   1, 0)

    # Dont flag if the submarket has a limited trend history to draw z score from and market rent change is within reasonable bound
    data['us_avg_G_mrent_chg'] = data[data['forecast_tag'] != 0].groupby('subsector')['three_yr_avg_G_mrent_nonc'].transform('mean')
    data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & ((data['G_mrent_quart'] == 2) | (data['G_mrent_quart'] == 3)), 0, data['g_flag_z'])
    
    if currqtr == 4:
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & (data['avg_G_mrent_chg'] < data['us_avg_G_mrent_chg']) & (data['G_mrent'] > data['us_avg_G_mrent_chg'] - 0.02) & (data['G_mrent_quart'] == 4), 0, data['g_flag_z'])
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & (data['avg_G_mrent_chg'] > data['us_avg_G_mrent_chg']) & (data['G_mrent'] < data['us_avg_G_mrent_chg'] + 0.02) & (data['G_mrent_quart'] == 1), 0, data['g_flag_z'])
    elif currqtr != 4:
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & (data['forecast_tag'] == 1) & (data['avg_G_mrent_chg'] < data['us_avg_G_mrent_chg']) & (data['implied_G_mrent'] > data['us_avg_G_mrent_chg'] - 0.02) & (data['G_mrent_quart'] == 4), 0, data['g_flag_z'])
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & (data['forecast_tag'] == 1) & (data['avg_G_mrent_chg'] > data['us_avg_G_mrent_chg']) & (data['implied_G_mrent'] < data['us_avg_G_mrent_chg'] + 0.02) & (data['G_mrent_quart'] == 1), 0, data['g_flag_z'])
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & (data['forecast_tag'] == 2) & (data['avg_G_mrent_chg'] < data['us_avg_G_mrent_chg']) & (data['G_mrent'] > data['us_avg_G_mrent_chg'] - 0.02) & (data['G_mrent_quart'] == 4), 0, data['g_flag_z'])
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['lim_hist'] <= 5) & (data['forecast_tag'] == 2) & (data['avg_G_mrent_chg'] > data['us_avg_G_mrent_chg']) & (data['G_mrent'] < data['us_avg_G_mrent_chg'] + 0.02) & (data['G_mrent_quart'] == 1), 0, data['g_flag_z'])

    # Dont flag if the rent change is in line with the current year trend rent chg (or last years trend rent if this is Q4)
    if currqtr != 4:
        data['curr_trend_G_mrent'] = np.where((data['yr'] == curryr) & (data['qtr'] == 5), data['G_mrent'], np.nan)
    elif currqtr == 4:
        data['curr_trend_G_mrent'] = np.where((data['yr'] == curryr - 1) & (data['qtr'] == 5), data['G_mrent'], np.nan)
    data['curr_trend_G_mrent'] = data.groupby('identity')['curr_trend_G_mrent'].ffill()
    if currqtr != 4:
        data['implied_check'] = np.where(data['implied_G_mrent'] <= data['total_trend_G_mrent'] / (4 - currqtr), 1, 0)
        data['implied_check'] = np.where((data['yr'] > curryr), np.nan, data['implied_check'])
        data['implied_check'] = data.groupby('identity')['implied_check'].ffill()
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['forecast_tag'] == 2) & (abs(data['G_mrent'] - data['curr_trend_G_mrent']) <= 0.005) & (data['G_mrent'] * data['curr_trend_G_mrent'] >= 0) & (data['implied_check'] == 1), 0, data['g_flag_z'])
    elif currqtr == 4:
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (abs(data['G_mrent'] - data['curr_trend_G_mrent']) <= 0.005) & (data['G_mrent'] * data['curr_trend_G_mrent'] >= 0), 0, data['g_flag_z'])

    data = data.drop(['us_avg_G_mrent_chg'], axis=1)

    # Dont flag if employment change indicates large change from history, or if the prior year shows large negative change from history and the curr year forecast is an improvement
    data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['G_mrent'] > data['avg_G_mrent_chg']) & (data['emp_chg_z'] >= 1.5), 999999999, data['g_flag_z'])
    data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['G_mrent'] < data['avg_G_mrent_chg']) & (data['emp_chg_z'] <= -1.5), 999999999, data['g_flag_z'])
    data['g_flag_z'] = np.where((((data['yr'] > curryr)) | ((currqtr == 4))) & (data['g_flag_z'] == 1) & (data['G_mrent'] < data['avg_G_mrent_chg']) & (data['emp_chg_z'].shift(1) <= -2) & (data['G_mrent'] > data['G_mrent'].shift(1)), 999999999, data['g_flag_z'])
    data['g_flag_z'] = np.where((data['yr'] == curryr) & (currqtr != 4) & (data['g_flag_z'] == 1) & (data['G_mrent'] < data['avg_G_mrent_chg']) & (data['emp_chg_z'].shift(currqtr+1) <= -2) & (data['G_mrent'] > data['G_mrent'].shift(currqtr+1)), 999999999, data['g_flag_z'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging.
    # Wider failsafe for large increases, as theoretically employment change has less of an impact on positive rent growth than it does on negative rent growth ie: when there is outlier negative emp chg, the rents could really tank and have crazy outlier z-scores. 
    data['g_flag_z'] = np.where((data['g_flag_z'] == 999999999) & (data['forecast_tag'] != 0) & 
                                   (((data['G_mrent_z'] > 2.5) | (data['G_mrent_z'] < -5))) & (data['G_mrent_quart'] > 2) &
                                   (data['G_mrent_z'] != np.inf) & (data['G_mrent_z'] != -np.inf),
                                   1, data['g_flag_z'])

    data['g_flag_z'] = np.where((data['g_flag_z'] == 999999999), 0, data['g_flag_z'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_z', 'G_mrent', 'grolsmre', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['G_mrent_z'] < (data['grolsmre'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg']) & (data['G_mrent_z'] > 0), 0, data['g_flag_z'])
        data['g_flag_z'] = np.where((data['g_flag_z'] == 1) & (data['G_mrent_z'] > (data['grolsmre'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg']) & (data['G_mrent_z'] < 0), 0, data['g_flag_z'])
        
    data['calc_gz'] = np.where((data['g_flag_z'] == 1), abs(data['G_mrent_z']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names


# Flag if there is low market rent growth variability in the forecast of a sub
def g_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr == 4:
        data['g_flag_lowv'] = np.where((data['forecast_tag'] == 1) & 
                                        (data['f_var_G_mrent'] < data['f_5_var_G_mrent']) & (data['f_var_G_mrent'].shift(1).isnull() == True),
                                         1, 0)
    elif currqtr != 4:
        data['g_flag_lowv'] = np.where((data['yr'] == curryr + 1) & 
                                    (data['f_var_G_mrent'] < data['f_5_var_G_mrent']),
                                    1, 0)                                   
    
    data['calc_glowv'] = np.where((data['g_flag_lowv'] == 1), (data['f_var_G_mrent'] - data['f_5_var_G_mrent']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])
    
    return data, calc_names


# Flag if there is high market rent growth variability in the forecast of a sub
def g_highv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr == 4:
        data['g_flag_highv'] = np.where((data['forecast_tag'] == 1) & 
                                         (data['f_var_G_mrent'] > data['f_95_var_G_mrent']),
                                         1, 0)
    elif currqtr != 4:
        data['g_flag_highv'] = np.where((data['yr'] == curryr + 1) & 
                                    (data['f_var_G_mrent'] > data['f_95_var_G_mrent']) & (data['f_var_G_mrent'].shift(1).isnull() == True),
                                    1, 0)
                                    
    data['calc_ghighv'] = np.where((data['g_flag_highv'] == 1), data['f_var_G_mrent'] - data['f_95_var_G_mrent'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if a market rent growth forecast is a new high for the submarket
def g_max(data, curryr, currqtr, sector_val, calc_names, use_rol_close):
    
    data['g_flag_max'] = np.where((data['forecast_tag'] != 0) & 
                                      (round(data['G_mrent'], 3) > round(data['max_G_mrent'], 3)),
                                      1, 0)

    # Dont flag if the value is close to the most recent trend rent chg
    data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['G_mrent'] < data['curr_trend_G_mrent'] + 0.005) & ((data['implied_check'] == 1) | (data['forecast_tag'] == 2)), 0, data['g_flag_max'])

    # Dont flag if this is not Q4, and the implied chg is less than the typical historical implied growth and the quartile is not 1 (which is measured on implied growth in a non q4 quarter)
    if currqtr != 4:
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['forecast_tag'] == 1) & (data['implied_G_mrent'] < data['hist_implied_G_mrent']) & (data['G_mrent_quart'] > 1), 0, data['g_flag_max'])
    
    # Dont flag if the sub has a limited trend history and the market rent growth is not in the first quartile nationally
    if currqtr == 4:
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['lim_hist'] <= 5) & (data['G_mrent_quart'] != 1) & (data['G_mrent'] < data['max_G_mrent'] + 0.02), 0, data['g_flag_max'])
    elif currqtr != 4:
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['lim_hist'] <= 5) & (data['G_mrent_quart'] != 1) & (data['implied_check'] == 1), 0, data['g_flag_max'])

    # Dont flag if there is very limited trend history and the rent growth is in line with the most recent trend value
    if currqtr != 4:
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['lim_hist'] < 3) & (data['forecast_tag'] == 1) & (data['implied_check'] == 1), 0, data['g_flag_max'])
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['lim_hist'] < 3) & (data['forecast_tag'] == 2) & (data['G_mrent'] - data['curr_trend_G_mrent'] <= 0.005) & (data['G_mrent'] * data['curr_trend_G_mrent'] >= 0) & (data['implied_check'] == 1), 0, data['g_flag_max'])
    elif currqtr == 4:
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['lim_hist'] < 3) & (data['G_mrent'] - data['curr_trend_G_mrent'] <= 0.005) & (data['G_mrent'] * data['curr_trend_G_mrent'] >= 0), 0, data['g_flag_max'])

    # Dont flag if employment change indicates significant change from history
    data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['emp_chg_z'] > 2), 999999999, data['g_flag_max'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['g_flag_max'] = np.where((data['g_flag_max'] == 999999999) & (data['forecast_tag'] != 0) & 
                                      (abs((data['G_mrent'] - data['max_G_mrent']) / data['max_G_mrent']) > 0.5) & (data['G_mrent'] > data['max_G_mrent']),
                                      1, data['g_flag_max'])

    data['g_flag_max'] = np.where((data['g_flag_max'] == 999999999), 0, data['g_flag_max'])
    
    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_max', 'G_mrent', 'grolsmre', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['g_flag_max'] = np.where((data['g_flag_max'] == 7777) & (data['grolsmre'] >= data['max_G_mrent']), 0, data['g_flag_max'])
        data['g_flag_max'] = np.where((data['g_flag_max'] == 7777), 1, data['g_flag_max'])
        data['g_flag_max'] = np.where((data['g_flag_max'] == 1) & (data['G_mrent'] < data['grolsmre']), 0, data['g_flag_max'])
     

    data['calc_gmax'] = np.where((data['g_flag_max'] == 1), data['G_mrent'] - data['max_G_mrent'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if the market rent growth forecast is well off the three year trend
def g_3trend(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_3_trend'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['yr'] == curryr + 1)) & 
                                         ((data['G_mrent'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001) > 0.25),
                                         1, 0)

    data['g_flag_3_trend'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) | (data['yr'] == curryr + 1)) &  
                                         ((data['G_mrent'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001) < -0.25),
                                         2, data['g_flag_3_trend'])

    # Handle cases that are close to the three year avg, but due to low magnitudes, get flagged when using percentage to evaluate distance
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (abs(data['G_mrent']) <= 0.015) & (abs(round(data['G_mrent'] - data['three_yr_avg_G_mrent_nonc'],3)) <= 0.003), 0, data['g_flag_3_trend'])
    
    # Dont flag if the sub has less than 3 years of history and the rent change is reasonable
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['lim_hist'] <= 3) & ((data['G_mrent_quart'] == 2) | (data['G_mrent_quart'] == 3)), 0, data['g_flag_3_trend'])
    
    # Dont flag if either above 3 year avg but in bottom quartile, or below 3 year avg but in upper quartile
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] < data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent_quart'] == 1), 0, data['g_flag_3_trend'])
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent_quart'] == 4), 0, data['g_flag_3_trend'])
    
    # Dont flag if this would be the third straight year of below average rent growth, even if the three year trend indicates rent should fall
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['yr'] == curryr)  & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent_z'] <= 1) & (data.shift(1)['G_mrent'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent'].shift(6) < data['avg_G_mrent_chg_nonc']), 0, data['g_flag_3_trend'])
    if currqtr != 4:
        data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['yr'] == curryr + 1)  & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent_z'] <= 1) & (data.shift(1)['G_mrent'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent'].shift(2 + currqtr) < data['avg_G_mrent_chg_nonc']), 0, data['g_flag_3_trend'])
    elif currqtr == 4:
        data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['yr'] == curryr + 1)  & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent_z'] <= 1) & (data.shift(1)['G_mrent'] < data['avg_G_mrent_chg_nonc']) & (data['G_mrent'].shift(2) < data['avg_G_mrent_chg_nonc']), 0, data['g_flag_3_trend'])
    
    # Dont flag if the forecast is above the three year trend and the difference can be attributed to new construction premium
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent'] - data['three_yr_avg_G_mrent_nonc'] <= (data['cons_prem'] * data['cons_prem_mod'])) & (data['cons'] / data['inv'] >= 0.015), 0, data['g_flag_3_trend'])

    # Dont flag if this is Q3 and the rent growth is in line with what weve observed in the recent trend year
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] == 1) & (data['G_mrent'] < data['curr_trend_G_mrent'] + 0.005) & (data['implied_check'] == 1), 0, data['g_flag_3_trend'])
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] == 2) & (data['G_mrent'] > data['curr_trend_G_mrent'] - 0.005) & (data['implied_check'] == 1), 0, data['g_flag_3_trend'])
    
    # Dont flag if employment change indicates big change from history, either in curryr or the prior year
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent'] - data['three_yr_avg_G_mrent_nonc'] < data['emp_chg_z'] / 150) & (data['emp_chg_z'] >= 1), 0, data['g_flag_3_trend'])
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] < data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent'] - data['three_yr_avg_G_mrent_nonc'] > data['emp_chg_z'] / 150) & (data['emp_chg_z'] <= -1), 0, data['g_flag_3_trend'])
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] > data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent'] - data['three_yr_avg_G_mrent_nonc'] < data['emp_chg_z'].shift(1) / 150) & (data['emp_chg_z'].shift(1) >= 2) & (data['G_mrent'] > data['G_mrent'].shift(1)), 0, data['g_flag_3_trend'])
    data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] != 0) & (data['G_mrent'] < data['three_yr_avg_G_mrent_nonc']) & (data['G_mrent'] - data['three_yr_avg_G_mrent_nonc'] < data['emp_chg_z'].shift(1) / 150)  & (data['emp_chg_z'].shift(1) <= -2) & (data['G_mrent'] > data['G_mrent'].shift(1)), 0, data['g_flag_3_trend'])
    
    
    data['g_flag_3_trend'] = np.where(data['g_flag_3_trend'] == 2, 1, data['g_flag_3_trend'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_3_trend', 'G_mrent', 'grolsmre', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        if currqtr != 4:
            data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] == 1) & ((data['G_mrent'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001) < (data['grolsmre'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001)) & (data['G_mrent'] > 0), 0, data['g_flag_3_trend'])
            data['g_flag_3_trend'] = np.where((data['g_flag_3_trend'] == 1) & ((data['G_mrent'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001) > (data['grolsmre'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001)) & (data['G_mrent'] < 0), 0, data['g_flag_3_trend'])

    
    data['calc_g3trend'] = np.where((data['g_flag_3_trend'] == 1), abs((data['G_mrent'] - data['three_yr_avg_G_mrent_nonc']) / (data['three_yr_avg_G_mrent_nonc'] + 0.000001)), np.nan)
    calc_names.append(list(data.columns)[-1])

    if currqtr != 4:
        data = data.drop(['implied_check'], axis=1)
    data = data.drop(['curr_trend_G_mrent'], axis=1)

    return data, calc_names

 # Flag if market rent growth forecast in the curr year forecast row results in a change from ROL market rent growth and the change increases the implied level
def g_improls(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:
        
        data['g_flag_improls'] = np.where((data['forecast_tag'] == 1) &
            (abs((data['implied_G_mrent'] - data['hist_implied_G_mrent'])) > abs((data['implied_using_grolsmre'] - data['hist_implied_G_mrent']))),
            1, 0)
        
        # Dont flag if the difference can be attributed to new construction premium
        data['g_flag_improls'] = np.where((data['g_flag_improls'] != 0) & (data['implied_G_mrent'] - data['implied_using_grolsmre'] > 0) & (data['implied_G_mrent'] - data['implied_using_grolsmre'] <= (data['cons_prem'] * data['cons_prem_mod'])) & ((data['implied_cons'] - data['rolscon']) / data['inv'] >= 0.015), 0, data['g_flag_improls'])
        
        # Dont flag if using rol would move in the opposite directiion of hist implied chg, even if that would minimize the difference to hist implied chg
        data['g_flag_improls'] = np.where((data['g_flag_improls'] != 0) & (data['implied_G_mrent'] * data['hist_implied_G_mrent'] > 0) & (data['implied_using_grolsmre'] * data['hist_implied_G_mrent'] < 0) & (abs((data['implied_G_mrent'] - data['hist_implied_G_mrent'])) - abs((data['implied_using_grolsmre'] - data['hist_implied_G_mrent'])) < 0.01), 0, data['g_flag_improls'])

        # Dont flag if employment change indicates large difference from prior quarter employment change
        data['g_flag_improls'] = np.where((data['g_flag_improls'] == 1) & ((data['implied_G_mrent'] - data['hist_implied_G_mrent']) > (data['implied_using_grolsmre'] - data['hist_implied_G_mrent'])) & ((data['implied_G_mrent'] - data['hist_implied_G_mrent']) - (data['implied_using_grolsmre'] - data['hist_implied_G_mrent']) <= data['emp_chg_diff'] * 3), 0, data['g_flag_improls'])
        data['g_flag_improls'] = np.where((data['g_flag_improls'] == 1) & ((data['implied_G_mrent'] - data['hist_implied_G_mrent']) < (data['implied_using_grolsmre'] - data['hist_implied_G_mrent'])) & ((data['implied_G_mrent'] - data['hist_implied_G_mrent']) - (data['implied_using_grolsmre'] - data['hist_implied_G_mrent']) >= data['emp_chg_diff'] * 3), 0, data['g_flag_improls'])
        
        data['calc_gimprols'] = np.where((data['g_flag_improls'] == 1), abs((data['implied_G_mrent'] - data['hist_implied_G_mrent'])) - abs((data['implied_using_grolsmre'] - data['hist_implied_G_mrent'])), np.nan)
        data['calc_gimprols'] = np.where((data['calc_gimprols'].isnull() == False), abs(data['calc_gimprols']), data['calc_gimprols'])
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['g_flag_improls'] = 0
        data['calc_gimprols'] = 0
        calc_names.append(list(data.columns)[-1])    

    return data, calc_names

# Flag if market rent growth forecast in the curr year forecast row is leaving a large amount of implied market rent growth
def g_imp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:
        data['g_flag_imp'] = np.where((data['forecast_tag'] == 1) & 
            ((data['implied_G_mrent'] - data['hist_implied_G_mrent']) / (data['hist_implied_G_mrent']+0.000001) > 0.75),
            1, 0)

        data['g_flag_imp'] = np.where((data['forecast_tag'] == 1) & 
            ((data['implied_G_mrent'] - data['hist_implied_G_mrent']) / (data['hist_implied_G_mrent']+0.000001) < -0.75),
            2, data['g_flag_imp'])

        # Because percentage change doesnt work so well when the numbers are really small, add additional qualification for spread instead of straight percentage change
        data['g_flag_imp'] = np.where((data['forecast_tag'] == 1) & 
            (abs(data['implied_G_mrent'] - data['hist_implied_G_mrent']) < 0.003) & (round(data['implied_G_mrent'],3) * round(data['hist_implied_G_mrent'],3) >= 0) & (abs(data['implied_G_mrent']) < 0.02),
            0, data['g_flag_imp'])

        # Dont flag if the difference can be attributed to new construction premium
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] > 0) & (data['implied_G_mrent'] * data['hist_implied_G_mrent'] >= 0) & (data['implied_G_mrent'] <= data['hist_implied_G_mrent'] + (data['cons_prem'] * data['cons_prem_mod'])) & (data['implied_cons'] / data['inv'] >= 0.015), 0, data['g_flag_imp'])
        
        # Dont flag if implied chg is above hist implied chg but the sub is in the bottom quartile, or if implied chg is below hist implied chg but the sub is in the upper quartile
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] <= 0.01) & (data['implied_G_mrent'] > data['hist_implied_G_mrent']) & (data['G_mrent_quart'] == 4), 0, data['g_flag_imp'])
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] >= -0.01) & (data['implied_G_mrent'] < data['hist_implied_G_mrent']) & (data['G_mrent_quart'] == 1), 0, data['g_flag_imp'])

        # Dont flag if the implied chg is in line with trend chg
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] > 0) & (data['implied_G_mrent'] > data['hist_implied_G_mrent']) & (data['implied_G_mrent'] * data['total_trend_G_mrent'] > 0) & (data['implied_G_mrent'] <= ((data['total_trend_G_mrent'] / currqtr) / 1.5) * (4 - currqtr)), 0, data['g_flag_imp'])
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] < 0)  & (data['implied_G_mrent'] < data['hist_implied_G_mrent']) & (data['implied_G_mrent'] * data['total_trend_G_mrent'] > 0) & (data['implied_G_mrent'] >= ((data['total_trend_G_mrent'] / currqtr) / 1.5) * (4 - currqtr)), 0, data['g_flag_imp'])

        # Dont flag if employment change indicates large change from history
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] > data['hist_implied_G_mrent']) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] <= data['emp_chg_z'] / 150) & (data['emp_chg_z'] >= 1), 0, data['g_flag_imp'])
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['implied_G_mrent'] < data['hist_implied_G_mrent']) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] >= data['emp_chg_z'] / 150) & (data['emp_chg_z'] <= -1), 0, data['g_flag_imp'])
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['emp_chg_z'] >= 1) & (data['implied_G_mrent'] > 0) & (data['implied_G_mrent'] > data['hist_implied_G_mrent']) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] <= 0.02 + ((data['G_mrent_quart'] * 0.25) / 100)) & (data['G_mrent_quart'] > 1), 0, data['g_flag_imp'])
        data['g_flag_imp'] = np.where((data['g_flag_imp'] != 0) & (data['emp_chg_z'] <= -1) & (data['implied_G_mrent'] < 0) & (data['implied_G_mrent'] < data['hist_implied_G_mrent']) & (data['implied_G_mrent'] - data['hist_implied_G_mrent'] >= -0.02 -  + ((1.25-(data['G_mrent_quart'] * 0.25)) / 100)) & (data['G_mrent_quart'] < 4), 0, data['g_flag_imp'])

        data['g_flag_imp'] = np.where(data['g_flag_imp'] == 2, 1, data['g_flag_imp'])

        data['calc_gimp'] = np.where((data['g_flag_imp'] == 1), abs((data['implied_G_mrent'] - data['hist_implied_G_mrent']) / (data['hist_implied_G_mrent']+0.000001)), np.nan)
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['g_flag_imp'] = 0
        data['calc_gimp'] = 0
        calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if market rent growth forecast in all non curr year forecast years is different than ROL
def g_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_rol'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                     (data['forecast_tag'] == 2)) & 
                                     ((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001) > 0.25),
                                     1,0)
    data['g_flag_rol'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                     (data['forecast_tag'] == 2)) & 
                                     ((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001) < -0.25),
                                     2, data['g_flag_rol'])

    # Because percentage change doesnt work so well when the numbers are really small, add additional qualification for spread instead of straight percentage change
    data['g_flag_rol'] = np.where((data['g_flag_rol'] != 0) & 
            (abs(data['G_mrent'] - data['grolsmre']) < 0.003) & (round(data['G_mrent'],3) * round(data['grolsmre'],3) >= 0) & (abs(data['G_mrent']) < 0.02),
            0, data['g_flag_rol'])
    
    # If this is Q4, do not flag for change from ROL if there was a significantly different fourth quarter trend finish
    if currqtr == 4:
        data['g_flag_rol'] = np.where((data['forecast_tag'] == 1) & (data['g_flag_rol'] != 0) &
            ((((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001)) - data['prev_G_mrent']) / data['prev_G_mrent'] < 0.10) & 
            ((((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001)) - data['prev_G_mrent']) / data['prev_G_mrent'] > 0) &
            ((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001) > 0),
            0, data['g_flag_rol'])
        
        data['g_flag_rol'] = np.where((data['forecast_tag'] == 1) & (data['g_flag_rol'] != 0) &
            ((((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001)) - data['prev_G_mrent']) / data['prev_G_mrent'] > -0.10) & 
            ((((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001)) - data['prev_G_mrent']) / data['prev_G_mrent'] < 0) &
            ((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001) < 0),
            0, data['g_flag_rol'])

    # Dont flag for difference to rol if there is a signicant change in construction and the change to market rent growth is not too large 
    data['g_flag_rol'] = np.where((data['forecast_tag'] != 0) & 
                                      (data['g_flag_rol'] != 0) &
                                      ((data['cons'] - data['rolscon']) / data['inv'] >= 0.015) &
                                      (data['G_mrent'] > data['grolsmre']) & (data['G_mrent'] -  data['grolsmre'] <= (data['cons_prem'] * data['cons_prem_mod'])), 
                                      0, data['g_flag_rol'])
    data['g_flag_rol'] = np.where((data['forecast_tag'] != 0) & 
                                      (data['g_flag_rol'] != 0) &
                                      ((data['cons'] - data['rolscon']) / data['inv'] <= -0.015) &
                                      (data['G_mrent'] < data['grolsmre']) & (data['G_mrent'] - data['grolsmre'] >= (data['cons_prem'] * data['cons_prem_mod'])), 
                                      0, data['g_flag_rol'])

    # Dont flag if employment change indicates conditions are different than they were last quarter
    data['g_flag_rol'] = np.where((data['g_flag_rol'] != 0) & (data['G_mrent'] > data['grolsmre']) & (data['G_mrent'] - data['grolsmre'] <= data['emp_chg_diff'] * 3), 0, data['g_flag_rol'])
    data['g_flag_rol'] = np.where((data['g_flag_rol'] != 0) & (data['G_mrent'] < data['grolsmre']) & (data['G_mrent'] - data['grolsmre'] >= data['emp_chg_diff'] * 3), 0, data['g_flag_rol'])

    data['g_flag_rol'] = np.where(data['g_flag_rol'] == 2, 1, data['g_flag_rol'])

    data['calc_grol'] = np.where((data['g_flag_rol'] == 1), abs((data['G_mrent'] - data['grolsmre']) / (data['grolsmre']+0.000001)), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if consecutive years of market rent growth in the forecast are significantly different than one another
def g_yrdiff(data, curryr, currqtr, sector_val, calc_names, use_rol_close):
   
    data['g_flag_yrdiff'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                     (data['forecast_tag'] == 2)) & 
                                     (abs((data['G_mrent'] - data['prev_G_mrent']) / (data['prev_G_mrent'] + 0.000001)) > 0.3),
                                     1, 0)

    # Because percentage change doesnt work so well when the numbers are really small, add additional qualification for spread instead of straight percentage change
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] != 0) & 
            (abs(round(data['G_mrent'],3) - round(data['prev_G_mrent'],3)) <= 0.005) & (round(data['G_mrent'],3) * round(data['prev_G_mrent'],3) >= 0) & (abs(data['G_mrent']) < 0.03),
            0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] != 0) & 
            (abs(round(data['G_mrent'],3) - round(data['prev_G_mrent'],3)) <= 0.02) & (round(data['G_mrent'],3) * round(data['prev_G_mrent'],3) < 0) & (abs(data['G_mrent']) < 0.01),
            0, data['g_flag_yrdiff'])

    # Dont flag if there is a significant difference in construction between the two years
    data['g_flag_yrdiff'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         ((data['cons'] - data['prev_cons']) / data['inv'] >= 0.01) &
                                         (data['cons'] > data['prev_cons']) & (data['G_mrent'] > data['prev_G_mrent']) & (data['G_mrent'] - data['prev_G_mrent'] <= (data['cons_prem'] * data['cons_prem_mod'])),
                                         0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         ((data['cons'] - data['prev_cons']) / data['inv'] <= -0.01) &
                                         (data['cons'] < data['prev_cons']) & (data['G_mrent'] < data['prev_G_mrent']) & (data['G_mrent'] - data['prev_G_mrent'] >= (data['cons_prem'] * data['cons_prem_mod'])),
                                         0, data['g_flag_yrdiff'])
    
    # Dont flag if the prior year's change was an outlier compared to the history at the sub, and this year's change is returning to a more normal submarket movement
    # Note: Calculate the G_mrent_z directly here, since the 2021 value stored as that var will be based on implied chg, and we want the full change for this check
    data['full_yr_z'] = np.where(data['forecast_tag'] == 1, (data['G_mrent'] - data['avg_G_mrent_chg']) / data['std_dev_G_mrent_chg'], data['G_mrent_z'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (abs(data['G_mrent_z']) < 1) & (abs(data['full_yr_z'].shift(1)) > 1.5) & (data['G_mrent_z'] * data['full_yr_z'].shift(1) >= 0), 0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (abs(data['G_mrent_z']) < 1) & (abs(data['full_yr_z'].shift(1)) > 1.5) & (abs(data['G_mrent'] - data['prev_G_mrent']) <= 0.02), 0, data['g_flag_yrdiff'])

    # Dont flag if the distance between the z-scores for the two years is reasonably close, and the raw difference is too
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (abs(data['G_mrent_z'] - data['full_yr_z'].shift(1)) <= 0.4) & (abs(data['G_mrent'] - data['prev_G_mrent']) <= 0.01), 0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (data['G_mrent_z'] < 1) & (data['full_yr_z'].shift(1) < 1) & (data['G_mrent_z'] * data['full_yr_z'].shift(1) > 0) & (abs(data['G_mrent'] - data['prev_G_mrent']) <= 0.02), 0, data['g_flag_yrdiff'])
    
    # Dont flag if the prior year was worse than the historical average and the current year is bouncing back to the typical average growth
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (round(data['G_mrent'],3) <= round(data['five_yr_avg_G_mrent'],3) + 0.01) & (data['G_mrent'] > data['prev_G_mrent']) & (data['full_yr_z'].shift(1) < 0), 0, data['g_flag_yrdiff'])

    data = data.drop(['full_yr_z'], axis=1)
    
    # Dont flag if employment change is very different between the two years (with a lower tolerance in years beyond curryr + 1, since ECCA forecast for those years will be pretty flat and not that relevant)
    if sector_val == "apt" or sector_val == "ret":
        emp_chg_use = 'emp_chg'
    elif sector_val == "off":
        emp_chg_use = 'off_emp_chg'
    elif sector_val == "ind":
        emp_chg_use = 'ind_emp_chg'
    
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (data['yr'] <= curryr + 1) & (data['G_mrent'] > data['prev_G_mrent']) & (data['G_mrent'] - data['prev_G_mrent'] <= (data[emp_chg_use] - data['prev_emp_chg']) * 2) & (data['emp_chg_z'] > -1.5), 0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (data['yr'] <= curryr + 1) & (data['G_mrent'] < data['prev_G_mrent']) & (data['G_mrent'] - data['prev_G_mrent'] >= (data[emp_chg_use] - data['prev_emp_chg']) * 2) & (data['emp_chg_z'] < 1.5), 0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (data['yr'] > curryr + 1) & (data['G_mrent'] > data['prev_G_mrent']) & (data['G_mrent'] - data['prev_G_mrent'] <= (data[emp_chg_use] - data['prev_emp_chg'])), 0, data['g_flag_yrdiff'])
    data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (data['yr'] > curryr + 1) & (data['G_mrent'] < data['prev_G_mrent']) & (data['G_mrent'] - data['prev_G_mrent'] >= (data[emp_chg_use] - data['prev_emp_chg'])), 0, data['g_flag_yrdiff'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data['g_flag_yrdiff'] = np.where((data['g_flag_yrdiff'] == 1) & (abs(round(data['G_mrent'] - data['prev_G_mrent'],3)) - abs(round(data['grolsmre'] - data['grolsmre'].shift(1),3)) < 0.003), 0, data['g_flag_yrdiff'])

    
    data['calc_gyrdiff'] = np.where((data['g_flag_yrdiff'] == 1), abs((data['G_mrent'] - data['prev_G_mrent']) / (data['prev_G_mrent'] + 0.000001)), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if there are three consecutive years of below average market rent growth in the submarket forecast
def g_cons_low(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_cons_low'] = np.where((data['forecast_tag'] != 0) & (data['cons_low_G_mrent'] == 1), 1, 0)
    
    # Dont flag if employment change indicates change from history
    if currqtr == 4:
        period = 1
    else:
        period = currqtr + 1
    data['g_flag_cons_low'] = np.where((data['g_flag_cons_low'] == 1) & (data['emp_chg_z'] <= -1.5), 0, data['g_flag_cons_low'])
    data['g_flag_cons_low'] = np.where((data['g_flag_cons_low'] == 1) & (data['yr'] == curryr) & (data['emp_chg_z'].shift(periods=period) <= -2) & (data['G_mrent_nonc'] > data['G_mrent_nonc'].shift(periods=period)), 0, data['g_flag_cons_low'])
    data['g_flag_cons_low'] = np.where((data['g_flag_cons_low'] == 1) & (data['yr'] > curryr) & (data['emp_chg_z'].shift(1) <= -2) & (data['G_mrent_nonc'] > data['G_mrent_nonc'].shift(1)), 0, data['g_flag_cons_low'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_cons_low', 'G_mrent', 'grolsmre', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['g_flag_cons_low'] = np.where((data['yr'] == curryr) & (data['g_flag_cons_low'] == 1) & (data['G_mrent'] + data['G_mrent'].shift(periods=period) + data['G_mrent'].shift(periods=period + 5) > data['grolsmre'] + data['grolsmre'].shift(periods=period) + data['grolsmre'].shift(periods=period + 5)), 0, data['g_flag_cons_low'])
        data['g_flag_cons_low'] = np.where((data['yr'] == curryr + 1) & (data['g_flag_cons_low'] == 1) & (data['G_mrent'] + data['G_mrent'].shift(1) + data['G_mrent'].shift(periods=period + 1) > data['grolsmre'] + data['grolsmre'].shift(1) + data['grolsmre'].shift(periods=period + 1)), 0, data['g_flag_cons_low'])
        data['g_flag_cons_low'] = np.where((data['yr'] > curryr + 1) & (data['g_flag_cons_low'] == 1) & (data['G_mrent'] + data['G_mrent'].shift(1) + data['G_mrent'].shift(2) > data['grolsmre'] + data['grolsmre'].shift(1) + data['grolsmre'].shift(2)), 0, data['g_flag_cons_low'])


    data['calc_gconslow'] = np.where((data['g_flag_cons_low'] == 1), data['cons_low_G_mrent'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if G_mrent isnt in line with the vacancy movement sentiment
def g_vac(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_vac'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) & 
                                         (abs(data['vac_chg']) > data['avg_vac_chg']) & (data['vac_chg'] > 0) & (data['G_mrent'] > data['avg_G_mrent_chg_nonc']),
                                          1, 0)
    data['g_flag_vac'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) & 
                                         (abs(data['vac_chg']) < data['avg_vac_chg'] ) & (data['vac_chg'] < 0) & (data['G_mrent'] < data['avg_G_mrent_chg_nonc']),
                                          1, data['g_flag_vac'])
    if currqtr != 4:
        data['g_flag_vac'] = np.where((data['forecast_tag'] == 1) & 
                                             (abs(data['implied_vac_chg']) > ((data['avg_vac_chg']) * ((4 - currqtr)/4))) & (data['implied_vac_chg'] > 0) & (data['implied_G_mrent'] > (data['avg_G_mrent_chg_nonc'] * ((4 - currqtr)/4))),
                                            1, data['g_flag_vac'])
        data['g_flag_vac'] = np.where((data['forecast_tag'] == 1) & 
                                             (abs(data['implied_vac_chg']) > ((data['avg_vac_chg']) * ((4 - currqtr)/4))) & (data['implied_vac_chg'] < 0) & (data['implied_G_mrent'] < (data['avg_G_mrent_chg_nonc'] * ((4 - currqtr)/4))),
                                            1, data['g_flag_vac'])

    # Dont flag if there is construction that is causing the opposing movements
    if currqtr == 4:
        data['cons_inv_multiple'] = np.where((data['cons'] / data['inv'] >= 0.15), 2, 1)
        data['g_flag_vac'] = np.where((data['g_flag_vac'] == 1) & (data['vac_chg'] > 0) & (data['abs_cons_r'] >= 0.5) & ((data['G_mrent'] / 4) < (data['cons_prem'] * data['cons_inv_multiple'])) & (data['cons'] / data['inv'] >= 0.015), 0, data['g_flag_vac'])
    elif currqtr != 4:
        data['cons_inv_multiple'] = np.where((data['forecast_tag'] == 1) & (data['implied_cons'] / data['inv'] >= 0.15), 2, 1)
        data['cons_inv_multiple'] = np.where((data['forecast_tag'] == 2) & (data['cons'] / data['inv'] >= 0.15), 2, data['cons_inv_multiple'])
        data['g_flag_vac'] = np.where((data['g_flag_vac'] == 1) & (data['forecast_tag'] == 2) & (data['vac_chg'] > 0) & (data['abs_cons_r'] >= 0.5) & ((data['G_mrent'] / 4) < ((data['cons_prem'] * data['cons_prem_mod']) * data['cons_inv_multiple'])) & (data['cons'] / data['inv'] >= 0.015), 0, data['g_flag_vac'])
        data['g_flag_vac'] = np.where((data['g_flag_vac'] == 1) & (data['forecast_tag'] == 1) & (data['implied_vac_chg'] > 0) & (data['abs_cons_r'] >= 0.5) & (data['implied_G_mrent'] / (4 - currqtr) < ((data['cons_prem'] * data['cons_prem_mod']) * data['cons_inv_multiple'])) & (data['implied_cons'] / data['inv'] >= 0.015), 0, data['g_flag_vac'])

    data = data.drop(['cons_inv_multiple'], axis=1)
    
    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'g_flag_vac', 'G_mrent', 'grolsmre', 'vac_chg', 'rolsvac_chg', 2, 'h', 'rol_h', sector_val, curryr, currqtr)

    
    data['calc_gvac'] = np.where((data['g_flag_vac'] == 1), (abs(data['G_mrent'] - data['avg_G_mrent_chg_nonc'])) * (abs(data['vac_chg'] - data['avg_vac_chg'])), np.nan)
    if currqtr != 4:
        data['calc_gvac'] = np.where((data['forecast_tag'] == 1) & (data['g_flag_vac'] == 1), (abs(data['implied_G_mrent'] - (data['avg_G_mrent_chg_nonc'] * ((4 - currqtr)/4)))) * (abs(data['implied_vac_chg'] - ((data['avg_vac_chg'] + data['std_dev_vac_chg']) * ((4 - currqtr)/4)))), data['calc_gvac'])
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if the market rent change has high variability across the submarkets within a metro for a particular year
def g_subv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['g_flag_subv'] = np.where((data['G_mrent_sub_var'] > 0), 1, 0)

    data['calc_gsubv'] = np.where((data['g_flag_subv'] == 1), data['G_mrent_sub_var'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if the market rent change quartile is at the opposite end of the employment chg quartile
def g_emp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "apt" or sector_val == "ret":
        quart_use = 'emp_quart'
        chg_use = "emp_chg"
    elif sector_val == "off":
        quart_use = 'off_emp_quart'
        chg_use = "off_emp_chg"
    elif sector_val == "ind":
        quart_use = "ind_emp_quart"
        chg_use = "ind_emp_chg"

    data['g_flag_emp'] = np.where((abs(data[quart_use] - data['G_mrent_quart']) == 3) & (data['forecast_tag'] == 1), 1, 0)
    
    data['g_flag_emp'] = np.where((data['G_mrent_quart'] == 1) & (data['forecast_tag'] == 2) & (data[chg_use] <= data['emp_5']), 1, data['g_flag_emp'])
    data['g_flag_emp'] = np.where((data['G_mrent_quart'] == 4) & (data['forecast_tag'] == 2) & (data[chg_use] >= data['emp_95']), 1, data['g_flag_emp'])
    data['g_flag_emp'] = np.where((data['G_mrent_quart'] == 1) & (data['forecast_tag'] == 2) & (data[chg_use] <= data['hist_emp_10']), 1, data['g_flag_emp'])
    data['g_flag_emp'] = np.where((data['G_mrent_quart'] == 4) & (data['forecast_tag'] == 2) & (data[chg_use] >= data['hist_emp_90']), 1, data['g_flag_emp'])

    # Dont flag if the G_mrent is ending up in a higher quartile than emp chg would indicate if nc is the cause
    if currqtr != 4:
        data['g_flag_emp'] = np.where((data['g_flag_emp'] == 1) & (data['forecast_tag'] == 1) & (data['implied_cons'] / data['inv'] >= 0.015) & (data['G_mrent_quart'] < data[quart_use]) & (data['G_mrent_quart'] > 1), 0, data['g_flag_emp'])
        data['g_flag_emp'] = np.where((data['g_flag_emp'] == 1) & (data['forecast_tag'] == 2) & (data['cons'] / data['inv'] >= 0.04) & (data['G_mrent_quart'] < data[quart_use]) & (data['G_mrent_quart'] == 1), 0, data['g_flag_emp'])
    elif currqtr == 4:
        data['g_flag_emp'] = np.where((data['g_flag_emp'] == 1) & (data['cons'] / data['inv'] >= 0.015) & (data['G_mrent_quart'] < data[quart_use]) & (data['G_mrent_quart'] > 1), 0, data['g_flag_emp'])
        data['g_flag_emp'] = np.where((data['g_flag_emp'] == 1) & (data['cons'] / data['inv'] >= 0.04) & (data['G_mrent_quart'] < data[quart_use]) & (data['G_mrent_quart'] == 1), 0, data['g_flag_emp'])
    
    data['calc_gemp'] = np.where((data['g_flag_emp'] == 1), abs(data[quart_use] - data['G_mrent_quart']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if there is a large change in the employment forecast from ROL, but not a commensurate reponse in market rent change
def g_emp_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "apt" or sector_val == "ret":
        quart_use = 'emp_quart'
        chg_use = 'emp_chg'
        rol_use = 'rol_emp_chg'
    elif sector_val == "off":
        quart_use = 'off_emp_quart'
        chg_use = 'off_emp_chg'
        rol_use = 'rol_off_emp_chg'
    elif sector_val == "ind":
        quart_use = "ind_emp_quart"
        chg_use = 'ind_emp_chg'
        rol_use = 'rol_ind_emp_chg'

    data['target_chg'] = (data[chg_use] - data[rol_use]) * 0.5
    data['g_flag_emp_rol'] = np.where((((data['forecast_tag'] == 2) & (data['yr'] <= curryr + 4)) | ((data['forecast_tag'] == 1) & (currqtr == 4))) & 
                                       (abs(data['target_chg']) > 0.005) & ((data['G_mrent'] - data['grolsmre']) * data['target_chg'] < 0)
                                       , 1, 0)
    data['g_flag_emp_rol'] = np.where(((data['forecast_tag'] == 2) | ((data['forecast_tag'] == 1) & (currqtr == 4))) & 
                                       (abs(data['target_chg']) > 0.005) & ((data['G_mrent'] - data['grolsmre']) - data['target_chg'] > 0.002) & (abs(data['G_mrent'] - data['grolsmre']) < abs(data['target_chg']))
                                       , 1, data['g_flag_emp_rol'])
    
    data['calc_gemp_rol'] = np.where((data['g_flag_emp_rol'] == 1), abs((data['G_mrent'] - data['grolsmre']) - data['target_chg']), np.nan)
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['target_chg'], axis=1)

    return data, calc_names

# Flag if gap chg is different from rol without absorption change justification if this is Q4 or a future forecast year
def e_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):
    
    # First test if gap is moving in the wrong direction relative to rol based on the change in vac from rol
    data['e_flag_rol'] =  np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         (data['gap_chg'] > data['rolsgap_chg']) & (data['vac_chg'] <= data['rolsvac_chg']) & (abs(data['gap_chg'] - data['rolsgap_chg']) > 0.003),
                                         1, 0)

    data['e_flag_rol'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         (data['gap_chg'] < data['rolsgap_chg']) & (data['vac_chg'] >= data['rolsvac_chg']) & (abs(data['gap_chg'] - data['rolsgap_chg']) > 0.003),
                                         1, data['e_flag_rol'])

    # Then test if the change in gap chg from rol is too large based on the change in vac chg, even if they are moving in the direction that one would expect
    data['e_flag_rol'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         (round(data['gap_chg'] - data['rolsgap_chg'],3) > round((data['vac_chg'] - data['rolsvac_chg']) * 0.70,3) + 0.003) & (data['gap_chg'] > data['rolsgap_chg']) & ((data['gap_chg'] - data['rolsgap_chg']) * (data['vac_chg'] - data['rolsvac_chg']) >= 0) & (abs(data['gap_chg'] - data['rolsgap_chg']) > 0.003),
                                         1, data['e_flag_rol'])

    data['e_flag_rol'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         (round(data['gap_chg'] - data['rolsgap_chg'],3) < round((data['vac_chg'] - data['rolsvac_chg']) * 0.70,3) - 0.003) & (data['gap_chg'] < data['rolsgap_chg']) & ((data['gap_chg'] - data['rolsgap_chg']) * (data['vac_chg'] - data['rolsvac_chg']) >= 0) & (abs(data['gap_chg'] - data['rolsgap_chg']) > 0.003),
                                         1, data['e_flag_rol'])

    # Dont flag if rol gap was moving in the wrong direction from vac chg, and now it is moving in the correct direction
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['rolsvac_chg'] < 0) & (data['rolsgap_chg'] > 0) & (data['vac_chg'] * data['gap_chg'] >= 0) & (abs(data['gap_chg'] - (data['vac_chg'] * 0.70)) <= 0.002), 0, data['e_flag_rol'])
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['rolsvac_chg'] > 0) & (data['rolsgap_chg'] < 0) & (data['vac_chg'] * data['gap_chg'] >= 0) & (abs(data['gap_chg'] - (data['vac_chg'] * 0.70)) <= 0.002), 0, data['e_flag_rol'])

    # Dont flag if the gap chg and vac_chg are now aligned, even if the diff to rol target is not met
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (abs(data['gap_chg'] - (data['vac_chg'] * 0.7)) <= 0.002) & (data['gap_chg'] * data['vac_chg'] >= 0), 0, data['e_flag_rol'])

    # Dont flag if there is only a small rise in vacancy and gap is not moving much
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['vac_chg'] < 0.005) & (data['vac_chg'] >= 0) & (abs(data['gap_chg']) < 0.002) & (data['vac_chg'] * data['gap_chg'] >= 0), 0, data['e_flag_rol'])

    # Dont flag if the target would cause the gap chg to exceed either the min gap chg or max gap chg significantly, or fall below or above an outlier gap level
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['vac_chg'] < 0) & (data['gap_chg'] <= 0) & (data['gap_chg'] > data['vac_chg']) & (data['vac_chg'] * 0.7 < data['min_gap_chg'] - 0.005), 0, data['e_flag_rol'])
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['vac_chg'] > 0) & (data['gap_chg'] >= 0) & (data['gap_chg'] < data['vac_chg']) & (data['vac_chg'] * 0.7 > data['max_gap_chg'] + 0.005), 0, data['e_flag_rol'])
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['vac_chg'] < 0) & (data['gap_chg'] <= 0.005) & (data['gap_chg'] >= 0) & (data['gap_chg'] >= data['vac']) & (data['gap'].shift(1) + (data['vac_chg'] * 0.7) < data['gap_95']), 0, data['e_flag_rol'])
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['vac_chg'] > 0) & (data['gap_chg'] >= 0.005) & (data['gap_chg'] <= 0) & (data['gap_chg'] <= data['vac']) & (data['gap'].shift(1) + (data['vac_chg'] * 0.7) > data['gap_5']), 0, data['e_flag_rol'])

    # Dont flag if employment change is different than ROL
    data['vac_add_factor'] = np.where(((data['gap_chg'] - data['rolsgap_chg']) * (data['vac_chg'] - data['rolsvac_chg']) > 0), ((data['vac_chg'] - data['rolsvac_chg']) * 0.70), 0)
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['gap_chg'] > data['rolsgap_chg']) & (data['vac_chg'] - data['rolsvac_chg'] >= -0.01) & (data['gap_chg'] - data['rolsgap_chg'] <= (data['emp_chg_diff'] * -3) + data['vac_add_factor']) & (data['emp_chg_diff'] < 0), 0, data['e_flag_rol'])
    data['e_flag_rol'] = np.where((data['e_flag_rol'] == 1) & (data['gap_chg'] < data['rolsgap_chg']) & (data['vac_chg'] - data['rolsvac_chg'] <= 0.01) & (data['gap_chg'] - data['rolsgap_chg'] >= (data['emp_chg_diff'] * -3) - data['vac_add_factor']) & (data['emp_chg_diff'] > 0), 0, data['e_flag_rol'])
    data = data.drop(['vac_add_factor'], axis=1)
    
    data['calc_erol'] = np.where((data['e_flag_rol']), abs((data['gap_chg'] - data['rolsgap_chg']) / data['rolsgap_chg']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if gap chg is similar to ROL gap but there has been a large change in vacancy chg relative to ROL
def e_rolvac(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_rolvac'] = np.where((((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                         (data['forecast_tag'] == 2)) &
                                         (abs(data['gap_chg'] - data['rolsgap_chg']) <= 0.002) & (abs(data['vac_chg'] - data['rolsvac_chg']) > 0.003) & ((data['gap_chg'] - data['rolsgap_chg']) * (data['vac_chg'] - data['rolsvac_chg']) >= 0) & (abs(abs(data['gap_chg'] - data['rolsgap_chg'])  - abs(data['vac_chg'] - data['rolsvac_chg'])) > 0.002),
                                         1, 0)

    data['calc_erolvac'] = np.where((data['e_flag_rolvac'] == 1), abs((abs(data['gap_chg'] - data['rolsgap_chg'])) - (abs(data['vac_chg'] - data['rolsvac_chg']))), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if gap is zero or below
def e_zero(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_zero'] = np.where((data['forecast_tag'] != 0) & (data['gap'] <= 0), 1, 0)

    data['calc_ezero'] = np.where((data['e_flag_zero'] == 1), data['gap'] * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if gap chg is below the 10 year min gap level
def e_min(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_min'] = np.where((data['forecast_tag'] != 0) & 
                                      (data['gap'] < data['min_gap'] - 0.01),
                                      1, 0)

    # Dont flag if the change in vacancy warrants the change in gap, even if it is outside the bound of the historical min, if the gap is not in the national outiler range
    data['e_flag_min'] = np.where((data['e_flag_min'] == 1) & (data['gap_chg'] >= ((data['vac_chg']) * 0.70)) & (data['vac_chg'] <= 0) & (data['gap'] - data['min_gap'] >= -0.02) & (data['gap'] > data['gap_95']), 0, data['e_flag_min'])

    # Dont flag if the sub has limited history and the gap is not an outlier
    data['e_flag_min'] = np.where((data['e_flag_min'] == 1) & (data['lim_hist'] <= 5) & (data['gap'] > data['gap_95']), 0, data['e_flag_min'])

    # Dont flag if employment change indicates large change from history
    data['e_flag_min'] = np.where((data['e_flag_min'] == 1) & (data['emp_chg_z'] >= 2) & (data['gap'] > data['gap_95']), 999999999, data['e_flag_min'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['e_flag_min'] = np.where((data['e_flag_min'] == 999999999) & (((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                      (data['forecast_tag'] == 2)) &
                                      (abs((data['gap_chg'] - data['min_gap_chg']) / data['min_gap_chg']) > 0.5) & (data['gap_chg'] < data['min_gap_chg']),
                                      1, data['e_flag_min'])

    data['e_flag_min'] = np.where((data['e_flag_min'] == 999999999), 0, data['e_flag_min'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'e_flag_min', 'gap', 'rolsgap', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['e_flag_min'] = np.where((data['e_flag_min'] == 7777) & (data['rolsgap'] <= data['min_gap']), 0, data['e_flag_min'])
        data['e_flag_min'] = np.where((data['e_flag_min'] == 7777), 1, data['e_flag_min'])
        data['e_flag_min'] = np.where((data['e_flag_min'] == 1) & (data['gap'] > data['rolsgap']), 0, data['e_flag_min'])

    data['calc_emin'] = np.where((data['e_flag_min'] == 1), (data['gap'] - data['min_gap']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if gap chg is above the 10 year max gap level
def e_max(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_max'] = np.where((data['forecast_tag'] != 0) &
                                     (data['gap'] > data['max_gap'] + 0.01),
                                     1, 0)

    # Dont flag if the change in vacancy warrants the change in gap, even if it is outside the bound of the historical max, if the gap is not in the national outiler range
    data['e_flag_max'] = np.where((data['e_flag_max'] == 1) & (data['gap_chg'] < ((data['vac_chg']) * 0.70)) & (data['vac_chg'] >= 0) & (data['gap'] - data['max_gap'] <= 0.02) & (data['gap'] < data['gap_5']), 0, data['e_flag_max'])

    # Dont flag if the sub has limited history and the gap is not an outlier
    data['e_flag_max'] = np.where((data['e_flag_max'] == 1) & (data['lim_hist'] <= 5) & (data['gap'] < data['gap_5']), 0, data['e_flag_max'])

    # Dont flag if employment indicates this year is an outlier
    data['e_flag_max'] = np.where((data['e_flag_max'] == 1) & (data['emp_chg_z'] <= -2) & (data['gap'] < data['gap_5']), 999999999, data['e_flag_max'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['e_flag_max'] = np.where((data['e_flag_max'] == 999999999) & (data['forecast_tag'] != 0) &
                                      (abs((data['gap_chg'] - data['max_gap_chg']) / data['max_gap_chg']) > 0.5) & (data['gap_chg'] > data['max_gap_chg']),
                                      1, data['e_flag_max'])

    data['e_flag_max'] = np.where((data['e_flag_max'] == 999999999), 0, data['e_flag_max'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'e_flag_max', 'gap', 'rolsgap', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['e_flag_max'] = np.where((data['e_flag_max'] == 7777) & (data['rolsgap'] >= data['max_gap']), 0, data['e_flag_max'])
        data['e_flag_max'] = np.where((data['e_flag_max'] == 7777), 1, data['e_flag_max'])
        data['e_flag_max'] = np.where((data['e_flag_max'] == 1) & (data['gap'] < data['rolsgap']), 0, data['e_flag_max'])

    data['calc_emax'] = np.where((data['e_flag_max'] == 1), data['gap_chg'] - data['max_gap_chg'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if gap chg is below the 10 year min gap chg
def e_min_chg(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_min_chg'] = np.where((data['forecast_tag'] != 0) & 
                                      (data['gap_chg'] < data['min_gap_chg'] - 0.002),
                                      1, 0)
    
    # Dont flag if the change in vacancy warrants the change in gap, even if it is outside the bound of the historical min
    data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 1) & (data['gap_chg'] >= ((data['vac_chg']) * 0.70) - 0.002) & (data['vac_chg'] <= 0) & (data['gap'] > data['gap_95']), 0, data['e_flag_min_chg'])

    # Dont flag if the sub has limited history and the gap chg is reasonable
    data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 1) & (data['lim_hist'] <= 5) & (data['gap_quart'] > 1) & (data['gap'] > data['gap_95']), 0, data['e_flag_min_chg'])

    # Dont flag if employment change indicates large change from history
    data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 1) & (data['emp_chg_z'] >= 2) & (data['gap'] > data['gap_95']), 999999999, data['e_flag_min_chg'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 999999999) & (((currqtr == 4) & (data['forecast_tag'] == 1)) |
                                      (data['forecast_tag'] == 2)) &
                                      (abs((data['gap_chg'] - data['min_gap_chg']) / data['min_gap_chg']) > 0.5) & (data['gap_chg'] < data['min_gap_chg']),
                                      1, data['e_flag_min_chg'])

    data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 999999999), 0, data['e_flag_min_chg'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'e_flag_min_chg', 'gap_chg', 'rolsgap_chg', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 7777) & (data['rolsgap_chg'] <= data['min_gap_chg']), 0, data['e_flag_min_chg'])
        data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 7777), 1, data['e_flag_min_chg'])
        data['e_flag_min_chg'] = np.where((data['e_flag_min_chg'] == 1) & (data['gap_chg'] > data['rolsgap_chg']), 0, data['e_flag_min_chg'])

    data['calc_emin_chg'] = np.where((data['e_flag_min_chg'] == 1), (data['gap_chg'] - data['min_gap_chg']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if gap chg is above the 10 year max gap chg
def e_max_chg(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_max_chg'] = np.where((data['forecast_tag'] != 0) &
                                     (data['gap_chg'] > data['max_gap_chg'] + 0.002),
                                     1, 0)

    # Dont flag if the change in vacancy warrants the change in gap, even if it is outside the bound of the historical max
    data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 1) & (data['gap_chg'] < ((data['vac_chg']) * 0.70) + 0.002) & (data['vac_chg'] >= 0) & (data['gap'] < data['gap_5']), 0, data['e_flag_max_chg'])

    # Dont flag if the sub has limited history and the gap chg is reasonable
    data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 1) & (data['lim_hist'] <= 5) & (data['gap_quart'] < 4) & (data['gap'] < data['gap_5']), 0, data['e_flag_max_chg'])

    # Dont flag if employment indicates this year is an outlier
    data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 1) & (data['emp_chg_z'] <= -2) & (data['gap'] < data['gap_5']), 999999999, data['e_flag_max_chg'])

    # Failsafe for cases where the employment forecast indicates history not in line with current economic conditions - widen the threshold for flagging
    data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 999999999) & (data['forecast_tag'] != 0) &
                                      (abs((data['gap_chg'] - data['max_gap_chg']) / data['max_gap_chg']) > 0.5) & (data['gap_chg'] > data['max_gap_chg']),
                                      1, data['e_flag_max_chg'])
    
    data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 999999999), 0, data['e_flag_max_chg'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'e_flag_max_chg', 'gap_chg', 'rolsgap_chg', False, False, 1, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 7777) & (data['rolsgap_chg'] >= data['max_gap_chg']), 0, data['e_flag_max_chg'])
        data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 7777), 1, data['e_flag_max_chg'])
        data['e_flag_max_chg'] = np.where((data['e_flag_max_chg'] == 1) & (data['gap_chg'] < data['rolsgap_chg']), 0, data['e_flag_max_chg'])

    data['calc_emax_chg'] = np.where((data['e_flag_max_chg'] == 1), data['gap_chg'] - data['max_gap_chg'], np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if effective rent growth forecast in the curr year forecast row results in a change from ROL effective rent growth and the change increases the implied level
def e_improls(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:
        
        data['e_flag_improls'] = np.where((data['forecast_tag'] == 1) &
            (abs((data['implied_gap_chg'] - (data['implied_vac_chg'] * 0.7))) - abs((data['implied_using_rolsgap_chg'] - (data['implied_vac_chg'] * 0.7))) > 0.0025),
            1, 0)

        # Dont flag if using rol would move in the opposite directiion of vac chg sentiment, even if that would minimize the difference 
        data['e_flag_improls'] = np.where((data['e_flag_improls'] != 0) & (data['implied_gap_chg'] * data['implied_vac_chg'] > 0) & 
                                (data['implied_using_rolsgap_chg'] * data['implied_vac_chg'] < 0) & (abs((data['implied_gap_chg'] - (data['implied_vac_chg'] * 0.7))) - abs((data['implied_using_rolsgap_chg'] - (data['implied_vac_chg'] * 0.7))) > 0.01), 0, data['e_flag_improls'])

        data['calc_eimprols'] = np.where((data['e_flag_improls'] == 1), abs(abs((data['implied_gap_chg'] - (data['implied_vac_chg'] * 0.7))) - abs((data['rolsgap_chg'] - (data['implied_vac_chg'] * 0.7)))), np.nan)
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['e_flag_improls'] = 0
        data['calc_eimprols'] = 0
        calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if implied gap movement is not in line with vacancy movement expectation if this is not Q4
def e_imp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr != 4:
        
        data['e_flag_imp'] = np.where((data['forecast_tag'] == 1) & 
                                    (abs((data['implied_gap_chg'] - (data['implied_vac_chg'] * 0.7)) / ((data['implied_vac_chg'] * 0.7) + 0.000001)) > 0.75),
                                    1, 0)

        # Because percentage change doesnt work so well when the numbers are really small, add additional qualification for spread instead of straight percentage change
        data['e_flag_imp'] = np.where((data['forecast_tag'] == 1) & 
            (abs(data['implied_gap_chg'] - (data['implied_vac_chg'] * 0.7)) < 0.005) & (round(data['implied_gap_chg'],3) * round(data['implied_vac_chg'],3) >= 0) & (abs(data['implied_gap_chg']) < 0.02),
            0, data['e_flag_imp'])

        # Dont flag cases where there is strong trend vac chg - gap movement can lag vac chg and show up here, despite what implied vac chg is doing
        data['trend_vac_chg'] = np.where((data['forecast_tag'] == 1), data['vac'].shift(1) - data['vac'].shift(periods=currqtr + 1), np.nan)
        data['trend_gap_chg'] = np.where((data['forecast_tag'] == 1), data['gap'].shift(1) - data['gap'].shift(periods=currqtr + 1), np.nan)
        data['e_flag_imp'] = np.where((data['e_flag_imp'] == 1) & (data['trend_vac_chg'] * 0.7 > 0) & (data['curr_yr_trend_cons'] / data['inv'] < 0.03) & (data['trend_gap_chg'] < data['trend_vac_chg'] * 0.7) & (data['implied_gap_chg'] > 0) & (data['implied_gap_chg'] < data['trend_vac_chg'] * 0.7 + 0.002), 0, data['e_flag_imp'])
        data['e_flag_imp'] = np.where((data['e_flag_imp'] == 1) & (data['trend_vac_chg'] * 0.7 < 0) & (data['trend_gap_chg'] > data['trend_vac_chg'] * 0.7) & (data['implied_gap_chg'] < 0) & (data['implied_gap_chg'] > data['trend_vac_chg'] * 0.7 - 0.002), 0, data['e_flag_imp'])        
        data = data.drop(['trend_vac_chg', 'trend_gap_chg'], axis=1)
    
        data['calc_eimp'] = np.where((data['e_flag_imp'] == 1), abs((data['implied_gap_chg'] - (data['implied_vac_chg'] * 0.7)) / ((data['implied_vac_chg'] * 0.7) + 0.000001)), np.nan)
        calc_names.append(list(data.columns)[-1])

    elif currqtr == 4:
        data['e_flag_imp'] = 0
        data['calc_eimp'] = 0
        calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if effective rent growth forecast in non curr year forecast row is not in line with vacancy change
def e_vac(data, curryr, currqtr, sector_val, calc_names, use_rol_close):
        
    data['e_flag_vac'] = np.where((data['forecast_tag'] == 2) & 
                                    (abs((data['gap_chg'] - (data['vac_chg'] * 0.7)) / ((data['vac_chg'] * 0.7) + 0.000001)) > 0.70),
                                    1, 0)

    # Because percentage change doesnt work so well when the numbers are really small, add additional qualification for spread instead of straight percentage change
    data['e_flag_vac'] = np.where((data['forecast_tag'] == 2) & 
            (abs(data['gap_chg'] - (data['vac_chg'] * 0.7)) < 0.005) & (round(data['gap_chg'],3) * round(data['vac_chg'],3) >= 0) & (abs(data['gap_chg']) < 0.02),
            0, data['e_flag_vac'])

    # Dont flag if gap is below the vac chg based target if moving in that direction would cause the gap to become an outlier value, or if gap is already an outlier value and gap change makes it less of an outlier, so long as gap chg is reasonable
    data['e_flag_vac'] = np.where((data['e_flag_vac'] == 1) & ((data['vac_chg'] * 0.7) + data['gap'].shift(1) >= data['gap_5']) & (data['vac_chg'] * 0.7 > 0) & (data['gap_chg'] >= -0.003), 0, data['e_flag_vac'])
    data['e_flag_vac'] = np.where((data['e_flag_vac'] == 1) & ((data['vac_chg'] * 0.7) + data['gap'].shift(1) <= data['gap_95']) & (data['vac_chg'] * 0.7 < 0) & (data['gap_chg'] <= 0.003), 0, data['e_flag_vac'])
    data['e_flag_vac'] = np.where((data['e_flag_vac'] == 1) & (data['gap'].shift(1) >= data['gap_5']) & (data['gap_chg'] >= -0.005) & (data['gap_chg'] <= 0) & (abs((data['vac_chg'] * 0.7) - data['gap_chg']) < 0.015) & (round(data['gap_chg'],3) * round(data['vac_chg'],3) <= 0), 0, data['e_flag_vac'])
    data['e_flag_vac'] = np.where((data['e_flag_vac'] == 1) & (data['gap'].shift(1) <= data['gap_95']) & (data['gap_chg'] <= 0.005) & (data['gap_chg'] >= 0) & (abs((data['vac_chg'] * 0.7) - data['gap_chg']) < 0.015) & (round(data['gap_chg'],3) * round(data['vac_chg'],3) <= 0), 0, data['e_flag_vac'])
    
    # Dont flag if gap is falling and was at an outlier level, even if vac chg is relatively flat
    data['e_flag_vac'] = np.where((data['e_flag_vac'] == 1) & (data['forecast_tag'] == 2) & (abs(data['vac_chg']) <= 0.002) & (data['gap_chg'] < 0) & (data['gap'] - data['gap_chg'] > data['gap_5']) & (abs(data['gap_chg']) < 0.02), 0, data['e_flag_vac'])

    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'e_flag_vac', 'gap_chg', 'rolsgap_chg', 'vac_chg', 'rolsvac_chg', 2, 'h', 'rol_h', sector_val, curryr, currqtr)

    data['calc_evac'] = np.where((data['e_flag_vac'] == 1), abs((data['gap_chg'] - (data['vac_chg'] * 0.7)) / ((data['vac_chg'] * 0.7) + 0.000001)), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if the effective rent growth is in the opposite direction as market rent growth
def e_market(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    data['e_flag_market'] = np.where((data['forecast_tag'] == 2) & (data['G_mrent'] * data['G_merent'] < 0) & (abs(data['G_mrent'] - data['G_merent']) > 0.003),
                                            1, 0)
    if currqtr == 4:
        data['e_flag_market'] = np.where((data['forecast_tag'] == 1) & (data['G_mrent'] * data['G_merent'] < 0) & (abs(data['G_mrent'] - data['G_merent']) > 0.003),
                                            1, data['e_flag_market'])
                                    
    elif currqtr != 4:
        data['e_flag_market'] = np.where((data['forecast_tag'] == 1) & (data['implied_G_mrent'] * data['implied_G_merent'] < 0) & (abs(data['implied_G_mrent'] - data['implied_G_merent']) > 0.003),
                                            1, data['e_flag_market'])
    
    # Dont flag if the reason effective rent is decreasing when market rent is increasing is due to construction
    data['e_flag_market'] = np.where((data['e_flag_market'] == 1) & (data['forecast_tag'] == 2) & (data['cons'] / data['inv']) & (data['G_mrent'] > 0) & (data['G_merent'] < 0) & (data['gap_chg'] < data['vac_chg'] * 0.7), 0, data['e_flag_market'])
    
    if currqtr == 4:
        data['e_flag_market'] = np.where((data['e_flag_market'] == 1) & (data['forecast_tag'] == 1) & (data['cons'] / data['inv']) & (data['G_mrent'] > 0) & (data['G_merent'] < 0) & (data['gap_chg'] < data['vac_chg'] * 0.7), 0, data['e_flag_market'])

    elif currqtr != 4:
        data['e_flag_market'] = np.where((data['e_flag_market'] == 1) & (data['forecast_tag'] == 1) & (data['implied_cons'] / data['inv']) & (data['implied_G_mrent'] > 0) & (data['implied_G_merent'] < 0) & (data['implied_gap_chg'] < data['implied_vac_chg'] * 0.7), 0, data['e_flag_market'])
    
    # Dont flag if the value is close to rol
    if use_rol_close == "Y":
        data = rol_close(data, 'e_flag_market', 'G_merent', 'grolsmer', 'G_mrent', 'grolsmre', 2, 'h', 'rol_h', sector_val, curryr, currqtr)
        data['e_flag_market'] = np.where((data['e_flag_market'] == 7777) & (data['grolsmre'] * data['grolsmer'] < 0), 0, data['e_flag_market'])
        data['e_flag_market'] = np.where((data['e_flag_market'] == 7777), 1, data['e_flag_market'])
        data['e_flag_market'] = np.where((data['forecast_tag'] == 2) & (data['e_flag_market'] == 1) & (data['G_mrent'] - data['G_merent'] < data['grolsmre'] - data['grolsmer']) & (data['grolsmre'] * data['grolsmer'] < 0), 0, data['e_flag_market'])

    data['calc_emarket'] = np.where((data['e_flag_market'] == 1), abs(data['G_mrent'] - data['G_merent']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if the gap change quartile is at the opposite end of the employment chg quartile
def e_emp(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "apt" or sector_val == "ret":
        quart_use = 'emp_quart'
        chg_use = "emp_chg"
    elif sector_val == "off":
        quart_use = 'off_emp_quart'
        chg_use = "off_emp_chg"
    elif sector_val == "ind":
        quart_use = "ind_emp_quart"
        chg_use = "ind_emp_chg"
    
    data['e_flag_emp'] = np.where((abs(data[quart_use] - data['gap_quart']) == 3) & (data['forecast_tag'] == 1), 1, 0)

    data['e_flag_emp'] = np.where((data['gap_quart'] == 1) & (data['forecast_tag'] == 2) & (data[chg_use] <= data['emp_5']), 1, data['e_flag_emp'])
    data['e_flag_emp'] = np.where((data['gap_quart'] == 4) & (data['forecast_tag'] == 2) & (data[chg_use] >= data['emp_95']), 1, data['e_flag_emp'])
    data['e_flag_emp'] = np.where((data['gap_quart'] == 1) & (data['forecast_tag'] == 2) & (data[chg_use] <= data['hist_emp_10']), 1, data['e_flag_emp'])
    data['e_flag_emp'] = np.where((data['gap_quart'] == 4) & (data['forecast_tag'] == 2) & (data[chg_use] >= data['hist_emp_90']), 1, data['e_flag_emp'])

    # Dont flag if gap change is in line with vacancy chg sentiment
    if currqtr == 4:
        data['e_flag_emp'] = np.where((data['e_flag_emp'] == 1) & (data['e_flag_vac'] == 0), 0, data['e_flag_emp'])
    else:
        data['e_flag_emp'] = np.where((data['e_flag_emp'] == 1) & (data['e_flag_vac'] == 0) & (data['forecast_tag'] == 2), 0, data['e_flag_emp'])
    
    data['calc_eemp'] = np.where((data['e_flag_emp'] == 1), abs(data[quart_use] - data['gap_quart']), np.nan)
    calc_names.append(list(data.columns)[-1])

    return data, calc_names

# Flag if there is a large change in the employment forecast from ROL, but not a commensurate reponse in gap chg
def e_emp_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if sector_val == "apt" or sector_val == "ret":
        quart_use = 'emp_quart'
        chg_use = 'emp_chg'
        rol_use = 'rol_emp_chg'
    elif sector_val == "off":
        quart_use = 'off_emp_quart'
        chg_use = 'off_emp_chg'
        rol_use = 'rol_off_emp_chg'
    elif sector_val == "ind":
        quart_use = "ind_emp_quart"
        chg_use = 'ind_emp_chg'
        rol_use = 'rol_ind_emp_chg'

    data['target_chg'] = (data[chg_use] - data[rol_use]) * -0.5
    data['e_flag_emp_rol'] = np.where((((data['forecast_tag'] == 2) & (data['yr'] <= curryr + 4)) | ((data['forecast_tag'] == 1) & (currqtr == 4))) & 
                                       (abs(data['target_chg']) > 0.005) & ((data['gap_chg'] - data['rolsgap_chg']) * data['target_chg'] < 0)
                                       , 1, 0)
    data['e_flag_emp_rol'] = np.where(((data['forecast_tag'] == 2) | ((data['forecast_tag'] == 1) & (currqtr == 4))) & 
                                       (abs(data['target_chg']) > 0.005) & ((data['gap_chg'] - data['rolsgap_chg']) - data['target_chg'] > 0.002) & (abs(data['gap_chg'] - data['rolsgap_chg']) < abs(data['target_chg']))
                                       , 1, data['e_flag_emp_rol'])
    
    data['calc_eemp_rol'] = np.where((data['e_flag_emp_rol'] == 1), abs((data['gap_chg'] - data['rolsgap_chg']) - data['target_chg']), np.nan)
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['target_chg'], axis=1)

    return data, calc_names

# Flag if the gap change variance throughout the forecast series at a sub is too low
def e_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close):

    if currqtr == 4:
        data['e_flag_lowv'] = np.where((data['forecast_tag'] == 1) & 
                                        (data['f_var_gap_chg'] < data['f_5_var_gap_chg']) & (data['f_var_gap_chg'].shift(1).isnull() == True),
                                         1, 0)
    elif currqtr != 4:
        data['e_flag_lowv'] = np.where((data['yr'] == curryr + 1) & 
                                    (data['f_var_gap_chg'] < data['f_5_var_gap_chg']),
                                    1, 0)                                   
    
    data['calc_elowv'] = np.where((data['e_flag_lowv'] == 1), (data['f_var_gap_chg'] - data['f_5_var_gap_chg']) * -1, np.nan)
    calc_names.append(list(data.columns)[-1])

    data = data.drop(['cons_prem_mod'], axis=1)

    return data, calc_names


def calc_flags(data_in, curryr, currqtr, sector_val, use_rol_close):

    data = data_in.copy()

    # When rounding a value that ends in 500 to the thousandths place, python will round down, which will cause flags to trigger that should not. So fix the rounding manually
    if sector_val != "apt":
        data['round_h_temp'] = round(data['h'],-3)
        data['round_h_temp'] = np.where((abs(data['h'] - data['cons']) == 500) & (data['round_h_temp'] < data['h']) & (data['round_h_temp'] < data['cons']), data['round_h_temp'] + 1000, data['round_h_temp'])
        data['round_rol_h_temp'] = round(data['rol_h'],-3)
        data['round_rol_h_temp'] = np.where((abs(data['rol_h'] - data['rolscon']) == 500) & (data['round_rol_h_temp'] < data['rol_h']) & (data['round_rol_h_temp'] < data['rolscon']), data['round_rol_h_temp'] + 1000, data['round_rol_h_temp'])
        data['round_t_temp'] = round(data['t'],-3)
        data['round_t_temp'] = np.where((abs(data['t'] - data['cons']) == 500) & (data['round_t_temp'] < data['t']) & (data['round_t_temp'] < data['cons']), data['round_t_temp'] + 1000, data['round_t_temp']) 
    else:
        data['round_h_temp'] = data['h']
        data['round_rol_h_temp'] = data['rol_h']
        data['round_t_temp'] = data['t']

    # Calculate the prev q5 trend occ for use in flags
    if currqtr != 4:
        data['prev_occ'] = np.where((data['forecast_tag'] == 2), data['occ'].shift(1), np.nan)
        data['prev_occ'] = np.where((data['forecast_tag'] == 1), data['occ'].shift(periods=currqtr + 1), data['prev_occ'])
    else:
        data['prev_occ'] = np.where((data['forecast_tag'] != 0), data['occ'].shift(1), np.nan)

    calc_names = []

    # Call the individual flag functions to assess what flags are current
    data, calc_names = c_comp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_h(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_t(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_sup(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_e(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_hist(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_size(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = c_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)

    data, calc_names = v_low(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_high(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_ratio(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_roll(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_improls(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_switch(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_imp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_z(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_min(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_max(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_level(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_3trend(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_cons_neg(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_subv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_emp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = v_emp_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)

    data, calc_names = g_low(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_nc(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_z(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_highv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_max(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_3trend(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_improls(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_imp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_yrdiff(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_cons_low(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_vac(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_subv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_emp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = g_emp_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)

    data, calc_names = e_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_rolvac(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_zero(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_min(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_max(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_min_chg(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_max_chg(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_improls(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_imp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_vac(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_market(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_emp(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_emp_rol(data, curryr, currqtr, sector_val, calc_names, use_rol_close)
    data, calc_names = e_lowv(data, curryr, currqtr, sector_val, calc_names, use_rol_close)

    flag_names = get_issue("list", sector_val)
    flag_names = list(flag_names.keys())

    # Calculate flag rankings for all flag cols
    data[flag_names] = data[calc_names].rank(ascending=False, method='first')
    data = data.drop(calc_names, axis=1)
    data[flag_names] = data[flag_names].fillna(0)

    #print("Take this out!!!!")
    #data.to_csv('/home/central/square/data/zzz-bb-test2/python/forecast/ind/test_data.csv')
    
    return data