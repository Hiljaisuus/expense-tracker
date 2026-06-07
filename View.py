from Container import Container

from enum import Enum

from Model import Category, Record, Model

from PySide6 import QtCore, QtGui, QtWidgets

import qfluentwidgets as qfw

class UI(Enum):
  CATEGORIES      = 0
  RECORDS         = 1
  STATISTICS      = 2

class ColorIndicator(QtWidgets.QWidget):
  def __init__(self, color: QtGui.QColor, side: int = 20) -> None:
    super().__init__()

    self.color = color
    self.side = side # square

    self.setFixedSize(self.side, self.side)

  def paintEvent(self, event: QtGui.QPaintEvent) -> None:
    painter = QtGui.QPainter(self)

    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

    painter.setPen(QtCore.Qt.PenStyle.NoPen)
    painter.setBrush(QtGui.QBrush(self.color))

    painter.drawRoundedRect(self.rect(), 0.25 * self.side, 0.25 * self.side)

class CategoryWidget(qfw.CardWidget):
  def __init__(self, category_id: int, categories: Container[Category]) -> None:
    super().__init__()
    
    self.category_id = category_id

    category = categories.get(self.category_id)

    self.edit = qfw.TransparentToolButton(qfw.FluentIcon.EDIT)
    self.remove = qfw.TransparentToolButton(qfw.FluentIcon.DELETE)

    self.h_layout = QtWidgets.QHBoxLayout(self)
    self.h_layout.setSpacing(10)

    self.h_layout.addWidget(ColorIndicator(category.color))
    self.h_layout.addWidget(qfw.TitleLabel(category.name))
    self.h_layout.addStretch()
    self.h_layout.addWidget(self.edit)
    self.h_layout.addWidget(self.remove)

class CategoriesView(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()

    self.add = qfw.TransparentToolButton(qfw.FluentIcon.ADD)
    
    self.scroll_area = qfw.SingleDirectionScrollArea(orient=QtCore.Qt.Orientation.Vertical)
    self.scroll_area.setWidgetResizable(True)
    
    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.DisplayLabel("Categories"))
    self.v_layout.addWidget(self.add)
    self.v_layout.addWidget(self.scroll_area)
  
  def set_data(self, categories: Container[Category]) -> None:
    indices: list[int] = list(range(len(categories.data)))

    indices.sort(key=lambda index: categories.data[index].name)

    widget = QtWidgets.QWidget()
    
    v_layout = QtWidgets.QVBoxLayout(widget)
    for index in indices:
      v_layout.addWidget(CategoryWidget(categories.index_to_id[index], categories))

    v_layout.addStretch()
    
    self.scroll_area.setWidget(widget)

class CreateCategoryDialog(qfw.MessageBoxBase):
  def __init__(self, parent: qfw.FluentWindow) -> None:
    super().__init__(parent)

    self.widget.setMinimumWidth(490)

    self.title = qfw.TitleLabel("New Category")

    self.color_field = qfw.ColorPickerButton(QtGui.QColor.fromRgb(0, 204, 255), "category color")
    self.color_field.setFixedSize(20, 20)

    self.name_field = qfw.LineEdit()
    self.name_field.setPlaceholderText("Category name")

    self.h_layout = QtWidgets.QHBoxLayout()
    self.h_layout.setSpacing(10)

    self.h_layout.addWidget(self.color_field)
    self.h_layout.addWidget(self.name_field)

    self.v_layout = QtWidgets.QVBoxLayout()
    self.v_layout.addWidget(self.title)
    self.v_layout.addSpacing(10)
    self.v_layout.addLayout(self.h_layout)

    self.viewLayout.addLayout(self.v_layout) 

class EditCategoryDialog(qfw.MessageBoxBase):
  def __init__(self, parent: qfw.FluentWindow, category_id: int, categories: Container[Category]) -> None:
    super().__init__(parent)

    self.category_id = category_id

    category = categories.get(self.category_id)

    self.widget.setMinimumWidth(490)

    self.title = qfw.TitleLabel("Edit Category")

    self.color_field = qfw.ColorPickerButton(category.color, "category color")
    self.color_field.setFixedSize(20, 20)

    self.name_field = qfw.LineEdit()
    self.name_field.setText(category.name)

    self.h_layout = QtWidgets.QHBoxLayout()
    self.h_layout.setSpacing(10)

    self.h_layout.addWidget(self.color_field)
    self.h_layout.addWidget(self.name_field)

    self.v_layout = QtWidgets.QVBoxLayout()
    self.v_layout.addWidget(self.title)
    self.v_layout.addSpacing(10)
    self.v_layout.addLayout(self.h_layout)

    self.viewLayout.addLayout(self.v_layout)

class RecordWidget(qfw.CardWidget):
  def __init__(self, record_id: int, model: Model) -> None:
    super().__init__()

    self.record_id = record_id
    self.category_id = model.records.get(self.record_id).category

    record = model.records.get(self.record_id)
    category = model.categories.get(self.category_id)

    self.color_indicator = ColorIndicator(category.color)
    self.category_name = qfw.BodyLabel(category.name)
    self.date = qfw.BodyLabel(QtCore.QDate.fromString(record.date, "yyyy-MM-dd").toString(QtCore.Qt.DateFormat.RFC2822Date))
    self.amount = qfw.StrongBodyLabel(str(record.amount))
    self.description = qfw.BodyLabel(record.description)

    self.category_name.setFixedWidth(200)
    self.date.setFixedWidth(200)
    self.amount.setFixedWidth(200)

    self.description.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

    self.edit = qfw.TransparentToolButton(qfw.FluentIcon.EDIT)
    self.remove = qfw.TransparentToolButton(qfw.FluentIcon.DELETE)

    self.h_layout = QtWidgets.QHBoxLayout(self)
    self.h_layout.setSpacing(10)
    
    self.h_layout.addWidget(self.color_indicator)
    self.h_layout.addWidget(self.category_name)
    self.h_layout.addWidget(self.date)
    self.h_layout.addWidget(self.amount)
    self.h_layout.addWidget(self.description)
    self.h_layout.addWidget(self.edit)
    self.h_layout.addWidget(self.remove)

class RecordsView(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()

    self.add = qfw.TransparentToolButton(qfw.FluentIcon.ADD)

    self.scroll_area = qfw.SingleDirectionScrollArea(orient=QtCore.Qt.Orientation.Vertical)
    self.scroll_area.setWidgetResizable(True)

    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.DisplayLabel("Records"))
    self.v_layout.addWidget(self.add)
    self.v_layout.addWidget(self.scroll_area)
  
  def set_data(self, model: Model) -> None:
    indices = list(range(len(model.records.data)))
    
    indices.sort(key=lambda index: model.records.data[index].date, reverse=True)
    
    widget = QtWidgets.QWidget()

    v_layout = QtWidgets.QVBoxLayout(widget)
    for index in indices:
      v_layout.addWidget(RecordWidget(model.records.index_to_id[index], model))

    v_layout.addStretch()

    self.scroll_area.setWidget(widget)

class CreateRecordDialog(qfw.MessageBoxBase):
  def __init__(self, parent: qfw.FluentWindow, categories: Container[Category]) -> None:
    super().__init__(parent)

    self.widget.setMinimumWidth(490)

    self.categories = categories # needed to convert category index into id

    self.title = qfw.TitleLabel("New Record")

    self.category_field = qfw.ComboBox()

    self.indices = list(range(len(self.categories.data)))

    self.indices.sort(key=lambda index: self.categories.data[index].name)

    for index in self.indices:
      self.category_field.addItem(self.categories.data[index].name)

    self.amount_field = qfw.CompactDoubleSpinBox()

    self.date_field = qfw.FastCalendarPicker()
    self.date_field.setText("")

    self.description_field = qfw.LineEdit()

    self.grid_layout = QtWidgets.QGridLayout()
    self.grid_layout.addWidget(qfw.BodyLabel("Category"), 0, 0)
    self.grid_layout.addWidget(self.category_field, 0, 1)
    self.grid_layout.addWidget(qfw.BodyLabel("Amount"), 1, 0)
    self.grid_layout.addWidget(self.amount_field, 1, 1)
    self.grid_layout.addWidget(qfw.BodyLabel("Date"), 2, 0)
    self.grid_layout.addWidget(self.date_field, 2, 1)
    self.grid_layout.addWidget(qfw.BodyLabel("Description"), 3, 0)
    self.grid_layout.addWidget(self.description_field, 3, 1)

    self.v_layout = QtWidgets.QVBoxLayout()
    self.v_layout.addWidget(self.title)
    self.v_layout.addLayout(self.grid_layout)

    self.viewLayout.addLayout(self.v_layout)
  
  def validate(self) -> bool:
    if self.amount_field.value() == 0:
      qfw.InfoBar.error(
        title="Error",
        content="Amount must be greater than zero.",
        orient=QtCore.Qt.Orientation.Horizontal,
        isClosable=True,
        position=qfw.InfoBarPosition.BOTTOM_RIGHT,
        duration=4000,
        parent=super().parent()
      )

      return False
    
    if not self.date_field.getDate().isValid():
      qfw.InfoBar.error(
        title="Error",
        content="Select a date.",
        orient=QtCore.Qt.Orientation.Horizontal,
        isClosable=True,
        position=qfw.InfoBarPosition.BOTTOM_RIGHT,
        duration=4000,
        parent=super().parent()
      )
      
      return False

    return True

class EditRecordDialog(qfw.MessageBoxBase):
  def __init__(self, parent: qfw.FluentWindow, record_id: int, model: Model) -> None:
    super().__init__(parent)

    self.widget.setMinimumWidth(490)

    self.record_id = record_id
    self.categories = model.categories # needed to convert category index into id

    record = model.records.get(record_id)

    self.title = qfw.TitleLabel("Edit Record")

    self.category_field = qfw.ComboBox()

    self.indices = list(range(len(self.categories.data)))

    self.indices.sort(key=lambda index: self.categories.data[index].name)

    for index in self.indices:
      self.category_field.addItem(self.categories.data[index].name)

    self.category_field.setCurrentIndex(
      self.indices.index(self.categories.id_to_index[record.category])
    )

    self.amount_field = qfw.CompactDoubleSpinBox()
    self.amount_field.setValue(record.amount)

    self.date_field = qfw.FastCalendarPicker()
    self.date_field.setDate(QtCore.QDate.fromString(record.date, "yyyy-MM-dd"))

    self.description_field = qfw.LineEdit()
    self.description_field.setText(record.description)

    self.grid_layout = QtWidgets.QGridLayout()
    self.grid_layout.addWidget(qfw.BodyLabel("Category"), 0, 0)
    self.grid_layout.addWidget(self.category_field, 0, 1)
    self.grid_layout.addWidget(qfw.BodyLabel("Amount"), 1, 0)
    self.grid_layout.addWidget(self.amount_field, 1, 1)
    self.grid_layout.addWidget(qfw.BodyLabel("Date"), 2, 0)
    self.grid_layout.addWidget(self.date_field, 2, 1)
    self.grid_layout.addWidget(qfw.BodyLabel("Description"), 3, 0)
    self.grid_layout.addWidget(self.description_field, 3, 1)

    self.v_layout = QtWidgets.QVBoxLayout()
    self.v_layout.addWidget(self.title)
    self.v_layout.addLayout(self.grid_layout)

    self.viewLayout.addLayout(self.v_layout)

  def validate(self) -> bool:
    if self.amount_field.value() == 0:
      qfw.InfoBar.error(
        title="Error",
        content="Amount must be greater than zero.",
        orient=QtCore.Qt.Orientation.Horizontal,
        isClosable=True,
        position=qfw.InfoBarPosition.BOTTOM_RIGHT,
        duration=4000,
        parent=super().parent()
      )

      return False
    
    if not self.date_field.getDate().isValid():
      qfw.InfoBar.error(
        title="Error",
        content="Select a date.",
        orient=QtCore.Qt.Orientation.Horizontal,
        isClosable=True,
        position=qfw.InfoBarPosition.BOTTOM_RIGHT,
        duration=4000,
        parent=super().parent()
      )
      
      return False

    return True

class StatisticsView(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()

    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.DisplayLabel("Statistics"))

class View(qfw.FluentWindow):
  def __init__(self) -> None:
    super().__init__()

    self.setWindowTitle("Expense Tracker")

    self.stackedWidget.setAnimationEnabled(False)

    # Create views
    self.categories_view = CategoriesView()
    self.records_view = RecordsView()
    self.statistics_view = StatisticsView()

    # Add views to stacked widget
    self.categories_view.setObjectName("categories-view")
    self.records_view.setObjectName("records-view")
    self.statistics_view.setObjectName("statistics-view")

    self.addSubInterface(self.categories_view, qfw.FluentIcon.TILES,"Categories")    
    self.addSubInterface(self.records_view, qfw.FluentIcon.DICTIONARY, "Records")
    self.addSubInterface(self.statistics_view, qfw.FluentIcon.MARKET, "Statistics")

  def set_view(self, ui) -> None:
    self.stackedWidget.setCurrentIndex(ui.value)
