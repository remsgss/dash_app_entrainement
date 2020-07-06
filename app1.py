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

import fonctions_callbacks
import layouts

USERNAME_PASSWORD_PAIRS = [['6fois7','mdp']]


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
fichiers_interet = [str for str in fichiers_chemin_donnees if str.startswith('./data/df_tweets_'+username)]
dates_fichiers_interet = [str.strip('./data/df_tweets_'+username).strip('.xlsx') for str in fichiers_interet]
dates_fichiers_interet = [dt.datetime.strptime(date, "%b-%d-%Y").date() for date in dates_fichiers_interet]
max_date = max(dates_fichiers_interet)
del(fichiers_chemin_donnees,fichiers_interet,dates_fichiers_interet)

df_tweets = pd.read_excel('./data/df_tweets_'+username+'_'+max_date.strftime("%b-%d-%Y")+'.xlsx')
df_tweets.loc[:,'hashtags'] = df_tweets.loc[:,'hashtags'].apply(lambda x: literal_eval(x))
nb_retweet_hashtags = pd.read_excel('./data/nb_retweets_'+username+'_'+max_date.strftime("%b-%d-%Y")+'.xlsx')





##################################################################################################
##################################################################################################
######################################### APPLICATION ############################################
# ouverture de l'appli
app = dash.Dash(__name__)
auth = dash_auth.BasicAuth(app,USERNAME_PASSWORD_PAIRS)
server = app.server

layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    ),


# app layout
app.layout = html.Div([

    html.H2(id="title",
            children="Suivi Médias Web",
            style={"text-align":"left","margin-left":"30px"}
    ),
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')

],style={'padding':'10'})

index_page = html.Div([
    dcc.Link('Consultations Site Web', href='/page-1'),
    html.Br(),
    dcc.Link('Analyse Réseaux Sociaux', href='/page-2'),
],className="lien_bas_page")



####################################################################################################
####################################################################################################
######################################### UPDATING FIGURES #########################################

@app.callback(
    Output('essai', 'children'),
    [
        Input('p2_t1_nb_retweet', 'active_cell ')
    ]
)
def selected_raw(active_cell ):
    print('coucou')
    print(type(active_cell ))
    # selected_rows = [rows[i] for i in selected_row_indices]
    # print(type(selected_rows),'\n')
    # print(selected_rows,'\n')

@app.callback(
    Output('p1_g1_suivi_nb_media','figure'),
    [
        Input('p1_g1_g2_submit-button','n_clicks'),
        Input('p1_g1_select_media_web','value')
    ],
    [
        State('p1_g1_g2_my-date-picker-range', 'start_date'),
        State('p1_g1_g2_my-date-picker-range', 'end_date'),
        State('p1_g1_2_select_dates_imp','value')
    ]
)
def p1_g1_mise_a_jour(n_clicks,select_media_web,start_date,end_date,dates_imp):
    return fonctions_callbacks.p1_g1_mise_a_jour_(n_clicks,select_media_web,start_date,end_date,dates_imp)

@app.callback(
    Output('p1_g2_pct_type_reserv','figure'),
    [
        Input('p1_g1_g2_submit-button','n_clicks')
    ],
    [
        State('p1_g1_g2_my-date-picker-range', 'start_date'),
        State('p1_g1_g2_my-date-picker-range', 'end_date'),
        State('p1_g1_2_select_dates_imp','value')
    ]
)
def p1_g2_mise_a_jour(n_clicks,start_date,end_date,dates_imp):
    return fonctions_callbacks.p1_g2_mise_a_jour_(n_clicks,start_date,end_date,dates_imp)

@app.callback(
    Output('p1_g3_type_consult_offre','figure'),
    [
        Input('p1_g3_select_profil_consultants', 'value')
    ]
)
def p1_g3_mise_a_jour(profils_consultants):
    return  fonctions_callbacks.p1_g3_mise_a_jour_(profils_consultants)

@app.callback(
    Output('p2_t1_t2_dropdown','options'),
    [
        Input('p1_t1_t2_input','value')
    ]
)
def p2_t1_t2_dropdown_mise_a_jour(value_input):
    return fonctions_callbacks.p2_t1_t2_dropdown_mise_a_jour_(value_input)

@app.callback(
    Output('p2_t1_nb_retweet','children'),
    [
        Input('p1_t1_t2_input','value')
    ]
)
def p2_t1_nb_retweet_mise_a_jour(value_input):
    return fonctions_callbacks.p2_t1_nb_retweet_mise_a_jour_(value_input)

# @app.callback(
#     Output('p2_t2_tweets_par_hashtags','children'),
#     [
#         Input('p2_t1_t2_dropdown','value')
#     ]
# )
# def p2_t2_tweets_par_hashtags_mise_a_jour(value_input):
#     return fonctions_callbacks.p2_t2_tweets_par_hashtags_mise_a_jour_(value_input)

@app.callback(
    Output('p2_t2_tweets_par_hashtags','children'),
    [
        Input('p2_t1_tweets', 'active_cell'),
        Input('p2_t1_tweets', 'derived_viewport_data'),
    ]
)
def p2_t1_selected_cell(active_cell,derived_virtual_data):
    if active_cell:
        df = pd.DataFrame(derived_virtual_data)
        if active_cell['column'] == 0 :
            return fonctions_callbacks.p2_t2_tweets_par_hashtags_mise_a_jour_(df.iloc[active_cell['row'],active_cell['column']])

@app.callback(
        Output('p2_t3_post_fb', 'children'),
        [Input('p2_fb_g1_nb_reactions', 'clickData')]
)
def affichage_post_fb(input_value):
    return fonctions_callbacks.affichage_post_fb_(input_value)

@app.callback(
        Output('p2_t3-image', 'src'),
        [Input('p2_fb_g1_nb_reactions', 'clickData')]
)
def affichage_image_fb(input_value):
    return fonctions_callbacks.affichage_image_fb_(input_value)
#-------------------------------------------------------------------------------
# INDEX
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return  layouts.page_1_layout
    elif pathname == '/page-2':
        return  layouts.page_2_layout
    else:
        return index_page
    # You could also return a 404 "URL not found" page here

@app.callback(dash.dependencies.Output('p2-tab-choix-content', 'children'),
              [dash.dependencies.Input('p2-tab-choix', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return layouts.analyse_hashtags_twitter
    elif tab == 'tab-2':
       return  layouts.analyse_facebook




# Running the server
if __name__ == '__main__':
    app.run_server()
