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
from flags_forecast import calc_flags
from support_functions_forecast import set_display_cols, display_frame, gen_metrics, rollup, live_flag_count, summarize_flags_ranking, summarize_flags, get_issue, get_diffs, metro_sorts, flag_examine
from support_functions_forecast import set_bar_scale, set_y2_scale, get_user_skips
from login_layout_forecast import get_login_layout
from forecast_app_layout import get_app_layout
from timer import Timer


# Function that determines the data type - int, float, etc - so that the correct format can be set for the app display
def get_types(sector_val):

    # In order for the comma seperator format to work, fields need to be set to float type. Put the conversion in a try and except, since some frames that come in this function wont have those fields
    try:
        dataframe[['inv', 'rolscon', 'rolsabs', 'rol_e']] = dataframe[['inv', 'rolscon', 'rolsabs', 'rol_e']].astype(float)
    except:
        False

    type_dict = {}
    format_dict = {}

    type_dict['subsector'] = 'text'
    type_dict['Subsector'] = 'text'
    type_dict['metcode'] = 'text'
    type_dict['Metcode'] = 'text'
    type_dict['Flag Type'] = 'text'


    type_dict['imp gap chg'] = 'numeric'
    type_dict['imp vac chg'] = 'numeric'
    type_dict['imp emp chg'] = 'numeric'
    type_dict['imp avginc chg'] = 'numeric'
    type_dict['avg inc chg'] = 'numeric'
    type_dict['emp chg'] = 'numeric'
    type_dict['emp chg z'] = 'numeric'
    type_dict['emp quart'] = 'numeric'
    type_dict['rol emp chg'] = 'numeric'
    type_dict['rol off emp chg'] = 'numeric'
    type_dict['off emp chg'] = 'numeric'
    type_dict['off emp quart'] = 'numeric'
    type_dict['rol ind emp chg'] = 'numeric'
    type_dict['ind emp chg'] = 'numeric'
    type_dict['imp indemp chg'] = 'numeric'
    type_dict['ind emp quart'] = 'numeric'
    type_dict['min gap'] = 'numeric'
    type_dict['min gap chg'] = 'numeric'
    type_dict['max gap'] = 'numeric'
    type_dict['max gap chg'] = 'numeric'
    type_dict['gap 5'] = 'numeric'
    type_dict['gap 95'] = 'numeric'
    type_dict['imp Gmerent'] = 'numeric'
    type_dict['gap quart'] = 'numeric'
    type_dict['vac chg sub var'] = 'numeric'
    type_dict['avg Gmrent'] = 'numeric'
    type_dict['Gmrent quart'] = 'numeric'
    type_dict['f var Gmrent'] = 'numeric'
    type_dict['f var gap chg'] = 'numeric'
    type_dict['Gmrent sub var'] = 'numeric'
    type_dict['f var cons'] = 'numeric'
    type_dict['imp cons'] = 'numeric'
    type_dict['avg vac chg'] = 'numeric'
    type_dict['vac z'] = 'numeric'
    type_dict['min vac'] = 'numeric'
    type_dict['max vac'] = 'numeric'
    type_dict['trendabs'] = 'numeric'
    type_dict['imp abs'] = 'numeric'
    type_dict['vac quart'] = 'numeric'
    type_dict['f var vacchg'] = 'numeric'
    type_dict['subid'] = 'numeric'
    type_dict['Subid'] = 'numeric'
    type_dict['inv'] = 'numeric'
    type_dict['avail'] = 'numeric'
    type_dict['yr'] = 'numeric'
    type_dict['qtr'] = 'numeric'
    type_dict['rol cons'] = 'numeric'
    type_dict['rol abs'] = 'numeric'
    type_dict['rol vac'] = 'numeric'
    type_dict['gap'] = 'numeric'
    type_dict['gap chg'] = 'numeric'
    type_dict['rol gap chg'] = 'numeric'
    type_dict['Total Flags'] = 'numeric'
    type_dict['% Fcast Rows W Flag'] = 'numeric'
    type_dict['% Subs W Flag'] = 'numeric'
    type_dict['3yr avgcons'] = 'numeric'
    type_dict['trendcons'] = 'numeric'
    type_dict['abs cons r'] = 'numeric'
    type_dict['abs nonc'] = 'numeric'
    type_dict['3yr avgabs'] = 'numeric'
    type_dict['3yr avgabs nonc'] = 'numeric'
    type_dict['imp abs rol'] = 'numeric'
    type_dict['histimp avgabs'] = 'numeric'
    type_dict['3yr avgGmrent'] = 'numeric'
    type_dict['3yr avgGmrent nonc'] = 'numeric'
    type_dict['imp Gmrent'] = 'numeric'
    type_dict['imp Gmrent rol'] = 'numeric'
    type_dict['sd vacchg'] = 'numeric'
    type_dict['sd Gmrent'] = 'numeric'
    type_dict['Gmrent nonc'] = 'numeric'
    type_dict['avg Gmrent nonc'] = 'numeric'
    type_dict['histimp Gmrent'] = 'numeric'
    type_dict['3yr avg empchg'] = 'numeric'
    type_dict['imp offemp chg'] = 'numeric'
    type_dict['imp emp chg'] = 'numeric'
    type_dict['vac chg'] =  'numeric'
    type_dict['rol vac chg'] =  'numeric'
    type_dict['avg abs cons'] = 'numeric'
    type_dict['10 yr vac'] = 'numeric'
    type_dict['occ'] = 'numeric'
    type_dict['p abs cons'] = 'numeric'
    type_dict['emp 5'] = 'numeric'
    type_dict['emp 95'] = 'numeric'
    type_dict['hist emp 10'] = 'numeric'
    type_dict['hist emp 90'] = 'numeric'
    type_dict['Gmrent'] = 'numeric'
    type_dict['Gmerent'] = 'numeric'
    type_dict['rol Gmrent'] = 'numeric'
    type_dict['rol Gmerent'] = 'numeric'
    type_dict['cons'] = 'numeric'
    type_dict['mrent'] = 'numeric'
    type_dict['merent'] = 'numeric'
    type_dict['vac'] = 'numeric'
    type_dict['abs'] = 'numeric'
    type_dict['Gmrent z'] = 'numeric'
    type_dict['cons prem'] = 'numeric'
    type_dict['min Gmrent'] = 'numeric'
    type_dict['max Gmrent'] = 'numeric'
    type_dict['h'] = 'numeric'
    type_dict['rol h'] = 'numeric'
    type_dict['rol e'] = 'numeric'
    type_dict['e'] = 'numeric'
    type_dict['t'] = 'numeric'
    type_dict['Cons Flags'] = 'numeric'
    type_dict['Vac Flags'] = 'numeric'
    type_dict['Rent Flags'] = 'numeric'
    type_dict['rol mrent'] = 'numeric'
    type_dict['rol merent'] = 'numeric'


    format_dict['emp 5'] = FormatTemplate.percentage(1)
    format_dict['emp 95'] = FormatTemplate.percentage(1)
    format_dict['hist emp 10'] = FormatTemplate.percentage(1)
    format_dict['hist emp 90'] = FormatTemplate.percentage(1)
    format_dict['emp chg'] = FormatTemplate.percentage(1)
    format_dict['rol emp chg'] = FormatTemplate.percentage(1)
    format_dict['3yr avg empchg'] = FormatTemplate.percentage(1)
    format_dict['ind emp chg'] = FormatTemplate.percentage(1)
    format_dict['rol ind emp chg'] = FormatTemplate.percentage(1)
    format_dict['off emp chg'] = FormatTemplate.percentage(1)
    format_dict['rol off emp chg'] = FormatTemplate.percentage(1)
    format_dict['imp emp chg'] = FormatTemplate.percentage(1)
    format_dict['imp indemp chg'] = FormatTemplate.percentage(1)
    format_dict['imp offemp chg'] = FormatTemplate.percentage(1)
    format_dict['% Fcast Rows W Flag'] = FormatTemplate.percentage(1)
    format_dict['% Subs W Flag'] = FormatTemplate.percentage(1)
    format_dict['cons prem'] = FormatTemplate.percentage(1)
    format_dict['avg inc chg'] = FormatTemplate.percentage(1)

    
    format_dict['vac'] = FormatTemplate.percentage(2)
    format_dict['rol vac'] = FormatTemplate.percentage(2)
    format_dict['vac chg'] = FormatTemplate.percentage(2)
    format_dict['rol vac chg'] = FormatTemplate.percentage(2)
    format_dict['imp vac chg'] = FormatTemplate.percentage(2)
    format_dict['gap'] = FormatTemplate.percentage(2)
    format_dict['gap chg'] = FormatTemplate.percentage(2)
    format_dict['rol gap chg'] = FormatTemplate.percentage(2)
    format_dict['imp gap chg'] = FormatTemplate.percentage(2)
    format_dict['3yr avgGmrent'] = FormatTemplate.percentage(2)
    format_dict['3yr avgGmrent nonc'] = FormatTemplate.percentage(2)
    format_dict['imp Gmrent'] = FormatTemplate.percentage(2)
    format_dict['imp Gmrent rol'] = FormatTemplate.percentage(2)
    format_dict['min vac'] = FormatTemplate.percentage(2)
    format_dict['max vac'] = FormatTemplate.percentage(2)
    format_dict['imp Gmerent'] = FormatTemplate.percentage(2)
    format_dict['sd vacchg'] = FormatTemplate.percentage(2)
    format_dict['sd Gmrent'] = FormatTemplate.percentage(2)
    format_dict['avg Gmrent'] = FormatTemplate.percentage(2)
    format_dict['Gmrent nonc'] = FormatTemplate.percentage(2)
    format_dict['avg Gmrent nonc'] = FormatTemplate.percentage(2)
    format_dict['histimp Gmrent'] = FormatTemplate.percentage(2)
    format_dict['f var vacchg'] = FormatTemplate.percentage(2)
    format_dict['avg vac chg'] = FormatTemplate.percentage(2)
    format_dict['imp avginc chg'] = FormatTemplate.percentage(2)
    format_dict['10 yr vac'] = FormatTemplate.percentage(2)
    format_dict['Gmrent'] = FormatTemplate.percentage(2)
    format_dict['Gmerent'] = FormatTemplate.percentage(2)
    format_dict['rol Gmrent'] = FormatTemplate.percentage(2)
    format_dict['rol Gmerent'] = FormatTemplate.percentage(2)
    format_dict['min Gmrent'] = FormatTemplate.percentage(2)
    format_dict['max Gmrent'] = FormatTemplate.percentage(2)
    format_dict['min gap'] = FormatTemplate.percentage(2)
    format_dict['min gap chg'] = FormatTemplate.percentage(2)
    format_dict['max gap'] = FormatTemplate.percentage(2)
    format_dict['max gap chg'] = FormatTemplate.percentage(2)
    format_dict['gap 5'] = FormatTemplate.percentage(2)
    format_dict['gap 95'] = FormatTemplate.percentage(2)
    format_dict['imp emp chg'] = FormatTemplate.percentage(2)

    
    format_dict['f var gap chg'] = FormatTemplate.percentage(3)
    format_dict['f var Gmrent'] = FormatTemplate.percentage(3)
    format_dict['Gmrent sub var'] = FormatTemplate.percentage(3)
    format_dict['vac chg sub var'] = FormatTemplate.percentage(3)
    

    format_dict['f var cons'] = Format(group=",")
    format_dict['3yr avgcons'] = Format(group=",")
    format_dict['trendcons'] = Format(group=",")
    format_dict['trendabs'] = Format(group=",")
    format_dict['3yr avgabs'] = Format(group=",")
    format_dict['imp abs'] = Format(group=",")
    format_dict['imp abs rol'] = Format(group=",")
    format_dict['histimp avgabs'] = Format(group=",")
    format_dict['p abs cons'] = Format(group=",")
    format_dict['imp cons'] = Format(group=",")
    format_dict['inv'] = Format(group=",")
    format_dict['cons'] = Format(group=",")
    format_dict['rol cons'] = Format(group=",")
    format_dict['abs'] = Format(group=",")
    format_dict['rol abs'] = Format(group=",")
    format_dict['abs nonc'] = Format(group=",")
    format_dict['avail'] = Format(group=",")
    format_dict['occ'] = Format(group=",")
    format_dict['h'] = Format(group=",")
    format_dict['rol h'] = Format(group=",")
    format_dict['rol e'] = Format(group=",")
    format_dict['e'] = Format(group=",")
    format_dict['t'] = Format(group=",")
    format_dict['3yr avgabs nonc'] = Format(group=",")

    
    format_dict['Flag Type'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Total Flags'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Cons Flags'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Vac Flags'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Rent Flags'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['subsector'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Subsector'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['metcode'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Metcode'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['yr'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['qtr'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['vac quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Gmrent quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['emp quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['ind emp quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['off emp quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['gap quart'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['subid'] = Format(precision=0, scheme=Scheme.fixed)
    format_dict['Subid'] = Format(precision=0, scheme=Scheme.fixed)

    
    format_dict['vac z'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['Gmrent z'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['emp chg z'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['abs cons r'] = Format(precision=1, scheme=Scheme.fixed)
    format_dict['avg abs cons'] = Format(precision=1, scheme=Scheme.fixed)

    format_dict['mrent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['merent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['rol mrent'] = Format(precision=2, scheme=Scheme.fixed)
    format_dict['rol merent'] = Format(precision=2, scheme=Scheme.fixed)

    return type_dict, format_dict

# Function that returns the highlighting style of the various dash datatables
def get_style(type_filt, dataframe_in, curryr, second_five, highlight_cols=[], highlight_rows=[]):
    dataframe = dataframe_in.copy()
    dataframe = dataframe.reset_index(drop=True)
    if type_filt == "full":
        style = [ 
                        {
                            'if': {'column_id': str(x), 'filter_query': '{{{0}}} < 0'.format(x)},
                            'color': 'red',
                        } for x in dataframe.columns
                
                    ] + [
                            
                        {
                            'if': {
                            'filter_query':   '{qtr} eq 5  && {yr} >' + curryr,
                                },
                    
                        'backgroundColor': 'lightblue'
                        },
                        {
                            'if': {
                            'filter_query': '{yr} >=' + second_five,
                                    },
                    
                        'backgroundColor': 'pink'
                        },
                        {
                            'if': {
                            'filter_query':  '{qtr} eq 5  && {yr} <' + curryr,
                                    },
                    
                        'backgroundColor': 'wheat'
                        },
                        {
                            'if': {
                            'filter_query':   '{qtr} eq 5  && {yr} =' + curryr,
                                },
                    
                        'backgroundColor': 'yellow'
                        },
                        ] + [
                        {
                            'if': {
                            'column_id': highlight_cols,
                            'row_index': highlight_rows,
                                },
                        'backgroundColor': 'LightGreen',
                    }
                    ]

    elif type_filt == "metrics":
        style = [ 
                        {
                            'if': {'column_id': str(x), 'filter_query': '{{{0}}} < 0'.format(x)},
                            'color': 'red',
                        } for x in dataframe.columns
                
                    ] + [
                        {
                            'if': {
                            'column_id': highlight_cols,
                                },
                        'backgroundColor': 'LightGreen',
                    }
                    ]
    
    elif type_filt == "partial":
        style = [ 
                    {
                        'if': {'column_id': str(x), 'filter_query': '{{{0}}} < 0'.format(x)},
                        'color': 'red',
                    } for x in dataframe.columns
                ]
    return style
    

def filter_graph(input_dataframe, curryr, currqtr, year_value, xaxis_var, yaxis_var, sector_val, comp_value, flags_only, aggreg_met, for_ts):
    dataframe = input_dataframe.copy()

    dataframe['vac_chg'] = round(dataframe['vac_chg'], 4)
    dataframe['G_mrent'] = round(dataframe['G_mrent'], 4)
    dataframe['avg_inc_chg'] = round(dataframe['avg_inc_chg'], 4)
    
    if currqtr != 4:
            dataframe = dataframe[((dataframe['yr'] >= curryr - 5) & (dataframe['yr'] < curryr) & (dataframe['qtr'] == 5)) | ((dataframe['yr'] == curryr) & (dataframe['qtr'] <= currqtr)) | ((dataframe['yr'] >= curryr) & (dataframe['qtr'] == 5))]
    elif currqtr == 4:
        dataframe = dataframe[(dataframe['yr'] >= curryr - 5) & (dataframe['qtr'] == 5)]

    scatter_graph_cols = ['subsector', 'metcode', 'subid', 'yr', 'qtr', 'inv', 'cons', 'vac', 'vac_chg', 'mrent', 'G_mrent', 'gap', 'gap_chg', 'avg_inc', 'avg_inc_chg']
    if aggreg_met == True:
        scatter_graph_cols.remove('subid')
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

    if for_ts == False:
        scatter_graph_cols += ['flagged_status']
    
    dataframe = dataframe[scatter_graph_cols]

    if for_ts == True:
        if aggreg_met == False:
            dataframe = pd.melt(dataframe, id_vars=['subsector', 'metcode', 'subid', 'yr', 'qtr'])
        elif aggreg_met == True:
            dataframe = pd.melt(dataframe, id_vars=['subsector', 'metcode', 'yr', 'qtr'])
        
        if aggreg_met == False:
            dataframe['index'] = dataframe['metcode'] + dataframe['subid'].astype(str) + dataframe['subsector']
        elif aggreg_met == True:
            dataframe['index'] = dataframe['metcode'] + dataframe['subsector']
        
        init_hover = False

    elif for_ts == False:
        if comp_value == "r":
            dataframe['diff_to_rol'] = np.where((dataframe['yr'] >= curryr) & (dataframe['qtr'] == 5), dataframe[xaxis_var] - dataframe[yaxis_var], np.nan)
            dataframe = dataframe[(abs(dataframe['diff_to_rol']) >= 0.001) | (dataframe['yr'] < curryr) | ((dataframe['qtr'] != 5) & (dataframe['yr'] == curryr))]
            get_first = dataframe.copy()
            get_first = get_first[(get_first['yr'] >= curryr) & (get_first['qtr'] == 5) & (abs(get_first['diff_to_rol']) >= 0.001)]
            if aggreg_met == False:
                first = get_first['metcode'].iloc[0] + get_first['subid'].iloc[0].astype(str) + get_first['subsector'].iloc[0]
            elif aggreg_met == True:
                first = get_first['metcode'].iloc[0] + get_first['subsector'].iloc[0]
            init_hover ={'points': [{'customdata': first}]}
        else:
            if aggreg_met == False:
                first = dataframe.reset_index().loc[0]['metcode'] + dataframe.reset_index().loc[0]['subid'].astype(str) + dataframe.reset_index().loc[0]['subsector']
            elif aggreg_met == True:
                first = dataframe.reset_index().loc[0]['metcode'] + dataframe.reset_index().loc[0]['subsector']
            init_hover ={'points': [{'customdata': first}]}

        if len(flags_only) > 0:
            if flags_only[0] == "f" and len(dataframe[dataframe['flagged_status'] == 1]) > 0:
                dataframe = dataframe[dataframe['flagged_status'] == 1]

        if aggreg_met == False:
            dataframe = pd.melt(dataframe, id_vars=['subsector', 'metcode', 'subid', 'yr', 'qtr'])
        elif aggreg_met == True:
            dataframe = pd.melt(dataframe, id_vars=['subsector', 'metcode', 'yr', 'qtr'])
        
        if aggreg_met == False:
            dataframe['index'] = dataframe['metcode'] + dataframe['subid'].astype(str) + dataframe['subsector']
        elif aggreg_met == True:
            dataframe['index'] = dataframe['metcode'] + dataframe['subsector']
        
        dataframe = dataframe[dataframe['variable'] != 'inv']

        dataframe = dataframe[dataframe['qtr'] == 5]
        
        if comp_value == "c":
            dataframe = dataframe[(dataframe['variable'] == xaxis_var) | (dataframe['variable'] == yaxis_var) | (dataframe['variable'] == 'flagged_status')]
        elif comp_value == "r":
            dataframe = dataframe[(dataframe['variable'] == xaxis_var) | (dataframe['variable'] == yaxis_var) | (dataframe['variable'] == "diff_to_rol") | (dataframe['variable'] == 'flagged_status')]
        
        dataframe = dataframe[dataframe['yr'] == year_value]

    return dataframe, init_hover

def create_scatter_plot(dataframe, xaxis_var, yaxis_var, comp_value, aggreg_met):

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
        if aggreg_met == False:
            x_axis_title = "Submarkets with Difference to Current"
        elif aggreg_met == True:
            x_axis_title = "Metros with Difference to Current"
        y_axis_title = "Curr Diff to ROL " + axis_titles[xaxis_var]

    if len(dataframe) > 0 and aggreg_met == False:
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
    else:
        color = 'blue'
        colorscale = []

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
        if "rol" in col_name_1:
            if col_name_1 == "rolscon" and currqtr == 1:
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

def sub_met_graphs(data, type_filt, curryr, currqtr, fileyr, sector_val):
    graph = data.copy()
    graph = graph[graph['qtr'] == 5]
    graph = graph[graph['yr'] >= curryr - 5]

    vac_range_list, vac_dtick, vac_tick_0 = set_y2_scale(graph, type_filt, "vac", sector_val)
    if type_filt == "sub":
        rent_range_list, rent_dtick, rent_tick_0 = set_y2_scale(graph, type_filt, "mrent", sector_val)
    else:
        rent_range_list, rent_dtick, rent_tick_0 = set_y2_scale(graph, type_filt, "mrent", sector_val)

    graph['cons_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['cons_oob'])
    graph['vac_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['vac_oob'])
    graph['vac_chg_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['vac_chg_oob'])
    graph['mrent_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['mrent_oob'])
    graph['G_mrent_oob'] = np.where((graph['yr'] < curryr), np.nan, graph['G_mrent_oob'])

    graph['cons_oob'] = np.where((graph['cons'] == graph['cons_oob']), np.nan, graph['cons_oob'])
    graph['vac_oob'] = np.where((graph['vac'] == graph['vac_oob']), np.nan, graph['vac_oob'])
    graph['mrent_oob'] = np.where((graph['mrent'] == graph['mrent_oob']), np.nan, graph['mrent_oob'])
    
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
        rent_tag_list = ['cons', 'rolscon', 'G_mrent', 'grolsmre', 'cons_oob', 'G_mrent_oob']
    else:
        vac_variable_list = ['cons', 'rolscon', 'vac', 'rolsvac', 'cons_oob', 'vac_oob']
        rent_variable_list = ['cons', 'rolscon', 'mrent', 'rol_mrent', 'cons_oob', 'mrent_oob']
        vac_tag_list = ['cons', 'rolscon', 'vac_chg', 'rolsvac_chg', 'cons_oob', 'vac_chg_oob']
        rent_tag_list = ['cons', 'rolscon', 'G_mrent', 'grolsmre', 'cons_oob', 'G_mrent_oob']
    
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
        if graph[(graph['variable'] == 'mrent_oob')]['value'].isnull().all() == True:
            rent_display_list.append(False)
        else:
            rent_display_list.append("legendonly")
    
    axis_list = ['y1', 'y1', 'y2', 'y2', 'y1', 'y2']

    if sector_val == "apt":
        rent_tick_format = '.0f'
    else:
        rent_tick_format = '.1f'

    for var, name, color, tag, axis, display, group in zip(vac_variable_list, vac_name_list, scatter_color_list, vac_tag_list, axis_list, vac_display_list, scatter_group_list):
        if "con" in var:
            fig_vac.add_trace(
            go.Bar(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == var]['value']),
                name = name,
                marker_color = color,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == tag]['value'])],
                yaxis=axis,
                visible= display,
                legendgroup = group,
                    )
                )
        else:
            fig_vac.add_trace(
            go.Scatter(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == var]['value']),
                name = name,
                marker_color = color,
                hovertemplate='%{x}, ' + '%{text:.2%}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == tag]['value'])],
                yaxis=axis,
                visible= display,
                legendgroup = group,
                    )
                )
    for var, name, color, tag, axis, display, group in zip(rent_variable_list, rent_name_list, scatter_color_list, rent_tag_list, axis_list, rent_display_list, scatter_group_list):
        if "con" in var:
            fig_rent.add_trace(
            go.Bar(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == var]['value']),
                name= name,
                marker_color = color,
                hovertemplate='%{x}, ' + '%{text:,}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == tag]['value'])],
                yaxis=axis,
                visible = display,
                legendgroup = group,
                    )
                ) 
        else:    
            fig_rent.add_trace(
            go.Scatter(
                x=list(graph['yr'].unique()),
                y=list(graph[graph['variable'] == var]['value']),
                name= name,
                marker_color = color,
                hovertemplate='%{x}, ' + '%{text:.2%}<extra></extra>',
                text = ['{}'.format(i) for i in list(graph[graph['variable'] == tag]['value'])],
                yaxis=axis,
                visible = display,
                legendgroup = group,
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
    elif "original_flags" in file_name:
        path_in = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), file_name))
        orig_flags = pd.read_pickle(path_in)
        path_out = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_original_flags.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
        orig_flags.reset_index().set_index('identity').to_csv(path_out, na_rep='')

    else:
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/intermediatefiles/{}.pickle".format(get_home(), file_name))
    
        if direction == "in":
            data = pd.read_pickle(file_path)
            return data
        elif direction == "out":
            dataframe.to_pickle(file_path)

def update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, action, flag_name, yr_val, cons_c, avail_c, rent_c):
    if action == "submit":
        
        decision_data_test = decision_data.copy()
        decision_data_test = decision_data_test[decision_data_test['identity'] == drop_val]
        
        drop_list = [x for x in list(decision_data_test.columns) if "new" in x]
        decision_data_test = decision_data_test.drop(drop_list, axis=1)
        
        rename_dict = {x : x[:-4] for x in list(decision_data_test.columns) if "oob" in x}
        decision_data_test = decision_data_test.rename(columns=rename_dict)

        update_data = data.copy()
        update_data = update_data[update_data['identity'] == drop_val]
        update_data = update_data[update_data['forecast_tag'] != 0]
        comments = update_data.copy()
        comments = comments[(comments['yr'] == curryr) & (comments['qtr'] == 5)]
        comments = comments[['cons_comment', 'avail_comment', 'rent_comment']]
        update_data = update_data[['identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr', 'cons', 'vac', 'abs', 'G_mrent', 'G_merent', 'gap', 'inv', 'avail', 'mrent', 'merent', 'vac_chg']]
        
        users = decision_data_test.copy()
        users = users[['c_user', 'v_user', 'g_user', 'e_user']]
        
        decision_data_test = decision_data_test.drop(['c_user', 'v_user', 'g_user', 'e_user', 'cons_comment', 'avail_comment',
                                                      'rent_comment', 'skipped', 'skip_user', 'occ'], axis=1)
        
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
        update_data[list(update_data.columns)] = update_data[list(update_data.columns)].fillna(9999999)
        decision_data_test[list(decision_data_test.columns)] = decision_data_test[list(decision_data_test.columns)].fillna(9999999)
        test = update_data.ne(decision_data_test)
        update_data = update_data[test].dropna(how='all')
        update_data = update_data.join(users)
        update_data = update_data.join(comments)

        # Because there are slight rounding differences, check if there is an actual change to the level var, null out chg vars
        for index, row in update_data.iterrows():
            if math.isnan(row['avail']) == True:
                update_data.loc[index, 'vac'] = np.nan 
                update_data.loc[index, 'vac_chg'] = np.nan 
                update_data.loc[index, 'abs'] = np.nan 
            if math.isnan(row['mrent']) == True:
                update_data.loc[index, 'G_mrent'] = np.nan 
            if math.isnan(row['merent']) == True:
                update_data.loc[index, 'G_merent'] = np.nan
            if  math.isnan(row['mrent']) == True and math.isnan(row['merent']) == True:
                update_data.loc[index, 'gap'] = np.nan

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
        
        # Replace the new values in the "new" columns in a trunc dataframe that also has the oob values
        decision_data_replace = decision_data.copy()
        decision_data_replace = decision_data_replace[decision_data_replace['identity'] == drop_val]
        replace_list = [x[:-4] for x in drop_list]
        update_data[replace_list] = update_data[replace_list].fillna(9999999)
        update_data[['c_user', 'v_user', 'g_user', 'e_user']] = update_data[['c_user', 'v_user', 'g_user', 'e_user']].fillna("temp")
        for x, y in zip(replace_list + ['c_user', 'v_user', 'g_user', 'e_user'], drop_list + ['c_user', 'v_user', 'g_user', 'e_user']):
            for index, row in update_data.iterrows():
                if x in ['c_user', 'v_user', 'g_user', 'e_user']:
                    if row[x] != "temp":
                        decision_data_replace.loc[index, y] = row[x]
                else:
                    if row[x] != 9999999:
                        decision_data_replace.loc[index, y] = row[x]

        # Append the updated decision for the "new" columns from the trunc dataframe we just created to the rest of the identities in the log, and output the updated log
        decision_data_update = decision_data.copy()
        decision_data_update = decision_data_update[decision_data_update['identity'] != drop_val]
        decision_data_update = decision_data_update.append(decision_data_replace)
        decision_data_update.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace = True)

        # Add comments to all rows
        decision_data_update = decision_data_update.reset_index().set_index('identity')
        if cons_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'cons_comment'] = cons_c
        if avail_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'avail_comment'] = avail_c
        if rent_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'rent_comment'] = rent_c
        decision_data_update = decision_data_update.reset_index().set_index('identity_row')
    
    elif action == "skip":
        decision_data_update = decision_data.copy()
        if decision_data_update['skipped'].loc[drop_val + str(curryr) + str(5)] == '':
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skipped'] = flag_name + str(yr_val)
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skip_user'] = user
        else:
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skipped'] = decision_data_update['skipped'].loc[drop_val + str(curryr) + str(5)] + ", " + flag_name + str(yr_val)
            decision_data_update.loc[drop_val + str(curryr) + str(5), 'skip_user'] = decision_data_update['skip_user'].loc[drop_val + str(curryr) + str(5)] + ", " + user

        # Add comments to all rows
        decision_data_update = decision_data_update.reset_index().set_index('identity')
        if cons_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'cons_comment'] = cons_c
        if avail_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'avail_comment'] = avail_c
        if rent_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'rent_comment'] = rent_c
        decision_data_update = decision_data_update.reset_index().set_index('identity_row')

    elif action == "comment":
        decision_data_update = decision_data.copy()
        decision_data_update = decision_data_update.reset_index().set_index('identity')
        if cons_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'cons_comment'] = cons_c
        if avail_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'avail_comment'] = avail_c
        if rent_c[-9:] != "Note Here":
            decision_data_update.loc[drop_val, 'rent_comment'] = rent_c
        decision_data_update = decision_data_update.reset_index().set_index('identity_row')
    
    return decision_data_update


# This function filters out submarkets flagged for a specific flag chosen by the user on the Home tab, and creates the necessary table and styles for display
def filter_flags(dataframe_in, drop_flag):

    flag_filt = dataframe_in.copy()

    flag_filt = flag_filt[[drop_flag, 'identity', 'flag_skip']]
    flag_filt = flag_filt[(flag_filt[drop_flag] > 0)]

    if len(flag_filt) > 0:
        has_skip = flag_filt['flag_skip'].str.contains(drop_flag, regex=False)
        flag_filt['has_skip'] = has_skip
        flag_filt = flag_filt[flag_filt['has_skip'] == False]
        if len(flag_filt) > 0:
            flag_filt = flag_filt.drop(['flag_skip', 'has_skip'], axis=1)
            flag_filt['Total Flags'] = flag_filt[drop_flag].count()
            temp = flag_filt.copy()
            temp = temp.reset_index()
            temp = temp.head(1)
            temp = temp[['Total Flags']]
            flag_filt_title = "Total Flags: " + str(temp['Total Flags'].loc[0])
            flag_filt.sort_values(by=['identity', drop_flag], ascending=[True, True], inplace=True)
            flag_filt = flag_filt.drop_duplicates('identity')
            flag_filt = flag_filt[['identity', drop_flag]]
            flag_filt[drop_flag] = flag_filt[drop_flag].rank(ascending=True, method='first')
            flag_filt = flag_filt.rename(columns={'identity': 'Submarkets With Flag', drop_flag: 'Flag Ranking'})
            flag_filt.sort_values(by=['Flag Ranking'], inplace=True)
        else:
            flag_filt_title =  'Total Flags: 0'
            data_fill = {'Submarkets With Flag': ['No Submarkets Flagged'],
                    'Flag Ranking': [0]}
            flag_filt = pd.DataFrame(data_fill, columns=['Submarkets With Flag', 'Flag Ranking'])
    elif len(flag_filt) == 0:
        flag_filt_title =  'Total Flags: 0'
        data_fill = {'Submarkets With Flag': ['No Submarkets Flagged'],
                'Flag Ranking': [0]}
        flag_filt = pd.DataFrame(data_fill, columns=['Submarkets With Flag', 'Flag Ranking'])

    flag_filt_display = {'display': 'block', 'padding-top': '40px'}

    if len(flag_filt) >= 10:
        flag_filt_style_table = {'height': '350px', 'overflowY': 'auto'}
    else:
        flag_filt_style_table = {'overflowY': 'visible'}

    return flag_filt, flag_filt_style_table, flag_filt_display, flag_filt_title


# This function produces the items that need to be returned by the update_data callback if the user has just loaded the program
def first_update(data_init, file_used, sector_val, orig_cols, curryr, currqtr, fileyr, use_rol_close):

    data_init = calc_stats(data_init, curryr, currqtr, True, sector_val)
    data_init = data_init[data_init['yr'] >= curryr - 6]
    data = data_init.copy()
    data = calc_flags(data, curryr, currqtr, sector_val, use_rol_close)

    r = re.compile("^._flag*")
    flag_cols = list(filter(r.match, data.columns))

    if file_used == "oob":
        rank_data_met = data.copy()
        rank_data_met = summarize_flags_ranking(rank_data_met, "met", flag_cols)
        rank_data_met = rank_data_met.rename(columns={'subsector': 'Subsector', 'metcode': 'Metcode'})
        rank_data_sub = data.copy()
        rank_data_sub = summarize_flags_ranking(rank_data_sub, "sub", flag_cols)
        rank_data_sub = rank_data_sub.rename(columns={'subsector': 'Subsector', 'metcode': 'Metcode', 'subid': 'Subid'})

        sum_data = data.copy()
        sum_data = sum_data[sum_data['forecast_tag'] != 0]
        filt_cols = flag_cols + ['identity', 'identity_us', 'identity_met', 'subid', 'yr', 'subsector', 'metcode']
        sum_data = sum_data[filt_cols]
    else:
        rank_data_met = use_pickle("in", "rank_data_met_" + sector_val, False, fileyr, currqtr, sector_val)
        rank_data_sub = use_pickle("in", "rank_data_sub_" + sector_val, False, fileyr, currqtr, sector_val)
        sum_data = use_pickle("in", "sum_data_" + sector_val, False, fileyr, currqtr, sector_val)

    if file_used == "oob":
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_original_flags.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
        temp = data.copy()
        temp = temp[['identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr'] + flag_cols]
        temp = temp[temp['yr'] >= curryr]
        temp = temp[temp['qtr'] == 5]
        temp.to_pickle(file_path)

    return data, rank_data_met, rank_data_sub, sum_data, flag_cols


# This function produces the outputs needed for the update_data callback if the submit button is clicked
def submit_update(data, shim_data, sector_val, orig_cols, user, drop_val, flag_list, skip_list, curryr, currqtr, fileyr, use_rol_close, yr_val, cons_c, avail_c, rent_c, proc_subsequent):
    
    data_save = False
    rebench_trigger = False

    shim_data['cons'] = np.where(shim_data['cons'] == '', np.nan, shim_data['cons'])
    shim_data['avail'] = np.where(shim_data['avail'] == '', np.nan, shim_data['avail'])
    shim_data['mrent'] = np.where(shim_data['mrent'] == '', np.nan, shim_data['mrent'])
    shim_data['merent'] = np.where(shim_data['merent'] == '', np.nan, shim_data['merent'])

    # Check to see if the analyst actually submitted a shim to one of the vars that is eligible to be adjusted
    if shim_data[['cons', 'avail', 'mrent', 'merent']].isnull().values.all() == True:
        shim = False
    else:
        shim = True

    # Check to see if a comment was entered, as we will want to allow that to be processed even if no shim was entered
    comment_check = False
    if (cons_c[-9:] != "Note Here" and len(cons_c) > 0) or (avail_c[-9:] != "Note Here" and len(avail_c) > 0) or (rent_c[-9:] != "Note Here" and len(rent_c) > 0):
        comment_check = True

    if not shim and len(skip_list) == 0 and not comment_check:
        message = "You did not enter any changes."
        message_display = True
    else:
        message = ''
        message_display = False

    if not message_display:
        
        # Implement shims if the user has entered values that differ from the current state of the dataset
        data_orig = data.copy()
        data_orig = data_orig[(data_orig['identity'] == drop_val)].tail(10)
        data_orig = data_orig[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        
        if shim:
            data, has_diff, avail_check, mrent_check, merent_check, first_yr = get_diffs(shim_data, data_orig, data, drop_val, curryr, currqtr, sector_val, 'submit', avail_c, rent_c, proc_subsequent)
        else:
            has_diff = 0

        if has_diff == 2:
            rebench_trigger = True

        # Update decision log with new values entered via shim, and save the updates
        if has_diff == 1 or (len(skip_list) > 0 and not rebench_trigger) or comment_check:
            decision_data = use_pickle("in", "decision_log_" + sector_val, False, fileyr, currqtr, sector_val)
        if has_diff == 1:
            decision_data = update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, "submit", False, yr_val, cons_c, avail_c, rent_c)
        
        # Update dataframe to store user flag skips
        if (flag_list[0] != "v_flag" and len(skip_list) > 0 and not rebench_trigger) or comment_check:
            if flag_list[0] != "v_flag" and len(skip_list) > 0 and not rebench_trigger:
                test = data.loc[drop_val + str(curryr) + str(5)]['flag_skip']
                test = test.split(",")
                test = [x.strip(' ') for x in test]
                for flag in skip_list:
                    if flag + str(yr_val) not in test:
                        if data.loc[drop_val + str(curryr) + str(5), 'flag_skip'] == '':
                            data.loc[drop_val + str(curryr) + str(5), 'flag_skip'] = flag + str(yr_val)
                        else:
                            data.loc[drop_val + str(curryr) + str(5), 'flag_skip'] += ", " + flag + str(yr_val)
                        
                        decision_data = update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, "skip", flag, yr_val, cons_c, avail_c, rent_c)
            elif comment_check:
                decision_data = update_decision_log(decision_data, data, drop_val, sector_val, curryr, currqtr, user, "comment", False, yr_val, cons_c, avail_c, rent_c)
        
        # Save decision log if there was an update, and also save the current state of the edits to ensure nothing gets lost if an error is encountered in later steps
        if has_diff == 1 or (len(skip_list) > 0 and not rebench_trigger) or comment_check:
            use_pickle("out", "decision_log_" + sector_val, decision_data, fileyr, currqtr, sector_val)
            data_save = True

    if not rebench_trigger:
        shim_data[['cons', 'avail', 'mrent', 'merent']] = np.nan

    if rebench_trigger:
        if avail_check:
            var = "vacancy"
        elif mrent_check:
            var = "market rent"
        elif merent_check:
            var = "effective rent"
        message = "You entered a {} shim in {} that resulted in a change from rol above the data governance threshold. To process the shim, enter a supporting comment to document why the shim was made.".format(var, first_yr)
        message_display = True

    return data, shim_data, message, message_display, data_save, rebench_trigger

def test_resolve_flags(preview_data, drop_val, curryr, currqtr, sector_val, orig_flag_list, skip_list, p_skip_list, flag_cols, flag_yr_val, use_rol_close):
    resolve_test = preview_data.copy()
    resolve_test = calc_stats(resolve_test, curryr, currqtr, False, sector_val)
    resolve_test = resolve_test[resolve_test['identity'] == drop_val]
    resolve_test = resolve_test[resolve_test['yr'] == flag_yr_val]
    
    test_flag_list = [x for x in orig_flag_list if x not in skip_list]
    resolve_test = calc_flags(resolve_test, curryr, currqtr, sector_val, use_rol_close)

    resolve_test = resolve_test[flag_cols]
    resolve_test['sum_flags'] = resolve_test[flag_cols].sum(axis=1)
    resolve_test = resolve_test[resolve_test['sum_flags'] > 0]
    if len(resolve_test) > 0:
        resolve_test = resolve_test[resolve_test.columns[(resolve_test != 0).any()]]
        resolve_test = resolve_test.drop(['sum_flags'], axis=1)
        flags_remaining = list(resolve_test.columns)
    
        flags_resolved = [x for x in test_flag_list if x not in flags_remaining and x not in skip_list]
        flags_unresolved = [x for x in test_flag_list if x in flags_remaining and x not in skip_list]
        new_flags = [x for x in flags_remaining if x not in orig_flag_list and x not in skip_list and x not in p_skip_list]
    else:
        flags_resolved = test_flag_list
        flags_unresolved = []
        new_flags = []

    return flags_resolved, flags_unresolved, new_flags

# This function produces the outputs needed for the update_data callback if the preview button is clicked
def preview_update(data, shim_data, sector_val, preview_data, drop_val, curryr, currqtr, orig_flag_list, skip_list, p_skip_list, use_rol_close, flag_yr_val, flag_cols, proc_subsequent): 
    
    shim_data['cons'] = np.where(shim_data['cons'] == '', np.nan, shim_data['cons'])
    shim_data['avail'] = np.where(shim_data['avail'] == '', np.nan, shim_data['avail'])
    shim_data['mrent'] = np.where(shim_data['mrent'] == '', np.nan, shim_data['mrent'])
    shim_data['merent'] = np.where(shim_data['merent'] == '', np.nan, shim_data['merent'])
    
    # At this point, will just always allow the button to be clicked, even if there are no edits entered, as want to allow the user to undo a previewed shim. Can think about a way to test if this is an undo vs a first time entry, but small potatoes as will only marginally increase speed
    message = ''
    message_display = False

    if not message_display:

        data_orig = data.copy()
        data_orig = data_orig[(data_orig['identity'] == drop_val)].tail(10)
        data_orig = data_orig[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        shim_data['cons'] = np.where(shim_data['cons'] == '', np.nan, shim_data['cons'])
        shim_data['avail'] = np.where(shim_data['avail'] == '', np.nan, shim_data['avail'])
        shim_data['mrent'] = np.where(shim_data['mrent'] == '', np.nan, shim_data['mrent'])
        shim_data['merent'] = np.where(shim_data['merent'] == '', np.nan, shim_data['merent'])
        
        preview_data = data.copy()
        preview_data, has_diff, avail_check, mrent_check, merent_check, first_yr = get_diffs(shim_data, data_orig, preview_data, drop_val, curryr, currqtr, sector_val, 'preview', False, False, proc_subsequent)
            
        if has_diff == 1:    
            
            # Test if the flag will be resolved by the edit by re-running calc stats flag and the relevant flag function 
            # Dont run if the col_issue is simply v_flag, which is an indication that there are no flags at the sub even though an edit is being made
            if orig_flag_list[0] != "v_flag":
                flags_resolved, flags_unresolved, new_flags = test_resolve_flags(preview_data, drop_val, curryr, currqtr, sector_val, orig_flag_list, skip_list, p_skip_list, flag_cols, flag_yr_val, use_rol_close)
            else:
                flags_resolved = []
                flags_unresolved = []
                new_flags = []
            
            preview_data = preview_data[(preview_data['identity'] == drop_val)]
            preview_data['sub_prev'] = np.where(preview_data['identity'] == drop_val, 1, 0)
        else:
            preview_data = pd.DataFrame()
            flags_resolved = []
            flags_unresolved = []
            new_flags = []

    return data, preview_data, shim_data, message, message_display, flags_resolved, flags_unresolved, new_flags

# Layout for login page
def login_layout():
    return get_login_layout()

# Main page layout
@validate_login_session
def app_layout(curryr, currqtr, sector_val):
    return get_app_layout(curryr, currqtr, sector_val)

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
                  [Input('url','pathname')],
                  [State('login-curryr', 'value'),
                  State('login-currqtr', 'value'),
                  State('sector_input', 'value')])
def router(pathname, curryr, currqtr, sector_val):
    if pathname[0:5] == '/home':
        return app_layout(curryr, currqtr, sector_val)
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
                    State('rol_close','value'),
                    State('flag_flow_input', 'value')])
def login_auth(n_clicks, username, pw, sector_input, curryr, currqtr, rol_close, flag_flow):

    input_file_alert = False

    if sector_input == "ind":
        for subsector in ["DW", "F"]:
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/InputFiles/{}subdiag_{}_{}q{}_OOB.csv".format(get_home(), sector_input, str(curryr), str(currqtr), sector_input, subsector, str(curryr), str(currqtr)))
            isFile = os.path.isfile(file_path)
            if isFile == True:
                input_file_alert = False
            else:
                input_file_alert = True
                break
    else:
        file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/InputFiles/{}subdiag_{}q{}_OOB.csv".format(get_home(), sector_input, str(curryr), str(currqtr), sector_input, str(curryr), str(currqtr)))
        isFile = os.path.isfile(file_path)
        if isFile == True:
            input_file_alert = False
        else:
            input_file_alert = True

    if n_clicks is None or n_clicks==0:
        return '/login', no_update, ''
    else:
        credentials = {'user': username, "password": pw, "sector": sector_input}
        if authenticate_user(credentials) == True and input_file_alert == False:
            session['authed'] = True
            pathname = '/home' + '?'
            if len(rol_close) == 0:
                rol_close = "N"
            else:
                rol_close = rol_close[0]
            return pathname, '', username + "/" + sector_input.title() + "/" + str(curryr) + "q" + str(currqtr) + "/" + rol_close + "/" + flag_flow
        else:
            session['authed'] = False
            if sector_input is None:
                message = "Select a Sector."
            elif authenticate_user(credentials) == False:
                message = 'Incorrect credentials.'
            elif input_file_alert == True:
                message = 'Input files not set up correctly.'
            return no_update, dbc.Alert(message, color='danger', dismissable=True), no_update


    
@forecast.callback([Output('store_user', 'data'),
                    Output('sector', 'data'),
                    Output('fileyr', 'data'),
                    Output('currqtr', 'data'),
                    Output('store_rol_close', 'data'),
                    Output('flag_flow', 'data')],
                    [Input('url', 'search')])
def store_input_vals(url_input):
    if url_input is None:
        raise PreventUpdate
    else:
        user, sector_val, global_vals, use_rol_close, flag_flow = url_input.split("/")
        fileyr, currqtr = global_vals.split("q")
        fileyr = int(fileyr)
        currqtr = int(currqtr)
        return user, sector_val.lower(), fileyr, currqtr, use_rol_close, flag_flow

@forecast.callback([Output('file_load_alert', 'is_open'),
                    Output('dropman', 'options'),
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
                    Output('rank_view', 'options'),
                    Output('store_flag_cols', 'data'),
                    Output('droproll', 'value'),
                    Output('init_trigger', 'data')],
                    [Input('sector', 'data'),
                    Input('fileyr', 'data'),
                    Input('currqtr', 'data'),
                    Input('store_rol_close', 'data')],
                    [State('store_flag_cols', 'data')])
def initial_data_load(sector_val, fileyr, currqtr, use_rol_close, flag_cols):
    if sector_val is None:
        raise PreventUpdate
    else:
        if currqtr == 4:
            curryr = fileyr + 1
        else:
            curryr = fileyr
        oob_data, orig_cols, file_used = initial_load(sector_val, curryr, currqtr, fileyr)

        try:
            path_in = Path("{}central/square/data/zzz-bb-test2/python/forecast/coeffs/{}/coeffs.csv".format(get_home(), sector_val))
            path_out = Path("{}central/square/data/zzz-bb-test2/python/forecast/coeffs/{}/coeffs.pickle".format(get_home(), sector_val))
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
                decision_data['cons_comment'] = ''
                decision_data['avail_comment'] = ''
                decision_data['rent_comment'] = ''
                use_pickle("out", "decision_log_" + sector_val, decision_data, fileyr, currqtr, sector_val)

            met_combos_temp = list(oob_data['identity_met'].unique())
            met_combos_temp.sort()
            met_combos = list(oob_data['identity_us'].unique()) + met_combos_temp
            if sector_val == "apt" or sector_val == "off" or sector_val == "ret":
                default_drop = met_combos[0]
            elif sector_val == "ind":
                default_drop = "US" + list(oob_data['subsector'].unique())[0] + list(oob_data['expansion'].unique())[0]
            available_years = np.arange(curryr, curryr + 10)

            temp = oob_data.copy()
            temp = temp.set_index('identity')
            sub_combos = list(temp.index.unique())

            oob_data, rank_data_met, rank_data_sub, sum_data, flag_cols = first_update(oob_data, file_used, sector_val, orig_cols, curryr, currqtr, fileyr, use_rol_close)              

            oob_data.replace([np.inf, -np.inf], np.nan, inplace=True)
            use_pickle("out", "main_data_" + sector_val, oob_data, fileyr, currqtr, sector_val)
            use_pickle("out", "rank_data_met_" + sector_val, rank_data_met, curryr, currqtr, sector_val)
            use_pickle("out", "rank_data_sub_" + sector_val, rank_data_sub, curryr, currqtr, sector_val)
            use_pickle("out", "sum_data_" + sector_val, sum_data, curryr, currqtr, sector_val)

            flag_list = get_issue("list", sector_val)
        
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

            return False, [{'label': i, 'value': i} for i in sub_combos], [{'label': i, 'value': i} for i in met_combos], [{'label': i, 'value': i} for i in met_combos], default_drop, [{'label': i, 'value': i} for i in available_years], [{'label': i, 'value': i} for i in available_years], curryr, file_used, orig_cols, curryr, [{'label': i, 'value': i} for i in flag_list_all], flag_list_all[0], rank_options, flag_cols, default_drop, True
        else:
            return True, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, False

@forecast.callback(Output('out_flag_trigger', 'data'),
                  [Input('sector', 'data'),
                  Input('flag-button', 'n_clicks'),
                  Input('store_init_flags', 'data')],
                  [State('curryr', 'data'),
                  State('currqtr', 'data'),
                  State('fileyr', 'data'),
                  State('init_trigger', 'data'),
                  State('store_flag_cols', 'data')])

def output_flags(sector_val, flag_button, init_flags_triggered, curryr, currqtr, fileyr, success_init, flag_cols):
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        input_id = get_input_id()
        if input_id == "flag-button":
            use_pickle(False, sector_val + "_original_flags", False, fileyr, currqtr, sector_val)

            current_flags = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
            
            cols_to_keep = ['identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr'] + flag_cols
            current_flags = current_flags[cols_to_keep]
            current_flags = current_flags[current_flags['yr'] >= curryr]
            current_flags = current_flags[current_flags['qtr'] == 5]
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_current_flags.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
            current_flags.reset_index().set_index('identity').to_csv(file_path, na_rep='')

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
    elif input_id != "finalize-button":
        raise PreventUpdate
    else:
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
    
    if sector_val is None or success_init == False or confirm_click is None:
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
        if sector_val == "ind":
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
            if sector_val == "ind":
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
            finalized_met = finalized_met.drop(['avail'], axis=1)

            if sector_val == "ind":
                output_cols_met = ['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolcons', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'occ', 'abs', 'rolabs', 'vac',	'rolvac', 
                                    'mrent', 'rolmrent', 'G_mrent', 'grolmren', 'merent', 'G_merent', 'rolmeren', 'grolmere', 'gap', 'rolgap', 'cons_oob', 'vac_oob', 'abs_oob', 
                                    'G_mrent_oob', 'G_merent_oob', 'mrent_oob',	'merent_oob', 'gap_oob']
            else:
                output_cols_met = ['metcode', 'yr',	'qtr', 'inv', 'cons', 'rolcons', 'h', 'rol_h', 'e', 't', 'demo', 'conv', 'occ', 'abs', 'rolabs', 'vac', 'rolvac',
                                    'mrent', 'rolmrent', 'G_mrent', 'grolmren', 'merent', 'G_merent', 'rolmeren',  'grolmere', 'gap', 'rolgap']

            finalized_met = finalized_met.rename(columns={'rolscon': 'rolcons', 'grolsmre': 'grolmren', 'rol_mrent' :'rolmrent', 'grolsmer': 'grolmere',
                                                            'rolsabs' :'rolabs', 'rolsvac': 'rolvac', 'rol_merent': 'rolmeren'})

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
            finalized_us = finalized_us.drop(['avail'], axis=1)

            if sector_val == "ind":
                output_cols_us = ['subsector', 'yr', 'qtr', 'US_inv', 'US_cons', 'US_rolcons', 'US_h', 'US_rol_h', 'US_e', 'US_t', 'US_vac', 'US_abs', 'US_rolabs',
                                    'US_mrent', 'US_G_mrent', 'US_merent', 'US_G_merent', 'US_gap']
            else:
                output_cols_us = ['yr', 'qtr', 'US_inv', 'US_cons', 'US_rolcons', 'US_h', 'US_rol_h', 'US_e', 'US_t', 'US_vac', 'US_abs', 'US_rolabs',
                                    'US_mrent', 'US_G_mrent', 'US_merent', 'US_G_merent', 'US_gap']

            finalized_us = finalized_us.rename(columns={'rolscon': 'rolcons', 'rolsabs': 'rolabs'})
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
                file_path_dta = "{}central/metcast/data/{}/forecast/current/US_{}test_{}q{}.dta".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_us.to_stata(file_path_dta, write_index=False)
                file_path_out = "{}central/metcast/data/{}/forecast/current/US_{}test_{}q{}.out".format(get_home(), sector_val, sector_val, str(curryr), str(currqtr))
                finalized_us.to_csv(file_path_out, index=False, na_rep='')

            # Convert decision log to csv file and save in OutputFiles folder
            decision_log_in_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/decision_log_{}.{}".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val, 'pickle'))
            decision_log = pd.read_pickle(decision_log_in_path)
            decision_log_out_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/decision_log_{}.{}".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val, 'csv'))
            decision_log.to_csv(decision_log_out_path, na_rep='')

            # Save a csv file with all the historical rebenches that crossed the data governance threshold
            rebench_log = decision_log.copy()
            comments = decision_log.copy()
            comments = comments[(comments['yr'] == curryr) & (comments['qtr'] == 5)]
            comments = comments.set_index('identity')
            comments = comments[['avail_comment', 'rent_comment']]
            rebench_log = rebench_log[['identity', 'subsector', 'metcode', 'subid', 'yr', 'qtr', 'vac_oob', 'mrent_oob', 'merent_oob', 'vac_new', 'mrent_new', 'merent_new', 'v_user', 'g_user', 'e_user']]
            rebench_log = rebench_log[(rebench_log['yr'] > curryr) | ((rebench_log['yr'] == curryr) & (rebench_log['qtr'] == 5))]
            rebench_log['vac_diff'] = rebench_log['vac_new'] - rebench_log['vac_oob']
            rebench_log['mrent_diff'] = (rebench_log['mrent_new'] - rebench_log['mrent_oob']) / rebench_log['mrent_oob']
            rebench_log['merent_diff'] = (rebench_log['merent_new'] - rebench_log['merent_oob']) / rebench_log['merent_oob']
            
            for var in ['vac_diff', 'mrent_diff', 'merent_diff']:
                first_rebench = rebench_log.copy()
                first_rebench = first_rebench[abs(first_rebench[var]) > 0.001]
                first_rebench.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], ascending=[True, True, True, True, True], inplace=True)
                first_rebench = first_rebench.drop_duplicates('identity')
                first_rebench['init_shim_period_' + var.replace("_diff", '')] = first_rebench['yr'].astype(str) + "q" + first_rebench['qtr'].astype(str)
                first_rebench = first_rebench.set_index('identity')
                first_rebench = first_rebench[['init_shim_period_' + var.replace("_diff", '')]]
                rebench_log = rebench_log.join(first_rebench, on='identity')
            rebench_log = rebench_log[(abs(rebench_log['vac_diff'] >= 0.01)) | (abs(rebench_log['mrent_diff'] >= 0.03)) | (abs(rebench_log['merent_diff'] >= 0.03))]
            rebench_log['vac_diff'] = np.where(abs(rebench_log['vac_diff']) < 0.01, np.nan, rebench_log['vac_diff'])
            rebench_log['mrent_diff'] = np.where(abs(rebench_log['mrent_diff']) < 0.03, np.nan, rebench_log['mrent_diff'])
            rebench_log['merent_diff'] = np.where(abs(rebench_log['merent_diff']) < 0.03, np.nan, rebench_log['merent_diff'])
            rebench_log['init_shim_period_vac'] = np.where(abs(rebench_log['vac_diff']) < 0.01, np.nan, rebench_log['init_shim_period_vac'])
            rebench_log['init_shim_period_mrent'] = np.where(abs(rebench_log['mrent_diff']) < 0.03, np.nan, rebench_log['init_shim_period_mrent'])
            rebench_log['init_shim_period_merent'] = np.where(abs(rebench_log['merent_diff']) < 0.03, np.nan, rebench_log['init_shim_period_merent'])
            rebench_log['v_user'] = np.where(abs(rebench_log['vac_diff']) < 0.01, np.nan, rebench_log['v_user'])
            rebench_log['g_user'] = np.where(abs(rebench_log['mrent_diff']) < 0.03, np.nan, rebench_log['g_user'])
            rebench_log['e_user'] = np.where(abs(rebench_log['merent_diff']) < 0.03, np.nan, rebench_log['e_user'])
            rebench_log = rebench_log.join(comments, on='identity')
            rebench_log = rebench_log.rename(columns={'avail_comment': 'vac_comment'})
            rebench_log.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], ascending=[True, True, True, False, False], inplace=True)
            rebench_log = rebench_log.drop_duplicates('identity')
            file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/rebench_log_{}_{}q{}.csv".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val, str(fileyr), str(currqtr)))
            rebench_log.to_csv(file_path, index=False, na_rep='')

        return True, alert_display, alert_text

@forecast.callback([Output('manual_message', 'message'),
                    Output('manual_message', 'displayed'),
                    Output('store_all_buttons', 'data'),
                    Output('store_submit_button', 'data'),
                    Output('store_preview_button', 'data'),
                    Output('store_init_flags', 'data'),
                    Output('store_flag_resolve', 'data'),
                    Output('store_flag_unresolve', 'data'),
                    Output('store_flag_new', 'data'),
                    Output('store_flag_skips', 'data'),
                    Output('flag_filt', 'data'),
                    Output('flag_filt', 'columns'),
                    Output('flag_filt', 'style_table'),
                    Output('flag_filt_container', 'style'),
                    Output('dropman', 'value'),
                    Output('countdown', 'data'),
                    Output('countdown', 'columns'),
                    Output('first_update', 'data'),
                    Output('key_yr_radios', 'value')],
                    [Input('submit-button', 'n_clicks'),
                    Input('preview-button', 'n_clicks'),
                    Input('dropflag', 'value'),
                    Input('init_trigger', 'data')],
                    [State('sector', 'data'),
                    State('store_orig_cols', 'data'),
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
                    State('p_skip_list', 'data'),
                    State('init_trigger', 'data'),
                    State('flag_description_noprev', 'children'),
                    State('flag_description_resolved', 'children'),
                    State('flag_description_unresolved', 'children'),
                    State('flag_description_new', 'children'),
                    State('flag_description_skipped', 'children'),
                    State('store_flag_cols', 'data'),
                    State('first_update', 'data'),
                    State('flag_flow', 'data'),
                    State('key_yr_radios', 'value'),
                    State('process_subsequent', 'value')])
def update_data(submit_button, preview_button, drop_flag, init_fired, sector_val, orig_cols, curryr, currqtr, fileyr, user, file_used, cons_c, avail_c, rent_c, drop_val, use_rol_close, flag_list, p_skip_list, success_init, skip_input_noprev, skip_input_resolved, skip_input_unresolved, skip_input_new, skip_input_skipped, flag_cols, first_update, flag_flow, yr_val, proc_subsequent):

    input_id = get_input_id()
    
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)

         # If there is a flag description, use this crazy dict/list slicer to get the actual values of the children prop so we can see what flags the user wants to skip
        if skip_input_noprev == "No flags for this year at the submarket" or skip_input_noprev == "You have cleared all the flags":
            skip_list = []
        elif skip_input_noprev != None or skip_input_resolved != None or skip_input_unresolved != None or skip_input_new != None or skip_input_skipped != None:
            skip_list = get_user_skips(skip_input_noprev, skip_input_resolved, skip_input_unresolved, skip_input_new, skip_input_skipped)
        else:
            skip_list = []

        if input_id != 'submit-button':
            rebench_trigger = False
        
        # Load preview data if previewing
        if input_id == 'preview-button':
            preview_data = use_pickle("in", "preview_data_" + sector_val, False, fileyr, currqtr, sector_val)
        
        # Load shim data if previewing or submitting
        if input_id == 'submit-button' or input_id == 'preview-button':
            shim_data = use_pickle("in", "shim_data_" + sector_val, False, fileyr, currqtr, sector_val)
        
        if input_id == 'submit-button':
            data, shim_data, message, message_display, data_save, rebench_trigger = submit_update(data, shim_data, sector_val, orig_cols, user, drop_val, flag_list, skip_list, curryr, currqtr, fileyr, use_rol_close, yr_val, cons_c, avail_c, rent_c, proc_subsequent)
            if rebench_trigger == False:
                preview_data = pd.DataFrame()
        elif input_id == 'preview-button':
            data, preview_data, shim_data, message, message_display, flags_resolved, flags_unresolved, flags_new = preview_update(data, shim_data, sector_val, preview_data, drop_val, curryr, currqtr, flag_list, skip_list, p_skip_list, use_rol_close, yr_val, flag_cols, proc_subsequent)
        
        else:
            message = ''
            message_display = False
            preview_data = pd.DataFrame()
            shim_data = pd.DataFrame()
        
        
        if message_display == False and input_id == 'submit-button':
            data = data.reset_index().set_index('identity')
            if cons_c[-9:] != "Note Here":
                data.loc[drop_val, 'cons_comment'] = cons_c
            if avail_c[-9:] != "Note Here":
                data.loc[drop_val, 'avail_comment'] = avail_c
            if rent_c[-9:] != "Note Here":
                data.loc[drop_val, 'rent_comment'] = rent_c
            data = data.reset_index().set_index('identity_row')

        if input_id != "preview-button":
            flag_filt, flag_filt_style_table, flag_filt_display, flag_filt_title = filter_flags(data, drop_flag)

        if input_id == "submit-button" or input_id == "init_trigger" or first_update == True:
            # Re-calc stats and flags now that the data has been updated, or if this is the initial load
            if  message_display == False:
                data = calc_stats(data, curryr, currqtr, False, sector_val)
                data = calc_flags(data, curryr, currqtr, sector_val, use_rol_close)

                # There might be cases where an analyst checked off to skip a flag, but that flag is no longer triggered (example: emdir, where there was a shim to mrent that fixed the flag). We will want to remove that skip from the log
                # if input_id == "submit-button":
                #     if len(skip_list) > 0:
                #         decision_data = use_pickle("in", "decision_log_" + sector_val, False, fileyr, currqtr, sector_val)
                #         data, decision_data = check_skips(data, decision_data, curryr, currqtr, sector_val, flag_cols, drop_val)
                #         use_pickle("out", "decision_log_" + sector_val, decision_data, fileyr, currqtr, sector_val)

            # Update countdown table
            countdown = data.copy()
            countdown = data[(data['yr'] >= curryr) & (data['qtr'] == 5)]
            countdown = countdown[['forecast_tag', 'identity_us', 'flag_skip'] + flag_cols]
            countdown = live_flag_count(countdown, sector_val, flag_cols)
            type_dict_countdown, format_dict_countdown = get_types(sector_val)

            # Get the next sub flagged
            flag_list, p_skip_list, drop_val, has_flag, yr_val = flag_examine(data, drop_val, False, curryr, currqtr, flag_cols, flag_flow, yr_val)
            use_pickle("out", "main_data_" + sector_val, data, fileyr, currqtr, sector_val)
        
        if rebench_trigger == False:
            use_pickle("out", "preview_data_" + sector_val, preview_data, fileyr, currqtr, sector_val)
        use_pickle("out", "shim_data_" + sector_val, shim_data, fileyr, currqtr, sector_val)

        if input_id == "submit-button":
            if data_save == True:
                data_to_save = data.copy()
                file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_mostrecentsave.pickle".format(get_home(), sector_val, str(fileyr), str(currqtr), sector_val))
                data_to_save = data_to_save[orig_cols]
                data_to_save.to_pickle(file_path)

        # Need to set this variable so that the succeeding callbacks will only fire once update is done
        if message_display == True:
            all_buttons = 1
            submit_button = no_update
            preview_button = no_update
            init_flags = no_update
            drop_val = no_update
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
            elif input_id == "dropflag":
                all_buttons = no_update
                submit_button = no_update
                preview_button = no_update
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

        if input_id == "submit-button" or input_id == "init_trigger" or first_update == True:
            return message, message_display, all_buttons, submit_button, preview_button, init_flags, flags_resolved, flags_unresolved, flags_new, skip_list, flag_filt.to_dict('records'), [{'name': [flag_filt_title, flag_filt.columns[i]], 'id': flag_filt.columns[i]} 
                        for i in range(0, len(flag_filt.columns))], flag_filt_style_table, flag_filt_display, drop_val, countdown.to_dict('records'), [{'name': ['Flags Remaining', countdown.columns[i]], 'id': countdown.columns[i], 'type': type_dict_countdown[countdown.columns[i]], 'format': format_dict_countdown[countdown.columns[i]]}
                    for i in range(0, len(countdown.columns))], False, yr_val
        elif input_id == "dropflag":
            return message, message_display, all_buttons, submit_button, preview_button, init_flags, no_update, no_update, no_update, no_update, flag_filt.to_dict('records'), [{'name': [flag_filt_title, flag_filt.columns[i]], 'id': flag_filt.columns[i]} 
                        for i in range(0, len(flag_filt.columns))], flag_filt_style_table, flag_filt_display, no_update, no_update, no_update, False, no_update
        else:
            return message, message_display, all_buttons, submit_button, preview_button, init_flags, flags_resolved, flags_unresolved, flags_new, skip_list, no_update, no_update, no_update, no_update, no_update, no_update, no_update, False, yr_val

@forecast.callback([Output('has_flag', 'data'),
                Output('flag_list', 'data'),
                Output('p_skip_list', 'data'),
                Output('key_met_radios', 'value')],
                [Input('dropman', 'value'),
                Input('sector', 'data'),
                Input('init_trigger', 'data'),
                Input('store_preview_button', 'data'),
                Input('key_yr_radios', 'value')],
                [State('curryr', 'data'),
                State('currqtr', 'data'),
                State('fileyr', 'data'),
                State('init_trigger', 'data'),
                State('store_flag_cols', 'data'),
                State('store_flag_unresolve', 'data'),
                State('store_flag_new', 'data'),
                State('flag_flow', 'data')])

def process_man_drop(drop_val, sector_val, init_fired, preview_status, yr_val, curryr, currqtr, fileyr, success_init, flag_cols, flags_unresolved, flags_new, flag_flow):
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:    
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        flag_list, p_skip_list, drop_val, has_flag, yr_val = flag_examine(data, drop_val, True, curryr, currqtr, flag_cols, flag_flow, yr_val)

        # Reset the radio button to the correct variable based on the new flag
        if has_flag == 1:
            if len(flags_unresolved) > 0:
                key_met_radio_val = flags_unresolved[0][0]
            elif len(flags_new) > 0:
                key_met_radio_val = flags_new[0][0]
            else:
                key_met_radio_val = flag_list[0][0]
        else:
            key_met_radio_val = no_update

        return has_flag, flag_list, p_skip_list, key_met_radio_val

@forecast.callback(Output('download_trigger', 'data'),
                   [Input('sector', 'data'),
                   Input('store_submit_button', 'data'),
                   Input('download-button', 'n_clicks')],
                   [State('curryr', 'data'),
                   State('currqtr', 'data'),
                   State('fileyr', 'data'),
                   State('store_orig_cols', 'data'),
                   State('init_trigger', 'data')])

def output_edits(sector_val, submit_button, download_button, curryr, currqtr, fileyr, orig_cols, success_init):
    input_id = get_input_id()
    if sector_val is None or success_init == False:
        raise PreventUpdate
    
    # Need this to tie to update_data callback so the csv is not set before the data is actually updated, but dont want to call the set csv function each time submit is clicked, so only do that when the input id is for the download button
    elif input_id == "store_submit_button" or input_id == "sector":
        raise PreventUpdate
    else:
        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        
        sub_edits_output = data.copy()
        if sector_val == "ret" or sector_val == "off":
            orig_cols += ['rolmerent']
        sub_edits_output = sub_edits_output[orig_cols]
        deep_file_path = Path("{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_deep_hist.pickle".format(get_home(), sector_val, str(curryr), str(currqtr), sector_val))
        deep_history = pd.read_pickle(deep_file_path)
        deep_history = deep_history[orig_cols]
        sub_edits_output = sub_edits_output.append(deep_history)
        sub_edits_output.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace=True)
        sub_edits_output['cons_comment'] = np.where(sub_edits_output['cons_comment'] == "Enter Cons Shim Note Here", '', sub_edits_output['cons_comment'])
        sub_edits_output['avail_comment'] = np.where(sub_edits_output['avail_comment'] == "Enter Avail Shim Note Here", '', sub_edits_output['avail_comment'])
        sub_edits_output['rent_comment'] = np.where(sub_edits_output['rent_comment'] == "Enter Rent Shim Note Here", '', sub_edits_output['rent_comment'])
        if sector_val == "apt" or sector_val == "off" or sector_val == "ret":
            sub_edits_output['inv'] = np.where(sub_edits_output['yr'] == 1998, "", sub_edits_output['inv'])
            sub_edits_output['inv'] = np.where((sub_edits_output['yr'] == 2003) & ((sub_edits_output['metcode'] == "PV") | (sub_edits_output['metcode'] == "WS")), "", sub_edits_output['inv'])

        file_path = "{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_edits_sub.csv".format(get_home(), sector_val, fileyr, currqtr, sector_val)
        sub_edits_output.to_csv(file_path, index=False, na_rep='')

        met_edits_output = data.copy()
        met_edits_output = rollup(met_edits_output, 'met_finalizer', curryr, currqtr, sector_val, "reg", True)
        met_edits_output = met_edits_output[['subsector', 'metcode', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'avail', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'mrent', 'rol_mrent', 'G_mrent', 'grolsmre', 'merent', 'rol_merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rolgap']]
        met_edits_output = met_edits_output.rename(columns={'rolscon': 'rol_cons', 'rolsvac': 'rol_vac', 'rolsvac_chg': 'rol_vac_chg', 'rolsabs': 'rol_abs', 'grolsmre': 'rol_G_mrent', 'grolsmer': 'rol_G_merent', 'rolgap': 'rol_gap'})
        met_edits_output = met_edits_output[((met_edits_output['yr'] >= curryr - 5) & (met_edits_output['qtr'] == 5)) | (met_edits_output['yr'] == curryr)]
        file_path = "{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_edits_met.csv".format(get_home(), sector_val, fileyr, currqtr, sector_val)
        met_edits_output.to_csv(file_path, index=False, na_rep='')

        nat_edits_output = data.copy()
        nat_edits_output = rollup(nat_edits_output, 'US_finalizer', curryr, currqtr, sector_val, "reg", True)
        nat_edits_output = nat_edits_output[['subsector', 'yr', 'qtr', 'inv', 'cons', 'rolscon', 'vac', 'vac_chg', 'rolsvac', 'rolsvac_chg', 'abs', 'rolsabs', 'mrent', 'rol_mrent', 'G_mrent', 'grolsmre', 'merent', 'rol_merent', 'G_merent', 'grolsmer', 'gap', 'gap_chg', 'rolgap']]
        nat_edits_output.sort_values(by=['subsector', 'yr', 'qtr'], ascending=[True, True, True], inplace=True)
        nat_edits_output = nat_edits_output.rename(columns={'rolscon': 'rol_cons', 'rolsvac': 'rol_vac', 'rolsvac_chg': 'rol_vac_chg', 'rolsabs': 'rol_abs', 'grolsmre': 'rol_G_mrent', 'grolsmer': 'rol_G_merent', 'rolgap': 'rol_gap'})
        nat_edits_output = nat_edits_output[((nat_edits_output['yr'] >= curryr - 5) & (nat_edits_output['qtr'] == 5)) | (nat_edits_output['yr'] == curryr)]
        file_path = "{}central/square/data/zzz-bb-test2/python/forecast/{}/{}q{}/OutputFiles/{}_edits_nat.csv".format(get_home(), sector_val, fileyr, currqtr, sector_val)
        nat_edits_output.to_csv(file_path, index=False, na_rep='')
        
        return True

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
                    Output('sum_container', 'style'),
                    Output('nat_eco_table', 'data'),
                    Output('nat_eco_table', 'columns'),
                    Output('nat_eco_table', 'style_data_conditional'),
                    Output('nat_eco_container', 'style'),],
                    [Input('sector', 'data'),
                    Input('dropsum', 'value'),
                    Input('store_init_flags', 'data')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data'),
                    State('store_flag_cols', 'data')])
def display_summary(sector_val, drop_val, init_flags, curryr, currqtr, fileyr, success_init, flag_cols):
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        dash_curryr = str(curryr)
        dash_second_five = curryr + 5
        dash_second_five = str(dash_second_five)
        
        input_id = get_input_id()

        sum_style = {'display': 'block', 'padding-top': '18px'}
        rank_style = {'display': 'block'}
        eco_style = {'display': 'block', 'padding-top': '30px'}

        if input_id == 'store_init_flags':
            rank_data_met = use_pickle("in", "rank_data_met_" + sector_val, False, fileyr, currqtr, sector_val)
            rank_data_sub = use_pickle("in", "rank_data_sub_" + sector_val, False, fileyr, currqtr, sector_val)
            sum_data = use_pickle("in", "sum_data_" + sector_val, False, fileyr, currqtr, sector_val)
            eco_data = use_pickle("in", "nat_eco_data_" + sector_val, False, fileyr, currqtr, sector_val)
            
            eco_data = eco_data[eco_data['yr'] <= curryr + 4]
            if sector_val == "apt" or sector_val == "ret":
                emp_to_use = "emp_chg"
                rol_emp_to_use = "rol_emp_chg"
                imp_emp_to_use = 'implied_emp_chg'
                header_name = "US Employment Change"
            elif sector_val == "off":
                emp_to_use = "off_emp_chg"
                rol_emp_to_use = "rol_off_emp_chg"
                imp_emp_to_use = 'implied_off_emp_chg'
                header_name = "US Office Employment Change"
            elif sector_val == "ind":
                emp_to_use = "ind_emp_chg"
                rol_emp_to_use = "rol_ind_emp_chg"
                imp_emp_to_use = 'implied_ind_emp_chg'
                header_name = "US Industrial Employment Change"

            if currqtr == 4:
                eco_data = eco_data[['yr', emp_to_use, rol_emp_to_use, 'emp_chg_z', 'avg_inc_chg']]
            elif currqtr != 4:
                eco_data = eco_data[['yr', emp_to_use, imp_emp_to_use, rol_emp_to_use, 'emp_chg_z', 'avg_inc_chg']]
                eco_data = eco_data.rename(columns={imp_emp_to_use: 'imp emp chg'})
            for col in eco_data:
                eco_data.rename(columns={col: col.replace('_', ' ')}, inplace=True)

            sum_data = summarize_flags(sum_data, drop_val, flag_cols)
            type_dict_rank_met, format_dict_rank_met = get_types(sector_val)
            highlighting_rank_met = get_style("partial", rank_data_met, dash_curryr, dash_second_five)
            type_dict_rank_sub, format_dict_rank_sub = get_types(sector_val)
            highlighting_rank_sub = get_style("partial", rank_data_sub, dash_curryr, dash_second_five)

            type_dict_sum, format_dict_sum = get_types(sector_val)
            highlighting_sum = get_style("partial", sum_data, dash_curryr, dash_second_five)

            type_dict_eco, format_dict_eco = get_types(sector_val)
            highlighting_eco = get_style("partial", eco_data, dash_curryr, dash_second_five)
        
            return rank_data_met.to_dict('records'), [{'name':['Top Ten Flagged Metros', rank_data_met.columns[i]], 'id': rank_data_met.columns[i], 'type': type_dict_rank_met[rank_data_met.columns[i]], 'format': format_dict_rank_met[rank_data_met.columns[i]]} 
                                for i in range(0, len(rank_data_met.columns))], highlighting_rank_met, rank_data_sub.to_dict('records'), [{'name':['Top Ten Flagged Submarkets', rank_data_sub.columns[i]], 'id': rank_data_sub.columns[i], 'type': type_dict_rank_sub[rank_data_sub.columns[i]], 'format': format_dict_rank_sub[rank_data_sub.columns[i]]} 
                                for i in range(0, len(rank_data_sub.columns))], highlighting_rank_sub, rank_style, sum_data.to_dict('records'), [{'name': ['OOB Initial Flag Summary', sum_data.columns[i]], 'id': sum_data.columns[i], 'type': type_dict_sum[sum_data.columns[i]], 'format': format_dict_sum[sum_data.columns[i]]} 
                                for i in range(0, len(sum_data.columns))], highlighting_sum, sum_style, eco_data.to_dict('records'), [{'name': [header_name, eco_data.columns[i]], 'id': eco_data.columns[i], 'type': type_dict_eco[eco_data.columns[i]], 'format': format_dict_eco[eco_data.columns[i]]} 
                                for i in range(0, len(eco_data.columns))], highlighting_eco, eco_style
        else:
            sum_data = use_pickle("in", "sum_data_" + sector_val, False, fileyr, currqtr, sector_val)
            sum_data = summarize_flags(sum_data, drop_val, flag_cols)
            type_dict_sum, format_dict_sum = get_types(sector_val)
            highlighting_sum = get_style("partial", sum_data, dash_curryr, dash_second_five)
            
            return no_update, no_update, no_update, no_update, no_update, no_update, no_update, sum_data.to_dict('records'), [{'name': ['OOB Initial Flag Summary', sum_data.columns[i]], 'id': sum_data.columns[i], 'type': type_dict_sum[sum_data.columns[i]], 'format': format_dict_sum[sum_data.columns[i]]} 
                                for i in range(0, len(sum_data.columns))], highlighting_sum, sum_style, no_update, no_update, no_update, no_update

@forecast.callback([Output('show_skips', 'value'),
                   Output('process_subsequent', 'value')],
                   [Input('store_submit_button', 'data'),
                   Input('dropman', 'value'),
                   Input('sector', 'data')],
                   [State('init_trigger', 'data')])
def remove_options(submit_button, drop_val, sector_val, success_init):
    if sector_val is None or success_init == False:
        raise PreventUpdate
    else:
        return ['N'], 'c'


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
                    Output('process_subsequent_container', 'style'),
                    Output('comment_cons', 'value'),
                    Output('comment_avail', 'value'),
                    Output('comment_rent', 'value')],
                    [Input('sector', 'data'),
                    Input('dropman', 'value'),
                    Input('store_all_buttons', 'data'),
                    Input('key_met_radios', 'value'),
                    Input('key_yr_radios', 'value'),
                    Input('show_skips', 'value')],
                    [State('has_flag', 'data'),
                    State('flag_list', 'data'),
                    State('store_orig_cols', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('store_flag_resolve', 'data'),
                    State('store_flag_unresolve', 'data'),
                    State('store_flag_new', 'data'),
                    State('store_flag_skips', 'data'),
                    State('init_trigger', 'data'),
                    State('store_flag_cols', 'data'),
                    State('comment_cons', 'value'),
                    State('comment_avail', 'value'),
                    State('comment_rent', 'value'),
                    State('flag_description_noprev', 'children'),
                    State('manual_message', 'message')])  
def output_display(sector_val, drop_val, all_buttons, key_met_val, yr_val, show_skips, has_flag, flag_list, orig_cols, curryr, currqtr, fileyr, flags_resolved, flags_unresolved, flags_new, flags_skipped, success_init, flag_cols, init_comment_cons, init_comment_avail, init_comment_rent, init_skips, message):  

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
        if len(shim_data) == 0:
            shim_data = data.copy()
            shim_data[['cons', 'avail', 'mrent', 'merent']] = np.nan
            shim_data = shim_data[(shim_data['identity'] == drop_val) ].tail(10)
        shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
        highlighting_shim = get_style("full", shim_data, dash_curryr, dash_second_five)

        # If the user changes the sub they want to edit, reset the shim section
        if (len(preview_data) > 0 and  drop_val != preview_data[preview_data['sub_prev'] == 1].reset_index().loc[0]['identity']) or (shim_data.reset_index()['identity_row'].str.contains(drop_val).loc[0] == False) == True:
            sub_change = True
        else:
            sub_change = False
        if sub_change == True:
            preview_data = pd.DataFrame()
            shim_data = data.copy()
            shim_data = shim_data[['qtr', 'identity', 'yr', 'cons', 'avail', 'mrent', 'merent']]
            shim_data = shim_data[(shim_data['yr'] >= curryr) & (shim_data['qtr'] == 5)]
            shim_data = shim_data[(shim_data['identity'] == drop_val)]
            shim_data[['cons', 'avail', 'mrent', 'merent']] = np.nan
            use_pickle("out", "preview_data_" + sector_val, preview_data, fileyr, currqtr, sector_val)
            use_pickle("out", "shim_data_" + sector_val, shim_data, fileyr, currqtr, sector_val)

        # Get the Divs that will display the current flags at the sub, as well as the metrics to highlight based on the flag
        if init_skips is not None and init_skips != "No flags for this year at the submarket" and init_skips != "You have cleared all the flags" and sub_change == False:
            init_skips = get_user_skips(init_skips, [], [], [], [])
        else:
            init_skips = []
        if "Y" in show_skips:
            show_skips = True
        else:
            show_skips = False
            p_skip_list = []

        if len(preview_data) > 0 and "governance" not in message:
            preview_status = True
        else:
            preview_status = False
        
        issue_description_noprev, issue_description_resolved, issue_description_unresolved, issue_description_new, issue_description_skipped, display_highlight_list, key_metrics_highlight_list, key_emp_highlight_list = get_issue("specific", sector_val, data, has_flag, flag_list, p_skip_list, show_skips, flags_resolved, flags_unresolved, flags_new, flags_skipped, curryr, currqtr, preview_status, init_skips)

        if len(issue_description_noprev) == 0:
            style_noprev = {'display': 'none'}
        else:
            if (has_flag == 0 or has_flag == 2) and (show_skips == False or len(p_skip_list) == 0):
                style_noprev = {'padding-left': '10px', 'width': '100%', 'display': 'inline-block', 'font-size': '16px', 'vertical-align': 'top', 'text-align': 'center'}
            else:
                style_noprev = {'padding-left': '10px', 'width': '60%', 'display': 'inline-block', 'font-size': '16px', 'vertical-align': 'top'}
        if len(issue_description_resolved) == 0:
            style_resolved = {'display': 'none'}
        else:
            width = str(len(flags_resolved) * 10) + '%'
            style_resolved = {'padding-left': '10px', 'width': width, 'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold', 'vertical-align': 'top'}
        if len(issue_description_unresolved) == 0:
            style_unresolved = {'display': 'none'}
        else:
            width = str(len(flags_unresolved) * 10) + '%'
            if len(issue_description_resolved) > 0:
                style_unresolved = {'width': width, 'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold', 'vertical-align': 'top'}
            else:
                style_unresolved = {'padding-left': '10px', 'width': width, 'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold', 'vertical-align': 'top'}
        if len(issue_description_new) == 0:
            style_new = {'display': 'none'}
        else:
            width = str(len(flags_new) * 10) + '%'
            if len(issue_description_resolved) > 0 or len(issue_description_unresolved) > 0:
                style_new = {'width': width, 'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold', 'vertical-align': 'top'}
            else:
                style_new = {'padding-left': '10px', 'width': width, 'display': 'inline-block', 'font-size': '16px', 'font-weight': 'bold', 'vertical-align': 'top'}
        if len(issue_description_skipped) == 0:
            style_skipped = {'display': 'none'}
        else:
            width = str(len(flags_skipped) * 10) + '%'
            if len(issue_description_resolved) > 0 or len(issue_description_unresolved) > 0 or len(issue_description_new) > 0:
                style_skipped = {'width': width, 'display': 'inline-block', 'font-size': '16px', 'vertical-align': 'top'}
            else:
                style_skipped = {'padding-left': '10px', 'width': width, 'display': 'inline-block', 'font-size': '16px', 'vertical-align': 'top'}
        
        # Call the function to set up the sub time series graphs
        if len(preview_data) > 0:
            data_vac, data_rent = sub_met_graphs(preview_data, "sub", curryr, currqtr, fileyr, sector_val)
        else:
            data_vac, data_rent = sub_met_graphs(data[(data['identity'] == drop_val)], "sub", curryr, currqtr, fileyr, sector_val)
        
        # Set the data for the main data display, using the correct data set based on whether the user is previewing a shim or not
        if len(preview_data) > 0:
            display_data = preview_data.copy()
        else:
            display_data = data.copy()
            display_data = display_data[(display_data['identity'] == drop_val)]
        
        # Use key_met_val to set display cols, and if there is none selected, set the display cols based on the first flag type for the sub
        if key_met_val is None:
            key_met_val = flag_list[0][0]
        display_cols, key_met_cols, key_emp_cols = set_display_cols(data, drop_val, sector_val, curryr, currqtr, key_met_val, yr_val, message)
        display_data = display_frame(display_data, drop_val, display_cols, curryr)

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
                                                    'grolsmre': 'rol Gmrent', 'grolsmer': 'rol Gmerent', 'G mrent': 'Gmrent', 'G merent': 'Gmerent', 'rolsgap chg': 'rol gap chg', 'rolmrent': 'rol mrent', 'rolmerent': 'rol merent'})
        
        # Get the row index of the metric to be highlighted in the display table
        if "governance" not in message or len(preview_data) == 0:
            temp = display_data.copy()
            temp = temp.reset_index()
            temp['id'] = temp.index
            var_flags = ['c_flag_lowv', 'v_flag_lowv', 'g_flag_lowv', 'g_flag_highv']
            if len(preview_data) == 0:
                if flag_list[0] in var_flags:
                    display_highlight_rows = list(temp.tail(10)['id'])
                else:
                    display_highlight_rows = list(temp[(temp['yr'] == yr_val) & (temp['qtr'] == 5)]['id'])
            else:
                if len(flags_new) > 0:
                    if flags_new[0] in var_flags:
                        display_highlight_rows = list(temp.tail(10)['id'])
                    else:
                        display_highlight_rows = list(temp[(temp['yr'] == yr_val) & (temp['qtr'] == 5)]['id'])
                elif len(flags_unresolved) > 0:
                    if flags_unresolved[0] in var_flags:
                        display_highlight_rows = list(temp.tail(10)['id'])
                    else:
                        display_highlight_rows = list(temp[(temp['yr'] == yr_val) & (temp['qtr'] == 5)]['id'])
                else:
                    if flag_list[0] in var_flags:
                        display_highlight_rows = list(temp.tail(10)['id'])
                    else:
                        display_highlight_rows = list(temp[(temp['yr'] == yr_val) & (temp['qtr'] == 5)]['id'])
        else:
            temp = display_data.copy()
            temp = temp.reset_index()
            temp['id'] = temp.index
            for yr in range(curryr, curryr + 10):
                if str(yr) in message:
                    display_highlight_rows = list(temp[(temp['yr'] == yr) & (temp['qtr'] == 5)]['id'])
                    break
            if "vacancy" in message:
                display_highlight_list = ['vac', 'rol vac']
            elif "market rent" in message:
                display_highlight_list = ['mrent', 'rol mrent']
            elif "effective rent" in message:
                display_highlight_list = ['merent', 'rol merent']

        
        # Get the data types and data formats for the data display
        type_dict_data, format_dict_data = get_types(sector_val)
        highlighting_display = get_style("full", display_data, dash_curryr, dash_second_five, display_highlight_list, display_highlight_rows)

        # Set the pixels neccesary to maintain the correct alignment of the shim view and the main data view, based on what type of historical series the selected sub has
        # Since not all subs have history going back to curryr - 5, the length of the main data set is not always consistent, thus the need for a variable pixel number
        len_display = len(display_data)

        if currqtr == 4:
            qtr_add = 0
        else:
            qtr_add = currqtr

        if len_display < 19 + qtr_add:
            if len_display == 19 + qtr_add - 1:
                padding = str(max((35 + (currqtr * 30)),0)) + 'px'
            else:
                padding = '35px'
        elif len_display == 19 + qtr_add:
            padding = padding = str(max((63 + (currqtr * 30)),0)) + 'px'
        spacing_style_shim = {'padding-left': '100px', 'display': 'block', 'padding-top': padding}

        # Set the key metrics and employment metrics display
        key_metrics = data.copy()
        key_metrics, key_emp = gen_metrics(key_metrics, drop_val, key_met_cols, key_emp_cols, yr_val)
        
        for col_name in list(key_metrics.columns):
            if "_" in col_name:
                col_name_replace = col_name.replace("_", " ")
                if "G mrent" in col_name_replace:
                    col_name_replace = col_name_replace.replace("G mrent", "Gmrent")
                key_metrics.rename(columns={col_name: col_name_replace}, inplace=True)
        for col_name in list(key_emp.columns):
            if "_" in col_name:
                col_name_replace = col_name.replace("_", " ")
                if "G mrent" in col_name_replace:
                    col_name_replace = col_name_replace.replace("G mrent", "Gmrent")
                key_emp.rename(columns={col_name: col_name_replace}, inplace=True)

        highlighting_metrics = get_style("metrics", key_metrics, dash_curryr, dash_second_five, key_metrics_highlight_list)
        highlighting_emp = get_style("metrics", key_emp, dash_curryr, dash_second_five, key_emp_highlight_list)
     
        title_met = "Key Metrics " + str(yr_val)
        title_emp = "Employment Metrics " + str(yr_val)
        type_dict_metrics, format_dict_metrics = get_types(sector_val)
        type_dict_emp, format_dict_emp = get_types(sector_val)

        # Retrieve the shim comments from the dataframe and display them to the user
        if sub_change == True or init_comment_cons is None:
            comment = data.copy()
            comment = comment[(comment['identity'] == drop_val) & (comment['yr'] == curryr + 1)]
            comment = comment.set_index('identity')
            cons_comment = comment['cons_comment'].loc[drop_val]
            avail_comment = comment['avail_comment'].loc[drop_val]
            rent_comment = comment['rent_comment'].loc[drop_val]
        elif sub_change == False:
            if init_comment_cons is not None:
                cons_comment = init_comment_cons
            if init_comment_avail is not None:
                avail_comment = init_comment_avail
            if init_comment_rent is not None:    
                rent_comment = init_comment_rent

        if cons_comment == "":
            cons_comment = 'Enter Cons Shim Note Here'
        if avail_comment == "":
            avail_comment = 'Enter Avail Shim Note Here'
        if rent_comment == "":
            rent_comment = 'Enter Rent Shim Note Here'


        # Get the submarket name and use it in the data table header
        temp = data.copy()
        sub_name = temp[temp['identity'] == drop_val].reset_index().loc[0]['subname']
        if sub_name != "N/A":
            data_title = drop_val + " "  + sub_name + " Submarket Data"
        else:
            data_title = "Submarket Data"

        # Output the main data set to a pickle file, to be read in and used by the scatter plot callback
        use_pickle("out", "scatter_data_" + sector_val, data, fileyr, currqtr, sector_val)

    return shim_data.to_dict('records'), [{'name': ['Insert Manual Fix', shim_data.columns[i]], 'id': shim_data.columns[i], 'type': type_dict_data[shim_data.columns[i]], 'format': format_dict_data[shim_data.columns[i]], 'editable': edit_dict[shim_data.columns[i]]} 
                            for i in range(3, len(shim_data.columns))], highlighting_shim, display_data.to_dict('records'), [{'name': [data_title, display_data.columns[i]], 'id': display_data.columns[i], 'type': type_dict_data[display_data.columns[i]], 'format': format_dict_data[display_data.columns[i]]} 
                            for i in range(0, len(display_data.columns))], highlighting_display, key_metrics.to_dict('records'), [{'name': [title_met, key_metrics.columns[i]], 'id': key_metrics.columns[i], 'type': type_dict_metrics[key_metrics.columns[i]], 'format': format_dict_metrics[key_metrics.columns[i]]} 
                            for i in range(0, len(key_metrics.columns))], highlighting_metrics, key_emp.to_dict('records'), [{'name': [title_emp, key_emp.columns[i]], 'id': key_emp.columns[i], 'type': type_dict_emp[key_emp.columns[i]], 'format': format_dict_emp[key_emp.columns[i]]} 
                            for i in range(0, len(key_emp.columns))], highlighting_emp, issue_description_noprev, issue_description_resolved, issue_description_unresolved, issue_description_new, issue_description_skipped, style_noprev, style_resolved, style_unresolved, style_new, style_skipped, go.Figure(data=data_vac), go.Figure(data=data_rent), spacing_style_shim, cons_comment, avail_comment, rent_comment

@forecast.callback([Output('vac_series_met', 'figure'),
                    Output('rent_series_met', 'figure'),
                    Output('vac_series_met', 'style'),
                    Output('rent_series_met', 'style'),
                    Output('metroll', 'data'),
                    Output('metroll', 'columns'),
                    Output('metroll', 'style_data_conditional'),
                    Output('metroll', 'page_action'),
                    Output('metroll', 'style_table'),
                    Output('metroll', 'fixed_rows'),
                    Output('met_rank', 'data'),
                    Output('met_rank', 'columns'),
                    Output('met_rank', 'style_data_conditional'),
                    Output('sub_rank', 'data'),
                    Output('sub_rank', 'columns'),
                    Output('sub_rank', 'style_data_conditional'),
                    Output('sub_rank_container', 'style'),
                    Output('met_rank_container', 'style'),
                    Output('rank_view_container', 'style'),
                    Output('roll_view', 'disabled'),
                    Output('first_roll', 'data')],
                   [Input('droproll', 'value'),
                    Input('roll_view', 'value'),
                    Input('rank_view', 'value'),
                    Input('sector', 'data'),
                    Input('tab_clicked', 'value')],
                    [State('store_orig_cols', 'data'),
                    State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data'),
                    State('dropman', 'value'),
                    State('first_roll', 'data')])
def output_rollup(roll_val, multi_view, year_val, sector_val, tab_clicked, orig_cols, curryr, currqtr, fileyr, success_init, drop_val, first_load):
    
    if sector_val is None or curryr is None or success_init == False or (tab_clicked != 'rollups' and first_load == False):
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
            if sector_val == "ret" or sector_val == "off":
                filt_cols += ['rolmerent']
            data_temp = data_temp[filt_cols]
            preview_data_temp = preview_data.copy()
            preview_data_temp = preview_data_temp[filt_cols]
            data_temp = data_temp[(data_temp['identity'] != drop_val) | (data_temp['forecast_tag'] == 0)]
            preview_data_temp = preview_data_temp[(preview_data_temp['identity'] == drop_val) & (preview_data_temp['forecast_tag'] != 0)]
            data_temp = data_temp.append(preview_data_temp)
            data_temp.sort_values(by=['subsector', 'metcode', 'subid', 'yr', 'qtr'], inplace=True)
            roll = data_temp.copy()
        else:
            roll = data.copy()

        # Call the rollup function to set the rollup data set, as well as the relevant vacancy and rent time series charts for the rollup tab
        if multi_view == False or roll_val[:2] == "US":
            rolled = rollup(roll, roll_val, curryr, currqtr, sector_val, "reg", False)
            if roll_val[:2] == "US":
                rolled = rolled[(rolled['identity_us'] == roll_val)]
            else:
                rolled = rolled[(rolled['metcode'] == roll_val[:2]) & (rolled['subsector'] == roll_val[2:])] 

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

        if rolled['merent'].isnull().all(axis=0) == True:
            rolled = rolled.drop(['merent', 'G_merent', 'gap', 'gap_chg'], axis=1)

        if roll_val[:2] == "US":
            data_vac_roll, data_rent_roll = sub_met_graphs(rolled, "nat", curryr, currqtr, fileyr, sector_val)
            vac_display_style = {'width': '100%', 'display': 'inline-block'}
            rent_display_style =  {'width': '100%', 'display': 'inline-block', 'padding-left': '50px'}
            sub_rank_display_style = {'display': 'none'}
            met_rank_display_style = {'display': 'none'}
            rank_view_display_style =  {'display': 'none'}
        else:
            if multi_view == False:
                data_vac_roll, data_rent_roll = sub_met_graphs(rolled, "met", curryr, currqtr, fileyr, sector_val)
                vac_display_style = {'width': '100%', 'display': 'inline-block'}
                rent_display_style =  {'width': '100%', 'display': 'inline-block', 'padding-left': '50px'}
                sub_rank_display_style = {'display': 'none'}
                met_rank_display_style = {'display': 'none'}
                rank_view_display_style =  {'display': 'none'}
            elif multi_view == True:
                sub_rank, met_rank = metro_sorts(rolled_rank, roll, roll_val, curryr, currqtr, sector_val, year_val)
                rolled = rolled[(rolled['metcode'] == roll_val[:2]) & (rolled['subsector'] == roll_val[2:])]
                vac_display_style = {'display': 'none'}
                rent_display_style = {'display': 'none'}
                sub_rank_display_style = {'display': 'inline-block', 'padding-left': '100px', 'width': '45%'}
                met_rank_display_style =  {'display': 'inline-block', 'padding-left': '250px', 'width': '50%'}
                rank_view_display_style = {'display': 'block', 'padding-left': '850px'}

                for x in list(sub_rank.columns):
                    sub_rank.rename(columns={x: x.replace('_', ' ')}, inplace=True)
                for x in list(met_rank.columns):
                    met_rank.rename(columns={x: x.replace('_', ' ')}, inplace=True)
                sub_rank = sub_rank.rename(columns={'G mrent': 'Gmrent', 'imp G mrent': 'imp Gmrent'})
                met_rank = met_rank.rename(columns={'G mrent': 'Gmrent', 'imp G mrent': 'imp Gmrent'})
                
                type_dict_rank, format_dict_rank = get_types(sector_val)
                highlighting_sub_rank = get_style("partial", sub_rank, curryr, currqtr, [], [])
                highlighting_met_rank = get_style("partial", met_rank, curryr, currqtr, [], [])
        
        rolled = rolled.drop(['cons_oob', 'vac_oob', 'vac_chg_oob',  'mrent_oob', 'G_mrent_oob', 'rol_mrent'], axis=1)
        rolled = rolled.rename(columns={'rolscon': 'rol cons', 'rolsvac': 'rol vac', 'vac_chg': 'vac chg', 'rolsvac_chg': 'rol vac chg', 'rolsabs': 'rol abs', 'gap_chg': 'gap chg', 'G_mrent': 'Gmrent', 'G_merent': 'Gmerent', 'grolsmre': 'rol Gmrent', 'grolsmer': 'rol Gmerent'})
        type_dict_roll, format_dict_roll = get_types(sector_val)
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

        first_load = False

        if multi_view == False or roll_val[:2] == "US":
            return go.Figure(data=data_vac_roll), go.Figure(data=data_rent_roll), vac_display_style, rent_display_style, rolled.to_dict('records'), [{'name': [data_title, rolled.columns[i]], 'id': rolled.columns[i], 'type': type_dict_roll[rolled.columns[i]], 'format': format_dict_roll[rolled.columns[i]]} 
            for i in range(0, len(rolled.columns))], highlighting_roll, 'none', {}, {}, no_update, no_update, no_update, no_update, no_update, no_update, sub_rank_display_style, met_rank_display_style, rank_view_display_style, disable_roll_view, first_load
        elif multi_view == True:
            return no_update, no_update, vac_display_style, rent_display_style, rolled.to_dict('records'), [{'name': [data_title, rolled.columns[i]], 'id': rolled.columns[i], 'type': type_dict_roll[rolled.columns[i]], 'format': format_dict_roll[rolled.columns[i]]} 
            for i in range(0, len(rolled.columns))], highlighting_roll, 'none', style_it, fixed_rows, met_rank.to_dict('records'), [{'name': ['Met Rank', met_rank.columns[i]], 'id': met_rank.columns[i], 'type': type_dict_rank[met_rank.columns[i]], 'format': format_dict_rank[met_rank.columns[i]]} 
                            for i in range(0, len(met_rank.columns))], highlighting_met_rank, sub_rank.to_dict('records'), [{'name': ['Sub Rank', sub_rank.columns[i]], 'id': sub_rank.columns[i], 'type': type_dict_rank[sub_rank.columns[i]], 'format': format_dict_rank[sub_rank.columns[i]]} 
                            for i in range(0, len(sub_rank.columns))], highlighting_sub_rank, sub_rank_display_style, met_rank_display_style, rank_view_display_style, disable_roll_view, first_load

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

        imp_switch = False
        if year_value != curryr and "implied" in init_xaxis_var:
            x_var = init_xaxis_var[8:]
            imp_switch = True
        if year_value != curryr and "implied" in init_yaxis_var:
            y_var = init_yaxis_var[8:]
            imp_switch = True

        if comp_value == 'c':
            lock = False
            placeholder = "Select:"
            x_var = init_xaxis_var
            if "rol" in init_yaxis_var:
                if init_xaxis_var != "G_mrent":
                    y_var = 'G_mrent'
                else:
                    y_var = "vac_chg"
            elif not imp_switch:
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

        if input_id != 'scatter_comparison_radios' and not imp_switch:
            x_var = no_update
            y_var = no_update

        return [{'label': i, 'value': i} for i in x_options_list], [{'label': i, 'value': i} for i in y_options_list], lock, placeholder, x_var, y_var

@forecast.callback([Output('scatter_graph', 'figure'),
                    Output('store_scatter_check', 'data'),
                    Output('scatter_graph', 'hoverData'),
                    Output('first_scatter', 'data')],
                    [Input('scatter_xaxis_var', 'value'),
                    Input('scatter_yaxis_var', 'value'),
                    Input('scatter_year_radios', 'value'),
                    Input('scatter_comparison_radios', 'value'),
                    Input('flags_only', 'value'),
                    Input('aggreg_level', 'value'),
                    Input('sector', 'data'),
                    Input('store_submit_button', 'data'),
                    Input('tab_clicked', 'value')],
                    [State('curryr', 'data'),
                    State('currqtr', 'data'),
                    State('fileyr', 'data'),
                    State('init_trigger', 'data'),
                    State('store_flag_cols', 'data'),
                    State('first_scatter', 'data')])
def produce_scatter_graph(xaxis_var, yaxis_var, year_value, comp_value, flags_only, aggreg_met, sector_val, submit_button, tab_val, curryr, currqtr, fileyr, success_init, flag_cols, first_scatter):

    if sector_val is None or success_init == False or curryr is None or (tab_val != "graphs" and first_scatter == False):
        raise PreventUpdate
    else:

        data = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)
        graph_data = data.copy()

        if comp_value == "r":
            match_list = {'rolscon': 'cons', 'rolsvac_chg': 'vac_chg', 'grolsmre': 'G_mrent', 'rolsgap_chg': 'gap_chg', 'rol-emp_chg': 'emp_chg', 'rol_off_emp_chg': 'off_emp_chg', 'rol_ind_emp_chg': 'ind_emp_chg'}
            xaxis_var = match_list[yaxis_var]
        
        # Tag subs as flagged or not flagged based on the xaxis var (or the yaxis var if the x is employment) for color purposes on scatter plot
        if aggreg_met == False:
            graph_data[flag_cols] = np.where((graph_data[flag_cols] != 0), 1, graph_data[flag_cols])

            def sum_flags(dataframe_in, flag_list, year_value):
                dataframe = dataframe_in.copy()
                dataframe['tot_flags'] = 0
                for flag_name in flag_list:
                    dataframe['tot_flags'] += dataframe[(dataframe['yr'] == year_value) & (dataframe['qtr'] == 5)].groupby('identity')[flag_name].transform('sum')

                return dataframe


            if comp_value == "c":
                if xaxis_var in ['cons', 'implied_cons']:
                    graph_data['c_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^c_flag*").sum(axis=1)
                    graph_data['flagged_status'] = np.where(graph_data['c_flag_tot'] > 0, 1, 0)
                    graph_data = graph_data.drop(['c_flag_tot'], axis=1) 
                elif xaxis_var in ['vac_chg', 'implied_vac_chg']:
                    graph_data['v_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^v_flag*").sum(axis=1)
                    graph_data['flagged_status'] = np.where(graph_data['v_flag_tot'] > 0, 1, 0)
                    graph_data = graph_data.drop(['v_flag_tot'], axis=1)
                elif xaxis_var in ['G_mrent', 'implied_G_mrent']:
                    graph_data['g_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^g_flag*").sum(axis=1)
                    graph_data['flagged_status'] = np.where(graph_data['g_flag_tot'] > 0, 1, 0)
                    graph_data = graph_data.drop(['g_flag_tot'], axis=1)
                elif xaxis_var in ['gap_chg', 'implied_gap_chg']:
                    graph_data['e_flag_tot'] = graph_data[(graph_data['yr'] == year_value) & (graph_data['qtr'] == 5)].filter(regex="^e_flag*").sum(axis=1)
                    graph_data['flagged_status'] = np.where(graph_data['e_flag_tot'] > 0, 1, 0)
                    graph_data = graph_data.drop(['e_flag_tot'], axis=1)
                elif xaxis_var in ['emp_chg', 'off_emp_chg', 'ind_emp_chg', 'avg_inc_chg', 'implied_emp_chg', 'implied_off_emp_chg', 'implied_ind_emp_chg', 'implied_avg_inc_chg']:
                    if yaxis_var in ['vac_chg', 'implied_vac_chg']:
                        graph_data = sum_flags(graph_data, ['v_flag_emp'], year_value)
                        graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                        graph_data = graph_data.drop(['tot_flags'], axis=1)
                    elif yaxis_var in ['G_mrent', 'implied_G_mrent']:
                        graph_data = sum_flags(graph_data, ['g_flag_emp'], year_value)
                        graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                        graph_data = graph_data.drop(['tot_flags'], axis=1)
                    elif yaxis_var in ["gap_chg", "implied_gap_chg"]:
                        graph_data= sum_flags(graph_data, ['e_flag_emp'], year_value)
                        graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                        graph_data = graph_data.drop(['tot_flags'], axis=1)
                    else:
                        graph_data = sum_flags(graph_data, ['v_flag_emp', 'g_flag_emp', 'e_flag_emp'], year_value)
                        graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                        graph_data = graph_data.drop(['tot_flags'], axis=1)
            
            elif comp_value == "r":
                if xaxis_var in ['cons', 'implied_cons']:
                    graph_data = sum_flags(graph_data, ['c_flag_rol'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                elif xaxis_var in ['vac_chg', 'implied_vac_chg']:
                    graph_data = sum_flags(graph_data, ['v_flag_rol', 'v_flag_improls', 'v_flag_switch'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                elif xaxis_var in ['G_mrent', 'implied_G_mrent']:
                    graph_data = sum_flags(graph_data, ['g_flag_rol', 'g_flag_improls'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                elif xaxis_var in ['gap_chg', 'implied_gap_chg']:
                    graph_data = sum_flags(graph_data, ['e_flag_rol', 'e_flag_improls', 'e_flag_rolvac'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)
                else:
                    graph_data = sum_flags(graph_data, ['v_flag_emp_rol', 'g_flag_emp_rol', 'e_flag_emp_rol'], year_value)
                    graph_data['flagged_status'] = np.where(graph_data['tot_flags'] > 0, 1, 0)
                    graph_data = graph_data.drop(['tot_flags'], axis=1)            

        if aggreg_met == True:
            graph_data = rollup(graph_data, "temp", curryr, currqtr, sector_val, "graph", False)
            graph_data['flagged_status'] = 0
            emp_data = data.copy()
            if sector_val == "apt" or sector_val == "ret":
                cols_to_keep = ['emp', 'emp_chg']
                if currqtr != 4:
                    cols_to_keep += ['implied_emp_chg']
            elif sector_val == "off":
                cols_to_keep = ['off_emp', 'off_emp_chg']
                if currqtr != 4:
                    cols_to_keep += ['implied_off_emp_chg']
            elif sector_val == "ind":
                cols_to_keep = ['ind_emp', 'ind_emp_chg']
                if currqtr != 4:
                    cols_to_keep += ['implied_ind_emp_chg']
            cols_to_keep += ['avg_inc', 'avg_inc_chg']
            if currqtr != 4:
                cols_to_keep += ['implied_avg_inc_chg']
            emp_data['identity_eco'] = emp_data['metcode'] + emp_data['yr'].astype(str) + emp_data['qtr'].astype(str)
            emp_data = emp_data.set_index('identity_eco')
            emp_data = emp_data[cols_to_keep]
            graph_data['identity_eco'] = graph_data['metcode'] + graph_data['yr'].astype(str) + graph_data['qtr'].astype(str)
            graph_data = graph_data.join(emp_data, on='identity_eco')

        scatter_graph, init_hover = filter_graph(graph_data, curryr, currqtr, year_value, xaxis_var, yaxis_var, sector_val, comp_value, flags_only, aggreg_met, False)
        
        scatter_layout = create_scatter_plot(scatter_graph, xaxis_var, yaxis_var, comp_value, aggreg_met)

        # Need to set this variable so that the succeeding callbacks will only fire once the intial load is done. 
        # This works because it makes the callbacks that use elements produced in this callback have an input that is linked to an output of this callback, ensuring that they will only be fired once this one completes
        scatter_check = True

        return scatter_layout, scatter_check, init_hover, False

@forecast.callback([Output('x_time_series', 'figure'),
                   Output('y_time_series', 'figure'),
                   Output('first_ts', 'data')],
                   [Input('scatter_graph', 'hoverData'),
                   Input('scatter_xaxis_var', 'value'),
                   Input('scatter_yaxis_var', 'value'),
                   Input('sector', 'data'),
                   Input('store_scatter_check', 'data'),
                   Input('init_trigger', 'data'),
                   Input('tab_clicked', 'value')],
                   [State('curryr', 'data'),
                   State('currqtr', 'data'),
                   State('fileyr', 'data'),
                   State('init_trigger', 'data'),
                   State('scatter_comparison_radios', 'value'),
                   State('aggreg_level', 'value'),
                   State('first_ts', 'data')])
def produce_timeseries(hoverData, xaxis_var, yaxis_var, sector_val, scatter_check, init_trigger, tab_val, curryr, currqtr, fileyr, success_init, comp_value, aggreg_met, first_ts):
    
    if sector_val is None or success_init == False or curryr is None or (tab_val != "graphs" and first_ts == False):
        raise PreventUpdate
    else:
        
        graph = use_pickle("in", "main_data_" + sector_val, False, fileyr, currqtr, sector_val)

        graph, temp = filter_graph(graph, curryr, currqtr, False, xaxis_var, yaxis_var, sector_val, comp_value, False, aggreg_met, True) 

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

    return fig_x, fig_y, False

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