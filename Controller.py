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

    self.view.records_view.add.connect(self.records_view_add)
    self.view.records_view.edit.connect(self.records_view_edit)
    self.view.records_view.remove.connect(self.records_view_remove)
  
  def view_changed(self, index: int) -> None:
    match index:
      case View.UI.CATEGORIES.value:
        self.view.categories_view.set_data(self.model.categories)
      case View.UI.RECORDS.value:
        self.view.records_view.set_data(self.model)
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
    dialog = qfw.Dialog("Remove Category", "Are you sure you want to remove the selected category?", self.view)

    if not dialog.exec():
      return
    
    self.model.categories.remove(category_id)

    self.view.categories_view.set_data(self.model.categories)
  
  def records_view_add(self) -> None:
    print("add record")

    dialog = View.CreateRecordDialog(self.view, self.model.categories)

    if not dialog.exec():
      return
    
    self.model.records.add(
      Model.Record(
        dialog.get_category_id(),
        dialog.amount_field.value(),
        dialog.date_field.getDate().toString("yyyy-MM-dd"),
        dialog.description_field.text()
      )
    )

    self.view.records_view.set_data(self.model)
  
  def records_view_edit(self, record_id: int) -> None:
    dialog = View.EditRecordDialog(self.view, record_id, self.model)

    if not dialog.exec():
      return
    
    self.model.records.set(
      record_id,
      Model.Record(
        dialog.get_category_id(),
        dialog.amount_field.value(),
        dialog.date_field.getDate().toString("yyyy-MM-dd"),
        dialog.description_field.text()
      )
    )

    self.view.records_view.set_data(self.model)
  
  def records_view_remove(self, record_id: int) -> None:
    dialog = qfw.Dialog("Remove Record", "Are you sure you want to remove the selected record?", self.view)

    if not dialog.exec():
      return
    
    self.model.records.remove(record_id)

    self.view.records_view.set_data(self.model)