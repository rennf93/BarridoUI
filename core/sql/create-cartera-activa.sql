CREATE TEMPORARY TABLE {2}_f_ultimo_debito AS
SELECT d.PARENTACCOUNTKEY, max(d.Fecha_ult_deposito) as Fecha_ult_deposito, sum(Importe_cobrado_mes_actual_total) as Importe_cobrado_mes_actual_total
			from (
				select l.PARENTACCOUNTKEY, max(l.ENTRYDATE) as Fecha_ult_deposito,
					  sum(case when left(l.ENTRYDATE, 7) = left(current_date, 7) then l.AMOUNT else 0.00 end) as Importe_cobrado_mes_actual_total
				from loantransaction l
				  join transactiondetails tdl on tdl.ENCODEDKEY  = l.DETAILS_ENCODEDKEY_OID
				  join transactionchannel tcl on tcl.ENCODEDKEY = tdl.TRANSACTIONCHANNELKEY
				where l.type ='REPAYMENT'
				  and l.REVERSALTRANSACTIONKEY is null
				group by l.PARENTACCOUNTKEY
				UNION
				select l.PARENTACCOUNTKEY, max(l.ENTRYDATE) as Fecha_ult_deposito,
					sum(case when left(l.ENTRYDATE, 7) = left(current_date, 7) then l.AMOUNT else 0.00 end) as Importe_cobrado_mes_actual_total
				from savingstransaction l
				  join transactiondetails tdl on tdl.ENCODEDKEY  = l.DETAILS_ENCODEDKEY_OID
				  join transactionchannel tcl on tcl.ENCODEDKEY = tdl.TRANSACTIONCHANNELKEY
				where l.type ='DEPOSIT'
				  and l.REVERSALTRANSACTIONKEY is null
				group by l.PARENTACCOUNTKEY
				) as d
			group by d.PARENTACCOUNTKEY;

CREATE INDEX {2}_f_ultimo_debito_IDX USING BTREE ON {2}_f_ultimo_debito (PARENTACCOUNTKEY);

CREATE TABLE {2}
SELECT DISTINCT
loanaccount.id AS 'Id',
@estado := CASE WHEN TRIM(UPPER(loanaccount.accountState)) IN ('PARTIAL_APPLICATION', 'PENDING_APPROVAL')
    THEN 'PENDIENTE'
   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('ACTIVE')
    THEN 'VIGENTE'
   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('APPROVED')
    THEN 'APROBADO'
   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('ACTIVE_IN_ARREARS')
    THEN 'MORA'
   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('CLOSED', 'CLOSED_WRITTEN_OFF')
    THEN 'CANCELADO'
   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('CLOSED_REJECTED')
    THEN 'RECHAZADO'
   ELSE 'ESTADO_DESCONOCIDO' END AS 'Estado',
CONCAT(loanaccount.accountstate, IFNULL(CONCAT(' - ', loanaccount.ACCOUNTSUBSTATE), '')) AS 'Estado_Mambu',

(SELECT customfieldvalue.value
    FROM customfield
    JOIN customfieldvalue
        ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
    WHERE customfield.id = 'id_gestion_especial'
        AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Cliente_en_Gest_Especial',

'-' AS 'Gestor',
'' AS 'Status',

IFNULL((SELECT IFNULL(customfieldvalue.value, '')
    FROM customfield
    JOIN customfieldvalue
    ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
    WHERE customfield.id = 'id_suc_del_prestamo'
    AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), branch.id) AS 'Sucursal_Prestamo', -- NombreEntidad

IFNULL((SELECT IFNULL(customfieldvalue.value, '')
    FROM customfield
    JOIN customfieldvalue
    ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
    WHERE customfield.id = 'id_centro_prestamo'
    AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), branch.id) AS 'Centro_Prestamo',

IFNULL(TRIM(CONCAT(
  CONCAT(TRIM(client.firstname), ' ')
  , TRIM(IFNULL(CONCAT((client.middlename), ' '), ''))
  , TRIM(client.lastname)
)), '-') AS 'AyN',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_address_street_name'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'Calle - Cliente',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_address_street_number'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'Nro - Cliente',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_address_region'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'Provincia - Cliente',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_address_postal_code'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'CP - Cliente',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_dni'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'DNI',

loanproduct.productname AS 'NombreLinea',
DATE_FORMAT(disbursementdetails.disbursementdate, '%d-%m-%y') AS 'fecha_otorgado',

TRUNCATE(loanaccount.loanAmount, 2) AS 'Capital',
loanaccount.repaymentInstallments AS 'Plazo',

@valor_cuota := repayment_agg.valor_cuota  AS 'ValorCuota',

DATE_FORMAT(repayment_agg.Ultimo_Vto, '%d-%m-%y') AS 'Ultimo_Vto',
DATE_FORMAT(repayment_agg.FecUltCuotaImpaga, '%d-%m-%y') AS 'FecUltCuotaImpaga',
DATE_FORMAT(repayment_agg.ProxVto, '%d-%m-%y') AS 'Proximo_Vto',
DATE_FORMAT(repayment_agg.Fecha1vto, '%d-%m-%y') AS 'fecha_1Vto',

ifnull(DATE_FORMAT((select max(r3.LASTPAIDDATE)
        from repayment as r3
        where r3.PARENTACCOUNTKEY = repayment_agg.PARENTACCOUNTKEY
        and month(r3.LASTPAIDDATE) = month(DATE_SUB(curdate(), INTERVAL 1 MONTH))), '%d-%m-%y'), '') as 'FecUltCuotaPagaMesAnt',

repayment_agg.MesCepa AS 'Mes_cepa',
DATE_FORMAT(repayment_agg.FechaUltPagoParcial, '%d-%m-%y') AS 'fecha_ultimo_pago_parcial',
repayment_agg.DiasAtraso AS 'DiasAtraso',

@mora_cuotas := TRUNCATE((loanaccount.principaldue + loanaccount.interestdue + loanaccount.penaltydue + loanaccount.feesdue), 2) AS 'MoraCuotas',

@punit_adeudado := TRUNCATE(repayment_agg.PunitoriosAdeudados, 2) AS 'PunitoriosAdeudados',
@cargo_adeudado := TRUNCATE(repayment_agg.CargosAdeudados, 2) AS 'CargosAdeudados',
TRUNCATE(repayment_agg.CantidadCuotasAdeudadas, 2) AS 'CantidadCuotasAdeudadas',
TRUNCATE(repayment_agg.SaldoCuotasNoVencidas, 2) AS 'SaldoCuotasNoVencidas',

TRUNCATE(repayment_agg.SaldoExigible, 2) as 'SaldoExigible',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_cbu'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'CBU',

(SELECT IFNULL(customfieldvalue.value, '')
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_dia_fijado'
AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Dia_Fijado',

(SELECT IFNULL(customfieldvalue.value, '')
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_gestion_cobranza'
AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Gestion Cobranza',

(SELECT IFNULL(customfieldvalue.value, '')
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_fecha_alta_presto_plus'
AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Fecha_Cargo_Presto_Plus',

(SELECT IFNULL(customfieldvalue.value, '')
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
WHERE customfield.id = 'id_adicional_presto_plus'
AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Monto_Cargo_Presto_Plus',


(SELECT IFNULL(customfieldvalue.value, '')
FROM customfield
JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY 
WHERE customfield.id = 'id_opp_salesforce'
AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'ID_Op_CRM',

@promesa_desc := (SELECT IFNULL(customfieldvalue.value, '')
    FROM customfield
    JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
    WHERE customfield.id = 'id_promesa_descripcion'
    AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Promesa_Pago_Desc',
@promesa_venc := (SELECT IFNULL(customfieldvalue.value, '')
    FROM customfield
    JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
    WHERE customfield.id = 'id_promesa_vencimiento'
    AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Promesa_Pago_Vencimiento',
(SELECT IFNULL(customfieldvalue.value, '')
    FROM customfield
    JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
    WHERE customfield.id = 'id_promesa_monto'
    AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Promesa_Pago_Monto',

CASE WHEN @promesa_venc IS NULL OR (@promesa_desc <> 'Refifix' AND @promesa_desc <> 'Devuelve prestamo') THEN 0 ELSE DATEDIFF(@promesa_venc, NOW()) + 1 END as Promesa_Pago_Dias_Vencer,

'' AS 'CBU_Pred',

IFNULL(TRIM(client.EMAILADDRESS), '-') AS 'email',
IFNULL(client.MOBILEPHONE1, '-') AS 'celular',
IFNULL(client.HOMEPHONE, '-') AS 'telefono_alternativo',

(SELECT customfieldvalue.value
    FROM customfieldvalue
    JOIN customfield
        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
    WHERE customfield.id = 'client_cuil'
        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'Cliente_Cuit',

TRUNCATE(loanaccount.principalbalance, 2) AS 'SaldoDeCapitalAdeudado',
TRUNCATE(loanaccount.interestbalance, 2) AS 'SaldoDeInteres',
TRUNCATE(loanaccount.accruedinterest, 2) as 'InteresDevengado',
TRUNCATE(loanaccount.feesbalance, 2) as 'SaldoDeCargo',
TRUNCATE(loanaccount.penaltybalance, 2) as 'SaldoDePenalizacion',
TRUNCATE(loanaccount.principaldue, 2) as 'PrincipalPendiente',
TRUNCATE(loanaccount.interestdue, 2) as 'InteresPendiente',
TRUNCATE(loanaccount.feesdue, 2) as 'CargosPendientes',
TRUNCATE(loanaccount.penaltydue, 2) as 'PenalizacionPendiente',
TRUNCATE(loanaccount.principalpaid + loanaccount.interestpaid + loanaccount.feespaid + loanaccount.penaltypaid, 2) as 'TotalPagado', 
TRUNCATE(loanaccount.principalpaid, 2) as 'PrincipalPagado', 
TRUNCATE(loanaccount.interestpaid, 2) as 'InteresPagado', 
TRUNCATE(loanaccount.feespaid, 2) as 'CargosPagados', 
TRUNCATE(loanaccount.penaltypaid, 2) as 'PenalizacionPagada', 

client.id AS 'Id_Cliente',

CASE WHEN loanaccount.accountState IN ('PARTIAL_APPLICATION', 'PENDING_APPROVAL')
     THEN loanaccount.id
     ELSE '' END AS 'Id_Solicitud',

@total_cta_rec := TRUNCATE(savingsaccount.BALANCE, 2) AS 'Total_Cta_Recaudadora',

@cargos_y_penalidades := IFNULL((SELECT ROUND(SUM(r3.PENALTYDUE - r3.PENALTYPAID) + SUM(r3.FEESDUE - r3.FEESPAID), 2)
            from repayment as r3
            where r3.PARENTACCOUNTKEY=loanaccount.encodedkey
            and r3.STATE in ('LATE', 'PENDING', 'PARTIALLY_PAID')
            and DATE_FORMAT(r3.duedate, '%y%m%d') <= DATE_FORMAT(repayment_agg.ProxVto, '%y%m%d')
            ), 0.00) AS 'Cargos_y_Penalidades',

@deuda_cuota := IFNULL((SELECT ROUND(SUM(r4.PRINCIPALDUE - r4.PRINCIPALPAID + r4.INTERESTDUE - r4.INTERESTPAID), 2)
            from repayment as r4
            where r4.PARENTACCOUNTKEY=loanaccount.encodedkey
            and DATE_FORMAT(r4.duedate, '%y%m%d') = DATE_FORMAT(repayment_agg.ProxVto, '%y%m%d')
            ), 0.00) AS 'Deuda_Cuota_ProxVto',

TRUNCATE((CASE
        WHEN @estado = 'VIGENTE' AND ROUND(@mora_cuotas) <= 0 AND DATEDIFF(repayment_agg.ProxVto, NOW()) < 20 THEN @valor_cuota + @cargos_y_penalidades
        ELSE @mora_cuotas
        END - IFNULL(savingsaccount.BALANCE, 0.00)), 2) AS 'Total_a_Barrer',

TRUNCATE((CASE
        WHEN @estado = 'VIGENTE' AND ROUND(@mora_cuotas) <= 0 AND DATEDIFF(repayment_agg.ProxVto, NOW()) < 20 THEN @deuda_cuota + @cargos_y_penalidades
        ELSE @mora_cuotas
        END - IFNULL(savingsaccount.BALANCE, 0.00)), 2) AS 'Total_a_Barrer_Nuevo',

TRUNCATE((CASE WHEN @estado = 'VIGENTE'
    THEN @valor_cuota + @cargos_y_penalidades
    ELSE @mora_cuotas
    END - IFNULL(savingsaccount.BALANCE, 0.00)), 2) AS 'Total_a_Barrer_anterior',

@bucket := CASE WHEN @estado = 'VIGENTE'
   THEN 
     CASE WHEN DATE_FORMAT(repayment_agg.ProxVto, '%y%m%d') = DATE_FORMAT(repayment_agg.Fecha1vto, '%y%m%d')
        THEN '(1) Nuevos'
       WHEN DATE_FORMAT(repayment_agg.ProxVto, '%y%m%d') > DATE_FORMAT(repayment_agg.Fecha1vto, '%y%m%d')
        THEN '(2) Vigentes'
       ELSE '' END
   ELSE 
     CASE 
     WHEN repayment_agg.DiasAtraso <= 30
        THEN '(3) Mora 1 a 30'
       WHEN repayment_agg.DiasAtraso <= 60
        THEN '(4) Mora 31 a 60'
       WHEN repayment_agg.DiasAtraso <= 90
        THEN '(5) Mora 61 a 90'
       WHEN repayment_agg.DiasAtraso <= 120
        THEN '(6) Mora 91 a 120'
       WHEN repayment_agg.DiasAtraso <= 180
        THEN '(7) Mora 121 a 180'
       WHEN repayment_agg.DiasAtraso <= 360
        THEN '(8) Mora 181 a 360'
       WHEN repayment_agg.DiasAtraso <= 720
        THEN '(9) Mora 361 a 720'
       ELSE '(10) Mora>720' END   
   END as 'Bucket',

ROUND(CASE WHEN @bucket = '(1) Nuevos' AND ROUND(@total_cta_rec) < ROUND(@valor_cuota)
    THEN @valor_cuota - @total_cta_rec
   WHEN @bucket = '(1) Nuevos' AND ROUND(@total_cta_rec) > ROUND(@valor_cuota)
    THEN 0.00
   WHEN @bucket = '(2) Vigentes' AND ROUND(@mora_cuotas) <= 0 AND ROUND(@total_cta_rec) >= ROUND(@valor_cuota)
    THEN 0.00
   WHEN @bucket = '(2) Vigentes' AND ROUND(@mora_cuotas) <= 0 AND ROUND(@total_cta_rec) < ROUND(@valor_cuota)
    THEN @valor_cuota - @total_cta_rec
   WHEN @bucket = '(2) Vigentes' AND ROUND(@mora_cuotas) > 0 AND ROUND(@total_cta_rec) < ROUND(@valor_cuota)
    THEN @valor_cuota + @mora_cuotas - @punit_adeudado - @total_cta_rec
   WHEN @bucket = '(3) Mora 1 a 30' AND ROUND(@mora_cuotas) > 0 AND DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(repayment_agg.Ultimo_Vto, '%y%m%d')
    THEN @valor_cuota + @mora_cuotas - @punit_adeudado - @total_cta_rec
   WHEN @bucket = '(3) Mora 1 a 30' AND ROUND(@mora_cuotas) > 0 AND DATE_FORMAT(CURDATE(), '%y%m%d') > DATE_FORMAT(repayment_agg.Ultimo_Vto, '%y%m%d')
    THEN @mora_cuotas - @punit_adeudado - @total_cta_rec
   WHEN @bucket = '(4) Mora 31 a 60' AND ROUND(@mora_cuotas) > 0 AND DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(repayment_agg.Ultimo_Vto, '%y%m%d')
    THEN @valor_cuota + @mora_cuotas - @punit_adeudado - @total_cta_rec
   WHEN @bucket = '(4) Mora 31 a 60' AND ROUND(@mora_cuotas) > 0 AND DATE_FORMAT(CURDATE(), '%y%m%d') > DATE_FORMAT(repayment_agg.Ultimo_Vto, '%y%m%d')
    THEN @mora_cuotas - @punit_adeudado - @total_cta_rec
   WHEN @bucket = '(5) Mora 61 a 90' AND ROUND(@mora_cuotas) > 0 AND DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(repayment_agg.Ultimo_Vto, '%y%m%d')
    THEN @valor_cuota + @mora_cuotas - @punit_adeudado - @total_cta_rec
   WHEN @bucket = '(5) Mora 61 a 90' AND ROUND(@mora_cuotas) > 0 AND DATE_FORMAT(CURDATE(), '%y%m%d') > DATE_FORMAT(repayment_agg.Ultimo_Vto, '%y%m%d')
    THEN @mora_cuotas - @punit_adeudado - @total_cta_rec
   ELSE @mora_cuotas - @punit_adeudado - @total_cta_rec END, 2) as 'K_mas_I'
, 0.0 as 'K_mas_I_inicial'
, 0.0 as 'Sueldo'
, '*' as 'Grupo' 
, CURDATE() as 'Fecha_cartera'
, null as 'FechaUltimoBarrido'
, '' as 'Con_cobro_2da_quincena'
, 0.0 as 'Monto_cobranza_inicial' 
, 0   as 'Dias_atraso_inicial'
, ''  as 'Estado_inicial'
, null as 'Fecha_cartera_inicial'
, null as 'Tipo_ultimo_barrido'
, null as 'Banco_utlimo_barrido'  
, null as 'PayingAgentBlockedRules'
, DATE_FORMAT(ult_pago_banco.Fecha_ult_deposito, '%d-%m-%y') as 'Fecha_ult_deposito'
, CASE WHEN ult_pago_banco.Fecha_ult_deposito IS NULL THEN null ELSE DATEDIFF(CURDATE(), ult_pago_banco.Fecha_ult_deposito) END as 'Dias_ult_debito_banco'
, CASE WHEN ult_pago_banco.Importe_cobrado_mes_actual_total IS NULL THEN 0.00 ELSE ult_pago_banco.Importe_cobrado_mes_actual_total END as 'ImporteCobradoMesActualTotal'
, 0.0 as 'Deuda_crossselling'
, CantTotalCuotas
, NroCuotaExigible
, null as 'FechaEstimadaDeCobro'
, 0.0 as 'ProbabilidadDeCobro'
, 0 as 'ScorePrestamo'
, null as 'ImporteCobradoMesActualDebitoDirecto'
, null as 'MaxFechaRendicion'
, null as 'MaxFechaCobro'
FROM client
JOIN loanaccount
    ON (client.encodedkey = loanaccount.accountHolderKey)
JOIN disbursementdetails
    ON (loanaccount.DISBURSEMENTDETAILSKEY = disbursementdetails.encodedkey)
JOIN loanproduct
    ON (loanaccount.productTypeKey = loanproduct.encodedkey)
JOIN
(
  SELECT MIN(duedate) AS Fecha1vto, parentaccountkey,
        ROUND(MIN(PRINCIPALDUE) + MAX(INTERESTDUE),2) AS valor_cuota,

        CONCAT(CASE
            WHEN MONTH(MIN(duedate)) = 1 THEN 'Ene.'
            WHEN MONTH(MIN(duedate)) = 2 THEN 'Feb.'
            WHEN MONTH(MIN(duedate)) = 3 THEN 'Mar.'
            WHEN MONTH(MIN(duedate)) = 4 THEN 'Abr.'
            WHEN MONTH(MIN(duedate)) = 5 THEN 'May.'
            WHEN MONTH(MIN(duedate)) = 6 THEN 'Jun.'
            WHEN MONTH(MIN(duedate)) = 7 THEN 'Jul.'
            WHEN MONTH(MIN(duedate)) = 8 THEN 'Ago.'
            WHEN MONTH(MIN(duedate)) = 9 THEN 'Sept.'
            WHEN MONTH(MIN(duedate)) = 10 THEN 'Oct.'
            WHEN MONTH(MIN(duedate)) = 11 THEN 'Nov.'
            WHEN MONTH(MIN(duedate)) = 12 THEN 'Dic.'
            ELSE '-' END, ' ', YEAR(MIN(duedate))) AS 'MesCepa' ,

      SUM(CASE WHEN state = 'LATE' THEN 1 ELSE 0 END) AS 'CantidadCuotasAdeudadas',

      IFNULL((SELECT MIN(a.duedate) FROM repayment AS a
                            WHERE DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
                            AND a.parentaccountkey = repayment.parentaccountkey
                            GROUP BY a.parentaccountkey), MAX(duedate)) AS 'ProxVto',

      MAX(CASE WHEN state = 'LATE' THEN DATEDIFF(NOW(), duedate) ELSE 0 END) AS 'DiasAtraso',

      MAX(duedate) AS 'Ultimo_Vto',

      (select min(DUEDATE)
        from repayment as r2
        where r2.STATE in ('LATE', 'PENDING', 'PARTIALLY_PAID')
        and r2.PARENTACCOUNTKEY=repayment.PARENTACCOUNTKEY) as 'FecUltCuotaImpaga',

      MAX(lastpaiddate) AS 'FechaUltPagoParcial',

      SUM(CASE WHEN state = 'PENDING' THEN (principaldue + interestdue + penaltydue + taxpenaltydue + feesdue + taxfeesdue) ELSE 0 END) AS 'SaldoCuotasNoVencidas',

      IFNULL(SUM(CASE
        WHEN state in ('LATE', 'PARTIALLY_PAID')
        THEN (PRINCIPALDUE-PRINCIPALPAID)
        ELSE 0.00 END), 0.00) AS 'CuotasPurasAdeudadas',

      SUM(CASE WHEN state in ('LATE', 'PARTIALLY_PAID') THEN
             (PRINCIPALDUE - PRINCIPALPAID +
              PENALTYDUE - PENALTYPAID +
              TAXINTERESTDUE - TAXINTERESTPAID +
              TAXFEESDUE - TAXFEESPAID +
              TAXPENALTYDUE - TAXPENALTYPAID)
             ELSE 0.00 END) AS 'SaldoExigible',

      COUNT(1) AS 'CantTotalCuotas',
             
      SUM(CASE WHEN state in ('PAID') THEN
             1 ELSE 0 END) + 1 AS 'NroCuotaExigible',

      SUM(INTERESTDUE) AS 'capital_interes',

      SUM(penaltydue - penaltypaid) AS 'PunitoriosAdeudados',
      SUM(FEESDUE - FEESPAID) AS 'CargosAdeudados'

  FROM repayment
  GROUP BY parentaccountkey
) repayment_agg
    ON (loanaccount.encodedkey = repayment_agg.parentaccountkey)
JOIN branch
    ON (client.assignedBranchKey = branch.encodedkey)
JOIN savingsaccount
    ON (client.encodedkey = savingsaccount.ACCOUNTHOLDERKEY)
LEFT JOIN {2}_f_ultimo_debito as ult_pago_banco
	ON ult_pago_banco.PARENTACCOUNTKEY = loanaccount.ENCODEDKEY
WHERE loanaccount.accountState NOT IN ('APPROVED','CLOSED', 'CLOSED_REJECTED', 'CLOSED_WRITTEN_OFF', 'PARTIAL_APPLICATION', 'PENDING_APPROVAL')
ORDER BY 1;

ALTER TABLE {2} MODIFY COLUMN Fecha_cartera DATE DEFAULT null;

ALTER TABLE {2} MODIFY COLUMN DNI VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_bin NULL;

ALTER TABLE {2} MODIFY COLUMN Sueldo bigint NULL;

ALTER TABLE {2} MODIFY COLUMN Grupo VARCHAR(50) NULL;

ALTER TABLE {2} MODIFY COLUMN Estado_inicial VARCHAR(50) NULL;

ALTER TABLE {2} MODIFY COLUMN Monto_cobranza_inicial DECIMAL(42,2) NULL;

ALTER TABLE {2} MODIFY COLUMN ImporteCobradoMesActualDebitoDirecto DECIMAL(42,2) NULL;

ALTER TABLE {2} MODIFY COLUMN K_mas_I_inicial DECIMAL(42,2) NULL;

ALTER TABLE {2} MODIFY COLUMN Fecha_cartera_inicial DATE NULL;

ALTER TABLE {2} MODIFY COLUMN MaxFechaRendicion DATE NULL;

ALTER TABLE {2} MODIFY COLUMN MaxFechaCobro DATE NULL;

ALTER TABLE {2} MODIFY COLUMN Con_cobro_2da_quincena VARCHAR(10) NULL;

ALTER TABLE {2} MODIFY COLUMN FechaUltimoBarrido DATE NULL;

ALTER TABLE {2} MODIFY COLUMN FechaEstimadaDeCobro DATE NULL;

ALTER TABLE {2} MODIFY COLUMN Tipo_ultimo_barrido VARCHAR(10) NULL;

ALTER TABLE {2} MODIFY COLUMN Banco_utlimo_barrido VARCHAR(50) NULL;

ALTER TABLE {2} MODIFY COLUMN PayingAgentBlockedRules VARCHAR(4096) NULL;

ALTER TABLE {2} MODIFY COLUMN Deuda_crossselling DECIMAL(42,2) NULL;

CREATE INDEX {2}_ID_IDX USING BTREE ON {2} (Id);

CREATE INDEX {2}_DNI_IDX USING BTREE ON {2} (DNI);
