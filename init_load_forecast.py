from pathlib import Path
import pandas as pd
import numpy as np
from IPython.core.display import display, HTML
import sys
import os
from os import listdir
from os.path import isfile, join
from datetime import datetime
import math

def get_home():
    if os.name == "nt": return "//odin/reisadmin/"
    else: return "/home/"

def initial_load(sector_val, curryr, currqtr, fileyr):

    if currqtr == 4:
        pastyr = str(curryr - 1)
        pastqtr = str(currqtr - 1)
    elif currqtr == 1:
        pastyr =  str(curryr - 1)
        pastqtr = str(4)
    else:
        pastyr = str(curryr)
        pastqtr = str(currqtr - 1)

    # Load the input file - if this is the first time the program is run, the oob data should be loaded in, and if this is not the first time, then the edits data should be loaded in
    file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_mostrecentsave.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
    isFile = os.path.isfile(file_path)
    if isFile == True: 
        oob_edits = pd.read_pickle(file_path)
        file_used = "edits"
        print("Using Saved File")
    else:
        file_used = "oob"
        print("Initial Load")
    
    if sector_val == "ind":
        data = pd.DataFrame()
        data_p = pd.DataFrame()
        for subsector in ["DW", "F"]:
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/InputFiles/{}subdiag_{}_{}q{}_OOB.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val, subsector, str(fileyr), str(currqtr)))
            file_path_p = Path("{}central/subcast/data/{}/forecast/current/{}subtest_{}_{}q{}.dta".format(get_home(), sector_val, sector_val, subsector, str(pastyr), str(pastqtr)))
            data_in = pd.read_csv(file_path, encoding = 'utf-8',  na_values= "", keep_default_na = False)
            data_in_p = pd.read_stata(file_path_p)
            cols = list(data_in.columns)
            data_in['subsector'] = subsector
            data_in = data_in[['subsector'] + cols]
            data = data.append(data_in, ignore_index=True)
            cols = list(data_in_p.columns)
            data_in_p['subsector'] = subsector
            data_in_p = data_in_p[['subsector'] + cols]
            data_p = data_p.append(data_in_p, ignore_index=True)
    elif sector_val != "ind":
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/InputFiles/{}subdiag_{}q{}_OOB.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val, str(fileyr), str(currqtr)))
        file_path_p = Path("{}central/subcast/data/{}/forecast/current/{}subtest_{}q{}.dta".format(get_home(), sector_val, sector_val, str(pastyr), str(pastqtr)))
        data = pd.read_csv(file_path, encoding = 'utf-8',  na_values= "", keep_default_na = False)
        data_p = pd.read_stata(file_path_p)
        cols = list(data.columns)
        data['subsector'] = sector_val.title()
        data = data[['subsector'] + cols]

    # Convert vars to correct types explicitly here, as read csv may have inferred them incorrectly
    data['subid'] = data['subid'].astype(int)
    data['yr'] = data['yr'].astype(int)
    data['qtr'] = data['qtr'].astype(int)
    
    # Remove extra columns in the initial input that are not used - not sure what they are used for, perhaps to calculate some of the forecast - to reduce dataframe dimensionality
    # But save them so they can be rejoined when finalizing for econ
    if file_used == "oob":
        if sector_val != "ind":
            drop_list = ['Bcon', 'rolcons', 'Babs', 'Brolabs', 'Bvac', 'rolvac', 'Bmrent', 'rolmrent', 'G_Bmrent', 'Bmerent', 'Brolmeren', 'G_Bmerent', 'Bgap', 'Brolgap']
            data_drop = data.copy()
            data_drop = data_drop[drop_list + ['metcode', 'subid', 'yr', 'qtr']]
            drop_file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_dropped_cols.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
            data_drop.to_pickle(drop_file_path)
            data = data.drop(drop_list, axis=1)
            data = data.rename(columns={'rolsmre': 'rolmrent'})
        if sector_val == "apt":
            data = data.rename(columns={'rolmere': 'rolmerent'})
        if sector_val == 'ind':
            data = data.rename(columns={'rolmeren': 'rolmerent'})
    
        # Code is not set up to handle a quarterly forecast, only an annual one. If we eventually do publish quarterly forecast, there will need to be a lot of revisions to the code to handle that...
        # For now, will just drop quarterly forecast rows here
        data['quarterly_row'] = np.where((data['yr'] > curryr) & (data['qtr'] != 5), 1, 0)
        data['quarterly_row'] = np.where((data['yr'] == curryr) & (data['qtr'] > currqtr) & (data['qtr'] != 5), 1, data['quarterly_row'])
        if currqtr == 4:
            data['quarterly_row'] = np.where((data['yr'] == curryr) & (data['qtr'] != 5), 1, data['quarterly_row'])
        data.drop(data[data['quarterly_row'] == 1].index, inplace = True) 
        data = data.drop(['quarterly_row'], axis=1)
    
        if sector_val == "apt" or sector_val == "off" or sector_val == "ret":
            data['avail'] = data['inv'] - data['occ']

        # Create the oob columns needed for graphs
        data['inv_oob'] = data['inv']
        data['avail_oob'] = data['avail']
        data['occ_oob'] = data['occ']
        data['mrent_oob'] = data['mrent']
        data['merent_oob'] = data['merent']
        if currqtr == 4:
            shift_period = 1
        else: 
            shift_period = currqtr + 1
        data['vac_chg_oob'] = np.where((data['yr'] == curryr) & (data['qtr'] == 5), data['vac_oob'] - data['vac'].shift(shift_period), np.nan)
        data['vac_chg_oob'] = np.where((data['yr'] > curryr) & (data['qtr'] == 5), data['vac_oob'] - data['vac'].shift(1), data['vac_chg_oob'])
        data['ask_chg_oob'] = np.where((data['yr'] == curryr) & (data['qtr'] == 5), (data['mrent_oob'] - data['mrent'].shift(shift_period)) /  data['mrent'].shift(shift_period), np.nan)
        data['ask_chg_oob'] = np.where((data['yr'] > curryr) & (data['qtr'] == 5), (data['mrent_oob'] - data['mrent'].shift(1)) /  data['mrent'].shift(1), data['ask_chg_oob'])
        
        # Create a column that will keep track if the user overrides a flag and does not think a change is warranted
        data['flag_skip'] = ''

        # Create columns to store the shim comments
        data['cons_comment'] = ""
        data['avail_comment'] = ""
        data['rent_comment'] = ""

        orig_cols = list(data.columns)
    
    # If this is not the first time the program is run for the quarter, append the edits file to the deep history file so that the changes already implemented are now included
    deep_file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_deep_hist.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
    if file_used == 'edits':
        orig_cols = list(oob_edits.columns)
        data = pd.read_pickle(deep_file_path)
        data = data[data['yr'] >= curryr - 6]
        data = data.drop(['rolsinv'], axis=1)
        if sector_val == "off" or sector_val == "ret":
            data = data.drop(['rolmerent'], axis=1)
        data = data.append(oob_edits)
        data['subid'] = data['subid'].astype(int)
        data['yr'] = data['yr'].astype(int)
        data['qtr'] = data['qtr'].astype(int)
        data.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace=True)
        data = data.reset_index()
        data = data.drop(['index'], axis=1)
    else:
        deep_hist = data.copy()
        deep_hist = deep_hist[deep_hist['yr'] < curryr - 6]
        data_p_deep = data_p.copy()
        data_p_deep['subid'] = data_p_deep['subid'].astype(int)
        data_p_deep['yr'] = data_p_deep['yr'].astype(int)
        data_p_deep['qtr'] = data_p_deep['qtr'].astype(int)
        if sector_val == "ind":
            data_p_deep['identity_row'] = data_p_deep['metcode'] + data_p_deep['subid'].astype(str) + data_p_deep['subsector'] + data_p_deep['yr'].astype(str) + data_p_deep['qtr'].astype(str)
            deep_hist['identity_row'] = deep_hist['metcode'] + deep_hist['subid'].astype(str) + deep_hist['subsector'] + deep_hist['yr'].astype(str) + deep_hist['qtr'].astype(str)
        else:
            data_p_deep['identity_row'] = data_p_deep['metcode'] + data_p_deep['subid'].astype(str) + sector_val.title() + data_p_deep['yr'].astype(str) + data_p_deep['qtr'].astype(str)
            deep_hist['identity_row'] = deep_hist['metcode'] + deep_hist['subid'].astype(str) + sector_val.title() + deep_hist['yr'].astype(str) + deep_hist['qtr'].astype(str)

        data_p_deep = data_p_deep.set_index('identity_row')
        data_p_deep = data_p_deep.rename(columns={'inv': 'rolsinv', 'merent': 'rolmerent'})
        if sector_val == "apt" or sector_val == "ind":
            data_p_deep = data_p_deep[['rolsinv']]
        else:
            data_p_deep = data_p_deep[['rolsinv', 'rolmerent']]
        deep_hist = deep_hist.join(data_p_deep, on='identity_row')
        deep_hist = deep_hist.drop(['identity_row'], axis=1)
        deep_hist.to_pickle(deep_file_path)

    # Label Submarkets as Legacy or Expansion Metros for Industrial, as Expansion metros wont have a Flex cut
    ind_expansion_list = ["AA", "AB", "AK", "AN", "AQ", "BD", "BF", "BI", "BR", "BS", "CG", "CM", "CN", "CS", "DC", 
                    "DM", "DN", "EP", "FC", "FM", "FR", "GD", "GN", "GR", "HR", "HL", "HT", "KX", "LL", "LO", 
                    "LR", "LV", "LX", "MW", "NF", "NM", "NO", "NY", "OK", "OM", "PV", "RE", "RO", "SC", "SH", 
                    "SR", "SS", "ST", "SY", "TC", "TM", "TO", "TU", "VJ", "VN", "WC", "WK", "WL", "WS"]    

    if sector_val == "ind":
        data['expansion'] = np.where(data['metcode'].isin(ind_expansion_list), "Exp", "Leg")
        data = data[(data['expansion'] == "Leg") | (data['subsector'] == "DW")]
    else:
        data['expansion'] = "Leg"

    # Create an identity to join the ecodemo data to the main dataset
    data['identity_eco'] = data['metcode'] + data['yr'].astype(str) + data['qtr'].astype(str)
    
    # Load the economic data on employment change and join it to the main dataset
    eco_file_path_curr = Path("{}central/metcast/data/rfa/current/rfa_{}q{}_final.dta".format(get_home(), fileyr, currqtr))
    if currqtr == 1:
        yr_past = str(curryr - 1)
        qtr_past = "4"
    elif currqtr == 4:
        yr_past = str(curryr - 1)
        qtr_past = str(currqtr - 1)
    else:
        yr_past = str(curryr)
        qtr_past = str(currqtr - 1)
    eco_file_path_past = Path("{}central/metcast/data/rfa/current/rfa_{}q{}_final.dta".format(get_home(), yr_past, qtr_past))
    ecodemo_curr = pd.read_stata(eco_file_path_curr, columns=['metcode', 'yr', 'qtr', 'qfet', 'offemp', 'indemp', 'avginc'])
    ecodemo_curr = ecodemo_curr.rename(columns={'qfet': 'totalemp_c', 'offemp': 'officeemp_c', 'indemp': 'indusemp_c', 'avginc': 'avg_inc'})
    ecodemo_past = pd.read_stata(eco_file_path_past, columns=['metcode', 'yr', 'qtr', 'qfet', 'offemp', 'indemp', 'avginc'])
    ecodemo_past = ecodemo_past.rename(columns={'qfet': 'totalemp_p', 'offemp': 'officeemp_p', 'indemp': 'indusemp_p',  'avginc': 'avg_inc_p'})
    ecodemo_curr['identity_eco'] = ecodemo_curr['metcode'] + ecodemo_curr['yr'].astype(str) + ecodemo_curr['qtr'].astype(str)
    ecodemo_curr = ecodemo_curr.set_index('identity_eco')
    ecodemo_past['identity_eco'] = ecodemo_past['metcode'] + ecodemo_past['yr'].astype(str) + ecodemo_past['qtr'].astype(str)
    ecodemo_past = ecodemo_past[['identity_eco', 'totalemp_p', 'officeemp_p', 'indusemp_p', 'avg_inc_p']]
    ecodemo_past = ecodemo_past.set_index('identity_eco')
    ecodemo = ecodemo_curr.join(ecodemo_past)
    ecodemo.sort_values(by=['metcode', 'yr', 'qtr'], inplace=True)

    # Only keep metros that have a published forecast
    data['has_f'] = 1
    ecodemo = ecodemo.join(data.drop_duplicates('metcode').set_index('metcode')[['has_f']], on='metcode')
    ecodemo = ecodemo[(ecodemo['has_f'].isnull() == False) | (ecodemo['metcode'] == "US")]
    data = data.drop(['has_f'],axis=1)
    
    # Determine the relvant employment categories based on the sector being analyzed
    ecodemo = ecodemo.rename(columns={'totalemp_c': 'emp', 'totalemp_p': 'rol_emp'})
    if sector_val == "apt" or sector_val == "ret":
        ecodemo = ecodemo.drop(['officeemp_p', 'officeemp_c', 'indusemp_p', 'indusemp_c'], axis=1)
    elif sector_val == "off":
        ecodemo = ecodemo.drop(['indusemp_p', 'indusemp_c'], axis=1)
        ecodemo = ecodemo.rename(columns={'officeemp_c': 'off_emp', 'officeemp_p': 'rol_off_emp'})
    elif sector_val == "ind":
        ecodemo = ecodemo.drop(['officeemp_p', 'officeemp_c'], axis=1)
        ecodemo = ecodemo.rename(columns={'indusemp_c': 'ind_emp', 'indusemp_p': 'rol_ind_emp'})
    
    ecodemo = ecodemo.rename(columns={'avg_inc_p': 'rol_avg_inc'})
    
    compute_list = ['emp', 'rol_emp', 'avg_inc']
    name_list = ['emp_chg', 'rol_emp_chg', 'avg_inc_chg']
    if sector_val == "off":
        compute_list += ['off_emp', 'rol_off_emp']
        name_list += ['off_emp_chg', 'rol_off_emp_chg']
    elif sector_val == "ind":
        compute_list += ['ind_emp', 'rol_ind_emp']
        name_list += ['ind_emp_chg', 'rol_ind_emp_chg']
    for var, name in zip(compute_list, name_list):
        ecodemo[name] = np.where((ecodemo['metcode'] == ecodemo['metcode'].shift(5)) & (ecodemo['qtr'] == 5) & (ecodemo['qtr'].shift(1) != 5), (ecodemo[var] - ecodemo[var].shift(5)) / ecodemo[var].shift(5), np.nan)
        ecodemo[name] = np.where((ecodemo['metcode'] == ecodemo['metcode'].shift(1)) & (ecodemo['qtr'] == 5) & (ecodemo['qtr'].shift(1) == 5) & (ecodemo['qtr'].shift(1) != 4), (ecodemo[var] - ecodemo[var].shift(1)) / ecodemo[var].shift(1), ecodemo[name])
        ecodemo[name] = np.where((ecodemo['metcode'] == ecodemo['metcode'].shift(1)) & (ecodemo['qtr'] != 5), (ecodemo[var] - ecodemo[var].shift(1)) / ecodemo[var].shift(1), ecodemo[name])
        ecodemo[name] = round(ecodemo[name], 3)
    
    if sector_val == "apt" or sector_val == "ret":
        ecodemo['emp_chg_diff'] = ecodemo['emp_chg'] - ecodemo['rol_emp_chg']
    elif sector_val == "off":
        ecodemo['emp_chg_diff'] = ecodemo['off_emp_chg'] - ecodemo['rol_off_emp_chg']
    elif sector_val == "ind":
        ecodemo['emp_chg_diff'] = ecodemo['ind_emp_chg'] - ecodemo['rol_ind_emp_chg']
    
    if sector_val == "apt" or sector_val == "ret":
        emp_to_use = "emp_chg"
    elif sector_val == "off":
        emp_to_use = "off_emp_chg"
    elif sector_val == "ind":
        emp_to_use = "ind_emp_chg"

    # Calculate the z-score for each forecast year's employment change to assess if the economic conditions do not warrant benchmarking against the recent trend history
    # Do this here so we can use the full ecodemo history for years we dont have trend data on
    ecodemo['forecast_tag'] = np.where((ecodemo['yr'] >= curryr) & (ecodemo['qtr'] == 5), 1, 0)
    ecodemo['identity_all'] = "US"
    ecodemo['absolute_emp_chg'] = abs(ecodemo[emp_to_use])
    avg_emp = pd.DataFrame(ecodemo[(ecodemo['qtr'] == 5) & ecodemo['forecast_tag'] == 0].groupby('metcode')['absolute_emp_chg'].mean())
    avg_emp.columns = ['avg_emp_chg']
    ecodemo = ecodemo.join(avg_emp, on="metcode")
    ecodemo['avg_emp_chg'] = round(ecodemo['avg_emp_chg'], 4)
    std_dev_emp_chg = pd.DataFrame(ecodemo[(ecodemo['qtr'] == 5) & (ecodemo['forecast_tag'] == 0)].groupby('metcode')['absolute_emp_chg'].std(ddof=0))
    std_dev_emp_chg.columns = ['std_dev_emp_chg']
    std_dev_emp_chg['std_dev_emp_chg'] = np.where((std_dev_emp_chg.std_dev_emp_chg < 0.000005) & (std_dev_emp_chg.std_dev_emp_chg > 0), 0, std_dev_emp_chg['std_dev_emp_chg'])
    ecodemo = ecodemo.join(std_dev_emp_chg, on="metcode")
    ecodemo['std_dev_emp_chg'] = round(ecodemo['std_dev_emp_chg'], 4)
    ecodemo['emp_chg_z'] = np.where((ecodemo['yr'] == curryr) | (ecodemo['yr'] == curryr + 1), (ecodemo['emp_chg'] - ecodemo['avg_emp_chg']) / ecodemo['std_dev_emp_chg'], np.nan)
    ecodemo['emp_chg_z'] = np.where((ecodemo['yr'] > curryr + 1) & (ecodemo['metcode'] == "US"), (ecodemo['emp_chg'] - ecodemo['avg_emp_chg']) / ecodemo['std_dev_emp_chg'], ecodemo['emp_chg_z'])
    ecodemo['emp_chg_z'] = round(ecodemo['emp_chg_z'], 1)

    # Calculate the implied employment change for the current forecast year
    ecodemo['identity_fill'] = ecodemo['metcode'] + str(curryr) + str(currqtr)
    
    ecodemo['implied_' + emp_to_use] = np.where((ecodemo['yr'] == curryr) & (ecodemo['qtr'] == 5), (ecodemo[emp_to_use[:-4]] - ecodemo[emp_to_use[:-4]].shift(periods=5-currqtr)) / ecodemo[emp_to_use[:-4]].shift(periods=5-currqtr), np.nan)
    if currqtr == 4:
        ecodemo['implied_' + emp_to_use] = np.nan
    ecodemo['implied_' + emp_to_use] = round(ecodemo['implied_' + emp_to_use], 3)

    # Calculate the implied avg income change for the current forecast year
    ecodemo['implied_avg_inc_chg'] = np.where((ecodemo['yr'] == curryr) & (ecodemo['qtr'] == 5), (ecodemo['avg_inc'] - ecodemo['avg_inc'].shift(periods=5-currqtr)) / ecodemo['avg_inc'].shift(periods=5-currqtr), np.nan)
    if currqtr == 4:
        ecodemo['implied_avg_inc_chg'] = np.nan
    ecodemo['implied_avg_inc_chg'] = round(ecodemo['implied_avg_inc_chg'], 3)

    if sector_val == "apt" or sector_val == "ret":
        ecodemo['emp_chg'] = round(ecodemo['emp_chg'], 4)       
    elif sector_val == "off":
        ecodemo['off_emp_chg'] = round(ecodemo['off_emp_chg'], 4)
    elif sector_val == "ind":
        ecodemo['ind_emp_chg'] = round(ecodemo['ind_emp_chg'], 4)

    def get_quarts(ecodemo, variable, variable_name, curryr, currqtr, quartiles, quart_names):
        for x, y in zip(quartiles, quart_names):
            # Calc quarts based on full year emp, not implied in curryr (as opposed to cre vars) since cre vars will lag emp
            if 0.50 in quartiles:
                emp_quarts = pd.DataFrame(ecodemo[(ecodemo['yr'] >= curryr) & (ecodemo['qtr'] == 5)].groupby('yr')[variable].quantile(x))
                emp_quarts.columns = [y]
                ecodemo = ecodemo.join(emp_quarts, on='yr')
            
            else:
                emp_quarts = pd.DataFrame(ecodemo[(ecodemo['yr'] < curryr) & (ecodemo['qtr'] == 5)].groupby('metcode')[variable].quantile(x))
                emp_quarts.columns = [y]
                ecodemo = ecodemo.join(emp_quarts, on='metcode')
        
        if 0.50 in quartiles:
            ecodemo[variable_name] = np.where(ecodemo[variable] < ecodemo['emp_25'], 4, 1)
            ecodemo[variable_name] = np.where((ecodemo[variable] < ecodemo['emp_50']) & (ecodemo[variable] >= ecodemo['emp_25']), 3, ecodemo[variable_name])
            ecodemo[variable_name] = np.where((ecodemo[variable] < ecodemo['emp_75']) & (ecodemo[variable] >= ecodemo['emp_50']), 2, ecodemo[variable_name])
            ecodemo = ecodemo.drop(['emp_25', 'emp_50', 'emp_75'], axis=1)

        return ecodemo

    if sector_val == "apt" or sector_val == "ret":
        ecodemo = get_quarts(ecodemo, 'emp_chg', 'emp_quart', curryr, currqtr, [0.05, 0.25, 0.50, 0.75, 0.95], ['emp_5', 'emp_25', 'emp_50', 'emp_75', 'emp_95'])
        ecodemo = get_quarts(ecodemo, 'emp_chg', 'emp_quart', curryr, currqtr, [0.10, 0.90], ['hist_emp_10', 'hist_emp_90'])
    elif sector_val == "off":
        ecodemo = get_quarts(ecodemo, 'off_emp_chg', 'off_emp_quart', curryr, currqtr, [0.05, 0.25, 0.50, 0.75, 0.95], ['emp_5', 'emp_25', 'emp_50', 'emp_75', 'emp_95'])
        ecodemo = get_quarts(ecodemo, 'off_emp_chg', 'off_emp_quart', curryr, currqtr, [0.10, 0.90], ['hist_emp_10', 'hist_emp_90'])
    elif sector_val == "ind":
        ecodemo = get_quarts(ecodemo, 'ind_emp_chg', 'ind_emp_quart', curryr, currqtr, [0.05, 0.25, 0.50, 0.75, 0.95], ['emp_5', 'emp_25', 'emp_50', 'emp_75', 'emp_95'])
        ecodemo = get_quarts(ecodemo, 'ind_emp_chg', 'ind_emp_quart', curryr, currqtr, [0.10, 0.90], ['hist_emp_10', 'hist_emp_90'])

    keep_list = ['emp_chg', 'rol_emp_chg', 'emp_chg_diff', 'avg_inc', 'avg_inc_chg', 'avg_emp_chg', 'std_dev_emp_chg', 'emp_chg_z', 'implied_avg_inc_chg']
    if sector_val == "apt" or sector_val == "ret":
        keep_list += ['emp', 'rol_emp', 'implied_emp_chg', 'emp_quart']
    elif sector_val == "off":
        keep_list += ['off_emp', 'implied_off_emp_chg', 'off_emp_chg', 'rol_off_emp', 'rol_off_emp_chg', 'off_emp_quart']
    elif sector_val == "ind":
        keep_list += ['ind_emp', 'implied_ind_emp_chg', 'ind_emp_chg', 'rol_ind_emp', 'rol_ind_emp_chg', 'ind_emp_quart']
    
    nat_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/intermediatefiles/nat_eco_data_{}.pickle".format(get_home(), sector_val))
    ecodemo[(ecodemo['metcode'] == 'US') & (ecodemo['yr'] >= curryr) & (ecodemo['qtr'] == 5)][keep_list + ['yr']].to_pickle(nat_path)
    
    ecodemo = ecodemo[keep_list + ['emp_5', 'emp_95', 'hist_emp_10', 'hist_emp_90']]
    data = data.join(ecodemo, on=("identity_eco"))
    
    # Create the submarket groupby identity
    data['identity'] = data['metcode'] + data['subid'].astype(str) + data['subsector']

    # Create the metro groupby identity
    data['identity_met'] = data['metcode'] + data['subsector']
    
    # Create a variable that we can use to rollup to the US level
    if sector_val == "ind":
        data['identity_us'] = "US" + data['subsector'] + data['expansion']
        data['identity_us_notier'] = "US" + data['subsector']
    else:
        data['identity_us'] = np.where((data['metcode'].isin(['PV', 'NO', 'WS'])), "US2", "US1")
        data['identity_us_notier'] = "US1"
    
    # Create the row identity
    data['identity_row'] = data['metcode'] + data['subid'].astype(str) + data['subsector'] + data['yr'].astype(str) + data['qtr'].astype(str)
    
    # set the index of the dataframe as the row identity
    data = data.set_index('identity_row')
    
    # identify the row that is the current year forecast
    data['forecast_tag'] = np.where((data['yr'] == curryr) & (data['qtr'] == 5), 1, 0)
    
    # identify the rows that are future year forecasts
    mask = data.yr > curryr
    data.loc[mask, 'forecast_tag'] = 2

    # For all sectors, get the inv, and t fields from the data_p file. If not ind, then also get the e field. Use these to create the rol vars 
    data_p['subid'] = data_p['subid'].astype(int)
    data_p['yr'] = data_p['yr'].astype(int)
    data_p['qtr'] = data_p['qtr'].astype(int)
    if sector_val == "ind":
        data_p['identity_row'] = data_p['metcode'] + data_p['subid'].astype(str) + data_p['subsector'] + data_p['yr'].astype(str) + data_p['qtr'].astype(str)
    else:
        data_p['identity_row'] = data_p['metcode'] + data_p['subid'].astype(str) + sector_val.title() + data_p['yr'].astype(str) + data_p['qtr'].astype(str)
    data_p = data_p.set_index('identity_row')
    data_p = data_p.rename(columns={'inv': 'rolsinv', 't': 'rol_t', 'e': 'rol_e', 'merent': 'rolmerent'})
    if sector_val == "ind":
        data_p = data_p[['rolsinv', 'rol_t']]
    elif sector_val == "apt":
        data_p = data_p[['rolsinv', 'rol_t', 'rol_e']]
    else:
        data_p = data_p[['rolsinv', 'rol_t', 'rol_e', 'rolmerent']]
    data = data.join(data_p)

    # Join in the subnames if this is apt, off, or ret, since that var is not included in the base file
    if sector_val != "ind":
        input_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/subnames.csv".format(get_home(), sector_val))
        subnames = pd.read_csv(input_path)
        subnames = subnames.set_index('identity')
        data = data.join(subnames, on='identity')

    # Null out zero values where the zero is really a dummy value in the first year end row of a submarket
    first_yearend = data.copy()
    first_yearend = first_yearend.reset_index()
    first_yearend = pd.DataFrame(first_yearend[(first_yearend['qtr'] == 5) & (first_yearend['forecast_tag'] == 0)].groupby('identity')['identity_row'].first())
    first_yearend = first_yearend.set_index('identity_row')
    first_yearend['firstyear_tag'] = 1
    data = data.join(first_yearend)
    data['firstyear_tag'] = data['firstyear_tag'].fillna(0)
    data['firstyear_tag'] = data['firstyear_tag'].astype(int)
    cols_to_nan = ['abs', 'rolsabs', 'G_mrent', 'grolsmre', 'G_merent', 'grolsmer']
    for x in cols_to_nan:
        data[x] = np.where((data['firstyear_tag'] == 1) & (data[x] == 0), np.nan, data[x])

    # Tag cuts that have less than 5 years of trend history, as their historical stats are not as meaningful and we may want to treat them differently for flagging purposes
    # And some metrics wont work at all, like z score and std dev, if there is only one trend year.
    temp = data.copy()
    temp['row_count'] = temp.groupby(['identity', 'yr'])['qtr'].transform('count')
    temp['trend_count'] = temp[(temp['row_count'] == 5) & (temp['qtr'] == 5) & (temp['forecast_tag'] == 0)].groupby('identity')['yr'].transform('count')
    temp['lim_hist'] = np.where((temp['trend_count'] < 5), temp['trend_count'], 0)
    temp = temp[temp['lim_hist'] > 0]
    temp = temp.drop_duplicates('identity')
    temp = temp.set_index('identity')
    temp = temp[['lim_hist']]
    data = data.join(temp, on='identity')
    data['lim_hist'] = data['lim_hist'].fillna(10)
    data['lim_hist'] = data['lim_hist'].astype(int)

    data = data.drop(['firstyear_tag'], axis=1)

    # For apartment office, and retail, we need to enter a dummy value for inv in the first year row so subsequent calculations will run
    # Also for 2003 in PV and WS
    if sector_val == "apt" or sector_val == "off" or sector_val == "ret":
        data['inv'] = np.where((data['yr'] == 1998) & (np.isnan(data['inv'] == True)), 0, data['inv'])
        data['inv'] = np.where((data['yr'] == 2003) & ((data['metcode'] == "PV") | (data['metcode'] == "WS")), 0, data['inv'])

    data['mrent'] = round(data['mrent'], 2)
    data['merent'] = round(data['merent'], 2)
        
    return data, orig_cols, file_used