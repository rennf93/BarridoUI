create table cartera_reno
SELECT `Fecha_Proceso`
,`Id`
,`Estado`
,`Estado_Mambu`
,`Dias_Atraso`
,`Cuota_Capital`
,`Cuota_Interes`
,`Max_Atraso_Pago_Cuota`
,`Ultima_Fecha_Cobro`
,`Antiguedad_Cobro`
,`Plazo_Prestamo`
,`Fecha_Otorgado`
,CEIL(`Valor_Cuota`) as 'input_current_quota'
,`Tasa_Interes`
,`Saldo_Capital_Adeudado` as 'input_pending_capital'
,`Capital` as 'input_original_capital'
,`Pais`
,`Nombre_Linea_Prestamo`
,`Id_Linea_Prestamo`
,`Sucursal_Prestamo`
,`Centro_Prestamo`
,`DNI` as 'input_dni'
,`Cuil`
,`Nombre_Cliente` as 'input_firstname'
,`Apellido_Cliente` as 'input_lastname'
,`Fecha_Nacimiento` as 'input_birthdate'
,`Cantidad_Cuotas_Adeudadas` as 'input_pending_quotas'
,`NroUltimaCuotaPaga`
,`Tipo_Fideicomiso`
,`Fideicomiso`
,`Sexo` as 'input_gender'
,`Es_Producto_Vigente`
,`Remaining_Installments` as 'input_remaining_installments'
,`First_Remaining_Installment_Date` as 'input_first_remaining_installment_date'
,CONCAT(UPPER(TRIM(`Centro_Prestamo`)), '_AR') AS `input_brand`
, 0 as 'Max_Score_BCRA'
, 0 as 'Score_Bhe'
, null as 'Fecha_Score_Bhe'
, null as 'Reglas_Bloqueo_Agente_Pago'
, 0 as 'Tiene_Producto_Vigente'
, null 'Ids_Fideicomiso_Prestamo'
, null 'Descs_Fideicomiso_Prestamo'
, null 'bucket_reno'
, null as 'Segmento_Tasa'
, DATE(FROM_UNIXTIME(0)) as 'input_last_lost_opportunity_date'
, 0 as 'input_remaining_payment_cycle_business_day_ord'
FROM
(SELECT DISTINCT
	date_format(now(),'%Y/%m/%d') as 'Fecha_Proceso',
	loanaccount.id AS 'Id',
	CASE WHEN TRIM(UPPER(loanaccount.accountState)) IN ('PARTIAL_APPLICATION', 'PENDING_APPROVAL')
	    THEN @estado := 'PENDIENTE'
	   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('ACTIVE')
	    THEN @estado := 'VIGENTE'
	   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('APPROVED')
	    THEN @estado := 'APROBADO'
	   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('ACTIVE_IN_ARREARS')
	    THEN @estado := 'MORA'
	   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('CLOSED', 'CLOSED_WRITTEN_OFF')
	    THEN @estado := 'CANCELADO'
	   WHEN TRIM(UPPER(loanaccount.accountState)) IN ('CLOSED_REJECTED')
	    THEN @estado := 'RECHAZADO'
	   ELSE @estado := 'ESTADO_DESCONOCIDO' END AS 'Estado',

	case when @estado in ('VIGENTE', 'MORA', 'APROBADO', 'PENDIENTE' ) then 1 else 0 end as 'Es_Producto_Vigente',

	CONCAT(loanaccount.accountstate, IFNULL(CONCAT(' - ', loanaccount.ACCOUNTSUBSTATE), '')) AS 'Estado_Mambu',
	loanaccount.accountstate as 'AccountState',
	loanaccount.ACCOUNTSUBSTATE as 'AccountSubState',
	TRUNCATE(loanaccount.loanAmount, 2) AS 'Capital',


	(Select Country from address LIMIT 1) as 'Pais',

	COALESCE((SELECT customfieldvalue.value
	    FROM customfield
	    JOIN customfieldvalue
	        ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	    WHERE customfield.id = 'id_gestion_especial'
	        AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), '') AS 'Cliente_en_Gest_Especial',

	COALESCE((SELECT COALESCE(REPLACE(customfieldvalue.value, '-',''), '')
	FROM customfield
	JOIN customfieldvalue
	ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'client_cuil'
	AND customfieldvalue.PARENTKEY = client.ENCODEDKEY), '') AS 'Cuil',

	(SELECT COUNT(*)
	FROM repayment
	WHERE repayment.PARENTACCOUNTKEY = loanaccount.ENCODEDKEY
	AND repayment.STATE <> 'PAID') as 'Remaining_Installments',

	(SELECT MIN(DUEDATE)
	FROM repayment
	WHERE repayment.PARENTACCOUNTKEY = loanaccount.ENCODEDKEY
	AND repayment.STATE <> 'PAID') as 'First_Remaining_Installment_Date',

	COALESCE((SELECT COALESCE(customfieldvalue.value, '')
	FROM customfield
	JOIN customfieldvalue
	ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'id_suc_del_prestamo'
	AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), branch.id) AS 'Sucursal_Prestamo',

	COALESCE((SELECT COALESCE(customfieldvalue.value, '')
	FROM customfield
	JOIN customfieldvalue
	ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'id_centro_prestamo'
	AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), branch.id) AS 'Centro_Prestamo',

	TRIM(client.firstname) AS 'Nombre_Cliente',
	TRIM(client.lastname) AS 'Apellido_Cliente',
	COALESCE(DATE_FORMAT(client.BIRTHDATE, '%d-%m-%Y'), '') as 'Fecha_Nacimiento',

	COALESCE((SELECT COALESCE(customfieldvalue.value, '')
	FROM customfield
	JOIN customfieldvalue
	ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'serie_lote_fide'
	AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), '') AS 'Fideicomiso',

	COALESCE((SELECT COALESCE(customfieldvalue.value, '')
	FROM customfield
	JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'tipo_fide'
	AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY), '') AS 'Tipo_Fideicomiso',

	(SELECT customfieldvalue.value
	    FROM customfieldvalue
	    JOIN customfield
	        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
	    WHERE customfield.id = 'client_dni'
	        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'DNI',

	loanproduct.productname AS 'Nombre_Linea_Prestamo',
	loanproduct.ID AS 'Id_Linea_Prestamo',

	truncate(interestproductsettings.DEFAULTINTERESTRATE,2) as 'Tasa_Interes',

	COALESCE(DATE_FORMAT(disbursementdetails.disbursementdate, '%Y-%m-%d'), '') AS 'Fecha_Otorgado',

	`Cuota_Capital`,
	`Cuota_Interes`,
	`Max_Atraso_Pago_Cuota`,
	COALESCE(DATE_FORMAT(`Ultima_Fecha_Cobro`, '%Y-%m-%d'),'') AS 'Ultima_Fecha_Cobro',
    COALESCE(`Antiguedad_Cobro`, 0) AS 'Antiguedad_Cobro',

	loanaccount.repaymentInstallments AS 'Plazo_Prestamo',

	@valor_cuota := repayment_agg.Cuota AS 'Valor_Cuota',

	DATE_FORMAT(repayment_agg.Ultimo_Vto, '%Y-%m-%d') AS 'Ultimo_Vto',
	DATE_FORMAT(repayment_agg.FecUltCuotaImpaga, '%Y-%m-%d') AS 'FecUltCuotaImpaga',
	DATE_FORMAT(repayment_agg.ProxVto, '%Y-%m-%d') AS 'Proximo_Vto',
	DATE_FORMAT(repayment_agg.Fecha1vto, '%Y-%m-%d') AS 'fecha_1Vto',

	repayment_agg.Dias_Atraso AS 'Dias_Atraso',
	repayment_agg.NroUltimaCuotaPaga,

	@mora_cuotas := TRUNCATE((loanaccount.principaldue + loanaccount.interestdue + loanaccount.penaltydue + loanaccount.feesdue), 2) AS 'MoraCuotas',

	@punit_adeudado := TRUNCATE(repayment_agg.PunitoriosAdeudados, 2) AS 'Punit_adeudado',
	TRUNCATE(repayment_agg.Cantidad_Cuotas_Adeudadas, 0) AS 'Cantidad_Cuotas_Adeudadas',
	TRUNCATE(repayment_agg.SaldoCuotasNoVencidas, 2) AS 'SaldoCuotasNoVencidas',

	TRUNCATE(repayment_agg.SaldoExigible, 2) as 'SaldoExigible',

	(SELECT COALESCE(customfieldvalue.value, '')
	FROM customfield
	JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'id_gestion_cobranza'
	AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'Gestion_Cobranza',

	(SELECT COALESCE(customfieldvalue.value, '')
	FROM customfield
	JOIN customfieldvalue ON customfield.ENCODEDKEY = customfieldvalue.CUSTOMFIELDKEY
	WHERE customfield.id = 'id_opp_salesforce'
	AND customfieldvalue.PARENTKEY = loanaccount.ENCODEDKEY) AS 'ID_Op_CRM',

	COALESCE(TRIM(client.EMAILADDRESS), '-') AS 'email',
	COALESCE(client.MOBILEPHONE1, '-') AS 'celular',
	COALESCE(client.HOMEPHONE, '-') AS 'telefono_alternativo',

	(SELECT customfieldvalue.value
	    FROM customfieldvalue
	    JOIN customfield
	        ON customfieldvalue.CUSTOMFIELDKEY = customfield.ENCODEDKEY
	    WHERE customfield.id = 'client_cuil'
	        AND customfieldvalue.PARENTKEY = client.ENCODEDKEY) AS 'Cliente_Cuit',

	TRUNCATE(loanaccount.principalbalance, 2) AS 'Saldo_Capital_Adeudado',

	client.id AS 'Id_Cliente',

	CASE WHEN loanaccount.accountState IN ('PARTIAL_APPLICATION', 'PENDING_APPROVAL')
	     THEN loanaccount.id
	     ELSE '' END AS 'Id_Solicitud',

	@total_cta_rec := TRUNCATE(savingsaccount.BALANCE, 2) AS 'Total_Cta_Recaudadora',


	TRUNCATE((CASE WHEN @estado = 'VIGENTE' AND ROUND(@mora_cuotas) <= 0 AND DATEDIFF(repayment_agg.ProxVto, NOW()) < 20 THEN @valor_cuota + @cargos_y_penalidades
	        ELSE @mora_cuotas
	        END - COALESCE(savingsaccount.BALANCE, 0.00)), 2) AS 'Total_a_Barrer',

	TRUNCATE(repayment_agg.PunitoriosAdeudados, 2) AS 'PunitoriosAdeudados'

	,TRUNCATE(repayment_agg.CargosAdeudados, 2) AS 'CargosAdeudados'

	#, ult_pago_banco.Fecha_ult_deposito as 'Fecha_ult_deposito'

	,branch.id as 'Sucursal'
	,SUBSTRING(client.GENDER,1,1) as 'Sexo'


	FROM client
	JOIN loanaccount ON (client.encodedkey = loanaccount.accountHolderKey)
	JOIN disbursementdetails ON (loanaccount.DISBURSEMENTDETAILSKEY = disbursementdetails.encodedkey)
	JOIN loanproduct ON (loanaccount.productTypeKey = loanproduct.encodedkey)
	JOIN interestproductsettings ON loanproduct.INTERESTRATESETTINGSKEY = interestproductsettings.encodedkey
	JOIN
		(
		  SELECT MIN(duedate) AS 'Fecha1vto', parentaccountkey,

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

		      SUM(CASE WHEN state = 'LATE' THEN 1 ELSE 0 END) AS 'Cantidad_Cuotas_Adeudadas',

		      MAX(CASE WHEN state = 'LATE' THEN DATEDIFF(NOW(), duedate) ELSE 0 END) AS 'Dias_Atraso',

		      MAX(duedate) AS 'Ultimo_Vto',

		      (select min(DUEDATE)
		        from repayment r2
		        where r2.STATE in ('LATE', 'PENDING', 'PARTIALLY_PAID')
		        and r2.PARENTACCOUNTKEY=repayment.PARENTACCOUNTKEY) as 'FecUltCuotaImpaga',

		      SUM(CASE WHEN state = 'PENDING' THEN (principaldue + interestdue + penaltydue + taxpenaltydue + feesdue + taxfeesdue) ELSE 0 END) AS 'SaldoCuotasNoVencidas',

		      COALESCE(SUM(CASE
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

			  SUM(INTERESTDUE) AS 'capital_interes',

		      SUM(penaltydue - penaltypaid) AS 'PunitoriosAdeudados',

		      SUM(FEESDUE - FEESPAID) AS 'CargosAdeudados',

		      ROUND(MIN(PRINCIPALDUE) + MAX(INTERESTDUE),2) AS 'Cuota',

		      SUM(CASE WHEN state = 'PAID' THEN 1 ELSE 0 END) AS 'NroUltimaCuotaPaga',

		      MAX(PRINCIPALDUE) as 'Cuota_Capital',
		      MAX(interestdue - taxinterestdue) as 'Cuota_Interes',
		      max(DATEDIFF(COALESCE(lastpaiddate, NOW()), duedate)) as 'Max_Atraso_Pago_Cuota',
		      max(lastpaiddate) as 'Ultima_Fecha_Cobro',
		      min(datediff(DATE(NOW()), lastpaiddate)) as 'Antiguedad_Cobro',


		      @prox_venc := COALESCE((SELECT MIN(duedate) AS ProxVto
		                FROM repayment AS a
		                WHERE DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
		                    AND a.parentaccountkey = repayment.parentaccountkey
		                GROUP BY a.parentaccountkey), MAX(duedate)) AS 'ProxVto',

		      (SELECT ROUND(SUM(PENALTYDUE - PENALTYPAID) + SUM(FEESDUE - FEESPAID), 2)
		            from repayment as r2
		            where r2.PARENTACCOUNTKEY=repayment.PARENTACCOUNTKEY
		            and r2.STATE in ('LATE', 'PENDING', 'PARTIALLY_PAID')
		            and DATE_FORMAT(r2.duedate, '%y%m%d') <= DATE_FORMAT(@prox_venc, '%y%m%d')
		            ) AS cargos_y_penalidades


		  FROM repayment
		  GROUP BY parentaccountkey
		) repayment_agg ON (loanaccount.encodedkey = repayment_agg.parentaccountkey)

		JOIN branch ON (client.assignedBranchKey = branch.encodedkey)
		JOIN savingsaccount  ON (client.encodedkey = savingsaccount.ACCOUNTHOLDERKEY)
		WHERE NOT client.GENDER IS NULL
		ORDER BY 1
		) as ca
	where ca.Cliente_en_Gest_Especial = ''
	and ca.sucursal not in ('roela', 'deuda_cero')
	and ca.centro_prestamo NOT IN ('Deuda Cero', 'Roela')
	and ca.sucursal_prestamo not in ('Roela', 'Deuda Cero')
	and ca.Estado_Mambu NOT IN ('ACTIVE - PARTIALLY_DISBURSED') #Se desestiman las RENO pendiente de desembolso
	and ca.accountstate NOT IN ('APPROVED', 'PARTIAL_APPLICATION', 'PENDING_APPROVAL'
);

ALTER TABLE cartera_reno MODIFY COLUMN `input_dni` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_bin NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `Cuil` VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_bin NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `Reglas_Bloqueo_Agente_Pago` VARCHAR(4096) NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `Ids_Fideicomiso_Prestamo` VARCHAR(4096) NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `Descs_Fideicomiso_Prestamo` VARCHAR(4096) NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `bucket_reno` VARCHAR(255) NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `Fecha_Score_Bhe` VARCHAR(10) NULL;

ALTER TABLE cartera_reno MODIFY COLUMN `Segmento_Tasa` VARCHAR(50) NULL;

CREATE INDEX cartera_reno_input_dni ON cartera_reno(`input_dni`);

CREATE INDEX cartera_reno_id ON cartera_reno(`id`);

CREATE INDEX cartera_reno_cuil ON cartera_reno(`Cuil`);

