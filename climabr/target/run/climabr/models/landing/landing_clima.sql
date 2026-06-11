create or replace view
    "AwsDataCatalog"."landing"."landing_clima"
  as
    
select
    location,
    location_requested,
    location_resolved,
    extraction_timestamp,
    payload_json,
    source,
    date
from "AwsDataCatalog"."landing"."clima"
