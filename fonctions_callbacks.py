
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
fichiers_interet = [str for str in fichiers_chemin_donnees if str.startswith('.\\data\\df_tweets_'+username)]
dates_fichiers_interet = [str.strip('./data/df_tweets_'+username).strip('.xlsx') for str in fichiers_interet]
dates_fichiers_interet = [dt.datetime.strptime(date, "%b-%d-%Y").date() for date in dates_fichiers_interet]
max_date = max(dates_fichiers_interet)
del(fichiers_chemin_donnees,fichiers_interet,dates_fichiers_interet)

df_tweets = pd.read_excel('./data/df_tweets_'+username+'_'+max_date.strftime("%b-%d-%Y")+'.xlsx')
df_tweets.loc[:,'hashtags'] = df_tweets.loc[:,'hashtags'].apply(lambda x: literal_eval(x))
nb_retweet_hashtags = pd.read_excel('./data/nb_retweets_'+username+'_'+max_date.strftime("%b-%d-%Y")+'.xlsx')

##################################################################################################
##################################################################################################
######################################### FONCTIONS ##############################################

#-------------------------------------------------------------------------------------------------
# FONCTIONS PAGE 1

# pour tracer les Dates Importantes
def p1_g1_g2_dates_imp_(dates_imp,min_,max_):
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

def p1_g1_mise_a_jour_(n_clicks,select_media_web,start_date,end_date,dates_imp):
    min_ = min(df.loc[:,[media for media in select_media_web]].min(axis=0))
    max_ = max(df.loc[:,[media for media in select_media_web]].max(axis=0))

    liste_date_imp = p1_g1_g2_dates_imp_(dates_imp,min_,max_)

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

def p1_g2_mise_a_jour_(n_clicks,start_date,end_date,dates_imp):

    liste_date_imp = p1_g1_g2_dates_imp_(dates_imp,0,1)

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

# pour tracer un graph selon  le type du consultant
def p1_g3_mise_a_jour_(profils_consultants):
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
                'layout':go.Layout(title='Profils des consultants de l\'offre selon la variable : {}'.format(profil_))
            }
        elif df2[profil_].dtypes == 'int64':
            fig={
                'data':[go.Histogram(x=df2[profil_])],
                'layout':go.Layout(title='Profils des consultants de l\'offre selon la variable : {}'.format(profil_))
            }
    elif len(profils_consultants)==2 and df2.loc[:,profils_consultants].dtypes.tolist().count('int64') == 2:
        fig={
            'data':[go.Scatter(
                        x=df2[profils_consultants[0]],
                        y=df2[profils_consultants[1]],
                        mode='markers'
                    )],
            'layout':go.Layout(title='Profils des consultants de l\'offre selon la variable '+profils_consultants[0]+' et la variable '+profils_consultants[1])
        }
    elif len(profils_consultants)==2 and df2.loc[:,profils_consultants].dtypes.tolist().count('int64') == 1:
        if df2[profils_consultants[0]].dtypes == 'int64':
            var_moy = profils_consultants[0]
            var_abscisse = profils_consultants[1]
            x_ = df2[profils_consultants[1]].unique()
            y_ = df2.groupby([profils_consultants[1]]).mean()[profils_consultants[0]]
        else:
            var_moy = profils_consultants[1]
            var_abscisse = profils_consultants[0]
            x_ = df2[profils_consultants[0]].unique()
            y_ = df2.groupby([profils_consultants[0]]).mean()[profils_consultants[1]]
        fig = {
            'data':[go.Bar(
                        x=x_, y=y_
                    )],
            'layout':go.Layout(title='Profils des consultants de l\'offre : moyenne de '+var_moy+' par '+ var_abscisse)
        }
    elif len(profils_consultants)==3 and df2.loc[:,profils_consultants].dtypes.tolist().count('int64') == 1 and df2.loc[:,profils_consultants].dtypes.tolist().count('O') ==2 :
        df2_ = df2.drop('id',axis=1)
        df2_ = df2_[profils_consultants]
        reper_var = df2_[profils_consultants].dtypes == 'int64'

        var_int = df2_.iloc[:,reper_var.values]
        var_cat = df2_.iloc[:,~reper_var.values]

        df_ = pd.DataFrame(df2.groupby(list(var_cat.columns)).mean()[list(var_int.columns)[0]]).reset_index()
        fig = {
            'data' : [  go.Bar(
                            x=df_.loc[df_[var_cat.columns[1]]==val_cat_leg , var_cat.columns[0]],
                            y=df_.loc[df_[var_cat.columns[1]]==val_cat_leg , var_int.columns[0]],
                            name=val_cat_leg,
                        ) for val_cat_leg in  df_.loc[:,var_cat.columns[1]].unique()
                     ] ,
            'layout' : go.Layout(title='Profils des consultants de l\'offre : moyenne de ' + var_int.columns[0] + ' par ' + var_cat.columns[0] + ' et ' + var_cat.columns[1])
        }
    elif len(profils_consultants)==2 and 'int64' not in  df2.loc[:,profils_consultants].dtypes.tolist():
        fig = px.sunburst(df2, path=profils_consultants)
    else:
        fig = {}

    return fig


#-------------------------------------------------------------------------------------------------
# FONCTIONS PAGE 2

# nuage de mot
def p2_g_mise_a_jour_(text):
    wc = WordCloud(stopwords = set(STOPWORDS),
                   max_words = 200,
                   max_font_size = 100)
    wc.generate(text)

    word_list=[]
    freq_list=[]
    fontsize_list=[]
    position_list=[]
    orientation_list=[]
    color_list=[]

    for (word, freq), fontsize, position, orientation, color in wc.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x=[]
    y=[]
    for i in position_list:
        x.append(i[0])
        y.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i*100)
    new_freq_list

    trace = go.Scatter(x=x,
                       y=y,
                       textfont = dict(size=new_freq_list,
                                       color=color_list),
                       hoverinfo='text',
                       hovertext=['{0}{1}'.format(w, f) for w, f in zip(word_list, freq_list)],
                       mode='text',
                       text=word_list
                      )

    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}})

    fig = go.Figure(data=[trace], layout=layout)

    return fig

def p2_t1_t2_dropdown_mise_a_jour_(value_input):
    df_ = nb_retweet_hashtags.loc[nb_retweet_hashtags['COUNT']>=value_input,:]
    df_ = df_.sort_values(by=['retweet_count'],ascending=False)

    hashtags = [tag for tag in df_['hashtags']]
    options = [ {'label': hashtags_, 'value': hashtags_} for hashtags_ in hashtags]

    return options

def p2_t1_nb_retweet_mise_a_jour_(value_input):
    df_ = nb_retweet_hashtags.loc[nb_retweet_hashtags['COUNT']>=value_input,('hashtags','retweet_count')]
    df_.retweet_count = df_.retweet_count.round(1)

    return dasht.DataTable(
        id="table",
        sort_action="native",
        # filter_action="native",
        #row_deletable=True,
        row_selectable='single',
        # css={
        #     "rule": "display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;"
        # },
        style_data={"whiteSpace": "normal"},
        style_cell={
            "padding": "10px",
            "midWidth": "0px",
            "textAlign": "center",
            "border": "white",
            'fontSize':20,
        },
        columns=[{"name": 'hashtags', "id": 'hashtags'},{"name": 'retweet_count', "id": 'retweet_count'}],
        data=df_.to_dict("rows"),
        page_size=6
    )

def p2_t2_tweets_par_hashtags_mise_a_jour_(value_input):

    df_ = df_tweets.loc[:,("date", "text","retweet_count","hashtags")]

    selection = [value_input]
    mask = pd.DataFrame(df_.hashtags.tolist()).isin(selection).any(1).tolist()
    df_ = df_[mask]

    df_['hashtags'] = [' '.join(map(str, l)) for l in df_['hashtags']]

    return dasht.DataTable(
        id="table",
        sort_action="native",
        #filter_action="native",
        #row_deletable=True,
        #row_selectable=True,
        # css={
        #     "rule": "display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;"
        # },
        style_data={"whiteSpace": "normal"},
        style_cell={
            "padding": "10px",
            "midWidth": "0px",
            "textAlign": "center",
            "border": "white",
            'fontSize':20,
        },
        style_cell_conditional=[
            {'if': {'column_id': 'text'},
             'width': '50%'},
        ],
        columns=[{"name": i, "id": i} for i in df_.columns],
        data=df_.to_dict("rows"),
        page_size=10
    )
