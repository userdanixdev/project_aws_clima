
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select load_datetime
from "AwsDataCatalog"."staging"."stg_clima"
where load_datetime is null



  
  
      
    ) dbt_internal_test