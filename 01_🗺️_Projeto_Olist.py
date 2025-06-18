import streamlit as st
from functions_module.functions import *
from functions_module.const import *


st.set_page_config("Análises Principais", layout="wide")



#COnfiguração da barra lateral
try:
    dados_completos = carregador_dados(consulta_sql) # Carregamento do DataFrame para as análises principais         
    dados_geograficos = carregador_dados(consulta_sql2) # Carregamento do DataFrame para as análises geográficas
    dados_receitas = carregador_dados(consulta_sql3) # Carregamento do DataFrame para as análises de receitas e fretes 
    
    # Os dados não serão salvos recorrentemente para tornar a aplicação mais fluida
    #dados_completos.to_csv("dados_completos.csv")
    #dados_geograficos.to_csv("dados_geograficos.csv")
    #dados_receitas.to_csv("dados_receitas.csv")

# Carregamento dos DataFrame com os últimos dados obtidos caso ocorra algum erro no banco de dados
except Exception as e:
    #st.warning(f"Falha na conecção com o banco de dados. Erro encontrado: {e}. Utilizando dados alternativos.")
    dados_completos = pd.read_csv("dados_completos.csv") 
    dados_geograficos = pd.read_csv("dados_geograficos.csv") 
    dados_receitas = pd.read_csv("dados_receitas.csv" )

with st.sidebar:    
    st.markdown(":orange[**Configuração das Análises**]")    
    
    with st.expander("Selecionar o tipo de visualização", expanded=True):
        visualizacao = st.radio("Selecione o tipo de análise", ["Desempenho Geral", "Metas e Variações", "Maiores Receitas vs Frete", 
                                                    "Menores Receitas vs Frete", "Compras por Concentração"], help="Selecione o tipo de análise que gostaria de visualizar")
        
    st.markdown(":orange[**Gostaria de personalizar as visualizações?**]", help="Selecione as configurações abaixo para a exibição de datas e metas", unsafe_allow_html=False)
    with st.expander(":orange[Configurações adicionais]"):        
        datas = st.date_input("Insira 1 ou 2 datas para filtrar nos gráficos", [], help="Escolha uma única data se quiser inserir apenas a data inicial,\
                                \n ou duas se quiser filtrar data inicial e final, respectivamente.")
        meta = st.number_input("Estipular meta", value=None, max_value=len(dados_completos)* 0.4e+3) 
            
    with st.expander(":orange[Conexão com banco de dados - Não alterar\
                        \n(em desenvolvimento)]", expanded=False):
        coluna_data = st.selectbox("Selecione a coluna de data", dados_completos.columns, index=0)    
        coluna_id = st.selectbox("Selecione a coluna de identificação do cliente", dados_completos.columns, index=1)
        coluna_categoria = st.selectbox("Selecione a coluna de categoria", dados_completos.columns, index=2)
        coluna_valor = st.selectbox("Selecione a coluna de Valor", dados_completos.columns, index=3)           


    processar = st.button("Processar", use_container_width=True)

    st.markdown(markdown, unsafe_allow_html=True) # Informações do desenvolvedor

if processar:
    dados_filtrados, clv, total_vendas, vendas_por_categoria, vendas_mensais, crescimento_perc, soma_cumulativa = gerador_calculos(dados_completos, coluna_data, coluna_id, coluna_categoria, coluna_valor, datas)
    
    # Filtragem de datas para as outras consultas no banco de dados
    if len(datas)>0:
        dados_geograficos = filtro_datas(dados_geograficos, coluna_data, datas) # Filtra os dados se filtros de data forem aplicados

    #Página Visão Geral
    if visualizacao=="Desempenho Geral":
        grafico_categoria, categoria_mais_vendida, grafico_mensal, melhor_mes, pior_mes = plot_desempenho_geral(vendas_por_categoria, vendas_mensais, coluna_valor)
        col1, col2 = st.columns(2)
        with col1:
            st.header("Líderes de Venda", divider='orange')
            st.plotly_chart(grafico_categoria, use_container_width=True, theme="streamlit" )

            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            dados_completos_date = dados_completos.set_index(coluna_data) # Será usado para períodos de comparação            
            st.markdown(f":orange[***Período disponível no conjunto de dados completo:***] *De ***{(dados_completos_date.index.date.min()).strftime('%d-%m-%Y')}*** até* ***{(dados_completos_date.index.date.max()).strftime('%d-%m-%Y')}*** ")

            df_nulos = dados_filtrados.reset_index().loc[:, [coluna_data, coluna_id, coluna_categoria, coluna_valor]] # Verificação e remoção de valores nulos             
            if df_nulos.isnull().values.any(): # Verifica se existem valores nulos no dataframe
                nulos = df_nulos.isnull().sum().sum() # Soma todos os valores nulos para exibição na aplicação
                data = dados_filtrados.reset_index().dropna() # Remove valores nulos do dataframe para evitar erros nos gráficos
                data = data.set_index(coluna_data) # Reconfiguração do índice do dataframe com a coluna de data

            dados_copy = dados_completos.copy() 
            #dados_copy = dados_copy.set_index(coluna_data)
            dados_copy.index = pd.to_datetime(dados_copy.index, format = "mixed")            
                
            # Exibir insights dinâmicos            
            st.markdown(f""":orange[***Ação:***] *A categoria **{categoria_mais_vendida.index[0].capitalize()}** lidera as vendas, totalizando **R${categoria_mais_vendida[coluna_valor].iloc[0]:,.2f}**.
                        Criar campanhas específicas para **{categoria_mais_vendida.index[0].capitalize()}**, destacando produtos mais vendidos e
                        priorizar estoque para categorias que puxam o faturamento pode otimizar ainda mais os resultados.*""")
            if len(datas) >0: # Se filtros de datas forem aplicados
                dados_agrupados = dados_filtrados.copy()  # Trabalhar com uma cópia do período filtrado
                dados_agrupados = dados_agrupados.resample("MS")[coluna_valor].sum()  # Totais somados mensalmente
                soma_periodo_atual = dados_agrupados.sum()  # Soma total do período atual
                
                # Ajuste da data inicial dos meses anteriores
                inicio_periodo_anterior = dados_agrupados.index.min() - pd.DateOffset(months=len(dados_agrupados))

                # Filtragem do período anterior
                dados_completos_copy = dados_completos.dropna().copy()
                dados_completos_copy[coluna_data] = pd.to_datetime(dados_completos_copy[coluna_data], format='mixed')
                dados_completos_copy = dados_completos_copy.set_index(coluna_data)[coluna_valor].resample("MS").sum()                
                periodo_anterior = dados_completos_copy.loc[
                    (dados_completos_copy.index >= inicio_periodo_anterior) & (dados_completos_copy.index < dados_agrupados.index.min())
                ]
                soma_periodo_anterior = periodo_anterior.sum()  # Soma total do período anterior
                                                        
                st.markdown(":orange[**Desempenho das Vendas em relação ao período anterior.**]")              
                variacao_absoluta = soma_periodo_atual - soma_periodo_anterior
                sinal = "+" if variacao_absoluta >=0 else ""        
                st.metric(label=f"*Período disponível para comparação:* ***{len(periodo_anterior)} meses.***",
                            value=f"R$ {sinal} {(variacao_absoluta):,.2f}", delta=f"{((soma_periodo_atual / soma_periodo_anterior) - 1)* 100:,.2f}%", delta_color="normal") 

                if len(periodo_anterior)< len(dados_agrupados): # Aviso se o conjunto de dados não for grande o suficiente para gerar uma comparação adequada
                    st.warning(f"""*O conjunto de dados não é grande o suficiente para gerar um período de comparação compatível.
                                Há apenas {len(periodo_anterior)} meses restantes para o período de comparação,
                                mas foram utilizados {len(dados_agrupados)} meses na análise principal.
                                Para uma análise mais precisa filtre um período de tempo menor.*""")   
            else:
                st.markdown(":orange[***Informação importante:***] *Utilize as configurações adicionais na barra lateral para filtrar datas específicas. " \
                "Ao filtrar as datas uma comparação entre períodos será exibida, mas note que essa comparação é limitada aos dados disponíveis no conjunto de dados.*")           
    
                                       
            
        with col2:
            st.header("Desempenho Mensal", divider='orange')
            st.plotly_chart(grafico_mensal, use_container_width=True)   
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)

            st.markdown(f":orange[CLV:] *Valor médio que um cliente gasta durante todo o período como cliente da empresa:\
                         <span style='color: orange; font-size: 20px'>R$ {clv.iloc[0]:,.2f}</span>\
                        \n:orange[Ação] A métrica acima deve ser acompanhada de perto e maximizada utilizando estratégias como\
                        \ncross-selling, up-selling e otimização do ticket médio.*", unsafe_allow_html=True) # Exibição do CLV
            
            st.markdown(f":orange[***Ação:***] *O mês de ***{mapeamento_meses[melhor_mes.index.month[0]]}*** de ***{melhor_mes.index.year[0]}***\
                        registrou o maior faturamento, totalizando **R${melhor_mes[coluna_valor].iloc[0]:,.2f}**.\
                            \nEstratégias sazonais podem ser otimizadas para esse período.*")
            st.markdown(f"*Em contraste, ***{mapeamento_meses[pior_mes.index.month[0]]}*** de ***{pior_mes.index.year[0]}***\
                         teve o menor desempenho, com R$ ***{pior_mes[coluna_valor].iloc[0]:,.2f}***. Avaliar causas e ajustar ações para ambos pode melhorar significativamente os resultados.*")            
                
                 
            if df_nulos.isnull().values.any(): # Exibição de valores nulos na aplicação para maior transparência (se encontrados)
                st.warning(f"Foram detectados {nulos} valores nulos no conjunto de dados. Esses valores serão desconsiderados nas análises. ")
            
                 

    if visualizacao =="Metas e Variações":
        grafico_crescimento, grafico_soma_cumulativa, melhor_porc, pior_porc, distancia_meta = plot_tendencia(crescimento_perc, soma_cumulativa, coluna_valor, meta)
        col1, col2 = st.columns([0.45,0.55])
        with col1:
            st.header("Monitoramento sazonal", divider='orange')
            st.plotly_chart(grafico_crescimento, use_container_width=True)
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            st.markdown(f""":orange[***Monitoramento de Crescimento e Retração:***] *Picos como o de **{round(melhor_porc[coluna_valor].iloc[0], 2)}%**
                        em ***{mapeamento_meses[melhor_porc.index.month[0]]}*** de ***{melhor_porc.index.year[0]}***
                        podem indicar uma campanha bem-sucedida ou um aumento na demanda. Replicar ou otimizar essa estratégia pode gerar novos impulsos de vendas.*""")
            
            st.markdown(f""" *A retração de ***{np.abs(pior_porc[coluna_valor].iloc[0]):,.2f}%*** em ***{mapeamento_meses[pior_porc.index.month[0]]}*** de ***{pior_porc.index.year[0]}***
                        sugere um impacto negativo, possivelmente devido a fatores externos ou mudanças no comportamento do consumidor.
                        Avaliar causas e efeitos pode  ajustar soluções pode evitar quedas futuras.*""")

        with col2:
            st.header("Acompanhamento de Metas", divider='orange')
            st.plotly_chart(grafico_soma_cumulativa, use_container_width=True)
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            if distancia_meta <0:
                st.markdown(f""":orange[***Expectativa de desempenho alcançada:***] *O gráfico de metas mostra que a empresa ultrapassou a meta de faturamento esperada,
                        atingindo um superávit de R$ {np.abs(distancia_meta):,.2f}. Isso demonstra um desempenho sólido e abre espaço para novas metas ainda mais ambiciosas.*""")
            else:
                st.markdown(f""":orange[***Expectativa de desempenho não alcançada:***] *O gráfico indica que o objetivo ainda não foi alcançado. Valor faltante: R$ {distancia_meta:,.2f}
                            Se o valor está muito longe do esperado ajustes podem ser necessários para manter o crescimento sustentável e garantir o objetivo.*""")
                
            st.markdown(":orange[***Informação:***] *A meta de faturamento pode ser ajustada em configurações adicionais na barra lateral ao lado.*")
                                
                
    if visualizacao=="Maiores Receitas vs Frete":                
        grafico_receita, grafico_pedidos = plot_tops(dados_receitas, "receita_total_vendas", "frete_medio", 
                                                   "Receita Total Gerada", "Menores Fretes", "Receita Total", "Frete Médio")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Maior Concentração de Receita", divider="orange")            
            st.plotly_chart(grafico_receita, use_container_width=True)
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            st.markdown(f""":orange[***Ação:***] *O ponto chave aqui é a eficiência logística e frete acessível. Em um cenário ideal **MAIOR RECEITA** representa **FRETE MAIS BARATO.**
                        Priorizar o investimento em marketing e estoque nessas áreas, é uma estrátegia para aumentar ainda mais a lucratividade e a  eficiência logística. 
                        Além de analisar mais profundamente o que as torna eficientes para replicar em outras áreas.*""")
        
        with col2:
            st.header("Fretes mais acessíveis", divider="orange")
            st.plotly_chart(grafico_pedidos, use_container_width=True)
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            st.markdown(f""":orange[***Ação:***] *Por outro lado, se uma região gera uma receita expressiva, mas possui custos de frete elevados,
                        isso pode significar perda de potenciais clientes e margem de lucro comprometida.*""")
            st.markdown(""" :orange[***Algumas perguntas à se fazer são:***] *É possível otimizar rotas? É possível abrir um centro de distribuição mais próximo?
                    O preço do produto pode ser ajustado (aumentado) para absorver parte do custo do frete, sem perder competitividade?
                    Há margem para negociar melhores taxas de frete para essas rotas?
                    Implementar estratégias como frete grátis apenas acima de certo valor para essa região, ou desconto para produtos adicionais?*""")

    if visualizacao=="Menores Receitas vs Frete":
        grafico_menor_receita, grafico_maior_frete = plot_smallest(dados_receitas, "receita_total_vendas", "frete_medio", 
                                                   "Receita Total Gerada", "Maiores Fretes", "Receita Total", "Frete Médio")
        col1, col2 = st.columns(2)
        with col1:
            st.header("Menor Concentração de Receita", divider="orange")
            st.plotly_chart(grafico_menor_receita, use_container_width=True)
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            st.markdown(""":orange[***Ação:***] *Em um cenário onde a receita é baixa e os fretes caros incentivar o aumento do ticket médio
                        (com cross-selling, up-selling) para diluir o custo do frete por item pode ser uma boa alternativa para aumentar o engajamento dos clientes.
                        Buscar parceiros logísticos mais eficientes para essas rotas e oferecer cupons para compras maiores também são estratégias que podem impulsionar a lucratividade na região.*""")
            st.markdown(""":orange[***Visão Macro (Análise atual):***] Oferecem uma visão de alto nível do desempenho regional. É possível identificar rapidamente os estados que mais contribuem para a
                         receita total e os estados onde o custo médio de frete é mais alto. """)
            st.markdown(""":orange[***Ideal para decisões estratégicas, como:***] Onde concentrar esforços de marketing ou expansão de vendedores.
                        Quais estados podem ter uma margem de lucro menor devido ao frete alto, mesmo que tenham boa receita.
                        Avaliar a necessidade de novos centros de distribuição em regiões de alta receita/volume ou para otimizar fretes em estados vizinhos.""")

        with col2:
            st.header("Fretes menos acessíveis", divider="orange")
            st.plotly_chart(grafico_maior_frete, use_container_width=True)
            st.markdown("<hr style='border:1px solid #0070f3'>", unsafe_allow_html=True)
            st.markdown(""":orange[***Ação:***] *Regiões com baixo volume de vendas, mas que são eficientes em termos de custo de frete podem ser "oportunidades ocultas" ou "mercados em crescimento".
                Direcionar campanhas de marketing de baixo custo para essas regiões subexploradas para tentar alavancar o volume de vendas, dado que a logística já é eficiente.
                Considerar expandir a oferta de produtos nessas áreas, ajustando preços de produtos com base na demanda regional e nos custos de frete.*""")  

            st.markdown(":orange[***Concentração de Compras:***] *A análise abaixo opera em uma granularidade muito mais fina: no nível de transação individual (ou localização específica), representada por latitude e longitude.*")
            st.markdown(""":orange[***Valor e Insights:***] *Identificação de Outliers e Pontos de Destaque: Permite identificar pontos específicos (endereços de clientes)
                    onde ocorreram as maiores vendas ou onde os fretes foram exorbitantemente caros. Isso é crucial para investigar casos extremos.*""")            

    if visualizacao=="Compras por Concentração":                
        col1, col2 = st.columns([0.62,0.38], gap="medium")
        with col1:
            fig = plot_scatter_map(dados_geograficos, center={"lat": -14.2350, "lon": -51.9253})
            st.plotly_chart(fig, use_container_width=True)            
            fig2 = plot_scatter_map(dados_geograficos, value_col="frete", title="Otimização de Logística: Quais clientes pagam os maiores fretes?",
                                    center={"lat": -14.2350, "lon": -51.9253}, label_name="Valor do Frete")
            st.plotly_chart(fig2, use_container_width=True)            
        with col2:
            maior_compra = dados_geograficos.loc[dados_geograficos["valor"]== dados_geograficos["valor"].max()] # Localização da Maior compra
            maior_frete = dados_geograficos.loc[dados_geograficos["frete"]== dados_geograficos["frete"].max()] # Localização do Maior frete
            st.subheader("Análise Geoespacial: Maiores Compras ", divider="orange", help="As bolhas representam vendas individuais.\
                         \nBolhas maiores e com cores diferentes representam as maiores vendas.")
            
            st.markdown(""":orange[***Descrição:***] *A maioria das compras estão concentradas no Sul e Sudeste, indicando forte poder aquisitivo.\
                    \n:orange[Ação:] Otimizar centros de distribuição para reduzir tempos de entrega e custos operacionais otimizando os lucros e a eficiência operacional nessas localidades*""")
            st.markdown(f""":orange[Compra Expressiva:] *A maior compra realizada no período foi de <span style='font-size:22px; font-weight:bold'> {(maior_compra["valor"].values[0]):,.2f} R$$</span>
                        com a seguinte localização: latitude <span style='font-size:22px; font-weight:bold'>{maior_compra["latitude"].values[0]}</span>
                         e longitude <span style='font-size: 22px; font-weight:bold'>{maior_compra["longitude"].values[0]}.</span>\
                        \nO frete pago pelo cliente foi de* <span style='font-size:22px; font-weight:bold'> {maior_compra["frete"].values[0]:,.2f}R$.</span>""", unsafe_allow_html=True)
            
            st.markdown(""":orange[Ação:] *Utilizar essas informações para implementar segmentação geográfica personalizada, 
                otimizando campanhas e ofertas baseadas nos padrões de consumo da região. 
                Otimizar centros de distribuição e realocar produtos mais vendidos em diferentes regiões.*""", unsafe_allow_html=True)

            st.markdown("")
            st.markdown("")
            st.markdown("")
            st.markdown("")
            
            st.subheader("Análise Geoespacial: Maiores Fretes", divider="orange", help="De forma análoga ao gráfico ao lado, cada bolha representa uma venda.\
                         \nBolhas maiores e com cores diferentes representam os fretes mais caros.")
            st.markdown(""":orange[***Descrição:***] *Altos custos logísticos identificados em regiões mais afastadas da base de clientes.
                            Esses custos podem impactar negativamente a conversão de vendas.*""")
            st.markdown(""":orange[Ação:] *Explorar subsídios ou parcerias logísticas para reduzir custos e melhorar experiência do cliente.
                        Renegociar contratos com transportadoras e otimizar rotas para reduzir custos operacionais e mitigar impactos do frete.*""")
            
            st.markdown(f""":orange[***Frete Expressivo***] *O maior frete pago no período foi de <span style='font-size: 22px; font-weight:bold'> {(maior_frete["frete"].values[0]):,.2f} R$$
                </span>para uma venda no valor de <span style='font-size: 22px; font-weight:bold'> {maior_frete["valor"].values[0]:,.2f}R$</span>
            com a seguinte localização: latitude <span style='font-size: 22px; font-weight:bold'>{maior_compra["latitude"].values[0]}</span> e longitude*
             <span style='font-size: 22px; font-weight:bold'>{maior_compra["longitude"].values[0]}.</span>""", unsafe_allow_html=True)
            st.markdown(""":orange[Ação:] *Criar ofertas segmentadas e programas de fidelidade para aumentar as vendas na região, 
                        possibilitando parcerias logísticas estratégicas, e consequentemente, a redução de custos de frete com o aumento do volume de entregas.*""")
            
            


            

        

