
  
    

create or replace transient table WILDFIRE_DB.ANALYTICS.fct_fire_risk
    
    
    
    as (with staged as (

    select * from WILDFIRE_DB.ANALYTICS.stg_air_weather

),

scored as (

    select
        region,
        collected_at,
        temperature_c,
        humidity_pct,
        wind_speed_kmh,
        pm2_5,
        least(temperature_c / 45.0, 1) * 40            as heat_points,
        (1 - (humidity_pct / 100.0)) * 35              as dryness_points,
        least(wind_speed_kmh / 40.0, 1) * 25           as wind_points
    from staged

)

select
    region,
    collected_at,
    temperature_c,
    humidity_pct,
    wind_speed_kmh,
    pm2_5,
    round(heat_points + dryness_points + wind_points, 1) as fire_risk_score,
    case
        when heat_points + dryness_points + wind_points >= 75 then 'Extreme'
        when heat_points + dryness_points + wind_points >= 55 then 'High'
        when heat_points + dryness_points + wind_points >= 35 then 'Moderate'
        else 'Low'
    end as fire_risk_level
from scored
    )
;


  