"""Parse and extract receipt data from JSON files."""

import json
import logging
import os
import re
from typing import Any

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

class ReceiptParser:
    def __init__(self, json_file: str | dict[str, Any]) -> None:
        """Load a raw receipt JSON file for parsing."""
        if isinstance(json_file, str):
            with open(json_file, "r", encoding="utf-8") as f:
                self.json_file = json.load(f)
        else:
            self.json_file = json_file
        self.journal = ""
        self.lines = []
        self.items = []
        self.voucher_value = None
        self.pfr_date = None
        self.pfr_time = None
        self.tax_id = None
        self.location_name = None
        self.total_amount = None
        self.invoice_number = None
        self.voucher_data = []
        self.output_matrix = {}

        self._load_data()
        self.is_tax_id_new = self._check_if_tax_id_new()
        if self.is_tax_id_new:
            self._parse_journal()
            self._archive_tax_id()

    def _load_data(self):

        self.journal = self.json_file.get("journal", "")
        self.lines = self.journal.splitlines()

        invoice = self.json_file.get("invoiceRequest", {})
        result = self.json_file.get("invoiceResult", {})

        self.tax_id = invoice.get("taxId")
        self.location_name = invoice.get("locationName")
        self.total_amount = result.get("totalAmount")
        self.invoice_number = result.get("invoiceNumber")

    def _archive_tax_id(self):
        """
        Appends the current tax_id to the 'processed_receipts' file in the archive folder.
        Each tax_id is written on a new line.
        """
        archive_dir = os.path.join(ROOT_DIR, "archive")
        os.makedirs(archive_dir, exist_ok=True)
        processed_file = os.path.join(archive_dir, "processed_receipts")
        with open(processed_file, "a", encoding="utf-8") as f:
            f.write(f"{self.invoice_number}\n")

    def _check_if_tax_id_new(self):
        """
        Checks if the current tax_id is already in the 'processed_receipts' file.
        Returns True if it is NOT present (i.e., it's new), False otherwise.
        """
        archive_dir = os.path.join(ROOT_DIR, "archive")
        processed_file = os.path.join(archive_dir, "processed_receipts")
        if not os.path.isfile(processed_file):
            return True  # File doesn't exist, so tax_id is new

        with open(processed_file, "r", encoding="utf-8") as f:
            invoice_numbers = {line.strip() for line in f}
        return str(self.invoice_number) not in invoice_numbers
            

    def _parse_euro_number(self, s: str) -> float:
        """Convert a European formatted number string to a float."""
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
        logger.info(
            "Constructing output matrix for tax_id: %s, pfr_date: %s",
            self.tax_id,
            self.pfr_date,
        )
        for item in self.items:
            item.append(self.tax_id)
            item.append(self.location_name)
            item.append(self.pfr_date)
            item.append(self.pfr_time)

        self.voucher_data = []
        self.voucher_data.append([
            self.tax_id,
            self.location_name,
            self.pfr_date,
            self.pfr_time,
            self.total_amount,
            self.voucher_value])

        self.output_matrix = {
            "items": self.items,
            "voucher_data": self.voucher_data
        }

    def to_dict(self) -> dict[str, Any] | None:
        """Return the processed output_matrix as a dict."""
        return self.output_matrix