import atexit
import pickle
import sys

from PySide6 import QtCore, QtGui, QtWidgets

import qfluentwidgets as qfw

import Model, View

class Controller:
  def __init__(self) -> None:
    self.model: Model.Model = pickle.load(open("model.pkl", "rb"))
    
    atexit.register(self.save_model)
    
    application = QtWidgets.QApplication()
    application.setAttribute(QtCore.Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    self.view = View.View()

    self.wire()

    self.view.set_view(View.UI.STATISTICS)
    self.view.statistics_view.set_data(self.model)

    self.view.show()

    sys.exit(application.exec())
  
  def save_model(self):
    with open("model.pkl", "wb") as file:
      pickle.dump(self.model, file, 5)
  
  def wire(self) -> None:
    self.view.stackedWidget.currentChanged.connect(self.view_changed)

    self.view.categories_view.add.connect(self.categories_view_add)
    self.view.categories_view.edit.connect(self.categories_view_edit)
    self.view.categories_view.remove.connect(self.categories_view_remove)

    self.view.income_view.add.connect(self.income_view_add)
    self.view.income_view.edit.connect(self.income_view_edit)
    self.view.income_view.remove.connect(self.income_view_remove)

    self.view.expenses_view.add.connect(self.expenses_view_add)
    self.view.expenses_view.edit.connect(self.expenses_view_edit)
    self.view.expenses_view.remove.connect(self.expenses_view_remove)
  
  def view_changed(self, index: int) -> None:
    match index:
      case View.UI.CATEGORIES.value:
        self.view.categories_view.set_data(self.model.categories)
      case View.UI.INCOME.value:
        self.view.income_view.set_data(self.model.categories, self.model.income)
      case View.UI.EXPENSES.value:
        self.view.expenses_view.set_data(self.model.categories, self.model.expenses)
      case View.UI.STATISTICS.value:
        self.view.statistics_view.set_data(self.model)

  def categories_view_add(self) -> None:
    dialog = View.CreateCategoryDialog(self.view)

    if not dialog.exec():
      return
    
    self.model.categories.add(
      Model.Category(
        dialog.name_field.text(),
        dialog.color_field.color
      )
    )

    self.view.categories_view.set_data(self.model.categories)
  
  def categories_view_edit(self, category_id: int) -> None:
    num_categories = self.model.categories.size()

    if num_categories == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No categories exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return

    dialog = View.EditCategoryDialog(self.view, category_id, self.model.categories)

    if not dialog.exec():
      return
    
    self.model.categories.set(
      category_id,
      Model.Category(
        dialog.name_field.text(),
        dialog.color_field.color
      )
    )

    self.view.categories_view.set_data(self.model.categories)
  
  def categories_view_remove(self, category_id: int) -> None:
    num_categories = self.model.categories.size()

    match num_categories:
      case 0:
        qfw.InfoBar.error(
          title="Error",
          content="No categories exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
        return
      case 1:
        qfw.InfoBar.error(
          title="Error",
          content="Cannot remove only remaining category.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
        return

    dialog = View.RemoveCategoryDialog(self.view, category_id, self.model.categories)

    if not dialog.exec():
      return
    
    replacement_category = dialog.get_category_id()
    
    for record in self.model.expenses.data:
      if record.category == category_id:
        record.category = replacement_category
    
    self.model.categories.remove(category_id)

    self.view.categories_view.set_data(self.model.categories)
  
  def income_view_add(self) -> None:
    num_categories = self.model.categories.size()

    if num_categories == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No categories exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return
    
    dialog = View.CreateRecordDialog(self.view, self.model.categories)

    if not dialog.exec():
      return
    
    self.model.income.add(
      Model.Record(
        dialog.get_category_id(),
        dialog.amount_field.value(),
        dialog.date_field.getDate().toString("yyyy-MM-dd"),
        dialog.description_field.text()
      )
    )

    self.view.income_view.set_data(self.model.categories, self.model.income)
  
  def income_view_edit(self, record_id: int) -> None:
    num_records = self.model.categories.size()

    if num_records == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No records exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return
    
    dialog = View.EditRecordDialog(self.view, record_id, self.model.categories, self.model.income)

    if not dialog.exec():
      return
    
    self.model.income.set(
      record_id,
      Model.Record(
        dialog.get_category_id(),
        dialog.amount_field.value(),
        dialog.date_field.getDate().toString("yyyy-MM-dd"),
        dialog.description_field.text()
      )
    )

    self.view.income_view.set_data(self.model.categories, self.model.income)
  
  def income_view_remove(self, record_id: int) -> None:
    num_records = self.model.categories.size()

    if num_records == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No records exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return
    
    dialog = View.RemoveRecordDialog(self.view)

    if not dialog.exec():
      return
    
    self.model.income.remove(record_id)

    self.view.income_view.set_data(self.model.categories, self.model.income)
  
  def expenses_view_add(self) -> None:
    num_categories = self.model.categories.size()

    if num_categories == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No categories exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return
    
    dialog = View.CreateRecordDialog(self.view, self.model.categories)

    if not dialog.exec():
      return
    
    self.model.expenses.add(
      Model.Record(
        dialog.get_category_id(),
        dialog.amount_field.value(),
        dialog.date_field.getDate().toString("yyyy-MM-dd"),
        dialog.description_field.text()
      )
    )

    self.view.expenses_view.set_data(self.model.categories, self.model.expenses)
  
  def expenses_view_edit(self, record_id: int) -> None:
    num_records = self.model.categories.size()

    if num_records == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No records exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return
    
    dialog = View.EditRecordDialog(self.view, record_id, self.model.categories, self.model.expenses)

    if not dialog.exec():
      return
    
    self.model.expenses.set(
      record_id,
      Model.Record(
        dialog.get_category_id(),
        dialog.amount_field.value(),
        dialog.date_field.getDate().toString("yyyy-MM-dd"),
        dialog.description_field.text()
      )
    )

    self.view.expenses_view.set_data(self.model.categories, self.model.expenses)
  
  def expenses_view_remove(self, record_id: int) -> None:
    num_records = self.model.categories.size()

    if num_records == 0:
      qfw.InfoBar.error(
          title="Error",
          content="No records exist.",
          orient=QtCore.Qt.Orientation.Vertical,
          isClosable=True,
          position=qfw.InfoBarPosition.BOTTOM_RIGHT,
          duration=4000,
          parent=self.view
        )
      return
    
    dialog = View.RemoveRecordDialog(self.view)

    if not dialog.exec():
      return
    
    self.model.expenses.remove(record_id)

    self.view.expenses_view.set_data(self.model.categories, self.model.expenses)