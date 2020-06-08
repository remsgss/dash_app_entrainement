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

#-------------------------------------------------------------------------------
# IMPORT DONNEES
df = pd.read_csv('df_nb_connections_sites.csv',sep=";")
df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y')
features = df.columns.drop(['date','Dates Importantes'])
dates_importantes = df['Dates Importantes'].dropna().unique()

df1 = pd.read_csv('df_evolution_reservations.csv',sep=";")
df1['date'] = pd.to_datetime(df1['date'],format='%d/%m/%Y')
features1 = df1.columns.drop(['date'])

df2 = pd.read_csv('df_profil_100_euros.csv',sep=";")
features2 = df2.columns.drop(['id'])


#-------------------------------------------------------------------------------
# FONTIONS

# pour tracer les Dates Importantes
def graph1_2_liste_date_imp_grah(dates_imp,min_,max_):
    if not dates_imp:
        liste = []
    else:
        liste = [go.Scatter(
            x = [   df.loc[df['Dates Importantes']==dates_import,'date'].values[0].astype('M8[D]').astype('O'),
                    df.loc[df['Dates Importantes']==dates_import,'date'].values[0].astype('M8[D]').astype('O')   ],
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
app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

# layout = dict(
#     autosize=True,
#     automargin=True,
#     margin=dict(l=30, r=30, b=20, t=40),
#     hovermode="closest",
#     plot_bgcolor="#F9F9F9",
#     paper_bgcolor="#F9F9F9",
#     legend=dict(font=dict(size=10), orientation="h"),
#     #title="Satellite Overview",
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         style="light",
#         center=dict(lon=-78.05, lat=42.54),
#         zoom=7,
#     ),
# )


# app layout
app.layout = html.Div([

    html.H2("Suivi médias web",style={'text-align': 'center'}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')

],style={'padding':'10'})

index_page = html.Div([
    dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
],className="lien_bas_page")

# PAGE 1
page_1_layout = html.Div([

    # graphique 1
    html.Div(
        [
            html.Div(
                [

                    # html.P(children="Selectionner le média web :",className="control_label"),
                    # dcc.Dropdown(
                    #     id='g1_select_media_web',
                    #     options=[{'label': i, 'value': i} for i in features],
                    #     value=[features[0]],
                    #     multi=True,
                    #     className="dcc_control")

                    html.P("Selectionner une date importante :",className="control_label"),
                    dcc.Dropdown(
                        id='g1_2_select_dates_imp',
                        options=[{'label': i, 'value': i} for i in dates_importantes],
                        value=[],
                        multi=True,
                        className="dcc_control"),

                    html.Br(),
                    html.P("Selectionner une période :",className="control_label"),
                    dcc.DatePickerRange(
                        id='g1_2_my-date-picker-range',
                        min_date_allowed='03/01/2020',
                        max_date_allowed='05/30/2020',
                        initial_visible_month='03/01/2020',
                        start_date=datetime(2020, 3, 1).date(),
                        end_date=datetime(2020, 5,30 ).date(),
                        className="dcc_control"),

                    html.Br(),
                    html.Button(
                        id ='g1_2_submit-button',
                        n_clicks = 0,
                        children='Générer Graph')

                ],className="pretty_container",style={'width':'18%',"display": "inline-block","vertical-align":"top"}
            ),

            html.Div(
                [
                    dcc.Checklist(
                        id='g1_select_media_web',
                        options=[{'label': i, 'value': i} for i in features],
                        value=[features[0],features[1],features[2]],
                        labelStyle={'display': 'inline-block'},
                        className="dcc_control"
                    ),
                    dcc.Graph(id='graphique_1')
                ],className="pretty_container",style={'width':'76%',"display": "inline-block","vertical-align":"top"}
            )

        ]
    ),



    html.Div(
        [
            # graphique 2
            html.Div(
                [
                    dcc.Graph(id='graphique_2')
                ],className="pretty_container",style={'width':'58%',"display": "inline-block","vertical-align":"middle"}
            ),

            # graphique 3
            html.Div(
                [
                    html.P(children="Selectionner les informations que vous souhaitez sur les personnes ayant consultées l'offre 100€ selon :",className="control_label"),
                    dcc.Dropdown(
                        id='g3_select_profil_consultants',
                        options=[{'label': i, 'value': i} for i in features2],
                        value=[features2[0]],
                        multi=True,
                        className="dcc_control"),

                    dcc.Graph(id = 'graphiques_3')
                ]
                ,className="pretty_container"
                ,style={'width':'36%',"display": "inline-block","vertical-align":"middle"}
            )
        ]
    ),

    html.Div(
        [
            html.Div(id='page-1-content'),
            html.Br(),
            dcc.Link('Go to Page 2', href='/page-2'),
            html.Br(),
            dcc.Link('Go back to home', href='/',)
        ],className="lien_bas_page"
    )


])

# PAGE 2
page_2_layout = html.Div([

    html.Div(
        [
            html.Div(id='page-1-content'),
            html.Br(),
            dcc.Link('Go to Page 1', href='/page-1'),
            html.Br(),
            dcc.Link('Go back to home', href='/')
        ],className="lien_bas_page"
    )

])


#-------------------------------------------------------------------------------
# CALLBACKS
# @app.callback(
#     Output('graphique_1','figure'),
#     [Input('g1_select_media_web', 'value')])
@app.callback(
    Output('graphique_1','figure'),
    [Input('g1_2_submit-button','n_clicks'),
     Input('g1_select_media_web','value')],
    [State('g1_2_my-date-picker-range', 'start_date'),
     State('g1_2_my-date-picker-range', 'end_date'),
     State('g1_2_select_dates_imp','value')
     ])
def graph1_mise_a_jour(n_clicks,select_media_web,start_date,end_date,dates_imp):
    min_ = min(df.loc[:,[media for media in select_media_web]].min(axis=0))
    max_ = max(df.loc[:,[media for media in select_media_web]].max(axis=0))

    liste_date_imp = graph1_2_liste_date_imp_grah(dates_imp,min_,max_)

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
                title='Nombre de visites par média',
                xaxis= {'automargin': True, 'title': 'Date'},
                yaxis= {'automargin': True, 'title': 'Nombre de visites'},
                legend={'font':{'size':12}}
            ),

        }

    return(fig)

@app.callback(
    Output('graphique_2','figure'),
    [Input('g1_2_submit-button','n_clicks')],
    [State('g1_2_my-date-picker-range', 'start_date'),
     State('g1_2_my-date-picker-range', 'end_date'),
     State('g1_2_select_dates_imp','value')
     ])
def graph2_mise_a_jour(n_clicks,start_date,end_date,dates_imp):

    liste_date_imp = graph1_2_liste_date_imp_grah(dates_imp,0,1)

    figure={
        'data': [go.Scatter(
                    x=df1.loc[(df1['date']>= start_date) & (df1['date']<=end_date),'date'],
                    y=df1.loc[(df1['date']>= start_date) & (df1['date']<=end_date),nom_type_hebergement],
                    name=nom_type_hebergement,
                    mode='lines',
                    line=dict(width=0.5),
                    stackgroup='one' # define stack group
                    ) for nom_type_hebergement in features1 ]
                    +
                    liste_date_imp,

        'layout': go.Layout(
            title='Type de réservation au cours du temps (pct)',
            xaxis= {'title': 'date'},
            yaxis= {'title': 'Type d\'hébergement','range':[0, 1]}
        )
    }
    return figure

@app.callback(
    Output('graphiques_3','figure'),
    [Input('g3_select_profil_consultants', 'value')])
def graph3_infos_consultant_offre(profils_consultants):
    return  graph3_infos_consultant_offre_(profils_consultants)

#-------------------------------------------------------------------------------
# INDEX
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return page_1_layout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here


#-------------------------------------------------------------------------------
# LANCEMENT APPLI
if __name__ == '__main__':
    app.run_server()
