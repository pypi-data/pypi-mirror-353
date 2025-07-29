from cashctrl.base import CashCtrlResource

class Person(CashCtrlResource):
    """
    The following API endpoints are for managing persons.
    """

    def __init__(self, client):
        super().__init__(client, 'person')
    
    def read(self, id):
        """
            Returns a single person by ID.
        """
        return super().read(id)
    
    def list(self, **kwargs):
        """
            Returns a list of people.
        """
        return super().list(**kwargs)
    