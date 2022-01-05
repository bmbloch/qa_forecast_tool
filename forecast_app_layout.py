import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_daq as daq
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme
from datetime import datetime
import pandas as pd
import numpy as np
from collections import OrderedDict

def get_app_layout(curryr, currqtr, sector_val):

    if sector_val == "ind":
        global_dropdown = {
                            'Subsector':
                                        {'clearable': False, 'options': [{'label': i, 'value': i} for i in ['DW', 'F']]},
                             'Year': 
                                        {'clearable': False, 'options': [{'label': i, 'value': i} for i in [str(x) for x in np.arange(curryr, curryr + 10)]]}
                          }
    else:
        global_dropdown = {
                            'Year': 
                                    {'clearable': False, 'options': [{'label': i, 'value': i} for i in [str(x) for x in np.arange(curryr, curryr + 10)]]}
                          }

    global_shim = pd.DataFrame(columns=['Subsector', 'Year', 'Cons', 'Vac Chg', 'Gmrent', 'Gap Chg'])
    if sector_val == "ind":
        default_sect = 'DW'
        subsect_pres = 'dropdown'
    else:
        default_sect = sector_val.title()
        subsect_pres = ''
    global_shim = pd.DataFrame(OrderedDict([
                                            ('Subsector', [default_sect]),
                                            ('Year', [curryr]),
                                            ('Cons', [np.nan]),
                                            ('Vac Chg', [np.nan]),
                                            ('Gmrent', [np.nan]),
                                            ('Gap Chg', [np.nan])
                                            ]))
    global_columns = [
                        {'name': ['Global Shim', 'Subsector'], 'id': 'Subsector', 'type': 'text', 'format': Format(precision=0, scheme=Scheme.fixed), 'presentation': subsect_pres}, 
                        {'name': ['Global Shim', 'Year'], 'id': 'Year', 'type': 'numeric', 'format': Format(precision=0, scheme=Scheme.fixed), 'presentation': 'dropdown'},
                        {'name': ['Global Shim', 'Cons'], 'id': 'Cons', 'type': 'numeric', 'format': Format(group=","), 'editable': True}, 
                        {'name': ['Global Shim', 'Vac Chg'], 'id': 'Vac Chg', 'type': 'numeric', 'format': FormatTemplate.percentage(2), 'editable': True},
                        {'name': ['Global Shim', 'Gmrent'], 'id': 'Gmrent', 'type': 'numeric', 'format': FormatTemplate.percentage(2), 'editable': True}, 
                        {'name': ['Global Shim', 'Gap Chg'], 'id': 'Gap Chg', 'type': 'numeric', 'format': FormatTemplate.percentage(2), 'editable': True}  
                     ]

    sector_long = {'apt': 'Apartment', 'ind': 'Industrial', 'off': 'Office', 'ret': 'Retail'}
    navbar_title = sector_long[sector_val] + " " + "Forecast Review " + str(curryr) + "Q" + str(currqtr)
    navbar = dbc.Navbar(
    [ 
        html.Div([
            html.Div([
                html.P(navbar_title)
                ], style={'font-size': '24px', 'width': '400px', 'display': 'inline-block'}),
            html.Div([  
                dbc.Row(
                dbc.Col(
                    dbc.Button('Export Data',id='download-button',color='primary',block=True, size='sm'),
                    width=20
                        ),
                    justify='center'
                        ),
                    ], style={'display': 'inline-block', 'padding-left': '260px'}),  
            html.Div([
                dbc.Row(
                dbc.Col(
                    dbc.Button('Export Flags',id='flag-button',color='warning',block=True, size='sm'),
                    width=20
                        ),
                    justify='center'
                        ),
                    ], style={'display': 'inline-block', 'padding-left': '50px'}),
            html.Div([
                dbc.Row(
                dbc.Col(
                    dbc.Button('Finalize Forecast',id='finalize-button',color='success',block=True, size='sm'),
                    width=20
                        ),
                    justify='center'
                        ),
                    ], style={'display': 'inline-block', 'padding-left': '50px'}),
            html.Div([
                dbc.Row(
                dbc.Col(
                    dbc.Button('Logout',id='logout-button',color='danger',block=True, size='sm'),
                    width=20
                        ),
                    justify='center'
                        ),
                    ], style={'display': 'inline-block', 'padding-left': '50px'}),
        ], style={'padding-left': '750px'}),
    ],
    fixed='top'
    )

    return \
        html.Div([
            dcc.Location(id='home-url',pathname='/home'),
            html.Div([    
        html.Div(id='store_shim_finals', style={'display': 'none'}),
        dcc.Store(id='store_all_buttons', data=0),
        dcc.Store(id='store_submit_button', data=0),
        dcc.Store(id='store_preview_button', data=0),
        dcc.Store(id='store_init_flags', data=0),
        dcc.Store(id='store_scatter_check', data=0),
        dcc.Store(id='store_orig_cols'),
        dcc.Store(id='curryr'),
        dcc.Store(id='currqtr'),
        dcc.Store(id='fileyr'),
        dcc.Store(id='flag_list'),
        dcc.Store(id='p_skip_list'),
        dcc.Store(id='identity_val'),
        dcc.Store(id='input_file'),
        dcc.Store(id='store_user'),
        dcc.Store(id='init_trigger'),
        dcc.Store(id='download_trigger'),
        dcc.Store(id='finalize_trigger'),
        dcc.Store(id='out_flag_trigger'),
        dcc.Store(id='store_rol_close'),
        dcc.Store(id='store_flag_resolve'),
        dcc.Store(id='store_flag_unresolve'),
        dcc.Store(id='store_flag_new'),
        dcc.Store(id='store_flag_skips'),
        dcc.Store(id='first_update', data=True),
        dcc.Store(id='first_roll', data=True),
        dcc.Store(id='first_scatter', data=True),
        dcc.Store(id='first_ts', data=True),
        dcc.Store(id='flag_flow'),
        dcc.Store(id='store_flag_cols'),
        dcc.Store('has_flag'),
        dcc.Store(id='sector'),
        dcc.Store(id='global_trigger'),
        dcc.ConfirmDialog(id='manual_message'),
        dcc.ConfirmDialog(id='global_message'),
        html.Div([
            dbc.Alert(
                "Something is wrong with the input file. Double check and re-start the program",
                id = "file_load_alert",
                dismissable=True,
                is_open=False,
                fade=False,
                color='danger',
            )
        ], style={'text-align': 'center', 'vertical-align': 'middle'}),
        html.Div([
            dcc.ConfirmDialog(
            id='confirm_finalizer',
            displayed=False,
            message="Clicking OK will finalize the forecast and overwrite any existing finalized files previously created for this month"
            ),
        ]),
        html.Div([
            dbc.Alert(
                html.P(id='logic_alert_text'),
                id = "finalizer_logic_alert",
                dismissable=True,
                is_open=False,
                fade=False,
                color='danger',
            )
        ], style={'text-align': 'center', 'vertical-align': 'middle'}),
            dcc.Tabs(id='tab_clicked', value='home', children=[
                dcc.Tab(label='Home', value='home', children=[
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='dropsum',
                                        ),
                            dash_table.DataTable(
                                id='sum_table',
                                merge_duplicate_headers=True,
                                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                                ),
                            ], style={'display': 'none'}, id='sum_container'),
                        html.Div([
                            dash_table.DataTable(
                                id = 'countdown',
                                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                merge_duplicate_headers=True,
                                                    ),
                                ], style={'display': 'block', 'padding-top': '30px'}),
                        html.Div([
                            dcc.Dropdown(
                                id='dropflag',
                                        ),
                            dash_table.DataTable(
                                id='flag_filt',
                                merge_duplicate_headers=True,
                                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                page_action='none',
                                fixed_rows={'headers': True},
                                style_cell={'textAlign': 'center'},
                                style_cell_conditional=[
                                            {'if': {'column_id': 'Submarkets With Flag'},
                                                    'width': '50%'},
                                            {'if': {'column_id': 'Flag'},
                                                    'width': '50%'},
                                                    ],
                                                ),
                                ], style={'display': 'none'}, id='flag_filt_container'),
                        html.Div([
                            dash_table.DataTable(
                                id='nat_eco_table',
                                merge_duplicate_headers=True,
                                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                style_cell={'textAlign': 'center'},
                                                ),
                                ], style={'display': 'none'}, id='nat_eco_container'),
                            ], style={'width': '35%', 'display': 'inline-block', 'padding-left': '30px'}),
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Div([
                                    dash_table.DataTable(
                                        id='rank_table_met',
                                        merge_duplicate_headers=True,
                                        style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                        style_cell_conditional=[
                                                {'if': {'column_id': 'Subsector'},
                                                        'width': '15%'},
                                                {'if': {'column_id': 'Metcode'},
                                                        'width': '15%'},
                                                {'if': {'column_id': '% Fcast Rows W Flag'},
                                                        'width': '15%'},
                                                        ],
                                                        ),
                                        ], style={'display': 'inline-block', 'width': '48%'}),
                                html.Div([
                                    dash_table.DataTable(
                                        id='rank_table_sub',
                                        merge_duplicate_headers=True,
                                        style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                        style_cell_conditional=[
                                                {'if': {'column_id': 'Subsector'},
                                                        'width': '15%'},
                                                {'if': {'column_id': 'Metcode'},
                                                        'width': '15%'},
                                                {'if': {'column_id': 'Subid'},
                                                        'width': '15%'},
                                                {'if': {'column_id': '% Fcast Rows W Flag'},
                                                        'width': '15%'},
                                                        ],
                                                        ),
                                        ], style={'display': 'inline-block', 'width': '48%', 'padding-left': '50px'}),
                                    ], style={'display': 'none'}, id='rank_table_container'),
                                html.Div([
                                    html.Div([
                                        dash_table.DataTable(
                                            id='global_shim',
                                            data = global_shim.to_dict('records'), 
                                            columns = global_columns,
                                            dropdown=global_dropdown,
                                            editable=True,
                                            merge_duplicate_headers=True,
                                            style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                            style_cell_conditional=[
                                                    {'if': {'column_id': 'Subsector'},
                                                            'width': '15%', 'textAlign': 'left'},
                                                    {'if': {'column_id': 'Year'},
                                                            'width': '15%', 'textAlign': 'left'},
                                                    {'if': {'column_id': 'Cons'},
                                                            'width': '15%', 'textAlign': 'left'},
                                                    {'if': {'column_id': 'Vac Chg'},
                                                            'width': '15%', 'textAlign': 'left'},
                                                    {'if': {'column_id': 'Gmrent'},
                                                            'width': '15%', 'textAlign': 'left'},
                                                    {'if': {'column_id': 'Gap Chg'},
                                                            'width': '15%', 'textAlign': 'left'},
                                                            ],
                                                            ),
                                            ], style={'display': 'none'}, id='global_shim_container'),
                                    html.Div([ 
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Button('Submit Global',id='global_submit_button',color='success',block=True,size='sm'),
                                                    width=20
                                                    ),
                                            justify='center'
                                                    ),
                                            ], style={'display': 'none'}, id='global_submit_container'),
                                    html.Div([ 
                                        dbc.Row(
                                            dbc.Col(
                                                dbc.Button('Preview Global',id='global_preview_button',color='warning',block=True,size='sm'),
                                                    width=20
                                                    ),
                                            justify='center'
                                                    ),
                                            ], style={'display': 'none'}, id='global_preview_container'),
                                    ], style={'display': 'block'}),
                                ], style={'display': 'block'}),
                            ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-right': '30px', 'padding-left': '150px'}),
                        ]),
                dcc.Tab(label='Data', value='data', children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                dcc.Dropdown(
                                    id='dropman',
                                            ),
                                    ], style={'padding-left': '10px', 'width': '60%', 'display': 'inline-block'}),
                            html.Div([
                                dcc.Checklist(
                                    id='show_skips',
                                    value=["N"],
                                    options=[
                                                {'label': ' Show Skips', 'value': 'Y'},
                                                ],
                                    labelStyle={'display': 'block'}), 
                                ], id='show_skips_container'),
                        ], style={'display': 'block'}),
                        html.Div([
                            dcc.Textarea(
                                id='comment_cons',
                                style={'width': '100%', 'height': 60},
                                title="Cons Shim Note",
                                draggable=False,
                                spellCheck=False
                                ),
                                ], style={'padding-left': '10px', 'padding-top': '10px'}),
                        html.Div([
                            dcc.Textarea(
                                id='comment_avail',
                                style={'width': '100%', 'height': 60},
                                title="Avail Shim Note",
                                draggable=False,
                                spellCheck=False
                                ),
                                ], style={'padding-left': '10px', 'padding-top': '10px'}),
                        html.Div([
                            dcc.Textarea(
                                id='comment_rent',
                                style={'width': '100%', 'height': 60},
                                title="Rent Shim Note",
                                draggable=False,
                                spellCheck=False
                                ),
                                ], style={'padding-left': '10px', 'padding-top': '10px'}),
                        html.Div([
                            dcc.RadioItems(
                                id='process_subsequent',
                                value = 'c',
                                options=[
                                            {'label': 'Curr', 'value': 'c'},
                                            {'label': 'ROL', 'value': 'r'},
                                        ],
                                labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}
                                            ), 
                                ], style={'display': 'block'}, id='process_subsequent_container'),
                        html.Div([
                                dash_table.DataTable(
                                    id='man_edits',
                                    style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                    merge_duplicate_headers=True,
                                    editable=True,
                                    ),
                                    ], style={'display': 'block', 'padding-left': '30px'}, id='man_edits_container'),
                        html.Div([
                            html.Div([ 
                                dbc.Row(
                                    dbc.Col(
                                        dbc.Button('Submit Fix',id='submit-button',color='success',block=True,size='sm'),
                                            width=20
                                            ),
                                    justify='center'
                                            ),
                                    ], style={'display': 'inline-block', 'padding-left': '55px', 'padding-top': '5px'}),
                            html.Div([ 
                                dbc.Row(
                                    dbc.Col(
                                        dbc.Button('Preview Fix',id='preview-button',color='warning',block=True,size='sm'),
                                            width=20
                                            ),
                                    justify='center'
                                            ),
                                    ], style={'display': 'inline-block', 'padding-left': '45px', 'padding-top': '5px'}),
                            ], style={'display': 'block'}, id='button_container'),
                        ], style={'display': 'inline-block', 'width': '15%'}),
                        html.Div([
                                html.Div([
                                    html.Div([
                                        html.P(id='flag_description_noprev')
                                            ], style={'display': 'none'}, id='noprev_container'),
                                    html.Div([
                                        html.P(id='flag_description_resolved')
                                            ], style={'display': 'none'}, id='resolved_container'),
                                    html.Div([
                                        html.P(id='flag_description_unresolved')
                                            ], style={'display': 'none'}, id='unresolved_container'),
                                    html.Div([
                                        html.P(id='flag_description_new')
                                            ], style={'display': 'none'}, id='new_container'),
                                    html.Div([
                                        html.P(id='flag_description_skipped')
                                            ], style={'display': 'none'}, id='skipped_container'),
                                ], style={'display': 'block'}, id='flags_container'),
                                html.Div([
                                    dash_table.DataTable(
                                        id='data_view',
                                        style_header={'fontWeight': 'bold', 'textAlign': 'center', 'whiteSpace': 'normal'},
                                        merge_duplicate_headers=True,
                                        style_cell_conditional=[
                                            {'if': {'column_id': 'yr'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'qtr'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'inv'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'cons'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'rol cons'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'vac'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'vac chg'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'rol vac'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'rol vac chg'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'occ'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'avail'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'abs'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'rol abs'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'mrent'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'Gmrent'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'rol Gmrent'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'merent'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'Gmerent'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'rol Gmerent'},
                                                    'width': '3%'},
                                            {'if': {'column_id': ''},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'gap'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'gap chg'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'rol gap chg'},
                                                    'width': '4%'},
                                            {'if': {'column_id': 'h'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'e'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 't'},
                                                    'width': '3%'},
                                                    ],
                                                        ),
                                        ], style={'display': 'block'}, id='man_data_container'),
                                html.Div([
                                    dcc.RadioItems(
                                        id='key_yr_radios',
                                        labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}), 
                                        ], style={'padding-top': '5px', 'display': 'inline-block', 'padding-left': '400px'}),
                            ], style={'display': 'inline-block', 'width': '80%', 'padding-left': '50px', 'vertical-align': 'top'}),
                        html.Div([
                            html.Div([
                                html.Div([
                                    dash_table.DataTable(
                                        id='key_metrics',
                                        merge_duplicate_headers=True,
                                        style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                                    ),
                                        ], style={'display': 'inline-block', 'padding-left': '30px', 'width': '94%'}),
                                html.Div([
                                    dcc.RadioItems(
                                        id='key_met_radios',
                                        value = 'v',
                                        options=[
                                                    {'label': 'cons', 'value': 'c'},
                                                    {'label': 'vac', 'value': 'v'},
                                                    {'label': 'mrent', 'value': 'g'},
                                                    {'label': 'erent', 'value': 'e'},
                                                ],
                                        labelStyle={'display': 'block', 'margin': '0 10px 0 10px'}), 
                                        ], style={'display': 'inline-block', 'width': '6%', 'padding-left': '5px', 'vertical-align': 'bottom'}),
                                ], style={'display': 'block'}),
                        ], style={'display': 'block'}),
                        html.Div([
                            dash_table.DataTable(
                            id='key_emp',
                            merge_duplicate_headers=True,
                            style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                            ),
                                ], style={'display': 'block', 'padding-top': '20px', 'padding-left': '30px', 'width': '95%'}),
                            html.Div([
                                html.Div([
                                    dcc.Graph(
                                        id='vac-series',
                                        config={'displayModeBar': False}
                                            )
                                        ], style={'width': '49%', 'display': 'inline-block'}),
                                html.Div([
                                    dcc.Graph(
                                        id='rent-series',
                                        config={'displayModeBar': False}
                                            )
                                        ], style={'width': '49%', 'display': 'inline-block', 'padding-left': '50px'}),
                                    ], style={'display': 'block'}),
                            ]),
                dcc.Tab(label='Graphs', value='graphs', children=[
                    html.Div([
                        html.Div([
                            html.Div([
                                dcc.Dropdown(
                                    id='scatter_xaxis_var',
                                    value='vac_chg'
                                            )
                                    ], style={'width': '14%', 'display': 'inline-block', 'padding-left': '75px'}),
                            html.Div([
                                dcc.Dropdown(
                                    id='scatter_yaxis_var',
                                    value='G_mrent'
                                            )
                                    ], style={'width': '11%', 'display': 'inline-block', 'padding-left': '10px'}),
                            html.Div([
                                dcc.RadioItems(
                                id='scatter_comparison_radios',
                                options=[
                                            {'label': 'Current', 'value': 'c'},
                                            {'label': 'ROL', 'value': 'r'},
                                        ],
                                        value='c',
                                labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}), 
                                    ], style={'width': '10%', 'display': 'inline-block', 'padding-left': '10px', 'vertical-align': 'top'}),
                            html.Div([
                                dcc.Checklist(
                                    id='flags_only',
                                    value=[],
                                    options=[
                                                {'label': ' Flags Only', 'value': 'f'},
                                                ],
                                    labelStyle={'display': 'block', 'margin': '0 10px 0 10px'}), 
                                    ],  style={'display': 'inline-block', 'vertical-align': 'top'}),
                            html.Div([
                                    daq.ToggleSwitch(
                                        id='aggreg_level',
                                        label=['Sub', 'Met'],
                                        style={'width': '5px', 'margin': 'auto'},
                                        value=False,
                                        ),
                                    ], style={'padding-left': '75px', 'display': 'inline-block', 'vertical-align': 'top'}),
                            ], style={'padding-left': '10px', 'width': '100%'}),
                        html.Div([
                            dcc.RadioItems(
                                id='scatter_year_radios',
                                labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}), 
                            ], style={'width': '100%', 'display': 'block', 'padding-left': '130px'}),
                        ]),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='scatter_graph',
                                    )
                            ], style={'width': '49%', 'display': 'inline-block', 'padding-left': '30px'}),
                        html.Div([
                            html.Div([
                                dcc.Graph(
                                    id='x_time_series',
                                    config={'displayModeBar': False}
                                        ),
                                    ]),
                            html.Div([
                                dcc.Graph(
                                    id='y_time_series',
                                    config={'displayModeBar': False}
                                        ),
                                ], style={'padding-top': '25px'}),
                            ], style={'display': 'inline-block', 'width': '49%', 'padding-left': '150px'}),   
                        ], style={'display': 'block'}),
                    ]),
                dcc.Tab(label='Rollups', value='rollups', children=[
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='droproll',
                                ),
                        ], style={'width': '50%', 'padding-left': '10px', 'display': 'inline-block'}),
                        html.Div([
                            daq.ToggleSwitch(
                                id='roll_view',
                                label=['Single', 'Multi'],
                                style={'width': '5px', 'margin': 'auto'},
                                value=False,
                                ),
                            ], style={'width': '20%', 'padding-left': '10px', 'padding-top': '5px', 'display': 'inline-block', 'vertical-align': 'top'}),
                        html.Div([
                            dash_table.DataTable(
                                id='metroll',
                                style_header={'fontWeight': 'bold', 'textAlign': 'center', 'whiteSpace': 'normal'},
                                merge_duplicate_headers=True,
                                style_cell_conditional=[                
                                                {'if': {'column_id': 'subsector'},
                                                'width': '5%'},
                                                {'if': {'column_id': 'metcode'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'subid'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'yr'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'qtr'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'inv'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'cons'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'rol cons'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'vac'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'vac chg'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'rol vac'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'rol vac chg'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'abs'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'rol abs'},
                                                'width': '4%'},
                                                {'if': {'column_id': 'mrent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'Gmrent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'rol Gmrent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'merent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'Gmerent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'rol Gmerent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'gap'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'gap chg'},
                                                'width': '3%'},
                                                ],
                                ),
                            ], style={'width': '98%', 'padding-left': '10px', 'display': 'block'}),
                    ], style={'display': 'block'}),
                    html.Div([
                        html.Div([
                            dcc.Graph(
                                id='vac_series_met',
                                config={'displayModeBar': False}
                                    )
                                ],style={'width': '49%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Graph(
                                id='rent_series_met',
                                config={'displayModeBar': False}
                                    )
                                ],style={'width': '49%', 'display': 'inline-block', 'padding-left': '50px'}),
                        ], style={'display': 'block'}),
                    html.Div([
                        dcc.RadioItems(
                            id='rank_view',
                            value='1',
                            labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}),
                        ], style={'width': '15%'}, id='rank_view_container'),
                    html.Div([
                        html.Div([
                           dash_table.DataTable(
                                id='sub_rank',
                                merge_duplicate_headers=True,
                                style_header={'fontWeight': 'bold', 'textAlign': 'center', 'whiteSpace': 'normal'},
                                style_cell_conditional =[
                                            {'if': {'column_id': 'metcode'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'subid'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'cons'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'vac chg'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'abs'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'Gmrent'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'gap chg'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'emp chg'},
                                                    'width': '3%'},
                                            {'if': {'column_id': 'imp cons'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'imp vac chg'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'imp abs'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'imp Gmrent'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'imp gap chg'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'imp emp chg'},
                                                    'width': '2%'},
                                                    ],
                                sort_action="native",
                                filter_action="native",
                                ),
                            ], style={'width': '45%'}, id='sub_rank_container'),
                        html.Div([
                            dash_table.DataTable(
                                id='met_rank',
                                merge_duplicate_headers=True,
                                style_header={'fontWeight': 'bold', 'textAlign': 'center', 'whiteSpace': 'normal'},
                                style_cell_conditional =[
                                            {'if': {'column_id': 'metcode'},
                                                    'width': '8%'},
                                            {'if': {'column_id': 'cons'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'vac chg'},
                                                    'width': '6%'},
                                            {'if': {'column_id': 'abs'},
                                                    'width': '2%'},
                                            {'if': {'column_id': 'Gmrent'},
                                                    'width': '7%'},
                                            {'if': {'column_id': 'gap chg'},
                                                    'width': '6%'},
                                            {'if': {'column_id': 'emp chg'},
                                                    'width': '8%'},
                                            {'if': {'column_id': 'imp cons'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'imp vac chg'},
                                                    'width': '7%'},
                                            {'if': {'column_id': 'imp abs'},
                                                    'width': '5%'},
                                            {'if': {'column_id': 'imp Gmrent'},
                                                    'width': '7%'},
                                            {'if': {'column_id': 'imp gap chg'},
                                                    'width': '6%'},
                                            {'if': {'column_id': 'imp emp chg'},
                                                    'width': '8%'},
                                                    ],
                                sort_action="native",
                                filter_action="native",
                                ),
                            ], style={'width': '50%'}, id='met_rank_container'),
                        ], style={'display': 'block'}),
                    ]),
                ], style={'padding-top': '50px'}),
            ]),
            html.Div([navbar]),
        ])
        