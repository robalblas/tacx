#!/usr/bin/python3
import tkinter as tk
from tkinter import *
import os
from os import path
import threading

import asyncio
import getopt

import tacx_misc
from tacx_misc import guivars
import tacx_real
from tacx_real import tacx_real, put_tacx_roadsurface
from tacx_sim import tacx_sim, put_tacxsim_roadsurface
from get_gpx import get_gpx, add_roadtype, parse_roadtype, wegpunten, transl_int_roadsurface


#class grapvals:
#  cvs_width=cvs_width
#  cvs_height=cvs_height
#  minlon=0
#  minlat=0
#  loladmax=0


def lola2cvs(pnt,guivars):
  x1=int((pnt.lon-guivars.minlon)*guivars.cvs_width/(guivars.loladmax/0.62))+10
  y1=guivars.cvs_height-int((pnt.lat-guivars.minlat)*guivars.cvs_height/(guivars.loladmax))
  return x1,y1

def make_track(fn_gpx,fn_wtype):
  gpx_list=None
  if (fn_gpx != None):
    gpx_list=get_gpx(fn_gpx)
  if (fn_wtype != None):
    add_roadtype(gpx_list,fn_wtype)
  return gpx_list

def draw_gpx(gpx_list,cvs):
  minlon=1000.
  maxlon=-1000.
  minlat=1000.
  maxlat=-1000.
  x2=1000
  for p1 in gpx_list:
    if (p1.lon<minlon): minlon=p1.lon
    if (p1.lon>maxlon): maxlon=p1.lon
    if (p1.lat<minlat): minlat=p1.lat
    if (p1.lat>maxlat): maxlat=p1.lat
  loladmax=maxlon-minlon
  if (loladmax<maxlat-minlat):
    loladmax=maxlat-minlat
#  print("{:.3f} {:.3f}  {:.3f} {:.3f} {:.3f}".format(minlon,maxlon,minlat,maxlat,loladmax))

  guivars.minlon=minlon
  guivars.minlat=minlat
  guivars.loladmax=loladmax

  for p1 in gpx_list:
    x1,y1=lola2cvs(p1,guivars)
    rf=str(p1.RoadSurface)
    rf1=rf.split('.')
    if (str(rf1[1])=="SIMULATION_OFF"):
      clr="blue"
    else:
      clr="brown"

    if (x2<1000):
      cvs.create_line(x1, y1, x2, y2,fill=clr)
    x2=x1
    y2=y1

  p1=gpx_list.head
  guivars.curpos=(0,0)
  guivars.mark=cvs.create_oval(-5,-5,5,5,fill="red")

  mark_curpos(cvs,p1,guivars)

def draw_wtp(fn_wtp,cvs):
  weglist=wegpunten()
  if (path.exists(fn_wtp)):
    fp = open(fn_wtp, 'r')
  
    parse_roadtype(fp,weglist)
    fp.close()
    for wl in weglist:
      x,y=lola2cvs(wl.pa,guivars)
      cvs.create_oval(x-5,y-5,x+5,y+5,fill="green")
      x,y=lola2cvs(wl.pb,guivars)
      cvs.create_oval(x-5,y-5,x+5,y+5,fill="green")


def mark_curpos(cvs,p1,guivars):
  x1,y1=lola2cvs(p1,guivars)
  x0,y0=guivars.curpos
  cvs.move(guivars.mark,x1-x0,y1-y0)
  guivars.curpos=(x1,y1)


def start_loop(address,fn_gpx,start_dist,fn_wtp,simulate):
  global loop
  #print("start_loop")
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
  if (simulate):
    loop.run_until_complete(tacx_sim(address,fn_gpx,fn_wtp))
  else:
    loop.run_until_complete(tacx_real(address,fn_gpx,fn_wtp))

  tacx_misc.running=False
#  set_entry(guivars.w20,"End-of-track")

def setup_gui(address,fn_gpx,start_dist,fn_wtp,simulate,cvswidth,cvsheight):
  def handle_keypress1(event):
    if (simulate):
      set_entry(guivars.w20,"Simulate Running")
    else:
      set_entry(guivars.w20,"Tacx Running")
    if (not tacx_misc.running):
      threading.Thread(target=start_loop,args=(address,fn_gpx,start_dist,fn_wtp,simulate)).start()
      tacx_misc.running=True
    tacx_misc.pauze=False

  def handle_keypress2(event):
    tacx_misc.pauze=not tacx_misc.pauze
    if (tacx_misc.pauze):
      wat="Pauze"
    else:
      wat="Running"
    if (simulate):
      set_entry(guivars.w20,"Simulate " + wat)
    else:
      set_entry(guivars.w20,"Tacx " + wat)

  def handle_keypress3(event):
    if (simulate):
      set_entry(guivars.w20,"Simulate Stopped")
    else:
      set_entry(guivars.w20,"Tacx Stopped")
    tacx_misc.running=False
    tacx_misc.pauze=False

  def handle_keypress4():

    rs=transl_int_roadsurface(var4.get())
    if (simulate):
      put_tacxsim_roadsurface("set_RoadSurface",rs,21)
    else:
      put_tacx_roadsurface("set_RoadSurface",rs,22.)

  def handle_keypress5():
    set_man_rs(var5.get())
    #ophalen toestand radio

  def val_changed(dummy=0):
    guivars.curval=int(current_value.get())

  wnd = tk.Tk()
  frame123=Frame(wnd)
  frame12=Frame(frame123)

  ##### Data from Tacx
  frame1=Frame(frame12)
  w11=Label(frame1,text="Positie" ,font=('Arial', 30, 'bold'),width=8)
  w12=Label(frame1,text="Afstand" ,font=('Arial', 30, 'bold'),width=8)
  w13=Label(frame1,text="Snelheid",font=('Arial', 30, 'bold'),width=8)
  w14=Label(frame1,text="Hoogte"  ,font=('Arial', 30, 'bold'),width=8)
  w15=Label(frame1,text="Helling" ,font=('Arial', 30, 'bold'),width=8)
  w16=Label(frame1,text="Wegdek"  ,font=('Arial', 30, 'bold'),width=8)
  guivars.w20=Entry(frame1,font=('Arial', 30, 'bold'),width=30,fg="red")
  guivars.w21=Entry(frame1,font=('Arial', 30, 'bold'))
  guivars.w22=Entry(frame1,font=('Arial', 30, 'bold'))
  guivars.w23=Entry(frame1,font=('Arial', 30, 'bold'))
  guivars.w24=Entry(frame1,font=('Arial', 30, 'bold'))
  guivars.w25=Entry(frame1,font=('Arial', 30, 'bold'))
  guivars.w26=Entry(frame1,font=('Arial', 30, 'bold'))

  w11.grid(column=0,row=1)
  w12.grid(column=0,row=2)
  w13.grid(column=0,row=3)
  w14.grid(column=0,row=4)
  w15.grid(column=0,row=5)
  w16.grid(column=0,row=6)
  guivars.w20.grid(column=0,columnspan=2,row=0)
  guivars.w21.grid(column=1,row=1)
  guivars.w22.grid(column=1,row=2)
  guivars.w23.grid(column=1,row=3)
  guivars.w24.grid(column=1,row=4)
  guivars.w25.grid(column=1,row=5)
  guivars.w26.grid(column=1,row=6)

  if (simulate):
    set_entry(guivars.w20,"Simulate")
  else:
    set_entry(guivars.w20,"Tacx")

  ##### Manually set road type
  var4 = IntVar()
  var5 = IntVar()
  frame2=Frame(frame12)
  Checkbutton(frame2,text="Manual",variable=var5,command=handle_keypress5).pack(anchor=W)
  Radiobutton(frame2,text="Asfalt",value=0,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="CONCRETE_PLATES",value=1,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="CATTLE_GRID",value=2,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="COBBLESTONES_HARD",value=3,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="COBBLESTONES_SOFT",value=4,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="BRICK_ROAD",value=5,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="OFF_ROAD",value=6,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="GRAVEL",value=7,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="ICE",value=8,variable=var4,command=handle_keypress4).pack(anchor=W)
  Radiobutton(frame2,text="WOODEN_BOARDS",value=9,variable=var4,command=handle_keypress4).pack(anchor=W)
  
  ##### on/off etc.
  frame3=Frame(frame123)
  w31=Button(frame3,text="Start")
  w31.bind("<Button-1>",handle_keypress1)
  w32=Button(frame3,text="Pauze")
  w32.bind("<Button-1>",handle_keypress2)
  w33=Button(frame3,text="Stop")
  w33.bind("<Button-1>",handle_keypress3)
  current_value = tk.StringVar(value=0)
  w34=Spinbox(frame3,textvariable=current_value,command=val_changed,from_=-10000,to_=10000,increment_=1,width=6)
  w34.bind("<Return>",val_changed)
  guivars.curval=0
  w31.grid(column=1,row=1)
  w32.grid(column=2,row=1)
  w33.grid(column=3,row=1)
  w34.grid(column=4,row=1)

  ##### Canvas: Map
  frame4=Frame(wnd)
  guivars.cvs = tk.Canvas(frame4, bg="grey90", height=cvsheight, width=cvswidth)
  guivars.cvs_width=cvswidth
  guivars.cvs_height=cvsheight
  gpx_list=make_track(fn_gpx,fn_wtp)
  if (gpx_list):
    draw_gpx(gpx_list,guivars.cvs)
  if (fn_wtp):
    draw_wtp(fn_wtp,guivars.cvs)
  guivars.cvs.grid(column=3,row=1,rowspan=12)


################################################################
  ##### Place parts:
  # wnd[frame123[frame12[frame1, frame2],frame3]frame4]
  
  frame1.pack(side=LEFT)
  frame2.pack(side=RIGHT)
  frame12.pack(side=TOP)

  frame3.pack(side=BOTTOM)
  frame123.pack(side=LEFT,anchor=N)

  frame4.pack()

  wnd.mainloop()

def show_pos(point,speed,dist):
  set_entry(guivars.w21,"[{:.5f},{:.5f}]".format(point.lat,point.lon))
  set_entry(guivars.w22,"{:d}".format(int(dist)))
  set_entry(guivars.w23,"{:.1f}".format(float(speed)))
  set_entry(guivars.w24,"{:.1f}".format(point.ele))
  set_entry(guivars.w25,"{:.1f}".format(point.slope))
  rf=str(point.RoadSurface)
  rf1=rf.split('.')
  if (str(rf1[1])=="SIMULATION_OFF"):
    set_entry(guivars.w26,"{:s}".format("Asfalt"))
  else:
    set_entry(guivars.w26,"{:s} / {:d}".format(str(rf1[1]),int(point.RoadSurface_intensity)))

  mark_curpos(guivars.cvs,point,guivars)

def set_man_rs(ena):
  tacx_misc.man_roadsurface=ena

def set_entry(w,s):
  w.delete(0,END)
  if (len(s)>=1):
    w.insert(0,s)

def main(argv):
  global cvs
  tacx_misc.init_globs()          # Call only once
  start_dist=0
  fn_wtp=None
  gpxfile=None
  simulate=False
  device_address = "C2:9D:1D:49:A9:C7"
  cvs_width=500
  cvs_height=500

  try:
    opts, args = getopt.getopt(argv,"hSg:w:s:a:x:y:")
  except getopt.GetoptError:
    print("ERR: -g <gpxfile> [-s <start_dist in meters>] [-w <wegfile>] [-a <trainer_address]")
    sys.exit(2)

  for opt, arg in opts:
    if opt == '-h':
      print("options: -g <gpxfile> [-s <start_dist in meters>] [-w <wegfile>] [-a <trainer_address] [-S]")
      sys.exit()
    elif opt in ("-a"):
      device_address = arg
    elif opt in ("-g"):
      gpxfile = arg
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

#  if (gpxfile==None):
#    print("ERROR -g <gpx>")
#    sys.exit(2)

  print("Trainer-address=" + device_address)
  if (gpxfile != None):
    print("gpx-file=" + gpxfile + "  start=" + str(start_dist) +  " meter  road-file=" + str(fn_wtp))

  if ((gpxfile) and (path.exists(gpxfile))):
    print("")
  elif (gpxfile!=None):
    print("Not found: " + gpxfile)
    sys.exit(2)

  if ((fn_wtp==None) or (path.exists(fn_wtp))):
    print("")
  else:
    print("Not found: " + fn_wtp)
    sys.exit(2)

  print("devadr=" + device_address)

  cvs=None

  setup_gui(device_address,gpxfile,start_dist,fn_wtp,simulate,cvs_width,cvs_height)


if __name__ == "__main__":
  main(sys.argv[1:])
