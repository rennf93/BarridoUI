select 'Id'
,'Estado'
,'Estado_Mambu'
,'Cliente_en_Gest_Especial'
,'Sucursal_Prestamo'
,'Centro_Prestamo'
,'AyN'
,'DNI'
UNION ALL
SELECT `Id`
,`Estado`
,`Estado_Mambu`
,`Cliente_en_Gest_Especial`
,`Sucursal_Prestamo`
,`Centro_Prestamo`
,`AyN`
,ca.`DNI`
FROM cartera_activa_inicial ca
WHERE ca.Estado_Mambu NOT IN ('ACTIVE - LOCKED', 'ACTIVE - PARTIALLY_DISBURSED');