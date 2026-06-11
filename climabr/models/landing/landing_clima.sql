{{ config(materialized='view') }}
select
    location,
    location_requested,
    location_resolved,
    extraction_timestamp,
    payload_json,
    source,
    date
from {{ source('landing', 'clima') }}