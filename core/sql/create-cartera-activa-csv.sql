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
,'Dia_Fijado'
,'fecha_1Vto'
,'DiasAtraso'
,'MoraCuotas'
,'PunitoriosAdeudados'
,'CargosAdeudados'
,'CantidadCuotasAdeudadas'
,'CBU'
,'SaldoDeCapitalAdeudado'
,'Total_Cta_Recaudadora'
,'Total_a_Barrer'
,'Total_a_Barrer_Nuevo'
,'Total_a_Barrer_anterior'
, 'Cargos_y_Penalidades'
, 'Bucket'
, 'K_mas_I'
, 'EstadoInicial'
, 'FecUltCuotaPagaMesAnt'
, 'ConCobro'
, 'Sueldo'
, 'Gestion Cobranza'
, 'Fecha_Cargo_Presto_Plus'
, 'Monto_Cargo_Presto_Plus'
, 'ID_Op_CRM'
, 'Monto_cobranza_inicial'
, 'Dias_atraso_inicial'
, 'Estado_inicial'
, 'Grupo'
, 'Banco'
, 'Categoria'
, 'FechaUltimoBarrido'
, 'Tipo_ultimo_barrido' 
, 'Banco_utlimo_barrido'
, 'Fecha_ult_pago_parcial'
, 'Fecha_ult_deposito'
, 'Dias_ult_debito_banco'
, 'PayingAgentBlockedRules'
, 'CantTotalCuotas'
, 'NroCuotaExigible'
, 'Deuda_crossselling'
, 'FechaEstimadaDeCobro'
, 'ImporteCobradoMesActualDebitoDirecto'
, 'ProbabilidadDeCobro'
, 'MaxFechaRendicion'
, 'MaxFechaCobro'
, 'ScorePrestamo'
, 'email'
, 'celular'
UNION ALL
SELECT `Id`
,`Estado`
,`Estado_Mambu`
,CONVERT(@gestion_esp USING latin1)
,`Sucursal_Prestamo`
,`Centro_Prestamo`
,`AyN`
,ca.`DNI`
,`NombreLinea`
,FLOOR(`ValorCuota`)
,`Ultimo_Vto`
,`FecUltCuotaImpaga`
,`Proximo_Vto`
,`Dia_Fijado`
,`fecha_1Vto`
,`DiasAtraso`
,FLOOR(`MoraCuotas`)
,FLOOR(`PunitoriosAdeudados`)
,FLOOR(`CargosAdeudados`)
,`CantidadCuotasAdeudadas`
,`CBU`
,FLOOR(`SaldoDeCapitalAdeudado`)
,FLOOR(`Total_Cta_Recaudadora`)
,FLOOR(`Total_a_Barrer` + COALESCE (`Deuda_crossselling`, 0))
,FLOOR(`Total_a_Barrer_Nuevo` + COALESCE (`Deuda_crossselling`, 0))
,FLOOR(`Total_a_Barrer_anterior`)
,`Cargos_y_Penalidades`
,`Bucket`
, CASE WHEN `K_mas_I` > 0 THEN FLOOR(TRUNCATE(`K_mas_I`, 2)) ELSE 0 END
, '' as 'EstadoInicial'
, `FecUltCuotaPagaMesAnt`
, `Con_cobro_2da_quincena` as 'ConCobro'
,`sueldo`
,`Gestion Cobranza`
,`Fecha_Cargo_Presto_Plus`
,`Monto_Cargo_Presto_Plus`
,`ID_Op_CRM`
,FLOOR(`Monto_cobranza_inicial`)
,`Dias_atraso_inicial` 
,`Estado_inicial`
,`Grupo`
,''
,''
, DATE_FORMAT(`FechaUltimoBarrido`, '%d-%m-%y')
,`Tipo_ultimo_barrido`  
,`Banco_utlimo_barrido`
,`fecha_ultimo_pago_parcial`
,`Fecha_ult_deposito`
,`Dias_ult_debito_banco`
,`PayingAgentBlockedRules`
,`CantTotalCuotas`
,`NroCuotaExigible`
,FLOOR(`Deuda_crossselling`)
,`FechaEstimadaDeCobro`
,`ImporteCobradoMesActualDebitoDirecto`
,`ProbabilidadDeCobro`
,`MaxFechaRendicion`
,`MaxFechaCobro`
,`ScorePrestamo`
,`email`
,`celular`
FROM {0} ca
WHERE (ca.Estado_Mambu is null || ca.Estado_Mambu NOT IN ('ACTIVE - PARTIALLY_DISBURSED'))
AND LENGTH(@gestion_esp := TRIM(COALESCE(CASE WHEN `Cliente_en_Gest_Especial` IS NOT NULL AND LENGTH(TRIM(`Cliente_en_Gest_Especial`)) > 0
                    THEN `Cliente_en_Gest_Especial`
                ELSE NULL END, CASE WHEN `Promesa_Pago_Dias_Vencer` > 0 THEN `Promesa_Pago_Desc` ELSE NULL END, ''))) = 0
ORDER BY ProbabilidadDeCobro DESC;
