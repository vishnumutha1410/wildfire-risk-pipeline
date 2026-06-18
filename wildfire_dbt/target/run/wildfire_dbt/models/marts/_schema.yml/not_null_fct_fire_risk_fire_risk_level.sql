
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select fire_risk_level
from WILDFIRE_DB.ANALYTICS.fct_fire_risk
where fire_risk_level is null



  
  
      
    ) dbt_internal_test