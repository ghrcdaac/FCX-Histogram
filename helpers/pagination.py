import math

class Pagination:
  def __init__(self, page = 1, size = 20):
    self.itemPerPage = size
    self.page = page
  
  def getOffset(self):
    return (self.page - 1) * self.itemPerPage

  def getItemPerPage(self):
    return self.itemPerPage

  def getPageOffsets(self, totalData):
    # necessary with offset and limit convention
    # not necessary with page and page size convention
    totalPages = math.ceil(totalData / self.itemPerPage)
    first = 0
    last = (totalPages - 1) * self.itemPerPage
    next = self.page * self.itemPerPage if self.page < totalPages else 0
    previous = (self.page - 2) * self.itemPerPage if self.page > 1 else last
    self = self.getOffset()
    return { self, first, last, next, previous }
  
  def getPageNos(self, totalData):
    # necessary with page and page size convention
    totalPages = math.ceil(totalData / self.itemPerPage)
    first = 1
    last = totalPages
    next = self.page + 1 if self.page < totalPages else 1
    previous = self.page - 1 if self.page > 1 else last
    self = self.page
    return { self, first, last, next, previous }