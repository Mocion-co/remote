
class Base:
  def __init__(self, www_folder="/var/www", repository='', domain="test.com", subdomain=".", branch="main"):
    self.www_folder = www_folder
    self.repository = repository
    self.domain = domain
    self.subdomain = subdomain
    self.branch = branch

  def deploy(self):
    return True
