from stock.exporters import CSVHistoryExportStrategy, CSVStockExportStrategy


class ExportService:
    def __init__(self, stock_strategy=None, history_strategy=None):
        self.stock_strategy = stock_strategy or CSVStockExportStrategy()
        self.history_strategy = history_strategy or CSVHistoryExportStrategy()

    def export_stocks_to_csv(self, stocks):
        return self.stock_strategy.export(stocks)

    def export_history_to_csv(self, history):
        return self.history_strategy.export(history)
