
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select data
from "AwsDataCatalog"."staging"."stg_clima"
where data is null



  
  
      
    ) dbt_internal_test