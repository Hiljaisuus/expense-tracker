from Container import Container

from enum import Enum

from Model import Category, Record, Model

from PySide6 import QtCore, QtGui, QtWidgets

import qfluentwidgets as qfw

import math

class UI(Enum):
  CATEGORIES      = 0
  INCOME          = 1
  EXPENSES        = 2
  STATISTICS      = 3

def draw_text(painter: QtGui.QPainter, x: int, y: int, w: int, h: int, text: str, align=QtCore.Qt.AlignmentFlag.AlignCenter) -> None:
  painter.drawText(
    QtCore.QRectF(
      x - w / 2,
      y - h / 2,
      w,
      h
    ),
    painter.fontMetrics().elidedText(
      text, QtCore.Qt.TextElideMode.ElideRight, w
    ),
    align
  )

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
  edit = QtCore.Signal(int)
  remove = QtCore.Signal(int)

  def __init__(self, category_id: int, categories: Container[Category]) -> None:
    super().__init__()
    
    self.category_id = category_id

    category = categories.get(self.category_id)

    self.edit_button = qfw.TransparentToolButton(qfw.FluentIcon.EDIT)
    self.remove_button = qfw.TransparentToolButton(qfw.FluentIcon.DELETE)

    self.edit_button.pressed.connect(lambda: self.edit.emit(self.category_id))
    self.remove_button.pressed.connect(lambda: self.remove.emit(self.category_id))

    self.h_layout = QtWidgets.QHBoxLayout(self)
    self.h_layout.setSpacing(10)

    self.h_layout.addWidget(ColorIndicator(category.color))
    self.h_layout.addWidget(qfw.TitleLabel(category.name))
    self.h_layout.addStretch()
    self.h_layout.addWidget(self.edit_button)
    self.h_layout.addWidget(self.remove_button)

class CategoriesView(QtWidgets.QWidget):
  add = QtCore.Signal()
  edit = QtCore.Signal(int)
  remove = QtCore.Signal(int)

  def __init__(self) -> None:
    super().__init__()

    self.add_button = qfw.TransparentToolButton(qfw.FluentIcon.ADD)
    self.add_button.pressed.connect(self.add.emit)

    self.scroll_area = qfw.SingleDirectionScrollArea(orient=QtCore.Qt.Orientation.Vertical)
    self.scroll_area.setWidgetResizable(True)
    
    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.DisplayLabel("Categories"))
    self.v_layout.addWidget(self.add_button)
    self.v_layout.addWidget(self.scroll_area)
  
  def set_data(self, categories: Container[Category]) -> None:
    indices: list[int] = list(range(len(categories.data)))

    indices.sort(key=lambda index: categories.data[index].name)

    widget = QtWidgets.QWidget()
    
    v_layout = QtWidgets.QVBoxLayout(widget)
    for index in indices:
      category = CategoryWidget(categories.index_to_id[index], categories)
      category.edit.connect(self.edit.emit)
      category.remove.connect(self.remove.emit)
      v_layout.addWidget(category)

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

class RemoveCategoryDialog(qfw.MessageBoxBase):
  def __init__(self, parent: qfw.FluentWindow, category_id: int, categories: Container[Category]) -> None:
    super().__init__(parent)

    self.categories = categories

    self.widget.setMinimumWidth(490)

    self.title_label = qfw.TitleLabel("Remove Category")
    self.category_label = qfw.BodyLabel("Replacement Category")
    self.category_field = qfw.ComboBox()

    self.category_field.setSizePolicy(
      QtWidgets.QSizePolicy.Policy.MinimumExpanding,
      QtWidgets.QSizePolicy.Policy.Preferred
    )

    self.indices: list[int] = []

    for index in range(self.categories.size()):
      id = self.categories.index_to_id[index]
      if id != category_id:
        self.indices.append(index)

    self.indices.sort(key=lambda index: self.categories.data[index].name)

    for index in self.indices:
      self.category_field.addItem(self.categories.data[index].name)

    self.h_layout = QtWidgets.QHBoxLayout()
    self.h_layout.addWidget(self.category_label)
    self.h_layout.addWidget(self.category_field)

    self.v_layout = QtWidgets.QVBoxLayout()
    self.v_layout.addWidget(self.title_label)
    self.v_layout.addLayout(self.h_layout)

    self.viewLayout.addLayout(self.v_layout)
  
  def get_category_id(self) -> int:
    return self.categories.index_to_id[self.indices[self.category_field.currentIndex()]]

class RecordWidget(qfw.CardWidget):
  edit = QtCore.Signal(int)
  remove = QtCore.Signal(int)

  def __init__(self, record_id: int, categories: Container[Category], records: Container[Record]) -> None:
    super().__init__()

    self.record_id = record_id
    self.category_id = records.get(self.record_id).category

    record = records.get(self.record_id)
    category = categories.get(self.category_id)

    self.color_indicator = ColorIndicator(category.color)
    self.category_name = qfw.BodyLabel(category.name)
    self.date = qfw.BodyLabel(QtCore.QDate.fromString(record.date, "yyyy-MM-dd").toString(QtCore.Qt.DateFormat.RFC2822Date))
    self.amount = qfw.StrongBodyLabel(str(record.amount))
    self.description = qfw.BodyLabel(record.description)

    self.category_name.setFixedWidth(200)
    self.date.setFixedWidth(200)
    self.amount.setFixedWidth(300)

    self.description.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred)

    self.edit_button = qfw.TransparentToolButton(qfw.FluentIcon.EDIT)
    self.remove_button = qfw.TransparentToolButton(qfw.FluentIcon.DELETE)

    self.edit_button.pressed.connect(lambda: self.edit.emit(self.record_id))
    self.remove_button.pressed.connect(lambda: self.remove.emit(self.record_id))

    self.h_layout = QtWidgets.QHBoxLayout(self)
    self.h_layout.setSpacing(10)
    
    self.h_layout.addWidget(self.color_indicator)
    self.h_layout.addWidget(self.category_name)
    self.h_layout.addWidget(self.date)
    self.h_layout.addWidget(self.amount)
    self.h_layout.addWidget(self.description)
    self.h_layout.addWidget(self.edit_button)
    self.h_layout.addWidget(self.remove_button)

class RecordsView(QtWidgets.QWidget):
  add = QtCore.Signal()
  edit = QtCore.Signal(int)
  remove = QtCore.Signal(int)

  def __init__(self, title: str) -> None:
    super().__init__()

    self.add_button = qfw.TransparentToolButton(qfw.FluentIcon.ADD)
    self.add_button.pressed.connect(self.add.emit)

    self.scroll_area = qfw.SingleDirectionScrollArea(orient=QtCore.Qt.Orientation.Vertical)
    self.scroll_area.setWidgetResizable(True)

    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.DisplayLabel(title))
    self.v_layout.addWidget(self.add_button)
    self.v_layout.addWidget(self.scroll_area)
  
  def set_data(self, categories: Container[Category], records: Container[Record]) -> None:
    indices = list(range(records.size()))
    
    indices.sort(key=lambda index: records.data[index].date, reverse=True)
    
    widget = QtWidgets.QWidget()

    v_layout = QtWidgets.QVBoxLayout(widget)
    for index in indices:
      record_widget = RecordWidget(records.index_to_id[index], categories, records)
      record_widget.edit.connect(self.edit.emit)
      record_widget.remove.connect(self.remove.emit)
      v_layout.addWidget(record_widget)

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

    self.amount_field = qfw.DoubleSpinBox()
    self.amount_field.setMaximum(1000000000)

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
  
  def get_category_id(self) -> int:
    return self.categories.index_to_id[self.indices[self.category_field.currentIndex()]]

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
  def __init__(self, parent: qfw.FluentWindow, record_id: int, categories: Container[Category], records: Container[Record]) -> None:
    super().__init__(parent)

    self.widget.setMinimumWidth(490)

    self.record_id = record_id
    self.categories = categories # needed to convert category index into id

    record = records.get(record_id)

    self.title = qfw.TitleLabel("Edit Record")

    self.category_field = qfw.ComboBox()

    self.indices = list(range(len(self.categories.data)))

    self.indices.sort(key=lambda index: self.categories.data[index].name)

    for index in self.indices:
      self.category_field.addItem(self.categories.data[index].name)

    self.category_field.setCurrentIndex(
      self.indices.index(self.categories.id_to_index[record.category])
    )

    self.amount_field = qfw.DoubleSpinBox()
    self.amount_field.setMaximum(1000000000)
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

  def get_category_id(self) -> int:
    return self.categories.index_to_id[self.indices[self.category_field.currentIndex()]]
  
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

class RemoveRecordDialog(qfw.MessageBoxBase):
  def __init__(self, parent: qfw.FluentWindow) -> None:
    super().__init__(parent)

    self.widget.setMinimumWidth(490)

    self.v_layout = QtWidgets.QVBoxLayout()
    self.v_layout.addWidget(qfw.TitleLabel("Remove Record"))
    self.v_layout.addWidget(qfw.BodyLabel(
      "Are you sure you want to remove the selected record?"
    ))

    self.viewLayout.addLayout((self.v_layout))

class Sector:
  def __init__(self, name: str, value: float, color: QtGui.QColor) -> None:
    self.name = name
    self.value = value
    self.color = color
    self.percentage: float
    self.start: float
    self.end: float

class PieChartRenderer(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()

    self.setMouseTracking(True)

    self.selected_sector = -1

  def set_data(self, sectors: list[Sector]) -> None:
    self.sectors = sectors

  def get_diameter(self) -> int:
    return int(0.9 * min(self.width(), self.height()))

  def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
    position = event.position()

    delta_x = position.x() - self.width()  / 2
    delta_y = position.y() - self.height() / 2

    radius = 0.5 * self.get_diameter()

    if delta_x * delta_x + delta_y * delta_y > radius * radius:
      if self.selected_sector != -1:
        self.selected_sector = -1
        self.update()
      return
    
    theta = 0.5 * (math.atan2(delta_x, delta_y) + math.pi) / math.pi

    for index, sector in enumerate(self.sectors):
      if sector.start < theta and theta < sector.end:
        if index != self.selected_sector:
          self.selected_sector = index
          self.update()

  def paintEvent(self, event: QtGui.QPaintEvent) -> None:
    painter = QtGui.QPainter(self)

    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    
    pen = QtGui.QPen()
    brush = QtGui.QBrush()

    pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

    diameter = self.get_diameter()

    h_padding = int(0.5 * (self.width()  - diameter))
    v_padding = int(0.5 * (self.height() - diameter))

    for index, sector in enumerate(self.sectors):
      pen.setColor(sector.color)
      brush.setColor(sector.color)

      if index == self.selected_sector:
        brush.setColor(sector.color.darker(110))

      painter.setPen(pen)
      painter.setBrush(brush)

      painter.drawPie(
        h_padding,
        v_padding,
        diameter,
        diameter,
        int(5760 * sector.start + 1440),
        int(5760 * sector.percentage),
      )
    
    pen.setColor(QtGui.QColor.fromRgb(255, 255, 255))
    brush.setColor(QtGui.QColor.fromRgb(255, 255, 255))

    painter.setPen(pen)
    painter.setBrush(brush)

    painter.drawEllipse(
      QtCore.QPointF(self.width() / 2, self.height() / 2),
      0.3 * diameter,
      0.3 * diameter
    )

    if self.selected_sector == -1:
      return

    pen.setColor(QtGui.QColor.fromRgb(0, 0, 0))
    painter.setPen(pen)

    sector = self.sectors[self.selected_sector]

    x = self.width()  // 2
    y = self.height() // 2

    painter.setFont(qfw.SubtitleLabel().getFont())
    draw_text(painter, x, y - 25, 130, 50, sector.name)

    painter.setFont(qfw.BodyLabel().getFont())
    draw_text(painter, x, y, 130, 50, f"Total: {int(sector.value)}")
    draw_text(painter, x, y + 20, 130, 50, f"Percentage: {int(100 * sector.percentage)}")

class PieChartWidget(qfw.CardWidget):
  def __init__(self, title: str) -> None:
    super().__init__()

    self.setMinimumHeight(300)
    self.setMinimumWidth(300)

    self.pie_chart_renderer = PieChartRenderer()

    self.pie_chart_renderer.setSizePolicy(
      QtWidgets.QSizePolicy.Policy.Preferred,
      QtWidgets.QSizePolicy.Policy.MinimumExpanding
    )

    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.TitleLabel(title), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
    self.v_layout.addWidget(self.pie_chart_renderer)

  def sizeHint(self) -> QtCore.QSize:
    return QtCore.QSize(720, 480)

  def set_data(self, sectors: list[Sector]) -> None:
    sectors = list(filter(lambda sector: sector.value != 0, sectors))

    total: float = 0
    for sector in sectors:
      total += sector.value
    
    for sector in sectors:
      sector.percentage = sector.value / total
    
    running_total: float = 0
    for sector in sectors:
      sector.start = running_total
      sector.end = sector.start + sector.percentage
      running_total += sector.percentage
    
    self.pie_chart_renderer.set_data(sectors)

class Section:
  def __init__(self, name: str, value: float, color: QtGui.QColor) -> None:
    self.name = name
    self.value = value
    self.color = color
    self.percentage: float
    self.start: float
    self.end: float

class Bar:
  def __init__(self, label: str, sections: list[Section]) -> None:
    self.label = label
    self.sections = sections

class BarChartRenderer(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()

    self.setMouseTracking(True)

  def set_data(self, bars: list[Bar]) -> None:
    self.bars = bars

    self.selected_month = -1
    self.selected_section = -1

  def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
    p = event.position()

    mx = int(p.x())
    my = int(p.y())

    self.mouse_x = mx
    self.mouse_y = my

    width  = self.width()
    height = self.height()

    l_margin = 0.05 * width
    t_margin = 0.05 * height
    r_margin = 0.05 * width
    b_margin = max(0.10 * height, 20)

    chart_width  = width  - l_margin - r_margin
    chart_height = height - t_margin - b_margin
    
    bar_width  = chart_width / 12
    bar_h_margin = 0.25 * bar_width

    for month, bar in enumerate(self.bars):
      for index, section in enumerate(bar.sections):
        x = l_margin + month * bar_width + bar_h_margin
        y = height - b_margin - section.end * chart_height
        w = bar_width - 2 * bar_h_margin
        h = (section.end - section.start) * chart_height

        if mx > x and mx < x + w and my > y and my < y + h:
          if month != self.selected_month or index != self.selected_section:
            self.selected_month = month
            self.selected_section = index
            self.update()
          return
    
    if self.selected_month == -1:
      return
    
    self.selected_month = -1
    self.selected_section = -1

    self.update()

  def paintEvent(self, event: QtGui.QPaintEvent) -> None:
    painter = QtGui.QPainter(self)

    painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

    pen = QtGui.QPen()
    brush = QtGui.QBrush()

    pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
    brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

    width  = self.width()
    height = self.height()

    l_margin = 0.05 * width
    t_margin = 0.05 * height
    r_margin = 0.05 * width
    b_margin = max(0.10 * height, 20)

    chart_width  = width  - l_margin - r_margin
    chart_height = height - t_margin - b_margin
    
    bar_width  = chart_width / 12
    bar_h_margin = 0.25 * bar_width

    for month, bar in enumerate(self.bars):
      for section in bar.sections:
        pen.setColor(section.color)
        brush.setColor(section.color)

        painter.setPen(pen)
        painter.setBrush(brush)

        x = l_margin + month * bar_width + bar_h_margin
        y = height - b_margin - section.end * chart_height

        painter.drawRect(QtCore.QRectF(x, y, bar_width - 2 * bar_h_margin, (section.end - section.start) * chart_height))
    
    pen.setColor(QtGui.QColor.fromRgb(0, 0, 0))
    
    painter.setPen(pen)

    painter.setFont(qfw.BodyLabel().getFont())

    for month, bar in enumerate(self.bars):
      x = int(l_margin + (month + 0.5) * bar_width)
      y = int(height - 0.5 * b_margin)
      w = 30
      h = int(b_margin)

      draw_text(painter, x, y, w, h, bar.label)
    
    if self.selected_month == -1:
      return
    
    pen.setColor(QtGui.QColor.fromRgb(251, 251, 251))
    brush.setColor(QtGui.QColor.fromRgb(251, 251, 251))

    painter.setPen(pen)

    painter.setBrush(brush)

    info_box_width  = int(max(110, 2 * bar_width))
    info_box_height = 76

    section = self.bars[self.selected_month].sections[self.selected_section]

    x = l_margin + (self.selected_month + 1) * bar_width - bar_h_margin + 2
    y = height - b_margin - section.end * chart_height

    if x > width - r_margin - info_box_width:
      x = l_margin + self.selected_month * bar_width + bar_h_margin - info_box_width - 2
    y = min(y, height - b_margin - info_box_height)

    x = int(x)
    y = int(y)

    painter.drawRect(x, y, info_box_width, info_box_height + 1)

    pen.setColor(QtGui.QColor(0, 0, 0))

    painter.setPen(pen)

    text_h_offset = info_box_width // 2 + 10

    painter.setFont(qfw.SubtitleLabel().getFont())
    draw_text(painter, x + text_h_offset, y + 28, info_box_width, 50, section.name, align=QtCore.Qt.AlignmentFlag.AlignLeft)

    painter.setFont(qfw.BodyLabel().getFont())
    draw_text(painter, x + text_h_offset, y + 53, info_box_width, 50, f"Total: {int(section.value)}", align=QtCore.Qt.AlignmentFlag.AlignLeft)
    draw_text(painter, x + text_h_offset, y + 73, info_box_width, 50, f"Percentage: {int(100 * section.percentage)}", align=QtCore.Qt.AlignmentFlag.AlignLeft)

class BarChartWidget(qfw.CardWidget):
  def __init__(self, title: str) -> None:
    super().__init__()

    self.setMinimumHeight(200)
    self.setMinimumWidth(350)

    self.bar_chart_renderer = BarChartRenderer()

    self.bar_chart_renderer.setSizePolicy(
      QtWidgets.QSizePolicy.Policy.Preferred,
      QtWidgets.QSizePolicy.Policy.MinimumExpanding
    )

    self.v_layout = QtWidgets.QVBoxLayout(self)
    self.v_layout.addWidget(qfw.TitleLabel(title), alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
    self.v_layout.addWidget(self.bar_chart_renderer)
  
  def sizeHint(self) -> QtCore.QSize:
    return QtCore.QSize(720, 480)

  def set_data(self, bars: list[Bar]) -> None:
    maximum: float = 0
    for bar in bars:
      total: float = 0
      for section in bar.sections:
        total += section.value
      maximum = max(maximum, total)

    for bar in bars:
      for section in bar.sections:
        section.percentage = section.value / maximum
      
      running_total: float = 0
      for section in bar.sections:
        section.start = running_total
        section.end = section.start + section.percentage
        running_total += section.percentage

    self.bar_chart_renderer.set_data(bars)

class StatisticsView(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()

    self.income_pie_chart = PieChartWidget("Income by Category")
    self.expense_pie_chart = PieChartWidget("Expenses by Category")

    self.income_bar_chart = BarChartWidget("Income Over Time")
    self.expense_bar_chart = BarChartWidget("Expenses Over Time")
    self.net_change_bar_chart = BarChartWidget("Net Change Over Time")

    self.scroll_area = qfw.SingleDirectionScrollArea(orient=QtCore.Qt.Orientation.Vertical)
    self.scroll_area.setWidgetResizable(True)

    self.scroll_area_widget = QtWidgets.QWidget()
    self.scroll_area_widget.setSizePolicy(
      QtWidgets.QSizePolicy.Policy.Preferred,
      QtWidgets.QSizePolicy.Policy.MinimumExpanding
    )
    self.scroll_area.setHorizontalScrollBarPolicy(
      QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    )

    self.grid_layout = QtWidgets.QGridLayout(self.scroll_area_widget)
    self.grid_layout.addWidget(self.income_pie_chart, 0, 0)
    self.grid_layout.addWidget(self.expense_pie_chart, 0, 1)
    self.grid_layout.addWidget(self.income_bar_chart, 1, 0)
    self.grid_layout.addWidget(self.expense_bar_chart, 1, 1)
    self.grid_layout.addWidget(self.net_change_bar_chart, 2, 0, 1, 2)

    self.scroll_area.setWidget(self.scroll_area_widget)

    self.v_layout_2 = QtWidgets.QVBoxLayout(self)
    self.v_layout_2.addWidget(qfw.DisplayLabel("Statistics"))
    self.v_layout_2.addWidget(self.scroll_area)

  def convert_records_to_sectors(self, categories: Container[Category], records: list[Record]) -> list[Sector]:
    num_category_ids = len(categories.id_to_index)

    category_sums: list[float] = [0] * num_category_ids

    for record in records:
      category_sums[record.category] += record.amount

    sectors: list[Sector] = []

    for id in range(num_category_ids):
      if not categories.has(id):
        continue
      
      category = categories.get(id)
      
      sectors.append(Sector(
        category.name,
        category_sums[id],
        category.color
      ))
    
    # sort sectors from largest to smallest
    sectors.sort(key=lambda s: s.value, reverse=True)

    return sectors

  def convert_records_to_bars(self, categories: Container[Category], records: list[Record]) -> list[Bar]:
    num_category_ids = len(categories.id_to_index)

    sums: list[list[float]] = [[0] * num_category_ids for i in range(12)]

    for record in records:
      month = QtCore.QDate.fromString(record.date, "yyyy-MM-dd").month() - 1
      sums[month][record.category] += record.amount
    
    category_sums: list[float] = [0] * num_category_ids

    for month in range(12):
      for category in range(num_category_ids):
        category_sums[category] += sums[month][category]
    
    category_ids = list(range(num_category_ids))

    category_ids.sort(key=lambda id: category_sums[id], reverse=True)

    month_names: list[str] = [
      "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    bars: list[Bar] = []

    for month in range(12):
      sections: list[Section] = []

      for id in category_ids:
        if not categories.has(id) or sums[month][id] == 0:
          continue

        category = categories.get(id)
        
        sections.append(Section(
          category.name,
          sums[month][id],
          category.color
        ))
    
      bars.append(Bar(month_names[month], sections))
    
    return bars

  def calculate_net_change(self, income_bars: list[Bar], expense_bars: list[Bar]) -> list[Bar]:
    monthly_net_change: list[float] = [0] * 12
    
    for month in range(12):
      for section in income_bars[month].sections:
        monthly_net_change[month] += section.value
      
      for section in expense_bars[month].sections:
        monthly_net_change[month] -= section.value
    
    absolute_net_change: float = 0
    
    for v in monthly_net_change:
      absolute_net_change += abs(v)

    minimum = min(monthly_net_change)
    maximum = max(monthly_net_change)

    bars: list[Bar] = []

    months: list[str] = [
      "Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    for i in range(12):
      section = Section("Total", monthly_net_change[i], QtGui.QColor(0, 0, 0))

      section.percentage = abs(section.value) / absolute_net_change

      if minimum >= 0:
        section.start = 0
        section.end = section.value / maximum

      else:
        if section.value >= 0:
          section.start = minimum / (minimum - maximum)
          section.end = (section.value - minimum) / (maximum - minimum)
        else:
          section.start = (section.value - minimum) / (maximum - minimum)
          section.end = minimum / (minimum - maximum)
      
      bars.append(Bar(months[i], [section]))

    return bars

  def set_data(self, model: Model) -> None:
    self.income_pie_chart.set_data(self.convert_records_to_sectors(model.categories, model.income.data))
    self.expense_pie_chart.set_data(self.convert_records_to_sectors(model.categories, model.expenses.data))

    income_bars = self.convert_records_to_bars(model.categories, model.income.data)
    expense_bars = self.convert_records_to_bars(model.categories, model.expenses.data)

    self.income_bar_chart.set_data(income_bars)
    self.expense_bar_chart.set_data(expense_bars)

    self.net_change_bar_chart.bar_chart_renderer.set_data(self.calculate_net_change(income_bars, expense_bars))

class View(qfw.FluentWindow):
  def __init__(self) -> None:
    super().__init__()

    self.setWindowTitle("Expense Tracker")

    self.stackedWidget.setAnimationEnabled(False)

    # Create views
    self.categories_view = CategoriesView()
    self.income_view = RecordsView("Income")
    self.expenses_view = RecordsView("Expenses")
    self.statistics_view = StatisticsView()

    # Add views to stacked widget
    self.categories_view.setObjectName("categories-view")
    self.income_view.setObjectName("income-view")
    self.expenses_view.setObjectName("expenses-view")
    self.statistics_view.setObjectName("statistics-view")

    self.addSubInterface(self.categories_view, qfw.FluentIcon.TILES,"Categories")    
    self.addSubInterface(self.income_view, qfw.FluentIcon.DICTIONARY, "Income")
    self.addSubInterface(self.expenses_view, qfw.FluentIcon.DICTIONARY, "Expenses")
    self.addSubInterface(self.statistics_view, qfw.FluentIcon.MARKET, "Statistics")

  def set_view(self, ui) -> None:
    self.stackedWidget.setCurrentIndex(ui.value)
