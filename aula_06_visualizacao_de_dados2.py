# Aula 06 - Visualização de Dados.

"""
Streamlit: É uma biblioteca em Python para criar aplicativos e compartilhar na web.
O Streamlit é um listener que fica “ouvindo” um arquivo.
Para "ouvir" o arquivo, deve digitar no terminal do Pycharm: streamlit run <nome do arquivo.py>

Se ocorrer alguma modificação no arquivo, o Streamlit recarrega o arquivo.
No PyCharm, para salvar um arquivo digita-se CTRL+S ou executa o arquivo.
Após digitar alguma coisa no arquivo e salvá-lo digitando CTRL+S ou executando o arquivo,
na página web do Streamlit vai exibir uma mensagem: Source File changed botão<ReRun> botão<Always rerun>.

Se selecionar o botão <ReRun> vai recarregar o arquivo.
Se selecionar o botão <Always rerun> sempre que ocorrer uma modificação no arquivo, o Streamlit o recarrega.

--- Instalar Streamlit:
Digitar no terminal do PyCharm: pip install streamlit
Digitar no terminal do Pycharm: streamlit hello.
Deve aparecer no terminal a seguinte mensagem:
  Welcome to Streamlit. Check out our demo in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.0.2:8501
  Ready to create your own Python apps super quickly?
  Just head over to https://docs.streamlit.io

Deve abrir uma página web escrito Welcome to Streamlit!

Após isto, digitar CTRL+C.

--- "Escutar" um arquivo Python:
No terminal do PyCharm digitar: streamlit run <nome do arquivo.py>.
Exemplo: streamlit run aula05_house_rocket_app.py
Vai aparecer no terminal a seguinte mensagem:
Your can view your Streamlit app in your browser.

Local URL: https://localhost:8501
Network URL: https://10.211.55.3:8501

e vai abrir uma página web.
"""
import streamlit as st
import pandas as pd
import geopandas  # GeoPandas is an open source project to make working with geospatial data in python easier.
import numpy as np
import folium  # Biblioteca para fazer mapa.
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import plotly.express as px
from datetime import datetime

# O comando st.set_page_config abaixo, define que vai exibir o conteúdo do dataset em toda a largura da página
# no browser.
st.set_page_config(layout='wide')


# O decorador @st.cache é um decorador do Streamlit que em vez de ler o arquivo do disco, lê da memória, tornando
# o processo mais rápido. O parâmetro allow_output_mutation=True define que o conteúdo da memória cache
# seja mutável, isto é, pode variar.
@st.cache(allow_output_mutation=True)
def get_data(path):
    data = pd.read_csv(path)
    return data


@st.cache(allow_output_mutation=True)
def get_geofile(url):
    geofile = geopandas.read_file(url)
    return geofile


# get data
path = 'datasets\kc_house_data.csv'
data = get_data(path)

# get geofile
# geofile: são arquivos espaciais. São arquivos JSON que contém dicionários com as medidas de latitude e
# longitude de cada região (exemplo: as regiões geográficas de cada bairros).
# geofile da região de Seattle: https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson
url = 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'
geofile = get_geofile(url)

# add new feature
# Cria uma nova coluna de preço por pés quadrado. Divide o preço pelo tamanho do terreno.
data['price_sqft'] = data['price'] / data['sqft_lot']

# ============================
# Data overview
#=============================

# Cria um filtro de coluna
# Define um sidebar com todos os nomes das colunas do dataset, onde o usuário pode selecionar quantos nomes quiser.
f_attributes = st.sidebar.multiselect('Enter columns:', data.columns)

#st.write(f_attributes) # Exibe os valores do atributo f_attributes.
#st.write(f_zipcode)  # Exibe os valores do atributo f_zipcode


# Cria um filtro para o zip code.
# Define um sidebar com todos os valores de Zip Code da coluna zicode, onde o usuário pode selecionar
# quantos valores quiser.
f_zipcode = st.sidebar.multiselect('Enter Zip Code:', data['zipcode'].sort_values().unique())


st.title('Data Overview')

# A condição abaixo exibe o dataset data de acordo com os atributos e zipcode selecionados pelo usuário.
# Se o usuário não selecionar nada, exibe o dataset data completo.
# attributes + zipcode = Selecionar Colunas e Linhas
# attributes = Selecionar Colunas
# zipcode = Selecionar Linhas
# 0 + 0 = Retorna o dataset original

if (f_zipcode != []) & (f_attributes != []):
    # O comando abaixo isin seleciona os valores da coluna zipcode que estão no atributo f_zipcode e
    # exibe as colunas que estão no atributo f_attributes.
    data = data.loc[data['zipcode'].isin(f_zipcode), f_attributes]

elif (f_zipcode != []) & (f_attributes == []):
    # O comando abaixo isin seleciona os valores da coluna zipcode que estão no atributo f_zipcode e
    # exibe todas as colunas do dataset data utilizando o parametro : .
    data = data.loc[data['zipcode'].isin(f_zipcode), :]

elif (f_zipcode == []) & (f_attributes != []):
    # O comando abaixo exibe todas as linhas e exibe as colunas que estão no atributo f_attributes.
    data = data.loc[:, f_attributes]

else:
    data = data.copy()

st.dataframe(data)  # Exibe o dataset data.


# O comando abaixo st.beta_columns define a quantidade e a largura das colunas na exibição na tela.
# Exemplo: st.beta_columns((1,1,1,1)) = Exibe quatro colunas todos com o mesmo tamanho.
# Exemplo: st.beta_columns((2,1,1)) = Exibe três colunas, onde a primeira coluna terá o dobro da
# largura da segunda e terceira colunas.
# O comando abaixo define os atributos c1 e c2 para as duas colunas que serão exibidas.
c1, c2 = st.beta_columns((2,1))  # O primeiro dataset terá o dobro da largura do segundo dataset.


# Average metrics
# Cria um dataset df1 com a quantidade de imóveis por zipcode.
df1 = data[['id', 'zipcode']].groupby('zipcode').count().reset_index()
# Cria um dataset df2 com a média dos preços por zipcode.
df2 = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()
# Cria um dataset df3 com a média do tamanho da sala de estar por zipcode.
df3 = data[['sqft_living', 'zipcode']].groupby('zipcode').mean().reset_index()
# Cria um dataset df4 com a média do preço por pés quadrado por zipcode.
df4 = data[['price_sqft', 'zipcode']].groupby('zipcode').mean().reset_index()


# merge
# O comando pd.merge juntas dois datasets. O parâmetro on= informa qual a coluna irá unir os datasets.
# O comange pd.merge é utilizado quando queremos garantir que o valor de uma coluna que está no primeiro dataset,
# seja igual à do segundo dataset.
m1 = pd.merge(df1, df2, on='zipcode', how='inner')
m2 = pd.merge(m1, df3, on='zipcode', how='inner')
df = pd.merge(m2, df4, on='zipcode', how='inner')

# Define o nome das colunas do dataset df.
df.columns = ['ZIPCODE', 'TOTAL HOUSES', 'PRICES', 'SQRT_LIVING', 'PRICE/FT2']

# O comando st.dataframe abaixo exibe o dataframe df. O parâmetro height define a altura do dataframe na tela.
# O parametro c1 define que é exibido na primeira coluna.
c1.header('Average Values')
c1.dataframe(df, height=800)


# Statistic Descriptive
# O comando data.select_dtypes abaixo cria um dataset num_attributes somente com os valores que são núméricos int64 e float64.
# Neste caso, todas as colunas serão selecionadas com exceção da coluna date que possui o formato datetime64.
num_attributes = data.select_dtypes(include=['int64', 'float64'])

# O comando set_option abaixo converte de notacão científica para float com 3 casas decimais.
pd.set_option('display.float_format', lambda x: '%.3f'%x)

# O comando apply executa uma determinada função nas linhas ou nas colunas do meu dataset.
# Central tendency: media, mediana
# O comando abaixo exibe a média dos valores das colunas:
# num_attributes.apply(np.mean, axis=0)  # axis=0 significa que executa a função ao longo das colunas.

# Armazena a média dos valores no atributo média e armazena a mediana dos valores no atributo mediana.
# O comando pd.DataFrame converte os valores para um dataframe.
media = pd.DataFrame(num_attributes.apply(np.mean, axis=0))
mediana = pd.DataFrame(num_attributes.apply(np.median, axis=0))

# dispersion: std, min, max
# Armazena o desvio padrão no atributo std, o mínimo no atributo min_ e o máximo no atributo max_.
# Foi utilizado underline no fim dos atributos min e max, pois as palavras min e max são palavras reservadas
std = pd.DataFrame(num_attributes.apply(np.std, axis=0))
min_ = pd.DataFrame(num_attributes.apply(np.min, axis=0))
max_ = pd.DataFrame(num_attributes.apply(np.max, axis=0))

# A função concat concatena uma sequencia de dataframes.
# O exemplo abaixo, concatena os dataframes max_, min_, media, mediana e std em um único dataframe chamado df1.
df1 = pd.concat([max_, min_, media, mediana, std], axis=1).reset_index()

# O comando abaixo atribui nome para as colunas do dataset df1.
df1.columns = ['attributes', 'max', 'min', 'mean', 'median', 'std']

# O comando st.dataframe abaixo exibe o dataframe df1. O parâmetro height define a altura do dataframe na tela.
# O parametro c2 define que é exibido na segunda coluna.
c2.header('Descriptive Analysis')
c2.dataframe(df1, height=800)

# ==============================
# Mapas de Densidade de Portfolio
#===============================

st.title('Region Overview')

c1, c2 = st.beta_columns((1,1))
c1.header('Portfolio Density')

df = data.sample(100)  # Seleciona cem valores do dataset original.

# Base Map - Folium: biblioteca para fazer mapas.
# A biblioteca Folium, quando em zoom out, agrupa os pontos no mapa, mostrando a quantidade em uma determinada região.
# Quando executamos o zoom in, os pontos no mapa aparecem individualmente.
# No comando abaixo location define o zoom do mapa baseado na media de latitude e longitude,
# No comando abaixo default_zoom_start define o comportamento do zoom in e zoom out.)
density_map = folium.Map(location=[data['lat'].mean(),
                                   data['long'].mean()],
                         default_zoom_start=15)

# O comando abaixo adiciona marcadores no mapa. Isto é, quando o usuário clicar em alguma localização de um
# imóvel no mapa, vai aparecer uma janela com as informações do comando popup definido abaixo.
marker_cluster = MarkerCluster().add_to(density_map)

# O comando abaixo iterrows() tranforma o dataset em um iterador.
for name, row in df.iterrows():  # row significa cada linha do dataset
    folium.Marker([row['lat'], row['long'] ],
        popup='Sold R${0} on: {1}. Features: {2} sqft, {3} bedrooms, {4} bathrooms, year_built {5}'.format(row['price'],
                    row['date'],
                    row['sqft_living'],
                    row['bedrooms'],
                    row['bathrooms'],
                    row['yr_built'])).add_to(marker_cluster)


# Exibe um mapa de densidade de portifólio.
with c1:
    folium_static(density_map)


# Region Price Map
c2.header('Price Density')

# Cria um dataset df com a média de preços por zipcode.
df = data[['price', 'zipcode']].groupby('zipcode').mean().reset_index()

df.columns = ['ZIP', 'PRICE']

df = df.sample(10)  # Seleciona dez valores do dataset original.


# Filtra o geofile apenas com os números de ZIP que estão do dataframe df.
geofile = geofile[geofile['ZIP'].isin(df['ZIP'].tolist())]


region_price_map = folium.Map(location=[data['lat'].mean(),
                                   data['long'].mean()],
                                   default_zoom_start=15)

# Método choropleth para criar as regiões na mapa.
# https://plotly.com/python/choropleth-maps/
# A Choropleth Map is a map composed of colored polygons. It is used to represent spatial variations of a quantity.
region_price_map.choropleth(data = df,
                            geo_data = geofile,
                            columns=['ZIP', 'PRICE'],
                            key_on='feature.properties.ZIP',
                            fill_color='YlOrRd',
                            fill_opacity=0.7,
                            line_opacity=0.2,
                            legend_name='AVG PRICE')

# Exibe um mapa de densidade de preços.
with c2:
    folium_static(region_price_map)


# ==================================================
# Distribuição dos imóveis por categorias comerciais
# ==================================================
# Cria um título para a barra lateral.
st.sidebar.title('Commercial Options')

st.title('Commercial Attributes')

# ----- Average Price per Year

# filters
# Tem que converter o valor para inteiro senão não funciona.
min_year_built = int(data['yr_built'].min())  # Armazena o menor valor da coluna yr_built no atributo min_year_built
max_year_built = int(data['yr_built'].max())  # Armazena o maior valor da coluna yr_built no atributo max_year_built

# Define um título para o filtro
st.sidebar.subheader('Select Max Year Built')

# Define um filtro do tipo slider
# min_year_built = valor mínimo.
# max_year_built = valor maximo.
# min_year_built = valor padrão.
f_year_built = st.sidebar.slider('Year Built', min_year_built, max_year_built, min_year_built)

# Define um título para o gráfico.
st.header('Average Price per Year Built')

# Armazena no dataframe df os valores dos anos de construção yr_built que forem menores que o valor
# selecionado no botão slider f_year_built.
df = data.loc[data['yr_built'] < f_year_built]

# Define um dataframe df com a média dos preços pelo ano de construção.
df = df[['yr_built', 'price']].groupby('yr_built').mean().reset_index()

# Define um gráfico de linha e armazena no atributo fig.
fig = px.line(df, x='yr_built', y='price')  # Define eixo X yr_built e eixo Y price.

# Exibe o gráfico de linha
st.plotly_chart(fig, use_container_width=True)  # use_container_width=True utiliza a largura total da página.


# ----- Average Price per Day

# Converte os valores da coluna date para data e formata para ano, mês e dia.
data['date'] = pd.to_datetime(data['date']).dt.strftime('%Y-%m-%d')

# Define um título para o gráfico.
st.header('Average Price per Day')

# Define um título para o filtro
st.sidebar.subheader('Select Max Date')

# filters
# Tem que formatar a data utilizando o comando datetime.strptime senão não funciona.
min_date = datetime.strptime(data['date'].min(), '%Y-%m-%d') # Armazena o menor valor da coluna date no atributo min_date.
max_date = datetime.strptime(data['date'].max(), '%Y-%m-%d') # Armazena o maior valor da coluna date no atributo max_date.

# Define um filtro do tipo slider
# min_date = valor mínimo.
# max_date = valor maximo.
# min_date = valor padrão.
f_date = st.sidebar.slider('Date', min_date, max_date, min_date)

# Converte os valores da coluna date para o tipo data.
data['date'] = pd.to_datetime(data['date'])

# Armazena no dataframe df os valores de data que forem menores que o valor
# selecionado no botão slider f_date.
df = data.loc[data['date'] < f_date]

# Define um dataframe df com a média dos preços pela data.
df = df[['date', 'price']].groupby('date').mean().reset_index()

# Define um gráfico de linha e armazena no atributo fig.
fig = px.line(df, x='date', y='price')  # Define eixo X date e eixo Y price.

# Exibe o gráfico de linha
st.plotly_chart(fig, use_container_width=True)  # use_container_width=True utiliza a largura total da página.


# ==========
# Histograma
# ==========
# Define um título para o gráfico.
st.header('Price Distribution')

# Define um título para o filtro
st.sidebar.subheader('Select Max Price')

#filter
min_price = int(data['price'].min())  # Armazena o menor valor da coluna price no atributo min_price
max_price = int(data['price'].max())  # Armazena o maior valor da coluna price no atributo max_price
avg_price = int(data['price'].mean())  # Armazena o valor médio da coluna price no atributo avg_price

# Define um filtro do tipo slider
# min_price = valor mínimo.
# max_price = valor maximo.
# avg_price = valor padrão.
f_price = st.sidebar.slider('Price', min_price, max_price, avg_price)

# Armazena no dataframe df os valores de price que forem menores que o valor
# selecionado no botão slider f_price.
df = data.loc[data['price'] < f_price]

# # Define um gráfico de histograma e armazena no atributo fig.
# nbins = define quantas barras irão aparecer no histograma.
fig = px.histogram(df, x='price', nbins=50)

# Exibe o gráfico de histograma
st.plotly_chart(fig, use_container_width=True)


# ==========
# Distribuição dos imóveis por categorias físicas
# ==========

st.sidebar.title('Attributes Options')

st.title('House Attributes')

#filter
# Define um filtro com os valores de bedrooms
f_bedrooms = st.sidebar.selectbox('Max number of bedrooms', data['bedrooms'].sort_values().unique())

# Define um filtro com os valores de bathrooms
f_bathrooms = st.sidebar.selectbox('Max number of bathrooms', sorted(set(data['bathrooms'].unique())))
# O comando sorted(set acima tem o mesmo efeito do comando sort_values no comando anterior.

c1, c2 = st.beta_columns(2)  # Cria duas colunas para exibir os gráficos lado a lado.

# House per bedrooms
c1.header('Houses per Bedrooms')
# Armazena no dataframe df os valores de bedrooms que forem menores que o valor
# selecionado no filtro f_bedrooms.
df = data[data['bedrooms'] < f_bedrooms]
# Cria um gráfico de histograma da quantidade de bedrooms
fig = px.histogram(df, x='bedrooms', nbins=19)
c1.plotly_chart(fig, use_container_width=True)


# House per bathrooms
c2.header('Houses per Bathrooms')
# Armazena no dataframe df os valores de bathrooms que forem menores que o valor
# selecionado no filtro f_bathrooms.
df = data[data['bathrooms'] < f_bathrooms]
# Cria um gráfico de histograma da quantidade de bathrooms
fig = px.histogram(df, x='bathrooms', nbins=19)
c2.plotly_chart(fig, use_container_width=True)

# filters
# Define um filtro com os valores de floors
f_floors = st.sidebar.selectbox('Max Number of Floors', sorted(set(data['floors'].unique())))

# Define um filtro para os valores de Water View.
f_waterview = st.sidebar.checkbox('Only Houses with Water View')

c1, c2 = st.beta_columns(2)  # Cria duas colunas para exibir os gráficos lado a lado.


# House per floors
c1.header('Houses per Floor')
# Armazena no dataframe df os valores de floors que forem menores que o valor
# selecionado no filtro f_floors.
df = data[data['floors'] < f_floors]
# Cria um gráfico de histograma da quantidade de andares
fig = px.histogram(df, x='floors', nbins=19)
c1.plotly_chart(fig, use_container_width=True)


# House per water view
c2.header('Houses per Water View')
if f_waterview:  # Se o usuário selecionar o chekbox f_waterview, armazena no datafram df os valores de
                 # waterfront que forem iguais à 1.
    df = data[data['waterfront'] == 1]
else:
    df = data.copy()
# Cria um gráfico de histograma da quantidade de vista para o mar
fig = px.histogram(df, x='waterfront', nbins=19)
c2.plotly_chart(fig, use_container_width=True)


# O Site awesome-streamlit.org possui vários exemplos de dashboard com streamlit.







