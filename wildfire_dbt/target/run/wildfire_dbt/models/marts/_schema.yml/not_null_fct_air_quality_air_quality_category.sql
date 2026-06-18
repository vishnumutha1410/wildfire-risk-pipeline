
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select air_quality_category
from WILDFIRE_DB.ANALYTICS.fct_air_quality
where air_quality_category is null



  
  
      
    ) dbt_internal_test