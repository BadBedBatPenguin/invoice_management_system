from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filepath: Mapped[str]
    created_at: Mapped[float]

    invoice_metadata: Mapped["InvoiceMetadata"] = relationship(
        back_populates="invoice",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class InvoiceMetadata(Base):
    __tablename__ = "invoice_meta_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(ForeignKey("invoices.id"), unique=True)

    invoice: Mapped["Invoice"] = relationship(back_populates="invoice_metadata")

    invoice_number: Mapped[str]
    issue_date: Mapped[date]
    supplier_id: Mapped[str]
    customer_id: Mapped[str]
    payable_amount: Mapped[Decimal]
