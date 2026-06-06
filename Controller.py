import atexit
import pickle
import sys

from PySide6.QtWidgets import QApplication

from Model import Model
from View import View, UI

class Controller:
  def __init__(self) -> None:
    self.model = pickle.load(open("model.pkl", "rb"))
    
    atexit.register(self.save_model)
    
    application = QApplication()

    self.view = View()

    self.view.set_view(UI.STATISTICS)

    self.view.show()

    sys.exit(application.exec())

  def save_model(self):
    with open("model.pkl", "wb") as file:
      pickle.dump(self.model, file, 5)