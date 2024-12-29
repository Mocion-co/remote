class Drupal10(Base):
  def __init__(self, site_name="My Drupal Site", theme="olivero",
         host="localhost", port=3306, database="drupal",
         user="drupal", password=""):
    """
    Constructor for Drupal10 class

    Args:
      site_name (str): Name of the Drupal site
      theme (str): Default theme
      host (str): Database host
      port (int): Database port
      database (str): Database name
      user (str): Database user
      password (str): Database password
    """
    # Call parent constructor
    super().__init__(host, port, database, user, password)

    # Drupal specific attributes
    self.site_name = site_name
    self.theme = theme
    self.version = "10.0"

  def get_site_info(self):
    """Returns the Drupal site information"""
    return {
      "site_name": self.site_name,
      "theme": self.theme,
      "version": self.version
    }

  def get_full_info(self):
    """Returns both connection and site information"""
    return {
      **self.get_connection_info(),
      **self.get_site_info()
    }
