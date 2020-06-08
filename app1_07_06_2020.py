import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime

USERNAME_PASSWORD_PAIRS = [['6fois7','mdp']]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#-------------------------------------------------------------------------------
# IMPORT DONNEES
df = pd.read_csv('df_nb_connections_sites.csv',sep=";")
df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y')
features = df.columns.drop(['date','date_importante'])
dates_importantes = df['date_importante'].dropna().unique()

df1 = pd.read_csv('df_evolution_reservations.csv',sep=";")
features1 = df1.columns.drop(['date'])

df2 = pd.read_csv('df_profil_100_euros.csv',sep=";")
features2 = df2.columns.drop(['id'])


#-------------------------------------------------------------------------------
# FONTIONS

# pour tracer les dates importantes
def graph1_liste_date_imp_grah(dates_imp,min_,max_):
    if not dates_imp:
        liste = []
    else:
        liste = [go.Scatter(
            x = [   df.loc[df['date_importante']==dates_import,'date'].values[0].astype('M8[D]').astype('O'),
                    df.loc[df['date_importante']==dates_import,'date'].values[0].astype('M8[D]').astype('O')   ],
            y = [min_,max_],
            name=dates_import,
            mode='lines',
            marker={
                'color': 'RGB(0,0,0)'
            }
        )for dates_import in dates_imp]
    return liste

# pour tracer un graph selon  le type du consultant
def graph3_infos_consultant_offre_(profils_consultants):
    if len(profils_consultants)==1:
        profil_ = profils_consultants[0]
        if df2[profil_].dtypes == 'O':
            count_y = df2.loc[:,profil_].value_counts()
            fig={
                'data': [go.Pie(
                        values=count_y,
                        labels=count_y.index.values,
                        hole=.4
                        )],
                'layout':go.Layout(title='Informations selon la variable : {}'.format(profil_))
            }
        elif df2[profil_].dtypes == 'int64':
            fig={
                'data':[go.Histogram(x=df2[profil_])],
                'layout':go.Layout(title='Informations selon la variable : {}'.format(profil_))
            }
    elif len(profils_consultants)==2 and df2.loc[:,profils_consultants].dtypes.tolist().count('int64') == 2:
        fig={
            'data':[go.Scatter(
                        x=df2[profils_consultants[0]],
                        y=df2[profils_consultants[1]],
                        mode='markers'
                    )],
            'layout':go.Layout(title='Informations selon la variable '+profils_consultants[0]+' et la variable '+profils_consultants[1])
        }
    elif len(profils_consultants)==2 and df2.loc[:,profils_consultants].dtypes.tolist().count('int64') == 1:
        if df2[profils_consultants[0]].dtypes == 'int64':
            x_ = df2[profils_consultants[1]].unique()
            y_ = df2.groupby([profils_consultants[1]]).mean()[profils_consultants[0]]
        else:
            x_ = df2[profils_consultants[0]].unique()
            y_ = df2.groupby([profils_consultants[0]]).mean()[profils_consultants[1]]
        fig = {
            'data':[go.Bar(
                        x=x_, y=y_
                    )],
            'layout':go.Layout(title='Informations selon la variable '+profils_consultants[0]+' et la variable '+profils_consultants[1])
        }
    elif 'int64' not in  df2.loc[:,profils_consultants].dtypes.tolist():
        fig = px.sunburst(df2, path=profils_consultants)
    else:
        fig = {}

    return fig


#-------------------------------------------------------------------------------
# APPLICATION
# ouverture de l'appli
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

# app layout
app.layout = html.Div([

    html.H1("Dashboard suivi médias web",style={'text-align': 'center'}),

    # graphique 1
    html.Div([
        html.Div([
            html.Label(children="Selectionner le média web :",style={'fontsize':'12'}),
            dcc.Dropdown(
                id='g1_select_media_web',
                options=[{'label': i, 'value': i} for i in features],
                value=[features[0]],
                multi=True,
                style={'margin':'1%','fontsize':'8'}
            ),
        ],style={'width':'25%','display':'inline-block','verticalAlign':'top','margin':'1%'}),

        html.Div([
            html.Label("Selectionner une période :",style={'fontsize':'12'}),
            dcc.DatePickerRange(
                id='g1_my-date-picker-range',
                min_date_allowed='03/01/2020',
                max_date_allowed='05/30/2020',
                initial_visible_month='03/01/2020',
                start_date=datetime(2020, 3, 1).date(),
                end_date=datetime(2020, 5,30 ).date(),
                style={'fontsize':'12','margin':'1%'}
            ),
        ],style={'width':'25%','display':'inline-block','verticalAlign':'top','margin':'1%'}),

        html.Div([
            html.Label("Selectionner une date importante :",style={'fontsize':'12'}),
            dcc.Dropdown(
                id='g1_select_dates_imp',
                options=[{'label': i, 'value': i} for i in dates_importantes],
                value=[],
                multi=True,
                style={'margin':'10','fontsize':'8'}
            )
        ],style={'width':'20%','display':'inline-block','margin':'1%'}),

        html.Div([
            html.Button(
                id ='g1_submit-button',
                n_clicks = 0,
                children='Générer Graph',
                style={'fontsize':'12'}
            )
        ],style={'width':'15%','display':'inline-block','margin':'1%'}),

        html.Div([
            dcc.Graph(id='graphique_1')
        ],style={'width':'90%','margin':'10'})

    ],style={'width':'90%','margin':'1%'}),


    # graphique 2
    html.Div([

        html.Div([
            dcc.Graph(
                id='graphique_2',
                figure={
                    'data': [go.Scatter(
                                x=df1.loc[:,'date'],
                                y=df1.loc[:,nom_type_hebergement],
                                name=nom_type_hebergement,
                                mode='lines',
                                line=dict(width=0.5),
                                stackgroup='one' # define stack group
                                ) for nom_type_hebergement in features1 ]
                                +
                                [go.Scatter(
                                    x = ['16/03/2020','16/03/2020'],
                                    y = [0,1],
                                    name='annonce confinement',
                                    mode='lines',
                                    marker={
                                        'color': 'RGB(0,0,0)'
                                    }
                                )]
                                +
                                [go.Scatter(
                                    x = ['07/05/2020','07/05/2020'],
                                    y = [0,1],
                                    name='annonce déconfinement',
                                    mode='lines',
                                    marker={
                                        'color': 'RGB(0,0,0)'
                                    }
                                )],

                    'layout': go.Layout(
                        title='Type de réservation au cours du temps (pct)',
                        xaxis= {'title': 'date'},
                        yaxis= {'title': 'Type d\'hébergement','range':[0, 1]}
                    )
                }
            )
        ],style={'margin':'1%'})


    ],style={'width':'58%','margin':'1%','display':'inline-block','verticalAlign':'bottom'}),

    # graphique 3
    html.Div([

        html.Div([
            html.Label(children="Selectionner les informations que vous souhaitez sur les personnes ayant consultées l'offre selon :",style={'fontsize':'12'}),
            dcc.Dropdown(
                id='g3_select_profil_consultants',
                options=[{'label': i, 'value': i} for i in features2],
                value=[features2[0]],
                multi=True,
                style={'margin':'10','fontsize':'12'}
            ),
        ],style={'width':'80%','margin':'1%'}),

        html.Div([
            dcc.Graph(
                id = 'graphiques_3'
            )
        ],style={'margin':'1%'})

    ],style={'width':'38%','margin':'1%','display':'inline-block','float': 'right','verticalAlign':'bottom'})

],style={'padding':'10'})


#-------------------------------------------------------------------------------
# CALLBACKS
@app.callback(
    Output('graphique_1','figure'),
    [Input('g1_submit-button','n_clicks')],
    [State('g1_select_media_web', 'value'),
     State('g1_my-date-picker-range', 'start_date'),
     State('g1_my-date-picker-range', 'end_date'),
     State('g1_select_dates_imp','value')
     ])
def graph1_mise_a_jour_graph(n_clicks,select_media_web,start_date,end_date,dates_imp):
    min_ = min(df.loc[:,[media for media in select_media_web]].min(axis=0))
    max_ = max(df.loc[:,[media for media in select_media_web]].max(axis=0))

    liste_date_imp = graph1_liste_date_imp_grah(dates_imp,min_,max_)

    fig = {
            'data': [go.Scatter(
                        x=df.loc[(df['date']>= start_date) & (df['date']<=end_date),'date'],
                        y=df.loc[(df['date']>= start_date) & (df['date']<=end_date),names_media_web],
                        mode = 'markers+lines',
                        name = names_media_web,
                        marker={
                            'size': 12,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                    ) for names_media_web in select_media_web]
                    + liste_date_imp,

            'layout': go.Layout(
                title='Volume visites sur les médias',
                xaxis= {'automargin': True, 'title': 'date'},
                yaxis= {'automargin': True, 'title': 'Nombre de visites'},
                legend={'font':{'size':12}}
            ),

        }
    return(fig)

@app.callback(
    Output('graphiques_3','figure'),
    [Input('g3_select_profil_consultants', 'value')])
def graph3_infos_consultant_offre(profils_consultants):
    return  graph3_infos_consultant_offre_(profils_consultants)


#-------------------------------------------------------------------------------
# LANCEMENT APPLI
if __name__ == '__main__':
    app.run_server()
