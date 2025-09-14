import json

from assistant.parser import ReceiptParser


def test_parse_euro_number(tmp_path, monkeypatch):
    data = {
        "journal": "",
        "invoiceRequest": {},
        "invoiceResult": {}
    }
    dummy = tmp_path / "dummy.json"
    dummy.write_text(json.dumps(data), encoding='utf-8')

    # prevent side effects in __init__
    monkeypatch.setattr(ReceiptParser, '_check_if_tax_id_new', lambda self: False)
    parser = ReceiptParser(str(dummy), user_telegram_id=1)
    assert parser._parse_euro_number('1.234,56') == 1234.56


def test_is_tax_id_new_property(tmp_path, monkeypatch):
    data = {
        "journal": "",
        "invoiceRequest": {},
        "invoiceResult": {}
    }
    dummy = tmp_path / "dummy.json"
    dummy.write_text(json.dumps(data), encoding='utf-8')

    monkeypatch.setattr(ReceiptParser, '_check_if_tax_id_new', lambda self: False)
    parser = ReceiptParser(str(dummy), user_telegram_id=1)
    assert parser.is_tax_id_new is False
