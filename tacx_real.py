######################################################################################
# Tacx control
######################################################################################
#
import asyncio

from tacx_interface import get_tacx_data, put_tacx_data
from get_gpx import get_gpx,goto_pos,add_roadtype

import tacx_misc
from tacx_misc import heardEnter, from_tacx
def put_tacx_roadsurface(cmd,val,val2):
  tacx_misc.man_roadsurface_type=val
  tacx_misc.man_roadsurface_intensity=val2
  tacx_misc.tacx_data.new_data=True

def put_tacx_slope(val):
  tacx_misc.man_slope=val

async def tacx_real(address,gpx_list):
  global cur_pos
  from bleak import BleakClient
  from pycycling2.tacx_trainer_control import TacxTrainerControl
  from gtacx import set_entry

  tacx_misc.running=True
  get_tacx_data.pdist=0
  get_tacx_data.ndist=0
  get_tacx_data.startdist=0
  get_tacx_data.reset=True

  # goto start position
  cur_pos=goto_pos(gpx_list,tacx_misc.offset)
  if (cur_pos):
    tacx_misc.man_roadsurface_type=cur_pos.RoadSurface
    tacx_misc.man_roadsurface_intensity=20

  set_entry(tacx_misc.guivars.w20,"Tacx Try to connect")
  async with BleakClient(address,  timeout=20.0) as client:
    set_entry(tacx_misc.guivars.w20,"Tacx Connecting")
    await client.is_connected()
    set_entry(tacx_misc.guivars.w20,"Tacx Connected")
    trainer = TacxTrainerControl(client)

    ######################################################
    # handle commands from tacx; get current position:
    def my_page_handler(data):
      global cur_pos
      tacx_misc.tacx_data=get_tacx_data(str(data),tacx_misc.offset)
      if (tacx_misc.tacx_data.new_data):
        cur_pos=goto_pos(gpx_list,tacx_misc.tacx_data.distance+tacx_misc.guivars.add_dist)
        if (tacx_misc.man_roadsurface):
          cur_pos.RoadSurface=tacx_misc.man_roadsurface_type
          cur_pos.RoadSurface_intensity=tacx_misc.man_roadsurface_intensity
          cur_pos.slope=tacx_misc.man_slope

    trainer.set_specific_trainer_data_page_handler(my_page_handler)
    trainer.set_general_fe_data_page_handler(my_page_handler)
    await trainer.enable_fec_notifications()

    #set fixed parameters
    await trainer.set_user_configuration(user_weight=75,bicycle_weight=10,bicycle_wheel_diameter=0.7,gear_ratio=1)
    set_entry(tacx_misc.guivars.w20,"Tacx Running")
    #print("Ready")

    ######################################################
    # Loop: send commands to tacx, check regularly if data from tacx changes
    while (tacx_misc.running):
      if (tacx_misc.tacx_data.new_data):
        if (cur_pos.end_track):
          break

        from gtacx import show_pos
        show_pos(tacx_misc.tacx_data,cur_pos)
        await put_tacx_data(trainer,"set_track_resistance",cur_pos.slope,0.002)
        await put_tacx_data(trainer,"set_RoadSurface",cur_pos.RoadSurface,int(cur_pos.RoadSurface_intensity))
        tacx_misc.tacx_data.new_data=False
      await asyncio.sleep(0.2)

    await trainer.disable_fec_notifications()
    if (cur_pos.end_track):
      set_entry(tacx_misc.guivars.w20,"End-of-track")
    else:
      set_entry(tacx_misc.guivars.w20,"Stopped @ gpx={:.3f} km".format(cur_pos.dist/1000.))


################################################################################
#Next for testing only
################################################################################
def test_tacx_real():
#  global offset
  device_address = "C2:9D:1D:49:A9:C7"
  fn_gpx="knetemacht.gpx"
  fn_wtype=None
  tacx_misc.running=True
  tacx_misc.tacx_data=from_tacx()
  tacx_real(device_address)

  loop = asyncio.new_event_loop()
  loop.run_until_complete(tacx_real(device_address))

#test_tacx_real()
