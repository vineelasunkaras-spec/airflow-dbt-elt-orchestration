select
    order_id,
    line_number,
    {{ dbt_utils.generate_surrogate_key(['order_id', 'line_number']) }} as order_line_id,
    customer_id,
    product_id,
    cast(quantity as integer)            as quantity,
    cast(unit_price as number(12, 2))    as unit_price,
    lower(status)                        as status,
    cast(order_ts as timestamp_ntz)      as order_ts,
    updated_at
from {{ source('raw', 'orders') }}
qualify row_number() over (partition by order_id, line_number order by updated_at desc) = 1
