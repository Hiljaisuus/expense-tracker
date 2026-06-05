from dataclasses import dataclass

from PySide6.QtGui import QColor

from Container import Container

@dataclass
class Category:
  name: str
  color: QColor

@dataclass
class Record:
  category: int
  amount: float
  date: str
  description: str

@dataclass
class Model:
  categories: Container[Category]
  records: Container[Record]