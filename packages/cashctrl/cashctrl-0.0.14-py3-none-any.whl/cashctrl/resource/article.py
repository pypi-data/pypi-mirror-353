from cashctrl.base import CashCtrlResource


class Article(CashCtrlResource):
    """
        Articles are physical products that can have a stock, or services.
    """
    def __init__(self, client):
        super().__init__(client, 'inventory/article')

    def read(self, id):
        """
            Returns a single article by ID.
        """
        return super().read(id)

    def list(self):
        return super().list()
