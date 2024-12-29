from .base import Base

class Drupal10(Base):
  def __init__(self, www_folder="/var/www", repository='', domain="test.com", subdomain=".", branch="main"):

    # Call parent constructor
    super().__init__(www_folder, repository, domain, subdomain, branch)

  def deploy(self):
    print(self.www_folder)
    print(self.repository)
    print(self.domain)
    print(self.subdomain)
    print(self.branch)

    return True
