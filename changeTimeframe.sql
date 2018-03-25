delimiter //
CREATE PROCEDURE change_timeframe
(
instrument varchar(10),
start date,
end date,
timeframe int
)
BEGIN
	DROP TABLE IF EXISTS hedge_fund.temp;

	SET @t1 = CONCAT("
	CREATE TABLE IF NOT EXISTS hedge_fund.temp AS 
	(
	select 
		*
		,UNIX_TIMESTAMP(datetime) DIV (", timeframe, "*60) tmstp
	from hedge_fund.", instrument," 
	where datetime between '", start, "' and '", end, "'  
	order by datetime
	);");
    
    PREPARE stmt1 FROM @t1;
	EXECUTE stmt1;
	DEALLOCATE PREPARE stmt1;

	DROP TEMPORARY TABLE IF EXISTS o;
	CREATE TEMPORARY TABLE IF NOT EXISTS o AS 
	(
	select 
		datetime
		, open
	from hedge_fund.temp
	where datetime in (select min(datetime) from hedge_fund.temp group by tmstp)
	);

	DROP TEMPORARY TABLE IF EXISTS hl;
	CREATE TEMPORARY TABLE IF NOT EXISTS hl AS 
	(
	select
		min(datetime) datetime
        , max(datetime) datetime_max
		, max(high) high
		, min(low) low
	from hedge_fund.temp
	group by tmstp
	);

	DROP TEMPORARY TABLE IF EXISTS c;
	CREATE TEMPORARY TABLE IF NOT EXISTS c AS 
	(
	select 
		datetime
		, close
	from hedge_fund.temp
	where datetime in (select max(datetime) from hedge_fund.temp group by tmstp)
	);

	select
		a.datetime
		, a.open
		, b.high
		, b.low
		, c.close
	from 
		o  a
	left join
		hl  b
	on a.datetime = b.datetime
	left join
		c 
	on b.datetime_max = c.datetime;

END
//


delimiter ;
