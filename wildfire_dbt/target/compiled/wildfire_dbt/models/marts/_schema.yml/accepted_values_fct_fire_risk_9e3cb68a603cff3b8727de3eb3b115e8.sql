
    
    

with all_values as (

    select
        fire_risk_level as value_field,
        count(*) as n_records

    from WILDFIRE_DB.ANALYTICS.fct_fire_risk
    group by fire_risk_level

)

select *
from all_values
where value_field not in (
    'Low','Moderate','High','Extreme'
)


