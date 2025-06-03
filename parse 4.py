import json
import re

def parse_euro_number(s):
    return float(s.replace('.', '').replace(',', '.'))

# Load JSON from file
with open("/home/soimimozo/Code/VSCode/reciept_bot/response_vero.json", encoding="utf-8") as f:
    data = json.load(f)

invoice = data["invoiceRequest"]
result = data["invoiceResult"]
journal = data["journal"]
lines = journal.splitlines()


print(f"Business: {invoice['locationName']}")
print(f"Invoice Number: {invoice['taxId']}")
print(f"Total Amount: {result['totalAmount']}")

# ----------------------------
# First pass: extract voucher and PFR time
# ----------------------------

voucher_value = None
pfr_date = None
pfr_time = None

for line in lines:
    line = line.strip()

    # Match Ваучер
    voucher_match = re.search(r"Ваучер:\s*([\d.,]+)", line)
    if voucher_match:
        voucher_value = parse_euro_number(voucher_match.group(1))

    # Match ПФР време
    pfr_match = re.search(r"ПФР време:\s*(\d{2}\.\d{2}\.\d{4})\.?\s+(\d{2}:\d{2}:\d{2})", line)
    if pfr_match:
        pfr_date, pfr_time = pfr_match.groups()


# ----------------------------
# Second pass: extract product items
# ----------------------------

items = []
buffer = []
parsing_items = False

for line in lines:
    line = line.strip()

    if not parsing_items:
        if "Укупно" in line:
            parsing_items = True
        continue

    # Stop at divider
    if re.match(r"-{30,}", line):
        break

    # Match number line
    number_match = re.match(r"^([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)$", line)
    if number_match:
        price_str, qty_str, total_str = number_match.groups()
        name = " ".join(buffer).strip()
        buffer.clear()

        if name:
            items.append({
                "name": name,
                "price": parse_euro_number(price_str),
                "quantity": parse_euro_number(qty_str),
                "total": parse_euro_number(total_str)
            })
    else:
        buffer.append(line)

# ----------------------------
# Output
# ----------------------------

print("=== Parsed Items ===")
for item in items:
    print(f"{item['name']}: {item['quantity']:.3f} × {item['price']:.2f} = {item['total']:.2f} RSD")

print("\n=== Additional Info ===")
if voucher_value is not None:
    print(f"Ваучер: {voucher_value:.2f} RSD")
if pfr_date and pfr_time:
    print(f"ПФР време: {pfr_date} at {pfr_time}")
