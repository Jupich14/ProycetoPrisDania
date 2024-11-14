SCRIPT DE LA BASE DE DATOS POSTGRESQL

-- Base de datos y esquema
create database tiendagalletas 
WITH OWNER = 'postgres' 
ENCODING = 'UTF-8';

\c tiendagalletas
create schema tg;
DROP schema public;
SET search_path TO tg;

-- Definición de dominios
create domain tg.txt as varchar(25) constraint ck_txt check (value ~ '^[A-Za-z ]{1,25}$');

create domain tg.cod as varchar(4) constraint ck_cod check(value~'^[0-9]{4}$');

create domain tg.nc as varchar(4) constraint ck_nc check(value~'^[0-9]{1,4}$');

create domain tg.cant as bigint constraint ck_cant check(value >= 0);

create domain tg.fec as varchar(10) constraint ck_fec check(value ~'^[0-9]{2}-[0-9]{2}-[0-9]{2}$');

create domain tg.curp as varchar(18) constraint ck_curp check(value ~'[A-Z]{4}[0-9]{6}[A-Z]{7}[0-9]{1}$');

create domain tg.cp as varchar(5) constraint ck_cp check(value ~'[0-9]{1,5}$');

create domain tg.contel as integer constraint ck_contel check (value BETWEEN 1 AND 3);

create domain tg.tel as varchar(12) constraint ck_tel check(value ~'[0-9]{3}-[0-9]{3}-[0-9]{4}$');

create domain tg.uni as varchar constraint ck_uni check(value in('3','5','9'));

create domain tg.rs as varchar constraint ck_rs check(value in('contado', 'credito'));

create table tg.cata_emple(
  id_empl tg.cod primary key,
  nom tg.txt not null,
  apellp tg.txt not null,
  apellm tg.txt not null,
  calle tg.txt not null,
  num_int tg.nc,
  num_ext tg.nc,
  curp tg.curp not null,
  cp tg.cp not null
);

create table tg.tel_empl (
  cont_tel tg.contel not null,
  id_empl tg.cod not null,
  tel_emp tg.tel not null,
  primary key (cont_tel, id_empl),
  constraint ck_emple foreign key (id_empl) references tg.cata_emple(id_empl)
  on delete restrict on update restrict
);

create table tg.cat_prod (
  id_prod tg.cod primary key,
  nom tg.txt not null,
  uni tg.uni not null
);

-- Crear las tablas que dependen de las anteriores
create table tg.enc_factu(
  fol_fact tg.cod primary key,
  id_empl tg.cod not null,
  fecha tg.fec not null,
  rs tg.rs not null,
  constraint ck_empl foreign key (id_empl) references tg.cata_emple(id_empl)
  ON DELETE restrict ON UPDATE restrict
);

create table tg.des_fact (
  fol_fact tg.cod not null,
  id_prod tg.cod not null,
  cant tg.cant not null,
  fec_cap tg.fec not null,
  primary key (fol_fact, id_prod),
  constraint ck_folfact foreign key (fol_fact) references tg.enc_factu(fol_fact)
  ON DELETE restrict ON UPDATE restrict,
  constraint ck_idproductos foreign key (id_prod) references tg.cat_prod(id_prod)
  ON DELETE restrict ON UPDATE restrict
);

create table tg.enc_tick(
  fol_tick tg.cod primary key,
  id_empl tg.cod not null,
  fec tg.fec not null,
  rs tg.rs not null,
  constraint ck_empl foreign key (id_empl) references tg.cata_emple(id_empl)
  ON DELETE restrict ON UPDATE restrict
);

create table tg.des_tick (
  fol_tick tg.cod not null,
  id_prod tg.cod not null,
  cant tg.cant not null,
  primary key (fol_tick, id_prod),
  constraint ck_foltick foreign key (fol_tick) references tg.enc_tick(fol_tick)
  ON DELETE restrict ON UPDATE restrict,
  constraint ck_idproductos foreign key (id_prod) references tg.cat_prod(id_prod)
  ON DELETE restrict ON UPDATE restrict
);

-----------------------------------------------------------------
\c postgres
drop database tiendagalletas;

\! cls

-------------------------------------
INSERT INTO tg.cata_emple (id_empl, nom, apellp, apellm, calle, num_int, num_ext, curp, cp)
VALUES 
    ('0001', 'Dania Jazmin', 'Martinez', 'Benitez', 'Plazo sezamo', '3103','1','PELA800101HVZSRNS1', '96535'),
    ('0002', 'Priscila Noemi', 'Mendez', 'Infanzon', 'Plazo sezamo', '1','5482','ERTE800101HVZSRNS2', '96520');

INSERT INTO tg.cat_prod(id_prod, nom, uni)
VALUES 
    ('0001', 'galleta de fresa','5'),
    ('0002', 'galleta de chocolate','5');

INSERT INTO tg.enc_factu (fol_fact, id_empl, fecha, rs)
VALUES 
    ('0001', '0001', '03-01-24', 'contado'),
    ('0002', '0002', '04-01-24', 'credito');

INSERT INTO tg.des_fact (fol_fact,id_prod, cant, fec_cap)
VALUES 
    ('0001', '0001', 20,'04-01-24'),
    ('0002', '0002', 10,'04-01-24');
    
-----------------------trigger---------------------------------
CREATE OR REPLACE FUNCTION tg.verificar_inventario()
RETURNS TRIGGER AS $$
DECLARE
    cantidad_total bigint;
BEGIN
    -- Calcula la cantidad total en inventario del producto afectado
    SELECT 
        COALESCE(SUM(df.cant), 0) + COALESCE(SUM(dt.cant), 0)
    INTO 
        cantidad_total
    FROM 
        tg.cat_prod AS p
    LEFT JOIN 
        tg.des_fact AS df ON p.id_prod = df.id_prod
    LEFT JOIN 
        tg.des_tick AS dt ON p.id_prod = dt.id_prod
    WHERE 
        p.id_prod = NEW.id_prod;

    -- Si la cantidad total es menor a 50, emite una advertencia
    IF cantidad_total < 50 THEN
        RAISE NOTICE 'Advertencia: Inventario bajo para el producto %', NEW.id_prod;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Trigger en des_fact
CREATE TRIGGER trig_verificar_inventario_factura
AFTER INSERT OR UPDATE ON tg.des_fact
FOR EACH ROW
EXECUTE FUNCTION tg.verificar_inventario();

-- Trigger en des_tick
CREATE TRIGGER trig_verificar_inventario_ticket
AFTER INSERT OR UPDATE ON tg.des_tick
FOR EACH ROW
EXECUTE FUNCTION tg.verificar_inventario();

--------------
SELECT 
    p.id_prod AS "ID Producto",
    p.nom AS "Nombre Producto",
    COALESCE(SUM(df.cant), 0) AS "Cantidad en Facturas",
    COALESCE(SUM(dt.cant), 0) AS "Cantidad en Tickets",
    COALESCE(SUM(df.cant), 0) + COALESCE(SUM(dt.cant), 0) AS "Cantidad Total en Inventario"
FROM 
    tg.cat_prod AS p
LEFT JOIN 
    tg.des_fact AS df ON p.id_prod = df.id_prod
LEFT JOIN 
    tg.des_tick AS dt ON p.id_prod = dt.id_prod
GROUP BY 
    p.id_prod, p.nom
ORDER BY 
    p.id_prod;


select * from tg.enc_tick;

select * from tg.des_tick;

truncate tg.enc_tick cascade;