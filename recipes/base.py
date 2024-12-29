import os
import random
import string

class Base:
  def __init__(self, www_folder="/var/www", repository='', domain="test.com", branch="main"):
    self.www_folder = www_folder
    self.repository = repository
    self.domain = domain
    self.branch = branch

  def generatePassword(self, length=12):
    safe_chars = (
      string.ascii_letters + string.digits +
      "!#$%&()*+,-./:;<=>?@[]^_`{|}~"
    )
    return ''.join(random.choice(safe_chars) for _ in range(length))

  def prepareFolders(self):
    if self.branch == 'main':
      directory = self.www_folder + '/' + self.domain + '/www'
    else:
      directory = self.www_folder + '/' + self.domain + '/' + self.branch

    if not os.path.exists(directory):
      os.makedirs(directory)

  def deploy(self):
    return True
