from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

import utils
import validation_models
from database import async_session
from settings import file_management_settings
from xml_parser import InvoiceParser

router = APIRouter(prefix="/invoices", tags=["Invoices"])


class Messages:
    SUCCESS_INVOICE_CREATION_MESSAGE = "Invoice saved successfully."
    INVOICE_CREATION_FAILED_MESSAGE = "An error occured while creating invoice: {error}"
    INVOICE_NOT_FOUND_ERROR = "Invoice with id = {id} not found."


messages = Messages()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@router.get("/invoices/get", response_model=list[validation_models.InvoiceRead])
async def read_invoices(
    session: AsyncSession = Depends(get_session),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    invoices = await utils.get_all_invoices(session, limit, offset)
    return [
        validation_models.InvoiceRead(
            created_at=datetime.fromtimestamp(invoice.created_at).isoformat() + "Z",
            id=invoice.id,
            metadata=validation_models.InvoiceMetadataRead(
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

        file_path = utils.get_unique_filename(
            file_management_settings.xml_files_directory,
            file.filename if file.filename else "",
        )

        utils.save_to_file_system(file_path, file)

        data = InvoiceParser(file_path).parse()

        await utils.create_invoice(
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
    invoice = await utils.get_invoice(session, invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=404,
            detail=messages.INVOICE_NOT_FOUND_ERROR.format(id=invoice_id),
        )
    with open(invoice.filepath, "r", encoding="utf-8") as f:
        xml_content = f.read()
    return Response(content=xml_content, media_type="application/xml")
