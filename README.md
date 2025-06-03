# Banco de Dados para Análises (Olist)

![Estrutura do banco de dados](C:\db_keys.png)

**_Aplicação para análises da Empresa Olist_**

# Projeto de Banco de Dados Olist: Do Dado Bruto ao Dashboard Interativo

## Visão Geral do Projeto

Este projeto demonstra um pipeline completo de ciência de dados, desde a ingestão e tratamento de dados brutos até a construção de um banco de dados relacional e a integração com um dashboard interativo. O objetivo principal é extrair insights valiosos do dataset de e-commerce brasileiro da Olist, que contém informações sobre pedidos, clientes, vendedores, produtos, pagamentos e reviews.

## Estrutura do Projeto

O projeto está organizado da seguinte forma:

* **`data/`**: Contém os datasets brutos (`raw_dfs/`) e os datasets limpos e transformados (`cleaned_dfs/`) utilizados na carga do banco de dados.
* **`sql/`**: Armazena o script SQL para a criação do esquema do banco de dados e a carga dos dados.
* **`notebooks/` ou `scripts/`**: Contém os scripts Python (Jupyter Notebooks ou `.py` files) para o pré-processamento, limpeza e transformação dos dados com Pandas.
* **`dashboard/`**: Contém o script Python do dashboard interativo construído com Streamlit.
* **`db_keys.png`**: Imagem que representa o esquema relacional do banco de dados.
* **`CHALLENGES.md`**: Documentação detalhada sobre os desafios de qualidade e integridade de dados encontrados e as soluções aplicadas.
* **`README.md`**: Este arquivo.

## Esquema Relacional do Banco de Dados

O banco de dados foi modelado para refletir as relações entre as entidades do e-commerce da Olist. O esquema relacional, com suas chaves primárias (PKs) e chaves estrangeiras (FKs) bem definidas, pode ser visualizado abaixo:

![Esquema Relacional do Banco de Dados Olist](db_keys.png)

## Desafios e Soluções (Engenharia de Dados)

A etapa de engenharia e limpeza de dados foi um componente crítico e o maior desafio deste projeto. O dataset bruto apresentava diversas inconsistências que exigiram um tratamento rigoroso para garantir a integridade e a confiabilidade dos dados no banco de dados.

Os desafios encontrados e as soluções implementadas estão detalhadamente documentados no arquivo:

[**CHALLENGES.md**](CHALLENGES.md)

Neste documento, você encontrará informações sobre:
* Inconsistências de Chaves Primárias (PKs) e como foram resolvidas.
* Problemas de Chaves Estrangeiras (FKs) e "dados órfãos".
* O "efeito cascata" das inconsistências e a metodologia de filtragem em cascata.
* Ajustes na definição do esquema SQL e otimizações com índices.

## Tecnologias Utilizadas

* **Python:** Linguagem principal para pré-processamento, limpeza de dados (Pandas) e desenvolvimento do dashboard (Streamlit).
* **Pandas:** Biblioteca para manipulação e análise de dados.
* **PostgreSQL:** Sistema de gerenciamento de banco de dados relacional para armazenamento e consulta dos dados.
* **SQL:** Linguagem para definição do esquema, carga de dados e consultas analíticas.
* **Streamlit:** Framework para a criação de dashboards interativos e visualização de dados.


## Contribuições

Sinta-se à vontade para explorar o código, sugerir melhorias ou relatar problemas.

## Contato

* **Seu Nome:** [Seu Nome Completo]
* **LinkedIn:** [Link para o seu perfil do LinkedIn]
* **GitHub:** [Link para o seu perfil do GitHub]