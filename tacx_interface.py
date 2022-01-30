######################################################################################
# TACX interface functions
######################################################################################
#
from tacx_misc import pri_dbg, from_tacx
# extract distance and speed from tacx
# format in 'str': distance_travelled=123, speed=4.5
#   distance in meters, modulo 256
#   speed in m/s
#class from_tacx:
#  def __init__(self):
#    self.distance=0
#    self.speed=0
#    self.cadence=0
#    self.new_data=False


################################################################################
# data from tacx
################################################################################
#'static' variables:
#  pdist
#  ndist
#  startdist
#  reset
def get_val_int(srch,stri,ival):
  if (stri.find(srch+'=')>=0):
    val=stri.split(srch+'=')
    val=val[1].split(',')
    if (val[0]=="None"):
      ival=0
    else:
      ival=int(val[0])
  return ival

def get_val_flt(srch,stri,fval):
  if (stri.find(srch+'=')>=0):
    val=stri.split(srch+'=')
    val=val[1].split(',')
    fval=float(val[0])
  return fval

def get_tacx_data(stri,offset):
  from_tacx.new_data=False
  if (stri.find('distance_travelled=')>=0):
    dst=stri.split('distance_travelled=')
    dst=dst[1].split(',')

    idist=int(dst[0])
    if (idist<get_tacx_data.pdist):
      get_tacx_data.ndist+=256
    get_tacx_data.pdist=idist

    if (get_tacx_data.reset):
      get_tacx_data.startdist=idist
      get_tacx_data.pdist=idist
      get_tacx_data.ndist=0
      get_tacx_data.reset=False

    dist=idist+get_tacx_data.ndist+offset-get_tacx_data.startdist
#    pri_dbg("dist={:d}  idist={:d}  ndist={:d}  offset={:d}  startdist={:d}".format(dist,idist,get_tacx_data.ndist,offset,get_tacx_data.startdist))

    if (get_tacx_data.tpdist!=dist):
      from_tacx.new_data=True
    get_tacx_data.tpdist=dist

    from_tacx.distance=dist

  from_tacx.speed=get_val_flt('speed',stri,get_tacx_data.speed)
  get_tacx_data.speed=ihrt=from_tacx.speed

  from_tacx.heart=get_val_int('heart_rate',stri,get_tacx_data.heart)
  get_tacx_data.heart=ihrt=from_tacx.heart

  from_tacx.cadence=get_val_int('instantaneous_cadence',stri,get_tacx_data.cadence)
  get_tacx_data.cadence=ihrt=from_tacx.cadence

  from_tacx.accu_pow=get_val_int('accumulated_power',stri,get_tacx_data.accu_pow)
  get_tacx_data.accu_pow=ihrt=from_tacx.accu_pow

  from_tacx.inst_pow=get_val_int('instantaneous_power',stri,get_tacx_data.inst_pow)
  get_tacx_data.inst_pow=ihrt=from_tacx.inst_pow


  return from_tacx

get_tacx_data.tpdist=0
get_tacx_data.cadence=0
get_tacx_data.accu_pow=0
get_tacx_data.inst_pow=0
get_tacx_data.heart=0
get_tacx_data.speed=0

################################################################################
# commands to tacx
################################################################################
async def put_tacx_data(trainer,cmd,val,val2):
  # handle command 'set_basic_resistance': val=0...200, actually gives just 11 values
  if (cmd == "set_basic_resistance"):
    ival=int(val)
    pri_dbg("set_basic_resistance: " + str(ival))
    await trainer.set_basic_resistance(ival)

  # handle command 'set_track_resistance': val=slope in %, val2=rolling resistance
  elif (cmd == "set_track_resistance"):
    ival=int(val)
    pri_dbg("set_track_resistance: " + str(ival) + "  val=" + str(val2))
    await trainer.set_track_resistance(ival,float(val2))

  # handle command 'set_neo_modes': val=road_surface_pattern, val2=intensity
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
