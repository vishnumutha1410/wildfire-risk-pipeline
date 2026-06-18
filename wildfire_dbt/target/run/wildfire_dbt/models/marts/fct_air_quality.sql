
  
    

create or replace transient table WILDFIRE_DB.ANALYTICS.fct_air_quality
    
    
    
    as (with staged as (

    select * from WILDFIRE_DB.ANALYTICS.stg_air_weather

)

select
    region,
    collected_at,
    pm2_5,
    pm10,
    case
        when pm2_5 <= 12   then 'Good'
        when pm2_5 <= 35   then 'Moderate'
        when pm2_5 <= 55   then 'Unhealthy for Sensitive Groups'
        when pm2_5 <= 150  then 'Unhealthy'
        when pm2_5 <= 250  then 'Very Unhealthy'
        else 'Hazardous'
    end as air_quality_category,
    case when pm2_5 > 35 then true else false end as is_unhealthy
from staged
    )
;


  