import pandas as pd
import os

# ------------------------------
# Part 1: Load and Validate Data
# ------------------------------

def load_excel(filename, required_columns):
    """Load an Excel file and validate required columns."""
    if not os.path.exists(filename):
        print(f"Error: {filename} is missing.")
        exit()
    df = pd.read_excel(filename)
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        print(f"Error: Missing columns {missing_cols} in {filename}")
        exit()
    return df

# Load SKU and Instock data
skus_df = load_excel('1500Skus.xlsx', ['Group ID', 'Product Name', 'EAN', 'Category', 'Brand', 'Quantity'])
instock_df = load_excel('Instock.xlsx', ['Store Name', 'Barcode', 'In Stock Qty'])

# Get supermarket name
supermarket_name = instock_df['Store Name'].iloc[0] if 'Store Name' in instock_df.columns and not instock_df['Store Name'].isna().all() else 'Supermarket'
output_filename = f"{supermarket_name}_output.xlsx"

# ------------------------------
# Part 2: Clean and Normalize Barcodes
# ------------------------------

def clean_barcode(barcode):
    """Standardize barcode format."""
    barcode = str(barcode).strip().replace('nan', '').replace('NaN', '')
    if barcode.endswith('.0'):
        barcode = barcode[:-2]
    return barcode

# Normalize barcodes
instock_df['Barcode'] = instock_df['Barcode'].apply(clean_barcode)
instock_df['Base Barcode'] = instock_df['Barcode'].apply(lambda x: x.split('-')[0] if x else x)

# Aggregate stock quantity by Base Barcode
base_lookup = instock_df.groupby('Base Barcode', as_index=False)['In Stock Qty'].sum()
base_lookup_dict = dict(zip(base_lookup['Base Barcode'], base_lookup['In Stock Qty']))

# ------------------------------
# Part 3: Match SKUs to Instock Barcodes
# ------------------------------

# Create lookup set for quick matching
instock_barcodes = set(instock_df['Barcode'])

# Process SKU matching
output_rows = []
max_matches = 0
for _, row in skus_df.iterrows():
    group_id = row['Group ID']
    product_name = row['Product Name']
    category = row['Category']
    brand = row['Brand']
    quantity = row['Quantity']
    ean_list = str(row['EAN']).split(';')  # Split multiple barcodes
    ean_list = [clean_barcode(ean) for ean in ean_list]
    
    # Find matching barcodes
    matching_barcodes = [ean for ean in ean_list if ean in instock_barcodes]
    max_matches = max(max_matches, len(matching_barcodes))
    
    output_rows.append({'Group ID': group_id, 'Product Name': product_name, 'Category': category, 'Brand': brand, 'Quantity': quantity, 'Matching Barcodes': matching_barcodes})

# ------------------------------
# Part 4: Build Output DataFrame
# ------------------------------

final_data = []
for row in output_rows:
    data_row = {'Group ID': row['Group ID'], 'Product Name': row['Product Name'], 'Category': row['Category'], 'Brand': row['Brand'], 'Quantity': row['Quantity']}
    for i in range(max_matches):
        col_name = f'Matched Barcode {i+1}'
        data_row[col_name] = row['Matching Barcodes'][i] if i < len(row['Matching Barcodes']) else None
    final_data.append(data_row)

final_df = pd.DataFrame(final_data)

# ------------------------------
# Part 5: Add Quantity Data
# ------------------------------

matched_barcode_cols = [col for col in final_df.columns if col.startswith('Matched Barcode')]
for col in matched_barcode_cols:
    final_df[col] = final_df[col].apply(clean_barcode)
    qty_col = 'Quantity ' + col.split()[-1]
    final_df[qty_col] = final_df[col].apply(lambda x: base_lookup_dict.get(x.split('-')[0] if x else '', 0))

# Compute Total Quantity
quantity_cols = [col for col in final_df.columns if col.startswith('Quantity ')]
final_df['Total Quantity'] = final_df[quantity_cols].sum(axis=1)

# ------------------------------
# Part 6: Identify Procurement Needs
# ------------------------------

# Flag products needing procurement
procure_df = final_df[final_df['Total Quantity'] <= 0].copy()

# Compute summary statistics
total_instock_1500 = (final_df['Total Quantity'] > 0).sum()
need_to_procure = (final_df['Total Quantity'] <= 0).sum()
summary_df = pd.DataFrame({
    'Metric': ['Total In Stock (1500)', 'Need to Procure'],
    'Value': [total_instock_1500, need_to_procure]
})

# ------------------------------
# Part 7: Save Final Output
# ------------------------------

with pd.ExcelWriter(output_filename, engine='xlsxwriter') as writer:
    summary_df.to_excel(writer, sheet_name='Summary', index=False)
    final_df.to_excel(writer, sheet_name='Final Output', index=False)
    procure_df.to_excel(writer, sheet_name='Need to Procure', index=False)

print(f"Final output saved in '{output_filename}' with three sheets (Summary, Final Output, Need to Procure).")
