import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from io import StringIO
from pmdarima import auto_arima
from sklearn.metrics import mean_absolute_percentage_error



    
    #Segunda Função Aninhada(Geração dos Gráficos)
    def gerador_graficos(total_vendas, vendas_por_categoria, vendas_mensais, crescimento_perc,ticket_medio_categoria, ticket_medio_mes, melhores_clientes, 
                          clientes_frequentes, taxa_retencao, taxa_recompra, clv, fig_arima, fig_compar, maiores_valores, data_copy): #Cálculos necessários para o gerador de gráficos

        #Gráfico de Vendas por Categoria
        categoria_mais_vendida = vendas_por_categoria[vendas_por_categoria[coluna_valor]== vendas_por_categoria[coluna_valor].max()]
        fig = px.bar(vendas_por_categoria, vendas_por_categoria.index, vendas_por_categoria[coluna_valor],  color=vendas_por_categoria[coluna_valor], color_continuous_scale="Greens",
                     title=f"{categoria_mais_vendida.index[0]} é a categoria com maior soma de vendas com um total de {categoria_mais_vendida[coluna_valor].iloc[0]:,.2f} ")
        
        fig.update_layout(xaxis_title="Categoria", yaxis_title="Total Vendido em cada categoria", template="plotly_dark")

        fig.update_traces(text=vendas_por_categoria[coluna_valor].apply(lambda x: f"R$ {x:,.2f}"), textposition="none", hovertemplate="Vendas por Categoria: R$%{y}<br>Categoria: %{x} ")
                

        #Gráfico de Vendas Totais
        fig2 = go.Figure(go.Indicator(mode="gauge+number", 
                                      value=total_vendas,
                                      title="Vendas Totais",
                                      align="center",
                                      gauge={"axis": {"range": [0, 1.25 * total_vendas]}}))
        
        fig2.add_annotation(x=0.5, y=-0.2, text="Total Vendido:  R${:,.2f}".format(total_vendas), 
                                showarrow=False, font=dict(size=19, color="white"))
        
        
        mapeamento_meses = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: 
                            "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"} #Dicionário para mapeamento dos meses
        
        # Preparação dos dados
        crescimento_perc = crescimento_perc.sort_index(ascending=False).iloc[:12,:]
        x = np.arange(len(crescimento_perc))  # Criando índices numéricos para os meses
        y = crescimento_perc[coluna_valor].values  # Valores de crescimento percentual

        melhor_porc = crescimento_perc[crescimento_perc[coluna_valor]== crescimento_perc[coluna_valor].max()]
        pior_porc = crescimento_perc[crescimento_perc[coluna_valor]== crescimento_perc[coluna_valor].min()]
        
        # Criar gráfico principal
        fig3 = px.line(crescimento_perc, x=crescimento_perc.index, y=crescimento_perc[coluna_valor], markers=True, color_discrete_sequence=["#1c83e1"],
                    title=f"O mês de {mapeamento_meses[melhor_porc.index.month[0]]} de {melhor_porc.index.year[0]} apresentou um crescimento percentual nas vendas de {melhor_porc[coluna_valor].iloc[0]:,.2f}%")


        # Ajuste polinomial (grau 1 para tendência)
        coef = np.polyfit(x, y, 1)
        poly = np.poly1d(coef)

        # Geração de pontos para a linha de tendência
        x_fit = x  # Mantendo a escala original
        y_fit = poly(x_fit)  # Aplicando a função polinomial


        fig3.update_layout(yaxis_title="Variação Percentual(%)", 
                        xaxis_title=f"{mapeamento_meses[pior_porc.index.month[0]]} de {pior_porc.index.year[0]} foi o mês com pior variação percentual: {pior_porc[coluna_valor].iloc[0]:,.2f}%")

        fig3.update_traces(text=crescimento_perc[coluna_valor], hovertemplate="Variação Percentual nas Vendas: %{y}%<br>Mês: %{x}",
                           marker=dict(color="#f7fbff"))

        # Adicionar linha de tendência polinomial corrigida
        fig3.add_scatter(x=crescimento_perc.index, y=y_fit, mode='lines', name="Tendência", line=dict(dash="dash", color="#f7fbff")) # Adição da linha de tendência
       

        #Gráfico de Ticket Médio por Categoria        
        maior_ticket_cat = ticket_medio_categoria[ticket_medio_categoria[coluna_valor]== ticket_medio_categoria[coluna_valor].max()]
        ticket_medio_categoria = ticket_medio_categoria.sort_values(coluna_valor, ascending=True)
        fig5 = px.bar(ticket_medio_categoria, y=ticket_medio_categoria.index, x=ticket_medio_categoria[coluna_valor], color=ticket_medio_categoria[coluna_valor],
                        title=f"O maior ticket médio foi da categoria {maior_ticket_cat.index[0]} com um valor de R${maior_ticket_cat[coluna_valor].iloc[0]:,.2f}")
        fig5.update_layout(xaxis_title="Valor do Ticket", yaxis_title="Categoria")
        fig5.update_traces(text=ticket_medio_categoria[coluna_valor].apply(lambda x: f"R$ {x:,.2f}"), textposition="inside", hovertemplate="Ticket Médio por Categoria: %{text}<br>Categoria: %{y}")
        
        #Gráfico de Ticket Médio por Mês        
        ticket_medio_mes = ticket_medio_mes.sort_index(ascending=False).iloc[:12,:]
        maior_ticket_mes = ticket_medio_mes[ticket_medio_mes[coluna_valor]== ticket_medio_mes[coluna_valor].max()]
        menor_ticket_mes = ticket_medio_mes[ticket_medio_mes[coluna_valor]== ticket_medio_mes[coluna_valor].min()]
        fig6 = px.bar(ticket_medio_mes, ticket_medio_mes.index, ticket_medio_mes[coluna_valor], color=ticket_medio_mes[coluna_valor],
            title=f"{mapeamento_meses[maior_ticket_mes.index.month[0]]} de {maior_ticket_mes.index.year[0]} apresentou o maior ticket médio com um valor de {maior_ticket_mes[coluna_valor].iloc[0]:.2f}")
        fig6.update_layout(yaxis_title="Valor do Ticket", 
                    xaxis_title=f"{mapeamento_meses[menor_ticket_mes.index.month[0]]} de {menor_ticket_mes.index.year[0]} foi o mês com o menor ticket médio: {menor_ticket_mes[coluna_valor].iloc[0]:,.2f}")
        fig6.update_traces(text=ticket_medio_mes[coluna_valor].apply(lambda x: f"R$ {x:,.2f}"), textposition="none", hovertemplate="Valor do Ticket: %{text}<br>Mês: %{x} ")

        #Gráfico de Melhores Clientes
        melhores_clientes = melhores_clientes.sort_values(coluna_valor, ascending=False).iloc[:maiores_valores,:].reset_index()
        melhor_cliente = melhores_clientes[melhores_clientes[coluna_valor]== melhores_clientes[coluna_valor].max()]
        fig7 = px.bar(melhores_clientes, melhores_clientes[coluna_id].apply(lambda x: "(" + x + ")"), melhores_clientes[coluna_valor],
                       color=melhores_clientes[coluna_valor], color_continuous_scale="Greens",
                      title=f"ID do Melhor Cliente: {melhor_cliente[coluna_id].iloc[0]}<br>Valor Total Gasto {melhor_cliente[coluna_valor].iloc[0]} ")
        fig7.update_layout(xaxis_title="ID dos Melhores Clientes", yaxis_title="Valor Gasto")
        fig7.update_traces(text=melhores_clientes[coluna_valor].apply(lambda x: f"R$ {x:,.2f}"), textposition="none", hovertemplate="Gastos do Cliente: R$%{text}<br>ID do Cliente: %{x}")

        
        #Gráfico de Clientes Mais Frequentes
        clientes_frequentes = clientes_frequentes.sort_values(coluna_valor, ascending=False).iloc[:maiores_valores,:].reset_index()
        cliente_mais_frequente = clientes_frequentes[clientes_frequentes[coluna_valor]== clientes_frequentes[coluna_valor].max()]
        fig8 = px.bar(clientes_frequentes, clientes_frequentes[coluna_id].apply(lambda x: "(" + x + ")"), 
                      clientes_frequentes[coluna_valor], color=clientes_frequentes[coluna_valor],  color_continuous_scale="Greens",
                      title=f"ID do Cliente mais frequente: {cliente_mais_frequente[coluna_id].iloc[0]}<br>Compras Realizadas: {cliente_mais_frequente[coluna_valor].iloc[0]} ")
        fig8.update_layout(xaxis_title="Clientes Mais Frequentes", yaxis_title="Quantidade de Compras realizadas")
        fig8.update_traces(text=clientes_frequentes[coluna_valor], textposition="auto", hovertemplate="Número de Compras do Cliente: %{y}<br>ID do Cliente: %{x} ")


        #Gráfico de Retenção de Clientes
        cor = "red" if taxa_retencao <0.2 else "green"
        fig9 = go.Figure(go.Indicator(mode="gauge+number", 
                                    value= taxa_retencao*100,
                                    title={"text": f"Taxa de Recorrência de Clientes: {taxa_retencao*100:.2f}% "},
                                    gauge={"axis": {"range": [0, 100]},
                                           "bar": {"color": cor}}))
        fig9.add_annotation(x=0.5, y=-0.2, 
                            text=f"Aproximadamente {round(taxa_retencao*10)} de cada 10 clientes voltaram a comprar",
                            showarrow=False, font=dict(size=25, color=cor))
        
        taxa_recompra = taxa_recompra*100
        maior_recorrencia = taxa_recompra[taxa_recompra.values== taxa_recompra.values.max()]
        menor_recorrencia = taxa_recompra[taxa_recompra.values== taxa_recompra.values.min()]
        fig10 = px.line(taxa_recompra, x=taxa_recompra.index, y=taxa_recompra.values, color_discrete_sequence=[cor])
        fig10.update_layout(xaxis_title=f"{mapeamento_meses[menor_recorrencia.index.month[0]]} de {menor_recorrencia.index.year[0]} apresentou a menor taxa de recorrência: {menor_recorrencia.values[0]:.2f}%",
            yaxis_title="Taxa de Recorrência(%)", title=f"No mês de {mapeamento_meses[maior_recorrencia.index.month[0]]} de {maior_recorrencia.index.year[0]} houve uma taxa de recompra de {maior_recorrencia.values[0]:.2f}%")
        fig10.update_traces(text=taxa_recompra.apply(lambda x: f"{x:.2f}%"), textposition="bottom center", hovertemplate="Taxa de Recompra: %{text}<br>Mês: %{x}")
        
        return fig, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, fig10, clv, fig_arima, fig_compar, data_copy
    
    
    total_vendas, vendas_por_categoria, vendas_mensais, crescimento_perc, ticket_medio_categoria, ticket_medio_mes, \
            melhores_clientes, clientes_frequentes, taxa_retencao, taxa_recompra, clv, fig_arima, fig_compar, maiores_valores, data_copy = gerador_calculos(data)
        
    return gerador_graficos(total_vendas, vendas_por_categoria, vendas_mensais, crescimento_perc,
                          ticket_medio_categoria, ticket_medio_mes, melhores_clientes, clientes_frequentes, taxa_retencao, taxa_recompra, clv, fig_arima, fig_compar, maiores_valores, data_copy)
    

#COnfiguração da barra lateral
with st.sidebar:    
    st.markdown(":blue[**Configuração das Análises**]")
    try:
        uploaded_file = st.file_uploader(":blue[Selecionar arquivo]", type="csv", help="Se nenhum arquivo for selecionado, \
                                                    \n a aplicação usará dados de exemplo")
        dados = carregador_dados(uploaded_file)  #dados brutos
    except Exception as error:
        st.error("Erro ao carregar o arquivo. Por favor selecione um conjunto de dados compatível e atualize corretamente as colunas\
                    de data, id do cliente , categoria e valor no seu arquivo CSV.")
    with st.expander("Selecionar o tipo de visualização", expanded=True):
        visualizacao = st.radio("Selecione o tipo de análise", ["Vendas por Categoria", "Vendas por Mês", "TickedMédio", "Clientes Engajados",
                                                                "Taxa de Recorrência", "Projeção"], help="Selecione o tipo de análise que gostaria de visualizar")        
    if dados.shape[1]<4: 
        st.error("Por Favor selecione um conjunto de dados válidos. O conjunto de dados deve conter "
                    "colunas de \'data, id do cliente, categoria e valor\'")      #Mensagem de erro se conjunto de dados carregado for incompatível        
    st.markdown(":blue[**Gostaria de personalizar as visualizações?**]", help="Selecione as configurações abaixo para personalizar \
                                    \n a exibição de meses, clientes e previsões", unsafe_allow_html=False)
    with st.expander("Configurações adicionais"):        
        datas = st.date_input("Insira 1 ou 2 datas para filtrar nos gráficos", [], help="Escolha uma única data se quiser inserir apenas a data inicial,\
                              \n ou duas se quiser filtrar data inicial e final, respectivamente.")
        maiores_valores = st.slider("Selecione o número de clientes que deseja exibir nos gráficos(Clientes Engajados)", 2, 20, 10, 1)                
        meses_prever = st.slider("Selecione o número de Meses que deseja prever(Projeção)", min_value=2, max_value=12, value=12, step=1)            
    st.markdown(":blue[**Fez o upload de um arquivo?**]", help="Se você fez o upload de um arquivo. Clique abaixo \
                \n para selecionar as  colunas necessárias para as análises, \
                    \n caso contrário a aplicação pode apresentar um ERRO", unsafe_allow_html=False)
    with st.expander("Clique aqui!", expanded=False):
        coluna_data = st.selectbox("Selecione a coluna de data", dados.columns, index=0)    
        coluna_id = st.selectbox("Selecione a coluna de identificação do cliente", dados.columns, index=1)
        coluna_categoria = st.selectbox("Selecione a coluna de categoria", dados.columns, index=2)
        coluna_valor = st.selectbox("Selecione a coluna de Valor", dados.columns, index=3)

     
    processar = st.button(":blue[Processar os dados]" )

if processar:
                    
                

        #Visualização da segunda Página
        elif visualizacao=="Vendas por Mês":
            col1, col2 = st.columns(2, gap="large")
            with col1:            
                st.subheader("Variação Percentual das Vendas")          
                st.plotly_chart(fig3, use_container_width=True)            
                st.markdown("*O gráfico acima exibe o crescimento percentual das Vendas*")
                st.markdown("<hr style='border:1px solid #1c83e1'>", unsafe_allow_html=True)
                st.markdown(":blue[**Dica:**]  *Analise a variação percentual nas vendas de acordo com o mês anterior \
                e veja como elas mudam ao longo do tempo comparando com o gráfico de vendas ao lado \
                Insira o número de meses ao lado para um visão mais detalhada se necessário*")

            with col2:
                st.subheader("Vendas Mensais")  
                st.plotly_chart(fig4, use_container_width=True)            
                st.markdown("*O gráfico acima exibe o total de Vendas Mensais*")
                st.markdown("<hr style='border:1px solid #1c83e1'>", unsafe_allow_html=True)
                st.markdown(":blue[**Informação:**] *Analise o gráfico acima para obter uma visão totalizada das vendas de cada mês \
                            e veja a relação com a variação percentual das vendas ao lado \
                            Todos os gráficos possuem ícones acima que permitem interação com os gráficos."
                            "Arrastar, aplicar zoom, exibir em tela cheia, fazer o download da imagem \
                                são apenas alguns dos recursos disponíveis nos gráficos*")

        #Visualização da terceira Página
        elif visualizacao=="TickedMédio":
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.subheader("Ticket Médio por Categoria")
                st.plotly_chart(fig5, use_container_width=True)
                st.markdown("*O gráfico acima mostra o ticket médio por categoria*")
                st.markdown("<hr style='border:1px solid #1c83e1'>", unsafe_allow_html=True)            
                st.markdown(":blue[**Descrição:**] *Veja quanto cada venda em determinada categoria \
                            representa em média.*")

            with col2:
                st.subheader("Ticket Médio por Mês")
                st.plotly_chart(fig6, use_container_width=True)
                st.markdown("*O gráfico acima mostra o ticket Médio por Mês*")
                st.markdown("<hr style='border:1px solid #1c83e1'>", unsafe_allow_html=True)            
                st.markdown(":blue[**Descrição:**] *Veja o quanto o valor médio de cada venda \
                            pode variar de um mês para o outro*")

        #Visualização da quarta Página
        elif visualizacao=="Clientes Engajados":
            col1, col2 = st.columns(2, gap="medium")
            with col1:
                st.subheader("*Clientes com Maiores Gastos*")
                st.plotly_chart(fig7, use_container_width=True)
                st.markdown("*O gráfico acima exibe os clientes com os maiores gastos*")
                st.markdown("<hr style='border:1px solid green'>", unsafe_allow_html=True)            
                st.markdown(":green[**Descrição:**] *Veja os clientes com maiores gastos \
                            no período selecionado. Opcionalmente, use o slider \
                            ao lado para filtrar o número de clientes desejado*")

            with col2:
                st.subheader("**Clientes Mais Frequentes**")
                st.plotly_chart(fig8, use_container_width=True)        
                st.markdown("*O gráfico acima exibe os clientes com maior número de compras*")
                st.markdown("<hr style='border:1px solid green'>", unsafe_allow_html=True)            
                st.markdown(":green[**Descrição:**] *Veja com que frequência os melhores clientes compraram na empresa \
                            no período selecionado.*")
            
        #Visualização da quinta Página
        elif visualizacao== "Taxa de Recorrência":        
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("*Clientes Recorrentes*")
                st.plotly_chart(fig9, use_container_width=True)
                st.markdown("<hr style='border:1px solid white'>", unsafe_allow_html=True)
                st.markdown(":green[**Descrição:**] *O gráfico acima mostra a proporção de clientes que voltaram a comprar durante o período selecionado*")            
                st.markdown(f"*Valor Médio Vitalício do Cliente(CLV):* <span style='font-size: 25px; font-weight:bold; color: green'>R${clv.iloc[0]:,.2f}</span>", unsafe_allow_html=True)
                st.markdown(":green[**Informação:**] *CLV é o valor médio que um cliente gasta durante todo o seu tempo \
                            como cliente da empresa. Observe que esse valor é calculado considerando todas as compras dos clientes \
                            dentro do período selecionado e pode apresentar uma variação significativa \
                            de acordo com o período selecionado*")

            with col2:
                st.subheader("*Taxa de Recorrência Mensal*")
                st.plotly_chart(fig10, use_container_width=True)
                st.markdown("<hr style='border:1px solid white'>", unsafe_allow_html=True)
                st.markdown(":green[**Descrição:**] *O gráfico acima mostra a proporção de clientes com compras recorrentes em um mesmo mês \
                            Altas taxas de recompra indicam que os clientes tendem a ser mais fiéis à empresa realizando mais de uma compra \
                            no mesmo mês enquanto taxas menores indicam baixo engajamento mensal dos clientes. \
                            Observe também que o engajamento tende a diminuir de forma exponencial à medida que \
                            o número de clientes da empresa aumenta*")
                

        #Visualização da sexta Página
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("*Vendas do período anterior*")
                st.plotly_chart(fig_compar, use_container_width=True)
                st.markdown(f"*O gráfico acima mostra as vendas do período anterior ao período previsto de **{meses_prever}** meses*")
                st.markdown("<hr style='border:1px solid #1E60FF'>", unsafe_allow_html=True)                
                st.markdown(":blue[**Informação:**] *É importante que você analize as previsões do modelo e as compare com os dados disponíveis, \
                    pois é possível que o modelo capte padrões nas vendas como altas, quedas, variações, sazonalidades etc. \
                    Porém dependendo do caso pode ser necessário utilizar outras abordagens como machine learning ou redes neurais, por exemplo. \
                    Também é interessante utilizar conjuntos de dados de tamanhos ao menos razoável para que esses padrões possam ser captados* ")
            
            with col2:
                st.subheader("*Previsões para o período selecionado*")
                st.plotly_chart(grafico_arima, use_container_width=True)                
                st.markdown(f"*O gráfico acima mostra as previsões do modelo para o período selecionado de **{meses_prever}** meses*")
                st.markdown("<hr style='border:1px solid #1E60FF'>", unsafe_allow_html=True)
                st.markdown(":blue[**Informação:**] *Note que este modelo foi construído para ser um modelo generalista que se adapta aos dados \
                            da melhor maneira possível, porém à depender da qualidade e quantidade dos dados disponíveis as previsões \
                            podem ter uma certa variação. Por isso é importante se atentar para o erro percentual do modelo \
                            que está disponibilizado abaixo do gráfico com as previsões*")
    except Exception as error:
        st.warning("Atenção. É extremamente importante que você selecione corretamente as colunas do dataframe na barra lateral caso você\
                   tenha feito o upload de um arquivo. Também é importante limpar os filtros de data pois a inserção de datas inexistentes\
                   no conjunto de dados pode gerar dataframes vazios e, consequentemente, erros na aplicação .")
        st.error(f"Erro ao processar os dados inseridos. Por favor, verifique a compatibilidade do dataframe\
                 com a aplicação e tente novamente. Erro técnico encontrado: {error}")
                



    
    


















