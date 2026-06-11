
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select fase_lua
from "AwsDataCatalog"."staging"."stg_clima"
where fase_lua is null



  
  
      
    ) dbt_internal_test