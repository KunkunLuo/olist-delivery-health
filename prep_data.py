"""Build the single order-level CSV that the dashboard reads.

The raw Olist archive is 9 files / ~130 MB. The dashboard needs one row per delivered
order with the delivery outcome, the customer's state and the review score, so we
aggregate the 9 tables into one small file and commit that instead.
"""
import pandas as pd, numpy as np

D = 'data/'
orders = pd.read_csv(D + 'olist_orders_dataset.csv')
items  = pd.read_csv(D + 'olist_order_items_dataset.csv')
rev    = pd.read_csv(D + 'olist_order_reviews_dataset.csv')
cust   = pd.read_csv(D + 'olist_customers_dataset.csv')
prod   = pd.read_csv(D + 'olist_products_dataset.csv')
tr     = pd.read_csv(D + 'product_category_name_translation.csv')

for c in ['order_purchase_timestamp', 'order_delivered_customer_date',
          'order_estimated_delivery_date']:
    orders[c] = pd.to_datetime(orders[c], errors='coerce')

# --- delivered orders only: the rest have no outcome to measure ---
d = orders[orders['order_status'] == 'delivered'].copy()
d = d[d['order_delivered_customer_date'].notna()]

d['purchase_date']  = d['order_purchase_timestamp'].dt.date
d['order_month']    = d['order_purchase_timestamp'].dt.to_period('M').astype(str)
d['delivery_days']  = (d['order_delivered_customer_date'] - d['order_purchase_timestamp']).dt.days
d['promised_days']  = (d['order_estimated_delivery_date'] - d['order_purchase_timestamp']).dt.days
d['late']           = d['order_delivered_customer_date'] > d['order_estimated_delivery_date']
d['delay_days']     = ((d['order_delivered_customer_date'] - d['order_estimated_delivery_date'])
                       .dt.days.clip(lower=0))

d = d.merge(cust[['customer_id', 'customer_state', 'customer_city']], on='customer_id', how='left')

# --- one review score per order (a few orders carry more than one review) ---
score = rev.groupby('order_id')['review_score'].mean().rename('review_score')
d = d.merge(score, on='order_id', how='left')

# --- order value and main category ---
it = items.merge(prod[['product_id', 'product_category_name']], on='product_id', how='left')
it = it.merge(tr, on='product_category_name', how='left')
it['category'] = it['product_category_name_english'].fillna(it['product_category_name'])

value = it.groupby('order_id').agg(order_value=('price', 'sum'),
                                  freight_value=('freight_value', 'sum')).reset_index()
main_cat = (it.sort_values('price', ascending=False)
              .drop_duplicates('order_id')[['order_id', 'category']])
d = d.merge(value, on='order_id', how='left').merge(main_cat, on='order_id', how='left')

# --- keep the categories that carry the volume; group the long tail ---
top = it.groupby('category')['order_id'].nunique().sort_values(ascending=False)
keep = set(top.head(12).index)
d['category'] = np.where(d['category'].isin(keep), d['category'], 'other')

out = d[['purchase_date', 'order_month', 'customer_state', 'customer_city', 'category',
         'order_value', 'freight_value', 'delivery_days', 'promised_days',
         'late', 'delay_days', 'review_score']].copy()

out['order_value']   = out['order_value'].round(2)
out['freight_value'] = out['freight_value'].round(2)
out['review_score']  = out['review_score'].round(2)
out = out.sort_values('purchase_date').reset_index(drop=True)

out.to_csv('olist_delivery.csv', index=False)

print('rows:', len(out), '| columns:', out.shape[1])
print('columns:', list(out.columns))
print()
print('order months present:', out['order_month'].nunique(),
      '|', out['order_month'].min(), '->', out['order_month'].max())
print()
print(out.head(5).to_string())
print()
print('on-time rate: %.4f' % (1 - out['late'].mean()))
print('avg delivery days: %.2f' % out['delivery_days'].mean())
print('avg review score: %.3f' % out['review_score'].mean())
print('missing review_score: %d (%.2f%%)'
      % (out['review_score'].isna().sum(), 100 * out['review_score'].isna().mean()))
print('missing category: %d' % out['category'].isna().sum())
print('states:', out['customer_state'].nunique())
import os
print()
print('file size: %.2f MB' % (os.path.getsize('olist_delivery.csv') / 1024 / 1024))
