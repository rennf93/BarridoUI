SELECT

'AyN'
,'Id'
,'Subestado_Cta'
,'Nro_Ctas'
,'DNI'
,'Fecha_Valor'
,'Monto_del_Capital'
,'Monto_de_Interes'
,'Monto_de_la_Penalizacion'
,'Monto_del_Cargo'
,'Montos_IVA_Interes_Penalizacion_Cargo'
,'Monto'
,'Tipo'
,'Canal'
,'Sucursal_Prestamo'
,'Centro_Prestamo'
,'Adicional_por_cuota_Cargo_Plus'
,'Fecha_Alta_Cargo_Plus'
,'Fecha_Baja_Cargo_Plus'
,'¿Tiene_Cross_Selling_cargado_manualmente?'
,'Monto_de_Interes_sin_IVA'
,'Monto_de_la_Penalizacion_sin_IVA'
,'Monto_del_Cargo_sin_IVA'

UNION ALL

select
`AyN`
,`Id`
,`Subestado_Cta`
,`Nro_Ctas`
,`DNI`
,`Fecha_Valor`
,`Monto_del_Capital`
,`Monto_de_Interes`
,`Monto_de_la_Penalizacion`
,`Monto_del_Cargo`
,`Montos_IVA_Interes_Penalizacion_Cargo`
,`Monto`
,`Tipo`
,`Canal`
,`Sucursal_Prestamo`
,`Centro_Prestamo`
,`Adicional_por_cuota_Cargo_Plus`
,`Fecha_Alta_Cargo_Plus`
,`Fecha_Baja_Cargo_Plus`
,`¿Tiene_Cross_Selling_cargado_manualmente?`
,`Monto_de_Interes_sin_IVA`
,`Monto_de_la_Penalizacion_sin_IVA`
,`Monto_del_Cargo_sin_IVA`

from (

select

replace(CONCAT(client.firstname, ' ',client.lastname),',',' ') AS 'AyN',

l.id AS 'Id',

ifnull(l.accountsubstate,'') as 'Subestado_Cta',

l.repaymentinstallments as 'Nro_Ctas',

(SELECT customfieldvalue.value
FROM customfieldvalue
JOIN customfield ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
WHERE customfield.id = 'client_dni'
AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'DNI',

date_format(lt.entrydate, '%Y-%m-%d') as 'Fecha_Valor',

round(lt.principalamount,2) as 'Monto_del_Capital',

round((lt.interestamount),2) as 'Monto_de_Interes',

round((lt.penaltyamount),2) as 'Monto_de_la_Penalizacion',

round((lt.feesamount),2) as 'Monto_del_Cargo',

round((lt.taxoninterestamount + lt.taxonpenaltyamount + lt.taxonfeesamount),2) as 'Montos_IVA_Interes_Penalizacion_Cargo',

round(lt.amount,2) as 'Monto',

lt.type as 'Tipo',

IFNULL((SELECT IFNULL(transactionchannel.id, ' ') #CANAL
FROM  transactionchannel
JOIN  transactiondetails
ON transactiondetails.TRANSACTIONCHANNELKEY = transactionchannel.ENCODEDKEY
WHERE transactiondetails.ENCODEDKEY  = lt.DETAILS_ENCODEDKEY_OID), IFNULL((SELECT IFNULL(transactionchannel.id, ' ') #CANAL
																			FROM  transactionchannel
																			LEFT JOIN  transactiondetails
																			ON transactiondetails.TRANSACTIONCHANNELKEY = transactionchannel.ENCODEDKEY
																			WHERE transactiondetails.ENCODEDKEY  = (SELECT LT3.DETAILS_ENCODEDKEY_OID
																													FROM loantransaction LT3
																													WHERE lt.ENCODEDKEY = LT3.REVERSALTRANSACTIONKEY)),"VACIO")) AS 'Canal',


IFNULL((SELECT customfieldvalue.value
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_suc_del_prestamo'
AND customfieldvalue.PARENTKEY = l.ENCODEDKEY), ' ') AS 'Sucursal_Prestamo',

IFNULL((SELECT customfieldvalue.value
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_centro_prestamo'
AND customfieldvalue.PARENTKEY = l.ENCODEDKEY), ' ') AS 'Centro_Prestamo',

IFNULL((SELECT customfieldvalue.value
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_adicional_presto_plus'
AND customfieldvalue.PARENTKEY = l.ENCODEDKEY), ' ') AS 'Adicional_por_cuota_Cargo_Plus',


IFNULL((SELECT customfieldvalue.value
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_fecha_alta_presto_plus'
AND customfieldvalue.PARENTKEY = l.ENCODEDKEY), ' ') AS 'Fecha_Alta_Cargo_Plus',

IFNULL((SELECT customfieldvalue.value
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_fecha_baja_presto_plus'
AND customfieldvalue.PARENTKEY = l.ENCODEDKEY), ' ') AS 'Fecha_Baja_Cargo_Plus',

IFNULL((SELECT customfieldvalue.value
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_cs_manual'
AND customfieldvalue.PARENTKEY = l.ENCODEDKEY), ' ') AS '¿Tiene_Cross_Selling_cargado_manualmente?',

round((lt.interestamount - lt.taxoninterestamount),2) as 'Monto_de_Interes_sin_IVA',

round((lt.penaltyamount - lt.taxonpenaltyamount),2) as 'Monto_de_la_Penalizacion_sin_IVA',

round((lt.feesamount - lt.taxonfeesamount),2) as 'Monto_del_Cargo_sin_IVA'

FROM 	loanaccount l
JOIN 	loantransaction lt 	ON l.encodedkey 			= lt.parentaccountkey AND (lt.type = 'REPAYMENT' AND lt.reversaltransactionkey is null AND date_format(lt.entrydate, '%Y-%m-%d') BETWEEN '$1' AND '$2')
JOIN  	client 				ON client.encodedkey 		= l.accountHolderKey 
JOIN	branch  			ON client.assignedBranchKey = branch.encodedkey
)  cta_cobrada