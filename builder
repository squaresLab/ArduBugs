#!/bin/bash
DIR_SRC=/opt/ardupilot
DIR_BIN="${DIR_SRC}/build/sitl/bin"
mkdir -p "${DIR_BIN}"

function build_make() {
  case $1 in
    rover)
      (cd APMrover2 && make sitl && mv APMrover2.elf "${DIR_BIN}/ardurover");;
    plane)
      (cd ArduPlane && make sitl && mv ArduPlane.elf "${DIR_BIN}/arduplane");;
    copter)
      (cd ArduCopter && make sitl && mv ArduCopter.elf "${DIR_BIN}/arducopter");;
    all|"")
      build_make rover && build_make plane && build_make copter
  esac
}

function build_waf() {
  case $1 in
    rover) ./waf rover;;
    plane) ./waf plane;;
    copter) ./waf copter;;
    all|"") ./waf build;;
  esac
}

function build() {
  pushd "${DIR_SRC}"
  if [ -f waf ]; then
    build_waf $1
  else
    build_make $1
  fi
}

build $1
