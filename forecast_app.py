import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, MATCH, ALL
from dash import no_update
import plotly.graph_objs as go 
from flask import session, copy_current_request_context
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme
from dash.exceptions import PreventUpdate
import urllib
import os
import numpy as np
import pandas as pd
import csv
from pathlib import Path
import re
from datetime import datetime
import math
pd.set_option('display.max_rows',  1000)
pd.set_option('display.max_columns', 100)
pd.options.display.float_format = '{:.4f}'.format
from IPython.core.display import display, HTML

# local imports
from init_load_forecast import get_home, initial_load
from authenticate_forecast import authenticate_user, validate_login_session
from server_forecast import forecast, server
from stats_forecast import calc_stats
from flags_forecast import cons_flags, vac_flags, rent_flags
from support_functions_forecast import set_display_cols, display_frame, gen_metrics, drop_cols, rollup, live_flag_count, summarize_flags_ranking, summarize_flags, get_issue, get_diffs, rank_it, flag_examine
from login_layout_forecast import get_login_layout
from forecast_app_layout import get_app_layout
from timer import Timer


# Function that determines the data type - int, float, etc - so that the correct format can be set for the app display
def get_types(dataframe, sector_val):

    # In order for the comma seperator format to work, fields need to be set to float type. Put the conversion in a try and except, since some frames that come in this function wont have those fields
    try:
        dataframe[['inv', 'rolscon', 'rolsabs', 'rol_e']] = dataframe[['inv', 'rolscon', 'rolsabs', 'rol_e']].astype(float)
    except:
        False

    type_dict = {}
    format_dict = {}
    dtypes = pd.DataFrame(dataframe.dtypes, columns = ['dtype'])
    dtypes = dtypes.reset_index()

    for index, row in dtypes.iterrows():
        if row['dtype'] == "object":
            type_dict[row['index']] = 'text'
            format_dict[row['index']] = Format(precision=2, scheme=Scheme.fixed)
        elif row['dtype'] == 'int64' or row['dtype'] == 'int32':
            type_dict[row['index']] = 'numeric'
            format_dict[row['index']] = Format(precision=0, scheme=Scheme.fixed)
        elif row['dtype'] == 'float64':
            type_dict[row['index']] = 'numeric'
            format_dict[row['index']] = FormatTemplate.percentage(2)

    type_dict['inv'] = 'numeric'
    type_dict['rol cons'] = 'numeric'
    type_dict['rol abs'] = 'numeric'
    type_dict['rol vac'] = 'numeric'
    type_dict['askrent'] = 'numeric'
    type_dict['effrent'] = 'numeric'
    type_dict['ask rent'] = 'numeric'
    type_dict['eff rent'] = 'numeric'
    type_dict['ask_chg'] = 'numeric'
    type_dict['eff_chg'] = 'numeric'
    type_dict['gap'] = 'numeric'
    type_dict['gap chg'] = 'numeric'
    type_dict['rol gap chg'] = 'numeric'
    type_dict['Flag Type'] = 'text'
    type_dict['Total Flags'] = 'numeric'
    type_dict['% Fcast Rows W Flag'] = 'numeric'
    type_dict['% Subs W Flag'] = 'numeric'
    type_dict['3yravgcons'] = 'numeric'
    type_dict['trendcons'] = 'numeric'
    type_dict['3yr_avgcons'] = 'numeric'
    type_dict['3yr_avgabs'] = 'numeric'
    type_dict['3yr_avgabs_nonc'] = 'numeric'
    type_dict['roll3_abs_cons_r'] = 'numeric'
    type_dict['imp_abs'] = 'numeric'
    type_dict['imp_abs_rol'] = 'numeric'
    type_dict['histimp_avgabs'] = 'numeric'
    type_dict['3yr_avgGmrent'] = 'numeric'
    type_dict['3yr_avgGmrent_nonc'] = 'numeric'
    type_dict['imp_Gmrent'] = 'numeric'
    type_dict['imp_Gmrent_rol'] = 'numeric'
    type_dict['histimp_avgGmrent'] = 'numeric'
    type_dict['imp_Gmerent'] = 'numeric'
    type_dict['imp_Gmerent_rol'] = 'numeric'
    type_dict['3yr_avgGmerent'] = 'numeric'
    type_dict['implied_rolsabs'] = 'numeric'
    type_dict['sd_vacchg'] = 'numeric'
    type_dict['sd_G_mrent'] = 'numeric'
    type_dict['avg_G_mrent'] = 'numeric'
    type_dict['p_unabs_cons'] = 'numeric'
    type_dict['trendabs'] = 'numeric'
    type_dict['f_var_vacchg'] = 'numeric'
    type_dict['avg_vacchg'] = 'numeric'
    type_dict['avg_G_mrent_nonc'] = 'numeric'
    type_dict['trendGmrent'] = 'numeric'
    type_dict['histimp_Gmrent'] = 'numeric'
    type_dict['3yr_avg_empchg'] = 'numeric'
    type_dict['imp_avginc_chg'] = 'numeric'
    type_dict['imp_offemp_chg'] = 'numeric'
    type_dict['imp_empchg'] = 'numeric'
    type_dict['imp_indemp_chg'] = 'numeric'
    type_dict['trendGmerent'] = 'numeric'
    type_dict['trendgapchg'] = 'numeric'
    type_dict['imp_gapchg'] = 'numeric'
    type_dict['imp_cons'] = 'numeric'
    type_dict['vac chg'] =  'numeric'
    type_dict['rol vac chg'] =  'numeric'
    type_dict['rolask_chg'] =  'numeric'
    type_dict['rol_eff_chg'] =  'numeric'
    type_dict['avg_abs_cons'] = 'numeric'
    type_dict['10_yr_vac'] = 'numeric'
    type_dict['occ'] = 'numeric'
    type_dict['rol_ask_chg'] = 'numeric'
    type_dict['rol_eff_chg'] = 'numeric'
    type_dict['p_abs_cons'] = 'numeric'
    type_dict['emp_5'] = 'numeric'
    type_dict['emp_95'] = 'numeric'
    type_dict['hist_emp_10'] = 'numeric'
    type_dict['hist_emp_90'] = 'numeric'
    type_dict['Gmrent'] = 'numeric'
    type_dict['Gmerent'] = 'numeric'
    type_dict['rol Gmrent'] = 'numeric'
    type_dict['rol Gmerent'] = 'numeric'
    

    format_dict['rol vac'] = FormatTemplate.percentage(2)
    format_dict['askrent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['effrent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['ask rent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['eff rent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['mrent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['rolmrent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['merent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['rolmerent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['vac chg'] = FormatTemplate.percentage(2)
    format_dict['rol vac chg'] = FormatTemplate.percentage(2)
    format_dict['ask_chg'] = FormatTemplate.percentage(2)
    format_dict['rol_ask_chg'] = FormatTemplate.percentage(2)
    format_dict['eff_chg'] = FormatTemplate.percentage(2)
    format_dict['rol_eff_chg'] = FormatTemplate.percentage(2)
    format_dict['gap'] = FormatTemplate.percentage(2)
    format_dict['gap chg'] = FormatTemplate.percentage(2)
    format_dict['rol gap chg'] = FormatTemplate.percentage(2)
    format_dict['Flag Type'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Total Flags'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['% Fcast Rows W Flag'] = FormatTemplate.percentage(1)
    format_dict['% Subs W Flag'] = FormatTemplate.percentage(1)
    format_dict['vac_z'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['G_mrent_z'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['emp_chg_z'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['vac_quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['G_mrent_quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['emp_quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['ind_emp_quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['off_emp_quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['gap_quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['f_var_vac_chg'] = FormatTemplate.percentage(3)
    format_dict['f_avg_var_vac_chg_us'] = FormatTemplate.percentage(3)
    format_dict['f_var_G_mrent'] = FormatTemplate.percentage(3)
    format_dict['f_avg_var_G_mrent_us'] = FormatTemplate.percentage(3)
    format_dict['abs_cons_r'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['rolling_3_abs_cons_r'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['roll3_abs_cons_r'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['f_var_cons'] = Format(group=",")
    format_dict['f_avg_var_cons_us'] = Format(group=",")
    format_dict['3yr_avgcons'] = Format(group=",")
    format_dict['trendcons'] = Format(group=",")
    format_dict['trendabs'] = Format(group=",")
    format_dict['3yr_avgabs'] = Format(group=",")
    format_dict['imp_abs'] = Format(group=",")
    format_dict['imp_abs_rol'] = Format(group=",")
    format_dict['histimp_avgabs'] = Format(group=",")
    format_dict['p_abs_cons'] = Format(group=",")
    format_dict['3yr_avgGmrent'] = FormatTemplate.percentage(2)
    format_dict['3yr_avgGmrent_nonc'] = FormatTemplate.percentage(2)
    format_dict['imp_Gmrent'] = FormatTemplate.percentage(2)
    format_dict['imp_Gmrent_rol'] = FormatTemplate.percentage(2)
    format_dict['histimp_avgGmrent'] = FormatTemplate.percentage(2)
    format_dict['imp_Gmerent'] = FormatTemplate.percentage(2)
    format_dict['trendGmrent'] = FormatTemplate.percentage(2)
    format_dict['trendGmerent'] = FormatTemplate.percentage(2)
    format_dict['trendgapchg'] = FormatTemplate.percentage(2)
    format_dict['imp_gapchg'] = FormatTemplate.percentage(2)
    format_dict['implied_rolsabs'] = Format(group=",")
    format_dict['inv'] = Format(group=",")
    format_dict['cons'] = Format(group=",")
    format_dict['rol cons'] = Format(group=",")
    format_dict['abs'] = Format(group=",")
    format_dict['rol abs'] = Format(group=",")
    format_dict['abs_nonc'] = Format(group=",")
    format_dict['p_unabs_cons'] = Format(group=",")
    format_dict['avail'] = Format(group=",")
    format_dict['occ'] = Format(group=",")
    format_dict['h'] = Format(group=",")
    format_dict['rol_h'] = Format(group=",")
    format_dict['rol_e'] = Format(group=",")
    format_dict['e'] = Format(group=",")
    format_dict['t'] = Format(group=",")
    format_dict['sd_vacchg'] = FormatTemplate.percentage(2)
    format_dict['sd_G_mrent'] = FormatTemplate.percentage(2)
    format_dict['avg_G_mrent'] = FormatTemplate.percentage(2)
    format_dict['avg_G_mrent_nonc'] = FormatTemplate.percentage(2)
    format_dict['trendGmrent'] = FormatTemplate.percentage(2)
    format_dict['histimp_Gmrent'] = FormatTemplate.percentage(2)
    format_dict['f_var_vacchg'] = FormatTemplate.percentage(2)
    format_dict['avg_vacchg'] = FormatTemplate.percentage(2)
    format_dict['p_unabs_cons'] = Format(group=",")
    format_dict['3yr_avgabs_nonc'] = Format(group=",")
    format_dict['3yr_avg_empchg'] = FormatTemplate.percentage(2)
    format_dict['imp_avginc_chg'] = FormatTemplate.percentage(2)
    format_dict['imp_cons'] = Format(group=",")
    format_dict['avg_abs_cons'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['10_yr_vac'] = FormatTemplate.percentage(2)
    format_dict['g_mrent'] = FormatTemplate.percentage(2)
    format_dict['g_merent'] = FormatTemplate.percentage(2)
    format_dict['Gmrent'] = FormatTemplate.percentage(2)
    format_dict['Gmerent'] = FormatTemplate.percentage(2)
    format_dict['rol Gmrent'] = FormatTemplate.percentage(2)
    format_dict['rol Gmerent'] = FormatTemplate.percentage(2)
    format_dict['emp_5'] = FormatTemplate.percentage(1)
    format_dict['emp_95'] = FormatTemplate.percentage(1)
    format_dict['hist_emp_10'] = FormatTemplate.percentage(1)
    format_dict['hist_emp_90'] = FormatTemplate.percentage(1)
    format_dict['emp_chg'] = FormatTemplate.percentage(1)
    format_dict['rol_emp_chg'] = FormatTemplate.percentage(1)
    format_dict['3yr_avg_empchg'] = FormatTemplate.percentage(1)
    format_dict['ind_emp_chg'] = FormatTemplate.percentage(1)
    format_dict['rol_ind_emp_chg'] = FormatTemplate.percentage(1)
    format_dict['off_emp_chg'] = FormatTemplate.percentage(1)
    format_dict['rol_off_emp_chg'] = FormatTemplate.percentage(1)
    format_dict['imp_empchg'] = FormatTemplate.percentage(1)
    format_dict['imp_indemp_chg'] = FormatTemplate.percentage(1)
    format_dict['imp_offemp_chg'] = FormatTemplate.percentage(1)
    

    return type_dict, format_dict

# Function that returns the highlighting style of the various dash datatables
def get_style(type_filt, dataframe_in, dash_curryr, dash_second_five):
    dataframe = dataframe_in.copy()
    if type_filt == "full":
        style = [ 
                        {
                            'if': {'column_id': str(x), 'filter_query': '{{{0}}} < 0'.format(x)},
                            'color': 'red',
                        } for x in dataframe.columns
                
                    ] + [
                            
                        {
                            'if': {
                            'filter_query':   '{qtr} eq 5  && {yr} >' + dash_curryr,
                                },
                    
                        'backgroundColor': 'lightblue'
                        },
                        {
                            'if': {
                            'filter_query': '{yr} >=' + dash_second_five,
                                    },
                    
                        'backgroundColor': 'pink'
                        },
                        {
                            'if': {
                            'filter_query':  '{qtr} eq 5  && {yr} <' + dash_curryr,
                                    },
                    
                        'backgroundColor': 'lightgreen'
                        },
                        {
                            'if': {
                            'filter_query':   '{qtr} eq 5  && {yr} =' + dash_curryr,
                                },
                    
                        'backgroundColor': 'yellow'
                        },
                    ]
    elif type_filt == "partial":
        style = [ 
                    {
                        'if': {'column_id': str(x), 'filter_query': '{{{0}}} < 0'.format(x)},
                        'color': 'red',
                    } for x in dataframe.columns
                ]
    return style
    

def filter_graph(input_dataframe, curryr, currqtr, year_value, xaxis_column_name, yaxis_column_name, sector_val, comp_value, flags_only):
    dataframe = input_dataframe.copy()

    dataframe['vac_chg'] = round(dataframe['vac_chg'], 4)
    dataframe['G_mrent'] = round(dataframe['G_mrent'], 4)
    dataframe['avg_inc_chg'] = round(dataframe['avg_inc_chg'], 4)
    
    if currqtr != 4:
            dataframe = dataframe[((dataframe['yr'] >= curryr - 5) & (dataframe['yr'] < curryr) & (dataframe['qtr'] == 5)) | ((dataframe['yr'] == curryr) & (dataframe['qtr'] <= currqtr)) | ((dataframe['yr'] >= curryr) & (dataframe['qtr'] == 5))]
    elif currqtr == 4:
        dataframe = dataframe[(dataframe['yr'] >= curryr - 5) & (dataframe['qtr'] == 5)]

    scatter_graph_cols = ['subsector', 'metcode', 'subid', 'yr', 'qtr', 'inv', 'cons', 'vac', 'vac_chg', 'mrent', 'G_mrent', 'gap', 'gap_chg', 'avg_inc', 'avg_inc_chg', 'flagged_status']
    if currqtr != 4:
        scatter_graph_cols += ['implied_cons', 'implied_vac_chg', 'implied_G_mrent', 'implied_gap_chg', 'implied_avg_inc_chg']
    if sector_val == "apt" or sector_val == "ret":
        scatter_graph_cols += ['emp', 'emp_chg', 'implied_emp_chg']      
    elif sector_val == "off":
        scatter_graph_cols += ['off_emp', 'off_emp_chg', 'implied_off_emp_chg']
    elif sector_val == "ind":
        scatter_graph_cols += ['ind_emp', 'ind_emp_chg', 'implied_ind_emp_chg']

    if comp_value == "r":
        scatter_graph_cols += ['rolscon', 'rolsvac', 'rolsvac_chg', 'rolmrent', 'grolsmre', 'rolsgap', 'rolsgap_chg']
        if sector_val == "apt" or sector_val == "ret":
            scatter_graph_cols += ['rol_emp', 'rol_emp_chg']      
        elif sector_val == "off":
            scatter_graph_cols += ['rol_off_emp', 'rol_off_emp_chg']
        elif sector_val == "ind":
            scatter_graph_cols += ['rol_ind_emp', 'rol_ind_emp_chg']
    
    dataframe = dataframe[scatter_graph_cols]

    for_time_series = dataframe.copy()
    for_time_series = pd.melt(for_time_series, id_vars=['subsector', 'metcode', 'subid', 'yr', 'qtr'])
    for_time_series['index'] = for_time_series['metcode'] + for_time_series['subid'].astype(str) + for_time_series['subsector']

    if comp_value == "r":
        dataframe['diff_to_rol'] = np.where((dataframe['yr'] >= curryr) & (dataframe['qtr'] == 5), dataframe[xaxis_column_name] - dataframe[yaxis_column_name], np.nan)
        dataframe = dataframe[(abs(dataframe['diff_to_rol']) >= 0.001) | (dataframe['yr'] < curryr) | ((dataframe['qtr'] != 5) & (dataframe['yr'] == curryr))]
        get_first_sub = dataframe.copy()
        get_first_sub = get_first_sub[(get_first_sub['yr'] >= curryr) & (get_first_sub['qtr'] == 5) & (abs(get_first_sub['diff_to_rol']) >= 0.001)]
        first_sub = get_first_sub['metcode'].iloc[0] + get_first_sub['subid'].iloc[0].astype(str) + get_first_sub['subsector'].iloc[0]
        init_hover ={'points': [{'customdata': first_sub}]}
    else:
        first_sub = dataframe.reset_index().loc[0]['metcode'] + dataframe.reset_index().loc[0]['subid'].astype(str) + dataframe.reset_index().loc[0]['subsector']
        init_hover ={'points': [{'customdata': first_sub}]}

    if len(flags_only) > 0:
        if flags_only[0] == "f" and len(dataframe[dataframe['flagged_status'] == 1]) > 0:
            dataframe = dataframe[dataframe['flagged_status'] == 1]
    
    dataframe = pd.melt(dataframe, id_vars=['subsector', 'metcode', 'subid', 'yr', 'qtr'])
    dataframe['index'] = dataframe['metcode'] + dataframe['subid'].astype(str) + dataframe['subsector']
    
    dataframe = dataframe[dataframe['variable'] != 'inv']

    dataframe = dataframe[dataframe['qtr'] == 5]
    
    if comp_value == "c":
        dataframe = dataframe[(dataframe['variable'] == xaxis_column_name) | (dataframe['variable'] == yaxis_column_name) | (dataframe['variable'] == 'flagged_status')]
    elif comp_value == "r":
        dataframe = dataframe[(dataframe['variable'] == xaxis_column_name) | (dataframe['variable'] == yaxis_column_name) | (dataframe['variable'] == "diff_to_rol") | (dataframe['variable'] == 'flagged_status')]
    
    dataframe = dataframe[dataframe['yr'] == year_value]

    return dataframe, for_time_series, init_hover

def create_scatter_plot(dataframe, xaxis_var, yaxis_var, comp_value):

    if comp_value == "c":
        vis_status = True
        text_val = dataframe[dataframe['variable'] == yaxis_var]['index']
        if xaxis_var == "cons" or xaxis_var == "implied_cons":
            x_data = dataframe[dataframe['variable'] == xaxis_var]['value'].astype(int)
            y_data = dataframe[dataframe['variable'] == yaxis_var]['value']
            x_tick_format = ','
            y_tick_format = ',.02%'
        elif yaxis_var == "cons" or yaxis_var == "implied_cons":
            x_data = dataframe[dataframe['variable'] == xaxis_var]['value']
            y_data = dataframe[dataframe['variable'] == yaxis_var]['value'].astype(int)
            x_tick_format = ',.02%'
            y_tick_format = ','
        else:
            x_data = dataframe[dataframe['variable'] == xaxis_var]['value']
            y_data = dataframe[dataframe['variable'] == yaxis_var]['value']
            x_tick_format = ',.02%'
            y_tick_format = ',.02%'
    
    elif comp_value == "r":
        vis_status = False
        text_val = False
        if xaxis_var == "cons":
            x_tick_format = ','
        else:
            x_tick_format = ',.02%'
        if yaxis_var == "rolscon":
            y_tick_format = ','
        else:
            y_tick_format = ',.02%'
           
            
        dataframe['identity'] = dataframe['metcode'] + dataframe['subid'].astype(str) + dataframe['subsector']
        x_data = dataframe['identity'].unique()
        y_data = dataframe[dataframe['variable'] == 'diff_to_rol']['value']

    axis_titles = {
                    "cons": "Construction",
                    "vac_chg": "Vacancy Change",
                    "G_mrent": "Market Rent Change",
                    "gap_chg": "Gap Change",
                    "implied_cons": " Implied Construction",
                    "implied_vac_chg": "Implied Vacancy Change",
                    "implied_G_mrent": "Implied Market Rent Change",
                    "implied_gap_chg": "Implied Gap Change",
                    "avg_inc_chg": "Average Income Change",
                    "implied_avg_inc_chg": "Implied Average Income Change",
                    "emp_chg": "Employment Change",
                    "implied_emp_chg": "Implied Employment Change",
                    "off_emp_chg": "Office Employment Change",
                    "implied_off_emp_chg": "Implied Office Employment Change",
                    "ind_emp_chg": "Industrial Employment Change",
                    "implied_ind_emp_chg": "Implied Industrial Employment Change"
                    }

    if comp_value == "c":
        x_axis_title = axis_titles[xaxis_var]
        y_axis_title = axis_titles[yaxis_var]
    elif comp_value == "r":
        x_axis_title = "Submarkets with Difference to Current"
        y_axis_title = "Curr Diff to ROL " + axis_titles[xaxis_var]

    flagged_status = dataframe.copy()
    flagged_status = flagged_status[flagged_status['variable'] == 'flagged_status'][['index', 'value']]
    flagged_status = list(flagged_status['value'])
    flagged_status = [int(i) for i in flagged_status]
    if all(x == flagged_status[0] for x in flagged_status) == True:
        if flagged_status[0] == 1:
            color = 'red'
        else:
            color = 'blue'
        colorscale = []
    else:
        color = [0 if x == 0 else 1 for x in flagged_status]
        colorscale = [[0, 'blue'], [1, 'red']]

    graph_dict = {
                    'data': [dict(
                        x = x_data,
                        y = y_data,
                        text = text_val,
                        customdata = dataframe[dataframe['variable'] == yaxis_var]['index'],
                        mode = 'markers',
                        marker={
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'},
                            'color': color,
                            'colorscale': colorscale
                                },
                            )],
                    'layout': dict(
                        xaxis={
                            'title': x_axis_title,
                            'tickformat': x_tick_format,
                            'title_standoff': 25,
                            'showticklabels': vis_status,
                            },
                        yaxis={
                            'title': y_axis_title,
                            'tickformat': y_tick_format,
                            'title_standoff': 25,
                            },
                        margin={'l': 80, 'b': 70, 't': 10, 'r': 0},
                        height=750,
                        hovermode='closest'
                                )
                    }

    return graph_dict

def split_trend_forecast(dataframe, col_name, curryr, currqtr, sector_val):

    # Since the graph will display the level, convert the variable selected by the user to the level instead of the chg
    if col_name == "vac_chg" or col_name == "implied_vac_chg":
        col_name_1 = "vac"
    elif col_name == "G_mrent" or col_name == "implied_G_mrent":
        col_name_1 = "mrent"
    elif col_name == "gap_chg" or col_name == "implied_gap_chg":
        col_name_1 = "gap"
    elif col_name == "emp_chg" or col_name == "implied_emp_chg":
        col_name_1 = "emp"
    elif col_name == "off_emp_chg" or col_name == "implied_off_emp_chg":
        col_name_1 = "off_emp"
    elif col_name == "ind_emp_chg" or col_name == "implied_ind_emp_chg":
        col_name_1 = "ind_emp"
    elif col_name == "avg_inc_chg" or col_name == "implied_avg_inc_chg":
        col_name_1 = "avg_inc"
    elif col_name == "cons" or col_name == "implied_cons":
        col_name_1 = "cons"
    elif col_name == "rolscon":
        col_name_1 = "rolscon"
    elif col_name == "rolsvac_chg":
        col_name_1 = "rolsvac"
    elif col_name == "grolsmre":
        col_name_1 = "rolmrent"
    elif col_name == "rolsgap_chg":
        col_name_1 = "rolsgap"
    elif col_name == "rol_emp_chg":
        col_name_1 = "rol_emp"
    elif col_name == "rol_off_emp_chg":
        col_name_1 = "rol_off_emp"
    elif col_name == "rol_ind_emp_chg":
        col_name_1 = "rol_ind_emp"

    # Get the y_tick_range if the variable is not construction
    if col_name_1 != "cons" or col_name_1 != "rolscon":
        y_tick_range, dtick, tick_0 = set_y2_scale(dataframe, "ts", col_name_1, sector_val)
    else:
        y_tick_range = []
        dtick = False
        tick_0 = False

    # Split the main dataset into two - one that holds the trend history, with the quarterly trend periods for curryr, one that holds the forecast periods, with the implied periods for curryr
    trend = dataframe.copy()
    forecast = dataframe.copy()
    if currqtr != 4:
        if "rol" in col_name_1:
            if currqtr == 1:
                trend = trend[(trend['yr'] < curryr)]
            else:
                trend = trend[((trend['yr'] < curryr) | ((trend['yr'] == curryr) & (trend['qtr'] == currqtr - 1)))]
        else:
            trend = trend[((trend['yr'] < curryr) | ((trend['yr'] == curryr) & (trend['qtr'] == currqtr)))]
    elif currqtr == 4:
        trend = trend[(trend['yr'] < curryr)]
    forecast = forecast[(forecast['yr'] >= curryr) & (forecast['qtr'] == 5)]

    # Filter out the variable for LEVEL for the choice that the user selected
    trend_level = trend.copy()
    forecast_level = forecast.copy()
    trend_level = trend_level[trend_level['variable'] == col_name_1]
    forecast_level = forecast_level[forecast_level['variable'] == col_name_1]

    # Filter out the variable for change for the choice that the user selected, but substitue the total trend value if not q4 in curryr.
    # If the user selected an implied variable, convert it to the non-implied variable, as the time series will show implied with the two distinct lines as opposed to the scatter plot which will show the actual implied variable
    # Also return the two curryr datapoints of trend and implied to connect the two lines in the graph
    if "implied" in col_name:
        col_name = col_name.replace('implied_', '')
    if currqtr == 4:
        trend_chg = trend.copy()
    elif currqtr != 4:
        trend_chg = dataframe.copy()
        trend_chg = trend_chg[((trend_chg['yr'] < curryr) | ((trend_chg['yr'] == curryr) & (trend_chg['qtr'] <= currqtr)))]
    forecast_chg = forecast.copy()
    trend_chg = trend_chg[trend_chg['variable'] == col_name]
    forecast_chg = forecast_chg[forecast_chg['variable'] == col_name]
    
    if currqtr != 4:
        if "rol" in col_name_1 and currqtr == 1:
            if col_name_1 == "rolscon":
                connector = []
            else:
                connector = list(trend_level['value'])[-1], list(forecast_level['value'])[0]
        else:
            trend_connect = trend_level[(trend_level['yr'] == curryr) & (trend_level['qtr'] == currqtr)]
            forecast_connect = forecast_level[(forecast_level['yr'] == curryr)]
            trend_connect = trend_connect.reset_index()
            forecast_connect = forecast_connect.reset_index()
            trend_value = trend_connect.at[0, 'value'] 
            forecast_value = forecast_connect.at[0, 'value']
            if col_name_1 != "cons":
                connector = [trend_value, forecast_value]

            p_trend = trend_level[(trend_level['yr'] == curryr - 1) & (trend_level['qtr'] == 5)]
            p_trend = p_trend.reset_index()
            p_trend_value = p_trend.at[0, 'value']

            if col_name_1 == "cons":
                total_trend_temp = trend_chg.copy()
                total_trend_temp = total_trend_temp[(total_trend_temp['yr'] == curryr) & (total_trend_temp['qtr'] != 5)]
                total_trend = pd.DataFrame(total_trend_temp.groupby('metcode')['value'].sum())
                total_trend = total_trend.reset_index()
                trend_chg_value = total_trend.at[0, 'value']
                trend_chg['value'] = np.where((trend_chg['yr'] == curryr) & (trend_chg['qtr'] == currqtr), trend_chg_value, trend_chg['value'])
                forecast_chg['value'] = np.where((forecast_chg['yr'] == curryr), (forecast_value - trend_chg_value), forecast_chg['value'])
                connector = [trend_chg_value, forecast_value]
            elif col_name_1 == "vac" or col_name_1 == "gap":
                trend_chg['value'] = np.where((trend_chg['yr'] == curryr) & (trend_chg['qtr'] == currqtr), (trend_value - p_trend_value), trend_chg['value'])
                forecast_chg['value'] = np.where((forecast_chg['yr'] == curryr), (forecast_value - trend_value), forecast_chg['value'])
            else:
                trend_chg['value'] = np.where((trend_chg['yr'] == curryr) & (trend_chg['qtr'] == currqtr), (trend_value - p_trend_value) / p_trend_value, trend_chg['value'])
                forecast_chg['value'] = np.where((forecast_chg['yr'] == curryr), (forecast_value - trend_value) / trend_value, forecast_chg['value'])
            
            trend_chg = trend_chg[((trend_chg['yr'] < curryr) | ((trend_chg['yr'] == curryr) & (trend_chg['qtr'] == currqtr)))]

    else: 
        if col_name_1 == "cons":
            connector = []
        else:
            connector = list(trend_level['value'])[-1], list(forecast_level['value'])[0]

    # Convert the datatype to an int if the variable selected is construction, or a float if not. Melting the dataset caused it to become a string since there were mixed datatypes in the column
    if col_name_1 == "cons":
        trend_level['value'] = trend_level['value'].astype(int)
        trend_chg['value'] = trend_chg['value'].astype(int)
    else:
        trend_level['value'] = trend_level['value'].astype(float)
        trend_chg['value'] = trend_chg['value'].astype(float)

    if col_name_1 == 'mrent':
        trend_level['value'] = round(trend_level['value'], 2)
        forecast_level['value'] = round(forecast_level['value'], 2)

    return trend_level, forecast_level, trend_chg, forecast_chg, connector, y_tick_range, dtick, tick_0

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
            rol_var = list(graph[(graph['variable'] == 'rolmrent') & (graph['value'] != '')]['value'])
            oob_var = list(graph[(graph['variable'] == 'mrent_oob') & (graph['value'] != '')]['value'])
        elif input_var == "askrent":
            rol_var = list(graph[(graph['variable'] == 'rolaskrent') & (graph['value'] != '')]['value'])
            oob_var = list(graph[(graph['variable'] == 'askrentoob') & (graph['value'] != '')]['value'])
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

def sub_met_graphs(data, type_filt, curryr, currqtr, fileyr, sector_val):
    graph = data.copy()
    graph = graph[graph['qtr'] == 5]
    graph = graph[graph['yr'] >= curryr - 5]

    vac_range_list, vac_dtick, vac_tick_0 = set_y2_scale(graph, type_filt, "vac", sector_val)
    if type_filt == "sub":
        rent_range_list, rent_dtick, rent_tick_0 = set_y2_scale(graph, type_filt, "mrent", sector_val)
    else:
        rent_range_list, rent_dtick, rent_tick_0 = set_y2_scale(graph, type_filt, "askrent", sector_val)

    graph['cons_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['cons_oob'])
    graph['vac_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['vac_oob'])
    graph['vac_chg_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['vac_chg_oob'])
    if type_filt == "sub":
        graph['mrent_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['mrent_oob'])
    else:
        graph['askrentoob'] = np.where((graph['yr'] < curryr), np.nan, graph['askrentoob'])
    graph['ask_chg_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['ask_chg_oob'])

    graph['cons_oob'] = np.where((graph['cons'] == graph['cons_oob']), np.nan, graph['cons_oob'])
    graph['vac_oob'] = np.where((graph['vac'] == graph['vac_oob']), np.nan, graph['vac_oob'])
    if type_filt == "sub":
        graph['mrent_oob'] = np.where((graph['mrent'] == graph['mrent_oob']), np.nan, graph['mrent_oob'])
    else:
        graph['askrentoob'] = np.where((graph['askrent'] == graph['askrentoob']), np.nan, graph['askrentoob'])
    
    graph_copy = graph.copy()
    
    if type_filt == "sub":
        graph = pd.melt(graph, id_vars=['subsector', 'metcode', 'subid', 'yr', 'qtr'])
    elif type_filt == "met":
        graph = pd.melt(graph, id_vars=['subsector', 'metcode', 'yr', 'qtr'])
    elif type_filt == "nat":
        graph = pd.melt(graph, id_vars=['subsector', 'yr', 'qtr'])
    
    fig_vac = go.Figure()
    fig_rent = go.Figure()

    if type_filt == "sub":
        cons_range_list, dtick = set_bar_scale(graph_copy, sector_val, ['cons', 'rolscon', 'cons_oob'], ['inv', 'rolsinv', 'inv_oob'])
    else:
        cons_range_list, dtick = set_bar_scale(graph_copy, sector_val, ['cons', 'rolscon', 'cons_oob'], ['inv', 'rolsinv', 'inv'])
    
    
    if type_filt == 'sub':
        vac_variable_list = ['cons', 'rolscon', 'vac', 'rolsvac', 'cons_oob', 'vac_oob']
        rent_variable_list = ['cons', 'rolscon', 'mrent', 'rolmrent', 'cons_oob', 'mrent_oob']
        vac_tag_list = ['cons', 'rolscon', 'vac_chg', 'rolsvac_chg', 'cons_oob', 'vac_chg_oob']
        rent_tag_list = ['cons', 'rolscon', 'G_mrent', 'grolsmer', 'cons_oob', 'G_mrent_oob']
    else:
        vac_variable_list = ['cons', 'rolscon', 'vac', 'rolsvac', 'cons_oob', 'vac_oob']
        rent_variable_list = ['cons', 'rolscon', 'askrent', 'rolaskrent', 'cons_oob', 'askrentoob']
        vac_tag_list = ['cons', 'rolscon', 'vac_chg', 'rolsvac_chg', 'cons_oob', 'vac_chg_oob']
        rent_tag_list = ['cons', 'rolscon', 'ask_chg', 'rol_ask_chg', 'cons_oob', 'ask_chg_oob']
    
    vac_name_list = ['construction', 'rolscon', 'vacancy', 'rolsvac', 'consoob', 'oobvac']
    rent_name_list = ['construction', 'rolscon', 'rent', 'rolmrent', 'consoob', 'oobmrent']
    
    scatter_color_list = ['mediumseagreen', 'palevioletred', 'darkgreen', 'red', 'lightskyblue', 'blue']
    scatter_group_list = ['', '', '', '', 'oob', 'oob']
    
    vac_display_list = [True, True, True, True]
    rent_display_list = [True, True, True, True]
    if graph[(graph['variable'] == 'cons_oob')]['value'].isnull().all() == True:
        vac_display_list.append(False)
        rent_display_list.append(False)
    else:
        vac_display_list.append("legendonly")
        rent_display_list.append("legendonly")
    if graph[(graph['variable'] == 'vac_oob')]['value'].isnull().all() == True:
        vac_display_list.append(False)
    else:
        vac_display_list.append("legendonly")
    if type_filt == 'sub':
        if graph[(graph['variable'] == 'mrent_oob')]['value'].isnull().all() == True:
            rent_display_list.append(False)
        else:
            rent_display_list.append("legendonly")
    else:
        if graph[(graph['variable'] == 'askrentoob')]['value'].isnull().all() == True:
            rent_display_list.append(False)
        else:
            rent_display_list.append("legendonly")
    
    axis_list = ['y1', 'y1', 'y2', 'y2', 'y1', 'y2']

    if sector_val == "apt":
        rent_tick_format = '.0f'
    else:
        rent_tick_format = '.1f'
    
    for x in range(0, len(vac_variable_list)):
        if "con" in vac_variable_list[x]:
            fig_vac.add_trace(
            go.Bar(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == vac_variable_list[x]]['value']),
                name = vac_name_list[x],
                marker_color = scatter_color_list[x],
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == vac_tag_list[x]]['value'])],
                yaxis=axis_list[x],
                visible= vac_display_list[x],
                legendgroup = scatter_group_list[x],
                    )
                )
        else:
            fig_vac.add_trace(
            go.Scatter(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == vac_variable_list[x]]['value']),
                name = vac_name_list[x],
                marker_color = scatter_color_list[x],
                hovertemplate='%{x}, ' + '%{text:.2%}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == vac_tag_list[x]]['value'])],
                yaxis=axis_list[x],
                visible= vac_display_list[x],
                legendgroup = scatter_group_list[x],
                    )
                )
    for x in range(0, len(rent_variable_list)):
        if "con" in rent_variable_list[x]:
            fig_rent.add_trace(
            go.Bar(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == rent_variable_list[x]]['value']),
                name= rent_name_list[x],
                marker_color = scatter_color_list[x],
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == rent_tag_list[x]]['value'])],
                yaxis=axis_list[x],
                visible = rent_display_list[x],
                legendgroup = scatter_group_list[x],
                    )
                ) 
        else:    
            fig_rent.add_trace(
            go.Scatter(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == rent_variable_list[x]]['value']),
                name= rent_name_list[x],
                marker_color = scatter_color_list[x],
                hovertemplate='%{x}, ' + '%{text:.2%}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == rent_tag_list[x]]['value'])],
                yaxis=axis_list[x],
                visible = rent_display_list[x],
                legendgroup = scatter_group_list[x],
                    )
                )
            
    fig_vac.update_layout(
        title={
            'text': "Vacancy",
            'y':0.85,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        legend=dict(
            itemclick="toggleothers",
            itemdoubleclick="toggle",
                ),
        legend_orientation="h",
        xaxis=dict(
            tick0=curryr - 5,
            dtick=1
                ),
        yaxis=dict(
            title='Construction',
            autorange=False,
            range=cons_range_list,
            dtick = dtick,
            tickformat=',',
            side='left',
            showgrid=False,
                ),
        yaxis2=dict(
            title='Vacancy Level',
            side='right',
            overlaying='y',
            tickformat= ',.01%',
            range=vac_range_list,
            fixedrange=True,
            autorange=False,
            dtick=vac_dtick,
            tick0=vac_tick_0
                )
            )

    fig_rent.update_layout(
        title={
            'text': "Market Rent",
            'y':0.85,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        legend=dict(
            itemclick="toggleothers",
            itemdoubleclick="toggle",
                ),
        legend_orientation="h",
        xaxis=dict(
            tick0=curryr - 5,
            dtick=1
                ),
        yaxis=dict(
            title='Construction',
            autorange=False,
            range=cons_range_list,
            dtick = dtick,
            tickformat=',',
            side='left',
            showgrid=False
                ),
        yaxis2=dict(
            title='Rent Level',
            side='right',
            overlaying='y',
            tickformat = rent_tick_format,
            range=rent_range_list,
            fixedrange=True,
            autorange=False,
            dtick=rent_dtick,
            tick0=rent_tick_0
                )
            )

    # if type_filt == "nat":
    #     file_path_temp = "{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/".format(get_home(), sector_val, fileyr, currqtr)
    #     fig_vac.write_html(file_path_temp + 'national_vac_series.html')
    #     fig_rent.write_html(file_path_temp + 'national_rent_series.html')

    return fig_vac, fig_rent

def set_ts_scatter(fig, trend_cons, forecast_cons, cons_connector_1, cons_connector_2, trend_level, forecast_level, trend_chg, forecast_chg, connector, format_choice, curryr, currqtr, comp_value):
  
    if (currqtr == 1 and (comp_value == "c" or "rol" not in trend_level.reset_index().loc[0]['variable'])) or currqtr == 2 or currqtr == 3:
        fig.add_trace(
            go.Bar(
                x=list(trend_cons['yr'].unique()),
                y=list(trend_cons['value']),
                marker_color='lightskyblue',
                width=0.5,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(trend_cons['value'])],
                yaxis='y1',
                    )
                )
        fig.add_trace(
            go.Bar(
                x=list(forecast_cons['yr'].unique()),
                y=list(forecast_cons['value']),
                marker_color='palevioletred',
                width=0.5,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(forecast_cons['value'])],
                yaxis='y1',
                    )
                )
        fig.add_trace(
            go.Bar(
                x=[curryr],
                y=[cons_connector_1],
                marker_color='lightskyblue',
                width=0.5,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in [cons_connector_1]],
                yaxis='y1',
                    )
                ),
        fig.add_trace(
            go.Bar(
                x=[curryr],
                y=[cons_connector_2],
                marker_color='palevioletred',
                width=0.5,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in [cons_connector_2]],
                yaxis='y1',
                    )
                )
        fig.add_trace(
            go.Scatter(
                x=list(trend_level['yr'].unique()),
                y=list(trend_level['value']),
                line={'dash': 'solid', 'color': 'blue'},
                hovertemplate = '%{x}, ' + format_choice,
                text = ['{}'.format(i) for i in list(trend_chg['value'])],
                cliponaxis= False,
                yaxis='y2',
                        )
                    ),
        fig.add_trace(
            go.Scatter(
                x=list(forecast_level['yr'].unique()),
                y=list(forecast_level['value']),
                line={'dash': 'dash', 'color': 'red'},
                hovertemplate='%{x}, ' + format_choice,
                text = ['{}'.format(i) for i in list(forecast_chg['value'])],
                cliponaxis= False,
                yaxis='y2'
                        )
                    ),
        fig.add_trace(
            go.Scatter(
                x=[curryr, curryr],
                y=connector,
                line={'dash': 'dash', 'color': 'red'},
                hoverinfo='skip',
                yaxis='y2'
                        )
                    ) 
    elif currqtr == 4 or (currqtr == 1 and comp_value == "r"):
        fig.add_trace(
            go.Bar(
                x=list(trend_level['yr'].unique()),
                y=list(trend_cons['value']),
                marker_color='lightskyblue',
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(trend_cons['value'])],
                yaxis='y1',
                    )
                )
        fig.add_trace(
            go.Bar(
                x=list(forecast_level['yr'].unique()),
                y=list(forecast_cons['value']),
                marker_color='palevioletred',
                width=0.5,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(forecast_cons['value'])],
                yaxis='y1',
                    )
                )
        fig.add_trace(
            go.Scatter(
                x=[curryr - 1, curryr],
                y=connector,
                line={'dash': 'dash', 'color': 'red'},
                hoverinfo='skip',
                yaxis='y2'
                        )
                    ) 
        fig.add_trace(
            go.Scatter(
                x=list(trend_level['yr'].unique()),
                y=list(trend_level['value']),
                line={'dash': 'solid', 'color': 'blue'},
                hovertemplate = '%{x}, ' + '%{text:.2%}<extra></extra>',
                text = ['{}'.format(i) for i in list(trend_chg['value'])],
                cliponaxis= False,
                yaxis='y2'
                        )
                    ),
        fig.add_trace(
            go.Scatter(
                x=list(forecast_level['yr'].unique()),
                y=list(forecast_level['value']),
                line={'dash': 'dash', 'color': 'red'},
                hovertemplate='%{x}, ' + '%{text:.2%}<extra></extra>',
                text = ['{}'.format(i) for i in list(forecast_chg['value'])],
                cliponaxis= False,
                yaxis='y2'
                        )
                    )
    return fig

def set_ts_bar(fig, trend_level, forecast_level, trend_chg, forecast_chg, connector_1, connector_2, format_choice, curryr, currqtr, comp_value):

    if (currqtr == 1 and (comp_value == "c" or "rol" not in trend_level.reset_index().loc[0]['variable'])) or currqtr == 2 or currqtr == 3:
        fig.add_trace(
            go.Bar(
                x=list(trend_level['yr'].unique()),
                y=list(trend_level['value']),
                marker_color= 'blue',
                width = 0.5,
                hovertemplate = '%{x}, ' + format_choice,
                text = ['{}'.format(i) for i in list(trend_chg['value'])],
                cliponaxis= False
                        )
                    ),
        fig.add_trace(
            go.Bar(
                x=list(forecast_level['yr'].unique()),
                y=list(forecast_level['value']),
                marker_color= 'red',
                width = 0.5,
                hovertemplate='%{x}, ' + format_choice,
                text = ['{}'.format(i) for i in list(forecast_chg['value'])],
                cliponaxis= False
                        )
                    ),
        fig.add_trace(
            go.Bar(
                x=[curryr],
                y=[connector_1],
                marker_color = 'blue',
                width = 0.5,
                hovertemplate='%{x}, ' + format_choice + '<extra></extra>',
                text = ['{}'.format(i) for i in [connector_1, connector_2]]
                        ),
                    ),
        fig.add_trace(
            go.Bar(
                x=[curryr],
                y=[connector_2],
                marker_color = 'red',
                width = 0.5,
                hovertemplate='%{x}, ' + format_choice + '<extra></extra>',
                text = ['{}'.format(i) for i in [connector_2]]
                        )
                     ) 
    elif currqtr == 4 or (currqtr == 1 and comp_value == "r"):
        fig.add_trace(
            go.Bar(
                x=list(trend_level['yr'].unique()),
                y=list(trend_level['value']),
                marker_color = 'blue',
                width = 0.5,
                hovertemplate='%{x}, ' + format_choice + '<extra></extra>',
                text = ['{}'.format(i) for i in list(trend_chg['value'])],
                cliponaxis= False,
                        )
                    ),
        fig.add_trace(
            go.Bar(
                x=list(forecast_level['yr'].unique()),
                y=list(forecast_level['value']),
                marker_color = 'red',
                width = 0.5,
                hovertemplate='%{x}, ' + format_choice + '<extra></extra>',
                text = ['{}'.format(i) for i in list(forecast_chg['value'])],
                cliponaxis= False,
                        )
                    )
    return fig

def set_ts_layout(fig, axis_var, identity, y_tick_range, dtick, tick_0, curryr, currqtr, chart_type, cons_range_list, bar_dtick, sector_val):
    
    graph_titles = {
                    "cons": "Construction",
                    "rolscon": "ROL Construction",
                    "vac_chg": "Vacancy Change",
                    "rolsvac_chg": "ROL Vacancy Change",
                    "G_mrent": "Market Rent Change",
                    "grolsmre": "ROL Market Rent Change",
                    "gap_chg": "Gap Change",
                    "rolsgap_chg": "ROL Gap Change",
                    "implied_cons": "Construction",
                    "implied_vac_chg": "Vacancy Change",
                    "implied_G_mrent": "Market Rent Change",
                    "implied_gap_chg": "Gap Change",
                    "avg_inc_chg": "Average Income Change",
                    "implied_avg_inc_chg": "Average Income Change",
                    "emp_chg": "Employment Change",
                    "rol_emp_chg": "ROL Employment Change",
                    "implied_emp_chg": "Employment Change",
                    "off_emp_chg": "Office Employment Change",
                    "rol_off_emp_chg": "ROL Office Employment Change",
                    "implied_off_emp_chg": "Office Employment Change",
                    "ind_emp_chg": "Industrial Employment Change",
                    "rol_ind_emp_chg": "ROL Industrial Employment Change",
                    "implied_ind_emp_chg": "Industrial Employment Change"
                    }

    axis_titles = {
                    "cons": "Construction",
                    "rolscon": "ROL Construction",
                    "vac_chg": "Vacancy Level",
                    "rolsvac_chg": "ROL Vacancy Level",
                    "G_mrent": "Market Rent Level",
                    "grolsmre": "ROL Market Rent Level",
                    "gap_chg": "Gap",
                    "rolsgap_chg": "ROL Gap",
                    "implied_cons": "Construction",
                    "implied_vac_chg": "Vacancy Level",
                    "implied_G_mrent": "Market Rent Level",
                    "implied_gap_chg": "Gap",
                    "avg_inc_chg": "Average Income",
                    "implied_avg_inc_chg": "Average Income",
                    "emp_chg": "Employment Level (millions)",
                    "rol_emp_chg": "ROL Employent Level (millions)",
                    "implied_emp_chg": "Employment Level (millions)",
                    "off_emp_chg": "Office Employment Level (millions)",
                    "rol_off_emp_chg": "ROL Office Employment Level (millions)",
                    "implied_off_emp_chg": "Office Employment Level (millions)",
                    "ind_emp_chg": "Industrial Employment Level (millions)",
                    "rol_ind_emp_chg": "ROL Industrial Employment Level (millions)",
                    "implied_ind_emp_chg": "Industrial Employment Level (millions)"
                    }

    title_name = '<b>{}</b><br>{}'.format(identity, graph_titles[axis_var])

    if axis_var == "cons" or axis_var == "rolscon":
        tick_format = ','
    elif "avg_inc" in axis_var:
        tick_format = ',.0f'
    elif "G_mrent" in axis_var:
        if sector_val == "apt":
            tick_format = '.0f'
        else:
            tick_format = '.2f'
    elif "emp_chg" in axis_var:
        tick_format = '.0f'
    else:
        tick_format = ',.01%'

    y_axis_title = axis_titles[axis_var]

    x_tick_range = [curryr - 5, curryr + 9]
    
    fig.update_layout(
        title={
            'text': title_name,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        height=350,
        margin={'l': 70, 'b': 30, 'r': 10, 't': 70, 'pad': 20},
        yaxis=dict(
            showgrid=False
                    ),
        xaxis=dict(
            title = "Year",
            title_font = dict(size=12),
            dtick = 1,
            tickangle = 45,
            range = x_tick_range,
            fixedrange=True,
                    )
        )
    
    fig.update_layout(showlegend=False)
    fig.update_layout(barmode='relative')

    if chart_type == "Bar":
        if cons_range_list != False:
            fig.update_layout(yaxis=dict(range=cons_range_list, autorange=False, dtick = bar_dtick, title=y_axis_title, tickformat = tick_format),
                                )

    else:
        fig.update_layout(
                yaxis2=dict(
                title = y_axis_title,
                title_font = dict(size=12),
                tickformat = tick_format,
                range = y_tick_range,
                dtick = dtick,
                tick0=tick_0,
                fixedrange = True,
                autorange=False,
                side='right', 
                overlaying='y',
                        )
                    )
        fig.update_layout(yaxis=dict(title='Construction', tickformat=',', side='left'))
        if cons_range_list != False:
            fig.update_layout(yaxis=dict(range=cons_range_list, autorange=False, dtick = bar_dtick))

    return fig          

# Function that returns the most recent input value updated by the user
def get_input_id():
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No update yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

   
    return button_id
  
# This function reads and writes dataframes to pickle files
def use_pickle(direction, file_name, dataframe, fileyr, currqtr, sector_val):

    if "decision_log" in file_name:
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), file_name))
        
        if direction == "in":
            data = pd.read_pickle(file_path)
            return data
        elif direction == "out":
            dataframe.to_pickle(file_path)
    elif "flags" in file_name:
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), file_name))
        orig_flags = pd.read_pickle(file_path)
        return orig_flags
    else:
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/intermediatefiles/{}.pickle".format(get_home(), file_name))
    
        if direction == "in":
            data = pd.read_pickle(file_path)
            return data
        elif direction == "out":
            dataframe.to_pickle(file_path)

def update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, button, flag_name, yr_val):
    if button == "submit":
        # Identify where the forecast series has changed for key variables
        decision_data_test = decision_data.copy()
        decision_data_test = decision_data_test[decision_data_test['identity'] == drop_val]
        drop_list = []
        for x in list(decision_data_test.columns):
            if "new" in x:
                drop_list.append(x)
        decision_data_test = decision_data_test.drop(drop_list, axis=1)
        for x in list(decision_data_test.columns):
            if "oob" in x:
                decision_data_test = decision_data_test.rename(columns={x: x[:-4]})
        update_data = data.copy()
        update_data = update_data[update_data['identity'] == drop_val]
        update_data = update_data[update_data['forecast_tag'] != 0]
        update_data = update_data[['identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr', 'cons', 'vac', 'abs', 'G_mrent', 'G_merent', 'gap', 'inv', 'avail', 'mrent', 'merent', 'vac_chg']]
        decision_data_test = decision_data_test.drop(['c_user', 'v_user', 'g_user', 'e_user'], axis=1)
        update_data['vac'] = round(update_data['vac'], 3)
        update_data['vac_chg'] = round(update_data['vac_chg'], 3)
        update_data['G_mrent'] = round(update_data['G_mrent'], 3)
        update_data['G_merent'] = round(update_data['G_merent'], 3)
        update_data['gap'] = round(update_data['gap'], 3)
        update_data['mrent'] = round(update_data['mrent'], 2)
        update_data['merent'] = round(update_data['merent'], 2)
        decision_data_test['vac'] = round(decision_data_test['vac'], 3)
        decision_data_test['vac_chg'] = round(decision_data_test['vac_chg'], 3)
        decision_data_test['G_mrent'] = round(decision_data_test['G_mrent'], 3)
        decision_data_test['G_merent'] = round(decision_data_test['G_merent'], 3)
        decision_data_test['gap'] = round(decision_data_test['gap'], 3)
        decision_data_test['mrent'] = round(decision_data_test['mrent'], 2)
        decision_data_test['merent'] = round(decision_data_test['merent'], 2)
        test = update_data.ne(decision_data_test)
        update_data = update_data[test]

        # Update user log with username that made the edit
        update_data['c_user'] = np.nan
        update_data['v_user'] = np.nan
        update_data['g_user'] = np.nan
        update_data['e_user'] = np.nan
        for index, row in update_data.iterrows():
            if math.isnan(row['cons']) == False:
                update_data.loc[index, 'c_user'] = user
            if math.isnan(row['vac']) == False or math.isnan(row['vac_chg']) == False or math.isnan(row['avail']) == False or math.isnan(row['abs']) == False:
                update_data.loc[index, 'v_user'] = user
            if math.isnan(row['mrent']) == False or math.isnan(row['G_mrent']) == False:
                update_data.loc[index, 'g_user'] = user
            if  math.isnan(row['merent']) == False or math.isnan(row['G_merent']) == False or math.isnan(row['gap']) == False:
                update_data.loc[index, 'e_user'] = user
        
        # Fill in the new values in a trunc dataframe
        decision_data_fill = decision_data.copy()
        decision_data_fill = decision_data_fill[decision_data_fill['identity'] == drop_val]
        no_change_list = ['identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr', 'c_user', 'v_user', 'g_user', 'e_user']
        for x in list(decision_data_fill.columns):
            if "new" not in x:
                if x not in no_change_list:
                    decision_data_fill = decision_data_fill.drop([x], axis=1)
            elif "new" in x:
                decision_data_fill = decision_data_fill.rename(columns={x: x[:-4]})
        # Since nan values wont replace non nan values when using combine first, replace them all with a crazy number that wont match a real value, and then replace back to nan after combined
        all_cols = list(update_data.columns)
        fill_list = [x for x in all_cols if x not in no_change_list]
        update_data[fill_list] = update_data[fill_list].fillna(9999999999999999)
        update_data[['c_user', 'v_user', 'g_user', 'e_user']] = update_data[['c_user', 'v_user', 'g_user', 'e_user']].fillna("temp")
        update_data = update_data.combine_first(decision_data_fill)
        for x in fill_list:
            update_data[x] = np.where(update_data[x] == 9999999999999999, np.nan, update_data[x])
        for x in ['c_user', 'v_user', 'g_user', 'e_user']:
            update_data[x] = np.where(update_data[x] == "temp", np.nan, update_data[x])
        for x in list(update_data.columns):
            if x not in no_change_list and "oob" not in x:
                update_data = update_data.rename(columns={x: x + "_new"})

        # Because there are slight rounding differences, check if there is an actual change to the level var, and null out diff if no change
        for index, row in update_data.iterrows():
            if math.isnan(row['avail_new']) == True:
                update_data.loc[index, 'vac_new'] = np.nan 
                update_data.loc[index, 'vac_chg_new'] = np.nan 
                update_data.loc[index, 'abs'] = np.nan 
                update_data.loc[index, 'v_user'] = np.nan 
            if math.isnan(row['mrent_new']) == True:
                update_data.loc[index, 'G_mrent_new'] = np.nan 
                update_data.loc[index, 'g_user'] = np.nan 
            if math.isnan(row['merent_new']) == True:
                update_data.loc[index, 'G_merent_new'] = np.nan 
                update_data.loc[index, 'gap_new'] = np.nan 
                update_data.loc[index, 'e_user'] = np.nan 
        
        # Replace the new values in the "new" columns in a trunc dataframe that also has the oob values
        decision_data_replace = decision_data.copy()
        decision_data_replace = decision_data_replace[decision_data_replace['identity'] == drop_val]
        decision_data_replace = decision_data_replace.reset_index()
        update_data = update_data.reset_index()
        for x in drop_list + ['c_user', 'v_user', 'g_user', 'e_user']:
            decision_data_replace[x] = update_data.loc[update_data['identity_row'] == decision_data_replace['identity_row'], x]
        decision_data_replace = decision_data_replace.set_index('identity_row')

        # Append the updated decision for the "new" columns from the trunc dataframe we just created to the rest of the identities in the log, and output the updated log
        decision_data_update = decision_data.copy()
        decision_data_update = decision_data_update[decision_data_update['identity'] != drop_val]
        decision_data_update = decision_data_update.append(decision_data_replace)
        decision_data_update.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace = True)
    
    elif button == "skip":
        decision_data_update = decision_data.copy()
        if decision_data_update['skipped'].loc[drop_val + str(curryr) + str(5)] == '':
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skipped'] = flag_name + str(yr_val)
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skip_user'] = user
        else:
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skipped'] = decision_data_update['skipped'].loc[drop_val + str(curryr) + str(5)] + ", " + flag_name + str(yr_val)
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skip_user'] = decision_data_update['skip_user'].loc[drop_val + str(curryr) + str(5)] + ", " + user

    return decision_data_update


# This function produces the items that need to be returned by the update_data callback if the user has just loaded the program
def first_update(data_init, file_used, sector_val, orig_cols, curryr, currqtr, fileyr, use_rol_close):

    data_init = calc_stats(data_init, curryr, currqtr, 0, sector_val)
    data_init = data_init[data_init['yr'] >= curryr - 6]
    data = data_init.copy()
    data = cons_flags(data, curryr, currqtr, sector_val, use_rol_close)
    data = vac_flags(data, curryr, currqtr, sector_val, use_rol_close)
    data = rent_flags(data, curryr, currqtr, sector_val, use_rol_close)
    rank_data_met = data.copy()
    rank_data_met = summarize_flags_ranking(rank_data_met, "met")
    rank_data_met = rank_data_met.rename(columns={'subsector': 'Subsector', 'metcode': 'Metcode'})
    rank_data_sub = data.copy()
    rank_data_sub = summarize_flags_ranking(rank_data_sub, "sub")
    rank_data_sub = rank_data_sub.rename(columns={'subsector': 'Subsector', 'metcode': 'Metcode', 'subid': 'Subid'})

    sum_data = data.copy()
    sum_data = sum_data[sum_data['forecast_tag'] != 0]
    r = re.compile("^._flag*")
    flag_cols = list(filter(r.match, sum_data.columns))
    filt_cols = flag_cols + ['identity', 'identity_us', 'identity_met', 'subid', 'yr', 'subsector', 'metcode']
    sum_data = sum_data[filt_cols]

    if file_used == "oob":
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_original_flags.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
        data.to_pickle(file_path)
        print("Orig Flags Saved")

    return data, rank_data_met, rank_data_sub, sum_data


# This function produces the outputs needed for the update_data callback if the submit button is clicked
#@Timer()
def submit_update(data, shim_data, sector_val, preview_data, orig_cols, user, drop_val, curryr, currqtr, fileyr, use_rol_close, flag_list, skip_list, yr_val):

    shim_data['cons'] = np.where(shim_data['cons'] == '', np.nan, shim_data['cons'])
    shim_data['avail'] = np.where(shim_data['avail'] == '', np.nan, shim_data['avail'])
    shim_data['mrent'] = np.where(shim_data['mrent'] == '', np.nan, shim_data['mrent'])
    shim_data['merent'] = np.where(shim_data['merent'] == '', np.nan, shim_data['merent'])

    if shim_data[['cons', 'avail', 'mrent', 'merent']].isnull().values.all() == True:
        no_shim = True
    else:
        no_shim = False

    if no_shim == True and len(skip_list) == 0:
        message = "You did not enter any changes."
        message_display = True
    else:
        message = ''
        message_display = False

    if message_display == False:
        
        # Implement shims if the user has entered values that differ from the current state of the dataset
        data_orig = data.copy()
        data_orig = data_orig[(data_orig['identity'] == drop_val)].tail(10)
        data_orig = data_orig[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        for index, row in shim_data.iterrows():
            for x in list(shim_data.columns):
                if row[x] == None or row[x] == '':
                    shim_data.at[index, x] = np.nan
        if no_shim == False:
            data, has_diff = get_diffs(shim_data, data_orig, data, drop_val, curryr, currqtr, sector_val)
        else:
            has_diff = 0

        # Update decision log with new values entered via shim, and save the updates
        if has_diff == 1 or len(skip_list) > 0:
            decision_data = use_pickle("in", "decision_log_" + sector_val, False, fileyr, currqtr, sector_val)
        if has_diff == 1:
            decision_data = update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, "submit", False, yr_val)
        
        # Update dataframe to store user flag skips
        if flag_list[0] != "v_flag" and len(skip_list) > 0:
            test = data.loc[drop_val + str(curryr) + str(5)]['flag_skip']
            test = test.split(",")
            test = [x.strip(' ') for x in test]
            for flag in skip_list:
                if flag + str(yr_val) not in test:
                    if data.loc[drop_val + str(curryr) + str(5), 'flag_skip'] == '':
                        data.loc[drop_val + str(curryr) + str(5), 'flag_skip'] = flag + str(yr_val)
                    else:
                        data.loc[drop_val + str(curryr) + str(5), 'flag_skip'] += ", " + flag + str(yr_val)
                    
                    decision_data = update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, "skip", flag, yr_val)
        
        # Save decision log if there was an update, and also save the current state of the edits to ensure nothing gets lost if an error is encountered in later steps
        if has_diff == 1 or len(skip_list) > 0:
            use_pickle("out", "decision_log_" + sector_val, decision_data, fileyr, currqtr, sector_val)
            data_save = data.copy()
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_mostrecentsave.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
            data_save = data_save[orig_cols]
            data_save.to_pickle(file_path)

    preview_data = pd.DataFrame()

    shim_data[['cons', 'avail', 'mrent', 'merent']] = np.nan

    print("End Submit Update")
    return data, preview_data, shim_data, message, message_display

# This function produces the outputs needed for the update_data callback if the preview button is clicked
#@Timer()
def preview_update(data, shim_data, sector_val, preview_data, drop_val, curryr, currqtr, orig_flag_list, skip_list, use_rol_close, flag_yr_val): 
    
    # At this point, will just always allow the button to be clicked, even if there are no edits entered, as want to allow the user to undo a previewed shim. Can think about a way to test if this is an undo vs a first time entry, but small potatoes as will only marginally increase speed
    message = ''
    message_display = False

    if message_display == False:

        data_orig = data.copy()
        data_orig = data_orig[(data_orig['identity'] == drop_val)].tail(10)
        data_orig = data_orig[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        shim_data['cons'] = np.where(shim_data['cons'] == '', np.nan, shim_data['cons'])
        shim_data['avail'] = np.where(shim_data['avail'] == '', np.nan, shim_data['avail'])
        shim_data['mrent'] = np.where(shim_data['mrent'] == '', np.nan, shim_data['mrent'])
        shim_data['merent'] = np.where(shim_data['merent'] == '', np.nan, shim_data['merent'])
        
        preview_data = data.copy()
        preview_data, has_diff = get_diffs(shim_data, data_orig, preview_data, drop_val, curryr, currqtr, sector_val)
            
        if has_diff == 1:    
            
            # Test if the flag will be resolved by the edit by re-running calc stats flag and the relevant flag function 
            # Dont run if the col_issue is simply v_flag, which is an indication that there are no flags at the sub even though an edit is being made

            if orig_flag_list[0] != "v_flag":
                resolve_test = preview_data.copy()
                resolve_test = drop_cols(resolve_test)
                resolve_test = calc_stats(resolve_test, curryr, currqtr, 1, sector_val)
                resolve_test = resolve_test[resolve_test['identity'] == drop_val]
                resolve_test = resolve_test[resolve_test['yr'] == flag_yr_val]
                
                test_flag_list = [x for x in orig_flag_list if x not in skip_list]
                resolve_test = cons_flags(resolve_test, curryr, currqtr, sector_val, use_rol_close)
                resolve_test = vac_flags(resolve_test, curryr, currqtr, sector_val, use_rol_close)
                resolve_test = rent_flags(resolve_test, curryr, currqtr, sector_val, use_rol_close)

                r = re.compile("^._flag*")
                flag_cols = list(filter(r.match, resolve_test.columns))
                resolve_test = resolve_test[flag_cols]
                resolve_test[flag_cols] = np.where((resolve_test[flag_cols] == 999999999), 0, resolve_test[flag_cols])
                resolve_test['sum_flags'] = resolve_test[flag_cols].sum(axis=1)
                resolve_test = resolve_test[resolve_test['sum_flags'] > 0]
                if len(resolve_test) > 0:
                    resolve_test = resolve_test[resolve_test.columns[(resolve_test != 0).any()]]
                    resolve_test = resolve_test.drop(['sum_flags'], axis=1)
                    flags_remaining = list(resolve_test.columns)
                
                    flags_resolved = [x for x in test_flag_list if x not in flags_remaining and x not in skip_list]
                    flags_unresolved = [x for x in test_flag_list if x in flags_remaining and x not in skip_list]
                    new_flags = [x for x in flags_remaining if x not in orig_flag_list and x not in skip_list]
                else:
                    flags_resolved = test_flag_list
                    flags_unresolved = []
                    new_flags = []
            else:
                flags_resolved = []
                flags_unresolved = []
                new_flags = []
            preivew_data['sub_prev'] = np.where(preview_data['identity'] == drop_val, 1, 0)
        else:
            preview_data = pd.DataFrame()
            flags_resolved = []
            flags_unresolved = []
            new_flags = []

    print("End Preview Update")
    return data, preview_data, shim_data, message, message_display, flags_resolved, flags_unresolved, new_flags

# Layout for login page
def login_layout():
    return get_login_layout()

# Main page layout
@validate_login_session
def app_layout():
    return get_app_layout()

# Full multipage app layout
forecast.layout = html.Div([
                    dcc.Location(id='url',refresh=False),
                        html.Div(
                            login_layout(),
                            id='page-content',                      
                                ),
                            ])

# Check to see what url the user entered into the web browser, and return the relevant page based on their choice
@forecast.callback(Output('page-content','children'),
                  [Input('url','pathname')])
def router(pathname):
    if pathname[0:5] == '/home':
        return app_layout()
    elif pathname == '/login':
        return login_layout()
    else:
        return login_layout()

# Authenticate by checking credentials, if correct, authenticate the session, if not, authenticate the session and send user to login
@forecast.callback([Output('url','pathname'),
                    Output('login-alert','children'),
                    Output('url', 'search')],
                    [Input('login-button','n_clicks')],
                    [State('login-username','value'),
                    State('login-password','value'),
                    State('sector_input','value'),
                    State('login-curryr','value'),
                    State('login-currqtr','value'),
                    State('rol_close','value')])
def login_auth(n_clicks, username, pw, sector_input, curryr, currqtr, rol_close):
    if n_clicks is None or n_clicks==0:
        return '/login', no_update, ''
    else:
        credentials = {'user': username, "password": pw, "sector": sector_input}
        if authenticate_user(credentials) == True:
            session['authed'] = True
            pathname = '/home' + '?'
            if len(rol_close) == 0:
                rol_close = "N"
            else:
                rol_close = rol_close[0]
            return pathname, '', username + "/" + sector_input.title() + "/" + str(curryr) + "q" + str(currqtr) + "/" + rol_close
        else:
            session['authed'] = False
            if sector_input is None:
                message = "Select a Sector."
            else:
                message = 'Incorrect credentials.'
            return no_update, dbc.Alert(message, color='danger', dismissable=True), no_update


    
@forecast.callback([Output('store_user', 'data'),
                    Output('sector', 'data'),
                    Output('fileyr', 'data'),
                    Output('currqtr', 'data'),
                    Output('store_rol_close', 'data')],
                    [Input('url', 'search')])
def store_input_vals(url_input):
    if url_input is None:
        raise PreventUpdate
    else:
        user, sector_val, global_vals, use_rol_close = url_input.split("/")
        fileyr, currqtr = global_vals.split("q")
        fileyr = int(fileyr)
        currqtr = int(currqtr)
        return user, sector_val.lower(), fileyr, currqtr, use_rol_close

@forecast.callback([Output('dropman', 'options'),
                    Output('droproll', 'options'),
                    Output('dropsum', 'options'),
                    Output('dropsum', 'value'),
                    Output('key_yr_radios', 'options'),
                    Output('scatter_year_radios', 'options'),
                    Output('scatter_year_radios', 'value'),
                    Output('input_file', 'data'),
                    Output('store_orig_cols', 'data'),
                    Output('curryr', 'data'),
                    Output('dropflag', 'options'),
                    Output('dropflag', 'value'),
                    Output('init_trigger', 'data'),
                    Output('file_load_alert', 'is_open'),
                    Output('rank_view', 'options')],
                    [Input('sector', 'data'),
                    Input('fileyr', 'data'),
                    Input('currqtr', 'data'),
                    Input('store_rol_close', 'data')])
def initial_data_load(sector_val, fileyr, currqtr, use_rol_close):
    if sector_val is None:
        raise PreventUpdate
    else:
        if currqtr == 4:
            curryr = fileyr + 1
        else:
            curryr = fileyr
        oob_data, orig_cols, file_used, file_load_error = initial_load(sector_val, curryr, currqtr, fileyr)

        if file_load_error == False:

            try:
                path_in = Path("{}central/square/data/zzz-bb-test2/python/forecast/coeffs/{}/{}q{}/coeffs.csv".format(get_home(), sector_val, fileyr, currqtr))
                path_out = Path("{}central/square/data/zzz-bb-test2/python/forecast/coeffs/{}/{}q{}/coeffs.pickle".format(get_home(), sector_val, fileyr, currqtr))
                coeffs = pd.read_csv(path_in)
                if sector_val != "ind":
                    coeffs['identity'] = coeffs['identity'] + sector_val.title()
                else:
                    print("set this up")
                coeffs.to_pickle(path_out)
            except:
                print("No coeffs file to load")

            # Export the pickled oob values to begin setting up the decision log if this is the first time the user is running the program
            if file_used == "oob":
                test_cols = list(oob_data.columns)
                oob_cols = []
                for x in test_cols:
                    if "oob" in x and "ask_chg" not in x:
                        oob_cols.append(x)
                decision_data = oob_data.copy()
                decision_data = decision_data.reset_index()
                decision_data = decision_data[decision_data['forecast_tag'] != 0]
                decision_data = decision_data[['identity_row', 'identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr',] + oob_cols]
                update_cols = ['cons_new', 'vac_new', 'abs_new', 'G_mrent_new', 'G_merent_new', 'gap_new', 'inv_new', 'avail_new', 'mrent_new', 'merent_new', 'vac_chg_new'] 
                for x in update_cols:
                    decision_data[x] = np.nan
                decision_data = decision_data.set_index('identity_row')
                decision_data['c_user'] = np.nan
                decision_data['v_user'] = np.nan
                decision_data['g_user'] = np.nan
                decision_data['e_user'] = np.nan
                decision_data['skipped'] = ''
                decision_data['skip_user'] = ''
                use_pickle("out", "decision_log_" + sector_val, decision_data, fileyr, currqtr, sector_val)

            # If nothing has been hovered over yet, set the initial metro/sub to display in the time series graphs as the first metro/sub by default
            first_sub = oob_data['identity'].iloc[0]
            met_combos_temp = list(oob_data['identity_met'].unique())
            met_combos_temp.sort()
            met_combos = list(oob_data['identity_us'].unique()) + met_combos_temp
            default_drop = list(oob_data['identity_us'].unique())[0] 
            available_years = np.arange(curryr, curryr + 10)

            temp = oob_data.copy()
            temp = temp.set_index('identity')
            sub_combos = list(temp.index.unique())

            oob_data, rank_data_met, rank_data_sub, sum_data = first_update(oob_data, file_used, sector_val, orig_cols, curryr, currqtr, fileyr, use_rol_close)              

            use_pickle("out", "main_data_" + sector_val, oob_data, fileyr, currqtr, sector_val)
            use_pickle("out", "rank_data_met_" + sector_val, rank_data_met, curryr, currqtr, sector_val)
            use_pickle("out", "rank_data_sub_" + sector_val, rank_data_sub, curryr, currqtr, sector_val)
            use_pickle("out", "sum_data_" + sector_val, sum_data, curryr, currqtr, sector_val)

            flag_list = get_issue(False, False, False, False, False, False, False, False, False, "list", sector_val)
        
            flag_list_all = list(flag_list.keys())

            if currqtr != 4:
                rank_options=[
                                {'label': '1 yr', 'value': '1'},
                                {'label': '1 yr imp', 'value': '1.5'},
                                {'label': '3 yr', 'value': '3'},
                                {'label': '5 yr', 'value': '5'},
                            ]
            else:
                rank_options=[
                            {'label': '1 yr', 'value': '1'},
                            {'label': '3 yr', 'value': '3'},
                            {'label': '5 yr', 'value': '5'},
                            ]

            init_trigger = True
            print("End Init Load")
            return [{'label': i, 'value': i} for i in sub_combos], [{'label': i, 'value': i} for i in met_combos], [{'label': i, 'value': i} for i in met_combos], default_drop, [{'label': i, 'value': i} for i in available_years], [{'label': i, 'value': i} for i in available_years], curryr, file_used, orig_cols, curryr, [{'label': i, 'value': i} for i in flag_list_all], flag_list_all[0], init_trigger, False, rank_options
        else:
            init_trigger = False
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, init_trigger, no_update, True, no_update

@forecast.callback(Output('out_flag_trigger', 'data'),
                  [Input('sector', 'data'),
                  Input('flag-button', 'n_clicks'),
                  Input('store_init_flags', 'data')],
                  [State('curryr', 'data'),
                  State('currqtr', 'data'),
                  State('fileyr', 'data'),
                  State('init_trigger', 'data'),
                  State('input_file', 'data')])

def output_flags(sector_val, flag_button, init_flags_triggered, curryr, currqtr, fileyr, success_init, file_used):
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        input_id = get_input_id()
        if input_id == "flag-button":
            orig_flags = use_pickle("out", sector_val + "_original_flags", False, fileyr, currqtr, sector_val)
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_all_data.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
            orig_flags.to_csv(file_path, na_rep='')

            r = re.compile("^._flag*")
            flag_cols = list(filter(r.match, orig_flags.columns))
            cols_to_keep = ['identity', 'metcode', 'subid', 'yr', 'qtr'] + flag_cols
            flags_only = orig_flags[cols_to_keep]
            flags_only = flags_only[flags_only['yr'] >= curryr]
            flags_only = flags_only[flags_only['qtr'] == 5]
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_original_flags.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
            flags_only.to_csv(file_path, na_rep='')
            
            data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
            data = data[cols_to_keep]
            data = data[data['yr'] >= curryr]
            data = data[data['qtr'] == 5]
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_current_flags.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
            data.to_csv(file_path, na_rep='')
            print("End Output Flags")
        return True


@forecast.callback(Output('confirm_finalizer', 'displayed'),
                [Input('sector', 'data'),
                Input('store_submit_button', 'data'),
                Input('finalize-button', 'n_clicks')],
                [State('curryr', 'data'),
                State('currqtr', 'data'),
                State('init_trigger', 'data')])
def confirm_finalizer(sector_val, submit_button, download_button, curryr, currqtr, success_init):
    input_id = get_input_id()
    if sector_val is None or success_init == False:
        raise PreventUpdate
    # Need this callback to tie to update_data callback so the callback is not executed before the data is actually updated, but only want to actually save the data when the finalize button is clicked, so only do that when the input id is for the finalize button
    elif input_id == "store_submit_button":
        raise PreventUpdate
    else:
        print("End Confirm Finalizer")
        return True


@forecast.callback([Output('finalize_trigger', 'data'),
                   Output('finalizer_logic_alert', 'is_open'),
                   Output('logic_alert_text', 'children')],
                   [Input('confirm_finalizer', 'submit_n_clicks')],
                   [State('sector', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data')])

def finalize_econ(confirm_click, sector_val, curryr, currqtr, fileyr, success_init):
    input_id = get_input_id()
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        finalized_sub = data.copy()
        finalized_met = data.copy()
        
        if sector_val != "ind":
            finalized_sub = finalized_sub.rename(columns={'rolmrent': 'rolsmre'})
        if sector_val == "apt" or sector_val == "off" or sector_val == "ret":
            finalized_sub = finalized_sub.rename(columns={'rolmerent': 'rolmere'})
        if sector_val == "off" or sector_val == "ret":
            finalized_sub = finalized_sub.rename(columns={'rolmerent': 'rolmeren'})
        if sector_val == 'ind':
            finalized_sub = finalized_sub.rename(columns={'rolmerent': 'rolmeren'})
        
        
        if sector_val == "ind":
            output_cols_sub = ['subsector', 'metcode', 'subid', 'subname', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'h', 'rol_h', 'e', 'rol_e', 't', 'avail', 'occ', 'vac',
                            'rolsvac', 'abs', 'rolsabs', 'mrent', 'rolmrent', 'G_mrent', 'grolsmre', 'merent', 'rolmeren', 'G_merent', 'grolsmer', 'gap', 'rolsgap', 
                            'cons_oob',	'vac_oob', 'abs_oob', 'gap_oob', 'G_mrent_oob',	'G_merent_oob',	'demo',	'conv']
        else:
            output_cols_sub = ['metcode', 'subid', 'yr', 'qtr',	'inv', 'cons', 'rolscon', 'h', 'rol_h',	'e', 't', 'demo', 'conv', 'occ', 'abs', 'rolsabs',
                            'vac', 'rolsvac', 'mrent', 'rolsmre', 'G_mrent', 'grolsmre', 'merent', 'rolmere', 'G_merent', 'grolsmer', 'gap', 'rolsgap', 
                            'cons_oob', 'vac_oob', 'abs_oob', 'G_mrent_oob', 'G_merent_oob', 'gap_oob']

            if sector_val == "off" or sector_val == "ret":
                output_cols_sub.remove('rolmere')

        finalized_sub = finalized_sub[output_cols_sub]

        # Append the deep history to the edits period
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_deep_hist.pickle".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val))
        deep_hist = pd.read_pickle(file_path)
        if sector_val != "ind":
            deep_hist = deep_hist.rename(columns={'rolmrent': 'rolsmre'})
        if sector_val == "apt":
            deep_hist = deep_hist.rename(columns={'rolmerent': 'rolmere'})
        if sector_val == 'ind':
            deep_hist = deep_hist.rename(columns={'rolmerent': 'rolmeren'})
        deep_hist = deep_hist[output_cols_sub]
        finalized_sub = finalized_sub.append(deep_hist, ignore_index=True)
        if sector_val == "ind":
            finalized_sub.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], ascending=[True, True, True, True, True], inplace=True)
        else:
            finalized_sub.sort_values(by=['metcode', 'subid', 'yr', 'qtr'], ascending=[True, True, True, True], inplace=True)
        
        if sector_val == "ind":
            finalized_sub.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace=True)
        elif sector_val == "apt":
            finalized_sub.sort_values(by=['metcode', 'subid', 'yr', 'qtr'], inplace=True)
        elif sector_val == "off":
            finalized_sub.sort_values(by=['metcode', 'subid', 'yr', 'qtr'], inplace=True)

        # Check for illogical values; alert the user if found and do not allow the trend to be finalized
        alert_display = False
        alert_text = ""
        vac_check = finalized_sub.copy()
        if sector_val == "ind" or sector_val == "ret":
            vac_check['identity'] = vac_check['metcode'] + vac_check['subid'].astype(str) + vac_check['subsector']
        else:
            vac_check['identity'] = vac_check['metcode'] + vac_check['subid'].astype(str)
        
        vac_check = vac_check[(vac_check['vac'] < 0) | (vac_check['vac'] > 1)] 
        if len(vac_check) > 0:
            subs_flagged = vac_check['identity'].unique()
            alert_display = True
            alert_text = "The following subs have illogical vacancy level values. Cannot the finalize forecast until they have been fixed: " + ', '.join(map(str, subs_flagged)) 
        else:
            gap_check = finalized_sub.copy()
            if sector_val == "ind" or sector_val == "ret":
                gap_check['identity'] = gap_check['metcode'] + gap_check['subid'].astype(str) + gap_check['subsector']
            else:
                gap_check['identity'] = gap_check['metcode'] + gap_check['subid'].astype(str)
            gap_check = gap_check[(gap_check['gap'] < 0) | (gap_check['gap'] > 1)] 
            if len(gap_check) > 0:
                subs_flagged = gap_check['identity'].unique()
                alert_display = True
                alert_text = "The following subs have illogical gap level values. Cannot finalize the forecast until they have been fixed: " + ', '.join(map(str, subs_flagged)) 
        
        if alert_display == False:
            if sector_val != "ind":
                drop_file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_dropped_cols.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
                drop_cols = pd.read_pickle(drop_file_path)
                drop_cols['join_ident'] = drop_cols['metcode'] + drop_cols['subid'].astype(str) + drop_cols['yr'].astype(str) + drop_cols['qtr'].astype(str)
                drop_cols = drop_cols.drop(['metcode', 'subid', 'yr', 'qtr'], axis=1)
                drop_cols = drop_cols.set_index('join_ident')
                finalized_sub['join_ident'] = finalized_sub['metcode'] + finalized_sub['subid'].astype(str) + finalized_sub['yr'].astype(str) + finalized_sub['qtr'].astype(str)
                finalized_sub = finalized_sub.join(drop_cols, on='join_ident')
                finalized_sub = finalized_sub.drop(['join_ident'], axis=1)
                order_cols = ['metcode', 'subid', 'yr', 'qtr',	'inv', 'cons', 'rolscon', 'h', 'rol_h',	'e', 't', 'Bcon', 'rolcons', 'demo', 'conv', 'occ', 'abs', 'rolsabs',
                                'Babs',	'Brolabs', 'vac', 'rolsvac', 'Bvac', 'rolvac', 'mrent', 'rolsmre', 'Bmrent', 'rolmrent',	'G_mrent', 'grolsmre', 'G_Bmrent', 'merent', 'rolmere',
                                    'G_merent', 'grolsmer', 'Bmerent',	'Brolmeren', 'G_Bmerent', 'gap', 'rolsgap',	'Bgap',	'Brolgap', 'cons_oob', 'vac_oob', 'abs_oob', 'G_mrent_oob',
                                    'G_merent_oob', 'gap_oob']
                if sector_val == "off" or sector_val == "ret":
                    order_cols.remove('rolmere')
                finalized_sub = finalized_sub[order_cols]
            
            if sector_val == "ind":
                for subsector in ["DW", "F"]:
                    finalized_copy = finalized_sub.copy()
                    finalized_copy = finalized_copy[finalized_copy['subsector'] == subsector]
                    finalized_copy = finalized_copy.drop(['subsector'], axis=1)
                    file_path_dta = "{}central/subcast/data/{}/forecast/current/{}subtest_{}_{}q{}.dta".format(get_home(), sector_val, sector_val, subsector, str(curryr), str(currqtr))
                    finalized_copy.to_stata(file_path_dta, write_index=False)
                    file_path_out = "{}central/subcast/data/{}/forecast/current/{}subtest_{}_{}q{}.out".format(get_home(), sector_val, sector_val, subsector, str(curryr), str(currqtr))
                    finalized_copy.to_csv(file_path_out, index=False, na_rep='')
                    
            
            elif sector_val == "apt" or sector_val == "off" or sector_val == "ret":
                file_path_dta = "{}central/subcast/data/{}/forecast/current/{}subtest_{}q{}.dta".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_sub.to_stata(file_path_dta, write_index=False)
                file_path_out = "{}central/subcast/data/{}/forecast/current/{}subtest_{}q{}.out".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_sub.to_csv(file_path_out, index=False, na_rep='')

            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_deep_hist.pickle".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val))
            deep_hist = pd.read_pickle(file_path)
            keep_cols = ['identity_met', 'identity_us', 'subsector', 'metcode', 'subid', 'yr', 'qtr', 'inv', 'rolsinv', 'cons', 'rolscon', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'avail', 'occ', 'abs', 'rolsabs', 'vac',	'rolsvac', 
                        'mrent', 'rolmrent', 'G_mrent', 'grolsmre', 'merent', 'G_merent', 'rolmerent', 'grolsmer', 'gap', 'rolsgap', 'inv_oob', 'cons_oob', 'avail_oob', 'vac_oob', 'abs_oob', 
                        'G_mrent_oob', 'G_merent_oob', 'mrent_oob',	'merent_oob', 'gap_oob']
            deep_hist['identity_met'] = deep_hist['metcode'] + deep_hist['subsector']
            
            ind_expansion_list = ["AA", "AB", "AK", "AN", "AQ", "BD", "BF", "BI", "BR", "BS", "CG", "CM", "CN", "CS", "DC", 
                            "DM", "DN", "EP", "FC", "FM", "FR", "GD", "GN", "GR", "HR", "HL", "HT", "KX", "LL", "LO", 
                            "LR", "LV", "LX", "MW", "NF", "NM", "NO", "NY", "OK", "OM", "PV", "RE", "RO", "SC", "SH", 
                            "SR", "SS", "ST", "SY", "TC", "TM", "TO", "TU", "VJ", "VN", "WC", "WK", "WL", "WS"]    

            if sector_val == "ind":
                deep_hist['expansion'] = np.where(deep_hist['metcode'].isin(ind_expansion_list), "Exp", "Leg")
                deep_hist = deep_hist[(deep_hist['expansion'] == "Leg") | (deep_hist['subsector'] == "DW")]
            else:
                deep_hist['expansion'] = "Leg"
            
            if sector_val == "ind":
                deep_hist['identity_us'] = "US" + deep_hist['subsector'] + deep_hist['expansion']
            else:
                deep_hist['identity_us'] = np.where((deep_hist['metcode'].isin(['PV', 'NO', 'WS'])), "US2", "US1")
            
            deep_hist = deep_hist[keep_cols]
            finalized_met = finalized_met[keep_cols]
            finalized_met = finalized_met.append(deep_hist, ignore_index=True)
            if sector_val == "ind":
                finalized_met.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], ascending=[True, True, True, True, True], inplace=True)
            else:
                finalized_met.sort_values(by=['metcode', 'subid', 'yr', 'qtr'], ascending=[True, True, True, True], inplace=True)

            finalized_us = finalized_met.copy()
            
            finalized_met = rollup(finalized_met, 'met_finalizer', curryr, currqtr, sector_val, "reg", True)

            if sector_val == "ind":
                output_cols_met = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolcons', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'occ', 'abs', 'rolabs', 'vac',	'rolvac', 
                                    'mrent', 'rolmrent', 'G_mrent', 'grolmren', 'merent', 'G_merent', 'rolmeren', 'grolmere', 'gap', 'rolgap', 'cons_oob', 'vac_oob', 'abs_oob', 
                                    'G_mrent_oob', 'G_merent_oob', 'mrent_oob',	'merent_oob', 'gap_oob']
            else:
                output_cols_met = ['metcode', 'yr',	'qtr', 'inv', 'cons', 'rolcons', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'occ', 'abs', 'rolabs', 'vac', 'rolvac',
                                    'mrent', 'rolmrent', 'G_mrent', 'grolmren', 'merent', 'G_merent', 'rolmeren',  'grolmere', 'gap', 'rolgap']

            finalized_met = finalized_met.rename(columns={'rolscon': 'rolcons', 'rol_ask_chg': 'grolmren', 'rolaskrent' :'rolmrent', 'rol_eff_chg': 'grolmere', 'eff_chg': 'G_merent', 
                                                            'rolsabs' :'rolabs', 'askrent': 'mrent', 'effrentoob': 'merent_oob', 'rolsvac': 'rolvac', 'roleffrent': 'rolmeren', 
                                                            'eff_chg_oob': 'G_merent_oob', 'ask_chg_oob': 'G_mrent_oob', 'askrentoob': 'mrent_oob', 'effrent': 'merent', 'ask_chg': 'G_mrent'})

            finalized_met = finalized_met[output_cols_met]

            if sector_val == "ind":
                for subsector in ["DW", "F"]:
                    finalized_copy = finalized_met.copy()
                    finalized_copy = finalized_copy[finalized_copy['subsector'] == subsector]
                    finalized_copy = finalized_copy.drop(['subsector'], axis=1)
                    file_path_dta = "{}central/metcast/data/{}/forecast/current/{}mettest_{}_{}q{}.dta".format(get_home(), sector_val, sector_val, subsector, str(curryr), str(currqtr))
                    finalized_copy.to_stata(file_path_dta, write_index=False)
                    file_path_out = "{}central/metcast/data/{}/forecast/current/{}mettest_{}_{}q{}.out".format(get_home(), sector_val, sector_val, subsector, str(curryr), str(currqtr))
                    finalized_copy.to_csv(file_path_out, index=False, na_rep='')
            
            elif sector_val == "apt" or sector_val == "off" or sector_val == "ret":
                # Since there are deep history periods in the finalized met file that are not in the subdiag input file, load the deep history from the prior quarter's final file and use that for all rolled values prior to 2009, where edits can still theoretically have been made to the trend series
                if currqtr == 4:
                    pastyr = str(curryr - 1)
                    pastqtr = str(currqtr - 1)
                elif currqtr == 1:
                    pastyr =  str(curryr - 1)
                    pastqtr = str(4)
                else:
                    pastyr = str(curryr)
                    pastqtr = str(currqtr - 1)
                file_path_met_deep = Path("{}central/metcast/data/{}/forecast/current/{}mettest_{}q{}.dta".format(get_home(), sector_val, sector_val, str(pastyr), str(pastqtr)))
                met_deep = pd.read_stata(file_path_met_deep)
                met_deep = met_deep[met_deep['yr'] < 2009]
                finalized_met = finalized_met[finalized_met['yr'] >= 2009]
                finalized_met = finalized_met.append(met_deep, ignore_index=True)
                finalized_met.sort_values(by=['metcode', 'yr', 'qtr'], ascending=[True, True, True], inplace=True)
                
                file_path_dta = "{}central/metcast/data/{}/forecast/current/{}mettest_{}q{}.dta".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_met.to_stata(file_path_dta, write_index=False)
                file_path_out = "{}central/metcast/data/{}/forecast/current/{}mettest_{}q{}.out".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_met.to_csv(file_path_out, index=False, na_rep='')

            finalized_us = rollup(finalized_us, 'US_finalizer', curryr, currqtr, sector_val, "reg", True)

            if sector_val == "ind":
                output_cols_us = ['subsector', 'yr', 'qtr', 'US_inv', 'US_cons', 'US_rolcons', 'US_h', 'US_rol_h', 'US_e', 'US_t', 'US_vac', 'US_abs', 'US_rolabs',
                                    'US_mrent', 'US_G_mrent', 'US_merent', 'US_G_merent', 'US_gap']
            else:
                output_cols_us = ['yr', 'qtr', 'US_inv', 'US_cons', 'US_rolcons', 'US_h', 'US_rol_h', 'US_e', 'US_t', 'US_vac', 'US_abs', 'US_rolabs',
                                    'US_mrent', 'US_G_mrent', 'US_merent', 'US_G_merent', 'US_gap']

            finalized_us = finalized_us.rename(columns={'rolscon': 'rolcons', 'rolsabs': 'rolabs', 'askrent': 'mrent', 'ask_chg': 'G_mrent', 'effrent': 'merent', 'eff_chg': 'G_merent'})
            for x in list(finalized_us.columns):
                if x not in ['subsector', 'yr', 'qtr']:
                    finalized_us.rename(columns={x: 'US_' + x}, inplace=True)
            finalized_us = finalized_us[output_cols_us]

            finalized_us['US_G_mrent'] = np.where(finalized_us['yr'] >= curryr, finalized_us['US_G_mrent'], np.nan)
            finalized_us['US_G_merent'] = np.where(finalized_us['yr'] >= curryr, finalized_us['US_G_merent'], np.nan)

            finalized_us = finalized_us[(finalized_us['yr'] > 1999) | ((finalized_us['yr'] == 1999) & (finalized_us['qtr'] == 5))]

            if sector_val == "ind":
                for subsector in ["DW", "F"]:
                    finalized_copy = finalized_us.copy()
                    finalized_copy = finalized_copy[finalized_copy['subsector'] == subsector]
                    finalized_copy = finalized_copy.drop(['subsector'], axis=1)
                    file_path_dta = "{}central/metcast/data/{}/forecast/current/US_{}test_{}_{}q{}.dta".format(get_home(), sector_val, sector_val, subsector, str(curryr), str(currqtr))
                    finalized_copy.to_stata(file_path_dta, write_index=False)
                    file_path_out = "{}central/metcast/data/{}/forecast/current/US_{}test_{}_{}q{}.out".format(get_home(), sector_val, sector_val, subsector, str(curryr), str(currqtr))
                    finalized_copy.to_csv(file_path_out, index=False, na_rep='')
            
            elif sector_val == "apt" or sector_val == "off" or sector_val == "ret":
                file_path_dta = "{}central/metcast/data/{}/forecast/current/US{}test_{}q{}.dta".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_us.to_stata(file_path_dta, write_index=False)
                file_path_out = "{}central/metcast/data/{}/forecast/current/US{}test_{}q{}.out".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_us.to_csv(file_path_out, index=False, na_rep='')

            # Convert decision log to csv file and save in OutputFiles folder
            decision_log_in_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/decision_log_{}.{}".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val, 'pickle'))
            decision_log = pd.read_pickle(decision_log_in_path)
            decision_log_out_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/decision_log_{}.{}".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val, 'csv'))
            decision_log.to_csv(decision_log_out_path)

        print("End Finalize Econ")
        return True, alert_display, alert_text

@forecast.callback([Output('store_flag_skips', 'data'),
                   Output('skip_list_trigger', 'data')],
                   [Input('sector', 'data'),
                   Input('submit-button', 'n_clicks'),
                   Input('preview-button', 'n_clicks')],
                   [State('curryr', 'data'),
                   State('currqtr', 'data'),
                   State('flag_description_noprev', 'children'),
                   State('flag_description_resolved', 'children'),
                   State('flag_description_unresolved', 'children'),
                   State('flag_description_new', 'children'),
                   State('flag_description_skipped', 'children'),
                   State('init_trigger', 'data')])

def get_skip_list(sector_val, submit_button, preview_button, curryr, currqtr, skip_input_noprev, skip_input_resolved, skip_input_unresolved, skip_input_new, skip_input_skipped, success_init):
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        input_id = get_input_id()
        
        # If there is a flag description, use this crazy dict/list slicer to get the actual values of the children prop so we can see what flags the user wants to skip
        if input_id != "submit_button" and input_id != "preview_button":
            if skip_input_noprev == "No flags for this year at the submarket":
                skip_list = []
            elif skip_input_noprev != None or skip_input_resolved != None or skip_input_unresolved != None or skip_input_new != None or skip_input_skipped != None:
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
            else:
                skip_list = []
            
            print("End Get Skip List")
            return skip_list, no_update
        
        else:
            print("End Get Skip List")
            return no_update, no_update

@forecast.callback([Output('manual_message', 'message'),
                    Output('manual_message', 'displayed'),
                    Output('store_all_buttons', 'data'),
                    Output('store_submit_button', 'data'),
                    Output('store_preview_button', 'data'),
                    Output('store_init_flags', 'data'),
                    Output('store_flag_resolve', 'data'),
                    Output('store_flag_unresolve', 'data'),
                    Output('store_flag_new', 'data')],
                    [Input('sector', 'data'),
                    Input('submit-button', 'n_clicks'),
                    Input('preview-button', 'n_clicks'),
                    Input('init_trigger', 'data'),
                    Input('skip_list_trigger', 'data')],
                    [State('store_orig_cols', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('store_user', 'data'),
                    State('input_file', 'data'),
                    State('comment_cons', 'value'),
                    State('comment_avail', 'value'),
                    State('comment_rent', 'value'),
                    State('dropman', 'value'),
                    State('store_rol_close', 'data'),
                    State('flag_list', 'data'),
                    State('key_yr_radios', 'value'),
                    State('store_flag_skips', 'data')])
#@Timer()
def update_data(sector_val, submit_button, preview_button, success_init, skip_trigger, orig_cols, curryr, currqtr, fileyr, user, file_used, cons_c, avail_c, rent_c, man_val, use_rol_close, flag_list, yr_val, skip_list):

    input_id = get_input_id()
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)

        if input_id == 'submit-button' or input_id == 'skip-button':
            data = data.reset_index()
            data = data.set_index('identity')
            data.loc[man_val, 'cons_comment'] = cons_c
            data.loc[man_val, 'avail_comment'] = avail_c
            data.loc[man_val, 'rent_comment'] = rent_c
            data = data.reset_index()
            data = data.set_index('identity_row')
        
        if input_id == 'submit-button' or input_id == 'preview-button':
            preview_data = use_pickle("in", "preview_data_" + sector_val, False, fileyr, currqtr, sector_val)
            shim_data = use_pickle("in", "shim_data_" + sector_val, False, fileyr, currqtr, sector_val)

        if input_id == 'submit-button':
            data, preview_data, shim_data, message, message_display = submit_update(data, shim_data, sector_val, preview_data, orig_cols, user, man_val, curryr, currqtr, fileyr, use_rol_close, flag_list, skip_list, yr_val)

        elif input_id == 'preview-button':
            data, preview_data, shim_data, message, message_display, flags_resolved, flags_unresolved, flags_new = preview_update(data, shim_data, sector_val, preview_data, man_val, curryr, currqtr, flag_list, skip_list, use_rol_close, yr_val)
        
        else:
            message = ''
            message_display = False
            preview_data = pd.DataFrame()
            shim_data = pd.DataFrame()
        
        if input_id == "submit-button":
            use_pickle("out", "main_data_" + sector_val, data, fileyr, currqtr, sector_val)
        use_pickle("out", "preview_data_" + sector_val, preview_data, fileyr, currqtr, sector_val)
        use_pickle("out", "shim_data_" + sector_val, shim_data, curryr, fileyr, sector_val)

        # Need to set this variable so that the succeeding callbacks will only fire once update is done
        # This works because it makes the callbacks that use elements produced in this callback have an input that is linked to an output of this callback, ensuring that they will only be fired once this one completes
         # Need to set this variable so that the succeeding callbacks will only fire once update is done
        # This works because it makes the callbacks that use elements produced in this callback have an input that is linked to an output of this callback, ensuring that they will only be fired once this one completes
        # But dont update this if the user didnt enter any shims, as we dont want the succeeding callbacks to update
        # We need five - to differentiate if suceeding callbacks should fire regardless of what button was clicked, or if they should only fire only if a particular button was clicked, or if they should only fire if this is initial load
        if message_display == True:
            all_buttons = no_update
            submit_button = no_update
            preview_button = no_update
            init_flags = no_update
        else:
            if input_id == "submit-button":
                all_buttons = 1
                submit_button = 1
                preview_button = no_update
                init_flags = no_update
            elif input_id == "preview-button":
                all_buttons = 1
                submit_button = no_update
                preview_button = 1
                init_flags = no_update
            else:
                all_buttons = 1
                submit_button = 1
                preview_button = 1
                init_flags = 1
        
        if input_id != "preview-button":
            flags_resolved = []
            flags_unresolved = []
            flags_new = []

        print("End Update Data")
        return message, message_display, all_buttons, submit_button, preview_button, init_flags, flags_resolved, flags_unresolved, flags_new

@forecast.callback(Output('download_trigger', 'data'),
                   [Input('sector', 'data'),
                   Input('store_submit_button', 'data'),
                   Input('download-button', 'n_clicks')],
                   [State('curryr', 'data'),
                   State('currqtr', 'data'),
                   State('fileyr', 'data'),
                   State('store_orig_cols', 'data'),
                   State('input_file', 'data'),
                   State('init_trigger', 'data')])

def output_edits(sector_val, submit_button, download_button, curryr, currqtr, fileyr, orig_cols, file_used, success_init):
    input_id = get_input_id()
    if sector_val is None or success_init == False:
        raise PreventUpdate
    # Need this callback to tie to update_data callback so the csv is not set before the data is actually updated, but dont want to call the set csv function each time submit is clicked, so only do that when the input id is for the download button
    elif input_id == "store_submit_button":
        raise PreventUpdate
    else:
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        
        edits_output = data.copy()
        edits_output = edits_output[orig_cols]
        deep_file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_deep_hist.pickle".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val))
        deep_history = pd.read_pickle(deep_file_path)
        deep_history = deep_history[orig_cols]
        edits_output = edits_output.append(deep_history)
        edits_output.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace=True)
        edits_output['cons_comment'] = np.where(edits_output['cons_comment'] == "Enter Cons Shim Note Here", '', edits_output['cons_comment'])
        edits_output['avail_comment'] = np.where(edits_output['avail_comment'] == "Enter Avail Shim Note Here", '', edits_output['avail_comment'])
        edits_output['rent_comment'] = np.where(edits_output['rent_comment'] == "Enter Rent Shim Note Here", '', edits_output['rent_comment'])
        if sector_val == "apt" or sector_val == "off" or sector_val == "ret":
            edits_output['inv'] = np.where(edits_output['yr'] == 1998, "", edits_output['inv'])
            edits_output['inv'] = np.where((edits_output['yr'] == 2003) & ((edits_output['metcode'] == "PV") | (edits_output['metcode'] == "WS")), "", edits_output['inv'])

        file_path = "{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_edits_forecast.csv".format(get_home(), sector_val, fileyr, currqtr, sector_val)
        edits_output.to_csv(file_path, index=False, na_rep='')

        print("End Set CSV")
        return True

@forecast.callback([Output('dropman', 'value'),
                    Output('key_yr_radios', 'value'),],
                    [Input('sector', 'data'),
                    Input('init_trigger', 'data'),
                    Input('store_submit_button', 'data')],
                    [State('identity_val', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('store_rol_close', 'data'),
                    State('key_yr_radios', 'value')])
def set_shim_drop(sector_val, success_init, submit_button, identity_val, curryr, currqtr, fileyr, use_rol_close, orig_yr_val):
    input_id = get_input_id()
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        input_id = get_input_id()

        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        
        if input_id == "init_trigger":
            flag_list, identity_val, yr_val = flag_examine(data, False, False, curryr, currqtr, orig_yr_val)
        else:
            # In order to get the next sub that is flagged, we need to recalc stats and flags to update the data to see if the old flag is removed.
            # Downside is this will slow down performance, as still need to call these functions in the next callback to get the new outputs, and cant combine due to circular callback issue
            data = drop_cols(data)
            data = calc_stats(data, curryr, currqtr, 1, sector_val)
            data = cons_flags(data, curryr, currqtr, sector_val, use_rol_close)
            data = vac_flags(data, curryr, currqtr, sector_val, use_rol_close)
            data = rent_flags(data, curryr, currqtr, sector_val, use_rol_close)
            flag_list, identity_val, yr_val = flag_examine(data, False, False, curryr, currqtr, orig_yr_val)
            use_pickle("out", "main_data_" + sector_val, data, fileyr, currqtr, sector_val)
        
        print("End Set Shim Drop") 
        return identity_val, yr_val

            
        
@forecast.callback([Output('identity_val', 'data'),
                   Output('flag_list', 'data'),
                   Output('key_met_radios', 'value')],
                   [Input('dropman', 'value'),
                   Input('sector', 'data'),
                   Input('init_trigger', 'data'),
                   Input('key_yr_radios', 'value')],
                   [State('curryr', 'data'),
                   State('currqtr', 'data'),
                   State('fileyr', 'data'),
                   State('init_trigger', 'data'),
                   State('store_rol_close', 'data')])

def calc_stats_flags(drop_val, sector_val, init_fired, yr_val, curryr, currqtr, fileyr, success_init, use_rol_close):
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:    
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)

        input_id = get_input_id()
        if input_id != "dropman" and input_id != "key_yr_radios":
            data = drop_cols(data)
            data = calc_stats(data, curryr, currqtr, sector_val)
            data = cons_flags(data, curryr, currqtr, sector_val, use_rol_close)
            data = vac_flags(data, curryr, currqtr, sector_val, use_rol_close)
            data = rent_flags(data, curryr, currqtr, sector_val, use_rol_close)
    
        flag_list, identity_val, yr_val = flag_examine(data, drop_val, True, curryr, currqtr, yr_val)

        # Reset the radio button to the correct variable based on the new flag
        if flag_list[0] != "v_flag":
            key_met_radio_val = flag_list[0][0]
        else:
            key_met_radio_val = 'v'

        # If the dropdown was used, the preview dataset should be cleared
        if input_id == "dropman":
            preview_data = pd.DataFrame()
            use_pickle("out", "preview_data_" + sector_val, preview_data, fileyr, currqtr, sector_val)       
    
        print("End Calc Stats and Flags")
        return identity_val, flag_list, key_met_radio_val
      

@forecast.callback([Output('rank_table_met', 'data'),
                    Output('rank_table_met', 'columns'),
                    Output('rank_table_met', 'style_data_conditional'),
                    Output('rank_table_sub', 'data'),
                    Output('rank_table_sub', 'columns'),
                    Output('rank_table_sub', 'style_data_conditional'),
                    Output('rank_table_container', 'style'),
                    Output('sum_table', 'data'),
                    Output('sum_table', 'columns'),
                    Output('sum_table', 'style_data_conditional'),
                    Output('sum_container', 'style')],
                    [Input('sector', 'data'),
                    Input('dropsum', 'value'),
                    Input('store_init_flags', 'data')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data')])
def display_summary(sector_val, drop_val, init_flags, curryr, currqtr, fileyr, success_init):
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        dash_curryr = str(curryr)
        dash_second_five = curryr + 5
        dash_second_five = str(dash_second_five)
        
        input_id = get_input_id()

        sum_style = {'display': 'block', 'padding-top': '20px'}
        rank_style = {'display': 'block'}

        if input_id == 'store_init_flags':
            rank_data_met = use_pickle("in", "rank_data_met_" + sector_val, False, fileyr, currqtr, sector_val)
            rank_data_sub = use_pickle("in", "rank_data_sub_" + sector_val, False, fileyr, currqtr, sector_val)
            sum_data = use_pickle("in", "sum_data_" + sector_val, False, fileyr, currqtr, sector_val)

            sum_data = summarize_flags(sum_data, drop_val)
            type_dict_rank_met, format_dict_rank_met = get_types(rank_data_met, sector_val)
            highlighting_rank_met = get_style("partial", rank_data_met, dash_curryr, dash_second_five)
            type_dict_rank_sub, format_dict_rank_sub = get_types(rank_data_sub, sector_val)
            highlighting_rank_sub = get_style("partial", rank_data_sub, dash_curryr, dash_second_five)

            type_dict_sum, format_dict_sum = get_types(sum_data, sector_val)
            highlighting_sum = get_style("partial", sum_data, dash_curryr, dash_second_five)
        
            return rank_data_met.to_dict('rows'), [{'name':['Top Ten Flagged Metros', rank_data_met.columns[i]], 'id': rank_data_met.columns[i], 'type': type_dict_rank_met[rank_data_met.columns[i]], 'format': format_dict_rank_met[rank_data_met.columns[i]]} 
                                for i in range(0, len(rank_data_met.columns))], highlighting_rank_met, rank_data_sub.to_dict('rows'), [{'name':['Top Ten Flagged Submarkets', rank_data_sub.columns[i]], 'id': rank_data_sub.columns[i], 'type': type_dict_rank_sub[rank_data_sub.columns[i]], 'format': format_dict_rank_sub[rank_data_sub.columns[i]]} 
                                for i in range(0, len(rank_data_sub.columns))], highlighting_rank_sub, rank_style, sum_data.to_dict('rows'), [{'name': ['OOB Initial Flag Summary', sum_data.columns[i]], 'id': sum_data.columns[i], 'type': type_dict_sum[sum_data.columns[i]], 'format': format_dict_sum[sum_data.columns[i]]} 
                                for i in range(0, len(sum_data.columns))], highlighting_sum, sum_style
        else:
            sum_data = use_pickle("in", "sum_data_" + sector_val, False, fileyr, currqtr, sector_val)
            sum_data = summarize_flags(sum_data, drop_val)
            type_dict_sum, format_dict_sum = get_types(sum_data, sector_val)
            highlighting_sum = get_style("partial", sum_data, dash_curryr, dash_second_five)
            print("End Display Summary")
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, sum_data.to_dict('rows'), [{'name': ['OOB Initial Flag Summary', sum_data.columns[i]], 'id': sum_data.columns[i], 'type': type_dict_sum[sum_data.columns[i]], 'format': format_dict_sum[sum_data.columns[i]]} 
                                for i in range(0, len(sum_data.columns))], highlighting_sum, sum_style


@forecast.callback([Output('flag_filt', 'data'),
                    Output('flag_filt', 'columns'),
                    Output('flag_filt', 'style_table'),
                    Output('flag_container', 'style')],
                    [Input('dropflag', 'value'),
                    Input('sector', 'data'),
                    Input('store_submit_button', 'data')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data')])

def filter_flag_table(drop_val, sector_val, submit_button, curryr, currqtr, fileyr, success_init):
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:

        flag_filt_style = {'display': 'block', 'padding-top': '40px'}

        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        dataframe = data.copy()
        dataframe = dataframe[[drop_val, 'identity', 'flag_skip']]
        dataframe = dataframe[(dataframe[drop_val] > 0) & (dataframe[drop_val] < 999999999)]
        if len(dataframe) > 0:
            count_skip = dataframe['flag_skip'].str.count(drop_val)
            dataframe['count_skips'] = count_skip
            dataframe['count_skips_all'] = dataframe.groupby('identity')['count_skips'].transform('sum')
            dataframe['count_rows'] = dataframe.groupby('identity')[drop_val].transform('count')
            dataframe['flags_left'] = dataframe['count_rows'] - dataframe['count_skips_all']
            dataframe['flag_count_row'] = dataframe.groupby('identity').transform('cumcount', ascending=False)
            dataframe['flag_count_row'] = dataframe['flag_count_row'] + 1
            dataframe = dataframe[(dataframe['flag_count_row'] <= dataframe['flags_left'])]
            dataframe = dataframe.drop(['flag_skip'], axis=1)
            dataframe['Total Flags'] = dataframe[drop_val].count()
            temp = dataframe.copy()
            temp = temp.reset_index()
            temp = temp.head(1)
            temp = temp[['Total Flags']]
            title = "Total Flags: " + str(temp['Total Flags'].loc[0])
            dataframe.sort_values(by=['identity', drop_val], ascending=[True, True], inplace=True)
            dataframe = dataframe.drop_duplicates('identity')
            dataframe = dataframe[['identity', drop_val]]
            dataframe = dataframe.rename(columns={'identity': 'Submarkets With Flag', drop_val: 'Flag Ranking'})
            dataframe.sort_values(by=['Flag Ranking'], inplace=True)
        elif len(dataframe) == 0:
            title =  'Total Flags: 0'
            data_fill = {'Submarkets With Flag': ['No Submarkets Flagged'],
                    'Flag Ranking': [0]}
            dataframe = pd.DataFrame(data_fill, columns=['Submarkets With Flag', 'Flag Ranking'])
        print("End Flag Filt")
        if len(dataframe) >= 10:
            return dataframe.to_dict('rows'), [{'name': [title, dataframe.columns[i]], 'id': dataframe.columns[i]} 
                    for i in range(0, len(dataframe.columns))], {'height': '350px', 'overflowY': 'auto'}, flag_filt_style
        else:
            return dataframe.to_dict('rows'), [{'name': [title, dataframe.columns[i]], 'id': dataframe.columns[i]} 
                    for i in range(0, len(dataframe.columns))], {'height': '350px', 'overflowY': 'visible'}, flag_filt_style


@forecast.callback([Output('man_edits', 'data'),
                    Output('man_edits', 'columns'),
                    Output('man_edits', 'style_data_conditional'),
                    Output('data_view', 'data'),
                    Output('data_view', 'columns'),
                    Output('data_view', 'style_data_conditional'),
                    Output('key_metrics', 'data'),
                    Output('key_metrics', 'columns'),
                    Output('key_metrics', 'style_data_conditional'),
                    Output('key_emp', 'data'),
                    Output('key_emp', 'columns'),
                    Output('key_emp', 'style_data_conditional'),
                    Output('flag_description_noprev', 'children'),
                    Output('flag_description_resolved', 'children'),
                    Output('flag_description_unresolved', 'children'),
                    Output('flag_description_new', 'children'),
                    Output('flag_description_skipped', 'children'),
                    Output('noprev_container', 'style'),
                    Output('resolved_container', 'style'),
                    Output('unresolved_container', 'style'),
                    Output('new_container', 'style'),
                    Output('skipped_container', 'style'),
                    Output('vac-series', 'figure'),
                    Output('rent-series', 'figure'),
                    Output('man_edits_container', 'style'),
                    Output('man_data_container', 'style'),
                    Output('comment_cons', 'value'),
                    Output('comment_avail', 'value'),
                    Output('comment_rent', 'value')],
                    [Input('sector', 'data'),
                    Input('dropman', 'value'),
                    Input('store_all_buttons', 'data'),
                    Input('key_met_radios', 'value'),
                    Input('key_yr_radios', 'value')],
                    [State('flag_list', 'data'),
                    State('identity_val', 'data'),
                    State('store_orig_cols', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('store_flag_resolve', 'data'),
                    State('store_flag_unresolve', 'data'),
                    State('store_flag_new', 'data'),
                    State('store_flag_skips', 'data'),
                    State('init_trigger', 'data')])  
#@Timer()
def output_data(sector_val, man_val, all_buttons, key_met_val, yr_val, flag_list, identity_val, orig_cols, curryr, currqtr, fileyr, flags_resolved, flags_unresolved, flags_new, flags_skipped, success_init):  
    
    input_id = get_input_id()

    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        dash_curryr = str(curryr)
        dash_second_five = curryr + 5
        dash_second_five = str(dash_second_five)

        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        preview_data = use_pickle("in", "preview_data_" + sector_val, False, fileyr, currqtr, sector_val)
        shim_data = use_pickle("in", "shim_data_" + sector_val, False, fileyr, currqtr, sector_val)

        # Since the flag counter was moved to its own callback, we can simply drop all flag cols here because we no longer need them to reduce dimensionality
        r = re.compile("^._flag*")
        flag_cols = list(filter(r.match, data.columns))
        data = data.drop(flag_cols, axis=1)

        # Determine what fields in the shim data set are editable and what are not
        display_filt = ['metcode', 'subid', 'subsector', 'yr', 'qtr', 'cons', 'avail', 'mrent', 'merent']
        edit_dict = {}
        for x in display_filt:
            if x == 'yr' or x == 'qtr':
                edit_dict[x] = False
            else:
                edit_dict[x] = True

        # Reset the shim view to all nulls, unless the user is previewing a change, or if a non button input was selected and there are shims entered
        if len(preview_data) == 0 or len(shim_data) == 0:
            shim_data = data.copy()
            shim_data[['cons', 'avail', 'mrent', 'merent']] = np.nan
            shim_data = shim_data[(shim_data['identity'] == man_val) ].tail(10)
        shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        highlighting_shim = get_style("full", shim_data, dash_curryr, dash_second_five)

        # If the user changes the sub they want to edit, reset the shim section
        if (len(preview_data) > 0 and  identity_val != preview_data[preview_data['sub_prev'] == 1].reset_index().loc[0]['identity']) or (shim_data.reset_index()['identity_row'].str.contains(identity_val).loc[0] == False):
            preview_data = pd.DataFrame()
            shim_data = data.copy()
            shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
            shim_data = shim_data[(shim_data['yr'] >= curryr) & (shim_data['qtr'] == 5)]
            shim_data = shim_data[(shim_data['identity'] == man_val)]
            shim_data[['cons', 'avail', 'mrent', 'merent']] = np.nan

        # Get the Divs that will display the current flags at the sub, as well as the metrics to highlight based on the flag
        issue_description_noprev, issue_description_resolved, issue_description_unresolved, issue_description_new, issue_description_skipped = get_issue(data, flag_list, flags_resolved, flags_unresolved, flags_new, flags_skipped, curryr, currqtr, len(preview_data), "specific", sector_val)
        if len(issue_description_noprev) == 0:
            style_noprev = {'display': 'none'}
        else:
            if flag_list[0] == "v_flag":
                style_noprev = {'padding-left': '10px', 'display': 'block', 'font-size': '24px', 'text-align': 'center'}
            else:
                style_noprev = {'padding-left': '10px', 'display': 'block', 'font-size': '16px', 'text-align-last': 'center'}
        if len(issue_description_resolved) == 0:
            style_resolved = {'display': 'none'}
        else:
            style_resolved = {'padding-left': '10px', 'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold'}
            if len(issue_description_unresolved) == 0 and len(issue_description_new) == 0 and len(issue_description_skipped) > 0:
                style_resolved['text-align-last'] = 'center'
        if len(issue_description_unresolved) == 0:
            style_unresolved = {'display': 'none'}
        else:
            style_unresolved = {'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold'}
            if len(issue_description_resolved) == 0:
                style_unresolved['padding-left'] = '10px'
            if len(issue_description_new) == 0 and len(issue_description_skipped) == 0:
                style_unresolved['text-align-last'] = 'center'
        if len(issue_description_new) == 0:
            style_new = {'display': 'none'}
        else:
            style_new = {'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold'}
            if len(issue_description_resolved) == 0 and len(issue_description_unresolved) == 0:
                style_new['padding-left'] = '10px'
            if len(issue_description_skipped) == 0:
                style_new['text-align-last'] = 'center'
        if len(issue_description_skipped) == 0:
            style_skipped = {'display': 'none'}
        else:
            style_skipped = {'display': 'inline-block', 'font-size': '16px', 'text-align-last': 'center'}
            if len(issue_description_resolved) == 0 and len(issue_description_unresolved) == 0 and len(issue_description_new) == 0:
                style_skipped['padding-left'] = '10px'
        
        # Call the function to set up the sub time series graphs
        if len(preview_data) > 0:
            data_vac, data_rent = sub_met_graphs(preview_data, "sub", curryr, currqtr, fileyr, sector_val)
        else:
            data_vac, data_rent = sub_met_graphs(data[(data['identity'] == man_val)], "sub", curryr, currqtr, fileyr, sector_val)
        
        # Set the data for the main data display, using the correct data set based on whether the user is previewing a shim or not
        if len(preview_data) > 0:
            display_data = preview_data.copy()
        else:
            display_data = data.copy()
            display_data = display_data[(display_data['identity'] == man_val)]
        
        # Set the display cols for the main data table
        display_cols, key_met_cols, key_emp_cols = set_display_cols(data, man_val, sector_val, curryr, currqtr, key_met_val, yr_val)
        display_data = display_frame(display_data, man_val, display_cols, curryr)

        # Remove pipeline support cons columns if no cons flags are selected and the key metrics choice is not cons, to give us more space for the columns of the main data display
        has_cons_flag = sum([1 for x in flag_list if x[0:2] == 'c_'])
        if has_cons_flag == 0 and key_met_val != "c":
            display_data = display_data.drop(['h', 'rol_h', 'e', 'rol_e', 't'], axis=1)
        else:
            display_data = display_data.drop(['occ'], axis=1)

        # Rename vars without underscores to help with display
        for col_name in list(display_data.columns):
            if "_" in col_name:
                col_name_replace = col_name.replace("_", " ")
                display_data.rename(columns={col_name: col_name_replace}, inplace=True)
        display_data = display_data.rename(columns={'rolscon': 'rol cons', 'rolsvac': 'rol vac', 'rolsvac chg': 'rol vac chg', 'rolsabs': 'rol abs',
                                                    'grolsmre': 'rol Gmrent', 'grolsmer': 'rol Gmerent', 'G mrent': 'Gmrent', 'G merent': 'Gmerent', 'rolsgap chg': 'rol gap chg'})
        
        # Get the data types and data formats for the data display
        type_dict_data, format_dict_data = get_types(display_data, sector_val)
        highlighting_display = get_style("full", display_data, dash_curryr, dash_second_five)

        # Set the pixels neccesary to maintain the correct alignment of the shim view and the main data view, based on what type of historical series the selected sub has
        # Since not all subs have history going back to curryr - 5, the length of the main data set is not always consistent, thus the need for a variable pixel number
        len_display = len(display_data)

        if currqtr == 4:
            qtr_add = 0
        else:
            qtr_add = currqtr

        if len_display < 19 + qtr_add:
            if len_display == 19 + qtr_add - 1:
                padding = str(max((38 + (currqtr * 30)),0)) + 'px'
            else:
                padding = '23px'
        elif len_display == 19 + qtr_add:
            padding = padding = str(max((68 + (currqtr * 30)),0)) + 'px'
        spacing_style_shim = {'padding-left': '30px', 'display': 'block', 'padding-top': padding}

        # Due to the 2020q2 new subs not having enough history yet, we need to move the main data display down a bit until enough history gets added there.
        # Should only be relevant before 2021Q2
        if len_display < 19 + qtr_add - 1 and curryr == 2021 and currqtr == 1:
            padding = '14px'
            spacing_style_data = {'display': 'block', 'padding-top': padding} 
        else: 
            spacing_style_data = {'display': 'block'}

        # Set the key metrics and employment metrics display
        key_metrics = data.copy()
        key_metrics, key_emp = gen_metrics(key_metrics, man_val, key_met_cols, key_emp_cols, yr_val)
        highlighting_metrics = get_style("partial", key_metrics, dash_curryr, dash_second_five)
        highlighting_emp = get_style("partial", key_emp, dash_curryr, dash_second_five)
     
        title_met = "Key Metrics " + str(yr_val)
        title_emp = "Employment Metrics " + str(yr_val)
        type_dict_metrics, format_dict_metrics = get_types(key_metrics, sector_val)
        type_dict_emp, format_dict_emp = get_types(key_emp, sector_val)

        # Retrieve the shim comments from the dataframe and display them to the user
        comment = data.copy()
        comment = comment[(comment['identity'] == man_val) & (comment['yr'] == curryr + 1)]
        comment = comment.set_index('identity')
        cons_comment = comment['cons_comment'].loc[man_val]
        avail_comment = comment['avail_comment'].loc[man_val]
        rent_comment = comment['rent_comment'].loc[man_val]

        if cons_comment == "":
            cons_comment = 'Enter Cons Shim Note Here'
        if avail_comment == "":
            avail_comment = 'Enter Avail Shim Note Here'
        if rent_comment == "":
            rent_comment = 'Enter Rent Shim Note Here'


        # Get the submarket name and use it in the data table header
        temp = data.copy()
        sub_name = temp[temp['identity'] == man_val].reset_index().loc[0]['subname']
        if sub_name != "N/A":
            data_title = man_val + " "  + sub_name + " Submarket Data"
        else:
            data_title = "Submarket Data"

        # Output the main data set to a pickle file, to be read in and used by the scatter plot callback
        use_pickle("out", "scatter_data_" + sector_val, data, fileyr, currqtr, sector_val)

    print("End Output Display")
    return shim_data.to_dict('rows'), [{'name': ['Insert Manual Fix', shim_data.columns[i]], 'id': shim_data.columns[i], 'type': type_dict_data[shim_data.columns[i]], 'format': format_dict_data[shim_data.columns[i]], 'editable': edit_dict[shim_data.columns[i]]} 
                            for i in range(3, len(shim_data.columns))], highlighting_shim, display_data.to_dict('rows'), [{'name': [data_title, display_data.columns[i]], 'id': display_data.columns[i], 'type': type_dict_data[display_data.columns[i]], 'format': format_dict_data[display_data.columns[i]]} 
                            for i in range(0, len(display_data.columns))], highlighting_display, key_metrics.to_dict('records'), [{'name': [title_met, key_metrics.columns[i]], 'id': key_metrics.columns[i], 'type': type_dict_metrics[key_metrics.columns[i]], 'format': format_dict_metrics[key_metrics.columns[i]]} 
                            for i in range(0, len(key_metrics.columns))], highlighting_metrics, key_emp.to_dict('records'), [{'name': [title_emp, key_emp.columns[i]], 'id': key_emp.columns[i], 'type': type_dict_emp[key_emp.columns[i]], 'format': format_dict_emp[key_emp.columns[i]]} 
                            for i in range(0, len(key_emp.columns))], highlighting_emp, issue_description_noprev, issue_description_resolved, issue_description_unresolved, issue_description_new, issue_description_skipped, style_noprev, style_resolved, style_unresolved, style_new, style_skipped, go.Figure(data=data_vac), go.Figure(data=data_rent), spacing_style_shim, spacing_style_data, cons_comment, avail_comment, rent_comment
        
@forecast.callback([Output('countdown', 'data'),
                    Output('countdown', 'columns')],
                    [Input('sector', 'data'),
                    Input('store_submit_button', 'data')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data')])
def output_flagcount(sector_val, submit_button, curryr, currqtr, fileyr, success_init):
   
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        # Produce the countdown dataframe to show the number of flags left to clear
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        r = re.compile("^._flag*")
        flag_cols = list(filter(r.match, data.columns))
        countdown = data.copy()
        countdown = data[(data['yr'] >= curryr) & (data['qtr'] == 5)]
        countdown = countdown[['forecast_tag', 'identity_us', 'flag_skip'] + flag_cols]
        countdown = live_flag_count(countdown, sector_val)
        print("End Flag Countdown")
        return countdown.to_dict('rows'), [{'name': ['Flags Remaining', countdown.columns[i]], 'id': countdown.columns[i]} 
                    for i in range(0, len(countdown.columns))]

@forecast.callback([Output('droproll', 'value'),
                    Output('roll_trigger', 'data')],
                    [Input('store_submit_button', 'data'),
                    Input('sector', 'data'),
                    Input('dropman', 'value')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('identity_val', 'data'),
                    State('init_trigger', 'data')])
def set_rolldrop(submit_button, sector_val, man_val, curryr, currqtr, fileyr, identity_val, success_init):
    input_id = get_input_id()
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)

        # When all flags are cleared, man_val will get set to false, so change it to the first sub by default
        if man_val == False:
            man_val = data['metcode'].iloc[0] + str(data['subid'].iloc[0]) + data['subsector'].iloc[0]
        
        # Set the rollup data set to display the default based on the input id, unless the user actively selected something
        # Set to the US as default if this is first load, otherwise if the input button is submit or preview, set it to the met/sect that was edited/previewed, if the input button is skip, set it to the next met/sect that is flagged
        if input_id == 'sector':
            roll_val = "US" + list(data['subsector'].unique())[0]
        elif input_id == "store_submit_button-button" or input_id == "dropman":
            if sector_val == "ind":
                if man_val[-1:] == "F":
                    roll_val= man_val[:2] + man_val[-1:]
                else:
                    roll_val= man_val[:2] + man_val[-2:]
            else:
                roll_val = man_val[:2] + man_val[-3:]
        
        print("End Set Roll Drop")
        
        return roll_val, True

@forecast.callback([Output('vac_series_met', 'figure'),
                    Output('rent_series_met', 'figure'),
                    Output('vac_series_met', 'style'),
                    Output('rent_series_met', 'style'),
                    Output('metroll', 'data'),
                    Output('metroll', 'columns'),
                    Output('metroll', 'style_data_conditional'),
                    Output('met_rank', 'data'),
                    Output('met_rank', 'columns'),
                    Output('sub_rank', 'data'),
                    Output('sub_rank', 'columns'),
                    Output('sub_rank_container', 'style'),
                    Output('met_rank_container', 'style'),
                    Output('rank_view_container', 'style'),
                    Output('metroll', 'page_action'),
                    Output('metroll', 'style_table'),
                    Output('metroll', 'fixed_rows'),
                    Output('roll_view', 'disabled')],
                   [Input('droproll', 'value'),
                    Input('dropman', 'value'),
                    Input('roll_trigger', 'data'),
                    Input('store_submit_button', 'data'),
                    Input('store_preview_button', 'data'),
                    Input('roll_view', 'value'),
                    Input('rank_view', 'value')],
                    [State('store_orig_cols', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('sector', 'data'),
                    State('init_trigger', 'data')])
def output_rollup(roll_val, man_val, roll_trigger, submit_button, preview_button, multi_view, year_val, orig_cols, curryr, currqtr, fileyr, sector_val, success_init):
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        preview_data = use_pickle("in", "preview_data_" + sector_val, False, fileyr, currqtr, sector_val)

        dash_curryr = str(curryr)
        dash_second_five = curryr + 5
        dash_second_five = str(dash_second_five)

        # If the user is previewing a fix, set the rollup data set used in the rollup function to reflect the previewed edits so the user can see their effect on the met and nat levels
        # Otherwise, the rollup data set can just be a copy of the current edited dataset
        if len(preview_data) > 0:
            data_temp = data.copy()
            filt_cols = orig_cols + ['identity', 'forecast_tag', 'identity_met', 'identity_us', 'rolsinv']
            data_temp = data_temp[filt_cols]
            preview_data_temp = preview_data.copy()
            preview_data_temp = preview_data_temp[filt_cols]
            data_temp = data_temp[(data_temp['identity'] != man_val) | (data_temp['forecast_tag'] == 0)]
            preview_data_temp = preview_data_temp[(preview_data_temp['identity'] == man_val) & (preview_data_temp['forecast_tag'] != 0)]
            data_temp = data_temp.append(preview_data_temp)
            data_temp.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace=True)
            roll = data_temp.copy()
        else:
            roll = data.copy()
        
        # Call the rollup function to set the rollup data set, as well as the relevant vacancy and rent time series charts for the rollup tab
        if multi_view == False or roll_val[:2] == "US":
            rolled = roll.copy()
            if roll_val[:2] == "US":
                rolled = rolled[(rolled['identity_us'] == roll_val)]
            else:
                rolled = rolled[(rolled['metcode'] == roll_val[:2]) & (rolled['subsector'] == roll_val[2:])]
            rolled = rollup(rolled, roll_val, curryr, currqtr, sector_val, "reg", False)   
        elif multi_view == True:
            roll_combined = pd.DataFrame()
            all_subs = roll.copy()
            all_subs = all_subs[all_subs['identity_met'] == roll_val]
            all_subs = all_subs.drop_duplicates('identity')
            all_subs = list(all_subs['identity'])
            for ident in all_subs:
                roll_temp = rollup(roll, ident, curryr, currqtr, sector_val, "list", False)
                roll_temp = roll_temp[roll_temp['yr'] >= curryr - 1]
                if len(roll_combined) == 0:
                    roll_combined = roll_temp
                else:
                    roll_combined = roll_combined.append(roll_temp)
            rolled = roll_combined.copy()

            rolled_rank = rollup(roll, roll_val, curryr, currqtr, sector_val, "reg", False)

        if roll_val[:2] == "US":
            data_vac_roll, data_rent_roll = sub_met_graphs(rolled, "nat", curryr, currqtr, fileyr, sector_val)
        else:
            if multi_view == False:
                data_vac_roll, data_rent_roll = sub_met_graphs(rolled, "met", curryr, currqtr, fileyr, sector_val)
            elif multi_view == True:
                sub_rank, met_rank = rank_it(rolled_rank, roll, roll_val, curryr, currqtr, sector_val, year_val)
                rolled = rolled[(rolled['metcode'] == roll_val[:2]) & (rolled['subsector'] == roll_val[2:])]

                for x in list(sub_rank.columns):
                    sub_rank.rename(columns={x: x.replace('_', ' ')}, inplace=True)
                for x in list(met_rank.columns):
                    met_rank.rename(columns={x: x.replace('_', ' ')}, inplace=True)
                sub_rank = sub_rank.rename(columns={'G mrent': 'Gmrent', 'imp G mrent': 'imp Gmrent'})
                met_rank = met_rank.rename(columns={'G mrent': 'Gmrent', 'imp G mrent': 'imp Gmrent'})
                
                type_dict_rank = {}
                format_dict_rank = {}
                for x in list(sub_rank.columns):
                    type_dict_rank[x] = 'numeric'
                    format_dict_rank[x] =  Format(precision=0, scheme=Scheme.fixed)

        rolled = rolled.drop(['cons_oob', 'vac_oob', 'vac_chg_oob',  'askrentoob', 'ask_chg_oob', 'rolaskrent'], axis=1)
        rolled = rolled.rename(columns={'rolscon': 'rol cons', 'rolsvac': 'rol vac', 'vac_chg': 'vac chg', 'rolsvac_chg': 'rol vac chg', 'rolsabs': 'rol abs', 'askrent': 'ask rent', 'ask_chg': 'ask chg', 'rol_ask_chg': 'rol ask chg', 'effrent': 'eff rent', 'eff_chg': 'eff chg', 'rol_eff_chg': 'rol eff chg', 'gap_chg': 'gap chg'})
        type_dict_roll, format_dict_roll = get_types(rolled, sector_val)
        highlighting_roll = get_style("full", rolled, dash_curryr, dash_second_five)

        if sector_val == "ind":
            if roll_val[0:2] == "US":
                if roll_val[2] == "F":
                    data_title = roll_val[:2] + " "  + roll_val[2] + " " + roll_val[3:] + " National Data"
                else:
                    data_title = roll_val[:2] + " "  + roll_val[2:4] + " " + roll_val[4:] + " National Data"
            else:
                data_title = roll_val[:2] + " "  + roll_val[2:] + " Metro Data"
        else:
            if roll_val[0:2] == "US":
                data_title = roll_val[:2] + " Tier " + roll_val[2:] + " National Data"
            else:
                data_title = roll_val[:2] + " Metro Data"

        if currqtr == 1:
            height = '810px'
        elif currqtr == 2:
            height = '840px'
        elif currqtr == 3:
            height = '870px'
        elif currqtr == 4:
            height = '690px'
        
        if len(rolled) > 28 and multi_view == True:
            style_it = {'height': height, 'overflowY': 'auto', 'overflowX': 'hidden'}
            fixed_rows = {'headers': True}
        elif multi_view == True:
            style_it = {'height': height, 'overflowY': 'hidden', 'overflowX': 'hidden'}
            fixed_rows = {}

        if roll_val[:2] == "US":
            disable_roll_view = True
            rolled = rolled.drop(['identity_us'], axis=1)
        else:
            disable_roll_view = False
        
        print("End Output Rollup")
        if multi_view == False or roll_val[:2] == "US":
            return go.Figure(data=data_vac_roll), go.Figure(data=data_rent_roll), {'width': '100%', 'display': 'inline-block'}, {'width': '100%', 'display': 'inline-block', 'padding-left': '50px'}, rolled.to_dict('rows'), [{'name': [data_title, rolled.columns[i]], 'id': rolled.columns[i], 'type': type_dict_roll[rolled.columns[i]], 'format': format_dict_roll[rolled.columns[i]]} 
            for i in range(0, len(rolled.columns))], highlighting_roll, no_update, no_update, no_update, no_update, {'display': 'none'}, {'display': 'none'}, {'display': 'none'}, 'none', {}, {}, disable_roll_view
        elif multi_view == True:
            return no_update, no_update, {'display': 'none'}, {'display': 'none'}, rolled.to_dict('rows'), [{'name': [data_title, rolled.columns[i]], 'id': rolled.columns[i], 'type': type_dict_roll[rolled.columns[i]], 'format': format_dict_roll[rolled.columns[i]]} 
            for i in range(0, len(rolled.columns))], highlighting_roll, met_rank.to_dict('rows'), [{'name': ['Met Rank', met_rank.columns[i]], 'id': met_rank.columns[i], 'type': type_dict_rank[met_rank.columns[i]], 'format': format_dict_rank[met_rank.columns[i]]} 
                            for i in range(0, len(met_rank.columns))], sub_rank.to_dict('rows'), [{'name': ['Sub Rank', sub_rank.columns[i]], 'id': sub_rank.columns[i], 'type': type_dict_rank[sub_rank.columns[i]], 'format': format_dict_rank[sub_rank.columns[i]]} 
                            for i in range(0, len(sub_rank.columns))], {'display': 'inline-block', 'padding-left': '100px', 'width': '45%'}, {'display': 'inline-block', 'padding-left': '250px', 'width': '45%'}, {'display': 'block', 'padding-left': '850px'}, 'none', style_it, fixed_rows, disable_roll_view

@forecast.callback(Output('store_shim_finals', 'data'),
                  [Input('man_edits', 'data'),
                  Input('sector', 'data')],
                  [State('curryr', 'data'),
                  State('currqtr', 'data'),
                  State('fileyr', 'data'),
                  State('init_trigger', 'data'),
                  State('dropman', 'value')])
def finalize_shims(shim_data, sector_val, curryr, currqtr, fileyr, success_init, drop_val):
    
    if shim_data is None or success_init == False:
        raise PreventUpdate
    else:
        shims_final = pd.DataFrame()
        for x in shim_data:
            x['identity_row'] = drop_val + str(x['yr']) + str(x['qtr'])
            shims_final = shims_final.append(x, ignore_index=True)
        shims_final = shims_final.set_index('identity_row')
        use_pickle("out", "shim_data_" + sector_val, shims_final, fileyr, currqtr, sector_val)
        print("End Finalize Shims")
        return False
        
@forecast.callback([Output('scatter_xaxis_var', 'options'),
                    Output('scatter_yaxis_var', 'options'),
                    Output('scatter_xaxis_var', 'disabled'),
                    Output('scatter_xaxis_var', 'placeholder'),
                    Output('scatter_xaxis_var', 'value'),
                    Output('scatter_yaxis_var', 'value')],
                    [Input('scatter_year_radios', 'value'),
                    Input('scatter_comparison_radios', 'value'),
                    Input('sector', 'data')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data'),
                    State('scatter_xaxis_var', 'value'),
                    State('scatter_yaxis_var', 'value')])
def set_scatter_drops(year_value, comp_value, sector_val, curryr, currqtr, fileyr, success_init, init_xaxis_var, init_yaxis_var):

    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        input_id = get_input_id()
        if comp_value == 'c':
            lock = False
            placeholder = "Select:"
            x_var = init_xaxis_var
            if "rol" in init_yaxis_var:
                if init_xaxis_var != "G_mrent":
                    y_var = 'G_mrent'
                else:
                    y_var = "vac_chg"
            else:
                y_var = init_yaxis_var
            if sector_val == "apt" or sector_val == "ret":
                x_options_list = ['cons', 'vac_chg', 'G_mrent', 'gap_chg', 'emp_chg', 'avg_inc_chg']         
            elif sector_val == "off":
                x_options_list = ['cons', 'vac_chg', 'G_mrent', 'gap_chg', 'off_emp_chg', 'avg_inc_chg']
            elif sector_val == "ind":
                x_options_list = ['cons', 'vac_chg', 'G_mrent', 'gap_chg', 'ind_emp_chg', 'avg_inc_chg']
                
            if year_value == curryr and currqtr != 4:
                imp_options_list = ['implied_cons', 'implied_vac_chg', 'implied_G_mrent', 'implied_gap_chg']
                if sector_val == "apt" or sector_val == "ret":
                    imp_options_list += ['implied_emp_chg', 'implied_avg_inc_chg']
                elif sector_val == "off":
                    imp_options_list += ['implied_off_emp_chg', 'implied_avg_inc_chg']
                elif sector_val == "ind":
                    imp_options_list += ['implied_ind_emp_chg', 'implied_avg_inc_chg']
                x_options_list = imp_options_list + x_options_list

            y_options_list = x_options_list

        elif comp_value == "r":
            lock = True
            placeholder = "Determined by ROL Variable"

            x_options_list = []
            if sector_val == "apt" or sector_val == "ret":
                y_options_list = ['rolscon', 'rolsvac_chg', 'grolsmre', 'rolsgap_chg', 'rol_emp_chg']         
            elif sector_val == "off":
                y_options_list = ['rolscon', 'rolsvac_chg', 'grolsmre', 'rolsgap_chg', 'rol_off_emp_chg'] 
            elif sector_val == "ind":
                y_options_list = ['rolscon', 'rolsvac_chg', 'grolsmre', 'rolsgap_chg', 'rol_ind_emp_chg'] 
            
            if sector_val == "apt" or sector_val == "ret":
                rol_emp_use = 'rol_emp_chg'  
            elif sector_val == "off":
                rol_emp_use = 'rol_off_emp_chg'
            elif sector_val == "ind":
                rol_emp_use = 'rol_ind_emp_chg'

            match_list = {'cons': 'rolscon', 'vac_chg': 'rolsvac_chg', 'G_mrent': 'grolsmre', 'gap_chg': 'rolsgap_chg', 'emp_chg': 'rol_emp_chg', 'off_emp_chg': 'rol_off_emp_chg', 'ind_emp_chg': 'rol_ind_emp_chg', 'avg_inc_chg': rol_emp_use, 'implied_avg_inc_chg': rol_emp_use, 'implied_emp_chg': rol_emp_use, 'implied_off_emp_chg': rol_emp_use, 'implied_ind_emp_chg': rol_emp_use}
            y_var = match_list[init_xaxis_var]
            x_var = init_xaxis_var
        
        x_options_list = sorted(x_options_list, key=lambda v: v.upper())
        y_options_list = sorted(y_options_list, key=lambda v: v.upper())


        print("End Set Scatter Drops")
        return [{'label': i, 'value': i} for i in x_options_list], [{'label': i, 'value': i} for i in y_options_list], lock, placeholder, x_var, y_var

@forecast.callback([Output('scatter_graph', 'figure'),
                    Output('store_scatter_check', 'data'),
                    Output('scatter_graph', 'hoverData')],
                    [Input('scatter_xaxis_var', 'value'),
                    Input('scatter_yaxis_var', 'value'),
                    Input('scatter_year_radios', 'value'),
                    Input('scatter_comparison_radios', 'value'),
                    Input('flags_only', 'value'),
                    Input('sector', 'data'),
                    Input('store_submit_button', 'data')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data')])
def produce_scatter_graph(xaxis_column_name, yaxis_column_name, year_value, comp_value, flags_only, sector_val, submit_button, curryr, currqtr, fileyr, success_init):

    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:

        graph_data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)

        if comp_value == "r":
            match_list = {'rolscon': 'cons', 'rolsvac_chg': 'vac_chg', 'grolsmre': 'G_mrent', 'rolsgap_chg': 'gap_chg', 'rol-emp_chg': 'emp_chg', 'rol_off_emp_chg': 'off_emp_chg', 'rol_ind_emp_chg': 'ind_emp_chg'}
            xaxis_column_name = match_list[yaxis_column_name]

        if year_value != curryr and "implied" in xaxis_column_name:
            xaxis_column_name = xaxis_column_name[8:]
        if year_value != curryr and "implied" in yaxis_column_name:
            yaxis_column_name = yaxis_column_name[8:]
        
        # Tag subs as flagged or not flagged based on the xaxis var (or the yaxis var if the x is employment) for color purposes on scatter plot
        r = re.compile("^._flag*")
        flag_cols = list(filter(r.match, graph_data.columns))
        graph_data[flag_cols] = np.where((graph_data[flag_cols] != 0) & (graph_data[flag_cols] != 999999999), 1, graph_data[flag_cols])
        graph_data[flag_cols] = np.where((graph_data[flag_cols] == 999999999), 0, graph_data[flag_cols])

        def sum_flags(dataframe_in, flag_list, year_value):
            dataframe = dataframe_in.copy()
            dataframe['tot_flags'] = 0
            for flag_name in flag_list:
                dataframe['tot_flags'] += dataframe[(dataframe['yr'] == year_value) & (dataframe['qtr'] == 5)].groupby('identity')[flag_name].transform('sum')

            return dataframe


        if comp_value == "c":
            if xaxis_column_name in ['cons', 'implied_cons']:
                graph_data['c_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^c_flag*").sum(axis=1)
                graph_data['flagged_status'] = np.where(graph_data['c_flag_tot'] > 0, 1, 0)
                graph_data = graph_data.drop(['c_flag_tot'], axis=1) 
            elif xaxis_column_name in ['vac_chg', 'implied_vac_chg']:
                graph_data['v_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^v_flag*").sum(axis=1)
                graph_data['flagged_status'] = np.where(graph_data['v_flag_tot'] > 0, 1, 0)
                graph_data = graph_data.drop(['v_flag_tot'], axis=1)
            elif xaxis_column_name in ['G_mrent', 'implied_G_mrent']:
                graph_data['g_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^g_flag*").sum(axis=1)
                graph_data['flagged_status'] = np.where(graph_data['g_flag_tot'] > 0, 1, 0)
                graph_data = graph_data.drop(['g_flag_tot'], axis=1)
            elif xaxis_column_name in ['gap_chg', 'implied_gap_chg']:
                graph_data['e_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^e_flag*").sum(axis=1)
                graph_data['flagged_status'] = np.where(graph_data['e_flag_tot'] > 0, 1, 0)
                graph_data = graph_data.drop(['e_flag_tot'], axis=1)
            elif xaxis_column_name in ['emp_chg', 'off_emp_chg', 'ind_emp_chg', 'avg_inc_chg', 'implied_emp_chg', 'implied_off_emp_chg', 'implied_ind_emp_chg', 'implied_avg_inc_chg']:
                if yaxis_column_name in ['vac_chg', 'implied_vac_chg']:
                    graph_data = sum_flags(graph_data, ['v_flag_emp'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                elif yaxis_column_name in ['G_mrent', 'implied_G_mrent']:
                    graph_data = sum_flags(graph_data, ['g_flag_emp'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                elif yaxis_column_name in ["gap_chg", "implied_gap_chg"]:
                    graph_data= sum_flags(graph_data, ['e_flag_emp'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                else:
                    graph_data = sum_flags(graph_data, ['v_flag_emp', 'g_flag_emp', 'e_flag_emp'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
        
        elif comp_value == "r":
            if xaxis_column_name in ['cons', 'implied_cons']:
                graph_data = sum_flags(graph_data, ['c_flag_rol'], year_value)
                graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                graph_data = graph_data.drop(['tot_flags'], axis=1)
            elif xaxis_column_name in ['vac_chg', 'implied_vac_chg']:
                graph_data = sum_flags(graph_data, ['v_flag_rol', 'v_flag_improls', 'v_flag_switch'], year_value)
                graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                graph_data = graph_data.drop(['tot_flags'], axis=1)
            elif xaxis_column_name in ['G_mrent', 'implied_G_mrent']:
                graph_data = sum_flags(graph_data, ['g_flag_rol', 'g_flag_improls'], year_value)
                graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                graph_data = graph_data.drop(['tot_flags'], axis=1)
            elif xaxis_column_name in ['gap_chg', 'implied_gap_chg']:
                graph_data = sum_flags(graph_data, ['e_flag_rol', 'e_flag_improls', 'e_flag_rolvac'], year_value)
                graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                graph_data = graph_data.drop(['tot_flags'], axis=1)
            else:
                graph_data = sum_flags(graph_data, ['c_flag_rol', 'v_flag_rol', 'v_flag_improls', 'v_flag_switch', 'g_flag_rol', 'g_flag_improls', 'e_flag_rol', 'e_flag_improls', 'e_flag_rolvac'], year_value)
                graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                graph_data = graph_data.drop(['tot_flags'], axis=1)

        scatter_graph, for_time_series, init_hover = filter_graph(graph_data, curryr, currqtr, year_value, xaxis_column_name, yaxis_column_name, sector_val, comp_value, flags_only)

        use_pickle("out", "ts_data_" + sector_val, for_time_series, fileyr, currqtr, sector_val)
        
        scatter_layout = create_scatter_plot(scatter_graph, xaxis_column_name, yaxis_column_name, comp_value)

        #Need to set this variable so that the succeeding callbacks will only fire once the intial load is done. 
        # This works because it makes the callbacks that use elements produced in this callback have an input that is linked to an output of this callback, ensuring that they will only be fired once this one completes
        scatter_check = True
        print("End Produce Scatter")
        return scatter_layout, scatter_check, init_hover

@forecast.callback([Output('x_time_series', 'figure'),
                   Output('y_time_series', 'figure')],
                   [Input('scatter_graph', 'hoverData'),
                   Input('scatter_xaxis_var', 'value'),
                   Input('scatter_yaxis_var', 'value'),
                   Input('sector', 'data'),
                   Input('store_scatter_check', 'data'),
                   Input('init_trigger', 'data')],
                   [State('curryr', 'data'),
                   State('currqtr', 'data'),
                   State('fileyr', 'data'),
                   State('init_trigger', 'data'),
                   State('scatter_comparison_radios', 'value')])
def produce_timeseries(hoverData, xaxis_var, yaxis_var, sector_val, scatter_check, init_trigger, curryr, currqtr, fileyr, success_init, comp_value):
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        
        graph = use_pickle("in", "ts_data_" + sector_val, False, fileyr, currqtr, sector_val)

        if comp_value == "r":
            match_list = {'rolscon': 'cons', 'rolsvac_chg': 'vac_chg', 'grolsmre': 'G_mrent', 'rolsgap_chg': 'gap_chg', 'rol-emp_chg': 'emp_chg', 'rol_off_emp_chg': 'off_emp_chg', 'rol_ind_emp_chg': 'ind_emp_chg'}
            xaxis_var = match_list[yaxis_var]
        
        # Filter out the correct metsub based on the point the user is hovering over
        graph = graph[graph['index'] == hoverData['points'][0]['customdata']]

        identity = hoverData['points'][0]['customdata']
        if sector_val != "ind":
            identity = identity[:-3]

        # "Unmelt" to get just cons and inv vars, for use in setting the bar graph scaling
        temp_1 = graph.copy()
        temp_1 = temp_1[(temp_1['variable'] == "inv")]
        temp_1 = temp_1[['yr', 'value']]
        temp_1 = temp_1.rename(columns={'value': 'inv'})
        temp_1 = temp_1.set_index('yr')
        temp_2 = graph.copy()
        temp_2 = temp_2[(temp_2['variable'] == "cons")]
        temp_2 = temp_2[['yr', 'value']]
        temp_2 = temp_2.rename(columns={'value': 'cons'})
        temp_2 = temp_2.set_index('yr')
        temp_1 = temp_1.join(temp_2, on='yr')
        if comp_value == "r":
            temp_3 = graph.copy()
            temp_3 = temp_3[(temp_3['variable'] == "rolscon")]
            temp_3 = temp_3[['yr', 'value']]
            temp_3 = temp_3.rename(columns={'value': 'rolscon'})
            temp_3 = temp_3.set_index('yr')
            temp_1 = temp_1.join(temp_3, on='yr')
        for_bar_scale = temp_1.copy()
        
        # Call the function that will return the relevant data points for the two time series graphs
        x_trend_level, x_forecast_level, x_trend_chg, x_forecast_chg, x_connector, x_y_tick_range, x_dtick, x_tick_0 = split_trend_forecast(graph, xaxis_var, curryr, currqtr, sector_val)
        y_trend_level, y_forecast_level, y_trend_chg, y_forecast_chg, y_connector, y_y_tick_range, y_dtick, y_tick_0 = split_trend_forecast(graph, yaxis_var, curryr, currqtr, sector_val)

        if xaxis_var != "cons" and xaxis_var != "implied_cons":
            x_trend_cons, x_forecast_cons, temp1, temp2, x_connector_cons, temp3, temp4, temp5 = split_trend_forecast(graph, "cons", curryr, currqtr, sector_val)
            x_cons_range_list, x_bar_dtick = set_bar_scale(for_bar_scale, sector_val, ['cons'], ['inv'])
            if currqtr != 4:
                x_connector_cons_1 = x_connector_cons[0]
                x_connector_cons_2 = x_connector_cons[1] - x_connector_cons[0]
            elif currqtr == 4:
                x_connector_cons_1 = False
                x_connector_cons_2 = False
     
        if yaxis_var != "cons" and yaxis_var != "implied_cons" and yaxis_var != "rolscon":
            if comp_value == "c":
                cons_use = 'cons'
                inv_use = 'inv'
            elif comp_value == "r":
                cons_use = 'rolscon'
                inv_use = 'rolsinv'
            y_trend_cons, y_forecast_cons, temp1, temp2, y_connector_cons, temp3, temp4, temp5 = split_trend_forecast(graph, cons_use, curryr, currqtr, sector_val)
            y_cons_range_list, y_bar_dtick = set_bar_scale(for_bar_scale, sector_val, [cons_use], [inv_use])
            if currqtr != 4:
                if comp_value == "c" or currqtr > 1:
                    y_connector_cons_1 = y_connector_cons[0]
                    y_connector_cons_2 = y_connector_cons[1] - y_connector_cons[0]
                elif comp_value == "r" and currqtr == 1:
                    y_connector_cons_1 = False
                    y_connector_cons_2 = False
            elif currqtr == 4:
                y_connector_cons_1 = False
                y_connector_cons_2 = False
       
        if xaxis_var == "cons" or xaxis_var == "implied_cons":
            if currqtr != 4:
                x_connector_1 = x_connector[0]
                x_connector_2 = x_connector[1] - x_connector[0]
            elif currqtr == 4:
                x_connector_1 = []
                x_connector_2 = []
            x_cons_range_list, x_bar_dtick = set_bar_scale(for_bar_scale, sector_val, ['cons'], ['inv'])
        
        if yaxis_var == "cons" or yaxis_var == "implied_cons" or yaxis_var == "rolscon":
            if comp_value == "c":
                cons_use = 'cons'
                inv_use = 'inv'
                if currqtr != 4:
                    y_connector_1 = y_connector[0]
                    y_connector_2 = y_connector[1] - y_connector[0]
                elif currqtr == 4:
                    y_connector_1 = []
                    y_connector_2 = []
            elif comp_value == "r":
                cons_use = 'rolscon'
                inv_use = 'rolsinv'
                if currqtr == 2 or currqtr == 3:
                    y_connector_1 = y_connector[0]
                    y_connector_2 = y_connector[1] - y_connector[0]
                elif currqtr == 1 or currqtr == 4:
                    y_connector_1 = []
                    y_connector_2 = []
            y_cons_range_list, y_bar_dtick = set_bar_scale(for_bar_scale, sector_val, [cons_use], [inv_use]) 
    
        if xaxis_var == "cons" or xaxis_var == "implied_cons":
            x_format_choice = '%{text:,}<extra></extra>'
        else:
            x_format_choice = '%{text:.02%}<extra></extra>'
        if yaxis_var == "cons" or yaxis_var == "implied_cons" or yaxis_var == "rolscon":
            y_format_choice = '%{text:,}<extra></extra>'
        else:
           y_format_choice = '%{text:.02%}<extra></extra>'

        fig_x = go.Figure()
        fig_y = go.Figure()
        
        if currqtr != 4:
            if xaxis_var == "cons" or xaxis_var == "implied_cons":
                fig_x = set_ts_bar(fig_x, x_trend_level[:-1], x_forecast_level[1:], x_trend_chg[:-1], x_forecast_chg[1:], x_connector_1, x_connector_2, x_format_choice, curryr, currqtr, comp_value)
            else:
                fig_x = set_ts_scatter(fig_x, x_trend_cons[:-1], x_forecast_cons[1:], x_connector_cons_1, x_connector_cons_2, x_trend_level, x_forecast_level, x_trend_chg, x_forecast_chg, x_connector, x_format_choice, curryr, currqtr, comp_value)
            if yaxis_var == "cons" or yaxis_var == "implied_cons" or yaxis_var == "rolscon":
                if currqtr == 1 and comp_value == "r":
                    fig_y = set_ts_bar(fig_y, y_trend_level, y_forecast_level, y_trend_chg, y_forecast_chg, y_connector_1, y_connector_2, y_format_choice, curryr, currqtr, comp_value)
                else:
                    fig_y = set_ts_bar(fig_y, y_trend_level[:-1], y_forecast_level[1:], y_trend_chg[:-1], y_forecast_chg[1:], y_connector_1, y_connector_2, y_format_choice, curryr, currqtr, comp_value)
            else:
                if currqtr == 1 and comp_value == "r":
                    fig_y = set_ts_scatter(fig_y, y_trend_cons, y_forecast_cons, y_connector_cons_1, y_connector_cons_2, y_trend_level, y_forecast_level, y_trend_chg, y_forecast_chg, y_connector, y_format_choice, curryr, currqtr, comp_value)
                else:
                    fig_y = set_ts_scatter(fig_y, y_trend_cons[:-1], y_forecast_cons[1:], y_connector_cons_1, y_connector_cons_2, y_trend_level, y_forecast_level, y_trend_chg, y_forecast_chg, y_connector, y_format_choice, curryr, currqtr, comp_value)
        elif currqtr == 4:
            if xaxis_var == "cons":
                fig_x = set_ts_bar(fig_x, x_trend_level, x_forecast_level, x_trend_chg, x_forecast_chg, x_connector_1, x_connector_2, x_format_choice, curryr, currqtr, comp_value)
            else:
                fig_x = set_ts_scatter(fig_x, x_trend_cons, x_forecast_cons, x_connector_cons_1, x_connector_cons_2, x_trend_level, x_forecast_level, x_trend_chg, x_forecast_chg, x_connector, x_format_choice, curryr, currqtr, comp_value)
            if yaxis_var == "cons" or yaxis_var == "rolscon":
                fig_y = set_ts_bar(fig_y, y_trend_level, y_forecast_level, y_trend_chg, y_forecast_chg, y_connector_1, y_connector_2, y_format_choice, curryr, currqtr, comp_value)
            else:
                fig_y = set_ts_scatter(fig_y, y_trend_cons, y_forecast_cons, y_connector_cons_1, y_connector_cons_2, y_trend_level, y_forecast_level, y_trend_chg, y_forecast_chg, y_connector, y_format_choice, curryr, currqtr, comp_value)
          
        
        if xaxis_var == "cons" or xaxis_var == "implied_cons":
            chart_type_x = "Bar"
        else:
            chart_type_x = "Scatter"
        if yaxis_var == "cons" or yaxis_var == "implied_cons" or yaxis_var == "rolscon":
            chart_type_y = "Bar"
        else:
            chart_type_y = "Scatter" 

        fig_x = set_ts_layout(fig_x, xaxis_var, identity, x_y_tick_range, x_dtick, x_tick_0, curryr, currqtr, chart_type_x, x_cons_range_list, x_bar_dtick, sector_val)
        fig_y = set_ts_layout(fig_y, yaxis_var, identity, y_y_tick_range, y_dtick, y_tick_0, curryr, currqtr, chart_type_y, y_cons_range_list, y_bar_dtick, sector_val)
    print("End Produce Time Series")
    return fig_x, fig_y

@forecast.callback(Output('home-url','pathname'),
                  [Input('logout-button','n_clicks')])
def logout_(n_clicks):
    '''clear the session and send user to login'''
    if n_clicks is None or n_clicks==0:
        return no_update
    session['authed'] = False
    return '/login'


server_check = os.getcwd()
    
if server_check[0:6] == "\\Odin":
    server = 0
else:
    server = 1


if __name__ == '__main__':
    
    if server == 1:
        test_ports = [8080, 8050, 8020, 8010, 8000]
        for x in test_ports:
            try:
                print("Trying port %d" % (x))
                forecast.run_server(port=x, host='0.0.0.0')
                break
            except:
                print("Port being used, trying another")
    elif server == 0:
        forecast.run_server(debug=True)