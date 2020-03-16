UPDATE {0}.{1} ca
  JOIN {0}.{2} cs
ON cs.dni = ca.dni
SET ca.sueldo = cs.sueldos;