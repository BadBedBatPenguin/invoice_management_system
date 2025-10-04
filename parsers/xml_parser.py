from pathlib import Path

from lxml import etree


class InvoiceParser:
    def __init__(self, path: Path):
        self.path = path
        self.tree = etree.parse(path)
        self.namespace = {
            "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        }
        self.xpaths = {
            "invoice_number": ("//cbc:ID/text()",),
            "issue_date": ("//cbc:IssueDate/text()",),
            "supplier_id": (
                "//cac:AccountingSupplierParty//cbc:EndpointID/text()",
                "//cac:AccountingSupplierParty//cac:PartyIdentification//cbc:ID/text()",
            ),
            "customer_id": (
                "//cac:AccountingCustomerParty//cbc:EndpointID/text()",
                "//cac:AccountingCustomerParty//cac:PartyIdentification//cbc:ID/text()",
            ),
            "payable_amount": ("//cbc:PayableAmount/text()",),
        }

    def get_first(self, xpath_expressions) -> str | None:
        for xpath_expr in xpath_expressions:
            result = self.tree.xpath(xpath_expr, namespaces=self.namespace)
            print(f"result: {result}, path_expr: {xpath_expr}")
            if result:
                return result[0]
        return None

    def parse(self) -> dict:
        return {key: self.get_first(value) for key, value in self.xpaths.items()}
