from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class InvoiceMetadataBase(BaseModel):
    invoice_number: str
    issue_date: date
    supplier_id: str
    customer_id: str
    payable_amount: Decimal


class InvoiceMetadataCreate(InvoiceMetadataBase):
    pass


class InvoiceMetadataRead(InvoiceMetadataBase):
    class Config:
        orm_mode = True


class InvoiceBase(BaseModel):
    created_at: str


class InvoiceCreate(InvoiceBase):
    id: int
    message: str


class InvoiceRead(InvoiceBase):
    id: int
    metadata: InvoiceMetadataRead | None = None

    class Config:
        orm_mode = True
        populate_by_name = True
