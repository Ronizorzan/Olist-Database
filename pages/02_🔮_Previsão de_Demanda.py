import streamlit as st
from functions_module.functions import *
from functions_module.const import *


st.set_page_config("Análise de Dados de Vendas", layout="wide")



#COnfiguração da barra lateral
with st.sidebar:        
    
    dados = carregador_dados(consulta_sql4) # Carregamento do DataFrame diretamente do banco de dados    
    #demanda = st.selectbox("Selecione o tipo de Previsão", ["Prever Demanda", "Prever Vendas"])
    meses_prever = st.slider("Quantos meses gostaria de prever?", min_value=6, max_value=24, value=12, help="Deslize para ajustar o horizonte de previsão")
    processar = st.button("Processar", use_container_width=True)

    st.markdown(markdown, unsafe_allow_html=True) # Informações do desenvolvedor


if processar:
    progresso = st.progress(50, "Processando.... Aguarde um momento!")
    col1, col2 = st.columns([0.55,0.45], gap="medium")

    # Agregação dos dados por mês e categoria
    
    df_monthly = dados.groupby(['mes_ano_compra', 'categoria'])['quantidade_itens_vendidos'].sum().unstack()

    # Seleção das 3 categorias mais vendidas
    top_categories = ['beleza_saude', 'relogios_presentes', 'cama_mesa_banho'] # Categorias Mais Vendidas
    df_top = df_monthly[top_categories]    
    df_top.index = pd.to_datetime(df_top.index)
    df_top = df_top[df_top.index>= "2017-01"].reset_index() # Somente dados limpos e relevantes    
    df_top = df_top.melt(id_vars=["mes_ano_compra"], var_name="categoria", value_name='quantidade_itens_vendidos') # Reorganização para plotagem adequada    
    
    with col1:        
        fig = plot_categories(df_top, 'quantidade_itens_vendidos') # Gráfico de Vendas por categoria
        st.header("Tendência Histórica de Demanda", divider="orange")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)

        st.markdown(""":orange[***Descrição:***] *Esta seção apresenta projeções de demanda para as categorias de produtos mais vendidas,
                    combinando dados históricos com modelos preditivos avançados. O objetivo dessa página é prever a demanda futura,
                    fornecendo insights acionáveis para otimizar a gestão de estoque, refinar estratégias logísticas e impulsionar o crescimento de vendas.*""")
        st.markdown(""":orange[***Foco em Marketing e Vendas:***] *A identificação de tendências e sazonalidades (como as identificadas acima) permite direcionar investimentos em marketing e
                     promoções de forma mais assertiva, capitalizando nos períodos de maior procura e incentivando vendas em períodos de menor demanda.*""")

    with col2:
        # Carregar dados agregados
        df_dados_previsao = df_top.copy()

       # Armazenar todas as previsões
        todas_previsoes = []
        for categoria in top_categories:
           df_categoria_especifica = df_dados_previsao[df_dados_previsao['categoria'] == categoria].copy() # Seleciona somente 1 categoria
            
            # Garantir que 'ds' seja datetime e tratar 'demanda' como numérico
           df_categoria_especifica['mes_ano_compra'] = pd.to_datetime(df_categoria_especifica['mes_ano_compra'])
           df_categoria_especifica['quantidade_itens_vendidos'] = pd.to_numeric(df_categoria_especifica['quantidade_itens_vendidos'])
             
             
             # Cria um range de datas para garantir que todos os meses estejam presentes
                      
           all_months = pd.date_range(start=df_categoria_especifica['mes_ano_compra'].min(),
                                      end=df_categoria_especifica['mes_ano_compra'].max(),
                                        freq='MS')
           full_df = pd.DataFrame({'mes_ano_compra': all_months})   # Preencher meses ausentes com 0 (Prophet lida bem com isso, mas é bom para séries)
           df_categoria_especifica = pd.merge(full_df, df_categoria_especifica, on='mes_ano_compra', how='left').fillna(0)
           df_categoria_especifica['categoria'] = categoria # Re-atribui a categoria após o merge
             
           previsao = prever_demanda_categoria(df_categoria_especifica[['mes_ano_compra', 'quantidade_itens_vendidos']], 'quantidade_itens_vendidos', periodos_futuros=meses_prever)
           previsao['categoria'] = categoria # Adicionar a categoria de volta à previsão
           todas_previsoes.append(previsao)

        df_previsoes_finais = pd.concat(todas_previsoes)
        df_previsoes_finais['yhat'] = df_previsoes_finais['yhat'].astype(int)
        df_previsoes_finais.rename(columns={"ds": "mes_ano_compra", "yhat": 'quantidade_itens_vendidos'}, inplace=True)
        fig2 = plot_categories(df_previsoes_finais, 'quantidade_itens_vendidos')
        fig2.update_layout(yaxis_title="Demanda Prevista")        
        progresso.progress(100, "Previsões Geradas com Sucesso")
        st.header(f"Demanda Prevista (próximos {meses_prever} meses) ", divider="orange")
        st.plotly_chart(fig2, use_container_width=True)        
        st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)

        st.markdown(""":orange[***Otimização de Estoque:***] *As previsões sinalizam períodos de alta demanda, como o final do ano e Black Friday,
                    permitindo um planejamento de estoque proativo para maximizar vendas, ou identificar momentos de baixa para gerenciar excessos.*""")
        st.markdown(""":orange[***Eficiência Logística:***] *Com a visibilidade da demanda futura, é possível antecipar volumes, otimizar a capacidade 
        de entrega e negociação com transportadoras, reduzindo custos de frete.*""")
        #st.dataframe(df_previsoes_finais)        
        
            
