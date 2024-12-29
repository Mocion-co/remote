import argparse
import os
from dotenv import load_dotenv
from recipes.drupal10 import Drupal10

load_dotenv()

def main():
  parser = argparse.ArgumentParser(description="Project configuration automation.")
  parser.add_argument('--type', type=str, default='drupal10', help="Project type (drupal10 by default).")
  parser.add_argument('--domain', type=str, required=True, help="Project domain.")
  parser.add_argument('--subdomain', type=str, required=True, help="Project subdomain.")
  parser.add_argument('--repository', type=str, required=True, help="Project repository.")
  parser.add_argument('--branch', type=str, required=True, help="Repository branch.")

  args = parser.parse_args()

  project = None

  if args.type == 'drupal10':
    project = Drupal10(os.getenv('WWW_FOLDER'), args.repository, args.domain, args.subdomain, args.branch)

  if project is not None:
    project.deploy()

if __name__ == "__main__":
  main()

# python3 main.py --type drupal10 --domain test.com --subdomain www --repository 'git@github.com:Mocion-co/tuasistentejuridico.git' --branch main
