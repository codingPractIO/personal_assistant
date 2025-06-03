import json
import re

# Load the JSON data from a file
with open("/home/soimimozo/Code/VSCode/reciept_bot/response_vero.json", encoding="utf-8") as f:
    data = json.load(f)

invoice = data["invoiceRequest"]
result = data["invoiceResult"]
journal = data["journal"]


print(f"Business: {invoice['locationName']}")
print(f"Invoice Number: {invoice['taxId']}")
print(f"Total Amount: {result['totalAmount']} RSD")

# Match item lines using regex
matches = re.findall(
    r"\n(.+?)\s+\([EЂ]\)\s*\n\s+([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)",
    journal
)

print("=== Parsed Items ===")
for name, price_str, qty_str, total_str in matches:
    # Convert comma to dot and then to float
    price_str= price_str.replace(".", "")
    qty_str= price_str.replace(".", "") 
    total_str= price_str.replace(".", "")  
    price = float(price_str.replace(",", "."))
    qty = float(qty_str.replace(",", "."))
    total = float(total_str.replace(",", "."))

    print(f"{name.strip()}: {qty:.3f} × {price:.2f} = {total:.2f} RSD")
