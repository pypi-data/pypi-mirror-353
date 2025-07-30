import logging
from typing import List, Optional, Tuple, Union

import requests
from crudclient.types import JSONDict

from tripletex.core.group import TripletexGroup
from tripletex.utils import ensure_date_params

from ..models.gbat10 import VoucherImportGbat10
from ..models.voucher import Voucher, VoucherCreate, VoucherResponse, VoucherUpdate
from .historical import TripletexVoucherHistorical
from .opening_balance import TripletexVoucherOpeningBalance

logger = logging.getLogger(__name__)


class VoucherGroup(TripletexGroup):
    _resource_path = "voucher"
    _datamodel = Voucher
    _create_model = VoucherCreate
    _update_model = VoucherUpdate
    _api_response_model = VoucherResponse
    allowed_actions = ["list", "read", "create", "update", "destroy"]

    def _register_child_endpoints(self) -> None:
        self.historical = TripletexVoucherHistorical(self.client, parent=self)
        self.opening_balance = TripletexVoucherOpeningBalance(self.client, parent=self)

    def create(self, data: Union[JSONDict, "VoucherCreate"], parent_id: Optional[str] = None, send_to_ledger: bool = True) -> Voucher:
        """
        Create a new voucher.
        """
        params = {"sendToLedger": send_to_ledger}
        return super().create(data=data, parent_id=parent_id, params=params)

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None):
        """
        List vouchers.
        """
        params = ensure_date_params(params)
        return super().list(parent_id=parent_id, params=params)

    def search(
        self,
        number: Optional[str] = None,
        number_from: Optional[int] = None,
        number_to: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        from_index: int = 0,
        count: int = 1000,
        sorting: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> VoucherResponse:
        """
        Find vouchers corresponding with sent data.
        """
        params: JSONDict = {"from": from_index, "count": count}
        if number:
            params["number"] = number
        if number_from:
            params["numberFrom"] = number_from
        if number_to:
            params["numberTo"] = number_to
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        params = ensure_date_params(params)
        if sorting:
            params["sorting"] = sorting
        if fields:
            params["fields"] = fields
        return super().list(params=params)

    def get_options(self, voucher_id: str) -> JSONDict:
        """
        Get meta information about operations available for this voucher (e.g., if deletable).
        """
        endpoint = self._get_endpoint(str(voucher_id), "options")
        return self.client.get(endpoint)

    def get_pdf(self, voucher_id: str) -> "requests.Response":
        """
        Get PDF representation of voucher by ID.
        """
        endpoint = self._get_endpoint(str(voucher_id), "pdf")
        response = self.client.http_client.request_raw("GET", endpoint)
        return response

    def list_non_posted(self, params: Optional[JSONDict] = None) -> VoucherResponse:
        """
        Find non-posted vouchers.
        """
        endpoint = self._get_endpoint(">nonPosted")
        raw_response = self.client.get(endpoint, params=params)
        return self._api_response_model.model_validate(raw_response)

    def download_pdf(self, voucher_id: str, file_path: Optional[str] = None) -> Tuple[str, str]:
        """
        Download PDF for voucher by ID and save to file_path.
        """
        import re

        response = self.get_pdf(voucher_id)
        content_disposition = response.headers.get("Content-Disposition", "")
        filename = "voucher.pdf"
        match = re.search(r'filename="?([^";]+)"?', content_disposition)
        if match:
            filename = match.group(1)
        pdf_bytes = response.content
        if file_path is None:
            file_path = filename
        with open(file_path, "wb") as f:
            f.write(pdf_bytes)
        return file_path, filename

    def upload_attachment(self, voucher_id: int, file_path: str) -> Voucher:
        """
        Upload an attachment to a voucher.
        """
        import os

        endpoint = self._get_endpoint(str(voucher_id), "attachment")
        url = self.client.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        with open(file_path, "rb") as f:
            filename = os.path.basename(file_path)
            if not filename.lower().endswith(".pdf"):
                raise ValueError("Only PDF files are allowed for voucher attachments. This is a limitation of the Tripletex API.")
            files = {"file": (filename, f, "application/pdf")}
            response = self.client.session.post(url, files=files)
            response.raise_for_status()
            data = response.json()
        return self._datamodel.model_validate(data["value"])

    def destroy(self, resource_id: str, parent_id: Optional[str] = None) -> None:
        """
        Delete voucher by ID.
        """
        return super().destroy(resource_id=resource_id, parent_id=parent_id)

    delete = destroy

    def destroy_attachment(
        self, voucher_id: str, attachment_id: str, version: Optional[int] = None, send_to_inbox: bool = False, split: bool = False
    ) -> None:
        """
        Delete an attachment from a voucher.
        """
        endpoint = self._get_endpoint(str(voucher_id), "attachment")
        params = {"id": attachment_id}
        if version is not None:
            params["version"] = str(version)
        if send_to_inbox:
            params["sendToInbox"] = str(send_to_inbox).lower()
        if split:
            params["split"] = str(split).lower()
        self.client.delete(endpoint, params=params)

    delete_attachment = destroy_attachment

    def voucher_reception(self, params: Optional[JSONDict] = None) -> VoucherResponse:
        """
        Get voucher reception list.
        """
        endpoint = self._get_endpoint(">voucherReception")
        raw_response = self.client.get(endpoint, params=params)
        return self._api_response_model.model_validate(raw_response)

    def external_voucher_number(
        self,
        external_voucher_number: Optional[str] = None,
        from_index: int = 0,
        count: int = 1000,
        sorting: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> VoucherResponse:
        """
        Find vouchers based on the external voucher number.
        """
        params: JSONDict = {"from": from_index, "count": count}
        if external_voucher_number:
            params["externalVoucherNumber"] = external_voucher_number
        if sorting:
            params["sorting"] = sorting
        if fields:
            params["fields"] = fields
        endpoint = self._get_endpoint(">externalVoucherNumber")
        raw_response = self.client.get(endpoint, params=params)
        return self._api_response_model.model_validate(raw_response)

    def import_gbat10(self, data: Union[JSONDict, "VoucherImportGbat10"]) -> None:
        """
        Import GBAT10 format vouchers.
        """
        import os

        from tripletex.endpoints.ledger.models.gbat10 import VoucherImportGbat10

        if isinstance(data, dict):
            data = VoucherImportGbat10.model_validate(data)
        if not os.path.exists(data.file_path):
            if data.content:
                data.write_content_to_file()
            else:
                try:
                    data.content = None
                    data.write_content_to_file()
                except ValueError:
                    raise ValueError(f"File not found: {data.file_path}")
        if not os.path.exists(data.file_path):
            raise ValueError(f"File not found: {data.file_path}")
        try:
            data.validate_content()
        except ValueError as validation_error:
            raise ValueError(f"Invalid GBAT10 file: {validation_error}")
        endpoint = self._get_endpoint("importGbat10")
        url = self.client.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        with open(data.file_path, "rb") as f:
            filename = os.path.basename(data.file_path)
            files = {"file": (filename, f)}
            form_data = {"generateVatPostings": str(data.generate_vat_postings).lower(), "encoding": data.encoding}
            response = self.client.session.post(url, files=files, data=form_data)
            response.raise_for_status()
        return None

    def update(
        self,
        resource_id: str,
        data: Union[JSONDict, "VoucherUpdate"],
        parent_id: Optional[str] = None,
        send_to_ledger: bool = False,
    ) -> Voucher:
        """
        Update a voucher by ID.
        """
        updated_voucher = super().update(resource_id=resource_id, data=data, parent_id=parent_id)
        is_in_ledger = updated_voucher.number is not None
        if send_to_ledger and not is_in_ledger:
            if updated_voucher.id is None:
                raise ValueError("Cannot send voucher to ledger: updated voucher has no ID.")
            return self.send_to_ledger(voucher_id=str(updated_voucher.id))
        return updated_voucher

    def reverse_voucher(self, voucher_id: str, date: Optional[str] = None) -> Voucher:
        """
        Reverse a voucher.
        """
        data = {}
        if date:
            data["date"] = date
        endpoint = self._get_endpoint(str(voucher_id), ":reverse")
        raw_response = self.client.put(endpoint, data=data)
        return self._datamodel.model_validate(raw_response["value"])

    def update_list(self, vouchers: List[Union[JSONDict, "VoucherUpdate"]]) -> List[Voucher]:
        """
        Update multiple vouchers.
        """
        data_list = []
        for voucher in vouchers:
            if hasattr(voucher, "model_dump"):
                data_list.append(voucher.model_dump(mode="json", by_alias=True))
            else:
                data_list.append(voucher)
        data = {"values": data_list}
        endpoint = self._get_endpoint("list")
        raw_response = self.client.put(endpoint, data=data)
        return [self._datamodel.model_validate(item) for item in raw_response["values"]]

    def send_to_ledger(self, voucher_id: str) -> Voucher:
        """
        Send a voucher to ledger.
        """
        endpoint = self._get_endpoint(str(voucher_id), ":sendToLedger")
        raw_response = self.client.put(endpoint)
        return self._datamodel.model_validate(raw_response["value"])

    def send_to_inbox(self, voucher_id: str) -> Voucher:
        """
        Send a voucher to inbox.
        """
        endpoint = self._get_endpoint(str(voucher_id), ":sendToInbox")
        raw_response = self.client.put(endpoint)
        return self._datamodel.model_validate(raw_response["value"])

    def import_document(
        self,
        file_path: str,
        description: Optional[str] = None,
        voucher_date: Optional[str] = None,
        voucher_type_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None,
        send_to_ledger: bool = True,
        split_by_vat: bool = False,
    ) -> Voucher:
        """
        Import a document as a voucher.
        """
        import mimetypes
        import os

        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        endpoint = self._get_endpoint("importDocument")
        url = self.client.base_url.rstrip("/") + "/" + endpoint.lstrip("/")
        mime_type, _ = mimetypes.guess_type(file_path)
        if not mime_type:
            mime_type = "application/octet-stream"
        form_data = {}
        if description:
            form_data["description"] = description
        if voucher_date:
            form_data["voucherDate"] = voucher_date
        if voucher_type_id:
            form_data["voucherTypeId"] = str(voucher_type_id)
        if supplier_id:
            form_data["supplierId"] = str(supplier_id)
        if employee_id:
            form_data["employeeId"] = str(employee_id)
        if department_id:
            form_data["departmentId"] = str(department_id)
        if project_id:
            form_data["projectId"] = str(project_id)
        form_data["sendToLedger"] = str(send_to_ledger).lower()
        form_data["splitByVat"] = str(split_by_vat).lower()
        with open(file_path, "rb") as f:
            filename = os.path.basename(file_path)
            files = {"file": (filename, f, mime_type)}
            response = self.client.session.post(url, files=files, data=form_data)
            response.raise_for_status()
            data = response.json()
        if "value" in data:
            return self._datamodel.model_validate(data["value"])
        else:
            return self._datamodel.model_validate(data)
