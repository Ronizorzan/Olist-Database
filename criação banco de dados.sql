DROP TABLE IF EXISTS ItensPedidos CASCADE;
DROP TABLE IF EXISTS Reviews CASCADE;
DROP TABLE IF EXISTS Pagamentos CASCADE;
DROP TABLE IF EXISTS Produtos CASCADE ;
DROP TABLE IF EXISTS Vendas CASCADE;
DROP TABLE IF EXISTS Clientes CASCADE;
DROP TABLE IF EXISTS Vendedores CASCADE;
DROP TABLE IF EXISTS Geolocalizacao CASCADE;


--Tabela Nº 1
--Criação da Tabela de Geolocalizacao 
CREATE TABLE Geolocalizacao (zip_code_prefix INT PRIMARY KEY,
	geolocation_lat REAL,
	geolocation_lng REAL,
	geolocation_city TEXT,
	geolocation_state TEXT	
); 							
COPY Geolocalizacao FROM 'C:/temp/projeto olist/cleaned_dfs/df_geolocation_cleaned.csv'
DELIMITER ','              --Tabela 'Geolocalizacao' foi tratada e adicionada à pasta 'cleaned_dfs'    
CSV HEADER;

--Tabela Nº 2
--Criação da Tabela de Vendedores 
CREATE TABLE Vendedores (seller_id TEXT PRIMARY KEY,
	zip_code_prefix INT NOT NULL,
	seller_city TEXT,
	seller_state TEXT, 
	FOREIGN KEY (zip_code_prefix) REFERENCES Geolocalizacao (zip_code_prefix)
	);
COPY Vendedores FROM 'C:/temp/projeto olist/cleaned_dfs/df_sellers_cleaned.csv'
DELIMITER ','            --Tabela 'Vendedores' foi tratada e adicionada à pasta 'cleaned_dfs'
CSV HEADER;


--Tabela Nº 3
--Criação da Tabela de Clientes
CREATE TABLE Clientes (customer_id TEXT PRIMARY KEY,
	customer_unique_id TEXT NOT NULL,
	zip_code_prefix INT NOT NULL,
	customer_city TEXT,
	customer_state TEXT,
	FOREIGN KEY (zip_code_prefix) REFERENCES Geolocalizacao (zip_code_prefix)
	);
COPY Clientes FROM 'C:/temp/projeto olist/cleaned_dfs/df_customers_cleaned.csv'
DELIMITER ','         --Tabela 'Clientes' foi tratada e adicionada à pasta 'cleaned_dfs'
CSV HEADER;


--Tabela Nº 4
--Criação da Tabela principal (Tabela de Vendas)
CREATE TABLE Vendas(order_id TEXT PRIMARY KEY,
	customer_id TEXT NOT NULL,
	order_status TEXT,
	order_purchase_timestamp TIMESTAMP,
	order_approved_at TIMESTAMP,
	order_delivered_carrier_date TIMESTAMP,
	order_delivered_customer_date TIMESTAMP,
	order_estimated_delivery_date TIMESTAMP,
	FOREIGN KEY (customer_id) REFERENCES Clientes (customer_id)
	);
COPY Vendas FROM 'C:/temp/projeto olist/cleaned_dfs/df_orders_cleaned.csv'
delimiter ','     --Tabela 'Vendas' foi tratada e adicionada à pasta 'cleaned_dfs'
CSV HEADER;


--Tabela Nº 5
-- Criação da Tabela de Produtos Chave Estrangeira -> 
CREATE TABLE Produtos (product_id TEXT PRIMARY KEY,
	product_category_name TEXT,
	product_name_lenght INT,
	product_description_lenght INT,
	product_photos_qty INT,
	product_weight_g INT,
	product_length_cm INT,
	product_height_cm INT,
	product_width_cm INT	
	);
COPY Produtos FROM 'C:/temp/projeto olist/raw_dfs/olist_products_dataset.csv'
delimiter ','
CSV HEADER;

	
--Tabela Nº 6
--Criação da Tabela de Pagamentos Chave Estrangeira -> Vendas(order_id)
CREATE TABLE Pagamentos (order_id TEXT NOT NULL,
	payment_sequential INT NOT NULL,
	payment_installments INT,
	payment_value REAL,	
	payment_type TEXT,	
	PRIMARY KEY (order_id, payment_sequential), -- Chave Primária Composta
	FOREIGN KEY (order_id) REFERENCES Vendas(order_id)
	);
COPY Pagamentos FROM 'C:/temp/projeto olist/cleaned_dfs/df_payments_cleaned.csv'	
delimiter ','          --Tabela 'Pagamentos' foi tratada e adicionada à pasta 'cleaned_dfs'
CSV HEADER;


--Tabela Nº 7
--Criação da Tabela de Reviews Chave Estrangeira(vendas[order_id])
CREATE TABLE Reviews (review_id TEXT NOT NULL,
	order_id TEXT PRIMARY KEY,
	review_score INT,	  
	review_comment_title TEXT,
	review_comment_message TEXT,
	review_creation_date TIMESTAMP,
	review_answer_timestamp TIMESTAMP,
	FOREIGN KEY (order_id) REFERENCES Vendas(order_id)	 
	);
COPY Reviews FROM 'C:/temp/projeto olist/cleaned_dfs/df_reviews_cleaned.csv'
delimiter ','          --Tabela 'Reviews' foi tratada e adicionada à pasta 'cleaned_dfs'
CSV HEADER;

	
--Tabela Nº 8
--Criação da Tabela de Itens dos Pedidos Chave Estrangeira(vendas[order_id])
CREATE TABLE ItensPedidos (order_id TEXT NOT NULL,
	order_item_id INT NOT NULL,
	product_id TEXT NOT NULL,
	seller_id TEXT NOT NULL,
	shipping_limit_date TIMESTAMP,
	price REAL,
	freight_value REAL,
	PRIMARY KEY (order_id, order_item_id),
	FOREIGN KEY (order_id) REFERENCES Vendas (order_id),
	FOREIGN KEY (product_id) REFERENCES Produtos (product_id),
	FOREIGN KEY (seller_id) REFERENCES Vendedores (seller_id)
	);
COPY ItensPedidos FROM 'C:/temp/projeto olist/cleaned_dfs/df_order_items.csv'
DELIMITER ','           --Tabela 'Reviews' foi tratada e adicionada à pasta 'cleaned_dfs'
CSV HEADER;	

	
	
--- ** OTIMIZAÇÃO: CRIAÇÃO DE ÍNDICES PARA CHAVES ESTRANGEIRAS ** ---
CREATE INDEX idx_vendas_customer_id ON Vendas (customer_id);
CREATE INDEX idx_reviews_order_id ON Reviews (order_id);
CREATE INDEX idx_itenspedidos_product_id ON ItensPedidos (product_id);
CREATE INDEX idx_itenspedidos_seller_id ON ItensPedidos (seller_id);
CREATE INDEX idx_vendedores_zip_code_prefix ON Vendedores (zip_code_prefix);
CREATE INDEX idx_clientes_zip_code_prefix ON Clientes (zip_code_prefix);