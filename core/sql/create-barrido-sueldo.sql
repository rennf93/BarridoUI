CREATE DATABASE IF NOT EXISTS {0};

USE {0};

CREATE TABLE IF NOT EXISTS client_salary(
dni varchar(20),
sueldo bigint,
PRIMARY KEY (`dni`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

TRUNCATE table {0}.client_salary;

LOAD DATA local infile '/shared_data/sueldos-barrido.csv' into table {0}.client_salary FIELDS TERMINATED BY ';' LINES TERMINATED BY '\n' IGNORE 1 ROWS (dni, @sueldos) SET sueldo=CAST(REPLACE(REPLACE(@sueldos, '.', ''), ',', '.') as DECIMAL(9,2));

UPDATE wenance.cartera_activa ca JOIN {0}.client_salary s ON s.dni = ca.dni SET ca.sueldo = s.sueldo;
