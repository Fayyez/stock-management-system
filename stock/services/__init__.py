from .export import ExportService
from .stock import StockService


class ServiceFactory:
    _stock_service = None

    @classmethod
    def get_stock_service(cls):
        if cls._stock_service is None:
            cls._stock_service = StockService()
        return cls._stock_service

    @classmethod
    def get_export_service(cls):
        return ExportService()


stock_service = ServiceFactory.get_stock_service()
export_service = ServiceFactory.get_export_service()
