from cashctrl.base import CashCtrlResource


class CustomField(CashCtrlResource):
    """
        The following API endpoints are for managing custom fields. An infinite number of custom fields can be defined for all main modules (Journal, Account, Inventory, Order, Person).
    """
    def __init__(self, client):
        super().__init__(client, 'customfield')

    def read(self, id):
        """
            Returns a single custom field by ID.
        """
        return super().read(id)

    def list(self, type=None, **kwargs):
        """
        Retrieves a list of customfields.

        :param type: which module the custom field belongs to. Possible values: JOURNAL, ACCOUNT, INVENTORY_ARTICLE, INVENTORY_ASSET, ORDER, PERSON, FILE, SALARY_STATEMENT.
        :return: A list of filtered and sorted items.
        :rtype: list
        """
        modules=[
            "JOURNAL",
            "ACCOUNT",
            "INVENTORY_ARTICLE",
            "INVENTORY_ASSET",
            "ORDER",
            "PERSON",
            "FILE",
            "SALARY_STATEMENT"
        ]
        if type is None:
            customfields=[]
            for module in modules:
                kwargs["type"] = module
                result=super().list(**kwargs)
                customfields.extend(result)
            return customfields
        if type not in modules:
            raise ValueError(f"Invalid type '{type}'. Possible values: {', '.join(modules)}.")
        return super().list(type=type, **kwargs)
