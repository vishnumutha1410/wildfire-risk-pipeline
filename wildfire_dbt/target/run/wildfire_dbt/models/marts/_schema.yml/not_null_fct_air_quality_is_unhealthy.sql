
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select is_unhealthy
from WILDFIRE_DB.ANALYTICS.fct_air_quality
where is_unhealthy is null



  
  
      
    ) dbt_internal_test