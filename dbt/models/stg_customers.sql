select
    customer_id,
    initcap(trim(first_name)) || ' ' || initcap(trim(last_name)) as customer_name,
    sha2(lower(trim(email)), 256)                                as email_hash,
    upper(state)                                                 as state,
    created_at,
    updated_at
from {{ source('raw', 'customers') }}
qualify row_number() over (partition by customer_id order by updated_at desc) = 1
