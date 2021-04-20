debug=False
import sys
import select
from enum import Enum
class RoadSurface(Enum):
  """
  Road surfaces supported by theTacxTrainerControl2 NEO road feel feature
  """
  SIMULATION_OFF = 0
  CONCRETE_PLATES = 1
  CATTLE_GRID = 2
  COBBLESTONES_HARD = 3
  COBBLESTONES_SOFT = 4
  BRICK_ROAD = 5
  OFF_ROAD = 6
  GRAVEL = 7
  ICE = 8
  WOODEN_BOARDS = 9

class from_tacx:
  def __init__(self):
    self.distance=0
    self.pdistance=0
    self.speed=0
    self.new_data=False

class guivars:
  def __init__(self):
    self.w20=None
    self.w21=None
    self.w22=None
    self.w23=None
    self.w24=None
    self.w25=None
    self.w26=None
    self.cvs=None
    self.cvs_width=0
    self.cvs_height=0
    self.minlon=0
    self.minlat=0
    self.loladmax=0.0
    self.curpos=(0,0)
    self.mark
    self.curval=0

def init_globs():
    global running,pauze,offset,tacx_data,man_roadsurface
    pauze=False
    running=False
    offset=0
    tacx_data=from_tacx()
    man_roadsurface=False
    man_roadsurface_type=RoadSurface.SIMULATION_OFF
    man_roadsurface_intensity=20

def pri_dbg(s):
  if (debug):
    print(s)

def heardEnter():
  i,o,e = select.select([sys.stdin],[],[],0.0001)
  for s in i:
    if s == sys.stdin:
      input = sys.stdin.readline()
      return True
    return False
