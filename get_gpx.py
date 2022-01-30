######################################################################################
# gpx and road type related functions
######################################################################################
#
import os.path
from os import path

from enum import Enum
import math

import gpxpy
import gpxpy.gpx

import tacx_misc
from tacx_misc import pri_dbg
from tacx_misc import RoadSurface

########## Track point including road type ##########
class punt:
  def __init__(self):
    self.lon=0.
    self.lat=0.
    self.ele=0.
    self.dist=0.
    self.slope=0.
    self.RoadSurface=RoadSurface.SIMULATION_OFF
    self.RoadSurface_intensity=0
    self.pos_valid=True
    self.end_track=False
    self.next=None
    self.prev=None

class punten:
  def __init__(self, nodes=None):
    self.head = None
    self.dist=0

  def __iter__(self):
    node = self.head
    while node is not None:
        yield node
        node = node.next

########## set of points for one road type piece
class wpunt:
  def __init__(self):
    self.pa=punt()
    self.pi=punt()
    self.pb=punt()
    self.next=None
    self.prev=None

class wegpunten:
  def __init__(self, nodes=None):
    self.head = None

  def __iter__(self):
    node = self.head
    while node is not None:
      yield node
      node = node.next

# relative distance between pa and pb, return: 0.5 = small distance
def get_dist(pa,pb):
  dist=math.sqrt((pa.lon-pb.lon)**2 + (pa.lat-pb.lat)**2)
  return dist*1000

# Add road types to list-of-gpx points
#   . p1 near pi, search back to pa or pb
#   .             search forward from pa/pb to pb/pa
#   . add road type between pa and pb
def get_trackpart(p1,pa,pb,pi):
  p2=p1
  mdist=0.5
  px=None

  #  search back to pa or pb
  while p2 is not None:
    if (px==None):
      # going back: check if p2 near pa
      if (get_dist(pa,p2) < mdist):
        pri_dbg("START1 " + str(p2.dist))
        px=pb
        break
      # going back: Or check if p2 near pb
      if (get_dist(pb,p2) < mdist):
        pri_dbg("START2 " + str(p2.dist))
        px=pa
        break
    else:
      # p2 near px (=pa or pb)
      if (get_dist(px,p2) < mdist):
        pri_dbg("START3 " + str(p2.dist))
        break
    p2.RoadSurface=pi.RoadSurface
    p2.RoadSurface_intensity=pi.RoadSurface_intensity
    p2 = p2.prev

  #  search forward to px=pb or pa, add RoadSurface type
  while p2 is not None:
    p2.RoadSurface=pi.RoadSurface
    p2.RoadSurface_intensity=pi.RoadSurface_intensity
    if (get_dist(px,p2) < mdist):
      pri_dbg("EINDE3 " + str(p2.dist))
      break
    p2 = p2.next

  return p2

# translate string to RoadSurface
def transl_roadsurface(s):

  if (s=="SIMULATION_OFF"):
    return RoadSurface.SIMULATION_OFF
  elif (s=="CONCRETE_PLATES"):
    return RoadSurface.CONCRETE_PLATES
  elif (s=="CATTLE_GRID"):
    return RoadSurface.CATTLE_GRID
  elif (s=="COBBLESTONES_HARD"):
    return RoadSurface.COBBLESTONES_HARD
  elif (s=="COBBLESTONES_SOFT"):
    return RoadSurface.COBBLESTONES_SOFT
  elif (s=="BRICK_ROAD"):
    return RoadSurface.BRICK_ROAD
  elif (s=="OFF_ROAD"):
    return RoadSurface.OFF_ROAD
  elif (s=="GRAVEL"):
    return RoadSurface.GRAVEL
  elif (s=="ICE"):
    return RoadSurface.ICE
  elif (s=="WOODEN_BOARDS"):
    return RoadSurface.WOODEN_BOARDS
  else:
    return RoadSurface.SIMULATION_OFF

# translate RoadSurface to number (? use enum?)
def transl_roadsurface_int(s):
  if (s==RoadSurface.SIMULATION_OFF):
    return 0
  elif (s==RoadSurface.CONCRETE_PLATES):
    return 1
  elif (s==RoadSurface.CATTLE_GRID):
    return 2
  elif (s==RoadSurface.COBBLESTONES_HARD):
    return 3
  elif (s==RoadSurface.COBBLESTONES_SOFT):
    return 4
  elif (s==RoadSurface.BRICK_ROAD):
    return 5
  elif (s==RoadSurface.OFF_ROAD):
    return 6
  elif (s==RoadSurface.GRAVEL):
    return 7
  elif (s==RoadSurface.ICE):
    return 8
  elif (s==RoadSurface.WOODEN_BOARDS):
    return 9
  else:
    return 0

def transl_int_roadsurface(n):
  if (n==0):
    return RoadSurface.SIMULATION_OFF
  elif (n==1):
    return RoadSurface.CONCRETE_PLATES
  elif (n==2):
    return RoadSurface.CATTLE_GRID
  elif (n==3):
    return RoadSurface.COBBLESTONES_HARD
  elif (n==4):
    return RoadSurface.COBBLESTONES_SOFT
  elif (n==5):
    return RoadSurface.BRICK_ROAD
  elif (n==6):
    return RoadSurface.OFF_ROAD
  elif (n==7):
    return RoadSurface.GRAVEL
  elif (n==8):
    return RoadSurface.ICE
  elif (n==9):
    return RoadSurface.WOODEN_BOARDS
  else:
    return RoadSurface.SIMULATION_OFF

ppunt=None
# create list: add a set of points to define road type
def add_road(wl,pa,pi,pb):
  global ppunt
  npunt=wpunt()
  if (wl.head==None):
    wl.head=npunt

  npunt.pa=pa
  npunt.pi=pi
  npunt.pb=pb
  if (ppunt != None):
    ppunt.next=npunt
    npunt.prev=ppunt
  ppunt=npunt

# add one road point
# format in s1: px=<lat,lon>
# format in s2: rx=<roadtype>[/intensity] 
def get_one_roadpunt(s1,s2,p):
  ss=s1.split('=')
  sss=ss[1].split(',')
  p.lat=float(sss[0])
  p.lon=float(sss[1])

  ss=s2.split('=')
  sss=ss[1].split('/')
  p.RoadSurface=transl_roadsurface(sss[0])
  print(sss)

  if (len(sss)>1):
    p.RoadSurface_intensity=int(sss[1])

def get_one_roadpos(s1,s2,p):
  ss=s1.split('=')
  p.dist=int(ss[1])
  ss=s2.split('=')
  sss=ss[1].split('/')
  p.RoadSurface=transl_roadsurface(sss[0])

  if (len(sss)>1):
    p.RoadSurface_intensity=int(sss[1])

# pa=<lat>,<lon> ra=<wegtype>[/n] pi=... pb=..
def parse_roadtype(fp,weglist):
  while True:    
    line=fp.readline().rstrip(' \n')
    if not line:
      break
    if (line[0]!='#'):
      pri_dbg(line)
      s=line.split(' ')
      pa=punt()
      pi=punt()
      pb=punt()
      if (line[1]=='d'):
        get_one_roadpos(s[0],s[1],pa)   # position
        add_road(weglist,pa,None,None)
      else:
        get_one_roadpunt(s[0],s[1],pa)   # start
        get_one_roadpunt(s[2],s[3],pi)   # halfway
        get_one_roadpunt(s[4],s[5],pb)   # end
        add_road(weglist,pa,pi,pb)

#    print(str(n) + "  dist= " + str(p1.dist) + "   weg= " + str(p1.RoadSurface) + "  dista= " + str(get_dist(pa,p1)) + "  distb= " + str(get_dist(pb,p1)))

# Print all gx-points including calculated slope and road type
def pri_roadinfo(gpx_list,fn):
  fp = open(fn, 'w')
  p=gpx_list.head
  while p is not None:
    fp.write("pos= [{:.5f},{:.5f}] dist= {:.1f} elev= {:.1f} slope= {:.1f} road_int= {:s}  road= {:s}  intensity= {:d}\n" \
      .format(p.lat,p.lon,p.dist,p.ele,p.slope,str((transl_roadsurface_int(p.RoadSurface))),str(p.RoadSurface),p.RoadSurface_intensity))
#       str(get_dist(p.pa,p))))
    p = p.next
  fp.close()


# Add road types defined in wfn to gpxlist, use locations
def add_roadtype1(gpx_list,wfn):
  if (wfn==None):
    return
  
  weglist=wegpunten()
  if (path.exists(wfn)):
    fp = open(wfn, 'r')
  
  parse_roadtype(fp,weglist)
  gpx_list.roadsurface_changes=weglist

  fp.close()
  pri_dbg("Add road type1...")

  p1=None
  for wl in weglist:
    pa=wl.pa
    pi=wl.pi
    pb=wl.pb
    if (pi==None):
      continue

    p1=gpx_list.head
    while p1 is not None:
      dist=get_dist(pi,p1)
      if (dist<0.5):
        pri_dbg("IN "+ str(p1.dist))
        p1=get_trackpart(p1,pa,pb,pi)
        pri_dbg("UIT "+ str(p1.dist))
#      print("  dist= " + str(p1.dist) + "   weg= " + str(p1.RoadSurface) + "  dista= " + str(get_dist(pa,p1)) + "  distb= " + str(get_dist(pb,p1)))
        break
      p1 = p1.next

  # evt. aanvullen tot einde? Moet pb.RoadSurface of pa.RoadSurface gebruiken!
  while p1 is not None:
    if (pb==None):
      p1 = p1.next
      continue
    p1.RoadSurface=pb.RoadSurface
    p1.RoadSurface_intensity=pb.RoadSurface_intensity
    p1 = p1.next

  p1=gpx_list.head
  while p1 is not None:
    if (p1.RoadSurface==0):
      p1.RoadSurface=RoadSurface.SIMULATION_OFF
    p1 = p1.next

# Add road types defined in wfn to gpxlist, use dist
def add_roadtype2(gpx_list,wfn):
  if (wfn==None):
    return
  
  weglist=wegpunten()
  if (path.exists(wfn)):
    fp = open(wfn, 'r')
  
  parse_roadtype(fp,weglist)
  gpx_list.roadsurface_changes=weglist

  fp.close()
  pri_dbg("Add road type2...")

  wl=weglist.head
  if (wl.pb!=None):
    return
  p1=gpx_list.head
  while p1 is not None:
    p1.RoadSurface=wl.pa.RoadSurface;
    p1.RoadSurface_intensity=wl.pa.RoadSurface_intensity
    if ((wl.next!=None) and (p1.dist > wl.next.pa.dist)):
      wl=wl.next
    p1 = p1.next


# Add road types defined in wfn to gpxlist
def add_roadtype(gpx_list,wfn):
  add_roadtype1(gpx_list,wfn)
  add_roadtype2(gpx_list,wfn)

# calc. slope using aerage between 2 points with minimum distance of 'mdist'
def calc_slope(gpx_list):
  mdist=30
  p1=gpx_list.head
  while p1 is not None:
    p2=p1

    # go back for 'mdist/2' meters
    while p2 is not None:
      if (p1.dist-p2.dist > mdist/2):
        break
      p2 = p2.prev

    n=0
    nslope=0.0
    # from here go forward to 'mdist' meters, ending at 'mdist/2'
    while p2 is not None:
      n=n+1
      pn=p2.next
      if (pn!= None):
        slope=(pn.ele-p2.ele)/(pn.dist-p2.dist)*100
        nslope=nslope+slope

      if (p2.dist-p1.dist > mdist/2):
        p1.slope=nslope/n
        break
      p2 = p2.next
    p1 = p1.next

#
def get_gpx(fn,tnr=0):
  fp = open(fn, 'r')
  gpx = gpxpy.parse(fp)
  fp.close()

  gpx_list=punten()
  ppunt=None

  # Get tracknr
  for track in gpx.tracks:
    if (tnr<=0):
      break
    tnr=tnr-1

  # track to gpx_list, calc. tot-dist
  previous_point = None
  distance_from_start=0
  for segment in track.segments:
    for point_no in range(len(segment.points)):
      point = segment.points[point_no]
      npunt=punt()
      if (gpx_list.head==None):
        gpx_list.head=npunt

      npunt.lon=point.longitude
      npunt.lat=point.latitude
      npunt.ele=point.elevation
      if previous_point and point_no > 0:
        distance = point.distance_2d(previous_point)
        distance_from_start += distance
        npunt.dist=distance_from_start
      previous_point = point

      if (ppunt != None):
        ppunt.next=npunt
        npunt.prev=ppunt
      ppunt=npunt
      gpx_list.dist=distance_from_start

  # calc. slope (over 30 meter)
  calc_slope(gpx_list)

  return gpx_list

# goto position in gpx_list closest to 'dist'
# Interpolate between pos. < dist and > dist
# Not found or no list: return empty 'punt'
def goto_pos(gpx_list,dist):
  pn=punt()
  pn.pos_valid=False
  if (gpx_list==None):
    return pn

  ok=False
  pr=punt()
  p2=punt()
  for p1 in gpx_list:
    if (p1.dist>dist):
      ok=True
      if (p1.dist != p2.dist):
        dfact=(dist-p2.dist)/(p1.dist-p2.dist)
      else:
        dfact=1.
      pr.lon=p2.lon+(p1.lon-p2.lon)*dfact
      pr.lat=p2.lat+(p1.lat-p2.lat)*dfact
      pr.ele=p2.ele+(p1.ele-p2.ele)*dfact
      pr.slope=p2.slope+(p1.slope-p2.slope)*dfact
      pr.dist=p2.dist+(p1.dist-p2.dist)*dfact
      pr.RoadSurface=p1.RoadSurface
      pr.RoadSurface_intensity=p1.RoadSurface_intensity

      break
    p2=p1

  if (ok):
    return pr
  else:
    pn.end_track=True
    return pn

def make_track(fn_gpx,fn_wtype):
  gpx_list=None
  if (fn_gpx != None):
    gpx_list=get_gpx(fn_gpx)
    if (fn_wtype != None):
      add_roadtype(gpx_list,fn_wtype)
    else:
      gpx_list.roadsurface_changes=None
  return gpx_list
