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
def set_display_cols(dataframe_in, identity_val, sector, curryr, currqtr, key_met_val, yr_val, message):
    dataframe = dataframe_in.copy()
    if key_met_val == False:
        key_met_val = "v"
        
    display_cols = ['identity_row', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'h', 'rol_h', 'e', 'rol_e', 't', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'occ', 'avail', 'abs', 'rolsabs', 'mrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rolsgap_chg']

    if "market rent" in message:
        display_cols.insert(20, 'rolmrent')
    elif "effective rent" in message:
        display_cols.insert(24, 'rolmerent')

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
        key_met_cols = ['min_gap', 'min_gap_chg', 'max_gap', 'max_gap_chg', 'gap_5', 'gap_95', 'implied_gap_chg', 'implied_G_merent', 'gap_quart', 'implied_vac_chg', 'f_var_gap_chg']
    
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
                   'implied_gap_chg': 'imp gap chg',
                   'implied_G_merent': 'imp_Gmerent', 
                   'three_yr_avg_emp_chg': '3yr_avg_empchg',
                   'implied_avg_inc_chg': 'imp_avginc_chg',
                   'implied_emp_chg': 'imp emp chg',
                   'implied_off_emp_chg': 'imp_offemp_chg',
                   'implied_ind_emp_chg': 'imp_indemp_chg',
                   'implied_vac_chg': 'imp vac chg'
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
    dataframe['implied_G_mrent'] = np.where((dataframe['yr'] == curryr) & (dataframe['qtr'] == 5), (dataframe['mrent'] - dataframe['mrent'].shift(1)) / dataframe['mrent'].shift(1), np.nan)
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
        dataframe['G_mrent_roll'] = np.where((dataframe['yr'] == curryr + year_val - 1), (dataframe['mrent'] - dataframe['mrent'].shift(year_val)) / dataframe['mrent'].shift(year_val), np.nan)
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
def metro_sorts(rolled, data, roll_val, curryr, currqtr, sector_val, year_val):
    frames = []

    for x in ['identity', 'identity_met']:
        if x == "identity":
            rank = data.copy()
            
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

        # rank_cols = [col +"_rank" for col in calc_cols]
        # for var, name in zip(calc_cols, rank_cols):
        #     if "vac" in var or "gap" in var:
        #         sort_order = True
        #     else:
        #         sort_order = False
        #     rank_filt[name] = rank_filt[var].rank(ascending=sort_order, method='min')
        #     rank_filt[name] = rank_filt[name].astype(int)

        if x == "identity_met":
            rank_filt = rank_filt.drop_duplicates(['metcode'])
            
        rank_filt['identity_met'] = rank_filt['metcode'] + rank_filt['subsector']    
        
        rank_filt = rank_filt.set_index(x)
        if x == "identity_met":
            rank_filt = rank_filt[['metcode'] + calc_cols]
        else:
            rank_filt = rank_filt[['metcode', 'subid', 'identity_met'] + calc_cols]
        
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
        
        if year_val != "1.5":
            rank_filt.sort_values(by=['cons'], ascending=[False], inplace=True)
        else:
            rank_filt.sort_values(by=['imp_cons'], ascending=[False], inplace=True)
        
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
    
    if filt_type == "reg" or filt_type == "graph":
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
    elif filt_type == "reg" or filt_type == "graph":
        if sector_val == "ind":
            roll.sort_values(by=['subsector', 'metcode', 'yr', 'qtr'], ascending=[True, True, True, True], inplace=True)
        else:
            roll.sort_values(by=['metcode', 'yr', 'qtr'], ascending=[True, True, True], inplace=True)
    
    if filt_type == "reg" or filt_type == "graph":
        if drop_val[:2] == "US":
            if finalizer == True:
                roll['drop_identity'] = roll['subsector'] + roll['yr'].astype(str) + roll['qtr'].astype(str)
            else:
                roll['drop_identity'] = roll['identity_us'] + roll['yr'].astype(str) + roll['qtr'].astype(str)
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
    
    roll['mrent'] = round(roll['askrevenue'] / roll['inv'],2)
    roll['merent'] = round(roll['effrevenue'] / roll['inv'],2)
    roll['rol_mrent'] = round(roll['rolaskrevenue'] / roll['rolsinv'],2)
    roll['mrent_oob'] = round(roll['oobaskrevenue'] / roll['inv'],2)
    roll['rol_merent'] = round(roll['roleffrevenue'] / roll['rolsinv'],2)
    roll['merent_oob'] = round(roll['oobeffrevenue'] / roll['inv'],2)
    
    roll = calc_chg(roll, 'G_mrent', 'mrent', identity_filt, sector_val)
    roll = calc_chg(roll, 'G_merent', 'merent', identity_filt, sector_val)
    roll = calc_chg(roll, 'grolsmre', 'rol_mrent', identity_filt, sector_val)
    roll = calc_chg(roll, 'G_mrent_oob', 'mrent_oob', identity_filt, sector_val)
    roll = calc_chg(roll, 'grolsmer', 'rol_merent', identity_filt, sector_val)
    roll = calc_chg(roll, 'G_merent_oob', 'merent_oob', identity_filt, sector_val)

    roll['gap'] = ((roll['merent'] - roll['mrent']) / roll['mrent']) *-1
    roll['rolgap'] = ((roll['rol_merent'] - roll['rol_mrent']) / roll['rol_mrent']) *-1
    roll['gap_oob'] = ((roll['merent_oob'] - roll['mrent_oob']) / roll['mrent_oob']) *-1
    
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

    if currqtr != 4 and finalizer == False and filt_type == "graph":
        roll['curr_yr_trend_cons'] = roll[(roll['yr'] == curryr) & (roll['qtr'] <= currqtr)].groupby('identity_met')['cons'].transform('sum')
        roll['implied_cons'] = np.where((roll['yr'] == curryr) & (roll['qtr'] == 5), roll['cons'] - roll['curr_yr_trend_cons'], np.nan)
        roll['implied_vac_chg'] = np.where((roll['yr'] == curryr) & (roll['qtr'] == 5), roll['vac'] - roll['vac'].shift(1), np.nan)
        roll['implied_G_mrent'] = np.where((roll['yr'] == curryr) & (roll['qtr'] == 5), (roll['mrent'] - roll['mrent'].shift(1)) / roll['mrent'].shift(1), np.nan)
        roll['implied_gap_chg'] = np.where((roll['yr'] == curryr) & (roll['qtr'] == 5), roll['gap'] - roll['gap'].shift(1), np.nan)
        roll = roll.drop(['curr_yr_trend_cons'], axis=1)

    if finalizer == False:
        if filt_type == "reg":
            cols_to_display = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'mrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rol_mrent']
        elif filt_type == "graph":
            cols_to_display = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'mrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rol_mrent', 'implied_cons', 'implied_vac_chg', 'implied_G_mrent', 'implied_gap_chg']
        else:
            cols_to_display = ['subsector', 'metcode', 'subid', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'mrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rol_mrent']
        cols_to_display += ['cons_oob', 'vac_oob', 'vac_chg_oob', 'mrent_oob', 'G_mrent_oob']
        if drop_val[:2] == "US":
            cols_to_display.remove('metcode')
            cols_to_display += ['identity_us']

        if currqtr == 4 and filt_type == 'graph':
            cols_to_display.remove('implied_cons')
            cols_to_display.remove('implied_vac_chg')
            cols_to_display.remove('implied_G_mrent')
            cols_to_display.remove('implied_gap_chg')

        roll = roll[cols_to_display]
        roll = roll[(roll['yr'] >= curryr - 5)]

    elif finalizer == True:
        cols_to_display = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'occ', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'mrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rolgap', 'rol_mrent', 'rol_merent', 'cons_oob', 'vac_oob', 'vac_chg_oob', 'mrent_oob', 'merent_oob', 'G_mrent_oob', 'G_merent_oob', 'abs_oob', 'gap_oob', 'avail']
        roll = roll[cols_to_display]

    roll['rolscon'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rolscon'])
    roll['rolsabs'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rolsabs'])
    roll['rol_mrent'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['rol_mrent'])
    roll['grolsmre'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['grolsmre'])
    if sector_val == "ind" or sector_val == "apt":
        roll['grolsmer'] = np.where((roll['yr'] == curryr + 9) & (currqtr == 4), np.nan, roll['grolsmer'])

    roll['rolscon'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolscon'])
    roll['rolsvac'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolsvac'])
    roll['rolsvac_chg'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolsvac_chg'])
    roll['rolsabs'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['rolsabs'])
    roll['grolsmre'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['grolsmre'])
    roll['grolsmer'] = np.where((roll['yr'] == curryr) & (currqtr != 4) & (roll['qtr'] == currqtr), np.nan, roll['grolsmer'])

    return roll

def live_flag_count(dataframe_in, sector_val, flag_cols):
    dataframe = dataframe_in.copy()
    dataframe[flag_cols] = np.where((dataframe[flag_cols] != 0), 1, dataframe[flag_cols])

    dataframe = dataframe[dataframe['forecast_tag'] != 0]
    
    dataframe['c_flag_tot_sub'] = dataframe.filter(regex="^c_flag*").sum(axis=1)
    dataframe['v_flag_tot_sub'] = dataframe.filter(regex="^v_flag*").sum(axis=1)
    dataframe['g_flag_tot_sub'] = dataframe.filter(regex="^g_flag*").sum(axis=1)
    dataframe['e_flag_tot_sub'] = dataframe.filter(regex="^e_flag*").sum(axis=1)
    
    c_left = dataframe['c_flag_tot_sub'].sum() -  dataframe['flag_skip'].str.count('c_flag').sum()
    v_left = dataframe['v_flag_tot_sub'].sum() - dataframe['flag_skip'].str.count('v_flag').sum()
    g_left = dataframe['g_flag_tot_sub'].sum() - dataframe['flag_skip'].str.count('g_flag').sum()
    e_left = dataframe['e_flag_tot_sub'].sum() - dataframe['flag_skip'].str.count('e_flag').sum()


    countdown_dict = {'Totals': [c_left, v_left, g_left, e_left]}
    countdown = pd.DataFrame.from_dict(countdown_dict, orient='index', columns=["Cons Flags", "Vac Flags", "Mrent Flags", "Erent Flags"])
    
    return countdown

def summarize_flags_ranking(dataframe_in, type_filt, flag_cols):
    dataframe = dataframe_in.copy()
    dataframe = dataframe.reset_index()

    if type_filt == "met":
        filt_val = 'identity_met'
    elif type_filt == "sub":
        filt_val = 'identity'

    dataframe[flag_cols] = np.where((dataframe[flag_cols] != 0), 1, dataframe[flag_cols])

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
    
def summarize_flags(dataframe_in, sum_val, flag_cols):
    
    dataframe = dataframe_in.copy()
    dataframe = dataframe.reset_index()
    if sum_val[0:2] == "US":
        identity_filt = 'identity_us'
    else:
        identity_filt = 'identity_met'

    dataframe = dataframe[dataframe[identity_filt] == sum_val]

    dataframe[flag_cols] = np.where((dataframe[flag_cols] != 0), 1, dataframe[flag_cols])

    dataframe['c_flag_tot'] = dataframe.filter(regex="^c_flag*").sum(axis=1)
    dataframe['v_flag_tot'] = dataframe.filter(regex="^v_flag*").sum(axis=1)
    dataframe['g_flag_tot'] = dataframe.filter(regex="^g_flag*").sum(axis=1)
    dataframe['e_flag_tot'] = dataframe.filter(regex="^e_flag*").sum(axis=1)

    dataframe['total_fcast_rows'] = dataframe.groupby(identity_filt)['identity_row'].transform('nunique')
    dataframe['total_subs'] = dataframe.groupby(identity_filt)['identity'].transform('nunique')

    for x  in ["c", "v", "g", "e"]:
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
                    'Flag Type': ['Cons Flags', 'Vac Flags', 'Mrent Flags', 'Erent Flags'], 
                    'Total Flags': [dataframe['c_flag_sum'].loc[0], dataframe['v_flag_sum'].loc[0], dataframe['g_flag_sum'].loc[0], dataframe['e_flag_sum'].loc[0]],
                    '% Fcast Rows W Flag': [dataframe['c_% Fcast Rows W Flag'].loc[0], dataframe['v_% Fcast Rows W Flag'].loc[0], dataframe['g_% Fcast Rows W Flag'].loc[0], dataframe['e_% Fcast Rows W Flag'].loc[0]],
                    '% Subs W Flag': [dataframe['c_% Subs W Flag'].loc[0], dataframe['v_% Subs W Flag'].loc[0], dataframe['g_% Subs W Flag'].loc[0], dataframe['e_% Subs W Flag'].loc[0]]
                  }
    
    dataframe_out = pd.DataFrame(input_dict)
    
    return dataframe_out


# Return a more verbose description of the flag to the user
def get_issue(type_return, sector_val, dataframe=False, has_flag=False, flag_list=False, p_skip_list=False, show_skips=False, flags_resolved=False, flags_unresolved=False, flags_new=False, flags_skipped=False, curryr=False, currqtr=False, preview_status=False, init_skips=False, write_permit=False):

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
        "v_flag_switch": "The vacancy rate is in the opposite direction from ROL.",
        "v_flag_imp": "The vacancy level results in an implied absorption for the rest of the forecast period that is very different than the typical average absorption for this submarket.",
        "v_flag_z": "The vacancy change is not consistent with the historical vacancy change at the submarket.",
        "v_flag_min": "The vacancy level is below the 10 year historical minimum vacancy level for this submarket.",
        "v_flag_max": "The vacancy level is above the 10 year historical maximum vacancy level for this submarket.",
        "v_flag_lowv": "The overall forecast vacancy change series exhibits low variability compared to the general national submarket average.",
        "v_flag_level": "The vacancy level is not in line with the 10 year historical average.",
        "v_flag_3_trend": "The vacancy change is not in line with the three year historical average for the submarket.",
        "v_flag_cons_neg": "There are three consecutive years of negative absorption in the submarket forecast.",
        "v_flag_subv": "The vacancy change has high variability accross the submarkets for the metro for this forecast year.",
        "v_flag_emp": "The vacancy change quartile is at the opposite end of the sector specific employment change quartile.",
        "v_flag_emp_rol": "There was a significant change in the employment forecast without a commensurate response in vac chg.",
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
        "g_flag_vac": "The market rent change is moving in the opposite direction of vacancy change sentiment.",
        "g_flag_subv": "The market rent change has high variability accross the submarkets for the metro for this forecast year.",
        "g_flag_emp": "The market rent change quartile is at the opposite end of the sector specific employment change quartile.",
        "g_flag_emp_rol": "There was a significant change in the employment forecast without a commensurate response in market rent chg.",
        "e_flag_rol": "The gap is very different from ROL and is not in line with vacancy change compared to ROL.",
        "e_flag_rolvac": "The gap has not changed significantly from ROL despite a significant change in vacancy relative to ROL.",
        "e_flag_zero": "The gap for the submarket is at zero or is negative.",
        "e_flag_min": "The gap level is a new 10 year low for the submarket.",
        "e_flag_max": "The gap level is a new 10 year high for the submarket.",
        "e_flag_min_chg": "The gap change is a new 10 year low for the submarket.",
        "e_flag_max_chg": "The gap change is a new 10 year high for the submarket.",
        "e_flag_improls": "The gap change is causing a wider difference between the expected gap change based on vacancy than if we had stuck with the ROL gap change.",
        "e_flag_imp": "The implied gap change is not in line with the implied vacancy change.",
        "e_flag_vac": "The gap change is moving in the opposite direction of vacancy change sentiment.",
        "e_flag_market": "The market rent and effective rent are moving in opposite directions.",
        "e_flag_emp": "The gap change quartile is at the opposite end of the sector specific employment change quartile.",
        "e_flag_emp_rol": "There was a significant change in the employment forecast without a commensurate response in gap chg.",
        "e_flag_lowv": "The overall forecast gap change series exhibits low variability compared to the general national submarket average."
    }

    highlighting = {
        "c_flag_comp": [['cons'], ['curr yr trend cons'], []], 
        "c_flag_h": [['cons', 'h'], [], []],
        "c_flag_t": [['cons', 't'], [], []],
        "c_flag_sup": [['cons'], ['3yr avgcons'], []],
        "c_flag_e": [['cons', 'e'], ['3yr avgcons'], []],
        "c_flag_hist": [['cons'], ['3yr avgcons'], []],
        "c_flag_rol": [['cons', 'rol cons'], [], []],
        "c_flag_size": [['cons'], [], []],
        "c_flag_lowv": [['cons'], ['f var cons'], []],
        "v_flag_low": [['vac'], ['min vac'], []],
        "v_flag_high": [['vac'], [], []],
        "v_flag_ratio": [['cons', 'abs'], ['abs cons r', 'p abs cons', 'avg abs cons', '3yr avgabs nonc'], []],
        "v_flag_roll": [['cons', 'abs'], ['abs cons r', 'p abs cons', 'avg abs cons', '3yr avgabs nonc'], []],
        "v_flag_improls": [['abs', 'rol abs'], ['imp abs', 'histimp avgabs', 'imp abs rol'], []],
        "v_flag_rol": [['abs', 'rol abs', 'cons', 'rol cons'], [], []],
        "v_flag_switch": [['vac chg', 'rol vac chg'], [], []],
        "v_flag_imp": [['abs'], ['imp abs', 'histimp avgabs'], []],
        "v_flag_z": [['vac chg'], ['vac z'], []],
        "v_flag_min": [['vac'], ['min vac'], []],
        "v_flag_max": [['vac'], ['max vac'], []],
        "v_flag_lowv": [['vac chg'], ['f var vac chg'], []],
        "v_flag_level": [['vac'], ['10 yr vac'], []],
        "v_flag_3_trend": [['abs'], ['3yr avgabs nonc'], []],
        "v_flag_cons_neg": [['abs'], [], []],
        "v_flag_subv": [['vac chg'], ['vac chg sub var'], []],
        "v_flag_emp": [['vac chg'], ['vac quart'], ['emp quart', 'off emp quart', 'ind emp quart', 'emp chg', 'off emp chg', 'ind emp chg']],
        "v_flag_emp_rol": [['vac chg', 'rol vac chg'], [], ['emp chg', 'off emp chg', 'ind emp chg' 'rol emp chg', 'rol off emp chg', 'rol ind emp chg']],
        "g_flag_low": [['Gmrent'], ['3yr avgGmrent nonc'], []],
        "g_flag_nc": [['cons', 'Gmrent'], ['3yr avgGmrent nonc', 'cons prem'], []],
        "g_flag_z": [['Gmrent'], ['Gmrent z'], []],
        "g_flag_lowv": [['Gmrent'], ['f var Gmrent'], []],
        "g_flag_highv": [['Gmrent'], ['f_var_G_mrent'], []],
        "g_flag_max": [['Gmrent'], ['max Gmrent'], []],
        "g_flag_3_trend": [['Gmrent'], ['3yr avgGmrent nonc'], []],
        "g_flag_improls": [['Gmrent', 'rol Gmrent'], ['imp Gmrent', 'histimp Gmrent', 'imp Gmrent rol'], []],
        "g_flag_imp": [['Gmrent'], ['imp Gmrent', 'histimp Gmrent'], []],
        "g_flag_rol": [['Gmrent', 'rol Gmrent'], [], []],
        "g_flag_yrdiff": [['Gmrent'], [], []],
        "g_flag_cons_low": [['Gmrent'], [], []],
        "g_flag_vac": [['vac chg', 'Gmrent'], ['avg vac chg', 'avg Gmrent nonc'], []],
        "g_flag_subv": [['Gmrent'], ['Gmrent sub var'], []],
        "g_flag_emp": [['Gmrent'], ['Gmrent quart'], ['emp quart', 'off emp quart', 'ind emp quart', 'emp chg', 'off emp chg', 'ind emp chg']],
        "g_flag_emp_rol": [['Gmrent', 'rol Gmrent'], [], ['emp chg', 'off emp chg', 'ind emp chg' 'rol emp chg', 'rol off emp chg', 'rol ind emp chg']],
        "e_flag_rol": [['gap chg', 'rol gap chg', 'vac chg', 'rol vac chg'], [], []],
        "e_flag_rolvac": [['gap chg', 'rol gap chg', 'vac chg', 'rol vac chg'], [], []],
        "e_flag_zero": [['gap'], [], []],
        "e_flag_max": [['gap'], ['max gap', 'gap 5'], []],
        "e_flag_min": [['gap'], ['min gap', 'gap 95'], []],
        "e_flag_min_chg": [['gap chg'], ['min gap chg'], []],
        "e_flag_max_chg": [['gap chg'], ['max gap chg'], []],
        "e_flag_improls": [['gap chg', 'rol gap chg', 'vac chg', 'rol vac chg'], ['imp gap chg', 'imp vac chg'], []],
        "e_flag_imp": [['gap chg'], ['imp gap chg', 'imp vac chg'], []],
        "e_flag_vac": [['gap chg', 'vac chg'], [], []],
        "e_flag_market": [['Gmerent', 'Gmrent'], [], []],
        "e_flag_emp": [['gap chg'], ['gap quart'], ['emp quart', 'off emp quart', 'ind emp quart', 'emp chg', 'off emp chg', 'ind emp chg']],
        "e_flag_emp_rol": [['gap chg', 'rol gap chg'], [], ['emp chg', 'off emp chg', 'ind emp chg' 'rol emp chg', 'rol off emp chg', 'rol ind emp chg']],
        "e_flag_lowv": [['gap chg'], ['f var gap chg'], []]
    }

    if type_return == "specific":

        display_issue_cols = []
        key_metric_issue_cols = []
        key_emp_issue_cols = []
        issue_description_noprev = []
        issue_description_resolved = []
        issue_description_unresolved = []
        issue_description_new = []
        issue_description_skipped = []

        if has_flag == 0:
            issue_description_noprev = "No flags for this year at the submarket"
            
        elif has_flag == 2 and (show_skips == False or len(p_skip_list) == 0):
            issue_description_noprev = "No flags for this year at the submarket"

        elif has_flag == 2 and show_skips == True and len(p_skip_list) > 0:
            p_skip_list = p_skip_list[0].replace(' ', '').split(",")
            
            issue_description_noprev = html.Div([
                                        html.Div([
                                            dbc.Container(
                                            [
                                                dbc.Checklist(
                                                    id="flag_descriptions_noprev",
                                                    options=[
                                                            {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}", "disabled": True}
                                                            for i in p_skip_list
                                                            ],
                                                    inline=True,
                                                    value = ["skip-" + x for x in p_skip_list]
                                                            ),  
                                                    
                                            ]
                                            + [
                                                dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                for i in p_skip_list
                                            ],
                                            fluid=True),
                                                
                                        ]), 
                                    ])
        elif has_flag == 1:
            if not preview_status:
                if show_skips == True:
                    flags_use = flag_list + p_skip_list
                    disabled_list = [False] * len(flag_list) + [True] * len(p_skip_list)
                else:
                    flags_use = flag_list
                    disabled_list = [False] * len(flag_list)

                if not write_permit:
                    disabled_list = [True] * len(flag_list)

                issue_description_noprev = html.Div([
                                        html.Div([
                                            dbc.Container(
                                            [
                                                dbc.Checklist(
                                                    id="flag_descriptions_noprev",
                                                    options=[
                                                            {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}", 'disabled': j}
                                                            for i, j in zip(flags_use, disabled_list)
                                                            ],
                                                    inline=True,
                                                    value = ["skip-" + x for x in init_skips]
                                                            ),  
                                                    
                                            ]
                                            + [
                                                dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                for i in flags_use
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
                    if not write_permit:
                        disabled_list = [True] * len(flags_unresolved)
                    else:
                        disabled_list = [False] * len(flags_unresolved)
                    issue_description_unresolved = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_unresolved",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}", 'disabled': j}
                                                                for i, j in zip(flags_unresolved, disabled_list)
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
                    if not write_permit:
                        disabled_list = [True] * len(flags_new)
                    else:
                        disabled_list = [False] * len(flags_new)
                    issue_description_new = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_new",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}", 'disabled': j}
                                                                for i, j in zip(flags_new, disabled_list)
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
                if len(flags_skipped) > 0 or len(p_skip_list) > 0:

                    if write_permit:
                        disabled_list = [False] * len(flags_skipped) + [True] * len(p_skip_list)
                    else:
                        disabled_list = [True] * len(flags_skipped) + [True] * len(p_skip_list)


                    issue_description_skipped = html.Div([
                                            html.Div([
                                                dbc.Container(
                                                [
                                                    dbc.Checklist(
                                                        id="flag_descriptions_skipped",
                                                        options=[
                                                                {"label": f" {i[0]} {i[6:]}", "value": f"skip-{i}", "label_id": f"label-{i}", "disabled": j}
                                                                for i, j in zip(flags_skipped + p_skip_list, disabled_list)
                                                                ],
                                                        value=[f"skip-{i}" for i in flags_skipped + p_skip_list],
                                                        inline=True,
                                                        labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px', 'color': 'black'},
                                                                ),  
                                                        
                                                ]
                                                + [
                                                    dbc.Tooltip(issue_descriptions[i], target=f"label-{i}")
                                                    for i in flags_skipped + p_skip_list
                                                ],
                                                fluid=True),
                                                    
                                            ]), 
                                        ])
                else:
                    issue_description_skipped = []

            if preview_status == False:
                display_issue_cols = highlighting[flag_list[0]][0]
                key_metric_issue_cols = highlighting[flag_list[0]][1]
                key_emp_issue_cols = highlighting[flag_list[0]][2]
            else:
                if len(flags_new) > 0:
                    display_issue_cols = highlighting[flags_new[0]][0]
                    key_metric_issue_cols = highlighting[flags_new[0]][1]
                    key_emp_issue_cols = highlighting[flags_new[0]][2]
                elif len(flags_unresolved) > 0:
                    display_issue_cols = highlighting[flags_unresolved[0]][0]
                    key_metric_issue_cols = highlighting[flags_unresolved[0]][1]
                    key_emp_issue_cols = highlighting[flags_unresolved[0]][2]
                else:
                    display_issue_cols = highlighting[flag_list[0]][0]
                    key_metric_issue_cols = highlighting[flag_list[0]][1]
                    key_emp_issue_cols = highlighting[flag_list[0]][2]

        return issue_description_noprev, issue_description_resolved, issue_description_unresolved, issue_description_new, issue_description_skipped, display_issue_cols, key_metric_issue_cols, key_emp_issue_cols
    
    elif type_return == "list":
        return issue_descriptions

# Function that checks to see if there was an adjustment made from last published data (ROL) that crosses the data governance threshold by a manual analyst shim, thus requiring a support note documenting why the change was made
def manual_rebench_check(data, data_temp, rebench_to_check, curryr, currqtr, sector_val, thresh, var, drop_val):
    orig_to_check = data.copy()
    if var == 'vac':
        new_vac = data_temp.copy()
        new_vac = new_vac[new_vac['identity'] == drop_val]
        new_vac = new_vac[[var, 'rolsvac', var + "_oob"]]
        rebench_to_check = rebench_to_check.join(new_vac)
        rebench_to_check = rebench_to_check.rename(columns={'rolsvac': 'rolvac'})
    else:
        rol_var = data_temp.copy()
        rol_var = rol_var[rol_var['identity'] == drop_val]
        rol_var = rol_var[['rol' + var, var + "_oob"]]
        rebench_to_check = rebench_to_check.join(rol_var)
    rebench_to_check = rebench_to_check[[var, 'rol' + var, var + '_oob']]
    orig_to_check = orig_to_check[orig_to_check['identity'] == drop_val]
    orig_to_check = orig_to_check[[var]]
    orig_to_check = orig_to_check.rename(columns={var: var + "_orig"})
    rebench_to_check = rebench_to_check.join(orig_to_check)
    if var == "vac":
        rebench_to_check['diff_to_oob'] = rebench_to_check[var] - rebench_to_check[var + "_oob"]
        rebench_to_check['diff_to_rol'] = rebench_to_check[var] - rebench_to_check['rol' + var]
        rebench_to_check['orig_diff_to_rol'] = rebench_to_check[var + "_orig"] - rebench_to_check['rol' + var]
    else:
        rebench_to_check['diff_to_oob'] = (rebench_to_check[var] - rebench_to_check[var + "_oob"]) / rebench_to_check[var + "_oob"]
        rebench_to_check['diff_to_rol'] = (rebench_to_check[var] - rebench_to_check['rol' + var]) / rebench_to_check['rol' + var]
        rebench_to_check['orig_diff_to_rol'] = (rebench_to_check[var + "_orig"] - rebench_to_check['rol' + var]) / rebench_to_check['rol' + var]
    
    rebench_to_check = rebench_to_check[((abs(rebench_to_check['diff_to_oob']) >= thresh) & (abs(rebench_to_check['diff_to_rol']) >= thresh) & (abs(rebench_to_check['diff_to_rol']) >= abs(rebench_to_check['orig_diff_to_rol']))) | 
                                        ((abs(rebench_to_check['diff_to_rol']) > abs(rebench_to_check['orig_diff_to_rol'])) & (abs(rebench_to_check['diff_to_rol']) >= thresh))]
    
    rebench_to_check = rebench_to_check[((rebench_to_check[var] > rebench_to_check['rol' + var]) & (rebench_to_check['diff_to_rol'] > 0)) | ((rebench_to_check[var] < rebench_to_check['rol' + var]) & (rebench_to_check['diff_to_rol'] < 0))]
    

    if len(rebench_to_check) > 0:
        check = True
        first_yr = rebench_to_check.reset_index().loc[0]['identity_row']
        first_yr = first_yr[-5:-1]
    else:
        check = False
        first_yr = False

    return check, first_yr

# Function that analyzes where edits are made in the display dataframe if manual edit option is selected
def get_diffs(shim_data, data_orig, data, drop_val, curryr, currqtr, sector_val, button, avail_c, rent_c, proc_subsequent, coeff_status):
    
    # First see if there is a true diff, and that the shims entered do not all match what is already in the published dataset
    has_true_diff = True
    data_update = shim_data.copy()
    indexes = data_orig.index.values
    data_update['new_index'] = indexes
    data_update = data_update.set_index('new_index')

    diffs = data_update.copy()
    diffs = diffs == data_orig
    diffs = data_update[~diffs]
    diffs = diffs.dropna(axis=0, how='all')
    diffs = diffs.dropna(axis=1, how='all')

    if len(diffs) == 0:
        has_true_diff = False

    # If there is at least one shim that is different than current published, process the shims. We will want to process all shims, in case one value matches the level in published but because of a shim in a prior period, it is there to maintain the value and is actually a true shim
    if has_true_diff == True:
    
        diffs = shim_data.copy()
        diffs[['cons', 'avail', 'mrent', 'merent']] = np.where(diffs[['cons', 'avail', 'mrent', 'merent']] == "None", np.nan, diffs[['cons', 'avail', 'mrent', 'merent']])
        diffs = diffs[~diffs.isnull().all(axis=1)]
        diffs = diffs[['cons', 'avail', 'mrent', 'merent']]
        diffs = diffs.dropna(axis='columns', how='all')
        diffs = diffs.dropna(axis='rows', how='all')

        data_temp = data.copy()
        if coeff_status:
            print("If really want to use coeffs, need to adjust the path here to the true location of the coeffs file. Get analyst buy in first though")
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/coeffs/{}/{}q{}/coeffs.pickle".format(get_home(), sector_val, curryr, currqtr))
            coeff_data = pd.read_pickle(file_path)
            if 'inv_chg_to_vac' not in list(data_temp.columns):
                coeff_data = coeff_data.set_index("identity")
                data_temp = data_temp.join(coeff_data, on='identity')
        
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
                    yr_change_diffs = data_temp.loc[row_to_fix_diffs]['yr']
                    
                    if coeff_status:
                        data_temp = insert_fix_coeffs(data_temp, row_to_fix_diffs, drop_val, fix_val, col_issue_diffs[0], yr_change_diffs, curryr, currqtr, sector_val, proc_subsequent)
                    else:
                        data_temp = insert_fix(data_temp, row_to_fix_diffs, drop_val, fix_val, col_issue_diffs[0], yr_change_diffs, curryr, currqtr, sector_val, proc_subsequent)
        
        # Check to see if a vacancy or rent shim created a change from ROL above the data governance threshold set by key stakeholders. If it did, do not process the shim unless there is an accompanying note explaining why the change was made
        avail_check = False
        mrent_check = False
        merent_check = False
        first_yr = False
        
        if button == 'submit':

            init_avail_c = data_temp.loc[drop_val + str(curryr) + str(5)]['avail_comment']
            init_rent_c = data_temp.loc[drop_val + str(curryr) + str(5)]['rent_comment']

            for var in ['avail', 'mrent', 'merent']:
                rebench_to_check = diffs.copy()
                if var in list(rebench_to_check.columns):
                    if rebench_to_check[var].isnull().values.all() == False:
                        if var == "avail" and (avail_c[-9:] == "Note Here" or len(avail_c.strip()) == 0 or avail_c == init_avail_c):
                            avail_check, first_yr = manual_rebench_check(data, data_temp, rebench_to_check, curryr, currqtr, sector_val, 0.01, "vac", drop_val)
                        elif var == "mrent" and avail_check == False and (rent_c[-9:] == "Note Here" or len(rent_c.strip()) == 0 or rent_c == init_rent_c):
                            mrent_check, first_yr = manual_rebench_check(data, data_temp, rebench_to_check, curryr, currqtr, sector_val, 0.03, "mrent", drop_val)
                        elif var == "merent" and mrent_check == False and avail_check == False and (rent_c[-9:] == "Note Here" or len(rent_c.strip()) == 0 or rent_c == init_rent_c):
                            merent_check, first_yr = manual_rebench_check(data, data_temp, rebench_to_check, curryr, currqtr, sector_val, 0.03, "merent", drop_val)

            if avail_check == False and mrent_check == False and merent_check == False:
                has_diff = 1
                data = data_temp.copy()
            else:
                has_diff = 2
        else:
            has_diff = 1
            data = data_temp.copy()
    else:
        has_diff = 0
        first_yr = False
        avail_check = False
        mrent_check = False
        merent_check = False
    
    return data, has_diff, avail_check, mrent_check, merent_check, first_yr

# Function to identify if a submarket has a flag for review
def flag_examine(data, identity_val, filt, curryr, currqtr, flag_cols, flag_flow, yr_val):

    dataframe = data.copy()
    has_flag = 0
    skip_list = []
    dataframe[flag_cols] = np.where((dataframe[flag_cols] > 0), 1, dataframe[flag_cols])
    dataframe = dataframe[dataframe['forecast_tag'] != 0]
    
    if filt == True:
        dataframe = dataframe[dataframe['identity'] == identity_val]
        skip_list = list(dataframe.loc[identity_val + str(curryr) + str(5)][['flag_skip']][0].split(","))
        skip_list = [x.strip() for x in skip_list]
        skip_list = [x[:-4] for x in skip_list if x[-4:] == str(yr_val)]
        dataframe = dataframe[dataframe['yr'] == yr_val]

    else:
        first_sub = dataframe.reset_index().loc[0]['identity']
        if flag_flow == "cat":
            dataframe_test = dataframe.copy()
            
            dataframe_test['has_c'] = dataframe_test.filter(regex="^c_flag*").sum(axis=1)
            dataframe_test['has_v'] = dataframe_test.filter(regex="^v_flag*").sum(axis=1)
            dataframe_test['has_g'] = dataframe_test.filter(regex="^g_flag*").sum(axis=1)
            dataframe_test['has_e'] = dataframe_test.filter(regex="^e_flag*").sum(axis=1)

            dataframe_test['has_c'] = dataframe_test['has_c'] -  dataframe_test['flag_skip'].str.count('c_flag')
            dataframe_test['has_v'] = dataframe_test['has_v'] - dataframe_test['flag_skip'].str.count('v_flag')
            dataframe_test['has_g'] = dataframe_test['has_g'] - dataframe_test['flag_skip'].str.count('g_flag')
            dataframe_test['has_e'] = dataframe_test['has_e'] - dataframe_test['flag_skip'].str.count('e_flag')

            for x in ['has_c', 'has_v', 'has_g', 'has_e']:
                dataframe_test_1 = dataframe_test.copy()
                dataframe_test_1 = dataframe_test_1[dataframe_test_1[x] > 0]
                if len(dataframe_test_1) > 0:
                    dataframe = dataframe_test_1.copy()
                    break
        elif flag_flow == "flag":
            dataframe_test = dataframe.copy()
            for x in flag_cols:
                dataframe_test_1 = dataframe_test.copy()
                dataframe_test_1['count_flags'] = dataframe_test_1[dataframe_test_1[x] > 0].groupby('identity')['yr'].transform('count')
                dataframe_test_1['count_skips'] = dataframe_test_1[dataframe_test_1['flag_skip'].str.contains(x) == True].groupby('identity')['yr'].transform('count')
                dataframe_test_1['count_flags'] = dataframe_test_1['count_flags'].fillna(0)
                dataframe_test_1['count_skips'] = dataframe_test_1['count_skips'].fillna(0)
                dataframe_test_1['flags_remaining'] = dataframe_test_1['count_flags'] - dataframe_test_1['count_skips']
                dataframe_test_1 = dataframe_test_1[(dataframe_test_1['yr'] == curryr) & (dataframe_test_1['qtr'] == 5)]
                dataframe_test_1 = dataframe_test_1[(dataframe_test_1['flags_remaining'] > 0)]
                if len(dataframe_test_1) > 0:
                    dataframe = dataframe_test_1.copy()
                    break

    cols_to_keep = flag_cols + ['identity', 'flag_skip', 'yr']
    dataframe = dataframe[cols_to_keep]
    dataframe['sum_flags'] = dataframe[flag_cols].sum(axis=1)
    dataframe['flag_skip'] = dataframe['flag_skip'].fillna('')
    dataframe['sum_skips'] = dataframe['flag_skip'].str.count(str(yr_val))
    dataframe['total_flags'] = dataframe.groupby('identity')['sum_flags'].transform('sum')
    dataframe['total_skips'] = dataframe.groupby('identity')['sum_skips'].transform('sum')
    dataframe['flags_left'] = round(dataframe['total_flags'] - dataframe['total_skips'],0)
    dataframe = dataframe[dataframe['flags_left'] > 0]

    if len(dataframe) == 0:
        if filt == True:
            has_flag = 2
            flag_list = ['v_flag']
        else:
            if identity_val is None:
                identity_val = first_sub
            has_flag = 0
            flag_list = ['v_flag']
    else:
        if filt == False:
            identity_val = dataframe.reset_index().loc[0]['identity']
            dataframe = dataframe[dataframe['identity'] == identity_val]
            testing_orig_yr_val = dataframe.copy()
            test_skip_list = [x for x in skip_list if x[-4:] == str(yr_val)]
            testing_orig_yr_val = testing_orig_yr_val[(testing_orig_yr_val['yr'] == yr_val) & (testing_orig_yr_val['identity'] == identity_val)]
            testing_orig_yr_val = testing_orig_yr_val[testing_orig_yr_val['sum_flags'] > len(test_skip_list)]
            if len(testing_orig_yr_val) == 0:
                new_yr = dataframe.copy()
                new_yr = new_yr[(new_yr['identity'] == identity_val) & (new_yr['sum_flags'] > 0)]
                yr_val = new_yr.reset_index().loc[0]['yr']
            skip_list = list(dataframe.loc[identity_val + str(curryr) + str(5)][['flag_skip']][0].split(","))
            skip_list = [x.strip() for x in skip_list]
            skip_list = [x[:-4] for x in skip_list if x[-4:] == str(yr_val)]
            dataframe = dataframe[dataframe['yr'] == yr_val]

        flags = dataframe.copy()
        flags = flags[flag_cols + ['flag_skip']]
        flags = flags[flags.columns[(flags != 0).any()]]
        flag_list = list(flags.columns)
        flag_list = [x for x in flag_list if x not in skip_list and x != 'flag_skip']
        
        if len(flag_list) > 0:
            has_flag = 1
        else:
            has_flag = 0
            if filt == True:
                flag_list = ['v_flag']
                has_flag = 2
            else:
                if identity_val is None:
                    identity_val = dataframe.reset_index().loc[0]['identity']  
                flag_list = ['v_flag']
    
    return flag_list, skip_list, identity_val, has_flag, yr_val


# Function to insert the suggested or user fix to the fixed dataframe for review by user, as originally formatted by BB before HSY suggestion of using model coefficients directly
def insert_fix(dataframe, row_to_fix, identity_val, fix, variable_fix, yr_change, curryr, currqtr, sector_val, proc_subsequent):

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
                    avail_add = cons_diff * orig_abs_cons_r
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
                if proc_subsequent == "c":
                    var = 'abs'
                elif proc_subsequent == "r":
                    var = 'rolsabs'
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe[var] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 >= 0) & ((dataframe[var] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 <= dataframe['inv']), (dataframe[var] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1, dataframe['avail'])
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe[var] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 < 0), dataframe['avail'].shift(periods=period), dataframe['avail'])
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe[var] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 > dataframe['inv']), dataframe['avail'].shift(periods=period), dataframe['avail'])
            dataframe['avail'] = round(dataframe['avail'], a_round_val)
            dataframe['occ'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['inv'] - dataframe['avail'], dataframe['occ'])
            dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
            dataframe['abs'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['occ'] - dataframe['occ'].shift(periods=period), dataframe['abs'])
            dataframe['vac_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['vac'] - dataframe['vac'].shift(periods=period), dataframe['vac_chg'])   
        elif variable_fix == "g":
            if x == 0:
                dataframe.loc[row_to_fix, 'mrent'] = fix
            if x > 0:
                if proc_subsequent == "c":
                    var = 'G_mrent'
                elif proc_subsequent == "r": 
                    var = 'grolsmre'
                dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['mrent'].shift(periods=period) * (1 + dataframe[var]), dataframe['mrent'])
                dataframe['mrent'] = round(dataframe['mrent'], m_round_val)
            dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'] - dataframe['mrent'].shift(periods=period)) / dataframe['mrent'].shift(periods=period), 4), dataframe['G_mrent'])
            dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'] * (dataframe['gap'] * -1)) + dataframe['mrent'], 4), dataframe['merent'])
            dataframe['merent'] = round(dataframe['merent'], m_round_val)
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), 4), dataframe['G_merent'])        
    
        elif variable_fix == "e":
            if x == 0:
                dataframe.loc[row_to_fix, 'merent'] = fix   
            if x > 0:
                dataframe['merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['merent'].shift(periods=period) * (1 + dataframe['G_merent']), dataframe['merent'])
                dataframe['merent'] = round(dataframe['merent'], m_round_val)
            dataframe['G_merent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['merent'] - dataframe['merent'].shift(periods=period)) / dataframe['merent'].shift(periods=period), 4), dataframe['G_merent'])
            dataframe['gap'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(((dataframe['merent'] - dataframe['mrent']) / dataframe['mrent']) * -1, 4), dataframe['gap'])
            dataframe['gap_chg'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['gap'] - dataframe['gap'].shift(periods=period), dataframe['gap_chg'])
    
    return dataframe

# Function to insert the suggested or user fix to the fixed dataframe for review by user based on oob model coefficients
def insert_fix_coeffs(dataframe, row_to_fix, identity_val, fix, variable_fix, yr_change, curryr, currqtr, sector_val, proc_subsequent):

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
            if x > 0 and proc_subsequent == "c":
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
            
            elif x > 0 and proc_subsequent == "r":
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe['rolsabs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 >= 0) & ((dataframe['rolsabs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 <= dataframe['inv']), (dataframe['rolsabs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1, dataframe['avail'])
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe['rolsabs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 < 0), dataframe['avail'].shift(periods=period), dataframe['avail'])
                dataframe['avail'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val) & ((dataframe['rolsabs'] + dataframe['occ'].shift(periods=period) - dataframe['inv']) * -1 > dataframe['inv']), dataframe['avail'].shift(periods=period), dataframe['avail'])
                dataframe['avail'] = round(dataframe['avail'], a_round_val)
                dataframe['vac'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round(dataframe['avail'] / dataframe['inv'],4), dataframe['vac'])
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
            if x > 0 and proc_subsequent == "c":
                total_effect = 0
                total_effect += (np.log(dataframe.loc[index_val]['mrent']) - np.log(dataframe.loc[index_val]['mrent_oob'])) * dataframe.loc[index_val]['rent_lchg_to_rent']
                dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['G_mrent_oob'] + total_effect, dataframe['G_mrent'])
                dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), (1+ dataframe['G_mrent']) * dataframe['mrent'].shift(periods=period), dataframe['mrent'])
                dataframe['mrent'] = round(dataframe['mrent'], m_round_val)
            elif x > 0 and proc_subsequent == "r":
                dataframe['mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), dataframe['mrent'].shift(periods=period) * (1 + dataframe['grolsmre']), dataframe['mrent'])
                dataframe['mrent'] = round(dataframe['mrent'], m_round_val)
                dataframe['G_mrent'] = np.where((dataframe['yr'] == yr_change + x) & (dataframe['qtr'] == 5) & (dataframe['identity'] == identity_val), round((dataframe['mrent'] - dataframe['mrent'].shift(periods=period)) / dataframe['mrent'].shift(periods=period), 4), dataframe['G_mrent'])

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

# This function sets the scale and tick distance for bar graphs based on the variable's max percentage of inventory
def set_bar_scale(data_in, sector_val, numer_list, denomer_list):
    
    data = data_in.copy()
    if 'rolscon' in numer_list:
        data['rolsinv'] = data['inv'] - (data['cons'] - data['rolscon'])
    val_list = []
    for x, y in zip(numer_list, denomer_list):
        data[x + "_per_inv"] = data[x] / data[y]
        data[x + "_per_inv"] = round(data[x + "_per_inv"], 2)
        val_list.append(list(data[x + "_per_inv"]))
    combined = []
    for x in val_list:
        x = [y for y in x if y == y]
        if len(x) > 0:
            combined += x
    combined = [float(i) for i in combined]
    
    max_cons_per_inv = max(combined)
    max_inv = max(list(data['inv']))
    
    if max_cons_per_inv == 0:
        if sector_val != "apt":
            range_list = [0, 400000]
            dtick = 100000
        elif sector_val == "apt":
            range_list = [0, 4000]
            dtick = 1000
    else:
        len_max = len(str(int((max_cons_per_inv * max_inv))))
        max_round = round((max_cons_per_inv * max_inv), (len_max - 1) * -1)

        if max_cons_per_inv < 0.02:
            upper_bound = max_round * 2.5
        elif max_cons_per_inv >= 0.02 and max_cons_per_inv < 0.05:
            upper_bound = max_round * 2
        elif max_cons_per_inv >= 0.05 and max_cons_per_inv < 0.1:
            upper_bound = max_round * 1.5
        else:
            upper_bound = max_round * 1
        
        range_list = [0, upper_bound]

        dtick = upper_bound / 4
        len_dtick = len(str(int(dtick)))
        dtick = round(dtick, (len_dtick - 1) * -1)
        
    return range_list, dtick

def set_y2_scale(graph, type_filt, input_var, sector_val):
    if type_filt == "sub":
        graph = pd.melt(graph, id_vars=['subsector', 'metcode', 'subid', 'yr', 'qtr'])
    elif type_filt == "met":
        graph = pd.melt(graph, id_vars=['subsector', 'metcode', 'yr', 'qtr'])
    elif type_filt == "nat":
        graph = pd.melt(graph, id_vars=['subsector', 'yr', 'qtr'])

    var = list(graph[graph['variable'] == input_var]['value'])

    if type_filt != "ts":
        if input_var == "vac":
            rol_var = list(graph[(graph['variable'] == 'rolsvac') & (graph['value'] != '')]['value'])
            oob_var = list(graph[(graph['variable'] == 'vac_oob') & (graph['value'] != '')]['value'])
        elif input_var == "mrent":
            rol_var = list(graph[(graph['variable'] == 'rol_mrent') & (graph['value'] != '')]['value'])
            oob_var = list(graph[(graph['variable'] == 'mrent_oob') & (graph['value'] != '')]['value'])
        rol_var = [float(i) for i in rol_var]
        oob_var = [float(i) for i in oob_var]
        combined = var + rol_var + oob_var
    elif type_filt == "ts":
        combined = var
    max_var = max(combined)
    min_var = min(combined)

    if input_var == "vac" or "gap" in input_var:
        round_val = 2
        tick_0 = max(min_var - 0.01, 0)
        tick_1 = min(max_var + 0.01, 100)
    elif "avg_inc" in  input_var:
        round_val = -3
        tick_0 = min_var - round((max_var - min_var) / 5, round_val)
        tick_1 = max_var + round((max_var - min_var) / 5, round_val)
    else:
        tick_0 = min_var - round((max_var - min_var) / 5, 2)
        tick_1 = max_var + round((max_var - min_var) / 5, 2)
    range_list = [round(tick_0, 2), round(tick_1, 2)]
    dtick = round((tick_1 - tick_0) / 5, 2)

    return range_list, dtick, tick_0

def get_user_skips(skip_input_noprev, skip_input_resolved, skip_input_unresolved, skip_input_new, skip_input_skipped):

    if len(skip_input_noprev) > 0:
        has_check = list(skip_input_noprev['props']['children'][0]['props']['children'][0]['props']['children'][0]['props'].keys())
        if 'value' in has_check:
            skip_list_temp = skip_input_noprev['props']['children'][0]['props']['children'][0]['props']['children'][0]['props']['value']
            skip_list = [e[5:] for e in skip_list_temp]
        else:
            skip_list = []
    else:
        skip_list = []
        for input_list in [skip_input_resolved, skip_input_unresolved, skip_input_new, skip_input_skipped]:
            if len(input_list) > 0:
                has_check = list(input_list['props']['children'][0]['props']['children'][0]['props']['children'][0]['props'].keys())
                if 'value' in has_check:
                    skip_list_temp = input_list['props']['children'][0]['props']['children'][0]['props']['children'][0]['props']['value']
                    skip_list_temp = [e[5:] for e in skip_list_temp]
                    skip_list += skip_list_temp

    return skip_list

def check_skips(dataframe_in, decision_data, curryr, currqtr, sector_val, flag_cols, init_drop_val, yr_val):
    dataframe = dataframe_in.copy()
        
    skips = list(dataframe[(dataframe['identity'] == init_drop_val) & (dataframe['yr'] == curryr) & (dataframe['qtr'] == 5)]['flag_skip'])
    skips = skips[0].replace(' ', '').split(",")
    skips = [x for x in skips if x[-4:] == str(yr_val)]
    skips = [x[:-4] for x in skips]
    dataframe = dataframe[(dataframe['identity'] == init_drop_val) & (dataframe['yr'] == yr_val) & (dataframe['qtr'] == 5)]
    if len(dataframe) > 0:           
        flags_only = dataframe.copy()
        flags_only = flags_only[flag_cols]
        flags = dataframe.apply(lambda row: row[row != 0].index, axis=1).values[0]
        flags = [x for x in flags if x in flag_cols]
        remove_skips = [x for x in skips if x not in flags]
        if len(remove_skips) > 0:
            new_skips = [x for x in skips if x in flags]
            dataframe_in.loc[init_drop_val + str(curryr) + str(5), 'flag_skip'] = ''
            for x in skips:
                if x not in remove_skips:
                    if dataframe_in.loc[init_drop_val + str(curryr) + str(5), 'flag_skip'] == '':
                            dataframe_in.loc[init_drop_val + str(curryr) + str(5), 'flag_skip'] = x
                    else:
                        dataframe_in.loc[init_drop_val + str(curryr) + str(5), 'flag_skip'] += ", " + x
            
            decision_data.loc[init_drop_val + str(curryr) + str(5), 'skipped'] = ''
            for x in skips:
                if x not in remove_skips:
                    if decision_data.loc[init_drop_val + str(curryr) + str(5), 'skipped'] == '':
                            decision_data.loc[init_drop_val + str(curryr) + str(5), 'skipped'] = x
                    else:
                        decision_data.loc[init_drop_val + str(curryr) + str(5), 'skipped'] += ", " + x
            if len(remove_skips) == len(skips):
                decision_data.loc[init_drop_val + str(curryr) + str(5), 'skip_user'] = ''

    return dataframe_in, decision_data

class GlobalShim:
    
    def __init__(self, sector_val, curryr, currqtr, var, target, subsector, year, init_lev_val, prev_lev_val, roll_val, override, preview_status, coeff_status):

        self.sector_val = sector_val
        self.curryr = curryr
        self.currqtr = currqtr
        self.var = var
        self.target = target
        self.subsector = subsector
        self.year = year
        self.roll_val = roll_val
        self.override = override
        self.preview_status = preview_status
        self.change = False
        self.coeff_status = coeff_status
        self.diff_to_target = target - init_lev_val
        if sector_val == "apt":
            self.round_val = 0
        else:
            self.round_val = -3
        
        thresh_dict = {'DW': 50000, 'F': 20000, 'apt': 20, 'off': 20000, 'ret': 10000}
        if sector_val == "ind":
            self.thresh = thresh_dict[subsector]
        else:
            self.thresh = thresh_dict[sector_val]
        if not override:
            self.cap = -0.01
        elif override:
            self.cap = -0.02
        
    # Generate the message displayed to user about how their global shims were implemented and if their target was hit
    def gen_message(self, achieved_target):
        
        if self.preview_status:
            button = 'Preview'
        elif not self.preview_status:
            button = 'Submit'
        
        if not achieved_target and not self.override:
            achieved_target = True
            message_display = True
            if self.change:
                message = "Some changes were implemented to reach your {} target, but there is limited support left to continue making changes. Do you want to proceed with more changes? If yes, click {} again.".format(self.var.lower(), button)
            else:
                message = "There is limited support for making any changes to reach your {} target. Do you want to make changes regardless? If yes, click {} again.".format(self.var.lower(), button)
        else:
            message = ''
            message_display = False

        if not achieved_target and self.override:
            achieved_target = True
            message_display = True
            if self.change:
                message = "Additional changes were implemented to reach your {} target, but there is limited support left to continue making changes. All additional changes should be submitted via submarket level shim".format(self.var.lower())
            else:
                message = "No additional changes were implemented to reach your {} target. All additional changes should be submitted via submarket level shim".format(self.var.lower())

        return achieved_target, message_display, message
    
    # Check if there are submarkets where we can increase the construction to match h stock
    def cons_inc_h(self, data):

        temp = data.copy()
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        temp = temp[(temp['cons'] < temp['round_h_temp'])]
        if len(temp) > 0:
            temp['diff'] = temp['round_h_temp'] - temp['cons']
            temp.sort_values(by=['diff'], ascending=[True], inplace=True)
            total_add = temp['diff'].sum()
            if len(temp) > 0:
                    return self.execute_global_shim(total_add, temp, data)

    # Check if there are submarkets where we can increase the construction back to rol levels
    def cons_inc_rol(self, data):

        temp = data.copy()
        total_add = 0
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        temp = temp[(temp['cons'] < temp['rolscon']) & (temp['cons'] < round(temp['t'], self.round_val)) & ((temp['rolscon'] - temp['cons']) > (temp['rol_h'] - temp['h'])) & ((data['rolscon'] - data['cons']) > (data['rol_e'] - data['e']))]
        if len(temp) > 0:
            if self.year == self.curryr:
                temp['ratio_test_target'] = round((temp['e'] * temp['e_thresh']) - (temp['cons'] - temp['round_h_temp']), self.round_val)
                temp['diff'] = np.where(((((temp['rolscon'] - temp['cons']) - (temp['rol_h'] - temp['h'])) + (temp['cons'] - temp['round_h_temp'])) / temp['e'] > temp['e_thresh']), temp['ratio_test_target'], (temp['rolscon'] - temp['cons']) - (temp['rol_h'] - temp['h']))
                temp = temp[temp['diff'] > 0]
            else:
                temp['diff'] = (temp['rolscon'] - temp['cons']) - (temp['rol_h'] - temp['h'])
            if len(temp) > 0:
                temp['diff'] = np.where((round(temp['cons'] + temp['diff'], self.round_val) > round(temp['t'], self.round_val)) & (temp['yr'] == self.curryr), temp['t'], temp['diff'])
                temp.sort_values(by=['diff'], ascending=[True], inplace=True)
                total_add = temp['diff'].sum()

            return self.execute_global_shim(total_add, temp, data)

    # Check if there is historical support to increase the construction level, as well as pipeline support
    def cons_inc_hist(self, data):
        
        if self.override:
            iters = 2
        else:
            iters = 1

        total_add = 0

        for iter in range(0, iters):
            
            if iters == 1:
                data['e_thresh_over'] = np.where(data['forecast_tag'] == 1, np.nan, 0.75)
                data['e_thresh_over'] = np.where((self.currqtr == 1) & (data['forecast_tag'] == 1), 0.45, data['e_thresh_over'])
                data['e_thresh_over'] = np.where((self.currqtr == 2) & (data['forecast_tag'] == 1), 0.4, data['e_thresh_over'])
                data['e_thresh_over'] = np.where((self.currqtr == 3) & (data['forecast_tag'] == 1), 0.3, data['e_thresh_over'])
                data['e_thresh_over'] = np.where((self.currqtr == 4) & (data['forecast_tag'] == 1), 0.5, data['e_thresh_over'])
                e_thresh_use = 'e_thresh_over'
            else:
                e_thresh_use = 'e_thresh'
            
            temp = data.copy()
            temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
            temp = temp[(temp['cons'] < temp['three_yr_avg_cons']) & (temp['cons'] < temp['round_t_temp']) & ((temp['cons'] - temp['round_h_temp']) / temp['e'] < temp[e_thresh_use])]
            if len(temp) > 0:
                temp['diff'] = np.where((temp['three_yr_avg_cons'] / temp['e'] <= temp['e_thresh']), temp['three_yr_avg_cons'] - temp['cons'], (round(temp['e'] * temp[e_thresh_use], self.round_val)) - (temp['cons'] - temp['round_h_temp']))
                temp['diff'] = round(temp['diff'], self.round_val)
                if not self.override:
                    temp['diff'] = np.where((temp['diff'] + temp['cons'] > temp['rolscon']), temp['rolscon'] - temp['cons'], temp['diff'])
                temp = temp[temp['diff'] > 0]
                if len(temp) > 0:
                    temp.sort_values(by=['diff'], ascending=[True], inplace=True)
                    total_add = temp['diff'].sum()

            return self.execute_global_shim(total_add, temp, data)

    # Check if there are submarkets that are above t stock
    def cons_decr_t(self, data):

        temp = data.copy()
        total_decr = 0
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        temp = temp[(temp['cons'] > temp['round_t_temp'])]
        if len(temp) > 0:
            temp['diff'] = temp['round_t_temp'] - temp['cons']
            temp['diff'] = round(temp['diff'], self.round_val)
            if len(temp) > 0:
                temp.sort_values(by=['diff'], ascending=[False], inplace=True)
                total_decr = temp['diff'].sum()

        return self.execute_global_shim(total_decr, temp, data)

    # Check if there are submarkets where we can decrease the construction back to rol levels
    def cons_decr_rol(self, data):

        temp = data.copy()
        total_decr = 0
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        temp = temp[(temp['cons'] > temp['rolscon']) & (temp['cons'] > round(temp['round_h_temp'], self.round_val))]
        if len(temp) > 0:
            temp['diff'] = (temp['rolscon'] - temp['cons']) - (temp['rol_h'] - temp['h'])
            if len(temp) > 0:
                temp['diff'] = np.where((temp['rolscon'] > temp['round_h_temp']), temp['rolscon'] - temp['cons'], temp['round_h_temp'] - temp['cons'])
                temp['diff'] = round(temp['diff'], self.round_val)
                temp.sort_values(by=['diff'], ascending=[True], inplace=True)
                total_decr = temp['diff'].sum()

        return self.execute_global_shim(total_decr, temp, data)
    
    # Check if there are submarkets that are above their historical construction average, if lack of pipeline support
    def cons_decr_sup(self, data):

        temp = data.copy()
        total_decr = 0
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        temp = temp[(temp['cons'] > temp['three_yr_avg_cons']) & (temp['cons'] > temp['round_h_temp'])]
        if len(temp) > 0:
            temp['diff'] = np.where((temp['three_yr_avg_cons'] > temp['round_h_temp']), temp['three_yr_avg_cons'] - temp['cons'], temp['round_h_temp'] - temp['cons'])
            temp['diff'] = round(temp['diff'], self.round_val)
            if len(temp) > 0:
                temp.sort_values(by=['diff'], ascending=[False], inplace=True)
                total_decr = temp['diff'].sum()

        return self.execute_global_shim(total_decr, temp, data)

    # Check if there are submarkets where we can decrease the vacancy in cases where it is currently above the historical max
    def vac_decr_max(self, data):

        temp = data.copy()
        total_decr = 0
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        if self.currqtr == 4 or self.year > self.curryr:
            temp = temp[(temp['vac'] > temp['max_vac']) & (temp['vac_chg'] >= self.cap)]
        else:
            temp = temp[(temp['vac'] > temp['max_vac']) & (temp['implied_vac_chg'] >= self.cap)]

        if len(temp) > 0:
            temp['diff'] = np.where((temp['max_vac'] - temp['vac'] >= self.cap), round((temp['max_vac'] - temp['vac']) * temp['inv'], self.round_val), round(((temp['vac'] + self.cap) - temp['vac']) * temp['inv'], self.round_val))
            temp.sort_values(by=['diff'], ascending=[False], inplace=True)
            total_decr = temp['diff'].sum()

        return self.execute_global_shim(total_decr, temp, data)

    # Check if there are submarkets where we can decrease the vacancy in cases where it is above the 10 year vac level
    def vac_decr_level(self, data):

        temp = data.copy()
        total_decr = 0
        temp = temp[(temp['yr'] == self.year) & (temp['qtr'] == 5) & (temp['subsector'] == self.subsector) & (temp['identity_us'] == self.roll_val)]
        temp = temp[(temp['vac'] > temp['10_yr_vac']) & (temp['vac_chg'] >= self.cap)]
        if len(temp) > 0:
            temp['diff'] = np.where((temp['10_yr_vac'] - temp['vac'] >= self.cap), round((temp['10_yr_vac'] - temp['vac']) * temp['inv'], self.round_val), round(((temp['vac'] + self.cap) - temp['vac']) * temp['inv'], self.round_val))
            temp.sort_values(by=['diff'], ascending=[False], inplace=True)
            total_decr = temp['diff'].sum()

        return self.execute_global_shim(total_decr, temp, data)


    def execute_global_shim(self, total_adjust, temp, data_in):
    
        if len(temp) == 0:
            data = data_in.copy()
            achieved_target = False
            self.change = False
        else:
            data = data_in.copy()

            if self.var == 'Cons':
                var = 'cons'
                indicator = 'c'
            elif self.var == 'Vac':
                var = 'avail'
                indicator = 'v'
            elif self.var == 'Gmrent':
                indicator = 'g'
            elif self.var == "Gap":
                indicator = 'e'

            if self.sector_val == "apt":
                min_val = 1
            else:
                min_val = 1000

            print("Total adjust:", total_adjust)
            print("Diff to Target", self.diff_to_target)
            if (total_adjust <= self.diff_to_target and total_adjust > 0) or (total_adjust >= self.diff_to_target and total_adjust < 0):
                
                self.change = True
                
                for index, row in temp.iterrows():
                    
                    diff = row['diff']

                    if total_adjust < 0 and var == 'cons':
                        if row['cons'] + diff < self.thresh:
                            diff = row['cons'] * -1
                    
                    if diff >= self.thresh or row['cons'] != 0 or total_adjust < 0 or var != 'cons':

                        if total_adjust > 0:
                            sub_chg = max(round(diff, self.round_val), min_val)
                        elif total_adjust < 0:
                            sub_chg = min(round(diff, self.round_val), (min_val * -1))

                        print("Sub Chg:", sub_chg)
                        display(data.loc[row['identity'] + str(self.year) + '5']['identity'])
                        display(data.loc[row['identity'] + str(self.year) + '5'][var])

                        if self.coeff_status:
                            data = insert_fix_coeffs(data, row['identity'] + str(self.year) + '5', row['identity'], row[var] + sub_chg, indicator, self.year, self.curryr, self.currqtr, self.sector_val, 'c')
                        else:
                            data = insert_fix(data, row['identity'] + str(self.year) + '5', row['identity'], row[var] + sub_chg, indicator, self.year, self.curryr, self.currqtr, self.sector_val, 'c')
            
                        data['global_change'] = np.where(data['identity'] == row['identity'], True, data['global_change'])
                        
                        display(data.loc[row['identity'] + str(self.year) + '5'][var])
                        
                        self.diff_to_target = self.diff_to_target - sub_chg
                
                achieved_target = False
            
            else:
                subs_left = len(temp)
                for index, row in temp.iterrows():

                    diff = row['diff']

                    if total_adjust < 0 and var == 'cons':
                        if row['cons'] + diff < self.thresh:
                            diff = row['cons'] * -1       
                    
                    if total_adjust < 0:
                        per_sub_chg = max(round(self.diff_to_target / subs_left, self.round_val), min_val)
                        sub_chg = max(min(per_sub_chg, round(diff, self.round_val)), min_val)
                    else:
                        per_sub_chg = min(round(self.diff_to_target / subs_left, self.round_val), (min_val * -1))
                        sub_chg = min(max(per_sub_chg, round(diff, self.round_val)), (min_val * -1))
                    
                    subs_left = subs_left - 1
                    
                    if diff >= self.thresh or row['cons'] != 0 or total_adjust < 0 or var != 'cons':
                        display(data.loc[row['identity'] + str(self.year) + '5']['identity'])
                        print("Sub Chg:", sub_chg)
                        display(data.loc[row['identity'] + str(self.year) + '5'][var])
                        
                        if self.coeff_status:
                            data = insert_fix_coeffs(data, row['identity'] + str(self.year) + '5', row['identity'], row[var] + sub_chg, indicator, self.year, self.curryr, self.currqtr, self.sector_val, 'c')
                        else:
                            data = insert_fix(data, row['identity'] + str(self.year) + '5', row['identity'], row[var] + sub_chg, indicator, self.year, self.curryr, self.currqtr, self.sector_val, 'c')
            
                        data['global_change'] = np.where(data['identity'] == row['identity'], True, data['global_change'])
                        
                        self.diff_to_target = self.diff_to_target - sub_chg
                        
                        display(data.loc[row['identity'] + str(self.year) + '5'][var])
                        print("Diff to target:", self.diff_to_target)
                        
                        if not self.change:
                            self.change = True
                    
                    if (self.diff_to_target <= 0 and total_adjust > 0) or (self.diff_to_target >= 0 and total_adjust < 0):
                        break
                    
                achieved_target = True

                print("New total:", data[(data['expansion'] == 'Leg') & (data['subsector'] == 'DW') & (data['yr'] == self.year) & (data['qtr'] == 5)][var].sum())
    
        return data, achieved_target, self.change



def get_global_sum_flags(global_data, global_trigger, data, init_global_flags, flag_cols):

    global_data = pd.DataFrame.from_dict(global_data)
    subsector = global_data.loc[0]['Subsector']
    year = global_data.loc[0]['Year']

    new_global_flags = {}
    for i in range(0, 2):
        new_flags_temp = []
        for var in ['c', 'v', 'g', 'e']:
            
            temp = data.copy()
            temp = temp[(temp['subsector'] == subsector) & (temp['expansion'] == 'Leg')]
            if i == 0:
                temp = temp[temp['yr'] == year]
            temp[flag_cols] = np.where((temp[flag_cols] != 0), 1, temp[flag_cols])
            temp['{}_flag_tot'.format(var)] = temp.filter(regex="^{}_flag*".format(var)).sum(axis=1)
            temp['{}_flag_sum'.format(var)] = temp['{}_flag_tot'.format(var)].sum()
            new_sum_flags = temp.reset_index().loc[0]['{}_flag_sum'.format(var)]
            new_flags_temp.append(new_sum_flags)
        if i == 0:
            new_global_flags[str(year)] = new_flags_temp
        else:
            new_global_flags['All'] = new_flags_temp

    flag_sum_table = pd.DataFrame()
    cond_style = []
    for i in range(0, 2):
        if i == 0:
            key_var = str(year)
        else:
            key_var = 'All'
        row_data = [key_var]
        c_flag_diff = new_global_flags[str(key_var)][0]  - init_global_flags[str(key_var)][0]
        v_flag_diff = new_global_flags[str(key_var)][1]  - init_global_flags[str(key_var)][1]
        g_flag_diff = new_global_flags[str(key_var)][2]  - init_global_flags[str(key_var)][2]
        e_flag_diff = new_global_flags[str(key_var)][3]  - init_global_flags[str(key_var)][3]

        for var, amt in zip(['Cons', 'Vac', 'Gmrent', 'Gap'], [c_flag_diff, v_flag_diff, g_flag_diff, e_flag_diff]):

            if amt > 0:
                indicator = '+' + str(int(abs(amt)))
                color = 'red'
            elif amt < 0:
                indicator = '-' + str(int(abs(amt)))
                color = 'forestgreen'
            elif amt == 0:
                indicator = '+' + str(int(abs(amt)))
                color = 'black'
            row_data.append(indicator) 
            style_temp = {'if': {'column_id': str(var), 'row_index':i}, 'color': color, 'width': '20%'}
            cond_style.append(style_temp)     

        flag_sum_table = flag_sum_table.append([row_data])
    flag_sum_table.columns=['Year', 'Cons', 'Vac', 'Gmrent', 'Gap']

    return flag_sum_table, cond_style
