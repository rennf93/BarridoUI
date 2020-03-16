UPDATE {2} AS ca
JOIN `{0}`.cartera_activa_inicial cai
    ON cai.Id=ca.Id
SET ca.`Monto_cobranza_inicial` = CEIL(cai.SaldoDeCapitalAdeudado)
    , ca.`Dias_atraso_inicial` = cai.DiasAtraso
    , ca.`Estado_inicial` = cai.Estado
    , ca.`Fecha_cartera_inicial` = cai.Fecha_cartera
    , ca.`K_mas_I_inicial` = cai.K_mas_I;

UPDATE {2} ca
JOIN {1}.`core_collectioncycle` cc
    ON cc.`end_date` = ca.`Fecha_cartera_inicial`
SET ca.`Con_cobro_2da_quincena` = CASE
    WHEN DATE_FORMAT(ca.FecUltCuotaPagaMesAnt, '%y%m%d') >= DATE_FORMAT(cc.`middle_date`, '%y%m%d')
        THEN 'Si'
    ELSE 'No' END
WHERE ca.FecUltCuotaPagaMesAnt IS NOT NULL AND CHAR_LENGTH(ca.FecUltCuotaPagaMesAnt) > 0;

UPDATE {2} AS ca
    JOIN `{0}`.client_blocked_account cba ON cba.client_id = ca.DNI
SET ca.PayingAgentBlockedRules = cba.blocked_accounts;

UPDATE {2} AS ca
JOIN `{0}`.`loan_client_data` lcd
    ON lcd.id_credito = ca.Id
SET ca.email = ifnull(lcd.email, ca.email),
	ca.celular = ifnull(lcd.celular, ca.celular),
	ca.ScorePrestamo = ifnull(lcd.score, 0),
	ca.ImporteCobradoMesActualDebitoDirecto = lcd.importeCobradoMesActual,
	ca.MaxFechaRendicion = lcd.maxFechaRendicion,
	ca.MaxFechaCobro = lcd.maxFechaCobro
WHERE lcd.id_pais = 1;