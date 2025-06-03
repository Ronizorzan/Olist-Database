# Desafios Encontrados e Superados na Construção do Banco de Dados Olist

Este documento detalha os principais desafios de qualidade e integridade de dados enfrentados durante a construção do banco de dados relacional (PostgreSQL) para o dataset de e-commerce da Olist. Ele serve como um registro das decisões tomadas e das metodologias aplicadas para garantir um ambiente de dados robusto e confiável para análises futuras e projetos de Machine Learning.

## Contexto do Projeto

O objetivo principal era migrar o dataset fornecido pela Olist (composto por múltiplos arquivos CSV) para um banco de dados relacional PostgreSQL, definindo um esquema que refletisse as relações entre as entidades (pedidos, clientes, produtos, vendedores, etc.) e garantisse a integridade referencial.

## Desafios Principais e Soluções

### 1. Inconsistências de Chave Primária (PK)

**Desafio:** Vários arquivos CSV continham registros duplicados em colunas que deveriam servir como Chaves Primárias (PKs) nas tabelas do banco de dados. Exemplos notáveis incluíram:
    * `order_id` no `olist_orders_dataset.csv`
    * `review_id` no `olist_order_reviews_dataset.csv`
    * Combinações `(order_id, payment_sequential)` no `olist_order_payments_dataset.csv`
    * Combinações `(order_id, order_item_id)` no `olist_order_items_dataset.csv`
    * `zip_code_prefix` no `olist_geolocation_dataset.csv` (onde um mesmo prefixo poderia ter múltiplas entradas para lat/lng/cidade/estado).

**Solução:**
    * **Pré-processamento com Pandas:** Para cada CSV, foi implementado um script em Python (Pandas) para identificar e remover as linhas duplicadas com base na(s) coluna(s) designada(s) como PK. A estratégia adotada foi `df.drop_duplicates(subset=[colunas_pk], keep='first')`, mantendo a primeira ocorrência.
    * **Impacto:** Garantiu a unicidade fundamental para a definição de `PRIMARY KEY` no esquema SQL, essencial para a integridade do banco. Uma pequena porcentagem de linhas foi removida nesses processos, considerada aceitável dada a escala do dataset.

### 2. Violação de Chaves Estrangeiras (FK) e "Dados Órfãos"

**Desafio:** Após a limpeza das Chaves Primárias, surgiram problemas de violação de Chaves Estrangeiras. Isso ocorreu quando IDs em tabelas "filhas" referenciavam IDs que não existiam mais nas tabelas "pai" (devido à remoção de duplicatas ou inconsistências). Exemplos:
    * `customer_id` em `Vendas` que não existia mais em `Clientes`.
    * `zip_code_prefix` em `Vendedores` e `Clientes` que não existia em `Geolocalizacao`.
    * `order_id`, `product_id`, `seller_id` em `ItensPedidos` que não existiam em `Vendas`, `Produtos` e `Vendedores`, respectivamente.
    * `order_id` em `Pagamentos` e `Reviews` que não existiam em `Vendas`.

**Solução:**
    * **Filtragem Cascata com Pandas (`merge`):** Foi adotada uma abordagem de filtragem sequencial. Para cada tabela "filha", um `inner merge` foi realizado com as colunas-chave das tabelas "pai" já limpas. Isso efetivamente removeu todas as linhas na tabela "filha" que não tinham uma correspondência válida na tabela "pai".
    * **Ordem de Limpeza Crucial:** O processo de limpeza dos CSVs foi estritamente seguido na ordem das dependências das tabelas (tabelas pai primeiro, depois tabelas filhas), espelhando a ordem de criação do banco de dados.
    * **Impacto:** Embora resultasse na remoção de algumas linhas (ex: 7 vendedores e 280 clientes foram removidos devido a `zip_code_prefix` inconsistentes em `Geolocalizacao`, que por sua vez levou à remoção de pedidos e itens relacionados), essa perda foi considerada aceitável (<1% do dataset total) em troca de um banco de dados com integridade referencial garantida.

### 3. Definição Incorreta de Chaves Estrangeiras no SQL

**Desafio:** Erros na sintaxe e no número de colunas referenciadas ao definir `FOREIGN KEY`s no script SQL. Por exemplo, tentar referenciar uma PK de coluna única com uma FK composta por múltiplas colunas (como `FOREIGN KEY (order_id, payment_sequential) REFERENCES Vendas(order_id)`).

**Solução:**
    * **Revisão Conceitual:** Reforço no entendimento da relação entre `PRIMARY KEY` (PK) e `FOREIGN KEY` (FK), garantindo que o número de colunas da FK corresponda exatamente ao número de colunas da PK/UNIQUE constraint referenciada.
    * **Correção no Script SQL:** Ajuste das definições de `FOREIGN KEY` em `Pagamentos` e `ItensPedidos` para referenciar corretamente a `order_id` da tabela `Vendas` como uma única coluna.

### 4. Otimização de Performance com Índices

**Desafio:** A garantia de um desempenho eficiente para consultas e `JOIN`s complexos, especialmente em um dataset de porte médio como o da Olist.

**Solução:**
    * **Criação de Índices Explícitos:** Além dos índices automáticos criados por `PRIMARY KEY`s, foram adicionados índices explícitos (`CREATE INDEX`) em colunas que atuam como `FOREIGN KEY`s, mas que não são parte de uma PK ou índice único já existente.
    * **Impacto:** Acelera as operações de busca e `JOIN` em colunas frequentemente utilizadas para relacionamento entre tabelas, melhorando a performance geral do banco de dados.

## Conclusão

A construção de um banco de dados a partir de dados brutos e inconsistentes é um processo iterativo que exige atenção aos detalhes e uma compreensão sólida dos princípios de modelagem de dados e integridade referencial. Os desafios encontrados neste projeto, embora demandem tempo e esforço significativos em limpeza e transformação, são representativos do cenário do mundo real e, uma vez superados, resultam em uma base de dados confiável e valiosa para análises e aplicações de Machine Learning.

Este trabalho de engenharia de dados é a base para qualquer análise ou modelo futuro, garantindo que as informações extraídas sejam precisas e as decisões tomadas sejam bem fundamentadas.

---