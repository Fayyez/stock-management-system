import csv
from abc import ABC, abstractmethod
from io import StringIO


class ExportStrategy(ABC):
    @abstractmethod
    def export(self, records):
        raise NotImplementedError


class CSVStockExportStrategy(ExportStrategy):
    def export(self, records):
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['CATEGORY', 'ITEM NAME', 'QUANTITY'])
        for stock in records:
            writer.writerow([stock.category, stock.item_name, stock.quantity])
        return output.getvalue()


class CSVHistoryExportStrategy(ExportStrategy):
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
                stock.received_by,
                stock.issued_by,
                stock.last_updated,
            ])
        return output.getvalue()
