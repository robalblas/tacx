# tacx
Controlling tacx using gpx file

This program uses TacxTrainerControl of pycycling.
Usage:
tacx.py -g <gpxfile> [-s <start_dist in meters>] [-w <wegfile>] [-a <trainer_address] [-S]
                                                                                       
There are 2 main modes:
. tacx mode (default)
. simulation mode (option -S)
In simulation mode no tacx, bluetooth etc. is necessary

The program works fine on a PI4 (2G RAM should be enough). This raspberry pi contains everything needed. Make sure bluetooth is switched on.

At program start, using option -g <gpx_file>, the route is displayed. 
Click on 'Start':
. tacx mode: connection with tacx is established
. simulation mode: a running tacx is simulated

Following parameters from tacx are shown: Power, distance, speed, cadans
Following parameters are shown and derived from tacx data: gear
Following parameters are shown and derived from gpx/wpt file and control tacx: position, altitude, slope, road type
Following parameter is not tested yet: heart beat

If desired the road surface can be added, which will then be used to set road surface in the tacx. This needs some hand work.
An example is available:
. knetemacht.gpx
. knetemacht.wtp


The first one is the gpx file, the second one specifies at which part of the track which surface type should be simulated:
  . SIMULATION_OFF (=asphalt)
  . CONCRETE_PLATES
  . CATTLE_GRID
  . COBBLESTONES_HARD
  . COBBLESTONES_SOFT
  . BRICK_ROAD
  . OFF_ROAD
  . GRAVEL
  . ICE 
  . WOODEN_BOARDS

The .wtp file contains distance from start and road type:
  pd=<dist1> rd=<roadtype1>/<intensity1>
  pd=<dist2> rd=<roadtype2>/<intensity2>

Etc. See knetemacht.wtp.

Track types non-asphalt are coloured brown.

This example is located in Bloemendaal, the Netherlands, and was used by Gerry Kneteman for training. 
. Length: 3.5 km
. Height is between 9 and 42 meters
. slope up to 16%

Use: ./tacx.py -g knetemacht.gpx -w knetemacht.wtp

You can also  override slope and roadtype:
. check 'Manual'
. choose roadtype, intensity and slope

In gtacx.py you can choose the language of buttons,e.g.:
butnames=butnames_en

Available: English, Dutch.

You can easily add your own langauge.

Note: use 'Stop' before exiting the program. If program stops unexpectedly bluetooth can hold the tacx, preventing connecting again. In  that case reset the bluetooth using commands:

bluetoothctl power off
bluetoothctl power on
