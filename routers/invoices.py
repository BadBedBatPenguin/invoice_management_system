from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_unique_filename, save_to_file_system
from models import invoices as invoice_models
from database.database import async_session
from settings import file_management_settings
from parsers.xml_parser import InvoiceParser
from database.invoices import get_all_invoices, get_invoice, write_invoice

router = APIRouter(prefix="/invoices", tags=["Invoices"])


class Messages:
    SUCCESS_INVOICE_CREATION_MESSAGE = "Invoice saved successfully."
    INVOICE_CREATION_FAILED_MESSAGE = "An error occured while creating invoice: {error}"
    INVOICE_NOT_FOUND_ERROR = "Invoice with id = {id} not found."


messages = Messages()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@router.get("/invoices/get", response_model=list[invoice_models.InvoiceRead])
async def read_invoices(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    invoices = await get_all_invoices(session, limit, offset)
    return [
        invoice_models.InvoiceRead(
            created_at=datetime.fromtimestamp(invoice.created_at).isoformat() + "Z",
            id=invoice.id,
            metadata=invoice_models.InvoiceMetadataRead(
                **invoice.invoice_metadata.__dict__
            ),
        )
        for invoice in invoices
    ]


@router.post("/invoices/create")
async def create_invoice(
    file: UploadFile = File(...), session: AsyncSession = Depends(get_session)
):
    try:

        file_path = get_unique_filename(
            file_management_settings.xml_files_directory,
            file.filename if file.filename else "",
        )

        save_to_file_system(file_path, file)

        data = InvoiceParser(file_path).parse()

        await write_invoice(
            session=session,
            filepath=str(file_path),
            created_at=datetime.now(),
            meta=data,
        )

        return {
            "id": data["invoice_number"],
            "message": messages.SUCCESS_INVOICE_CREATION_MESSAGE,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=messages.INVOICE_CREATION_FAILED_MESSAGE.format(error=e),
        )


@router.get("/invoices/{invoice_id}/xml")
async def get_invoice_xml(
    invoice_id: int, session: AsyncSession = Depends(get_session)
):
    invoice = await get_invoice(session, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=messages.INVOICE_NOT_FOUND_ERROR.format(id=invoice_id),
        )
    with open(invoice.filepath, "r", encoding="utf-8") as f:
        xml_content = f.read()
    return Response(content=xml_content, media_type="application/xml")
