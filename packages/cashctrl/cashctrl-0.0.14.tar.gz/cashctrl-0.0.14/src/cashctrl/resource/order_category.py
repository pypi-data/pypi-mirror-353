#!/usr/bin/env python

from cashctrl.base import CashCtrlResource

class OrderCategory(CashCtrlResource):
    """
    API endpoints for managing order categories (invoices, offers, etc.).
    """

    def __init__(self, client):
        super().__init__(client, 'order/category')

    def read(self, id):
        """
        Returns a single category by ID.
        """
        return super().read(id)

    def list(self, **kwargs):
        """
        Returns a list of categories (sales or purchase).
        :param fiscalPeriodId: (int) ID of fiscal period to retrieve counts from.
        :param type: (str) SALES or PURCHASE. Defaults to SALES.
        """
        return super().list(**kwargs)

    def create(self, data, **kwargs):
        """
        Creates a new category.
        :param data: (dict) Category fields, e.g. accountId, namePlural, nameSingular, status, etc.
        """
        return self._client._make_request(
            'POST',
            f'{self._resource}/create.json',
            data={**data, **kwargs}
        )

    def update(self, data, **kwargs):
        """
        Updates an existing category.
        :param data: (dict) Category fields, must include 'id'.
        """
        return self._client._make_request(
            'POST',
            f'{self._resource}/update.json',
            data={**data, **kwargs}
        )

    def delete(self, ids, **kwargs):
        """
        Deletes one or multiple categories by IDs (comma-separated if multiple).
        """
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/delete.json',
            data={'ids': ids, **kwargs}
        )

    def reorder(self, ids, target, before=True, type='SALES'):
        """
        Changes the order of one or multiple categories.
        :param ids: (list or comma-separated string) IDs of entries to reorder.
        :param target: (int) The target entry ID.
        :param before: (bool) Place before target if true, else after.
        :param type: (str) SALES or PURCHASE.
        """
        if isinstance(ids, (list, tuple)):
            ids = ",".join(map(str, ids))
        return self._client._make_request(
            'POST',
            f'{self._resource}/reorder.json',
            data={'ids': ids, 'target': target, 'before': before, 'type': type}
        )

    def read_status(self, id, **kwargs):
        """
        Returns a single status by ID.
        """
        return self._client._make_request(
            'GET',
            f'{self._resource}/read_status.json',
            params={'id': id, **kwargs}
        )
