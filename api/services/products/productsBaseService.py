from abc import ABC, abstractmethod


class ProductsBaseService(ABC):

    @abstractmethod
    def get_products(self):
        """ Abstarct method to get all Products"""
        pass