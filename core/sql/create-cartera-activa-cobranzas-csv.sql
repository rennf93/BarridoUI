select 'Id'
,'Estado'
,'Estado_Mambu'
,'Cliente_en_Gest_Especial'
,'Sucursal_Prestamo'
,'Centro_Prestamo'
,'AyN'
,'DNI'
,'NombreLinea'
,'fecha_otorgado'
,'Capital'
,'Plazo'
,'ValorCuota'
,'FecUltCuotaImpaga'
,'Proximo_Vto'
,'fecha_1Vto'
,'Mes_cepa'
,'fecha_ultimo_pago_parcial'
,'DiasAtraso'
,'MoraCuotas'
,'PunitoriosAdeudados'
,'CantidadCuotasAdeudadas'
,'SaldoCuotasNoVencidas'
,'email'
,'celular'
,'telefono_alternativo'
,'Cliente_Cuit'
,'Id_Cliente'
,'Total_Cta_Recaudadora'
,'Total_a_Barrer'
,'Bucket'
,'BucketAtCliente'
,'Calle - Cliente'
,'Nro - Cliente'
,'Provincia - Cliente'
,'CP - Cliente'
, 'K_mas_I_inicial'
, 'K_mas_I'
,'SaldoDelPrincipal'
,'SaldoDeInteres'
,'InteresDevengado'
,'SaldoDeCargo'
,'SaldoDePenalizacion'
,'TotalAPagar'
,'ImporteCobradoMesActualTotal'
,'PrincipalPendiente'
,'InteresPendiente'
,'CargosPendientes'
,'PenalizacionPendiente'
,'TotalPagado'
,'PrincipalPagado'
,'InteresPagado' 
,'CargosPagados'
,'PenalizacionPagada'
,'Promesa_Pago_Desc'
,'Promesa_Pago_Vencimiento'
,'Promesa_Pago_Monto'
,'ScorePrestamo'
,'Prioridad'
UNION ALL
SELECT `Id`
,`Estado`
,`Estado_Mambu`
,`Cliente_en_Gest_Especial`
,`Sucursal_Prestamo`
,`Centro_Prestamo`
,`AyN`
,`DNI`
,`NombreLinea`
,`fecha_otorgado`
,FLOOR(`Capital`)
,`Plazo`
,FLOOR(`ValorCuota`)
,`FecUltCuotaImpaga`
,`Proximo_Vto`
,`fecha_1Vto`
,`Mes_cepa`
,`fecha_ultimo_pago_parcial`
,`DiasAtraso`
,`MoraCuotas`
,FLOOR(`PunitoriosAdeudados`)
,`CantidadCuotasAdeudadas`
,FLOOR(`SaldoCuotasNoVencidas`)
,`email`
,`celular`
,`telefono_alternativo`
,`Cliente_Cuit`
,`Id_Cliente`
,FLOOR(`Total_Cta_Recaudadora`)
,FLOOR(`Total_a_Barrer` + `Deuda_crossselling`)
,`Bucket`
, '' as `BucketAtCliente`
,`Calle - Cliente`
, `Nro - Cliente`
,`Provincia - Cliente`
,`CP - Cliente`
, `K_mas_I_inicial`
, CASE WHEN K_mas_I > 0 THEN FLOOR(TRUNCATE(K_mas_I, 2)) ELSE 0 END
,SaldoDeCapitalAdeudado
,SaldoDeInteres
,InteresDevengado
,SaldoDeCargo
,SaldoDePenalizacion
,`MoraCuotas`
,ImporteCobradoMesActualTotal
,PrincipalPendiente
,InteresPendiente
,CargosPendientes
,PenalizacionPendiente
,TotalPagado
,PrincipalPagado
,InteresPagado
,CargosPagados
,PenalizacionPagada
,Promesa_Pago_Desc
,Promesa_Pago_Vencimiento
,Promesa_Pago_Monto
,ScorePrestamo
,'' as 'Prioridad'
FROM {0} ca;
