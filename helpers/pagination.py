import math

class Pagination:
  def __init__(self, page = 1, size = 20):
    """
    Args:
        page (int, optional): page number. Defaults to 1.
        size (int, optional): size of data rows per page. Defaults to 20.
    """
    self.itemPerPage = size
    self.page = page
  
  def get_offset(self):
    """returns the index of required data

    Returns:
        number: the index of required data
    """
    return (self.page - 1) * self.itemPerPage

  def get_item_per_page(self):
    """returns the no of data items/rows per page

    Returns:
        number: the no of data items/rows per page
    """
    return self.itemPerPage

  def get_page_nos(self, totalData):
    """
      When supplied the total available data, returns all information related to pages,
      according to the page size and current page number.

    Args:
        totalData (number): The length (no. of rows) of the data, that is to be paginated

    Returns:
        dictonary: returns information related to page. keys are self, first, last, next, previous
                   self (number): the current page number,
                   first (number): the first possible page number,
                   last (number): the last possible page number,
                   next (number): the next page number,
                   previous (number): the previous page number
    """
    # necessary with page and page size convention
    totalPages = math.ceil(totalData / self.itemPerPage)
    first = 1
    last = totalPages
    next = self.page + 1 if self.page < totalPages else 1
    previous = self.page - 1 if self.page > 1 else last
    return { "self": self.page, "first":first, "last":last, "next":next, "previous":previous }