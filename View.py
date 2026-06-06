from enum import Enum

from PySide6.QtWidgets import QWidget

from qfluentwidgets import FluentIcon, FluentWindow

class UI(Enum):
  CATEGORIES      = 0
  CREATE_CATEGORY = 1
  EDIT_CATEGORY   = 2
  RECORDS         = 3
  CREATE_RECORD   = 4
  EDIT_RECORD     = 5
  STATISTICS      = 6

class CategoryWidget(QWidget):
  def __init__(self) -> None:
    super().__init__()

class CategoriesView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class CreateCategoryView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class EditCategoryView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class RecordsView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class CreateRecordView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class EditRecordView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class StatisticsView(QWidget):
  def __init__(self) -> None:
    super().__init__()

class View(FluentWindow):
  def __init__(self) -> None:
    super().__init__()

    self.setWindowTitle("Expense Tracker")

    self.stackedWidget.setAnimationEnabled(False)

    self.navigationInterface.setExpandWidth(300)
    self.navigationInterface.setCollapsible(False)

    # Create views
    self.categories_view = CategoriesView()
    self.create_category_view = CreateCategoryView()
    self.edit_category_view = EditCategoryView()

    self.records_view = RecordsView()
    self.create_record_view = CreateRecordView()
    self.edit_record_view = EditRecordView()

    self.statistics_view = StatisticsView()

    # Add views to stacked widget
    self.categories_view.setObjectName("categories-view")
    self.records_view.setObjectName("records-view")
    self.statistics_view.setObjectName("statistics-view")

    self.addSubInterface(self.categories_view, FluentIcon.TILES,"Categories")
    self.stackedWidget.addWidget(self.create_category_view)
    self.stackedWidget.addWidget(self.edit_category_view)
    
    self.addSubInterface(self.records_view, FluentIcon.DICTIONARY, "Records")
    self.stackedWidget.addWidget(self.create_record_view)
    self.stackedWidget.addWidget(self.edit_record_view)
    
    self.addSubInterface(self.statistics_view, FluentIcon.MARKET, "Statistics")

  def set_view(self, ui) -> None:
    self.stackedWidget.setCurrentIndex(ui.value)
