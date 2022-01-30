######################################################################################
# Gui setup
######################################################################################
#
import tkinter as tk
from tkinter import *
from tkinter.filedialog import askopenfilename

import os
from os import path

import threading
import asyncio

import tacx_misc
from tacx_misc import guivars

from tacx_real import tacx_real, put_tacx_roadsurface, put_tacx_slope

from tacx_sim import tacx_sim, put_tacxsim_roadsurface,put_tacxsim_slope,put_tacxsim_intens
from get_gpx import parse_roadtype, wegpunten, transl_int_roadsurface, make_track

butnames_nl=["Vermogen","Afstand" ,"Snelheid","Cadans","Overbreng.","Positie" ,"Hoogte"  ,"Helling","Wegdek"  ,"Hart" ,"Intensiteit" ]
butnames_en=["Power"   ,"Distance","Speed"   ,"Cadans","Gear"      ,"Position","Altitude","Slope"  ,"Roadtype","Heart","Intensity"   ]
butnames=butnames_en

########## Define tacx-app ##########
def get_gpxtrack(filename):
  global gpx_list
  gpx_list=read_files(filename,None)
  draw_track(gpx_list)


class TacxApp(tk.Frame):
  def __init__(self, master=None):
    tk.Frame.__init__(self, master)
    self.master.title("TacxApp")

    top = self.winfo_toplevel()
    self.menubar = tk.Menu(top)
    top['menu'] = self.menubar

    self.submenu = tk.Menu(self.menubar)
    self.menubar.add_cascade(label="File", menu=self.submenu)
    self.submenu.add_command(label="Open", command=self.get_filename)

  def get_filename(self):
    filename = askopenfilename()
    get_gpxtrack(filename)

########## Convert lon/lat into x,y ##########
def lola2cvs(pnt,guivars):
  x1=int((pnt.lon-guivars.minlon)*guivars.cvs_width/(guivars.loladmax/0.62))+10
  y1=guivars.cvs_height-int((pnt.lat-guivars.minlat)*guivars.cvs_height/(guivars.loladmax))
  return x1,y1


########## Start run-loop, actual tacx or simulate ##########
def start_loop(address,gpx_list,start_dist,simulate):
  global loop
  loop = asyncio.new_event_loop()
  asyncio.set_event_loop(loop)
#  print("gpx_list=" +str(gpx_list))
  if (simulate):
    loop.run_until_complete(tacx_sim(address,gpx_list))
  else:
    loop.run_until_complete(tacx_real(address,gpx_list))

  tacx_misc.running=False

########## Mark current position ##########
def mark_curpos(cvs,p1,guivars):
  x1,y1=lola2cvs(p1,guivars)
  x0,y0=guivars.curpos
  cvs.move(guivars.mark,x1-x0,y1-y0)
  guivars.curpos=(x1,y1)

########## Draw track in gui ##########
def draw_gpx(gpx_list,cvs):
  minlon=1000.
  maxlon=-1000.
  minlat=1000.
  maxlat=-1000.
  x0=1000
  y0=1000
  if (gpx_list==None):
    return

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
  rfp=None
  for p1 in gpx_list:
    x1,y1=lola2cvs(p1,guivars)
    rf=str(p1.RoadSurface)
#    print(rf)
    rf1=rf.split('.')
    if (str(rf1[1])=="SIMULATION_OFF"):
      clr="blue"
    else:
      clr="brown"

    if (x0<1000):
      cvs.create_line(x0, y0, x1, y1,fill=clr)

    if ((rfp==None) or (rfp != rf)):
      cvs.create_oval(x0-2,y0-2,x0+2,y0+2,fill="green")
    x0=x1
    y0=y1

    rfp=rf    

  p1=gpx_list.head
  guivars.curpos=(0,0)
  guivars.mark=cvs.create_oval(-5,-5,5,5,fill="red")

  mark_curpos(cvs,p1,guivars)

########## Read gpx and wtp (road type changes), load into gpx_list ##########
# If fn_wtp=None: try gpx-file with extension wtp
def read_files(fn_gpx,fn_wtp):
  if (fn_gpx==None):
    return
  if (not path.exists(fn_gpx)):
    return

  if (fn_wtp==None):
    fn_wtp=fn_gpx.strip(".gpx") + ".wtp"
  if (not path.exists(fn_wtp)):
    fn_wtp=None

  gpx_list=make_track(fn_gpx,fn_wtp)

  return gpx_list



########## Draw road changes (not used anymore, done in draw_gpx) ##########
def draw_wtp(weglist,cvs):
  for wl in weglist:
    x,y=lola2cvs(wl.pa,guivars)
    cvs.create_oval(x-2,y-2,x+2,y+2,fill="green")
    if (wl.pb!=None):
      x,y=lola2cvs(wl.pb,guivars)
      cvs.create_oval(x-2,y-2,x+2,y+2,fill="green")

########## Draw new track in gui ##########
def draw_track(gpx_list):
  guivars.cvs.delete("all")
  if (gpx_list):
    draw_gpx(gpx_list,guivars.cvs)
#    if (gpx_list.roadsurface_changes):
#      draw_wtp(gpx_list.roadsurface_changes,guivars.cvs)

def overbr(speed,cadence):
  wielomtrek=2.1
  if (cadence==0):
    return 0.0
  return float(speed*1000/60/wielomtrek/float(cadence))

show_accupow=False
show_hart=False
########## Print position in gui ##########
def show_pos(tacx_data,point):
  speed=tacx_misc.tacx_data.speed
  cadence=tacx_data.cadence
  dist=tacx_misc.tacx_data.distance+tacx_misc.guivars.add_dist
  set_entry(guivars.w21,"{:.1f}".format(float(tacx_data.inst_pow)))
  set_entry(guivars.w22,"{:d}".format(int(dist)))
  set_entry(guivars.w23,"{:.1f}".format(float(speed*3.6)))
  set_entry(guivars.w24,"{:d}".format(int(cadence)))
  set_entry(guivars.w25,"{:.2f}".format(float(overbr(speed,cadence))))
  if (point.pos_valid):
    set_entry(guivars.w26,"[{:.5f},{:.5f}]".format(point.lat,point.lon))
  else:
    set_entry(guivars.w26,"[??,??]")

  set_entry(guivars.w27,"{:.1f}".format(point.ele))
  set_entry(guivars.w28,"{:.1f}".format(point.slope))

  rf=str(point.RoadSurface)
  rf1=rf.split('.')
  if (str(rf1[1])=="SIMULATION_OFF"):
    set_entry(guivars.w29,"{:s}".format("Asfalt"))
  else:
    set_entry(guivars.w29,"{:s} / {:d}".format(str(rf1[1]),int(point.RoadSurface_intensity)))

  if (show_hart):
    set_entry(guivars.w30,"{:d}".format(int(tacx_data.heart)))
  else:
    if (show_accupow):
      set_entry(guivars.w30,"{:.1f}".format(float(tacx_data.accu_pow)))

  if (point.pos_valid):
    mark_curpos(guivars.cvs,point,guivars)

########## Print status in gui ##########
def set_entry(w,s):
  w.delete(0,END)
  if (len(s)>=1):
    w.insert(0,s)

########## Setup the gui ##########
def setup_gui(address,fn_gpx,fn_wtp,start_dist,simulate,cvswidth,cvsheight):
  from get_gpx import goto_pos
  from tacx_sim import reset_dist
  global gpx_list
  def handle_keypress_reset(event):
    reset_dist(gpx_list)

  def handle_keypress_start(event):
    if (simulate):
      if (gpx_list==None):
        set_entry(guivars.w20,"No gpx!")
        return
      else:
        set_entry(guivars.w20,"Simulation runs")
    else:
      if (gpx_list==None):
        set_entry(guivars.w20,"Tacx, no gpx")
      else:
        set_entry(guivars.w20,"Tacx active")

    if (not tacx_misc.running):
      threading.Thread(target=start_loop,args=(address,gpx_list,start_dist,simulate)).start()
      tacx_misc.running=True

    tacx_misc.pauze=False

  def handle_keypress_pauze(event):
    if (tacx_misc.running):
      tacx_misc.pauze=not tacx_misc.pauze
      if (tacx_misc.pauze):
        wat="Pauze"
      else:
        wat="Running"
      if (simulate):
        set_entry(guivars.w20,"Simulate " + wat)
      else:
        set_entry(guivars.w20,"Tacx " + wat)

  def handle_keypress_stop(event):
    if (simulate):
      set_entry(guivars.w20,"Simulation stopped")
    else:
      set_entry(guivars.w20,"Tacx stopped")
    tacx_misc.running=False
    tacx_misc.pauze=False

  def handle_keypress_bt_rst(event):
    os.system("bluetoothctl power off")
    os.system("bluetoothctl power on")

  def handle_keypress_roadtype():
    rs=transl_int_roadsurface(var4.get())
    if (simulate):
      put_tacxsim_roadsurface("set_RoadSurface",rs,tacx_misc.man_roadsurface_intensity)
    else:
      put_tacx_roadsurface("set_RoadSurface",rs,tacx_misc.man_roadsurface_intensity)

  def handle_keypress_roadman():
    tacx_misc.man_roadsurface=var5.get()
    if (tacx_misc.man_roadsurface):
      handle_keypress_roadtype()

  def val_dist_changed(dummy=0):
    guivars.add_dist=int(value_dist.get())
    cur_pos=goto_pos(gpx_list,tacx_misc.tacx_data.distance+tacx_misc.guivars.add_dist)
    show_pos(tacx_misc.tacx_data,cur_pos)

  def val_intens_changed(dummy=0):
    intens=int(value_intens.get())
    if (simulate):
      put_tacxsim_intens(intens)
    else:
      put_tacx_intens(intens)

  def val_slope_changed(dummy=0):
    slope=int(value_slope.get())
    if (simulate):
      put_tacxsim_slope(slope)
    else:
      put_tacx_slope(slope)

  wnd = tk.Tk()
  frame123=Frame(wnd)
  frame12=Frame(frame123)

  ##### Data from Tacx
  frame1=Frame(frame12)
  w11=Label(frame1,text=butnames[0], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w12=Label(frame1,text=butnames[1], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w13=Label(frame1,text=butnames[2], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w14=Label(frame1,text=butnames[3], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w15=Label(frame1,text=butnames[4], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w16=Label(frame1,text=butnames[5], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w17=Label(frame1,text=butnames[6], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w18=Label(frame1,text=butnames[7], font=('Arial', 30, 'bold'),width=10,anchor=W)
  w19=Label(frame1,text=butnames[8], font=('Arial', 30, 'bold'),width=10,anchor=W)

  if (show_hart):
    w20=Label(frame1,text=butnames[9], font=('Arial', 30, 'bold'),width=10,anchor=W)
  else:
    if (show_accupow):
      w20=Label(frame1,text="Acc. pow"  ,font=('Arial', 30, 'bold'),width=8,anchor=W)

  guivars.w20=Entry(frame1,font=('Arial', 35, 'bold'),width=30,fg="red")
  guivars.w21=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w22=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w23=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w24=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w25=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w26=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w27=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w28=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  guivars.w29=Entry(frame1,font=('Arial', 30, 'bold'),width=25)
  if ((show_hart) | (show_accupow)):
    guivars.w30=Entry(frame1,font=('Arial', 30, 'bold'),width=25)

  w11.grid(column=0,row=1)
  w12.grid(column=0,row=2)
  w13.grid(column=0,row=3)
  w14.grid(column=0,row=4)
  w15.grid(column=0,row=5)
  w16.grid(column=0,row=6)
  w17.grid(column=0,row=7)
  w18.grid(column=0,row=8)
  w19.grid(column=0,row=9)
  if ((show_hart) | (show_accupow)):
    w20.grid(column=0,row=10)

  guivars.w20.grid(column=0,columnspan=2,row=0)
  guivars.w21.grid(column=1,row=1)
  guivars.w22.grid(column=1,row=2)
  guivars.w23.grid(column=1,row=3)
  guivars.w24.grid(column=1,row=4)
  guivars.w25.grid(column=1,row=5)
  guivars.w26.grid(column=1,row=6)
  guivars.w27.grid(column=1,row=7)
  guivars.w28.grid(column=1,row=8)
  guivars.w29.grid(column=1,row=9)
  if ((show_hart) | (show_accupow)):
    guivars.w30.grid(column=1,row=10)

  if (simulate):
    set_entry(guivars.w20,"Simulate")
  else:
    set_entry(guivars.w20,"Tacx")

  ##### Manually set road type
  var4 = IntVar()
  var5 = IntVar()
  frame2=Frame(frame12)
  Checkbutton(frame2,text="Manual",variable=var5,command=handle_keypress_roadman).pack(anchor=W)
  Radiobutton(frame2,text="Asfalt",value=0,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="CONCRETE_PLATES",value=1,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="CATTLE_GRID",value=2,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="COBBLESTONES_HARD",value=3,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="COBBLESTONES_SOFT",value=4,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="BRICK_ROAD",value=5,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="OFF_ROAD",value=6,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="GRAVEL",value=7,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="ICE",value=8,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)
  Radiobutton(frame2,text="WOODEN_BOARDS",value=9,variable=var4,command=handle_keypress_roadtype).pack(anchor=W)

  value_intens = tk.StringVar(value=20)
  wx2=Label(frame2,text=butnames[10]).pack(anchor=W)
  Spinbox(frame2,textvariable=value_intens,command=val_intens_changed,from_=0,to_=70,increment_=5,width=4).pack(anchor=W)


  value_slope = tk.StringVar(value=0)
  wx1=Label(frame2,text=butnames[7]).pack(anchor=W)
  Spinbox(frame2,textvariable=value_slope,command=val_slope_changed,from_=-20,to_=20,increment_=1,width=4).pack(anchor=W)

  ##### on/off etc.
  frame3=Frame(frame123)
  w31=Button(frame3,text="Reset")
  w31.bind("<Button-1>",handle_keypress_reset)
  w32=Button(frame3,text="Start")
  w32.bind("<Button-1>",handle_keypress_start)
  w33=Button(frame3,text="Pauze")
  w33.bind("<Button-1>",handle_keypress_pauze)
  w34=Button(frame3,text="Stop")
  w34.bind("<Button-1>",handle_keypress_stop)
  w35=Button(frame3,text="Reset BlueTooth")
  w35.bind("<Button-1>",handle_keypress_bt_rst)

  value_dist = tk.StringVar(value=0)
  w360=Label(frame3,text="Add dist")
  w36=Spinbox(frame3,textvariable=value_dist,command=val_dist_changed,from_=-10000,to_=10000,increment_=1,width=6)
  w36.bind("<Return>",val_dist_changed)
  guivars.add_dist=0

  w31.grid(column=1,row=1)
  w32.grid(column=2,row=1)
  w33.grid(column=3,row=1)
  w34.grid(column=4,row=1)
  w35.grid(column=5,row=1)
  w360.grid(column=6,row=1)
  w36.grid(column=7,row=1)

  ##### Canvas: Map
  frame4=Frame(wnd)
  guivars.cvs = tk.Canvas(frame4, bg="grey90", height=cvsheight, width=cvswidth)
  guivars.cvs_width=cvswidth
  guivars.cvs_height=cvsheight

  gpx_list=read_files(fn_gpx,fn_wtp)
  draw_track(gpx_list)

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

  wnd1=TacxApp()
  wnd1.mainloop()

