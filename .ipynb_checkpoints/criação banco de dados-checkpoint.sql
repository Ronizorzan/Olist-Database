CREATE TABLE vendas(order_id TEXT PRIMARY KEY,
	customer_id TEXT ,
	order_status TEXT ,
	order_purchase_timestamp TIMESTAMP ,
	order_approved_at TIMESTAMP,
	order_delivered_carrier_date TIMESTAMP,
	order_estimated_delivery_date TIMESTAMP
	);
COPY vendas FROM 'C:\\Users\\roni_\\projetos_streamlit\\projeto olist\\olist_orders_dataset.csv'
delimiter ','
CSV HEADER;


