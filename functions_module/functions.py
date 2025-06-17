import psycopg2
from dotenv import load_dotenv
import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from prophet import Prophet


mapeamento_meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: 
                    "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"} #Dicionário para exibição dos meses em português

# Informações do desenvolvedor
markdown = """ 
        <style>.footer {    
        background: linear-gradient(135deg, #a0a0a0, #efefef);
        padding: 12px 17px;
        border-radius: 30px;
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        margin-top: 10px;
        margin-bottom: 15px;
        color: #262730;
        box-shadow: 0 8px 10px rgba(10,10,10,1.0);
    }
    .footer p {
        margin: 6px 0;
    }
    .footer a {
        margin: 0 10px;
        display: inline-block;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-decoration: none;
    }
    .footer a:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }
    .footer img {
        height: 42px;
        width: auto;
        vertical-align: middle;
    }
    </style>
    <div class="footer">
        <p><strong>Desenvolvido por: Ronivan</strong></p>
        <a href="https://github.com/Ronizorzan" target="_blank" title="GitHub">
            <img src="https://img.icons8.com/ios-filled/50/000000/github.png" alt="GitHub">
        </a>
        <a href="https://www.linkedin.com/in/ronivan-zorzan-barbosa" target="_blank" title="LinkedIn">
            <img src="https://img.icons8.com/color/48/000000/linkedin.png" alt="LinkedIn">
        </a>
        <a href="https://share.streamlit.io/user/ronizorzan" target="_blank" title="Projetos Streamlit">
            <img src="https://images.seeklogo.com/logo-png/44/1/streamlit-logo-png_seeklogo-441815.png" alt="Streamlit Community">
        </a>
    </div>
    """ 

#Função de Carregamento dos dados 
@st.cache_data
def carregador_dados(consulta):
    """Carrega os dados diretamente do banco de dados
    Parâmetros: consulta - Consulta SQL à ser pesquisada
    Retorno: df - DataFrame com os dados retornados pela consulta"""
    
    try:
        # Carregar as variáveis do arquivo .env
        load_dotenv('config.env')

        # Obter credenciais
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

        cur = conn.cursor()
        cur.execute(consulta)
        results = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        df = pd.DataFrame(results, columns=columns)
    
    finally:
        if cur in locals():
            cur.close()

        if conn in locals():
            conn.close()   

                
    return df



#Função de Geração dos Cálculos E Gráficos
@st.cache_resource
def gerador_calculos(data, coluna_data, coluna_id, coluna_categoria, coluna_valor, datas):
    data = data.set_index(coluna_data)
    data.index = pd.to_datetime(data.index, format="mixed") 
    
    clv = data.groupby(coluna_id)[[coluna_valor]].sum().mean() # Soma o valor vitalício do cliente através de TODOS os clientes

    #Cálculos Principais e preparação dos dados    
    if len(datas)==2: #Filtra os meses se especificado                    
        data = data.loc[(data.index >= pd.to_datetime(datas[0], format="%d-%m-%Y")) & (data.index <= pd.to_datetime(datas[1], format="%d-%m-%Y"))]
    elif len(datas)==1:
        data = data.loc[data.index >= pd.to_datetime(datas[0], format="%d-%m-%Y")]

    data[coluna_id] = data[coluna_id].astype(str) #Transforma a coluna de identificação em string para plotagem adequada    
    total_vendas = data[coluna_valor].sum() # Total em Vendas
    vendas_por_categoria = data.groupby(coluna_categoria)[[coluna_valor]].sum().nlargest(10, coluna_valor)   #Top 10 categorias mais vendidas
    vendas_mensais = data.resample("MS")[[coluna_valor]].sum() 
    crescimento_perc = vendas_mensais[[coluna_valor]].pct_change() *100  #Crescimento percentual          
                               
    return data, clv, total_vendas, vendas_por_categoria, vendas_mensais, crescimento_perc

#Função de Geração dos Cálculos E Gráficos
@st.cache_resource
def filtro_datas(data, coluna_data, datas):
    data = data.set_index(coluna_data)
    data.index = pd.to_datetime(data.index, format="mixed") 
   

    #Filtragem dos dados    
    if len(datas)==2: #Filtra os meses se especificado                    
        data = data.loc[(data.index >= pd.to_datetime(datas[0], format="%d-%m-%Y")) & (data.index <= pd.to_datetime(datas[1], format="%d-%m-%Y"))]
    elif len(datas)==1:
        data = data.loc[data.index >= pd.to_datetime(datas[0], format="%d-%m-%Y")]
    
    return data




# Gráficos da página de desempenho geral
def plot_desempenho_geral(vendas_por_categoria, vendas_mensais, coluna_valor):        
        categoria_mais_vendida = vendas_por_categoria[vendas_por_categoria[coluna_valor]== vendas_por_categoria[coluna_valor].max()]
        grafico_categoria = px.bar(vendas_por_categoria, vendas_por_categoria.index, vendas_por_categoria[coluna_valor],  color=vendas_por_categoria[coluna_valor],
                                    color_continuous_scale=['#ff6600', '#0070f3'], labels={coluna_valor: "Total Vendido"},
                            title=f"{(categoria_mais_vendida.index[0]).capitalize()} se destaca entre as categorias mais vendidas com um total de {categoria_mais_vendida[coluna_valor].iloc[0]:,.2f} ")
        
        grafico_categoria.update_layout(xaxis_title="Top 10 Categorias", yaxis_title="Total Vendido em cada categoria", template="plotly_dark")

        grafico_categoria.update_traces(text=vendas_por_categoria[coluna_valor].apply(lambda x: f"R$ {x:,.2f}"), textposition="none", hovertemplate="Total vendido: R$%{text}<br>Categoria: %{x} ")    


        #Gráfico de Vendas Mensais
        vendas_mensais = vendas_mensais.sort_index(ascending=False).iloc[:12,:]
        melhor_mes = vendas_mensais[vendas_mensais[coluna_valor]== vendas_mensais[coluna_valor].max()]
        pior_mes = vendas_mensais[vendas_mensais[coluna_valor]== vendas_mensais[coluna_valor].min()]
        grafico_mensal = px.bar(vendas_mensais, vendas_mensais.index, vendas_mensais[coluna_valor],
                                color_continuous_scale=['#ff6600',  '#0070f3'], color=vendas_mensais[coluna_valor], labels={coluna_valor: "Vendas Mensais"},
            title=f"O mês de {mapeamento_meses[melhor_mes.index.month[0]]} de {melhor_mes.index.year[0]} se destaca com um total de R${melhor_mes[coluna_valor].iloc[0]:,.2f} vendido")
                      
        
        grafico_mensal.update_layout(yaxis_title="Total Mensal em Vendas", xaxis={"tickangle": 0}, 
                    xaxis_title=f"{mapeamento_meses[pior_mes.index.month[0]]} de {pior_mes.index.year[0]} foi o mês de menor faturamento: R${pior_mes[coluna_valor].iloc[0]:,.2f} ") 

        grafico_mensal.update_traces(text=vendas_mensais[coluna_valor].apply(lambda x: f"{x:,.2f}"), textposition="none", hovertemplate="Vendas Totais: R$%{text}<br>Mês: %{x} ")


        return grafico_categoria, categoria_mais_vendida, grafico_mensal, melhor_mes, pior_mes


# Gráficos da página Tendência de Vendas
def plot_tendencia(crescimento_perc, vendas_mensais, coluna_valor, meta):
        
        
        # Preparação dos dados              
        crescimento_perc = crescimento_perc.sort_index(ascending=False).iloc[:12,:]
        x = np.arange(len(crescimento_perc))  # Criando índices numéricos para os meses
        y = crescimento_perc[coluna_valor].values  # Valores de crescimento percentual

        melhor_porc = crescimento_perc[crescimento_perc[coluna_valor]== crescimento_perc[coluna_valor].max()]
        pior_porc = crescimento_perc[crescimento_perc[coluna_valor]== crescimento_perc[coluna_valor].min()]
        
        # Criar gráfico principal
        grafico_crescimento = px.line(crescimento_perc, x=crescimento_perc.index, y=crescimento_perc[coluna_valor], markers=True, color_discrete_sequence=["#0070f3"],
                    title=f"O mês de {mapeamento_meses[melhor_porc.index.month[0]]} de {melhor_porc.index.year[0]} apresentou<br>um crescimento percentual nas vendas de {melhor_porc[coluna_valor].iloc[0]:,.2f}%")

        # Ajuste polinomial (grau 1 para tendência)
        coef = np.polyfit(x, y, 1)
        poly = np.poly1d(coef)

        # Geração de pontos para a linha de tendência
        x_fit = x  # Mantendo a escala original
        y_fit = poly(x_fit)  # Aplicando a função polinomial

        grafico_crescimento.update_layout(yaxis_title="Variação Percentual(%)", 
            xaxis_title=f"{mapeamento_meses[pior_porc.index.month[0]]} de {pior_porc.index.year[0]} aprensentou um desempenho negativo <br>com uma variação de {pior_porc[coluna_valor].iloc[0]:,.2f}% nas vendas")

        grafico_crescimento.update_traces(text=crescimento_perc[coluna_valor], hovertemplate="Variação Percentual nas Vendas: %{y}%<br>Mês: %{x}",
                           marker=dict(color="#ff6600"))

        # Adicionar linha de tendência polinomial corrigida
        grafico_crescimento.add_scatter(x=crescimento_perc.index, y=y_fit, mode='lines', name="Tendência", line=dict(dash="dash", color="#f7fbff")) # Adição da linha de tendência        
        

        # Gráfico de soma cumulativa
        soma_cumulativa = vendas_mensais[coluna_valor].cumsum() # Soma Cumulativa
        if len(soma_cumulativa)> 12:
            soma_cumulativa = soma_cumulativa.sort_values(ascending=False).head(12) # Localização dos 12 últimos meses para maior consistência nas análises

        # Atualiza o valor da meta
        if meta is not None:
             pass
        else:
             meta = 4e+5 * len(soma_cumulativa) # Valor padrão da meta: (400 mil x meses)

        distancia_meta = meta - soma_cumulativa.values.max() # diferença entre a meta e o valor vendido no período
        data_batimento = soma_cumulativa.index[soma_cumulativa.values >= meta] # Pega a data do batimento da meta (primeira ocorrência)
        data_batimento = pd.to_datetime(data_batimento)
        title_text = f"Valor faltante em relação ao objetivo: {distancia_meta:,.2f} " if distancia_meta >0 else f"Meta estipulada: {meta:,.2f}<br>Mês de batimento da meta: {mapeamento_meses[data_batimento.month[0]]}"
        grafico_soma_cumulativa = px.bar(
            soma_cumulativa, soma_cumulativa.index, soma_cumulativa.values, 
            color=soma_cumulativa.values, color_continuous_scale=['#ff6600', '#0070f3'],
            title=title_text, labels={"color": "Valores Acumulados"}
        )

        # Atualização com títulos e linha de meta
        title_x = f"Ultrapassou a meta em {np.abs(distancia_meta):,.2f} " if distancia_meta <0 else f"Vendas Acumuladas no período: {soma_cumulativa.values.max():,.2f} "
        grafico_soma_cumulativa.update_layout(
            xaxis_title=title_x, yaxis_title="Acúmulo das Vendas", template="plotly_dark"
        )
        grafico_soma_cumulativa.update_traces(
            text=soma_cumulativa.values, textposition="none", 
            hovertemplate="Vendas acumuladas atualmente: R$%{y}<br>Data: %{x}"
        )
        grafico_soma_cumulativa.add_hline(
            y=meta,  annotation=dict(text="Meta de Faturamento"), annotation_position="top left",
            line=dict(dash="dash", color="#f7fbff") )  # Adiciona a Linha de meta

        
        return grafico_crescimento, grafico_soma_cumulativa, melhor_porc, pior_porc, distancia_meta


def plot_tops(df, coluna1, coluna2, titulo1, titulo2, label1, label2):
    """Retorna dois gráficos.
    fig1 - Retorna um gráfico dos estados que 
    geraram as maiores receitas no período
    fig2 - Retorna um gráfico com os menores fretes
    médios pagos por região.
    """
    tops = df.nlargest(10, coluna1) # Dataframe com os maiores valores
    fig1 = px.bar(tops, x='estado', y=coluna1,
                                    title=titulo1, labels={coluna1: label1},
                                    color=tops[coluna1], color_continuous_scale=['#ff6600', '#0070f3'])  
    fig1.update_traces(text=tops[coluna1].apply(lambda x: f"R$ {x:,.2f} "), textposition="none", hovertemplate="Estado: %{x}<br>Receita Total: %{text}R$")                                  
    
        
    df[coluna2] = df[coluna2].astype(float)
    smallest = df.nsmallest(10, coluna2) # Dataframe com os menores valores
    fig2 = px.bar(smallest, x='estado', y=coluna2,
                                    title=titulo2, labels={coluna2: label2},
                                    color=smallest[coluna2], color_continuous_scale=['#ff6600', '#0070f3'])
    fig2.update_traces(text=smallest[coluna2].apply(lambda x: f"R$ {x:,.2f} "), textposition="none", hovertemplate="Estado: %{x}<br>Frete Médio: %{text}R$")
    

    return fig1, fig2


def plot_smallest(df, coluna1, coluna2, titulo1, titulo2, label1, label2): 
    """Retorna dois gráficos.
    fig1 - Retorna um gráfico dos estados que 
    geraram as menores receitas no período
    fig2 - Retorna um gráfico com os maiores fretes
    médios pagos por região.
    """  
    tops1 = df.nsmallest(10, coluna1) # Dataframe com os menores valores
    fig1 = px.bar(tops1, x='estado', y=coluna1,
                                    title=titulo1, labels={coluna1: label1},
                                    color=tops1[coluna1], color_continuous_scale=['#ff6600', '#0070f3'])   
    fig1.update_traces(text=tops1[coluna1].apply(lambda x: f"R$ {x:,.2f} "), textposition="none", hovertemplate="Estado: %{x}<br>Receita Total: %{text}R$")
    fig1.update_layout(xaxis_title="Estado")
    
        
    df[coluna2] = df[coluna2].astype(float)
    tops2 = df.nlargest(10, coluna2) # Dataframe com os maiores valores
    fig2 = px.bar(tops2, x='estado', y=coluna2,
                                    title=titulo2, labels={coluna2: label2},
                                    color=tops2[coluna2], color_continuous_scale=['#ff6600', '#0070f3'])
    fig2.update_traces(text=tops2[coluna2].apply(lambda x: f"R$ {x:,.2f} "), textposition="none", hovertemplate="Estado: %{x}<br>Frete Médio Total: %{text}R$")
    fig2.update_layout(xaxis_title="Estado")

    return fig1, fig2


@st.cache_resource
def plot_scatter_map(
    df,
    lat_col: str   = "latitude",

    
    lon_col: str   = "longitude",
    value_col: str = "valor",
    hover_col: str = None,
    mapbox_style: str = "carto-positron",
    color_scale = ["#0070f3", "#ff6600"],
    zoom: float = 3.9,
    center: dict = None,
    mapbox_token: str = None,
    title: str = "Onde estão concentradas as maiores compras.",
    label_name: str = "Valor da Compra"
):
    """
    Plota um mapa de pontos, onde o tamanho e a cor
    representam uma métrica (ex.: compras).
    
    Parâmetros:
    - df: pandas.DataFrame com suas colunas geográficas + métrica.
    - lat_col / lon_col: nome das colunas de latitude/longitude.
    - value_col: métrica a ser exibida (e.g. valor).
    - hover_col: coluna extra para mostrar no hover.
    - mapbox_style: estilo do fundo (ex.: 'open-street-map', 'carto-positron').
    - color_scale: lista de cores contínuas.
    - zoom: nível de zoom inicial.
    - center: dict {'lat':…, 'lon':…}. Se None, centraliza pelos dados.
    - mapbox_token: token Mapbox (para usar estilos privados).
    - title: Título à ser exibido no gráfico
    - label_name: Legenda customizada da 'colorbar'
    
    Retorno:
    - fig: plotly.graph_objects.Figure
    """
    if mapbox_token:
        px.set_mapbox_access_token(mapbox_token)

    # centraliza no conjunto de dados, caso não seja informado center
    if center is None:
        center = {
            "lat": df[lat_col].mean(),
            "lon": df[lon_col].mean()
        }
    
    fig = px.scatter_mapbox(
        df, lat=lat_col, lon=lon_col,
        size=value_col, color=value_col,
        hover_name=hover_col,
        color_continuous_scale=color_scale,
        size_max=25, zoom=zoom, center=center,
        mapbox_style=mapbox_style,
        labels={value_col: label_name}
    )
    fig.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        title=title
    )
    
    return fig

def plot_categories(df_melted, demanda):
    """
    Função para plotar um gráfico de linhas interativo com Plotly.
    
    Parâmetros:
    df_melted (DataFrame): DataFrame no formato longo (melted) com colunas 'mes_ano_compra', 'categoria' e 'receita'.
    
    Retorno:
    Exibe um gráfico interativo.
    """    
    
    pico_demanda = df_melted.loc[df_melted[demanda]==df_melted[demanda].max()].reset_index()
    pico_demanda['mes_ano_compra'] = pd.to_datetime(pico_demanda['mes_ano_compra'], format="mixed")
    pico_demanda['mes_ano_compra'] = pico_demanda['mes_ano_compra'].dt.month
    fig = px.line(df_melted, 
                  x="mes_ano_compra", 
                  y=demanda,
                  color_discrete_sequence=['#ff6600', '#0070f3', '#f9f9fb'],
                  color="categoria",
                  title=f"Pico de demanda em {mapeamento_meses[pico_demanda['mes_ano_compra'][0]]} ",
                  labels={"mes_ano_compra": "Data", "categoria": "Categoria", "quantidade_itens_vendidos": "Demanda"},
                  markers=True)
    
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Total de Itens Vendidos",
        legend_title="Categorias",
        hovermode="x unified",
        template="plotly_white"
    )   
    
    return fig



def prever_demanda_categoria(df_historico_categoria, demanda, periodos_futuros=12):
    """
    Treina um modelo Prophet para uma única categoria e gera previsões.

    Args:
        df_historico_categoria (pd.DataFrame): DataFrame com colunas 'ds' (data) e 'y' (demanda).
        demanda (str): Nome da coluna que contém os valores de demanda.
        periodos_futuros (int): Número de meses futuros para prever.

    Returns:
        pd.DataFrame: DataFrame com as previsões (colunas 'ds', 'yhat', 'yhat_lower', 'yhat_upper').
    """
    # Renomear colunas para o formato exigido pelo Prophet
    df_prophet = df_historico_categoria.rename(columns={'mes_ano_compra': 'ds', demanda: 'y'}).fillna(0)

    # Criar e treinar o modelo Prophet
    model = Prophet(seasonality_mode='multiplicative', changepoint_prior_scale=0.1,
                    seasonality_prior_scale=15.0, yearly_seasonality=5)  # Ajuste de parâmetros importantes
    model.fit(df_prophet)

    # Identificar a última data do histórico e adicionar um mês
    ultima_data = df_prophet['ds'].max()
    future_start = ultima_data + pd.DateOffset(months=1)

    # Criar DataFrame com datas futuras para previsão
    future = model.make_future_dataframe(periods=periodos_futuros, freq='MS')  # 'MS' para início do mês
    future = future[future['ds'] >= future_start]  # Garantir que começa um mês após o último dado

    # Gerar previsões
    forecast = model.predict(future)

    # Retornar apenas as colunas relevantes para a previsão
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']] # Os intervalos de confiança serão usados nas futuras versões do projeto
