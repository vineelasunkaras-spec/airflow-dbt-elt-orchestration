select
    {{ dbt_utils.generate_surrogate_key(['customer_id']) }} as customer_key,
    customer_id,
    customer_name,
    email_hash,
    state,
    created_at as customer_since
from {{ ref('stg_customers') }}
