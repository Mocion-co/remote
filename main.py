import argparse
import os

def main():
  parser = argparse.ArgumentParser(description="Project configuration automation.")
  parser.add_argument('--type', type=str, default='drupal', help="Project type (drupal by default).")
  parser.add_argument('--domain', type=str, required=True, help="Project domain.")
  parser.add_argument('--repository', type=str, required=True, help="Project repository.")
  parser.add_argument('--branch', type=str, required=True, help="Repository branch.")

  args = parser.parse_args()

  # copyAndModifyFiles(args.projectType, args.environment, args.domain, args.subdomain, args.repository, args.branch)

if __name__ == "__main__":
  main()
