
  create or replace   view WILDFIRE_DB.ANALYTICS.stg_air_weather
  
  
  
  
  as (
    with source as (

    select * from WILDFIRE_DB.RAW.air_weather_raw

)

select
    region,
    latitude,
    longitude,
    collected_at,
    cast(temperature_c   as float) as temperature_c,
    cast(humidity_pct    as float) as humidity_pct,
    cast(wind_speed_kmh  as float) as wind_speed_kmh,
    cast(pm2_5           as float) as pm2_5,
    cast(pm10            as float) as pm10
from source
where temperature_c is not null
  and pm2_5 is not null
  );

