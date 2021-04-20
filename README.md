# tacx
Controlling tacx using gpx file

This program uses TacxTrainerControl of pycycling.
Usage:
gtacx.py -g <gpxfile> [-s <start_dist in meters>] [-w <wegfile>] [-a <trainer_address] [-S]
                                                                                       
There are 2 main modes:
. tacx mode (default)
. simulation mode (option -S)
In simulation mode no tacx, bluetooth etc. is necessary

The program works fine on a PI4 (2G RAM is enough). This raspberry pi contains everything needed. Make sure bluetooth is switched on.

At program start, using -g option, the route is displayed. 
Click on 'Start':
. tacx mode: connection with tacx is established
. simulation mode: a running tacx is simulated

Position, speed and slope is shown.

In tacx mode the slope is used with 'set_track_resistance'.
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

3 coordinates per track need to be specified:
  pa=start, pb=end, pi=somwhere in-between
  type:
    <type>/<intensity> (intensity betwen 0 and 50)

Track types non-asphalt are coloured brown.

This example is located in Bloemendaal, the Netherlands, and was used by Gerry Kneteman for training. 
. Length: 3.5 km
. Height is between 9 and 42 meters
. slope to 16%

Use: ./gtacx.py -g knetemacht.gpx -w knetemacht.wtp

Note: use 'Stop' before exiting the program. If program stops unexpectedly bluetooth can hold the tacx, preventing connecting again. In  that case reset the bluetooth using commands:

bluetoothctl power off
bluetoothctl power on
