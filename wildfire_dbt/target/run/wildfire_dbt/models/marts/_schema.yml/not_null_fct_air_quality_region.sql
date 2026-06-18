
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select region
from WILDFIRE_DB.ANALYTICS.fct_air_quality
where region is null



  
  
      
    ) dbt_internal_test