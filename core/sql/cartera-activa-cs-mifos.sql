SELECT  'externalId'
		,'loanId'
		,'Product'
		,'Estado'
		,'Id_Credito_Mambu'
		,'Nombre_Apellido'
		,'DNI'
        ,'CBU'
		,'DiasMora'
		,'Situacion_CS'
		,'Bucket'
		,'Fecha_Activacion'
		,'Monto_CS'
		,'Plazo'
		,'Cant_Cuotas_Pagas'
		,'Cant_Cuotas_Impagas'
		,'ValorCuota'
		,'FecUltCuotaImp'
		,'ProxVto'
		,'Fecha_1Vto'
		,'Fecha_Ult_Pago'
		,'MoraCuota'
		,'totalDue'
		,'Total_a_barrer'
		,'Total_Pagado'
UNION ALL (
SELECT  `externalId`
		,`loanId`
		,`Product`
		,`Estado`
		,`Id_Credito_Mambu`
		,`Nombre_Apellido`
		,`DNI`
        ,`CBU`
		,`DiasMora`
		,`Situacion_CS`
		,`Bucket`
		,`Fecha_Activacion`
		,replace(round(`Monto_CS`,2),",",".") 		AS 'Monto_CS'
		,`Plazo`
		,`Cant_Cuotas_Pagas`
		,`Cant_Cuotas_Impagas`
		,replace(round(`ValorCuota`,2),",",".") 	AS 'ValorCuota'
		,`FecUltCuotaImp`
		,`ProxVto`
		,`Fecha_1Vto`
		,`Fecha_Ult_Pago`
		,replace(round(`MoraCuota`,2),",",".") 		AS 'MoraCuota'
		,replace(round(`sum_totalDue`,2),",",".") 	AS 'totalDue'
		,replace(round(`Total_a_barrer`,2),",",".") AS 'Total_a_barrer'
		,replace(round(`Total_Pagado`,2),",",".") 	AS 'Total_Pagado'
from
	(select mc.external_id 							AS 'externalId',
		cast(ml.account_no as unsigned) 			AS 'loanId',
		pl.name 									AS 'Product',
		ml.client_id 								AS 'client_id',

		case
			when ml.loan_status_id = 0 		THEN 'INVALIDO'
			when ml.loan_status_id = 100	THEN 'ESPERANDO APROBACION'
			when ml.loan_status_id = 200	THEN 'APROBADO'
			when ml.loan_status_id = 300	THEN 'ACTIVO'
			when ml.loan_status_id = 400	THEN 'RETIRADO POR EL CLIENTE'
			when ml.loan_status_id = 500	THEN 'RECHAZADO'
			when ml.loan_status_id = 601	THEN 'ENVIADO A PERDIDA'
			when ml.loan_status_id = 600	THEN 'CERRADO'
			when ml.loan_status_id = 602	THEN 'REFINANCIADO / RENOVADO'
			when ml.loan_status_id = 700	THEN 'SOBREPAGADO'
			ELSE 'N/A'
		END AS 'Estado',

		substr(ml.external_id,LOCATE('-',ml.external_id)+1,6) AS 'ID_CREDITO_MAMBU',
        mc.display_name 							AS "Nombre_Apellido",

		ifnull((select document_key
				from m_client_identifier ci
				where UPPER(description) = 'DOCUMENTO DE IDENTIDAD'
				and ci.client_id = mc.account_no),'') AS 'DNI',

        ifnull((select document_key
				from m_client_identifier ci
				where UPPER(description) = 'CBU'
				and ci.client_id = mc.account_no),'') AS 'CBU',

		repayment.diasmora_2 						AS 'diasMora',
		repayment.estado 							AS 'Situacion_CS',

		CASE
			WHEN repayment.estado = 'VIGENTE'  THEN
				CASE
					WHEN DATE_FORMAT(repayment.ProxVto_CS, '%y%m%d') = DATE_FORMAT(repayment.Fecha_1Vto, '%y%m%d') THEN '(1) Nuevos'
					WHEN DATE_FORMAT(repayment.ProxVto_CS, '%y%m%d') > DATE_FORMAT(repayment.Fecha_1Vto, '%y%m%d') THEN '(2) Vigentes'
					ELSE ''
				END
			ELSE
			CASE
				WHEN repayment.diasmora_2 <= 30 	THEN '(3) Mora 1 a 30'
				WHEN repayment.diasmora_2 <= 60 	THEN '(4) Mora 31 a 60'
				WHEN repayment.diasmora_2 <= 90 	THEN '(5) Mora 61 a 90'
				WHEN repayment.diasmora_2 <= 120 	THEN '(6) Mora 91 a 120'
				WHEN repayment.diasmora_2 <= 180 	THEN '(7) Mora 121 a 180'
				WHEN repayment.diasmora_2 <= 360 	THEN '(8) Mora 181 a 360'
				WHEN repayment.diasmora_2 <= 720 	THEN '(9) Mora 361 a 720'
			   ELSE '(10) Mora>720'
			END
		END AS 'Bucket',

		ml.disbursedon_date 						AS 'Fecha_Activacion',
		round(ml.principal_amount,2) 				AS 'Monto_CS',
		ml.term_frequency 							AS 'Plazo',
		repayment.Cant_Cuotas_Pagas 				AS 'Cant_Cuotas_Pagas',
		repayment.Cant_Cuotas_Impagas  				AS 'Cant_Cuotas_Impagas',
		repayment.FecUltCuotaImp 					AS 'FecUltCuotaImp',
		repayment.ProxVto_CS 						AS 'ProxVto',
		repayment.Fecha_1Vto 						AS 'Fecha_1Vto',
		repayment.fecha_ult_pago 					AS 'Fecha_Ult_Pago',

		@valor_cuota := repayment.ValorCuota2 		AS 'ValorCuota',
		@mora_cuota := round(repayment.Mora,2) 		AS 'MoraCuota',

		round(repayment.totalDue_total_a_barrer,2) 	AS 'Total_a_barrer',
		repayment_group.sum_totalDue 				AS 'sum_totalDue',
		round(cast(ml.total_repayment_derived as unsigned),2) AS 'Total_Pagado'


	FROM m_loan ml
	join m_client mc				ON mc.account_no = ml.client_id
	jOIN r_enum_value rev 			ON rev.enum_id = ml.loan_status_id AND rev.enum_name = 'loan_status_id'
	JOIN m_product_loan pl 			ON pl.id = ml.product_id
    join (
				SELECT 	ml2.client_id,
				rs.loan_id,
				rs.fromdate,
				rs.duedate,
				rs.installment,
				ifnull(rs.principal_amount,0) 				AS 'principal_amount',
				ifnull(rs.principal_completed_derived,0) 	AS 'principal_completed_derived',
				rs.completed_derived,
				min(rs.duedate) 							AS 'Fecha_1Vto',

				@proxVto := ifnull(	(select min(a.duedate)
						FROM m_loan_repayment_schedule as a
						where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
						and a.loan_id = rs.loan_id
						group by a.loan_id), max(rs.duedate)) AS 'ProxVto_CS',


				ifnull(	(select min(a.duedate)
						FROM m_loan_repayment_schedule as a
						where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
						and a.loan_id = rs.loan_id
						and a.completed_derived = 0
						group by a.loan_id),'') 			AS 'FecUltCuotaImp',

				@mora := ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
					   from m_loan_repayment_schedule b
					   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
					   and b.loan_id = rs.loan_id
					   group by b.loan_id),0) 				AS 'Mora',

				ifnull((select date_format(s3.lastmodified_date, '%Y-%m-%d')
						from m_loan_repayment_schedule s3
						where s3.loan_id = rs.loan_id
						and s3.lastmodified_date = (select max(s4.lastmodified_date) from m_loan_repayment_schedule s4
															where s4.loan_id = s3.loan_id)
						and s3.lastmodified_date <> s3.created_date
						and s3.loan_id = rs.loan_id
						group by s3.loan_id),'') 			AS 'fecha_ult_pago',

				(select count(completed_derived)
				from m_loan_repayment_schedule s1
				where completed_derived=0
				and s1.loan_id = rs.loan_id) 				AS 'Cant_Cuotas_Impagas',

				(select count(completed_derived)
				from m_loan_repayment_schedule s1
				where completed_derived=1
				and s1.loan_id = rs.loan_id) 				AS 'Cant_Cuotas_Pagas',

				@valor_cuota := round((select rs3.principal_amount
										from m_loan_repayment_schedule rs3
										where rs3.installment=1
										and rs3.loan_id = rs.loan_id),2) 	AS 'ValorCuota2',

				@diasmora := ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
										from m_loan_arrears_aging laa
										where laa.loan_id = rs.loan_id),0) 	AS 'diasmora_2',



				case
					when @diasmora = 0 then 'VIGENTE'
					else 'MORA'
				end as 'estado',

				round(case
							WHEN
									ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
									from m_loan_arrears_aging laa
									where laa.loan_id = rs.loan_id),0) = 0
								AND
									datediff(date_format(ifnull((select min(a.duedate)
																FROM m_loan_repayment_schedule as a
																where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
																and a.loan_id = rs.loan_id
																group by a.loan_id), max(rs.duedate)),'%y%m%d'),
												date_format(curdate(),'%y%m%d')) between 0 and 20
								THEN
									round((select rs3.principal_amount
											from m_loan_repayment_schedule rs3
											where rs3.installment=1
											and rs3.loan_id = rs.loan_id),2)



							WHEN
									ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
									from m_loan_arrears_aging laa
									where laa.loan_id = rs.loan_id),0) >0
								AND
									datediff(date_format(ifnull((select min(a.duedate)
																FROM m_loan_repayment_schedule as a
																where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
																and a.loan_id = rs.loan_id
																group by a.loan_id), max(rs.duedate)),'%y%m%d'),
												date_format(curdate(),'%y%m%d')) between 0 and 20
								THEN
									round((select rs3.principal_amount
											from m_loan_repayment_schedule rs3
											where rs3.installment=1
											and rs3.loan_id = rs.loan_id),2)
									+

									ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
										   from m_loan_repayment_schedule b
										   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
										   and b.loan_id = rs.loan_id
										   group by b.loan_id),0)



                            WHEN
									ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
									from m_loan_arrears_aging laa
									where laa.loan_id = rs.loan_id),0) >0
								AND
									datediff(date_format(ifnull((select min(a.duedate)
																FROM m_loan_repayment_schedule as a
																where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
																and a.loan_id = rs.loan_id
																group by a.loan_id), max(rs.duedate)),'%y%m%d'),
												date_format(curdate(),'%y%m%d')) < 0
								THEN

									ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
										   from m_loan_repayment_schedule b
										   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
										   and b.loan_id = rs.loan_id
										   group by b.loan_id),0)


							ELSE
								ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
									   from m_loan_repayment_schedule b
									   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
									   and b.loan_id = rs.loan_id
									   group by b.loan_id),0)
					end,2) as 'totalDue_total_a_barrer'


				FROM m_loan_repayment_schedule rs
				join m_loan ml2		on rs.loan_id = ml2.account_no
                where ml2.loan_status_id = 300

				group by rs.loan_id
		) AS  repayment 					ON repayment.loan_id = ml.account_no


   JOIN
    (
        select 	repayment_group_pre.client_id,
				SUM(repayment_group_pre.sum_totalDue_p) AS 'sum_totalDue'

        from
        (
				SELECT 	ml3.client_id,
						rs3.loan_id,

						@proxVto3 := ifnull((select min(a.duedate)
								FROM m_loan_repayment_schedule as a
								where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a.duedate, '%y%m%d')
								and a.loan_id = rs3.loan_id
								group by a.loan_id), max(rs3.duedate)),


					ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
							   from m_loan_repayment_schedule b
							   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
							   and b.loan_id = rs3.loan_id
							   group by b.loan_id),0),


					round((select c.principal_amount
												from m_loan_repayment_schedule c
												where c.installment=1
												and c.loan_id = rs3.loan_id),2) ,

						@diasmora3 := ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
												from m_loan_arrears_aging laa
												where laa.loan_id = rs3.loan_id),0) ,


                        case
							when @diasmora3 = 0 then 'VIGENTE'
							else 'MORA'
						end as 'estado3',


						round(case
												WHEN
													ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
															from m_loan_arrears_aging laa
															where laa.loan_id = rs3.loan_id),0) = 0
													AND
														datediff(date_format(ifnull((select min(a1.duedate)
																					FROM m_loan_repayment_schedule as a1
																					where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a1.duedate, '%y%m%d')
																					and a1.loan_id = rs3.loan_id
																					group by a1.loan_id), max(rs3.duedate)),'%y%m%d'),
																		date_format(curdate(),'%y%m%d')) between 0 and 20
													THEN
														round((select c.principal_amount
																from m_loan_repayment_schedule c
																where c.installment=1
																and c.loan_id = rs3.loan_id),2)


												WHEN
													ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
															from m_loan_arrears_aging laa
															where laa.loan_id = rs3.loan_id),0) > 0
                                                AND datediff(date_format(ifnull((select min(a2.duedate)
																				FROM m_loan_repayment_schedule as a2
																				where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a2.duedate, '%y%m%d')
																				and a2.loan_id = rs3.loan_id
																				group by a2.loan_id), max(rs3.duedate)),'%y%m%d'),
																	date_format(curdate(),'%y%m%d')) between 0 and 20
												THEN
													round((select c.principal_amount
															from m_loan_repayment_schedule c
															where c.installment=1
															and c.loan_id = rs3.loan_id),2)
													+

													ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
														   from m_loan_repayment_schedule b
														   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
														   and b.loan_id = rs3.loan_id
														   group by b.loan_id),0)


                                                WHEN
													ifnull((select  datediff(curdate(),laa.overdue_since_date_derived)
															from m_loan_arrears_aging laa
															where laa.loan_id = rs3.loan_id),0) > 0
                                                AND datediff(date_format(ifnull((select min(a2.duedate)
																				FROM m_loan_repayment_schedule as a2
																				where DATE_FORMAT(CURDATE(), '%y%m%d') <= DATE_FORMAT(a2.duedate, '%y%m%d')
																				and a2.loan_id = rs3.loan_id
																				group by a2.loan_id), max(rs3.duedate)),'%y%m%d'),
																	date_format(curdate(),'%y%m%d')) < 0
												THEN

													ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
														   from m_loan_repayment_schedule b
														   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
														   and b.loan_id = rs3.loan_id
														   group by b.loan_id),0)



												ELSE
													ifnull((select sum(b.principal_amount) - ifnull(sum(b.principal_completed_derived),0)
														   from m_loan_repayment_schedule b
														   where DATE_FORMAT(b.duedate, '%y%m%d') <= DATE_FORMAT(CURDATE(), '%y%m%d')
														   and b.loan_id = rs3.loan_id
														   group by b.loan_id),0)

										end,2) as 'sum_totalDue_p'


						FROM m_loan_repayment_schedule rs3
						join m_loan ml3		on rs3.loan_id = ml3.account_no

                        where ml3.loan_status_id = 300
						group by rs3.loan_id
					) repayment_group_pre
		group by 1
	)  repayment_group		ON ml.client_id = repayment_group.client_id

	WHERE ml.loan_status_id =300
	GROUP BY ml.account_no

) as ca
order by ca.client_id asc
)