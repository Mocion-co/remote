#!/bin/bash

print_hi() {
  echo "  _  _  __   _  _  _ ____  ____    ____  ____  _  _   __  ____  ____  _  "
  echo " ( \/ )/  \ / )( \(/(  _ \(  __)  (  _ \(  __)( \/ ) /  \(_  _)(  __)/ \ "
  echo "  )  /(  O )) \/ (   )   / ) _)    )   / ) _) / \/ \(  O ) )(   ) _) \_/ "
  echo " (__/  \__/ \____/  (__\_)(____)  (__\_)(____)\_)(_/ \__/ (__) (____)(_) "
  echo ""
}

install() {
  echo $(python3 --version)
  echo $(python3 --user deployer -m venv .venv)
  echo $(. .venv/bin/activate)
  echo $(pip3 install --upgrade pip --user deployer)
  echo $(pip3 install --user deployer -r requirements.txt)
}

print_hi
install
