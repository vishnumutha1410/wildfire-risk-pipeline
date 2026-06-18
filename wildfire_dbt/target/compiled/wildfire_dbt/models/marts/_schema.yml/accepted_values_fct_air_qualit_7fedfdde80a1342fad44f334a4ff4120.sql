
    
    

with all_values as (

    select
        air_quality_category as value_field,
        count(*) as n_records

    from WILDFIRE_DB.ANALYTICS.fct_air_quality
    group by air_quality_category

)

select *
from all_values
where value_field not in (
    'Good','Moderate','Unhealthy for Sensitive Groups','Unhealthy','Very Unhealthy','Hazardous'
)


