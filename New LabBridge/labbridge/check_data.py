from mcp_server import list_table_data
import logging

logging.basicConfig(level=logging.INFO)

print("--- Listando Planos ---")
# limit=5
print(list_table_data("plans", 5))
print("--- Listando Tenants ---")
print(list_table_data("tenants", 5))
