# Consulta principal
consulta_sql ="""SELECT V.ORDER_PURCHASE_TIMESTAMP,
	V.CUSTOMER_ID,		
	P.PRODUCT_CATEGORY_NAME,
	IP.PRICE
	FROM VENDAS V	
	INNER JOIN ITENSPEDIDOS IP ON V.ORDER_ID = IP.ORDER_ID
	INNER JOIN PRODUTOS P ON IP.PRODUCT_ID = P.PRODUCT_ID	
	WHERE V.ORDER_STATUS = 'delivered'"""

# Consulta Estados
consulta_sql2 = """SELECT VDS.ORDER_PURCHASE_TIMESTAMP,
	GL.GEOLOCATION_LAT AS latitude,
	GL.GEOLOCATION_LNG AS longitude,
	VDS.ORDER_STATUS AS status,    
	SUM(IP.PRICE) AS valor,
	SUM(IP.FREIGHT_VALUE) AS frete	
    FROM CLIENTES CL	
	LEFT JOIN GEOLOCALIZACAO GL ON CL.ZIP_CODE_PREFIX = GL.ZIP_CODE_PREFIX
	LEFT JOIN VENDAS VDS ON CL.CUSTOMER_ID = VDS.CUSTOMER_ID
	INNER JOIN ITENSPEDIDOS IP ON VDS.ORDER_ID = IP.ORDER_ID	
    WHERE VDS.ORDER_STATUS = 'delivered'
	GROUP BY VDS.ORDER_ID, GL.GEOLOCATION_LAT, GL.GEOLOCATION_LNG, VDS.ORDER_STATUS, IP.PRICE, IP.FREIGHT_VALUE;"""


consulta_sql3 = """SELECT
    c.customer_state AS Estado, -- Sigla do estado (UF)
    COUNT(DISTINCT c.customer_unique_id) AS total_clientes,
    COUNT(DISTINCT v.order_id) AS total_pedidos,
    SUM(oi.price) AS receita_total_vendas,
    AVG(oi.freight_value) AS frete_medio    
    
FROM Clientes c
LEFT JOIN Vendas v ON c.customer_id = v.customer_id
LEFT JOIN ItensPedidos oi ON v.order_id = oi.order_id
WHERE v.order_id IS NOT NULL -- Apenas estados com pedidos
AND v.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY c.customer_state;
"""

consulta_sql4="""SELECT
    TO_CHAR(v.order_purchase_timestamp, 'YYYY-MM') AS mes_ano_compra,
    p.product_category_name AS categoria,
    COUNT(oi.order_item_id) AS quantidade_itens_vendidos,
    SUM(oi.price) AS receita_total_mes
FROM Vendas v
JOIN ItensPedidos oi ON v.order_id = oi.order_id
JOIN Produtos p ON oi.product_id = p.product_id
WHERE v.order_status = 'delivered' -- Considerar apenas pedidos entregues como demanda real
GROUP BY 1, 2
ORDER BY 1, 2;"""