import numpy as np
import pandas as pd
import math
from IPython.core.display import display, HTML
import re
from pathlib import Path
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import itertools
import math

from init_load_forecast import get_home

# Function that filters the dataframe for the columns to display on the data tab to the user, based on what type of flag is currently being analyzed
def set_display_cols(dataframe_in, identity_val, sector, curryr, currqtr, key_met_val, yr_val):
    dataframe = dataframe_in.copy()
    if key_met_val == False:
        key_met_val = "v"
        
    display_cols = ['identity_row', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'h', 'rol_h', 'e', 'rol_e', 't', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'occ', 'avail', 'abs', 'rolsabs', 'mrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rolsgap_chg']
    
    if key_met_val == "c":
        key_met_cols = ['three_yr_avg_cons', 'curr_yr_trend_cons', 'f_var_cons', 'implied_cons', 'avg_abs_cons']

    elif key_met_val == "v":
        key_met_cols = ['avg_vac_chg', 'std_dev_vac_chg', 'vac_z', 'min_vac', 'max_vac', '10_yr_vac', 'abs_cons_r', 'avg_abs_cons', 'extra_used_act', 'abs_nonc', 
                        'three_yr_avg_abs', 'three_yr_avg_abs_nonc', 'total_trend_abs', 'implied_abs', 'implied_rolsabs','hist_implied_abs', 'vac_quart', 
                        'f_var_vac_chg', 'vac_chg_sub_var']

    elif key_met_val == "g":
        key_met_cols = ['avg_G_mrent_chg', 'std_dev_G_mrent_chg', 'G_mrent_z', 'G_mrent_nonc', 'avg_G_mrent_chg_nonc', 'cons_prem', 'min_G_mrent', 'max_G_mrent', 'three_yr_avg_G_mrent',
                        'three_yr_avg_G_mrent_nonc', 'implied_G_mrent', 'implied_using_grolsmre', 'hist_implied_G_mrent', 'G_mrent_quart', 'f_var_G_mrent', 
                        'G_mrent_sub_var']

    elif key_met_val == "e":
        key_met_cols = ['min_gap', 'min_gap_chg', 'max_gap', 'max_gap_chg', 'gap_5', 'gap_95', 'implied_gap_chg', 'implied_G_merent', 'gap_quart']
    
    key_emp_cols = ['emp_chg', 'emp_chg_z', 'three_yr_avg_emp_chg', 'emp_5', 'emp_95', 'hist_emp_10', 'hist_emp_90']
    if sector == "apt" or sector == "ret":
        if currqtr != 4:
            key_emp_cols += ['rol_emp_chg', 'implied_emp_chg', 'emp_quart']
        elif currqtr == 4:
            key_emp_cols += ['rol_emp_chg', 'emp_quart']
    elif sector == "off":
        if currqtr != 4:
            key_emp_cols +=  ['rol_off_emp_chg', 'off_emp_chg', 'implied_off_emp_chg', 'off_emp_quart']
        elif currqtr == 4:
            key_emp_cols += ['rol_off_emp_chg', 'off_emp_chg', 'off_emp_quart']
    elif sector == "ind":
        if currqtr != 4:
            key_emp_cols +=  ['rol_ind_emp_chg', 'ind_emp_chg', 'implied_ind_emp_chg', 'ind_emp_quart']
        elif currqtr == 4:
            key_emp_cols += ['rol_ind_emp_chg', 'ind_emp_chg', 'ind_emp_quart']
    if currqtr != 4:
        key_emp_cols += ['avg_inc_chg', 'implied_avg_inc_chg']
    elif currqtr == 4:
        key_emp_cols += ['avg_inc_chg']

    if currqtr == 4:
        key_met_cols = [x for x in key_met_cols if "imp" not in x and "trend" not in x]
        key_emp_cols = [x for x in key_emp_cols if "imp" not in x and "trend" not in x]
    
    dataframe = dataframe[(dataframe['yr'] == yr_val) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val)]
    dataframe = dataframe.set_index("identity")
    
    key_met_cols = [x for x in key_met_cols if math.isnan(dataframe[x]) == False]
    key_emp_cols = [x for x in key_emp_cols if math.isnan(dataframe[x]) == False]
    
    return display_cols, key_met_cols, key_emp_cols

# Function to create current and suggested fix datatables for display to user on the data tab
def display_frame(dataframe_in, identity_val, display_cols, curryr):
    dataframe = dataframe_in.copy()
    dataframe = dataframe.reset_index()
    dataframe = dataframe.rename(columns={"index": "identity_row"})
    dataframe = dataframe.set_index("identity")
    dataframe = dataframe[(dataframe['yr'] >= curryr - 1) | ((dataframe['yr'] >= curryr - 5) & (dataframe['qtr'] == 5))]
    dataframe = dataframe[display_cols]
    dataframe = dataframe.loc[identity_val]
    dataframe = dataframe.reset_index()
    dataframe = dataframe.set_index("identity_row")
    dataframe = dataframe.drop(['identity'], axis =1)
    for z in display_cols[1:]:
        dataframe[z] = dataframe[z].apply(lambda x: '' if pd.isnull(x) else x)
    
    return dataframe

# Function to determine what key metrics to display to user based on the type of flag                    
def gen_metrics(dataframe, identity_val, key_met_cols, key_emp_cols, yr_val):
    
    dataframe_met = dataframe.copy()
    dataframe_met = dataframe_met.reset_index()

    dataframe_met = dataframe_met[(dataframe_met['yr'] == yr_val) & (dataframe_met['qtr'] == 5) & (dataframe_met['identity'] == identity_val)]
    dataframe_met = dataframe_met.set_index("identity")
    dataframe_met = dataframe_met[key_met_cols]
    dataframe_met = pd.DataFrame(dataframe_met.loc[identity_val]).transpose()
    for z in key_met_cols:
        dataframe_met[z] = dataframe_met[z].apply(lambda x: '' if pd.isnull(x) else x)
    
    dataframe_emp = dataframe.copy()
    dataframe_emp = dataframe_emp.reset_index()
    dataframe_emp = dataframe_emp[(dataframe_emp['yr'] == yr_val) & (dataframe_emp['qtr'] == 5) & (dataframe_emp['identity'] == identity_val)]
    dataframe_emp = dataframe_emp.set_index("identity")
    dataframe_emp = dataframe_emp[key_emp_cols]
    dataframe_emp = pd.DataFrame(dataframe_emp.loc[identity_val]).transpose()
    for z in key_emp_cols:
        dataframe_emp[z] = dataframe_emp[z].apply(lambda x: '' if pd.isnull(x) else x)

    rename_dict = {
                   'three_yr_avg_cons': '3yr_avgcons',
                   'curr_yr_trend_cons': 'trendcons', 
                   'implied_cons': 'imp_cons',
                   'std_dev_vac_chg': 'sd_vacchg',
                   'extra_used_act': 'p_abs_cons', 
                   'three_yr_avg_abs': '3yr_avgabs', 
                   'three_yr_avg_abs_nonc': '3yr_avgabs_nonc',
                   'total_trend_abs': 'trendabs', 
                   'implied_abs': 'imp_abs', 
                   'implied_rolsabs' : 'imp_abs_rol',
                   'hist_implied_abs': 'histimp_avgabs', 
                   'f_var_vac_chg': 'f_var_vacchg',
                   'avg_G_mrent_chg': 'avg_G_mrent',
                   'avg_G_mrent_chg_nonc': 'avg_G_mrent_nonc',
                   'std_dev_G_mrent_chg': 'sd_G_mrent',
                   'three_yr_avg_G_mrent': '3yr_avgGmrent',
                   'three_yr_avg_G_mrent_nonc': '3yr_avgGmrent_nonc',
                   'implied_G_mrent': 'imp_Gmrent',
                   'hist_implied_G_mrent': 'histimp_Gmrent', 
                   'implied_using_grolsmre': 'imp_Gmrent_rol', 
                   'total_trend_gap_chg': 'trendgapchg', 
                   'implied_gap_chg': 'imp_gapchg',
                   'implied_G_merent': 'imp_Gmerent', 
                   'three_yr_avg_emp_chg': '3yr_avg_empchg',
                   'implied_avg_inc_chg': 'imp_avginc_chg',
                   'implied_emp_chg': 'imp_empchg',
                   'implied_off_emp_chg': 'imp_offemp_chg',
                   'implied_ind_emp_chg': 'imp_indemp_chg'
                   }
    
    dataframe_met = dataframe_met.rename(columns=rename_dict)
    dataframe_emp = dataframe_emp.rename(columns=rename_dict)
    
    return dataframe_met, dataframe_emp

# This function calculates the implied vars on a met level
def get_met_implied(dataframe, curryr, currqtr):
    dataframe['identity_met'] = dataframe['metcode'] + dataframe['subsector']
    dataframe['total_trend_cons'] = dataframe[(dataframe['yr'] == curryr) & (dataframe['qtr'] != 5)].groupby('identity_met')['cons'].transform('sum')
    dataframe['total_trend_abs'] = dataframe[(dataframe['yr'] == curryr) & (dataframe['qtr'] != 5)].groupby('identity_met')['abs'].transform('sum')
    dataframe['implied_cons'] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5), dataframe['cons'] - dataframe['total_trend_cons'].shift(1), np.nan)
    dataframe['implied_abs'] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5), dataframe['abs'] - dataframe['total_trend_abs'].shift(1), np.nan)
    dataframe['implied_vac_chg'] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5), dataframe['vac'] - dataframe['vac'].shift(1), np.nan)
    dataframe['implied_G_mrent'] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5), (dataframe['askrent'] - dataframe['askrent'].shift(1)) / dataframe['askrent'].shift(1), np.nan)
    dataframe['implied_gap_chg'] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5), dataframe['gap'] - dataframe['gap'].shift(1), np.nan)

    return dataframe        

# This function creates the key vars for three year and five year rolls
def calc_subsequent(data_in, curryr, currqtr, sector_val, identity_val, year_val):
    dataframe = data_in.copy()
    dataframe['cons_roll'] = dataframe[(dataframe['yr'] > curryr - 1)].groupby(identity_val)['cons'].transform('sum')
    dataframe['vac_chg_roll'] = np.where((dataframe['yr'] == curryr + year_val - 1), dataframe['vac'] - dataframe['vac'].shift(year_val), np.nan)
    dataframe['abs_roll'] = np.where((dataframe['yr'] == curryr + year_val - 1), dataframe['occ'] - dataframe['occ'].shift(year_val), np.nan)
    if identity_val == "identity":
        dataframe['G_mrent_roll'] = np.where((dataframe['yr'] == curryr + year_val - 1), (dataframe['mrent'] - dataframe['mrent'].shift(year_val)) / dataframe['mrent'].shift(year_val), np.nan)
    else:
        dataframe['G_mrent_roll'] = np.where((dataframe['yr'] == curryr + year_val - 1), (dataframe['askrent'] - dataframe['askrent'].shift(year_val)) / dataframe['askrent'].shift(year_val), np.nan)
    dataframe['gap_chg_roll'] = np.where((dataframe['yr'] == curryr + year_val - 1), dataframe['gap'] - dataframe['gap'].shift(year_val), np.nan)

    dataframe = dataframe.drop(['cons', 'vac_chg', 'abs', 'G_mrent', 'gap_chg'], axis=1)
    for x in list(dataframe.columns):
        if "roll" in x:
            dataframe = dataframe.rename(columns={x: x[:-5]})

    dataframe = dataframe[dataframe['yr'] == curryr + year_val - 1]

    if identity_val == "identity":
        dataframe = dataframe[[identity_val, 'subsector', 'metcode', 'subid', 'yr', 'qtr', 'cons', 'vac_chg', 'abs', 'G_mrent', 'gap_chg']]
    else:
        dataframe = dataframe[[identity_val, 'subsector', 'metcode', 'yr', 'qtr', 'cons', 'vac_chg', 'abs', 'G_mrent', 'gap_chg']]

    return dataframe

# This function creates the rank table for key vars for subs within the met
def rank_it(rolled, data, roll_val, curryr, currqtr, sector_val, year_val):
    frames = []

    for x in ['identity', 'identity_met']:
        if x == "identity":
            rank = data.copy()
            #rank = rank[rank['identity_met'] == roll_val]
        elif x == "identity_met":
            rank = rolled.copy()
            rank = rank[rank['yr'] >= curryr - 1]
            if sector_val == "ind":
                if "DW" in roll_val:
                    rank = rank[rank['subsector'] == "DW"]
                else:
                    rank = rank[rank['subsector'] == "F"]
            if currqtr != 4 and year_val == "1.5":
                rank = get_met_implied(rank, curryr, currqtr)
            emp_data = data.copy()
            emp_data['join_ident'] = emp_data['metcode'] + emp_data['subsector'] + emp_data['yr'].astype(str) + emp_data['qtr'].astype(str)
            emp_data = emp_data.drop_duplicates('join_ident')
            emp_data = emp_data.set_index('join_ident')
            if sector_val == "apt" or sector_val == "ret":
                emp_data = emp_data[['emp_chg', 'implied_emp_chg']]
            elif sector_val == "off":
                emp_data = emp_data[['off_emp_chg', 'implied_off_emp_chg']]
            elif sector_val == "ind":
                emp_data = emp_data[['ind_emp_chg', 'implied_ind_emp_chg']]
            rank['join_ident'] = rank['metcode'] + rank['subsector'] + rank['yr'].astype(str) + rank['qtr'].astype(str)
            rank = rank.join(emp_data, on='join_ident')
            rank = rank.rename(columns={'ask_chg': 'G_mrent'})

        rank_filt = rank.copy()
        rank_filt = rank_filt[(rank_filt['yr'] >= curryr - 1) & (rank_filt['qtr'] == 5)]

        if currqtr != 4 and year_val == "1.5":
            calc_cols = ['implied_cons', 'implied_vac_chg', 'implied_abs', 'implied_G_mrent', 'implied_gap_chg']
            if sector_val == "apt" or sector_val == "ret":
                calc_cols += ['implied_emp_chg']
            elif sector_val == "off":
                calc_cols += ['implied_off_emp_chg']
            elif sector_val == "ind":
                calc_cols += ['implied_ind_emp_chg']
        else:
            calc_cols = ['cons', 'vac_chg', 'abs', 'G_mrent', 'gap_chg']
            if sector_val == "apt" or sector_val == "ret":
                calc_cols += ['emp_chg']
            elif sector_val == "off":
                calc_cols += ['off_emp_chg']
            elif sector_val == "ind":
                calc_cols += ['ind_emp_chg']
        
        if year_val == "1" or year_val == "1.5":
            rank_filt = rank_filt[rank_filt['yr'] == curryr]
        else:
            if year_val == "3":
                rank_filt = rank_filt[(rank_filt['yr'] >= curryr - 1) & (rank_filt['yr'] <= curryr + 2) & (rank_filt['qtr'] == 5)]
            elif year_val == "5":
                rank_filt = rank_filt[(rank_filt['yr'] >= curryr - 1) & (rank_filt['yr'] <= curryr + 4) & (rank_filt['qtr'] == 5)]
            if x == "identity_met":
                temp = data.copy()
                temp = temp[['identity_met', 'yr', 'qtr', 'occ']]
                temp['occ_roll'] = temp.groupby(['identity_met', 'yr', 'qtr'])['occ'].transform('sum')
                temp['temp_join'] = temp['identity_met'] + temp['yr'].astype(str) + temp['qtr'].astype(str)
                temp = temp.drop_duplicates('temp_join')
                temp = temp.set_index('temp_join')
                temp = temp[['occ_roll']]
                temp = temp.rename(columns={'occ_roll': 'occ'})
                rank_filt['temp_join'] = rank_filt['metcode'] + rank_filt['subsector'] + rank_filt['yr'].astype(str) + rank_filt['qtr'].astype(str)
                rank_filt = rank_filt.join(temp, on='temp_join')
            rank_filt['identity_met'] = rank_filt['metcode'] + rank_filt['subsector']
            rank_filt = calc_subsequent(rank_filt, curryr, currqtr, sector_val, x, math.floor(float(year_val)))
            
            emp_data = data.copy()
            emp_data['join_ident'] = emp_data['metcode'] + emp_data['subsector'] + emp_data['yr'].astype(str) + emp_data['qtr'].astype(str)
            emp_data = emp_data.drop_duplicates('join_ident')
            emp_data = emp_data.set_index('join_ident')
            if sector_val == "apt" or sector_val == "ret":
                emp_data = emp_data[['emp', 'yr']]
                emp_use = "emp"
            elif sector_val == "off":
                emp_data = emp_data[['off_emp', 'yr']]
                emp_use = "off_emp"
            elif sector_val == "ind":
                emp_data = emp_data[['ind_emp', 'yr']]
                emp_use = "ind_emp"
            emp_data['emp_chg_roll'] = np.where((emp_data['yr'] == curryr + math.floor(float(year_val)) - 1), (emp_data[emp_use] - emp_data[emp_use].shift(math.floor(float(year_val)))) / emp_data[emp_use].shift(math.floor(float(year_val))), np.nan)
            emp_data = emp_data[['emp_chg_roll']]
            if sector_val == "apt" or sector_val == "ret":
                emp_data = emp_data.rename(columns={'emp_chg_roll': 'emp_chg'})
            elif sector_val == "off":
                emp_data = emp_data.rename(columns={'emp_chg_roll': 'off_emp_chg'})
            elif sector_val == "ind":
                emp_data = emp_data.rename(columns={'emp_chg_roll': 'ind_emp_chg'})
            rank_filt['join_ident'] = rank_filt['metcode'] + rank_filt['subsector'] + rank_filt['yr'].astype(str) + rank_filt['qtr'].astype(str)
            rank_filt = rank_filt.join(emp_data, on='join_ident')

        rank_cols = []
        for y in calc_cols:
            col_name = y + "_rank"
            rank_cols.append(col_name)
            if "vac" in y or "gap" in y:
                sort_order = True
            else:
                sort_order = False
            rank_filt[col_name] = rank_filt[y].rank(ascending=sort_order, method='min')
            rank_filt[col_name] = rank_filt[col_name].astype(int)

        if x == "identity_met":
            rank_filt = rank_filt.drop_duplicates(['metcode'])
        
        rank_filt['identity_met'] = rank_filt['metcode'] + rank_filt['subsector']    
        
        rank_filt = rank_filt.set_index(x)
        if x == "identity_met":
            rank_filt = rank_filt[['metcode'] + rank_cols]
        else:
            rank_filt = rank_filt[['metcode', 'subid', 'identity_met'] + rank_cols]
        
        for z in list(rank_filt.columns):
            if "implied" in z:
                rank_filt = rank_filt.rename(columns={z: "imp_" + z[8:]})
        for z in list(rank_filt.columns): 
            if "_rank" in z:
                rank_filt = rank_filt.rename(columns={z: z[:-5]})
        for z in list(rank_filt.columns): 
            if "emp_chg" in z and "imp" not in z:
                rank_filt = rank_filt.rename(columns={z: "emp_chg"})
            elif "emp_chg" in z and "imp" in z:
                rank_filt = rank_filt.rename(columns={z: "imp_emp_chg"})
        
        temp = rank_filt.copy()
        temp = temp.reset_index()
        temp = temp[temp['identity_met'] == roll_val]
        rank_filt = rank_filt.reset_index()
        rank_filt = rank_filt[rank_filt['identity_met'] != roll_val]
        rank_filt = pd.concat([temp, rank_filt]).reset_index(drop=True)
        rank_filt = rank_filt.set_index(x)
        if x == "identity":
            rank_filt = rank_filt.drop(['identity_met'], axis=1)
       
        frames.append(rank_filt)

    return frames[0], frames[1]


    
# This function will roll up the data on a metro or national level for review based on the selection of metro by the user on the Rollups tab    
def rollup(dataframe, drop_val, curryr, currqtr, sector_val, filt_type, finalizer):
    roll = dataframe.copy()

    ind_expansion_list = ["AA", "AB", "AK", "AN", "AQ", "BD", "BF", "BI", "BR", "BS", "CG", "CM", "CN", "CS", "DC", 
                     "DM", "DN", "EP", "FC", "FM", "FR", "GD", "GN", "GR", "HR", "HL", "HT", "KX", "LL", "LO", 
                     "LR", "LV", "LX", "MW", "NF", "NM", "NO", "NY", "OK", "OM", "PV", "RE", "RO", "SC", "SH", 
                     "SR", "SS", "ST", "SY", "TC", "TM", "TO", "TU", "VJ", "VN", "WC", "WK", "WL", "WS"]

    if finalizer == True and drop_val[:2] == "US":
        if sector_val == "ind":
            roll = roll[~roll['metcode'].isin(ind_expansion_list)]
        else:
            roll = roll[~roll['metcode'].isin(["NO", "WS", "PV"])]
    
    if filt_type == "reg":
        if drop_val[:2] == "US":
            identity_filt = 'identity_us'
        else:
            identity_filt = 'identity_met'
    else:
        identity_filt = 'identity'
        roll = roll[roll[identity_filt] == drop_val]

    roll['askrevenue'] = roll['inv'] * roll['mrent']
    roll['effrevenue'] = roll['inv'] * roll['merent']
    roll['oobaskrevenue'] = roll['inv_oob'] * roll['mrent_oob']

    roll['rolsavail'] = roll['rolsinv'] * roll['rolsvac']
    if sector_val == "apt":
        roll['rolsavail'] = round(roll['rolsavail'], 0)
    else:
        roll['rolsavail'] = round(roll['rolsavail'], -3)

    roll['rolaskrevenue'] = roll['rolsinv'] * roll['rolmrent']
    roll['roleffrevenue'] = roll['rolsinv'] * roll['rolmerent']
    roll['oobeffrevenue'] = roll['inv_oob'] * roll['merent_oob']

    # With the addition of new submarkets in Q2 2020 that only have a trend history beginning in 2019, the year end row for 2019 for those subs is blank for abs, even though there is abs in every quarter period. 
    # Manually add the abs from the quarters to fill in the year end row so that the abs will be included on the metro rollup as it should be
    roll['abs'] = np.where((roll['yr'] == 2019) & (roll['qtr'] == 5) & np.isnan((roll['abs']) == True), roll['abs'].shift(1) + roll['abs'].shift(2) + roll['abs'].shift(3) + roll['abs'].shift(4), roll['abs'])

    if finalizer == False:
        roll = roll[(roll['yr'] >= curryr - 6)]
        roll = roll[(roll['qtr'] == 5) | (roll['yr'] >= curryr)]

    cols_to_roll = ['inv', 'rolsinv', 'inv_oob', 'cons', 'rolscon', 'cons_oob', 'avail', 'avail_oob', 'rolsavail', 'occ', 'abs', 'rolsabs', 'askrevenue', 'effrevenue', 'rolaskrevenue', 'roleffrevenue', 'oobaskrevenue', 'oobeffrevenue']
    if finalizer == True:
        cols_to_roll += ['h', 'rol_h', 'e', 't', 'demo', 'conv', 'abs_oob']
    
    roll[cols_to_roll] = roll.groupby([identity_filt, 'yr', 'qtr'])[cols_to_roll].transform('sum')

    
    if drop_val[:2] == "US":
        roll.sort_values(by=[identity_filt, 'yr', 'qtr'], ascending=[False, True, True], inplace=True)
    elif filt_type == "reg":
        if sector_val == "ind":
            roll.sort_values(by=['subsector', 'metcode', 'yr', 'qtr'], ascending=[True, True, True, True], inplace=True)
        else:
            roll.sort_values(by=['metcode', 'yr', 'qtr'], ascending=[True, True, True], inplace=True)
    
    if filt_type == "reg":
        if drop_val[:2] == "US":
            roll['drop_identity'] = roll['subsector'] + roll['yr'].astype(str) + roll['qtr'].astype(str)
        else:
            roll['drop_identity'] = roll['subsector'] + roll['metcode'] + roll['yr'].astype(str) + roll['qtr'].astype(str)
        roll = roll.drop_duplicates(subset="drop_identity")
    else:
        roll['drop_identity'] = roll['subsector'] + roll['metcode'] + roll['subid'].astype(str) + roll['yr'].astype(str) + roll['qtr'].astype(str)
        roll = roll.drop_duplicates(subset="drop_identity")
    
    if currqtr == 4:
        period = 1
    else:
        period = currqtr + 1

    roll['vac'] = round(roll['avail'] / roll['inv'], 4)
    roll['rolsvac'] = round(roll['rolsavail'] / roll['rolsinv'], 4)
    roll['vac_oob'] = round(roll['avail_oob'] / roll['inv_oob'], 4)
    
    def calc_chg(data_in, chg_name, var_name, identity_filt, sector_val):
        dataframe = data_in.copy()

        if 'vac' in var_name or 'gap' in var_name:
            dataframe[chg_name] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(periods=period)), dataframe[var_name] - dataframe[var_name].shift(periods=period), np.nan)
            dataframe[chg_name] = np.where((dataframe['yr'] > curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(1)), dataframe[var_name] - dataframe[var_name].shift(1), dataframe[chg_name])
            dataframe[chg_name] = np.where((dataframe['yr'] <= curryr) & (dataframe['qtr'] != 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(1)), dataframe[var_name] - dataframe[var_name].shift(1), dataframe[chg_name])
            dataframe[chg_name] = np.where((dataframe['yr'] < curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(5)) & (dataframe['qtr'].shift(5) == 5) & (dataframe['qtr'].shift(1) != 5), dataframe[var_name] - dataframe[var_name].shift(5), dataframe[chg_name])
            dataframe[chg_name] = np.where((dataframe['yr'] < curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(1)) & (dataframe['qtr'].shift(1) == 5), dataframe[var_name] - dataframe[var_name].shift(1), dataframe[chg_name])
        else:
            dataframe[chg_name] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(periods=period)), (dataframe[var_name] - dataframe[var_name].shift(periods=period)) / dataframe[var_name].shift(periods=period), np.nan)
            dataframe[chg_name] = np.where((dataframe['yr'] > curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(1)), (dataframe[var_name] - dataframe[var_name].shift(1)) / dataframe[var_name].shift(1), dataframe[chg_name])
            dataframe[chg_name] = np.where((dataframe['yr'] <= curryr) & (dataframe['qtr'] != 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(1)), (dataframe[var_name] - dataframe[var_name].shift(1)) / dataframe[var_name].shift(1), dataframe[chg_name])
            dataframe[chg_name] = np.where((dataframe['yr'] < curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(5)) & (dataframe['qtr'].shift(5) == 5) & (dataframe['qtr'].shift(1) != 5), (dataframe[var_name] - dataframe[var_name].shift(5)) / dataframe[var_name].shift(5), dataframe[chg_name])
            dataframe[chg_name] = np.where((dataframe['yr'] < curryr) & (dataframe['qtr'] == 5) & (dataframe[identity_filt] == dataframe[identity_filt].shift(1)) & (dataframe['qtr'].shift(1) == 5), (dataframe[var_name] - dataframe[var_name].shift(1)) / dataframe[var_name].shift(1), dataframe[chg_name])
        
        return dataframe

    roll = calc_chg(roll, 'vac_chg', 'vac', identity_filt, sector_val)
    roll = calc_chg(roll, 'rolsvac_chg', 'rolsvac', identity_filt, sector_val)
    roll = calc_chg(roll, 'vac_chg_oob', 'vac_oob', identity_filt, sector_val)
    
    roll['askrent'] = round(roll['askrevenue'] / roll['inv'],2)
    roll['effrent'] = round(roll['effrevenue'] / roll['inv'],2)
    roll['rolaskrent'] = round(roll['rolaskrevenue'] / roll['rolsinv'],2)
    roll['askrentoob'] = round(roll['oobaskrevenue'] / roll['inv'],2)
    roll['roleffrent'] = round(roll['roleffrevenue'] / roll['rolsinv'],2)
    roll['effrentoob'] = round(roll['oobeffrevenue'] / roll['inv'],2)
    
    roll = calc_chg(roll, 'ask_chg', 'askrent', identity_filt, sector_val)
    roll = calc_chg(roll, 'eff_chg', 'effrent', identity_filt, sector_val)
    roll = calc_chg(roll, 'rol_ask_chg', 'rolaskrent', identity_filt, sector_val)
    roll = calc_chg(roll, 'ask_chg_oob', 'askrentoob', identity_filt, sector_val)
    roll = calc_chg(roll, 'rol_eff_chg', 'roleffrent', identity_filt, sector_val)
    roll = calc_chg(roll, 'eff_chg_oob', 'effrentoob', identity_filt, sector_val)

    roll['gap'] = ((roll['effrent'] - roll['askrent']) / roll['askrent']) *-1
    roll['rolgap'] = ((roll['roleffrent'] - roll['rolaskrent']) / roll['rolaskrent']) *-1
    roll['gap_oob'] = ((roll['effrentoob'] - roll['askrentoob']) / roll['askrentoob']) *-1
    
    roll = calc_chg(roll, 'gap_chg', 'gap', identity_filt, sector_val)

    roll['cons'] = roll['cons'].astype(int)
    roll['rolscon'] = roll['rolscon'].astype(int)
    roll['cons_oob'] = roll['cons_oob'].astype(int)
    roll['abs'] = roll['abs'].astype(int)
    roll['rolsabs'] = roll['rolsabs'].astype(int)

    roll['first_trend'] = np.where(roll[identity_filt] != roll[identity_filt].shift(1), 1, 0) 
    roll['abs'] = np.where((roll['yr'] != curryr - 5) & (roll['first_trend'] == 1) & (roll['yr'] > curryr - 5), np.nan, roll['abs'])
    roll['rolsabs'] = np.where((roll['yr'] != curryr - 5) & (roll['first_trend'] == 1), np.nan, roll['rolsabs'])
    roll = roll.drop(['first_trend'], axis=1)

    if finalizer == False:
        if filt_type == "reg":
            cols_to_display = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'askrent', 'ask_chg', 'rol_ask_chg', 'effrent', 'eff_chg', 'rol_eff_chg', 'gap', 'gap_chg', 'rolaskrent']
        else:
            cols_to_display = ['subsector', 'metcode', 'subid', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'askrent', 'ask_chg', 'rol_ask_chg', 'effrent', 'eff_chg', 'rol_eff_chg', 'gap', 'gap_chg', 'rolaskrent']
        cols_to_display += ['cons_oob', 'vac_oob', 'vac_chg_oob', 'askrentoob', 'ask_chg_oob']
        if drop_val[:2] == "US":
            cols_to_display.remove('metcode')
            cols_to_display += ['identity_us']

        roll = roll[cols_to_display]
        roll = roll[(roll['yr'] >= curryr - 5)]

    elif finalizer == True:
        cols_to_display = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'occ', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'askrent', 'ask_chg', 'rol_ask_chg', 'effrent', 'eff_chg', 'rol_eff_chg', 'gap', 'gap_chg', 'rolgap', 'rolaskrent', 'roleffrent', 'cons_oob', 'vac_oob', 'vac_chg_oob', 'askrentoob', 'effrentoob', 'ask_chg_oob', 'eff_chg_oob', 'abs_oob', 'gap_oob']
        roll = roll[cols_to_display]

    roll['rolscon'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rolscon'])
    roll['rolsabs'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rolsabs'])
    roll['rolaskrent'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rolaskrent'])
    roll['rol_ask_chg'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rol_ask_chg'])
    if sector_val == "ind" or sector_val == "apt":
        roll['rol_eff_chg'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rol_eff_chg'])

    roll['rolscon'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolscon'])
    roll['rolsvac'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolsvac'])
    roll['rolsvac_chg'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolsvac_chg'])
    roll['rolsabs'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolsabs'])
    roll['rol_ask_chg'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rol_ask_chg'])
    roll['rol_eff_chg'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rol_eff_chg'])

    return roll

def live_flag_count(dataframe_in, sector_val):
    dataframe = dataframe_in.copy()
    r = re.compile("^._flag*")
    flag_cols = list(filter(r.match, dataframe.columns))
    dataframe[flag_cols] = np.where((dataframe[flag_cols] != 0) & (dataframe[flag_cols] != 999999999), 1, dataframe[flag_cols])
    dataframe[flag_cols] = np.where((dataframe[flag_cols] == 999999999), 0, dataframe[flag_cols])

    dataframe = dataframe[dataframe['forecast_tag'] != 0]
    
    dataframe['c_flag_tot_sub'] = dataframe.filter(regex="^c_flag*").sum(axis=1)
    dataframe['v_flag_tot_sub'] = dataframe.filter(regex="^v_flag*").sum(axis=1)
    dataframe['g_flag_tot_temp1'] = dataframe.filter(regex="^g_flag*").sum(axis=1)
    dataframe['g_flag_tot_temp2'] = dataframe.filter(regex="^e_flag*").sum(axis=1)
    dataframe['g_flag_tot_sub'] = dataframe['g_flag_tot_temp1'] + dataframe['g_flag_tot_temp2']
    dataframe = dataframe.drop(['g_flag_tot_temp1', 'g_flag_tot_temp2'], axis=1)
    
    c_left = dataframe['c_flag_tot_sub'].sum() -  dataframe['flag_skip'].str.count('c_flag').sum()
    v_left = dataframe['v_flag_tot_sub'].sum() - dataframe['flag_skip'].str.count('v_flag').sum()
    g_left = dataframe['g_flag_tot_sub'].sum() - dataframe['flag_skip'].str.count('g_flag').sum() - dataframe['flag_skip'].str.count('e_flag').sum()


    countdown_dict = {'Totals': [c_left, v_left, g_left]}
    countdown = pd.DataFrame.from_dict(countdown_dict, orient='index', columns=["Cons Flags", "Vac Flags", "Rent Flags"])
    
    return countdown

def summarize_flags_ranking(dataframe_in, type_filt):
    dataframe = dataframe_in.copy()
    dataframe = dataframe.reset_index()

    if type_filt == "met":
        filt_val = 'identity_met'
    elif type_filt == "sub":
        filt_val = 'identity'

    r = re.compile("^._flag*")
    flag_cols = list(filter(r.match, dataframe.columns))
    dataframe[flag_cols] = np.where((dataframe[flag_cols] != 0) & (dataframe[flag_cols] != 999999999), 1, dataframe[flag_cols])
    dataframe[flag_cols] = np.where((dataframe[flag_cols] == 999999999), 0, dataframe[flag_cols])

    dataframe = dataframe[dataframe['forecast_tag'] != 0]
    
    dataframe['c_flag_tot'] = dataframe.filter(regex="^c_flag*").sum(axis=1)
    dataframe['v_flag_tot'] = dataframe.filter(regex="^v_flag*").sum(axis=1)
    dataframe['g_flag_tot_temp1'] = dataframe.filter(regex="^g_flag*").sum(axis=1)
    dataframe['g_flag_tot_temp2'] = dataframe.filter(regex="^e_flag*").sum(axis=1)
    dataframe['g_flag_tot'] = dataframe['g_flag_tot_temp1'] + dataframe['g_flag_tot_temp2']

    dataframe['has_flag'] = np.where((dataframe['c_flag_tot'] != 0) | (dataframe['v_flag_tot'] != 0) | (dataframe['g_flag_tot'] != 0), 1, 0)    
    dataframe['sum_has_flag'] = dataframe.groupby(filt_val)['has_flag'].transform('sum')
    dataframe['total_fcast_rows'] = dataframe.groupby(filt_val)['identity_row'].transform('nunique')
    dataframe['% Fcast Rows W Flag'] = dataframe['sum_has_flag'] / dataframe['total_fcast_rows']
    if type_filt == "met":
        dataframe = dataframe[['subsector', 'metcode', '% Fcast Rows W Flag']]
        dataframe = dataframe.drop_duplicates(['subsector', 'metcode'])
    elif type_filt == "sub":
        dataframe = dataframe[['subsector', 'metcode', 'subid', '% Fcast Rows W Flag']]
        dataframe = dataframe.drop_duplicates(['subsector', 'metcode', 'subid'])
    dataframe = dataframe.sort_values(by=['% Fcast Rows W Flag'], ascending=False)
    dataframe = dataframe.iloc[:10]
    
    return dataframe
    
def summarize_flags(dataframe_in, sum_val):

    dataframe = dataframe_in.copy()
    dataframe = dataframe.reset_index()
    if sum_val[0:2] == "US":
        identity_filt = 'identity_us'
    else:
        identity_filt = 'identity_met'
    
    dataframe = dataframe[dataframe[identity_filt] == sum_val]

    r = re.compile("^._flag*")
    flag_cols = list(filter(r.match, dataframe.columns))
    dataframe[flag_cols] = np.where((dataframe[flag_cols] != 0) & (dataframe[flag_cols] != 999999999), 1, dataframe[flag_cols])
    dataframe[flag_cols] = np.where((dataframe[flag_cols] == 999999999), 0, dataframe[flag_cols])

    dataframe['c_flag_tot'] = dataframe.filter(regex="^c_flag*").sum(axis=1)
    dataframe['v_flag_tot'] = dataframe.filter(regex="^v_flag*").sum(axis=1)
    dataframe['g_flag_tot_temp1'] = dataframe.filter(regex="^g_flag*").sum(axis=1)
    dataframe['g_flag_tot_temp2'] = dataframe.filter(regex="^e_flag*").sum(axis=1)
    dataframe['g_flag_tot'] = dataframe['g_flag_tot_temp1'] + dataframe['g_flag_tot_temp2']

    dataframe['total_fcast_rows'] = dataframe.groupby(identity_filt)['identity_row'].transform('nunique')
    dataframe['total_subs'] = dataframe.groupby(identity_filt)['identity'].transform('nunique')

    for x  in ["c", "v", "g"]:
        dataframe[x + '_flag_sum'] = dataframe.groupby(identity_filt)[x + '_flag_tot'].transform('sum')
        
        dataframe['has_flag'] = np.where((dataframe[x + '_flag_tot'] != 0), 1, 0)    
        dataframe['sum_has_flag'] = dataframe.groupby(identity_filt)['has_flag'].transform('sum')
        dataframe[x + '_% Fcast Rows W Flag'] = dataframe['sum_has_flag'] / dataframe['total_fcast_rows']

        dataframe[x + '_sub_has_flag'] = dataframe[dataframe['has_flag'] == 1].groupby(identity_filt)['identity'].transform('nunique')
        dataframe[x + '_% Subs W Flag'] = dataframe[x + '_sub_has_flag'] / dataframe['total_subs']
        dataframe[x + '_% Subs W Flag'] = dataframe[x + '_% Subs W Flag'].fillna(method='ffill').fillna(method='bfill')
        dataframe[x + '_% Subs W Flag'] = dataframe[x + '_% Subs W Flag'].fillna(0)


    dataframe = dataframe.drop_duplicates(identity_filt)
    dataframe = dataframe.reset_index()

    input_dict = {
                    'Flag Type': ['Cons Flags', 'Vac Flags', 'Rent Flags'], 
                    'Total Flags': [dataframe['c_flag_sum'].loc[0], dataframe['v_flag_sum'].loc[0], dataframe['g_flag_sum'].loc[0]],
                    '% Fcast Rows W Flag': [dataframe['c_% Fcast Rows W Flag'].loc[0], dataframe['v_% Fcast Rows W Flag'].loc[0], dataframe['g_% Fcast Rows W Flag'].loc[0]],
                    '% Subs W Flag': [dataframe['c_% Subs W Flag'].loc[0], dataframe['v_% Subs W Flag'].loc[0], dataframe['g_% Subs W Flag'].loc[0]]
                  }
    
    dataframe_out = pd.DataFrame(input_dict)
    
    return dataframe_out


# Return a more verbose description of the flag to the user
def get_issue(dataframe, flag_list, flags_resolved, flags_unresolved, flags_new, flags_skipped, curryr, currqtr, preview_status, type_return, sector_val):

    # This dict holds a more verbose explanation of the flags, so that it can be printed to the user for clarity
    issue_descriptions = {
        "c_flag_comp": "Construction is below the total already completed in the trend periods.",
        "c_flag_h": "Construction is below the total h stock.",
        "c_flag_t": "Construction is above the total t stock.",
        "c_flag_sup": "Construction is not in line with the three year historical average or the three year rolling average for the submarket.",
        "c_flag_e": "Construction is not in line with the stock in the pipeline.",
        "c_flag_hist": "Construction is well below the typical construction level for this submarket.",
        "c_flag_rol": "Construction is different from ROL without a supporting change in the pipeline.",
        "c_flag_size": "Construction is lower than the average size of a typical building for this subsector.",
        "c_flag_lowv": "The overall forecast construction level series exhibits low variability compared to the general national submarket average.",   
        "v_flag_low": "The vacancy level is getting too low. We may need to forecast a slight correction to raise the vacancy level.",
        "v_flag_high": "The vacancy level is above 100 percent.",
        "v_flag_ratio": "The absorption construction ratio is either too high or too low.",
        "v_flag_roll": "A significant amount of Construction in the period 3 years prior to the flagged period remains unabsorbed.",
        "v_flag_improls": "The vacancy level changed from last period's forecast, and it caused a wider gap between implied absorption and the typical average absorption for this submarket.",
        "v_flag_rol": "The vacancy change is very different from ROL.",
        "v_flag_switch": "The absorption sentiment is in the opposite direction from ROL.",
        "v_flag_imp": "The vacancy level results in an implied absorption for the rest of the forecast period that is very different than the typical average absorption for this submarket.",
        "v_flag_z": "The vacancy change is not consistent with the historical vacancy change at the submarket.",
        "v_flag_min": "The vacancy level is below the 10 year historical minimum vacancy level for this submarket.",
        "v_flag_max": "The vacancy level is above the 10 year historical maximum vacancy level for this submarket.",
        "v_flag_lowv": "The overall forecast vacancy change series exhibits low variability compared to the general national submarket average.",
        "v_flag_level": "The vacancy level is not in line with the 10 year historical average.",
        "v_flag_3_trend": "The vacancy change is not in line with the three year historical average for the submarket.",
        "v_flag_exps": "The vacancy change does not seem to be properly weighting the more recent historical vacancy movements.",
        "v_flag_cons_neg": "There are three consecutive years of negative absorption in the submarket forecast.",
        "v_flag_subv": "The vacancy change has high variability accross the submarkets for the metro for this forecast year.",
        "v_flag_emp": "The vacancy change quartile is at the opposite end of the sector specific employment change quartile.",
        "g_flag_low": "Market rent change is very low.",
        "g_flag_nc": "Market rent change is low given the forecasted construction level.",
        "g_flag_z": "The magnitude of the market rent change is high based on the historical rent change at the submarket.",
        "g_flag_lowv": "The overall forecast market rent change series exhibits low variability compared to the general national submarket average.",
        "g_flag_highv": "The overall forecast market rent change series exhibits high variability compared to the general national submarket average.",
        "g_flag_max": "The market rent change is a new 10 year high for the submarket.",
        "g_flag_3_trend": "The market rent change is not in line with the three year historical average for the submarket.",
        "g_flag_improls": "The market rent change changed from last period's forecast, and it caused a a wider gap between implied market rent change and the typical average market rent change for this submarket.",
        "g_flag_imp": "The market rent change results in an implied market rent change for the rest of the forecast period that is very different than the typical average market rent change for this submarket.",
        "g_flag_rol": "The market rent change is very different from ROL.",
        "g_flag_yrdiff": "There is a large difference between this year's forecast for market rent change and the previous year's market rent change.",
        "g_flag_cons_low": "There are three consecutive years of low market rent change in the forecast for this submarket.",
        "g_flag_exps": "The market rent change does not seem to be properly weighting the more recent historical market rent movements.",
        "g_flag_vac": "The market rent change is moving in the opposite direction of vacancy change sentiment.",
        "g_flag_subv": "The market rent change has high variability accross the submarkets for the metro for this forecast year.",
        "g_flag_emp": "The market rent change quartile is at the opposite end of the sector specific employment change quartile.",
        "e_flag_rol": "The gap is very different from ROL and is not in line with vacancy change compared to ROL.",
        "e_flag_rolvac": "The gap has not changed significantly from ROL despite a significant change in vacancy relative to ROL.",
        "e_flag_zero": "The gap for the submarket is at zero or is negative.",
        "e_flag_max": "The gap level is a new 10 year high for the submarket.",
        "e_flag_min": "The gap level is a new 10 year low for the submarket.",
        "e_flag_min_chg": "The gap change is a new 10 year low for the submarket.",
        "e_flag_max_chg": "The gap change is a new 10 year high for the submarket.",
        "e_flag_improls": "The gap change is causing a wider difference between the expected gap change based on vacancy than if we had stuck with the ROL gap change.",
        "e_flag_imp": "The implied gap change is not in line with the implied vacancy change.",
        "e_flag_vac": "The gap change is moving in the opposite direction of vacancy change sentiment.",
        "e_flag_market": "The market rent and effective rent are moving in opposite directions.",
        "e_flag_emp": "The gap change quartile is at the opposite end of the sector specific employment change quartile."
    }

    if type_return == "specific":
        if flag_list[0] == "v_flag":
            issue_description_noprev = "No flags for this year at the submarket"
            issue_description_resolved = []
            issue_description_unresolved = []
            issue_description_new = []
            issue_description_skipped = []
        else:
            if preview_status == 0:
                issue_description_resolved = []
                issue_description_unresolved = []
                issue_description_new = []
                issue_description_skipped = []
                issue_description_noprev = html.Div([
                                        html.Div([
                                            dbc.Container(
                                            [
                                                dbc.Checklist(
                                                    id="flag_descriptions_noprev",
                                                    options=[
                                                            {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}"}
                                                            for i in flag_list
                                                            ],
                                                    inline=True, 
                                                            ),  
                                                    
                                            ]
                                            + [
                                                dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                for i in flag_list
                                            ],
                                            fluid=True),
                                                
                                        ]), 
                                    ])
            else:                
                issue_description_noprev = []
                if len(flags_resolved) > 0:
                    issue_description_resolved = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_resolved",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}", 'disabled': True}
                                                                for i in flags_resolved
                                                                ],
                                                        inline=True,
                                                        labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px', 'color': 'green'},
                                                                ),  
                                                        
                                                ]
                                                + [
                                                    dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                    for i in flags_resolved
                                                ],
                                                fluid=True),
                                                    
                                            ]), 
                                        ])
                else:
                    issue_description_resolved = []
                
                if len(flags_unresolved) > 0:
                    issue_description_unresolved = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_unresolved",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}"}
                                                                for i in flags_unresolved
                                                                ],
                                                        inline=True,
                                                        labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px', 'color': 'red'},
                                                                ),  
                                                        
                                                ]
                                                + [
                                                    dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                    for i in flags_unresolved
                                                ],
                                                fluid=True),
                                                    
                                            ]), 
                                        ])
                else:
                    issue_description_unresolved = []

                if len(flags_new) > 0:
                    issue_description_new = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_new",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}"}
                                                                for i in flags_new
                                                                ],
                                                        inline=True,
                                                        labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px', 'color': 'GoldenRod'},
                                                                ),  
                                                        
                                                ]
                                                + [
                                                    dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                    for i in flags_new
                                                ],
                                                fluid=True),
                                                    
                                            ]), 
                                        ])
                else:
                    issue_description_new = []

                if len(flags_skipped) > 0:
                    issue_description_skipped = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_skipped",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}"}
                                                                for i in flags_skipped
                                                                ],
                                                        value=[f"skip-{i}" for i in flags_skipped],
                                                        inline=True,
                                                        labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px', 'color': 'black'},
                                                                ),  
                                                        
                                                ]
                                                + [
                                                    dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                    for i in flags_skipped
                                                ],
                                                fluid=True),
                                                    
                                            ]), 
                                        ])
                else:
                    issue_description_skipped = []

        return issue_description_noprev, issue_description_resolved, issue_description_unresolved, issue_description_new, issue_description_skipped
    
    elif type_return == "list":
        return issue_descriptions

# Function that analyzes where edits are made in the display dataframe if manual edit option is selected
def get_diffs(shim_data, data_orig, data, drop_val, curryr, currqtr, sector_val):
    data_update = shim_data.copy()
    
    indexes = data_orig.index.values
    data_update['new_index'] = indexes
    data_update = data_update.set_index('new_index')

    diffs = data_update.where(data_update.values==data_orig.values).notna()
    diffs = data_update[~diffs]
    diffs = diffs.dropna(how='all')
    diffs = diffs.dropna(axis=1, how='all')

    if len(diffs) > 0:
        try:
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/coeffs/{}/{}q{}/coeffs.pickle".format(get_home(), sector_val, curryr, currqtr))
            coeff_data = pd.read_pickle(file_path)
            coeff_data = coeff_data.set_index("identity")
            data = data.join(coeff_data, on='identity')
            using_coeff = 1
        except:
            using_coeff = 0
        for index, row in diffs.iterrows():
            for col_name in list(diffs.columns):
                row_to_fix_diffs = index
                if math.isnan(row[col_name]) == False:
                    fix_val = row[col_name]
                    if col_name == "inv":
                        col_issue_diffs = "i_flag"
                    elif col_name == "cons":
                        col_issue_diffs = "c_flag"
                    elif col_name == "avail":
                        col_issue_diffs = "v_flag"
                    elif col_name == "mrent":
                        col_issue_diffs = "g_flag"
                    elif col_name == "merent":
                        col_issue_diffs = "e_flag"
                    yr_change_diffs = data.loc[row_to_fix_diffs]['yr']
                    
                    if using_coeff == 1:
                        data = insert_fix_coeffs(data, row_to_fix_diffs, drop_val, fix_val, col_issue_diffs[0], yr_change_diffs, curryr, currqtr, sector_val)
                    else:
                        data = insert_fix(data, row_to_fix_diffs, drop_val, fix_val, col_issue_diffs[0], yr_change_diffs, curryr, currqtr, sector_val)
        has_diff = 1
    else:
        has_diff = 0
   
    return data, has_diff

# Function to identify if a submarket has a flag for review
def flag_examine(data, identity_val, filt, curryr, currqtr, yr_val):

    dataframe = data.copy()
    if filt == True:
        dataframe = dataframe[dataframe['identity'] == identity_val]
        
    dataframe = dataframe[dataframe['forecast_tag'] != 0]

    r = re.compile("^._flag*")
    flag_cols = list(filter(r.match, dataframe.columns))
    cols_to_keep = flag_cols + ['identity', 'yr', 'flag_skip']
    dataframe = dataframe[cols_to_keep]
    dataframe[flag_cols] = np.where((dataframe[flag_cols] == 999999999), 0, dataframe[flag_cols])
    dataframe[flag_cols] = np.where((dataframe[flag_cols] > 0), 1, dataframe[flag_cols])
    
    if filt == False:
        dataframe['sum_commas'] = dataframe['flag_skip'].str.count(',')
        dataframe['sum_skips'] = np.where((dataframe['flag_skip'] == ''), 0, np.nan)
        dataframe['sum_skips'] = np.where((dataframe['flag_skip'] != ''), dataframe['sum_commas'] + 1, dataframe['sum_skips'])
        dataframe['total_skips'] = dataframe.groupby('identity')['sum_skips'].transform('sum')
    else:
        skips = dataframe.copy()
        skips = skips.reset_index()
        if len(dataframe) > 0:
            skip_list = str.split(skips.loc[skips.index[0]]['flag_skip'].replace(",", ""))
            skip_list = [x for x in skip_list if x[-4:] == str(yr_val)]
        else:
            skip_list = []
        dataframe['total_skips'] = np.nan
        dataframe.loc[identity_val + str(yr_val) + str(5), 'total_skips'] = len(skip_list)

    if filt == True:
        dataframe = dataframe[dataframe['yr'] == yr_val]
    dataframe['sum_flags'] = dataframe[flag_cols].sum(axis=1)
    dataframe['total_flags'] = dataframe.groupby('identity')['sum_flags'].transform('sum')
    
    dataframe['flags_left'] = dataframe['total_flags'] - dataframe['total_skips']
    dataframe = dataframe[dataframe['flags_left'] > 0]

    if len(dataframe) == 0:
        if filt == True:
            flag_list = ['v_flag']
    else:
        if filt == False:
            identity_val = dataframe.reset_index().loc[0]['identity']

            skips = dataframe.copy()
            skips = skips.reset_index()
            skip_list = str.split(skips.loc[skips.index[0]]['flag_skip'].replace(",", ""))
            
            
            testing_orig_yr_val = dataframe.copy()
            test_skip_list = [x for x in skip_list if x[-4:] == str(yr_val)]
            testing_orig_yr_val = testing_orig_yr_val[(testing_orig_yr_val['yr'] == yr_val) & (testing_orig_yr_val['identity'] == identity_val)]
            testing_orig_yr_val = testing_orig_yr_val[testing_orig_yr_val['sum_flags'] > len(test_skip_list)]
            if len(testing_orig_yr_val) == 0:
                new_yr = dataframe.copy()
                new_yr = new_yr[(new_yr['identity'] == identity_val) & (new_yr['sum_flags'] > 0)]
                yr_val = new_yr.reset_index().loc[0]['yr']
                
            dataframe = dataframe[dataframe['identity'] == identity_val]
            
            dataframe = dataframe[dataframe['yr'] == yr_val]
            

        flags = dataframe.copy()
        flags = flags[flag_cols + ['flag_skip']]
        flags = flags[flags.columns[(flags != 0).any()]]
        flag_list = list(flags.columns)
        flag_list = [x for x in flag_list if x + str(yr_val) not in skip_list]
        flag_list.remove('flag_skip')
        
        if len(flag_list) == 0:
            if filt == True:
                flag_list = ['v_flag']
                identity_val = identity_val
            else: 
                flag_list = ['v_flag']
        
    return flag_list, identity_val, yr_val

def reset_subsequent_years(dataframe, row_to_fix, identity_val, variable_fix, yr_change, period, sector_val):
    if sector_val == "apt":
        a_round_val = 0
        m_round_val = 2
    else:
        a_round_val = -3
        m_round_val = 2
    loop_df = dataframe.copy()
    prev_occ = loop_df.loc[row_to_fix]['occ']
    loop_df = loop_df.set_index("identity")
    loop_df = loop_df.loc[identity_val]
    loop_df = loop_df[loop_df['yr'] > yr_change]
    count_loop = 1
    for index, row in loop_df.iterrows():
        if variable_fix == "c":
            new_avail = (row['abs'] + prev_occ - row['inv']) * -1
            dataframe['avail'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), new_avail, dataframe['avail'])
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])
            prev_occ = dataframe.loc[identity_val + str(yr_change + count_loop) + '5']['occ']
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(1), dataframe['abs'])
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(1), dataframe['vac_chg'])
        
        elif variable_fix == "v":
            new_avail_test = (row['abs'] + prev_occ - row['inv']) * -1
            new_avail_test = round(new_avail_test, a_round_val)
            if new_avail_test < 0:
                new_avail = 0
            else:
                new_avail = new_avail_test
            dataframe['avail'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), new_avail, dataframe['avail'])
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])
            prev_occ = dataframe.loc[identity_val + str(yr_change + count_loop) + '5']['occ']
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(1), dataframe['abs'])
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(1), dataframe['vac_chg'])
        
        elif variable_fix == "g" or variable_fix == "e":
            if variable_fix == "g":
                ren_var = 'mrent'
                g_ren_var = 'G_mrent'
            elif variable_fix == "e":
                ren_var = 'merent'
                g_ren_var = 'G_merent'
            for index, row in loop_df.iterrows():
                dataframe[ren_var] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), ((dataframe[g_ren_var] * dataframe.shift(1)[ren_var]) + dataframe.shift(1)[ren_var]), dataframe[ren_var])
                if variable_fix == "g":
                    dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'].shift(1) * (1 + dataframe['G_mrent'])), 4), dataframe['mrent'])
                    dataframe['mrent'] = round(dataframe['mrent'], m_round_val)
                    dataframe['merent'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'] * (dataframe['gap'] * -1)) + dataframe['mrent'], 4), dataframe['merent'])
                    dataframe['merent'] = round(dataframe['merent'], m_round_val)
                    dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(1)) / dataframe['merent'].shift(1), 4), dataframe['G_merent'])
                    dataframe['G_merent'] = round(dataframe['G_merent'], 4)
                elif variable_fix == "e":
                    dataframe['merent'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'].shift(1) * (1 + dataframe['G_merent'])), 4), dataframe['merent'])
                    dataframe['merent'] = round(dataframe['merent'], m_round_val)
                    dataframe['gap'] = np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(((dataframe['merent'] - dataframe['mrent']) / dataframe['mrent']) * -1, 4), dataframe['gap'])
                    dataframe['gap_chg'] =  np.where((dataframe['yr'] == yr_change + count_loop) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap'] - dataframe['gap'].shift(1), dataframe['gap_chg'])
                    dataframe['gap'] = round(dataframe['gap'], 4) 


        count_loop += 1
        
    return dataframe


# Function to insert the suggested or user fix to the fixed dataframe for review by user, as originally formatted by BB before HSY suggestion of using model coefficients directly
def insert_fix(dataframe, row_to_fix, identity_val, fix, variable_fix, yr_change, curryr, currqtr, sector_val):
    
    if sector_val == "apt":
        a_round_val = 0
        m_round_val = 0
    else: 
        a_round_val = -3
        m_round_val = 2

    
    for x in range(0, (10 - (yr_change - curryr))):
        index_val = identity_val + str(yr_change + x) + "5"
        
        if yr_change > curryr or x > 0 or currqtr == 4:
            period = 1
        else:
            period = currqtr + 1
     
        if variable_fix == "c":
            if x == 0:
                orig_cons = dataframe.loc[row_to_fix]['cons']
                cons_diff = fix - orig_cons
                dataframe.loc[row_to_fix, 'cons'] = fix
            
            dataframe['inv'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] + cons_diff, dataframe['inv'])
            dataframe['inv'] = dataframe['inv'].astype(int)
        
            if math.isnan(dataframe.loc[index_val]['avg_abs_cons']) == True:
                avg_abs_cons = 0.6
            elif dataframe.loc[index_val]['avg_abs_cons'] > 1:
                avg_abs_cons = 1
            else:
                avg_abs_cons = dataframe.loc[index_val]['avg_abs_cons']
            
            if cons_diff > 0:
                avail_add = cons_diff * (1-avg_abs_cons)
            elif cons_diff < 0:
                orig_abs = dataframe.loc[index_val]['abs']
                orig_abs_cons_r = dataframe.loc[index_val]['abs_cons_r']
                if orig_abs_cons_r >= 1:
                    avail_add = cons_diff
                elif orig_abs_cons_r >= 0:
                    avail_add = cons_diff * orig_abs_cons
                else:
                    avail_add = cons_diff * avg_abs_cons
            if x == 0:
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['avail'] + avail_add, dataframe['avail'])
            else:
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['abs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1, dataframe['avail'])
            dataframe['avail'] = round(dataframe['avail'], a_round_val)
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(periods=period), dataframe['abs'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])
            
        elif variable_fix == "v":
            if x == 0:
                orig_avail = dataframe.loc[row_to_fix]['avail']
                avail_diff = fix - orig_avail
                dataframe.loc[row_to_fix, 'avail'] = fix
            else:
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe['abs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 >= 0) & ((dataframe['abs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 <= dataframe['inv']), (dataframe['abs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1, dataframe['avail'])
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe['abs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 < 0), dataframe['avail'].shift(periods=period), dataframe['avail'])
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe['abs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 > dataframe['inv']), dataframe['avail'].shift(periods=period), dataframe['avail'])
            dataframe['avail'] = round(dataframe['avail'], a_round_val)
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(periods=period), dataframe['abs'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])
                
        elif variable_fix == "g":
            if x == 0:
                dataframe.loc[row_to_fix, 'mrent'] = fix
            dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'] - dataframe['mrent'].shift(periods=period)) / dataframe['mrent'].shift(periods=period), 4), dataframe['G_mrent'])
            dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'] * (dataframe['gap'] * -1)) + dataframe['mrent'], 4), dataframe['merent'])
            dataframe['merent'] = round(dataframe['merent'], m_round_val)
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), 4), dataframe['G_merent'])        
    
        elif variable_fix == "e":
            if x == 0:
                dataframe.loc[row_to_fix, 'merent'] = fix   
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), 4), dataframe['G_merent'])
            dataframe['gap'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(((dataframe['merent'] - dataframe['mrent']) / dataframe['mrent']) * -1, 4), dataframe['gap'])
            dataframe['gap_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap'] - dataframe['gap'].shift(periods=period), dataframe['gap_chg'])
    
    return dataframe

# Function to insert the suggested or user fix to the fixed dataframe for review by user based on oob model coefficients
def insert_fix_coeffs(dataframe, row_to_fix, identity_val, fix, variable_fix, yr_change, curryr, currqtr, sector_val):

    # Cap the inv_chg_to_vac coeff at minimum of zero, since it doesnt really make sense to say that a decrease in inventory will have a predictive effect on vac
    # Likely there are negative coeffs because of demos/conversions
    dataframe['inv_chg_to_vac'] == np.where(dataframe['inv_chg_to_vac'] < 0, 0, dataframe['inv_chg_to_vac'])

    if sector_val == "apt":
        a_round_val = 0
        m_round_val = 0
    else: 
        a_round_val = -3
        m_round_val = 2
    
    cons_diff = fix - dataframe.loc[row_to_fix]['cons']
     
    for x in range(0, (10 - (yr_change - curryr))):
        index_val = identity_val + str(yr_change + x) + "5"
        
        if yr_change > curryr or x > 0 or currqtr == 4:
            period = 1
        else:
            period = currqtr + 1
        
        if variable_fix == "c":

            # Insert the user edit for cons
            if x == 0:
                dataframe.loc[row_to_fix, 'cons'] = fix

            # Recalculate the inventory level for all year rows based on the change in cons
            if x == 0:
                dataframe['inv'] = np.where((dataframe['yr'] >= yr_change) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] + cons_diff, dataframe['inv'])
                dataframe['inv'] = dataframe['inv'].astype(int)

            # Adjust vac chg using the coefficients that affect vac, and calculate the new vac level once we have the new vac chg
            total_effect = 0
            total_effect += ((dataframe.loc[index_val]['cons'] - dataframe.loc[index_val]['cons_oob']) / dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['inv']) * dataframe.loc[index_val]['inv_chg_to_vac']
            if x > 0:
                total_effect += (dataframe.loc[index_val]['vac'] - dataframe.loc[index_val]['vac_oob']) * dataframe.loc[index_val]['vac_level_to_vac']
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac_oob'] + total_effect, dataframe['vac'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])

            # Calculate the new avail stock based on the new vac level and new inventory level
            dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] * dataframe['vac'], dataframe['avail'])
            dataframe['avail'] = round(dataframe['avail'], a_round_val)
            
            # Recalc vac and vac_chg to avoid rounding descrepency with avail stock
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])
            
            # Calculate the new occ stock based on the new vac level and inventory level
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])

            # Calculate the new abs and vac chg based on the new vac level and occupancy level
            
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(periods=period), dataframe['abs'])
            
            # Adjust the market rent growth using the coefficients that affect rent, and claculate the new market rent level once we have the new market rent chg
            total_effect = 0
            total_effect += ((dataframe.loc[index_val]['cons'] - dataframe.loc[index_val]['cons_oob']) / dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['inv']) * dataframe.loc[index_val]['inv_chg_to_rent']
            total_effect += (((1 - dataframe.loc[index_val]['vac']) - (1 - dataframe.loc[index_val]['vac_oob'])) / (1 - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['vac'])) * dataframe.loc[index_val]['occ_chg_to_rent']
            if x > 0:
                total_effect += (np.log(dataframe.loc[index_val]['inv']) - np.log(dataframe.loc[index_val]['inv_oob'])) * dataframe.loc[index_val]['inv_lchg_to_rent']
                total_effect += (np.log((1 - dataframe.loc[index_val]['vac'])) - np.log((1 - dataframe.loc[index_val]['vac_oob']))) * dataframe.loc[index_val]['occ_lchg_to_rent']
                total_effect += (np.log(dataframe.loc[index_val]['mrent']) - np.log(dataframe.loc[index_val]['mrent_oob'])) * dataframe.loc[index_val]['rent_lchg_to_rent']
            dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['G_mrent_oob'] + total_effect, dataframe['G_mrent'])
            dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (1+ dataframe['G_mrent']) * dataframe['mrent'].shift(periods=period), dataframe['mrent'])
            dataframe['mrent'] = round(dataframe['mrent'], m_round_val)

            # Adjust the gap level using the coefficients that affect gap level
            total_effect = 0
            total_effect += ((dataframe.loc[index_val]['cons'] - dataframe.loc[index_val]['cons_oob']) / dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['inv']) * dataframe.loc[index_val]['inv_chg_to_gap']
            total_effect += (((1 - dataframe.loc[index_val]['vac']) - (1 - dataframe.loc[index_val]['vac_oob'])) / (1 - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['vac'])) * dataframe.loc[index_val]['occ_chg_to_gap']
            if x > 0:
                total_effect += (np.log(dataframe.loc[index_val]['inv']) - np.log(dataframe.loc[index_val]['inv_oob'])) * dataframe.loc[index_val]['inv_lchg_to_gap']
                total_effect += (np.log((1 - dataframe.loc[index_val]['vac'])) - np.log((1 - dataframe.loc[index_val]['vac_oob']))) * dataframe.loc[index_val]['occ_lchg_to_gap']
                total_effect += (dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['gap'] - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['gap_oob']) * dataframe.loc[index_val]['gap_level_to_gap']
            dataframe['gap'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap_oob'] + total_effect, dataframe['gap'])
            dataframe['gap'] - round(dataframe['gap'], 4)
           
            # Recalculate the gap chg based on the new gap level
            dataframe['gap_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap'] - dataframe['gap'].shift(periods=period), dataframe['gap_chg'])

            # Recalculate the effective rent level based on the new mrent level and new gap level
            dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), ((dataframe['gap'] * dataframe['mrent']) * -1) + dataframe['mrent'], dataframe['merent'])
            dataframe['merent'] = round(dataframe['merent'], m_round_val)

            # Recalculate G_merent now that we have the new effective rent level
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), 4), dataframe['G_merent']) 
        
        elif variable_fix == "v":
            
            # Insert the user edit for avail
            if x == 0:
                dataframe.loc[row_to_fix, 'avail'] = fix
            
            # Recalculate the vacancy level based on the new avail stock if this is the row to fix, and calculate the new vacancy change
            if x == 0:
                dataframe['vac'] = np.where((dataframe['yr'] == yr_change) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['avail'] / dataframe['inv'], dataframe['vac'])
                dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])

            # Adjust vac chg using the coefficients that affect vac, and calculate the new vac level once we have the new vac chg
            if x > 0:
                total_effect = 0
                total_effect += (dataframe.loc[index_val]['vac'] - dataframe.loc[index_val]['vac_oob']) * dataframe.loc[index_val]['vac_level_to_vac']
                dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac_oob'] + total_effect, dataframe['vac'])
                dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])

                # Calculate the new avail stock based on the new vac level
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] * dataframe['vac'], dataframe['avail'])
                dataframe['avail'] = round(dataframe['avail'], a_round_val)
            
                # Recalc vac and vac_chg to avoid rounding descrepency with avail stock
                dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['avail'] / dataframe['inv'], dataframe['vac'])
                dataframe['vac'] = round(dataframe['vac'], 4)
                dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])
            
            # Recalculate the new occ stock based on the new avail stock
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])
            
            # Adjust abs based on the new occ stock
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(periods=period), dataframe['abs'])
            
            # Adjust the market rent growth using the coefficients that affect rent, and claculate the new market rent level once we have the new market rent chg
            total_effect = 0
            total_effect += (((1 - dataframe.loc[index_val]['vac']) - (1 - dataframe.loc[index_val]['vac_oob'])) / (1 - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['vac'])) * dataframe.loc[index_val]['occ_chg_to_rent']
            if x > 0:
                total_effect += (np.log(1 - dataframe.loc[index_val]['vac']) - np.log(1 - dataframe.loc[index_val]['vac_oob'])) * dataframe.loc[index_val]['occ_lchg_to_rent']
            if x > 1:
                total_effect += (np.log(dataframe.loc[index_val]['mrent']) - np.log(dataframe.loc[index_val]['mrent_oob'])) * dataframe.loc[index_val]['rent_lchg_to_rent']
            dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['G_mrent_oob'] + total_effect, dataframe['G_mrent'])
            dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (1+ dataframe['G_mrent']) * dataframe['mrent'].shift(periods=period), dataframe['mrent'])
            dataframe['mrent'] = round(dataframe['mrent'], m_round_val)

            # Adjust the gap level using the coefficients that affect it
            total_effect = 0
            total_effect += (((1 - dataframe.loc[index_val]['vac']) - (1 - dataframe.loc[index_val]['vac_oob'])) / (1 - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['vac'])) * dataframe.loc[index_val]['occ_chg_to_gap']
            if x > 0:
                total_effect += (np.log((1 - dataframe.loc[index_val]['vac'])) - np.log((1 - dataframe.loc[index_val]['vac_oob']))) * dataframe.loc[index_val]['occ_lchg_to_gap']
                total_effect += (dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['gap'] - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['gap_oob']) * dataframe.loc[index_val]['gap_level_to_gap']
            dataframe['gap'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap_oob'] + total_effect, dataframe['gap'])
            dataframe['gap'] - round(dataframe['gap'], 4)

            # Recalculate the gap chg based on the new gap level
            dataframe['gap_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap'] - dataframe['gap'].shift(periods=period), dataframe['gap_chg'])

            # Recalculate the effective rent level based on the new mrent level and new gap level
            dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), ((dataframe['gap'] * dataframe['mrent']) * -1) + dataframe['mrent'], dataframe['merent'])
            dataframe['merent'] = round(dataframe['merent'], m_round_val)

            # Recalculate G_merent now that we have the new effective rent level
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), 4), dataframe['G_merent'])
        
        elif variable_fix == "g":
            
            # Insert the user edit for market rent
            if x == 0:
                dataframe.loc[row_to_fix, 'mrent'] = fix

            # Adjust the market rent growth if this is the row with the fix based on the new rent level
            if x == 0:
                dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['mrent'] - dataframe['mrent'].shift(periods=period)) / dataframe['mrent'].shift(periods=period), dataframe['G_mrent'])
            
            # Adjust the market rent growth using the coefficients that affect rent, and calculate the new market rent level once we have the new market rent chg
            if x > 0:
                total_effect = 0
                total_effect += (np.log(dataframe.loc[index_val]['mrent']) - np.log(dataframe.loc[index_val]['mrent_oob'])) * dataframe.loc[index_val]['rent_lchg_to_rent']
                dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['G_mrent_oob'] + total_effect, dataframe['G_mrent'])
                dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (1+ dataframe['G_mrent']) * dataframe['mrent'].shift(periods=period), dataframe['mrent'])
                dataframe['mrent'] = round(dataframe['mrent'], m_round_val)

         
            # Recalculate the effective rent level to maintain the original gap level due to the change in market rent level
            dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['mrent'] * (dataframe['gap'] * -1)) + dataframe['mrent'], dataframe['merent'])
            dataframe['merent'] = round(dataframe['merent'], m_round_val)

            # Recalculate gmerent based on the new effective rent level
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), dataframe['G_merent'])        
        
        elif variable_fix == "e":
            
            # Insert the user edit to effective rent level
            if x == 0:
                dataframe.loc[row_to_fix, 'merent'] = fix
            
            # Adjust the effective rent growth and gap if this is the row with the fix based on the new erent level
            if x == 0:
                dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), dataframe['G_merent'])
                dataframe['gap'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), ((dataframe['merent'] - dataframe['mrent']) / dataframe['mrent']) * -1, dataframe['gap'])
            
            # Recalculate the gap in subsequent years based on the change in gap level coeff, and calculate the new erent level and erent growth once we have the new gap
            if x > 0:
                total_effect = 0
                total_effect += (dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['gap'] - dataframe.loc[identity_val + str(yr_change - 1 + x) + "5"]['gap_oob']) * dataframe.loc[index_val]['gap_level_to_gap']
                dataframe['gap'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap_oob'] + total_effect, dataframe['gap'])
                dataframe['gap'] - round(dataframe['gap'], 4)

                dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['gap'] * dataframe['mrent'] * -1) + dataframe['mrent'], dataframe['merent'])
                dataframe['merent'] = round(dataframe['merent'], m_round_val)

                dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), dataframe['G_merent'])

            # Recalculate the gap change based on the change in gap level
            dataframe['gap_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['identity'] == identity_val) & (dataframe['qtr'] == 5), dataframe['gap'] - dataframe['gap'].shift(periods=period), dataframe['gap_chg'])

    return dataframe