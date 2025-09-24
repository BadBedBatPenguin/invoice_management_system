import shutil
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, Sequence

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Invoice, InvoiceMetadata


async def create_invoice(
    session: AsyncSession, filepath: str, created_at: datetime, meta: dict
) -> Invoice:
    invoice = Invoice(filepath=filepath, created_at=created_at.timestamp())
    invoice.invoice_metadata = InvoiceMetadata(
        invoice_id=invoice.id,
        invoice_number=meta["invoice_number"],
        issue_date=date.fromisoformat(meta["issue_date"]),
        supplier_id=meta["supplier_id"],
        customer_id=meta["customer_id"],
        payable_amount=Decimal(meta["payable_amount"]),
    )
    session.add(invoice)
    await session.commit()
    await session.refresh(invoice)
    return invoice


async def get_invoice(session: AsyncSession, invoice_id: int) -> Optional[Invoice]:
    result = await session.execute(select(Invoice).where(Invoice.id == invoice_id))
    return result.scalar_one_or_none()


async def get_all_invoices(
    session: AsyncSession, limit: int, offset: int
) -> Sequence[Invoice]:
    result = await session.execute(select(Invoice).limit(limit).offset(offset))
    return result.scalars().all()


def get_unique_filename(directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)

    file_path = directory / filename
    if not file_path.exists():
        return file_path

    stem = file_path.stem
    suffix = file_path.suffix
    counter = 1

    while True:
        new_filename = f"{stem} ({counter}){suffix}"
        new_file_path = directory / new_filename
        if not new_file_path.exists():
            return new_file_path
        counter += 1


def save_to_file_system(path: Path, file: UploadFile):
    with path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
