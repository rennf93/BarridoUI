select 'Id'
,'Estado'
,'Estado_Mambu'
,'Cliente_en_Gest_Especial'
,'Sucursal_Prestamo'
,'Centro_Prestamo'
,'AyN'
,'DNI'
,'NombreLinea'
,'ValorCuota'
,'Ultimo_Vto'
,'FecUltCuotaImpaga'
,'Proximo_Vto'
,'fecha_1Vto'
,'DiasAtraso'
,'MoraCuotas'
,'PunitoriosAdeudados'
,'CantidadCuotasAdeudadas'
,'CBU'
,'SaldoDeCapitalAdeudado'
,'Total_Cta_Recaudadora'
,'Total_a_Barrer'
, 'Cargos_y_Penalidades'
, 'Bucket'
, 'K_mas_I'
, 'EstadoInicial'
, 'FecUltCuotaPagaMesAnt'
, 'ConCobro'
, 'Sueldo'
, 'Gestion Cobranza'
, 'ID_Op_CRM'
, 'Monto_cobranza_inicial'
, 'Dias_atraso_inicial'
, 'Estado_inicial'
, 'CantTotalCuotas'
, 'NroCuotaExigible'
, 'Deuda_crossselling'
UNION ALL
SELECT `Id`
,`Estado`
,`Estado_Mambu`
,`Cliente_en_Gest_Especial`
,`Sucursal_Prestamo`
,`Centro_Prestamo`
,`AyN`
,ca.`DNI`
,`NombreLinea`
,FLOOR(`ValorCuota`)
,`Ultimo_Vto`
,`FecUltCuotaImpaga`
,`Proximo_Vto`
,`fecha_1Vto`
,`DiasAtraso`
,FLOOR(`MoraCuotas`)
,FLOOR(`PunitoriosAdeudados`)
,`CantidadCuotasAdeudadas`
,`CBU`
,FLOOR(`SaldoDeCapitalAdeudado`)
,FLOOR(`Total_Cta_Recaudadora`)
,FLOOR(`Total_a_Barrer` + `Deuda_crossselling`)
,`Cargos_y_Penalidades`
,`Bucket`
, CASE WHEN K_mas_I > 0.00 THEN FLOOR(TRUNCATE(K_mas_I, 2)) ELSE 0.00 END
, '' as 'EstadoInicial'
, `FecUltCuotaPagaMesAnt`
, `Con_cobro_2da_quincena` as 'ConCobro'
,`sueldo`
,`Gestion Cobranza`
,`ID_Op_CRM`
,FLOOR(`Monto_cobranza_inicial`)
,`Dias_atraso_inicial` 
,`Estado_inicial`
,`CantTotalCuotas`
,`NroCuotaExigible`
,FLOOR(`Deuda_crossselling`)
FROM cartera_activa_inicial ca
WHERE ca.Estado_Mambu NOT IN ('ACTIVE - LOCKED', 'ACTIVE - PARTIALLY_DISBURSED');
