import dash
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import dash_daq as daq
from datetime import datetime

def get_app_layout():

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
        dcc.Store(id='identity_val'),
        dcc.Store(id='input_file'),
        dcc.Store(id='store_user'),
        dcc.Store(id='init_trigger'),
        dcc.Store(id='out_flag_trigger'),
        dcc.Store(id='skip_list_trigger'),
        dcc.Store(id='comment_trigger'),
        dcc.Store(id='roll_trigger'),
        dcc.Store(id='download_trigger'),
        dcc.Store(id='finalize_trigger'),
        dcc.Store(id='store_rol_close'),
        dcc.Store(id='store_flag_resolve'),
        dcc.Store(id='store_flag_unresolve'),
        dcc.Store(id='store_flag_new'),
        dcc.Store(id='store_flag_skips'),
        dcc.Store(id='sector'),
        dcc.ConfirmDialog(id='manual_message'),
            dcc.Tabs([
                dcc.Tab(label='Home', children=[
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
                        dbc.Alert(
                            html.P(id='logic_alert_text'),
                            id = "finalizer_logic_alert",
                            dismissable=True,
                            is_open=False,
                            fade=False,
                            color='danger',
                        )
                    ], style={'text-align': 'center', 'vertical-align': 'middle'}),
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
                                ], style={'display': 'block', 'padding-top': '85px'}),
                        html.Div([
                            dcc.Dropdown(
                                id='dropflag',
                                        ),
                            dash_table.DataTable(
                                id='flag_filt',
                                merge_duplicate_headers=True,
                                style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                page_action='none',
                                sort_action="native",
                                fixed_rows={'headers': True},
                                style_cell={'textAlign': 'center'},
                                style_cell_conditional=[
                                            {'if': {'column_id': 'Submarkets With Flag'},
                                                    'width': '50%'},
                                            {'if': {'column_id': 'Flag'},
                                                    'width': '50%'},
                                                    ],
                                                ),
                                ], style={'display': 'none'}, id='flag_container'),
                            ], style={'width': '35%', 'display': 'inline-block', 'padding-left': '30px', 'padding-top': '78px'}),
                    html.Div([
                        html.Div([
                            html.Div([  
                                dbc.Row(
                                dbc.Col(
                                    dbc.Button('Export Data',id='download-button',color='primary',block=True,size='sm'),
                                    width=20
                                        ),
                                    justify='center'
                                        ),
                                    ], style={'display': 'inline-block', 'padding': '20px'}),  
                            html.Div([
                                dbc.Row(
                                dbc.Col(
                                    dbc.Button('Export Flags',id='flag-button',color='warning',block=True,size='sm'),
                                    width=20
                                        ),
                                    justify='center'
                                        ),
                                    ], style={'display': 'inline-block', 'padding': '20px'}),
                            html.Div([
                                dbc.Row(
                                dbc.Col(
                                    dbc.Button('Finalize Forecast',id='finalize-button',color='success',block=True,size='sm'),
                                    width=20
                                        ),
                                    justify='center'
                                        ),
                                    ], style={'display': 'inline-block', 'padding': '20px'}),
                            html.Div([
                                dbc.Row(
                                dbc.Col(
                                    dbc.Button('Logout',id='logout-button',color='danger',block=True,size='sm'),
                                    width=20
                                        ),
                                    justify='center'
                                        ),
                                    ], style={'display': 'inline-block', 'padding': '20px'}),
                            ], style={'display': 'block', 'padding-left': '325px'}),
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
                                                {'if': {'column_id': '% Forecast Rows W Flag'},
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
                                                {'if': {'column_id': '% Forecast Rows W Flag'},
                                                        'width': '15%'},
                                                        ],
                                                        ),
                                        ], style={'display': 'inline-block', 'width': '48%', 'padding-left': '50px'}),
                                    ], style={'display': 'none'}, id='rank_table_container'),
                                ], style={'display': 'block'}),
                            ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-right': '30px', 'padding-left': '150px'}),
                        ]),
                dcc.Tab(label='Data', children=[
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='dropman',
                                        ),
                                ], style={'padding-left': '10px', 'width': '105%', 'display': 'block'}),
                        html.Div([
                            dcc.Textarea(
                                id='comment_cons',
                                style={'width': '105%', 'height': 60},
                                title="Cons Shim Note",
                                draggable=False,
                                spellCheck=False
                                ),
                                ], style={'padding-left': '10px', 'padding-top': '10px'}),
                        html.Div([
                            dcc.Textarea(
                                id='comment_avail',
                                style={'width': '105%', 'height': 60},
                                title="Avail Shim Note",
                                draggable=False,
                                spellCheck=False
                                ),
                                ], style={'padding-left': '10px', 'padding-top': '10px'}),
                        html.Div([
                            dcc.Textarea(
                                id='comment_rent',
                                style={'width': '105%', 'height': 60},
                                title="Rent Shim Note",
                                draggable=False,
                                spellCheck=False
                                ),
                                ], style={'padding-left': '10px', 'padding-top': '10px'}),
                        html.Div([
                                dash_table.DataTable(
                                    id='man_edits',
                                    style_header={'fontWeight': 'bold', 'textAlign': 'center'},
                                    merge_duplicate_headers=True,
                                    editable=True,
                                    ),
                                    ], style={'display': 'block'}, id='man_edits_container'),
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
                        ], style={'display': 'inline-block'}),
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
                                            {'if': {'column_id': 'rol vac chg'},
                                                    'width': '5%'},
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
                dcc.Tab(label='Graphs', children=[
                    html.Div([
                        html.Div([
                            dcc.Dropdown(
                                id='scatter_xaxis_var',
                                value='vac_chg'
                                        )
                                ], style={'width': '15%', 'display': 'inline-block'}),
                        html.Div([
                            dcc.Dropdown(
                                id='scatter_yaxis_var',
                                value='G_mrent'
                                        )
                                ], style={'width': '15%', 'display': 'inline-block', 'padding-left': '10px'}),
                        html.Div([
                            dcc.RadioItems(
                            id='scatter_comparison_radios',
                            options=[
                                        {'label': 'Current', 'value': 'c'},
                                        {'label': 'ROL', 'value': 'r'},
                                    ],
                                    value='c',
                            labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}), 
                                ], style={'width': '10%', 'display': 'inline-block', 'padding-left': '30px', 'vertical-align': 'top'}),
                        html.Div([
                            dcc.Checklist(
                                id='flags_only',
                                value=[],
                                options=[
                                            {'label': ' Flags Only', 'value': 'f'},
                                            ],
                                labelStyle={'display': 'block', 'margin': '0 10px 0 10px'}), 
                                ],  style={'padding-left': '10px', 'display': 'inline-block', 'vertical-align': 'top'}),
                            ], style={'padding': '10px 5px'}),
                    html.Div([
                        dcc.RadioItems(
                            id='scatter_year_radios',
                            labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}), 
                        ], style={'width': '100%', 'display': 'inline-block', 'padding-left': '30px'}),
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
                    ]),
                dcc.Tab(label='Rollups', children=[
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
                                                {'if': {'column_id': 'ask rent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'ask chg'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'rol ask chg'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'eff rent'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'eff chg'},
                                                'width': '3%'},
                                                {'if': {'column_id': 'rol eff chg'},
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
                                                    'width': '2%'},
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
                                                    'width': '2%'},
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
                            ], style={'width': '45%'}, id='met_rank_container'),
                        ], style={'display': 'block'}),
                    ]),
                ]),
            ])
        ])
        