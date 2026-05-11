import csv
from io import StringIO


class CSVStockExportStrategy:
    def export(self, records):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
        for stock in records:
            writer.writerow([stock.category, stock.item_name, stock.quantity])
        return output.getvalue()


class CSVHistoryExportStrategy:
    def export(self, records):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'CATEGORY',
            'ITEM NAME',
            'QUANTITY',
            'ISSUE QUANTITY',
            'RECEIVE QUANTITY',
            'RECEIVE BY',
            'ISSUE BY',
            'LAST UPDATED',
        ])
        for stock in records:
            writer.writerow([
                stock.category,
                stock.item_name,
                stock.quantity,
                stock.issue_quantity,
                stock.receive_quantity,
                stock.received_by_user.username if getattr(stock, 'received_by_user', None) else stock.received_by,
                stock.issued_by_user.username if getattr(stock, 'issued_by_user', None) else stock.issued_by,
                stock.last_updated,
            ])
        return output.getvalue()
