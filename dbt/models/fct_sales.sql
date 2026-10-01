{{ config(materialized='incremental', unique_key='order_line_id', on_schema_change='append_new_columns') }}

select
    o.order_line_id,
    o.order_id,
    c.customer_key,
    p.product_key,
    to_number(to_char(o.order_ts, 'YYYYMMDD')) as date_key,
    o.quantity,
    o.unit_price,
    o.quantity * o.unit_price                    as gross_amount,
    o.status,
    o.order_ts,
    o.updated_at
from {{ ref('stg_orders') }} o
left join {{ ref('dim_customer') }} c on o.customer_id = c.customer_id
left join {{ ref('dim_product') }}  p on o.product_id  = p.product_id
{% if is_incremental() %}
where o.updated_at > (select coalesce(max(updated_at), '1900-01-01') from {{ this }})
{% endif %}
