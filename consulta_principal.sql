-- Primeira Consulta
SELECT V.CUSTOMER_ID,	
	V.ORDER_PURCHASE_TIMESTAMP,
	P.PRODUCT_CATEGORY_NAME,
	IP.PRICE
	FROM VENDAS V	
	INNER JOIN ITENSPEDIDOS IP ON V.ORDER_ID = IP.ORDER_ID
	INNER JOIN PRODUTOS P ON IP.PRODUCT_ID = P.PRODUCT_ID	
	WHERE V.ORDER_STATUS = 'delivered'
	ORDER BY IP.PRICE DESC;


-- Segunda Consulta
SELECT GL.ZIP_CODE_PREFIX,
	GL.GEOLOCATION_LAT AS latitude,
	GL.GEOLOCATION_LNG AS longitude,
	VDS.ORDER_STATUS AS status,
	IP.PRICE AS valor,
	IP.FREIGHT_VALUE AS frete
	FROM CLIENTES CL	
	LEFT JOIN GEOLOCALIZACAO GL ON CL.ZIP_CODE_PREFIX = GL.ZIP_CODE_PREFIX
	LEFT JOIN VENDAS VDS ON CL.CUSTOMER_ID = VDS.CUSTOMER_ID
	INNER JOIN ITENSPEDIDOS IP ON VDS.ORDER_ID = IP.ORDER_ID	
	ORDER BY IP.PRICE DESC;
	
SELECT
    c.customer_state AS estado_sigla, -- Sigla do estado (UF)
    COUNT(DISTINCT c.customer_unique_id) AS total_clientes,    
    SUM(oi.price) AS receita_total_vendas,
    AVG(oi.freight_value) AS frete_medio,
    AVG(r.review_score) AS score_medio_reviews
    
FROM Clientes c
LEFT JOIN Vendas v ON c.customer_id = v.customer_id
LEFT JOIN ItensPedidos oi ON v.order_id = oi.order_id
LEFT JOIN Reviews r ON v.order_id = r.order_id
WHERE v.order_id IS NOT NULL -- Apenas estados com pedidos
GROUP BY c.customer_state
ORDER BY c.customer_state;

SELECT
    TO_CHAR(v.order_purchase_timestamp, 'YYYY-MM') AS mes_ano_compra,
    p.product_category_name AS categoria,
    COUNT(oi.order_item_id) AS quantidade_itens_vendidos,
    SUM(oi.price) AS receita_total_mes
FROM Vendas v
JOIN ItensPedidos oi ON v.order_id = oi.order_id
JOIN Produtos p ON oi.product_id = p.product_id
WHERE v.order_status = 'delivered' -- Considerar apenas pedidos entregues como demanda real
GROUP BY 1, 2
ORDER BY 1, 2;


