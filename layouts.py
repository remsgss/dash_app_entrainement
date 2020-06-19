import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_auth
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output, State
import pandas as pd
from datetime import datetime
import dash_table as dasht

from wordcloud import WordCloud, STOPWORDS
import glob
import datetime as dt
from ast import literal_eval
import os

##################################################################################################
##################################################################################################
######################################### IMPORT DONNEES #########################################

df = pd.read_csv('./data/df_nb_connections_sites.csv',sep=";")
df['date'] = pd.to_datetime(df['date'],format='%d/%m/%Y')
features = df.columns.drop(['date','Dates Importantes'])
dates_importantes = df['Dates Importantes'].dropna().unique()

df1 = pd.read_csv('./data/df_evolution_reservations.csv',sep=";")
df1['date'] = pd.to_datetime(df1['date'],format='%d/%m/%Y')
features1 = df1.columns.drop(['date'])

df2 = pd.read_csv('./data/df_profil_100_euros.csv',sep=";")
features2 = df2.columns.drop(['id'])

# import extractions tweets
username = 'LesCharentes'

fichiers_chemin_donnees = glob.glob("./data/*.xlsx")
print(fichiers_chemin_donnees,'\n')
fichiers_interet = [str for str in fichiers_chemin_donnees if str.startswith('./data/df_tweets_'+username)]
print(fichiers_interet,'\n')
dates_fichiers_interet = [str.strip('./data/df_tweets_'+username).strip('.xlsx') for str in fichiers_interet]
print(dates_fichiers_interet,'\n')
dates_fichiers_interet = [dt.datetime.strptime(date, "%b-%d-%Y").date() for date in dates_fichiers_interet]
print(dates_fichiers_interet,'\n')
max_date = max(dates_fichiers_interet)
del(fichiers_chemin_donnees,fichiers_interet,dates_fichiers_interet)

df_tweets = pd.read_excel('./data/df_tweets_'+username+'_'+max_date.strftime("%b-%d-%Y")+'.xlsx')
df_tweets.loc[:,'hashtags'] = df_tweets.loc[:,'hashtags'].apply(lambda x: literal_eval(x))
nb_retweet_hashtags = pd.read_excel('./data/nb_retweets_'+username+'_'+max_date.strftime("%b-%d-%Y")+'.xlsx')


nom_page='tourismecharentes'
fichiers_chemin_donnees = glob.glob("./data/*.csv")
fichiers_interet = [str for str in fichiers_chemin_donnees if str.startswith('./data/extraction_fb_'+nom_page+'_preprocesse_')]
dates_fichiers_interet = [str.strip('./data/extraction_fb_'+nom_page+'_preprocesse_').strip('.csv') for str in fichiers_interet]
dates_fichiers_interet = [dt.datetime.strptime(date, "%b-%d-%Y").date() for date in dates_fichiers_interet]
max_date = max(dates_fichiers_interet)

df_fb = pd.read_csv('.\\data\\extraction_fb_'+nom_page+'_preprocesse_'+max_date.strftime("%b-%d-%Y")+'.csv')

text_p1_g3 = '''
    Le graphique ci dessous permet d'illustrer les profils des utilisateurs ayant consulté **l'offre de 100€** selon les modalités de différentes variables.

    Choisissez les variables :
'''

text_p2_twitter = '''
    On s'intéresse aux nombres de retweets selon les hashtags.

    On peut choisir d'analyser les hashtags uniquement s'ils ont été utilisés un nombre minimum de fois en considérant le nombre minimum dnas l'encadré ci dessous.
'''

####################################################################################################
####################################################################################################
# PAGE 1
####################################################################################################
####################################################################################################

page_1_layout = html.Div([

        html.H3(children="Consultations Site Web",
                style={"text-align":"left","margin-left":"30px"}),

        dbc.Col(
            html.Div(
                [
                    # graphique 1
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P("Selectionner une date importante :",className="control_label"),
                                    dcc.Dropdown(
                                        id='p1_g1_2_select_dates_imp',
                                        options=[{'label': i, 'value': i} for i in dates_importantes],
                                        value=[],
                                        multi=True,
                                        className="dcc_control"),

                                    html.Br(),
                                    html.P("Selectionner une période :",className="control_label"),
                                    dcc.DatePickerRange(
                                        id='p1_g1_g2_my-date-picker-range',
                                        min_date_allowed='03/01/2020',
                                        max_date_allowed='05/30/2020',
                                        initial_visible_month='03/01/2020',
                                        start_date=datetime(2020, 3, 1).date(),
                                        end_date=datetime(2020, 5,30 ).date(),
                                        className="dcc_control"),

                                    html.Br(),
                                    html.Br(),
                                    html.Button(
                                        id ='p1_g1_g2_submit-button',
                                        className='button',
                                        n_clicks = 0,
                                        children='Générer Graph')

                                ]
                                ,className="pretty_container _l1"
                            ),

                            html.Div(
                                [
                                    dcc.Checklist(
                                        id='p1_g1_select_media_web',
                                        options=[{'label': i, 'value': i} for i in features],
                                        value=[features[0],features[1],features[2]],
                                        labelStyle={'display': 'inline-block'},
                                        className="dcc_control"
                                    ),
                                    dcc.Graph(id='p1_g1_suivi_nb_media')
                                ]
                                ,className="pretty_container _l3"
                            ),

                        ],className="row flex-display flex-start-display "
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    dcc.Graph(id='p1_g2_pct_type_reserv')
                                ]
                                ,className="pretty_container _l1"
                            ),

                            html.Div(
                                [
                                    dcc.Markdown(children=text_p1_g3,className="markdown"),
                                    #html.P(children="Selectionner les informations que vous souhaitez sur les personnes ayant consultées l'offre 100€ selon :"),
                                    dcc.Dropdown(
                                        id='p1_g3_select_profil_consultants',
                                        options=[{'label': i, 'value': i} for i in features2],
                                        value=[features2[0]],
                                        multi=True,
                                        className="dcc_control"),

                                    dcc.Graph(id = 'p1_g3_type_consult_offre')
                                ]
                                ,className="pretty_container _l1"
                            ),

                        ],className='row flex-display'
                    ),

                    html.Div(
                        [
                            html.Div(id='page-1-content'),
                            html.Br(),
                            dcc.Link('Analyse Réseaux Sociaux', href='/page-2'),
                            html.Br(),
                            dcc.Link('Go back to home', href='/',),
                            html.Br(),
                        ],className="lien_bas_page"
                    )
                ]
            )
        )


],className="mainContainer")


####################################################################################################
####################################################################################################
# PAGE 2
####################################################################################################
####################################################################################################

page_2_layout = html.Div([

    html.H3(children="Analyse Réseaux Sociaux",
            style={"text-align":"left","margin-left":"30px"}),

     dbc.Col(
        html.Div(
            [
                dcc.Tabs(id="p2-tab-choix", value='tab-1', children=[
                        dcc.Tab(label='Analyse Twitter', value='tab-1',style={'fontSize':'22px'}),
                        dcc.Tab(label='Analyse Facebook', value='tab-2',style={'fontSize':'22px'}),
                ]),

                html.Div(id='p2-tab-choix-content')

            ]), width=9
    ),

    html.Div(
        [
            html.Div(id='page-1-content'),
            html.Br(),
            dcc.Link('Consultations Site Web', href='/page-1'),
            html.Br(),
            dcc.Link('Go back to home', href='/'),
            html.Br(),
        ]
        ,className="lien_bas_page"
    )

],className="mainContainer")

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Page 2 onglet 1
analyse_hashtags_twitter = html.Div([
    html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            #html.P(children="Nombre minimum de fois ou le hashtags a été utilisé :",className="control_label"),
                            dcc.Markdown(children=text_p2_twitter,className='markdown'),
                            dcc.Input(
                                id='p1_t1_t2_input',
                                placeholder='Enter a value...',
                                type='number',
                                value=30,
                                className="dcc_control",
                            ),
                        ]
                    ),
                ]
                ,className="pretty_container _l1"
            ),

            html.Div([
                    html.Div(id='p2_t1_nb_retweet')
                ]
                ,className="pretty_container _l3_"
            ),
        ]
        ,className="row flex-display"
    ),

    html.Div(
        [
            html.Div([
                    dcc.Dropdown(id='p2_t1_t2_dropdown',className="dcc_control"),
                    html.Div(id='p2_t2_tweets_par_hashtags')
                ]
                ,className="pretty_container _l1"
            )
        ]
        ,className="row flex-display"
    ),

    html.Div(id='essai'),

])

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
# Page 2 onglet 1
analyse_facebook = html.Div([
    html.Div(
        [
            html.Div(
                [
                    dcc.Graph(id = 'p2_fb_g1_nb_reactions',
                                figure={
                                    'data' :  [ go.Scatter(
                                                    y = df_fb.loc[:,col] ,
                                                    mode='lines',
                                                    name=col,
                                                    marker={
                                                        'size': 10,
                                                        'opacity': 0.5,
                                                        'line': {'width': 0.5, 'color': 'white'}
                                                    }
                                                ) for col in ['nb_reactions','nb_jadore','nb_jaime'] ],
                                    'layout' : go.Layout(title='Réactions au cours du temps')
                                }),
                ],className="pretty_container _l1"
            )
        ]
        ,className="row flex-display"
    ),

])
