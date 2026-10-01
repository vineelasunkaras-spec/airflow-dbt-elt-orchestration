select
    product_id,
    product_name,
    category,
    cast(list_price as number(12, 2)) as list_price,
    updated_at
from {{ source('raw', 'products') }}
qualify row_number() over (partition by product_id order by updated_at desc) = 1
