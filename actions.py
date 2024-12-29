import os
import shutil
import subprocess
import sys
import pwd
import grp

PROCESS_BASE_PATH = '/home/deploy/basket/process'
CLEANERS_BASE_PATH = '/home/deploy/basket/templates/cleaners'
APACHE_SITES_PATH = '/etc/apache2/sites-'

def getProcessFolder(folder_name):
  return os.path.join(PROCESS_BASE_PATH, folder_name)

def getCleanerFilePath(project_type):
  return os.path.join(CLEANERS_BASE_PATH, f"{project_type}.log")

def getApacheConfigPaths(config_name):
  return {
    "enabled": os.path.join(APACHE_SITES_PATH + 'enabled', config_name),
    "available": os.path.join(APACHE_SITES_PATH + 'available', config_name)
  }

def loadConfig(processFolder):
  configPath = os.path.join(processFolder, 'config.txt')
  with open(configPath, 'r') as file:
    configData = {
      "repoUrl": file.readline().strip(),
      "repoBranch": file.readline().strip(),
      "apacheConfigName": file.readline().strip(),
      "projectPullFolder": file.readline().strip() or f'/home/deploy/repos/{file.readline().strip()}',
      "projectDeployFolder": file.readline().strip(),
      "dbUser": file.readline().strip(),
      "dbName": file.readline().strip(),
      "projectType": file.readline().strip().lower()
    }
  return configData

def cloneOrUpdateRepo(repoUrl, repoBranch, projectPullFolder):
  uid = pwd.getpwnam('deploy').pw_uid
  gid = grp.getgrnam('deploy').gr_gid

  if not os.path.exists(projectPullFolder):
    os.makedirs(projectPullFolder)
  os.chown(projectPullFolder, uid, gid)
  os.chmod(projectPullFolder, 0o755)

  if os.path.exists(os.path.join(projectPullFolder, '.git')):
    gitCommand = ['git', '-C', projectPullFolder, 'pull', 'origin', repoBranch]
  else:
    gitCommand = ['git', 'clone', '-b', repoBranch, repoUrl, projectPullFolder]

  def preexecFn():
    os.setgid(gid)
    os.setuid(uid)

  subprocess.run(gitCommand, preexec_fn=preexecFn, check=True)

def runComposerInstall(projectPullFolder, projectType):
  if projectType == 'laravel':
    subprocess.run(['sudo', '-u', 'deploy', 'composer', 'install', '--working-dir', f"{projectPullFolder}/laravel"], check=True)
  else:
    subprocess.run(['sudo', '-u', 'deploy', 'composer', 'install', '--working-dir', projectPullFolder], check=True)

def cleanDeploymentFolder(projectDeployFolder, projectType):
  cleanerFilePath = getCleanerFilePath(projectType)
  if os.path.exists(cleanerFilePath):
    with open(cleanerFilePath, 'r') as cleanerFile:
      for line in cleanerFile:
        relative_path = line.strip()

        pathToDelete = os.path.join(projectDeployFolder, relative_path)
        if os.path.isfile(pathToDelete) or os.path.isfile(f"{pathToDelete}/"):
          os.remove(pathToDelete)
        elif os.path.isdir(pathToDelete) or os.path.isdir(pathToDelete.rstrip('/')):
          shutil.rmtree(pathToDelete.rstrip('/'))

def syncProjectFiles(projectPullFolder, projectDeployFolder, projectType, exclude=None):
  exclude = exclude or []

  if not os.path.exists(projectDeployFolder):
    os.makedirs(projectDeployFolder)

  if projectType == 'laravel':
    rsync_command = ['rsync', '-a'] + [f"--exclude={item}" for item in exclude] + [f"{projectPullFolder}/laravel", projectDeployFolder]
  else:
    rsync_command = ['rsync', '-a'] + [f"--exclude={item}" for item in exclude] + [f"{projectPullFolder}/", projectDeployFolder]
  subprocess.run(rsync_command, check=True)

def setupEnvironmentFile(processFolder, projectDeployFolder, projectType):
  if projectType == 'laravel':
    envFilePath = os.path.join(projectDeployFolder, 'laravel', '.env')
  else:
    envFilePath = os.path.join(projectDeployFolder, '.env')

  if not os.path.exists(envFilePath):
    shutil.copyfile(os.path.join(processFolder, '.env'), envFilePath)

    if projectType == 'laravel':
      laravelFolder = os.path.join(projectDeployFolder, 'laravel')
      os.chdir(laravelFolder)
      subprocess.run(['php', 'artisan', 'key:generate'], check=True)

      print("Laravel application key generated.")

    return False;

def runScriptDumpSql(projectDeployFolder, dbName):
  envFilePath = os.path.join(projectDeployFolder, '.env')

  if os.path.exists(envFilePath):
    sqlScriptPath = os.path.join(projectDeployFolder, '.lando', 'database', 'dump.sql.gz')
    sqlDumpFolder = os.path.join(projectDeployFolder, '.lando', 'database')

    if os.path.exists(sqlScriptPath):
      os.chdir(sqlDumpFolder)
      try:
        print(f"Importing database '{dbName}' from '{sqlScriptPath}'...")
        subprocess.run(
          f"zcat {sqlScriptPath} | mysql {dbName}",
          shell=True,
          check=True
        )
        print("Database imported successfully.")
      except subprocess.CalledProcessError as e:
        print(f"Error during database import: {e}")
    else:
      print(f"Error: The dump file '{sqlScriptPath}' does not exist.")

def runSqlScript(processFolder, projectDeployFolder, dbUser):
  sqlScriptPath = os.path.join(processFolder, 'mysql.sql')
  subprocess.run(f'mysql -u root < {sqlScriptPath}', shell=True, cwd=projectDeployFolder, check=True)

def runDrushCommands(projectDeployFolder):
  settingsPath = os.path.join(projectDeployFolder, 'web', 'sites', 'default', 'settings.php')

  if os.path.isfile(settingsPath):
    print("Running Drush commands to synchronize database and configurations")

    try:
      subprocess.run(['./vendor/bin/drush', 'cim', '-y'], cwd=projectDeployFolder, check=True)
    except subprocess.CalledProcessError as e:
      print(f"Warning: 'drush cim' failed with error: {e}. Continuing with the process.")

    try:
      subprocess.run(['./vendor/bin/drush', 'cr'], cwd=projectDeployFolder, check=True)
    except subprocess.CalledProcessError as e:
      print(f"Warning: 'drush cr' failed with error: {e}. Continuing with the process.")
  else:
    print("settings.php not found. Skipping Drush commands.")

def migrateFresh(projectDeployFolder):
  laravelFolder = os.path.join(projectDeployFolder, 'laravel')
  os.chdir(laravelFolder)
  subprocess.run(['php', 'artisan', 'migrate:fresh'], check=True)

  print("Laravel migrations fresh executed.")

def changeOwnershipToWebServerUser(projectDeployFolder):
  try:
    subprocess.run(['chown', '-R', 'www-data:www-data', projectDeployFolder], check=True)
    print(f"Ownership of {projectDeployFolder} changed to www-data:www-data")
  except subprocess.CalledProcessError as e:
    print(f"Error changing ownership for {projectDeployFolder}: {e}")
    sys.exit(1)

def configureApache(processFolder, apacheConfigName):
  apachePaths = getApacheConfigPaths(apacheConfigName)

  if not os.path.exists(apachePaths["enabled"]):
    if not os.path.exists(apachePaths["available"]) and os.path.exists(os.path.join(processFolder, apacheConfigName)):
      shutil.copyfile(os.path.join(processFolder, apacheConfigName), apachePaths["available"])
    subprocess.run(['a2ensite', apacheConfigName], check=True)

def reloadApache():
  subprocess.run(['systemctl', 'reload', 'apache2'], check=True)

def deleteProjectPullFolder(projectPullFolder):
  if os.path.exists(projectPullFolder):
    shutil.rmtree(projectPullFolder)
    print(f"Folder {projectPullFolder} has been deleted.")

def setupProject(processFolder):
  # Load configuration
  config = loadConfig(processFolder)

  # Step-by-step setup process
  cloneOrUpdateRepo(config["repoUrl"], config["repoBranch"], config["projectPullFolder"])
  runComposerInstall(config["projectPullFolder"], config["projectType"])
  cleanDeploymentFolder(config["projectDeployFolder"], config["projectType"])
  syncProjectFiles(config["projectPullFolder"], config["projectDeployFolder"], config["projectType"], ['.git', '.gitignore', 'README.md', 'workspace.code-workspace'])
  wasEnv = setupEnvironmentFile(processFolder, config["projectDeployFolder"], config["projectType"])
  setupEnvironmentFile(processFolder, config["projectDeployFolder"], config["projectType"])
  runSqlScript(processFolder, config["projectDeployFolder"], config["dbUser"])

  print(wasEnv)

  if wasEnv == False and config["projectType"] == "drupal":
    runScriptDumpSql(config["projectDeployFolder"], config["dbName"])

  # Run Drush commands after syncing files if projectType is drupal
  if config["projectType"] == "drupal":
    runDrushCommands(config["projectDeployFolder"])

  # Migrate fresh if projectType is Laravel
  if config["projectType"] == 'laravel':
    migrateFresh(config["projectDeployFolder"])

  changeOwnershipToWebServerUser(config["projectDeployFolder"])

  configureApache(processFolder, config["apacheConfigName"])
  reloadApache()

  # Delete the projectPullFolder after setup
  deleteProjectPullFolder(config["projectPullFolder"])

# Check if the script is executed with the proper arguments
if len(sys.argv) != 2:
  print("Usage: python script.py <process_folder_name>")
  sys.exit(1)

# Define the process folder based on the input parameter
processFolderName = sys.argv[1]
processFolder = getProcessFolder(processFolderName)

# Start setup process
setupProject(processFolder)
