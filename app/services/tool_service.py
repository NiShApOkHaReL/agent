from langchain.tools import tool
import requests
from app.config.settings import settings
from langchain_community.utilities import GoogleSerperAPIWrapper

search = GoogleSerperAPIWrapper()

class CurrencyTools:
    @staticmethod
    @tool
    def get_exchange_rate(currency_from: str, currency_to: str) -> str:
        """Returns exchange rate between currencies"""
        url = f"https://api.frankfurter.app/latest?from={currency_from}&to={currency_to}"
        return requests.get(url).text

class MathTools:
    @staticmethod
    @tool
    def magic_function(input: int) -> int:
        """Applies a magic function to an input"""
        return input + 2
    
    @staticmethod
    @tool
    def add(a: float, b: float) -> float:
        """Adds two numbers"""
        return a + b
    
    @staticmethod
    @tool
    def multiply(a: float, b: float) -> float:
        """Multiplies two numbers"""
        return a * b
 
class SearchTools:
    @staticmethod
    @tool
    def google_search(query: str) -> str:
        """Performs Google search"""
        return search.run(query)
