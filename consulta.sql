SELECT V.order_status,
	V.order_approved_at,
	V.order_purchase_timestamp,
	V.order_delivered_customer_date,
	P.payment_type,
	p.payment_value
	FROM VENDAS V
	JOIN pagamentos P ON V.order_id = P.order_id	
	WHERE order_status = 'delivered'
	ORDER BY order_approved_at asc LIMIT 20

SELECT	v.order_status,
	v.order_approved_at,	
	p.payment_type,
	SUM(ip.price) as "valor_total",
	SUM(ip.freight_value) as "frete_total",
	MAX(ip.order_item_id) as "total_produtos",
	p.payment_value as "pagamento_total"
	
from vendas v
join pagamentos p on v.order_id = p.order_id
join itenspedidos ip on v.order_id = ip.order_id
WHERE v.order_status not in ('delivered', 'canceled', 'invoiced', 'shipped', 'processing')
group by v.order_id, p.payment_value, p.payment_type


SELECT * from PRODUTOS 

SELECT v.customer_id AS "ID CLIENTE",
	v.order_purchase_timestamp AS "HORA DA COMPRA",
	p.product_category_name AS "CATEGORIA",
	SUM(ip.price) AS "TOTAL VENDAS"	
	FROM VENDAS V	
	INNER JOIN ITENSPEDIDOS IP ON V.ORDER_ID = IP.ORDER_ID
	INNER JOIN PRODUTOS P ON IP.PRODUCT_ID = P.PRODUCT_ID
	GROUP BY v.customer_id, p.product_category_name, v.order_purchase_timestamp
	ORDER BY "ID CLIENTE" ASC LIMIT 100;

SELECT product_category_name, FROM PRODUTOS
	GROUP BY (PRODUCT_ID)
	SUM(PRODUCT_CATEGORY_NAME)
	
