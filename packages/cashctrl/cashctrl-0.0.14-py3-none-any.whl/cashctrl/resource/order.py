#!/usr/bin/env python

from cashctrl.base import CashCtrlResource

class Order(CashCtrlResource):
    """
    API endpoints for managing orders (invoices, offers, etc.), both sales and purchase.
    """

    def __init__(self, client):
        super().__init__(client, 'order', 'description')

    def read(self, id):
        """
            Returns a single order by ID.
        """
        return super().read(id)

    def list(self, **kwargs):
        """
            Returns a list of orders.
        """
        return super().list(**kwargs)

    def export_excel(self, **kwargs):
        return self._client._make_request(
            'GET',
            f'{self._resource}/list.xlsx',
            params={**kwargs}
        )

    def export_csv(self, **kwargs):
        return self._client._make_request(
            'GET',
            f'{self._resource}/list.csv',
            params={**kwargs}
        )

    def export_pdf(self, **kwargs):
        return self._client._make_request(
            'GET',
            f'{self._resource}/list.pdf',
            params={**kwargs}
        )

    def create(self, data, **kwargs):
        return self._client._make_request(
            'POST',
            f'{self._resource}/create.json',
            data={**data, **kwargs}
        )

    def update(self, data):
        return self._client._make_request(
            'POST',
            f'{self._resource}/update.json',
            data=data
        )

    def prepare_for_update(self,order):
        import json
        """
        Map order fields from the read endpoint to the /update.json payload.
        Remove read-only fields not accepted by /update.json.
        """
        # Mandatory
        payload = {
            "id": order["id"],  # mandatory
            "associateId": order["associateId"],  # mandatory
            "categoryId": order["categoryId"],  # mandatory
            # date must be YYYY-MM-DD
            "date": order["date"][:10],
        }

        # Optional fields the update endpoint accepts:
        if order.get("accountId") is not None:
            payload["accountId"] = order["accountId"]

        if order.get("currencyId") is not None:
            payload["currencyId"] = order["currencyId"]

        if order.get("currencyRate") is not None:
            payload["currencyRate"] = order["currencyRate"]

        if order.get("custom"):
            payload["custom"] = order["custom"]  # e.g. <values><customField101>...</customField101></values>

        if order.get("daysBefore") is not None:
            payload["daysBefore"] = order["daysBefore"]

        if order.get("description"):
            payload["description"] = order["description"]

        if order.get("discountPercentage") is not None:
            payload["discountPercentage"] = order["discountPercentage"]

        if order.get("dueDays") is not None:
            payload["dueDays"] = order["dueDays"]

        if order.get("endDate"):
            # Must be YYYY-MM-DD
            payload["endDate"] = order["endDate"][:10] if len(order["endDate"]) >= 10 else order["endDate"]

        if order.get("groupId") is not None:
            payload["groupId"] = order["groupId"]

        if order.get("isDisplayItemGross") is not None:
            payload["isDisplayItemGross"] = "true" if order["isDisplayItemGross"] else "false"

        if order.get("language"):
            payload["language"] = order["language"]

        if order.get("notes"):
            payload["notes"] = order["notes"]

        if order.get("notifyEmail"):
            payload["notifyEmail"] = order["notifyEmail"]

        if order.get("notifyPersonId") is not None:
            payload["notifyPersonId"] = order["notifyPersonId"]

        if order.get("notifyType"):
            payload["notifyType"] = order["notifyType"]

        if order.get("notifyUserId") is not None:
            payload["notifyUserId"] = order["notifyUserId"]

        if order.get("nr"):
            payload["nr"] = order["nr"]

        if order.get("previousId") is not None:
            payload["previousId"] = order["previousId"]

        if order.get("recurrence"):
            payload["recurrence"] = order["recurrence"]

        if order.get("responsiblePersonId") is not None:
            payload["responsiblePersonId"] = order["responsiblePersonId"]

        if order.get("roundingId") is not None:
            payload["roundingId"] = order["roundingId"]

        if order.get("sequenceNumberId") is not None:
            payload["sequenceNumberId"] = order["sequenceNumberId"]

        if order.get("startDate"):
            payload["startDate"] = order["startDate"][:10]

        if order.get("statusId") is not None:
            payload["statusId"] = order["statusId"]

        # Items: convert to the minimal necessary fields as JSON
        if "items" in order and order["items"]:
            sanitized_items = []
            for item in order["items"]:
                sanitized_item = {
                    # mandatory in items
                    "accountId": item.get("accountId") or 0,
                    "name": item.get("name") or "",
                    "unitPrice": item.get("unitPrice") or 0,

                    # optional
                    "articleNr": item.get("articleNr") or "",
                    "description": item.get("description") or "",
                    "discountPercentage": item.get("discountPercentage"),
                    "inventoryId": item.get("inventoryId"),
                    "quantity": item.get("quantity") or 1,
                    "taxId": item.get("taxId"),
                    "type": item.get("type") or "ARTICLE",
                    "unitId": item.get("unitId") or "1002",
                }
                sanitized_items.append(sanitized_item)

            # The update endpoint wants this array as a JSON string
            payload["items"] = json.dumps(sanitized_items)

        # Skipped (read-only or purely informational):
        #    - actionId, allocationCount, associateName, attachmentCount, attachments, bookType,
        #      costCenterIds, costCenterNumbers, created, createdBy, currencyCode, dateDeliveryEnd,
        #      dateDeliveryStart, dateLastBooked, defaultCurrencyTotal, downloaded, downloadedBy,
        #      due, foreignCurrency, groupOpen, hasDueDays, hasRecurrence, icon, isAddStock, isBook,
        #      isClosed, isCreditNote, isFileReplacement, isRemoveStock, iso11649Reference,
        #      lastUpdated, lastUpdatedBy, namePlural, nameSingular, open, paid, qrReference,
        #      recurrenceId, responsiblePersonName, roundingDifference, sent, sentBy, sentStatusId,
        #      statusName, subTotal, tax, taxType, total, type

        return payload

    def delete(self, ids, **kwargs):
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/delete.json',
            data={'ids': ids, **kwargs}
        )

    def read_status(self, id, **kwargs):
        return self._client._make_request(
            'GET',
            f'{self._resource}/status_info.json',
            params={'id': id, **kwargs}
        )

    def update_status(self, ids, status_id, **kwargs):
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/update_status.json',
            data={'ids': ids, 'statusId': status_id, **kwargs}
        )

    def update_recurrence(self, id, **kwargs):
        return self._client._make_request(
            'POST',
            f'{self._resource}/update_recurrence.json',
            data={'id': id, **kwargs}
        )

    def continue_as(self, category_id, ids, **kwargs):
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/continue.json',
            data={'categoryId': category_id, 'ids': ids, **kwargs}
        )

    def read_dossier(self, id, **kwargs):
        return self._client._make_request(
            'GET',
            f'{self._resource}/dossier.json',
            params={'id': id, **kwargs}
        )

    def add_to_dossier(self, group_id, ids, **kwargs):
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/dossier_add.json',
            data={'groupId': group_id, 'ids': ids, **kwargs}
        )

    def remove_from_dossier(self, group_id, ids, **kwargs):
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/dossier_remove.json',
            data={'groupId': group_id, 'ids': ids, **kwargs}
        )

    def update_attachments(self, id, file_ids=None, **kwargs):
        if isinstance(file_ids, (list, tuple)):
            file_ids = ",".join(map(str, file_ids))
        data = {'id': id}
        if file_ids is not None:
            data['fileIds'] = file_ids
        data.update(kwargs)
        return self._client._make_request(
            'POST',
            f'{self._resource}/update_attachments.json',
            data=data
        )
