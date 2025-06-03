import json
import re
import os

class ReceiptParser:
    def __init__(self, json_path):
        self.json_path = json_path
        self.journal = ""
        self.lines = []
        self.items = []
        self.voucher_value = None
        self.pfr_date = None
        self.pfr_time = None
        self.tax_id = None
        self.location_name = None
        self.total_amount = None
        self.voucher_data = []
        self.output_matrix = {}

        self._load_data()
        self._parse_journal()

    def _load_data(self):
        with open(self.json_path, encoding="utf-8") as f:
            data = json.load(f)

            self.journal = data.get("journal", "")
            self.lines = self.journal.splitlines()

            invoice = data.get("invoiceRequest", {})
            result = data.get("invoiceResult", {})

            self.tax_id = invoice.get("taxId")
            self.location_name = invoice.get("locationName")
            self.total_amount = result.get("totalAmount")

    def _parse_euro_number(self, s):
        return float(s.replace('.', '').replace(',', '.'))

    def _parse_journal(self):
        self._extract_voucher_and_pfr_time()
        self._extract_items()

    def _extract_voucher_and_pfr_time(self):
        for line in self.lines:
            line = line.strip()

            voucher_match = re.search(r"Ваучер:\s*([\d.,]+)", line)
            if voucher_match:
                self.voucher_value = self._parse_euro_number(voucher_match.group(1))

            pfr_match = re.search(r"ПФР време:\s*(\d{2}\.\d{2}\.\d{4})\.?\s+(\d{2}:\d{2}:\d{2})", line)
            if pfr_match:
                self.pfr_date, self.pfr_time = pfr_match.groups()

    def _extract_items(self):
        parsing_items = False
        buffer = []
        items = []

        for line in self.lines:
            line = line.strip()

            if not parsing_items:
                if "Укупно" in line:
                    parsing_items = True
                continue

            if re.match(r"-{30,}", line):
                break

            number_match = re.match(r"^([\d.,]+)\s+([\d.,]+)\s+([\d.,]+)$", line)
            if number_match:
                price_str, qty_str, total_str = number_match.groups()
                name = " ".join(buffer).strip()
                buffer.clear()

                if name:
                    item_list = [
                        name,
                        self._parse_euro_number(price_str),
                        self._parse_euro_number(qty_str),
                        self._parse_euro_number(total_str)
                    ]
                    items.append(item_list)
            else:
                buffer.append(line)
        
        self.items = items
        self._construct_output_matrix()
        

    def _construct_output_matrix(self):
        print(f"Constructing output matrix for tax_id: {self.tax_id}, pfr_date: {self.pfr_date}")
        for item in self.items:
            item.append(self.tax_id)
            item.append(self.location_name)
            item.append(self.pfr_date)
            item.append(self.pfr_time)

        self.voucher_data = [
            self.tax_id,
            self.location_name,
            self.pfr_date,
            self.pfr_time,
            self.total_amount,
            self.voucher_value
        ]

        self.output_matrix = {
            "items": self.items,
            "voucher_data": self.voucher_data
        }

        self._export_output_matrix_to_json()
    
    def _export_output_matrix_to_json(self):
        print(f"Exporting data to JSON file for tax_id: {self.tax_id}, pfr_date: {self.pfr_date}")
        """
        Exports the output_matrix dictionary to a JSON file in the 'output' subfolder.
        The filename is constructed from self.tax_id and self.pfr_date.
        If the file exists, it will be overwritten.
        """
        output_dir = os.path.join(os.path.dirname(__file__), "parsed_data")
        os.makedirs(output_dir, exist_ok=True)
        # Sanitize values for filename
        tax_id = str(self.tax_id) if self.tax_id else "unknown"
        pfr_date = str(self.pfr_date).replace('.', '-') if self.pfr_date else "unknown"
        filename = f"{tax_id}_{pfr_date}.json"
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.output_matrix, f, ensure_ascii=False, indent=4)



    def get_summary(self):
        return (
            self.tax_id,
            self.location_name,
            self.pfr_date,
            self.pfr_time,
            self.total_amount,
            self.voucher_value
        )

    def get_items(self):
        return self.items

