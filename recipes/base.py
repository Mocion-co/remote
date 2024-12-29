
class Base:
  def __init__(self, host="localhost", port=3306, database="mydatabase", user="root", password=""):
    """
    Constructor for Base class

    Args:
      host (str): Database host
      port (int): Database port
      database (str): Database name
      user (str): Database user
      password (str): Database password
    """
    self.host = host
    self.port = port
    self.database = database
    self.user = user
    self.password = password

  def get_connection_info(self):
    """Returns the connection information"""
    return {
      "host": self.host,
      "port": self.port,
      "database": self.database,
      "user": self.user
    }
