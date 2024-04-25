import pandas as pd
import streamlit as st
import numpy as np


st.title("Streamlit para o Tô no Mapa")
st.header("Página de teste")

st.write("Exemplo de gráfico")

# Criação de um gráfico simples
data = pd.DataFrame(
    np.random.randn(50, 3),
    columns=['a', 'b', 'c']
)

st.line_chart(data)

# Mostrar um dataframe
st.write("Dataframe aleatório gerado com pandas")
st.write(data)

