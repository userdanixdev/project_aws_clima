
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select id_cidade
from "AwsDataCatalog"."staging"."stg_clima"
where id_cidade is null



  
  
      
    ) dbt_internal_test