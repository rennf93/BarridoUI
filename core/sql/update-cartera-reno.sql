update cartera_reno cr
inner join `{0}`.bcra_deudores_cendeu bc on (cr.Cuil = bc.nro_identificacion)
set cr.Max_Score_BCRA = bc.max_situacion_bcra;

UPDATE cartera_reno cr
    JOIN `{0}`.client_blocked_account cba ON cba.client_id = cr.input_dni
SET cr.Reglas_Bloqueo_Agente_Pago = cba.blocked_accounts;

update cartera_reno cr
inner join `{0}`.ft_behavior_cartera_activa bca on (cr.Cuil = bca.client_id and bca.country_id = 1)
set cr.Score_Bhe = bca.score_beh,
	  cr.Fecha_Score_Bhe = convert(convert(process_date, DATE), CHAR(10));

UPDATE cartera_reno cr
INNER JOIN cartera_reno cr2 on (cr.Cuil = cr2.Cuil)
SET cr.Tiene_Producto_Vigente = 1
WHERE cr2.Es_Producto_Vigente = 1;

update cartera_reno cr
inner join (
  select id_credito, GROUP_CONCAT(id_fideicomiso) as 'Ids_Fideicomiso_Prestamo', GROUP_CONCAT("'", descripcion, "'") as 'Descs_Fideicomiso_Prestamo'
  from `{0}`.ft_fideicomiso_detalle
  where pais_ik = 1
  GROUP BY id_credito) fd on (cr.Id = fd.id_credito)
set cr.Ids_Fideicomiso_Prestamo = fd.Ids_Fideicomiso_Prestamo,
    cr.Descs_Fideicomiso_Prestamo = fd.Descs_Fideicomiso_Prestamo;

update  cartera_reno set input_last_lost_opportunity_date = null;

update cartera_reno cr
inner join (select dni, opportunity_date from `{0}`.reno_lost_opportunity ) ro
on ro.dni = cr.input_dni
set cr.input_last_lost_opportunity_date = ro.opportunity_date;


update cartera_reno cr
inner join (select calendar_date, collection_cycle, collection_cycle_business_day_ordinal from `{0}`.business_dates ) cd
on cd.calendar_date = cr.input_first_remaining_installment_date
set cr.input_remaining_payment_cycle_business_day_ord = case when cd.calendar_date is null then 0 else cd.collection_cycle_business_day_ordinal end
where cd.collection_cycle = (select collection_cycle from `{0}`.business_dates where calendar_date = CURDATE())
and cd.collection_cycle_business_day_ordinal <= 15
and cr.input_first_remaining_installment_date is not null;