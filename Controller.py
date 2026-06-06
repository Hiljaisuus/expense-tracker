import atexit
import pickle
import sys

from PySide6.QtWidgets import QApplication

from Model import Model
from View import View, UI

class Controller:
  def __init__(self) -> None:
    application = QApplication()

    self.view = View()

    self.view.set_view(UI.STATISTICS)

    self.view.show()

    sys.exit(application.exec())