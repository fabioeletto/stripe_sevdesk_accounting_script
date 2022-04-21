from datetime import datetime
from view_models.view_model import ViewModel


class AccountingViewModel(ViewModel):
    """Accounting view model which contains the properties for the accounting process"""
    def __init__(
        self,
        invoice,
        voucher_id,
        voucher_number,
        voucher_pdf_url,
        voucher_date,
        voucher_type,
        voucher_tax_rate,
        voucher_position_lines_data,
        voucher_total_amount,
        voucher_paid_at,
    ):
        super().__init__()
        self.invoice = invoice
        self.voucher_id = voucher_id
        self.voucher_number = voucher_number
        self.voucher_pdf_url = voucher_pdf_url
        self.voucher_date = datetime.fromtimestamp(
            int(voucher_date)
        ).strftime("%d.%m.%Y")
        self.supplier_name = (
            invoice.customer_name
            if invoice.customer_name is not None
            else invoice.customer_email
        )
        self.voucher_type = voucher_type
        self.delivery_date = datetime.fromtimestamp(
            int(invoice.lines.data[0].period.start)
        ).strftime("%d.%m.%Y")

        self.delivery_date_until = datetime.fromtimestamp(
            int(invoice.lines.data[0].period.end)
        ).strftime("%d.%m.%Y")
        self.voucher_tax_rate = voucher_tax_rate
        self.voucher_position_lines_data = voucher_position_lines_data
        self.voucher_total_amount = voucher_total_amount
        self.voucher_paid_at = datetime.fromtimestamp(
            int(voucher_paid_at)
        ).strftime("%d.%m.%Y")
        
