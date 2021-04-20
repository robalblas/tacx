import asyncio

from tacx_interface import get_tacx_data, put_tacx_data
from get_gpx import get_gpx,goto_pos,add_roadtype

import tacx_misc
from tacx_misc import heardEnter, from_tacx, pri_dbg

global sim_dist
def gen_data():
  global sim_dist
  str1="distance_travelled=" + str(sim_dist) + ", speed=1.2"
  if (not tacx_misc.pauze):
    sim_dist=sim_dist+1
  return str1

async def put_tacxsim_data(trainer,cmd,val,val2):
  pri_dbg(str(cmd)+" " + str(val) + "  " + str(val2))


def put_tacxsim_roadsurface(cmd,val,val2):
  tacx_misc.man_roadsurface_type=val
  tacx_misc.man_roadsurface_intensity=val2
  tacx_misc.tacx_data.new_data=True

async def tacx_sim(address,fn_gpx,fn_wtype):
  from gtacx import set_entry
  global cur_pos,sim_dist
  sim_dist=0
  tacx_misc.running=True
  get_tacx_data.pdist=0
  get_tacx_data.ndist=0
  get_tacx_data.startdist=0
  get_tacx_data.reset=True
  gpx_list=None

  if (fn_gpx):
    print("Read gpx '" + fn_gpx + "...")
    gpx_list=get_gpx(fn_gpx)
    if (fn_wtype != None):
      add_roadtype(gpx_list,fn_wtype)

  # goto start position
  cur_pos=goto_pos(gpx_list,tacx_misc.offset)
  tacx_misc.man_roadsurface_type=cur_pos.RoadSurface
  tacx_misc.man_roadsurface_intensity=20

  set_entry(tacx_misc.guivars.w20,"Would be Tacx Try to connect")
  if (True):
    set_entry(tacx_misc.guivars.w20,"Would be Tacx Connecting")
#      await client.is_connected()
    set_entry(tacx_misc.guivars.w20,"Would be Tacx Connected")
    sim_trainer = 1

    ######################################################
    # handle commands from tacx; get current position:
    def my_page_handler_sim(data):
      global cur_pos
      tacx_misc.tacx_data=get_tacx_data(str(data),tacx_misc.offset)
      if (tacx_misc.tacx_data.new_data):
        cur_pos=goto_pos(gpx_list,tacx_misc.tacx_data.distance+tacx_misc.guivars.curval)
        if (tacx_misc.man_roadsurface):
          cur_pos.RoadSurface=tacx_misc.man_roadsurface_type
          cur_pos.RoadSurface_intensity=tacx_misc.man_roadsurface_intensity

    ######################################################
    # Loop: simulate commands to tacx, check each sec, if tacxi.cmd changes
    while (tacx_misc.running):
      if (tacx_misc.tacx_data.new_data):
        from gtacx import show_pos
        if (cur_pos==None):
          break

        show_pos(cur_pos,tacx_misc.tacx_data.speed,tacx_misc.tacx_data.distance+tacx_misc.guivars.curval)
        await put_tacxsim_data(sim_trainer,"set_track_resistance",cur_pos.slope,0.002)
        await put_tacxsim_data(sim_trainer,"set_RoadSurface",cur_pos.RoadSurface,cur_pos.RoadSurface_intensity)
        tacx_misc.tacx_data.new_data=False
      await asyncio.sleep(0.01)

      my_page_handler_sim(gen_data())
#      if heardEnter():
#        break

#        await trainer.disable_fec_notifications()
    if (cur_pos!=None):
      set_entry(tacx_misc.guivars.w20,"Stopped @ gpx={:.3f} km".format(cur_pos.dist/1000.))
    else:
      set_entry(tacx_misc.guivars.w20,"End-of-track")
