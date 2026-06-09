from collections.abc import Callable

from typing import TypeVar, Generic

# See Pezzza's Work: The magic container
# https://www.youtube.com/watch?v=L4xOCvELWlU

T = TypeVar('T')

class Container(Generic[T]):
  def __init__(self) -> None:
    # map id to position in data array
    self.id_to_index: list[int] = []
    # map position in data array to id
    self.index_to_id: list[int] = []
    # data container
    self.data: list[T] = []
  
  def add(self, element: T) -> int:
    new_index = len(self.data)
    new_id = len(self.id_to_index)
    
    self.id_to_index.append(new_index)
    self.index_to_id.append(new_id)
    self.data.append(element)

    return new_id

  def remove(self, element_id: int) -> None:
    # overwrite removed element with last elemment 
    element_index = self.id_to_index[element_id]
    last_index = len(self.data) - 1
    last_id = self.index_to_id[last_index]

    self.id_to_index[last_id] = element_index
    self.index_to_id[element_index] = last_id
    self.data[element_index] = self.data[last_index]
    
    # remove last element
    self.id_to_index[element_id] = -1
    self.index_to_id.pop()    
    self.data.pop()
  
  def get(self, id) -> T:
    return self.data[self.id_to_index[id]]
  
  def get_elements(self) -> list[T]:
    return self.data.copy()

  def set(self, id, element: T) -> None:
    self.data[self.id_to_index[id]] = element
  
  def filter(self, condition: Callable[[T], bool]) -> list[T]:
    result: list[T] = []
    for element in self.data:
      if condition(element):
        result.append(element)
    return result