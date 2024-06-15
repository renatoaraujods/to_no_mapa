import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# CARREGAMENTO DA BASE DE DADOS NO FORMATO DATAFRAME - EXTRACT
data = pd.read_csv( 'tabela-base.csv' )

# PREPARANDO VARIÁVEIS - TRANSFORM

# Renomeando a coluna Nome.1 para Estado
data = data.rename(columns={'Nome.1': 'Estado'})

# Número de cadastros
cadastros = len(data)

# Área
# Conversão da área de m² para km²
data['area'] = data['area'] / 1000000

area_total_raw = int(data[ 'area' ].sum())
area_total_virgula = f"{area_total_raw:,}"
area_total = area_total_virgula.replace(",", ".")

area_media_raw = int(area_total_raw / cadastros)
area_media_virgula = f"{area_media_raw:,}"
area_media = area_media_virgula.replace(",", ".")

# Famílias
# total_familias = str(data[ 'Qtde Familias' ].sum())
total_familias_raw = int(data[ 'Qtde Familias' ].sum())
total_familias_virgula = f"{total_familias_raw:,}"
total_familias = total_familias_virgula.replace(",", ".")
media_familias_por_comunidade = str(int(data['Qtde Familias'].mean()))

# Estados
contagem_estados = {}
for estado in data[ 'Estado' ].unique():
    contagem_estados[ estado ] = data[ data[ 'Estado' ] == estado ][ 'Estado' ].count()
df_estados = pd.DataFrame(contagem_estados, index=[0]).T
df_estados = df_estados.reset_index()
df_estados.columns = [ 'Estado', 'Comunidades' ]
df_estados = df_estados.sort_values(by = 'Comunidades', ascending=False).reset_index( drop = True )
df_estados.index += 1

# Biomas
# Substituindo os biomas nulls
data['Bioma'] = data['Bioma'].fillna('Indefinido')
contagem_biomas = data['Bioma'].value_counts()
# Criar um DataFrame a partir da série
df_biomas = pd.DataFrame({'Bioma': contagem_biomas.index, 'count': contagem_biomas.values})

# Municípios
contagem_municipios = data['Municipio Referencia'].nunique()

# Segmentos
# podemos buscar da API !!!!!!!!
lista_pctafs = [
    "agricultores-familiares",
    "andirobeiras",
    "apanhadores-de-sempre-vivas",
    "benzedeiros",
    "caatingueiros",
    "caboclos",
    "caicaras",
    "castanheiras",
    "catadores-de-mangaba",
    "ciganos",
    "cipozeiros",
    "extrativistas",
    "extrativistas-costeiros-e-marinhos",
    "faxinalenses",
    "fundo-e-fecho-de-pasto",
    "geraizeiros",
    "ilheus",
    "indigenas",
    "isqueiros",
    "juventude-de-povos-e-comunidades-tradicionais",
    "morroquianos",
    "outros-segmentos",
    "pantaneiros",
    "pescadores-artesanais",
    "piacaveiros",
    "pomeranos",
    "povos-de-terreiro-matriz-africana",
    "quebradeiras-de-coco-babacu",
    "quilombolas",
    "retireiros",
    "ribeirinhos",
    "seringueiros",
    "vazanteiros",
    "veredeiros"
]

dict_pctafs = {}
for pctaf in lista_pctafs:
    nome_concat = 'tipoComunidade_' + pctaf
    contagem = data[nome_concat][ data[nome_concat] != 0 ].count()
    dict_pctafs[ pctaf ] = contagem

# contando o número de segmentos até agora.
cont = 0
for segmento in dict_pctafs:
    if dict_pctafs[segmento] != 0:
        cont = cont + 1

# preparando o df de segmentos
df_pctafs = pd.DataFrame( dict_pctafs, index=[0] ).T.reset_index()
df_pctafs.columns = ['Segmento', 'Comunidades']
df_pctafs = df_pctafs.sort_values( by = 'Comunidades', ascending = False )

# criando df só com os segmentos que apareceram
df_pctafs_nao_nulo = df_pctafs[ df_pctafs[ 'Comunidades' ] != 0 ].reset_index( drop = True )
df_pctafs_nao_nulo['Segmento'] = df_pctafs_nao_nulo['Segmento'].str.replace('-', ' ') # Substituir "-" por " "


# conflitos
lista_conflitos = [
    "conflito-por-terra",
    "conflito-por-agua",
    "contaminacao-por-agrotoxico",
    "desmatamento",
    "garimpo",
    "invasao",
    "mineracao",
    "outro-conflito",
    "queimadas-nao-controladas",
    "racismo"
]

dict_conflitos = {}

for conflito in lista_conflitos:
    nome_concat = 'tipoConflito_' + conflito
    contagem = data[nome_concat][ data[nome_concat] != 0 ].count()
    dict_conflitos[ conflito ] = contagem

# preparando o df de conflitos
df_conflitos = pd.DataFrame( dict_conflitos, index=[0] ).T.reset_index()
df_conflitos.columns = ['Conflito', 'Comunidades']
df_conflitos = df_conflitos.sort_values( by = 'Comunidades', ascending = False )
df_conflitos['Conflito'] = df_conflitos['Conflito'].str.replace('-', ' ') # Substituir "-" por " "

# contagem de comunidades com conflito e porcentagem
com_conflito = len(data[data['conflitos'].notnull()])
porc_com_conflito = round((com_conflito / cadastros) * 100)

#  Contagem de áreas de conflito
# Obtendo todas as colunas que começam com 'tipoConflito_'
colunas_tipo_conflito = [coluna for coluna in data.columns if coluna.startswith('tipoConflito_')]
# Somando as áreas de conflito
soma_areas_conflito = data[colunas_tipo_conflito].sum().sum()

# Preparando tabela de porcentagem de comunidades que tem conflitos por estado
# Filtrar apenas as comunidades com conflitos
comunidades_com_conflito = data[data[colunas_tipo_conflito].sum(axis=1) > 0]
# Contar o número de comunidades com conflitos por Estado
comunidades_com_conflito_por_estado = comunidades_com_conflito.groupby('Estado').size().reset_index(name='comunidades_com_conflito')
# Juntar com o dataframe df_estados
df_estados = df_estados.merge(comunidades_com_conflito_por_estado, on='Estado', how='left')
# Substituir NaN por 0 no caso de estados que não têm conflitos
df_estados['comunidades_com_conflito'].fillna(0, inplace=True)
# Calcular a porcentagem de comunidades com conflitos
df_estados["Comunidades com conflito"] = round((df_estados['comunidades_com_conflito'] / df_estados['Comunidades']) * 100)

# corrigindo a falta de acentuação nos conflitos
# Dicionário de substituições
substituicoes = {
    'invasao': 'invasão',
    'queimadas nao controladas': 'queimadas não controladas',
    'conflito por agua': 'conflito por água',
    'contaminacao por agrotoxico': 'contaminação por agrotóxico',
    'mineracao': 'mineração'
}
# Substituir os valores na coluna 'Conflito'
df_conflitos['Conflito'] = df_conflitos['Conflito'].replace(substituicoes)



# INTERFACE - LOAD


# 1. Métricas principais no topo
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<h2><strong>{cadastros}</strong></h2><p style='margin-top: -15px'> comunidades cadastradas<p>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<h2><strong>{total_familias}</strong></h2><p style='margin-top: -15px'>  famílias nos territórios<p>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<h2><strong>{area_total}</strong></h2><p style='margin-top: -15px'> km² mapeados<p>", unsafe_allow_html=True)
st.write('')


# 2. Expanders

# Localização
with st.expander('Localização'):
    col1, col2 = st.columns(2)
    
    with col1:
        st.write('')

        # Número de municípios alcançados
        st.markdown(f"<span style='font-size:22px; font-weight:bold'>{contagem_municipios}</span> <span style='font-size:18px;'>municípios alcançados</span>", unsafe_allow_html=True)
        st.write('')

        # Gráfico de barras
        st.write('**Número de comunidades por bioma:**')
        # Configurar o gráfico
        plt.figure(figsize=(5, 4))
        sns.barplot(x='Bioma', y='count', data=df_biomas, orient='v',  color='#10A37F')
        # Adicionar rótulos (labels) nas barras
        for index, value in enumerate(df_biomas['count']): 
            plt.text(index, value, str(value), ha='center', va='bottom')  
        plt.xlabel('') 
        plt.ylabel('Comunidades')
        plt.xticks(rotation=45, ha='right') # Inclinar os rótulos do eixo x
        plt.yticks([]) # Remover os valores do eixo x
        # Remover a borda do gráfico
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)
        plt.gca().spines['bottom'].set_visible(False)
        plt.gca().spines['left'].set_visible(False)
        plt.tight_layout()  # Ajuste para garantir que todos os elementos do gráfico estejam visíveis
        st.pyplot(plt) # Exibir o gráfico

    with col2:
        st.write('')
        st.write('**Número de comunidades por estado:**')
        st.dataframe(data = df_estados[['Estado', 'Comunidades']], use_container_width=True, hide_index=True )


# Comunidades tradicionais
with st.expander('Comunidades tradicionais'):
    st.write('')

    # Métricas
    st.markdown(f"<span style='font-size:18px;'>Média de </span><span style='font-size:22px; font-weight:bold'>{media_familias_por_comunidade} famílias</span> <span style='font-size:18px;'> por comunidade</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:18px;'>Área média de </span><span style='font-size:22px; font-weight:bold'>{area_media} km²</span> <span style='font-size:18px;'> por comunidade</span>", unsafe_allow_html=True)
    st.markdown(f"<span style='font-size:18px;'>Foram mapeadas comunidades de </span><span style='font-size:22px; font-weight:bold'>{str(cont)} diferentes</span> <span style='font-size:18px;'> segmentos:</span>", unsafe_allow_html=True)
    st.write('')

    # Configurar o gráfico
    plt.figure(figsize=(8, 5))  # Ajuste o tamanho conforme necessário
    sns.barplot(y='Segmento', x='Comunidades', data=df_pctafs_nao_nulo, orient='h', color='#10A37F')
    # Adicionar rótulos (labels) nas barras
    for index, value in enumerate(df_pctafs_nao_nulo['Comunidades']): 
        plt.text(value, index, str(value), ha='left', va='center')  
    plt.xlabel('')  # Remover o rótulo do eixo x
    plt.ylabel('')  # Remover o rótulo do eixo y
    plt.xticks([])  # Remover os valores do eixo x
    plt.gca().spines['top'].set_visible(False) # removendo a moldura
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.tight_layout()
    st.pyplot(plt)  # Exibir o gráfico


# Conflitos
with st.expander('Conflitos'):

    # porcentagem de conflitos
    st.markdown(f"<span style='font-size:22px; font-weight:bold'>{porc_com_conflito}%</span> <span style='font-size:18px;'> das comunidades </span> <span style='font-size:22px; font-weight:bold'>relataram conflitos</span> <span style='font-size:18px;'> no território</span>", unsafe_allow_html=True)

    # número total de conflitos
    st.markdown(f"<span style='font-size:22px; font-weight:bold'>{soma_areas_conflito} áreas de conflito</span> <span style='font-size:18px;'> identificadas </span>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Tabela com porcentagem de comunidades com conflito por estado
        # Ordenar pelo valor numérico da coluna "Comunidades com conflito"
        df_estados = df_estados.sort_values(by="Comunidades com conflito", ascending=False)

        # Concatenar o caractere % aos valores na coluna "Comunidades com conflito" e remover o decimal
        df_estados["Comunidades com conflito"] = df_estados["Comunidades com conflito"].apply(lambda x: f"{int(round(x))}%")

        st.dataframe(df_estados[['Estado','Comunidades com conflito']], hide_index=True)

    with col2:
        st.dataframe(df_conflitos, hide_index=True)
