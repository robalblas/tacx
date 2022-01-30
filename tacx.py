#!/usr/bin/python3
######################################################################################
# Main program
#   . Get options
#   . Start gui
######################################################################################
#
import sys
import os
from os import path
import getopt
import tacx_misc
from gtacx import setup_gui

def main(argv):
  global cvs
  tacx_misc.init_globs()          # Call only once
  start_dist=0
  fn_wtp=None
  fn_gpx=None
  simulate=False
  device_address = "C2:9D:1D:49:A9:C7"
  cvs_width=500
  cvs_height=500
  cvs=None

  try:
    opts, args = getopt.getopt(argv,"hSg:w:s:a:x:y:")
  except getopt.GetoptError:
    print("ERR: -g <fn_gpx> [-s <start_dist in meters>] [-w <wegfile>] [-a <trainer_address]")
    sys.exit(2)

  #get commandline options
  for opt, arg in opts:
    if opt == '-h':
      print("options: -g <gpx_file> [-s <start_dist in meters>] [-w <roadsurface_file>] [-a <trainer_address] [-S]")
      sys.exit()
    elif opt in ("-a"):
      device_address = arg
    elif opt in ("-g"):
      fn_gpx = arg
    elif opt in ("-s"):
      start_dist = int(arg)
    elif opt in ("-w"):
      fn_wtp = arg
    elif opt in ("-S"):
      simulate=True
    elif opt in ("-x"):
      cvs_width=int(arg)
      cvs_height=cvs_width
    elif opt in ("-y"):
      cvs_height=int(arg)
      cvs_width=cvs_height

  print("Trainer-address=" + device_address)
  if (fn_gpx != None):
    print("gpx-file=" + fn_gpx + "  start=" + str(start_dist) +  " meter  road-file=" + str(fn_wtp))

  if ((fn_gpx) and (path.exists(fn_gpx))):
    print("")
  elif (fn_gpx!=None):
    print("Not found: " + fn_gpx)
    sys.exit(2)

  if ((fn_wtp==None) or (path.exists(fn_wtp))):
    print("")
  else:
    print("Not found: " + fn_wtp)
    sys.exit(2)

  print("devadr=" + device_address)

  setup_gui(device_address,fn_gpx,fn_wtp,start_dist,simulate,cvs_width,cvs_height)


if __name__ == "__main__":
  main(sys.argv[1:])
