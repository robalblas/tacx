from tacx_misc import pri_dbg, from_tacx
# extract distance and speed from tacx
# format in 'str': distance_travelled=123, speed=4.5
#   distance in meters, modulo 256
#   speed in m/s
#class from_tacx:
#  def __init__(self):
#    self.distance=0
#    self.pdistance=0
#    self.speed=0
#    self.new_data=False


################################################################################
# data from tacx
################################################################################
#'static' variables:
#  pdist
#  ndist
#  startdist
#  reset
def get_tacx_data(stri,offset):
  from_tacx.new_data=False
  if (stri.find('distance_travelled=')>=0):
    dst=stri.split('distance_travelled=')
    dst=dst[1].split(',')
    spd=dst[1].split('=')

    idist=int(dst[0])
    if (idist<get_tacx_data.pdist):
      get_tacx_data.ndist+=256
    get_tacx_data.pdist=idist

    if (get_tacx_data.reset):
      print("RESET")
      get_tacx_data.startdist=idist
      get_tacx_data.pdist=idist
      get_tacx_data.ndist=0
      get_tacx_data.reset=False
#      get_tacx_data.tpdist=-1

    dist=idist+get_tacx_data.ndist+offset-get_tacx_data.startdist
#    pri_dbg("dist={:d}  idist={:d}  ndist={:d}  offset={:d}  startdist={:d}".format(dist,idist,get_tacx_data.ndist,offset,get_tacx_data.startdist))
    speed=float(spd[1])*3.6
    if (get_tacx_data.tpdist!=dist):
      from_tacx.new_data=True
    get_tacx_data.tpdist=dist

    from_tacx.distance=dist
    from_tacx.speed=speed

  return from_tacx
get_tacx_data.tpdist=0

################################################################################
# commands to tacx
################################################################################
async def put_tacx_data(trainer,cmd,val,val2):
  # handle command 'set_basic_resistance'import sys, getopt
  if (cmd == "set_basic_resistance"):
    ival=int(val)
    pri_dbg("set_basic_resistance: " + str(ival))
    await trainer.set_basic_resistance(ival)

  # handle command 'set_track_resistance'
  elif (cmd == "set_track_resistance"):
    ival=int(val)
    pri_dbg("set_track_resistance: " + str(ival) + "  val=" + str(val2))
    await trainer.set_track_resistance(ival,float(val2))

  elif (cmd == "set_RoadSurface"):
    pri_dbg("road_surface_pattern=" + str(val) + "  intensity=" + str(val2))
    await trainer.set_neo_modes(road_surface_pattern=val,road_surface_pattern_intensity=int(val2),isokinetic_mode=False)

################################################################################
#Next for testing only
################################################################################
def test_get_tacx_data():
  #set 'statics'
  get_tacx_data.pdist=0
  get_tacx_data.ndist=0
  get_tacx_data.startdist=0
  get_tacx_data.tpdist=-1
  get_tacx_data.reset=False

  # dist = 123
  xxx=get_tacx_data("distance_travelled=123, speed=4.5",0)
  print("tdist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))

  # dist = 255
  xxx=get_tacx_data("distance_travelled=255, speed=5.5",0)
  print("tdist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))

  # dist=0 ==> totdist=256
  xxx=get_tacx_data("distance_travelled=0, speed=10.5",0)
  print("tdist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))

  # dist=100 ==> totdist=356
  xxx=get_tacx_data("distance_travelled=100, speed=10.5",0)
  print("tdist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))

  #dist=10 => reset ==> totdist=0
  get_tacx_data.reset=True
  xxx=get_tacx_data("distance_travelled=10, speed=10.5",0)
  print("tdist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))

  # dist 0 ==> totdist=246
  xxx=get_tacx_data("distance_travelled=0, speed=0",0)
  print("tdist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))

  # dist 2, offset=5 ==> totdist=248+5=253
  xxx=get_tacx_data("distance_travelled=2, speed=0",5)
  print("dist={:d} speed={:.2f} startdist={:d}".format(xxx.distance,xxx.speed,get_tacx_data.startdist))


#test_get_tacx_data()
