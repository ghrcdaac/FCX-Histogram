import math

class Pagination:
  def __init__(self, page = 1, size = 20, total_data=None):
    """
    Args:
        page (int, optional): page number. Defaults to 1.
        size (int, optional): size of data rows per page. Defaults to 20.
        total_data (int): total no of rows in the data, that needs to be paginated
    """
    self.itemPerPage = int(size)
    self.page = int(page)
    self.totalData = int(total_data)
  
  def get_offset(self):
    """returns the start index (offset) of required data

    Returns:
        number: the index of required data
    """
    return (self.page - 1) * self.itemPerPage

  def get_offset_end(self):
    """
      based on the page number given, the data content per page and total no of data
      in the constructor, return the end index (offset) of the required data
    """
    startOffsetIndex = (self.page - 1) * self.itemPerPage
    # handle if the requested page is the end page. i.e. end index is start offset index + rem data.
    lastPage = math.ceil(self.totalData / self.itemPerPage)
    if(self.page == lastPage):
      # calculate the remaining items in last page.
      remItems = self.totalData % self.itemPerPage
      # add it to the start offset index of this last page.
      return startOffsetIndex + remItems
    return startOffsetIndex + self.itemPerPage

  def get_item_per_page(self):
    """returns the no of data items/rows per page

    Returns:
        number: the no of data items/rows per page
    """
    return self.itemPerPage

  def get_page_nos(self):
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
    totalPages = math.ceil(self.totalData / self.itemPerPage)
    first = 1
    last = totalPages
    next = self.page + 1 if self.page < totalPages else 1
    previous = self.page - 1 if self.page > 1 else last
    return { "self": self.page, "first":first, "last":last, "next":next, "previous":previous }