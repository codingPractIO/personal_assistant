import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from parser import ReceiptParser


def test_parse_euro_number(tmp_path, monkeypatch):
    data = {
        "journal": "",
        "invoiceRequest": {},
        "invoiceResult": {}
    }
    dummy = tmp_path / "dummy.json"
    dummy.write_text(json.dumps(data), encoding='utf-8')

    # prevent side effects in __init__
    monkeypatch.setattr(ReceiptParser, '_is_tax_id_new', lambda self: False)
    parser = ReceiptParser(str(dummy))
    assert parser._parse_euro_number('1.234,56') == 1234.56
