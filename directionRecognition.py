#! /usr/bin/env python
# coding: utf-8
print("Start script")

from Tkinter import *
import serial
import time
import threading
import datetime
import random

print "Version 1"
def scan():
    """scan for available ports. return a list of tuples (num, name)"""
    available = []
    for i in range(256):
        try:
            port = "/dev/ttyUSB%d" % i
            ser = serial.Serial(port, baudrate=115200, timeout=10)
            available.append( (i, ser.portstr))
            ser.close()   # explicit close 'cause of delayed GC in java

        except serial.serialutil.SerialException :
            pass     
    for i in range(256):
        try:
            port = "/dev/ttyACM%d" % i
            ser = serial.Serial(port, baudrate=115200, timeout=10)
            available.append( (i, ser.portstr))
            ser.close()   # explicit close 'cause of delayed GC in java

        except serial.serialutil.SerialException :
            pass    
    return available


#found = False
# Search for available serial ports on the platform
#for i in range(64) :
#  try :
    #port = "/dev/ttyACM%d" % i
#    port = "/dev/ttyUSB%d" % i
#    ser = serial.Serial(port, baudrate=115200, timeout=10)
#    ser.close()
#    print "Найден последовательный порт: ", port
#    found = True
#  except serial.serialutil.SerialException :
#    #print "error open serial port:%d " %i
#    pass
#if not found :
#  print "Последовательных портов не обнаружено"

#constants
uType = 0x55
kType = 0x4b
  
queryRadio0Package   = "\x23\x30\x51\x01\x52\xFB\xFB"
queryRadio1Package   = "\x23\x31\x51\x01\x52\x8D\x4F"

getDataCh0Package   = "\x23\x30\x47\x02\xff\xff\xb5\xc8"
getDataCh1Package   = "\x23\x31\x47\x02\xff\xff\x1f\x99"



def int2hex(inArray):
    lenOfarray = len(inArray)
    OutArray=''
    mysum=0
    for i in range(lenOfarray):
        OutArray = OutArray+str(hex(inArray[i]))+' '
    return OutArray


class ConDis():
    def __init__(self):
        self.but = Button(root,width=20,height=2,bg = "SteelBlue1");
        self.but["text"] = "Connect"
        self.but.bind("<Button-1>",self.handlerCon)
        self.but.pack() # display button on the screen
    def handlerCon(self,event):
         global portOpened
         global flagT
         global flagWr
         global flagPP
         if "Connect"==self.but["text"]:          
            self.but["text"]="Disconnect"
            self.but["bg"]="yellow"
            objLogTxt.txt.insert(END, "Connected \n")
            #take from Listbox
            strCOMxx=objLBCOM.listPort.selection_get()
            #print(strCOMxx)
            #print(strCOMxx[3:])
            #comPortNum = (int(strCOMxx[3:])-1)
            boderate = 115200
            objSerialPort.mySer = serial.Serial(strCOMxx, boderate)
            objSerialPort.mySer.port = strCOMxx       
            portOpened=1
            objLogTxt.txt.insert(END, strCOMxx)
            objLogTxt.txt.insert(END, " port is opened. \n")
            print('COM Port is open.')
            myThread.start()
            pktProssesTread.start()
            writeThread.start()
            myClockTread.start()
            flagClk=1
            flagT=1
            flagWr=1
            objLBCOM.listPort.grid_forget()# hide COMx ListBox 
         elif "Disconnect"==self.but["text"]:
            self.but["text"]="Connect"
            self.but["bg"]="SteelBlue1"
            objSerialPort.mySer.close()
            objLogTxt.txt.insert(END, "Disconnected \n")
            print('COM Port is closed.')
            portOpened=0
            flagT  = 0
            flagWr = 0
            flagPP = 0
            flagClk= 0
            self.but.pack_forget()
            self.but.grid_forget()#hide ConDis buttun
            self.but.grid_remove()
         else:
            self.but["text"]="Error"
            objLogTxt.txt.insert(END, "Error \n")
            portOpened=0
            

class MySerialPort():
   def __init__(self):
      global portOpened
      self.mySer =  serial.Serial()
      self.mySer.baudrate = 115200
      self.mySer.timeout  = 1
      self.mySer.stopbits = 1 
      self.mySer.bytesize = 8
      portOpened=0

  #def __del__(self):

    # self.mySer.close()

#Listbox for COM port selection
class LBCOM:
    def __init__(self):
        self.listPort=Listbox(root,selectmode=SINGLE,height=3,width=16)
        self.listPort.pack()
        #self.listPort.place(x=500, y=10)
        #self.listPort.grid(row=0, column=1)
        portOpened=0
        #self.place(x=10, y=10)
        for n,s in scan():
            self.listPort.insert(END,s)
            #print "(%d) %s" % (n,s)
        self.listPort.selection_set(first=0)
        #self.listPort.bind('<<ListboxSelect>>', CurPortSelet)
    def getText(self):
        return self.listPort.selection_get()

class LogText:
    def __init__(self):
        self.txt = Text(root,width=60, font="Verdana 12", wrap=WORD,foreground="purple")
        #self.txt.tag_config(foreground="purple")
        self.txt.pack() # print



class CleanLogBut():
    def __init__(self):
        self.but=Button(root, width=20, height=2,bg = "SteelBlue1")
        self.but["text"] = "Clean log"
        self.but.bind("<Button-1>",self.handlerCleanLogButton)
        self.but.pack() # display button on the screen
    def handlerCleanLogButton(self,event):
        objLogTxt.txt.delete(1.0, END)

class QueryRadioButton0():
   def __init__(self):
      self.but = Button(root,width=20,height=2,bg = "SteelBlue1")
      self.but["text"] = "Query Radio CH0"
      self.but.bind("<Button-1>",self.handlerQueryRadioButton)
      self.but.pack() # display button on the screen
   def handlerQueryRadioButton(self,event):
      global endOfSlaveResponse 
      if portOpened==1:
        #endOfSlaveResponse =1 
        TxQueue.append(queryRadio0Package)
        TxQueue.append(getDataCh0Package)
      else:
        #print('No COM Port Open.')#for debugging
        objLogTxt.txt.insert(END, "Lack of opened serial port. \n")

class QueryRadioButton1():
   def __init__(self):
      self.but = Button(root,width=20,height=2,bg = "SteelBlue1")
      self.but["text"] = "Query Radio CH1"
      self.but.bind("<Button-1>",self.handlerQueryRadioButton)
      self.but.pack() # display button on the screen
   def handlerQueryRadioButton(self,event):
      global endOfSlaveResponse 
      if portOpened==1:
        #endOfSlaveResponse =1 
        TxQueue.append(queryRadio1Package)
        TxQueue.append(getDataCh1Package)
      else:
        #print('No COM Port Open.')#for debugging
        objLogTxt.txt.insert(END, "Lack of opened serial port. \n")         


class PollingButton():
   def __init__(self):
      self.but = Button(root,width=20,height=2,bg = "SteelBlue1")
      self.but["text"] = "polling off"
      #pollingOn=0
      self.but.bind("<Button-1>",self.handlerPollingButton)
      self.but.pack() # display button on the screen
   def handlerPollingButton(self,event):
         global pollingOn
         if "polling off"==self.but["text"]:          
             if 0==portOpened:
                 objLogTxt.txt.insert(END, "Lack of opened serial port. \n")
                 self.but["text"]="polling off"
                 self.but["bg"]="SteelBlue1"
                 pollingOn=0
             if 1==portOpened:
                 self.but["text"]="polling on"
                 self.but["bg"]="yellow"
                 pollingOn=1
         elif "polling on"==self.but["text"]:
             pollingOn=0
             self.but["text"]="polling off"
             self.but["bg"]="SteelBlue1"
         else:
            self.but["text"]="Error"



#state machine for packet recognition
def parseByte(inputData):
    global receivedPacket
    global rCounter
    global expectedSizeOfPkt
    global endOfSlaveResponse
    inData = int(inputData, 16)
    #print(inputData) # for debugging
    global rCounter
    #sync byte (header)
    if 0==rCounter:
        if 0x23 == inData:
            rxBuffer.append(inData)
            rCounter=rCounter+1
        else:
            rCounter=0
            dataSize=0
            del rxBuffer[:]
    #chanel byte (header)
    elif 1==rCounter:
        if (0x30==inData) or (0x31==inData):
            rxBuffer.append(inData)
            rCounter=rCounter+1
        else:
            rCounter=0
            dataSize=0
            del rxBuffer[:]
    #command byte  (header) 
    elif 2==rCounter:
        if 0x4B==inData:
            endOfSlaveResponse=1
            #print("Slave Listen after K")
        else:
            endOfSlaveResponse=0
        rxBuffer.append(inData)
        rCounter=rCounter+1
    #Message length in bytes   (header)
    elif 3==rCounter:
        rxBuffer.append(inData)
        rCounter=rCounter+1
        expectedSizeOfPkt =inData+4+2
    else:
        if (rCounter < (expectedSizeOfPkt-1) ):
            rxBuffer.append(inData)
            rCounter=rCounter+1
        elif ( rCounter == (expectedSizeOfPkt-1) ):
            #the last packet byte arrived. Write it into a memory and reset the reception.
            rxBuffer.append(inData)
            rCounter          = 0
            expectedSizeOfPkt = 0
            receivedPacket  =list(rxBuffer)
            objLogTxt.txt.tag_config("cc", foreground="blue")
            #int2hex(receivedPacket)
            objLogTxt.txt.insert(END, int2hex(receivedPacket), ("cc") )
            objLogTxt.txt.insert(END, "\n")
            if(1==endOfSlaveResponse):
                objLogTxt.txt.insert(END, "--->All Pkts have been received. \n")
            if (uType==receivedPacket[2]):
                #put Pkt in Queue
                RxQueue.append(receivedPacket)
            del rxBuffer[:]
        else:
            rCounter          = 0
            expectedSizeOfPkt = 0
            del rxBuffer[:]
    
def analyzeTxPkt(inArray):
    if '0'==inArray[1]:
        objLogTxt.txt.insert(END, " CH0 ")
    if '1'==inArray[1]:
        objLogTxt.txt.insert(END, " CH1 ")
    if 'G'==inArray[2]:
        objLogTxt.txt.insert(END, " G ")
    if 'Q'==inArray[2]:
        objLogTxt.txt.insert(END, " Q ")

def PutGetDataPktPackedInQueue():
   #print('Get  current status package has been sent.') # for debuggung
   global g_ch
   global TxQueue
   if 1==g_ch:
       g_ch=0
       TxQueue.append(getDataCh1Package)
   elif 0==g_ch:
       g_ch=1
       TxQueue.append(getDataCh0Package)
   else:
       g_ch=0


class CanvasPlate:
    pixelSize =1
    widthM=399+pixelSize 
    heightM=400
    offset1=300
    offset2=200
    offset3=100
    xPos =1
    def __init__(self):
        #global widthM
        #global heightM
        #widthM=400
        #heightM=400
        self.canv = Canvas(root, width=widthM, height=heightM, bg="white" )
        self.canv.pack() # display button on the screen
    def putDotOnCanva(self, x, y, plotNum):
        if(1==plotNum):
            offset = self.offset1
        if(2==plotNum):
            offset = self.offset2
        if(3==plotNum):
            offset = self.offset3
        cx1=x
        cx2=(x+self.pixelSize)
        cy1=heightM-offset-y
        cy2=heightM-offset-(y+self.pixelSize)
        
        if cx1< widthM and cx1< widthM  and cy1< heightM and cy1< heightM:
            self.canv.create_rectangle( cx1, heightM-offset, cx2, heightM-offset+1,     outline = "cyan");
            self.canv.create_rectangle( cx1, heightM-offset+histMax, cx2, heightM-offset+histMax, outline="red")
            self.canv.create_rectangle( cx1, heightM-offset-histMax, cx2, heightM-offset-histMax, outline="yellow")
            self.canv.create_rectangle( cx1, cy1, cx2, cy2, outline="black")
    def putDot(self, val,plotNum):
        self.putDotOnCanva(self.xPos, val, plotNum);
        self.xPos=self.xPos+1
        if (300<self.xPos):
            self.xPos=2
            #self.canv.delete("All")
            self.canv.create_rectangle(0, 0, widthM, heightM, fill="white")
            print "clear canvas"       
            print "Size Of Rx Queue: " + str (len(RxQueue)) 
    def plotFun1(self, yArray):
        #clean canva
        sizeOfArray = len(yArray)
        for i in range(sizeOfArray):
            self.canv.create_rectangle( i, heightM-self.offset1-yArray[i], (i+self.pixelSize),     heightM-self.offset1-(yArray[i]+self.pixelSize), outline="black");
            self.canv.create_rectangle( i, heightM-self.offset1, (i+1), heightM-self.offset1+1,               outline = "cyan");
            self.canv.create_rectangle( i, heightM-self.offset1+histMax, (i+1), heightM-self.offset1+histMax, outline="red")
            self.canv.create_rectangle( i, heightM-self.offset1-histMax, (i+1), heightM-self.offset1-histMax, outline="yellow") 
            #self.canv.pack() # display button on the screen
    def plotFun2(self, yArray):
        #clean canva
        sizeOfArray = len(yArray)
        for i in range(sizeOfArray):
            self.canv.create_rectangle(i, heightM-self.offset2-yArray[i],   (i+self.pixelSize),     heightM-self.offset2-(yArray[i]+self.pixelSize), outline="green")
            self.canv.create_rectangle(i, heightM-self.offset2, (i+1)   ,   heightM-self.offset2+1, outline="cyan")
            self.canv.create_rectangle(i, heightM-self.offset2+histMax  ,   (i+1),                  heightM-self.offset2+histMax, outline="red")
            self.canv.create_rectangle(i, heightM-self.offset2-histMax  ,   (i+1),                  heightM-self.offset2-histMax, outline="yellow") 
            
# transmit thread    
def writeSerialPort():
    global TxQueue
    global endOfSlaveResponse
    global Tout
    while flagWr:
        # Slave is in Rx mode
        if 1==endOfSlaveResponse:
            #print("Slave Speaks")
            # Is here anything to transmit?
            if 0<len(TxQueue):
                endOfSlaveResponse=0
                #eject the package from the queue
                arrayToTx = TxQueue.pop(0)
                if 0==flagWr:
                    return
                time.sleep(0.3)
                objSerialPort.mySer.write(arrayToTx)   	
                analyzeTxPkt(arrayToTx)
                objLogTxt.txt.insert(END, "package has been sent. \n")
                if ('Q'==arrayToTx[2]):
                    #MCND will not respond on Q pkt immediately
                    endOfSlaveResponse=1
                    print("Slave Listen after Q")
        Tout = Tout-1
        if( Tout < 1):
            Tout = 70
            if 1==pollingOn:
                PutGetDataPktPackedInQueue()
                PutGetDataPktPackedInQueue()
                #print "TimeOut"
                if 10<len(TxQueue):
                    #TxQueue=[]
                    #TxQueue.clear()
                    del TxQueue[:] 
                    print "clean TxQueue"
            endOfSlaveResponse=1
        time.sleep(0.01)
            #print(Tout)




#-------------------------------------------------------------------


histMax = 10
histMin = -histMax

#inputs
evUp  =0
evMid =1
evDown=2

evCnt =3

#states:
stUndefUp  =0
stMidUp    =1
stDownUp   =2
stUndefMid =3
stUpMid    =4
stDownMid  =5
stUndefDown=6
stUpDown   =7
stMidDown  =8
stUndef    =9

stCnt    =10

#actions:
actDirUp  =0
actDirDown=1
actNone   =2


#                     0           1         2        3          4           5         6             7          8         9     
#                  stUndefUp   stMidUp  stDownUp  stUndefMid  stUpMid    stDownMid  stUndefDown  stUpDown   stMidDown  stUndef     
StateTable = [    [ stUndefUp, stMidUp,  stDownUp, stMidUp,    stMidUp,   stMidUp,   stDownUp,    stDownUp,  stDownUp,  stUndefUp   ],   #evUp
                  [ stUpMid,   stUpMid,  stUpMid,  stUndefMid, stUpMid,   stDownMid, stDownMid,   stDownMid, stDownMid, stUndefMid  ],   #evMid
                  [ stUpDown , stUpDown, stUpDown, stMidDown,  stMidDown, stMidDown, stUndefDown, stUpDown,  stMidDown, stUndefDown ] ]  #evDown
             

#                     0           1           2             3          4           5         6             7          8         9     
#                   stUndefUp  stMidUp     stDownUp     stUndefMid   stUpMid     stDownMid  stUndefDown  stUpDown   stMidDown  stUndef     
ActionTable =[    [ actNone,   actNone,    actNone,     actDirUp,    actNone,    actDirUp,  actNone,     actDirUp,  actDirUp,  actDirUp ],   #evUp
                  [ actNone,   actNone,    actNone,     actNone,     actNone,    actNone,   actNone,     actNone,   actNone,   actNone ],   #evMid
                  [ actNone,   actDirDown, actDirDown,  actDirDown,  actDirDown, actNone,   actNone,     actNone,   actNone,   actDirDown ] ]  #evDown
             


def printCurState(curState):
    if (stUndefUp    == curState):
        print "stUndefUp"
    elif (stMidUp    == curState):
        print "stMidUp"
    elif (stDownUp   == curState):
        print "stDownUp"
    elif (stUndefMid == curState):
        print "stUndefMid"
    elif (stUpMid    == curState):
        print "stUpMid"
    elif (stDownMid  == curState):
        print "stDownMid"
    elif (stUndefDown== curState):
        print "stUndefDown"
    elif (stUpDown   == curState):
        print "stUpDown"
    elif (stMidDown  == curState):
        print "stMidDown"
    elif (stUndef    == curState):
        print "stUndef"
    else:
        print "error: unKnowState"


def printOurPut(outPut):
    if outPut==actDirUp:
        print "actDirUp"
    elif outPut==actDirDown:
        print "actDirDown"
    elif outPut==actNone:
        print "actNone"
    else:
        print "unknow act"

        
class SchmittFlipFlop:
    curState = stUndef
    inPut    = evMid
    outPut   = actNone
    thresholdRSSIdiff = histMax
    def __init__(self):
        self.curState = stUndef
        self.inPut = evMid
        self.outPut = 0
        self.thresholdRSSIdiff=histMax
    def GetInput(self, rssiDiff):
        if self.thresholdRSSIdiff<rssiDiff:
            self.inPut = evUp
            #print "Up"
        elif rssiDiff<-self.thresholdRSSIdiff:
            self.inPut = evDown
            #print "Down"
        else:
            self.inPut = evMid
            #print "Mid"     
    def GetState(self):
        if(self.inPut<evCnt  and   self.curState< stCnt):
            self.curState = StateTable[self.inPut][self.curState]
            #printCurState(self.curState)
        else:
            print "inPut"
            print self.inPut
            print "curState"
            print self.curState
            print "error inPut or State in State Table"
        return self.curState
    def doAction(self):
        if(self.inPut<evCnt  and  self.curState< stCnt):
            self.action = ActionTable[self.inPut][self.curState]
            if(actDirUp==self.action):
                self.outPut=1.5*histMax
                print "dirUp"
            if(actDirDown==self.action):
                self.outPut=-1.5*histMax
                print "dirDown"
        else:
            print "inPut"
            print self.inPut
            print "curState"
            print self.curState
            print "error: inPut or State in Action Table "
    def getAction(self):
        return self.outPut
        

  

class FIRfilter:
    lenOffilter=0
    inPutSignal=[]
    outPutSignal=0
    def __init__(self):
        self.inPutSignal  = []
        self.outPutSignal = 0
        self.lenOffilter  = 10
    def PutValue(self, val):
        self.inPutSignal.append(val)
        if ( self.lenOffilter<len(self.inPutSignal) ):
            self.inPutSignal.pop(0)
    def calcOutPut(self):
        self.outPutSignal = sum(self.inPutSignal)/self.lenOffilter 
    def GetValue(self):
        return self.outPutSignal
    def calcFIRout(self, val):
        self.inPutSignal.append(val)
        if ( self.lenOffilter<len(self.inPutSignal) ):
            self.inPutSignal.pop(0)
        self.outPutSignal = sum(self.inPutSignal)/self.lenOffilter 
        return self.outPutSignal
    
    
def putValueInShiftRawReg(xVal, yVal):
    global timeArray
    global rawRssiArray
    global lenthOfPlotx
    timeArray.append(xVal)
    rawRssiArray.append(yVal)
    if lenthOfPlotx<len(timeArray):
        timeArray.pop(0)
    if lenthOfPlotx<len(rawRssiArray):
        rawRssiArray.pop(0)

def putValueInShiftFirReg(xVal, yVal):
    global firRssiArray
    global lenthOfPlotx
    firRssiArray.append(yVal)
    if lenthOfPlotx<len(firRssiArray):
        firRssiArray.pop(0)


class Beacon():
    ID=0
    RSSIch0=255
    RSSIch1=255
    TTL=0
    def __init__(self):
        self.ID=0
        self.RSSIch0=255
        self.RSSIch1=255
        self.TTL=0
    def upDateBeacon(self, uPkt):
        #           0                  1                  2                 3                 4           5        6        7         8            9
        #_-------------------------------------------------------------------------------------------------------------------------------------------------
        #     Start character  |  channel number  |  Command  Message  |  length in bytes  |  ID hi  |  Idlow  |  flags  |  rssi  |  CRC16Hi  |  CRC16Lo  |
        #--------------------------------------------------------------------------------------------------------------------------------------------------
        #
        self.ID = extractID(uPkt)
        if(uType==uPkt[2]):#Type
            if (0x30==uPkt[1]): #Ch
                self.RSSIch0  = uPkt[7]
            if (0x31==uPkt[1]): #Ch
                self.RSSIch1  = uPkt[7]               
    def printRssiPlot(self):
        global myFile
        global timeArray
        global cutTime
        global rawRssiArray
        global histMax
        if(self.ID==17839):
            curRssiDiff = self.RSSIch1-self.RSSIch0
            #print  "17839: " + " RSSI ch1 " + str(self.RSSIch1) + " RSSI ch0 " + str(self.RSSIch0) +" < "+ str(curRssiDiff)+ " > "
            curRssiDiffFir = objFIRfilter.calcFIRout(curRssiDiff)
            cutTime=cutTime+1
            objSchmittFlipFlop.GetInput(curRssiDiffFir)
            objSchmittFlipFlop.doAction()
            objSchmittFlipFlop.GetState()
            FFoutPut = objSchmittFlipFlop.getAction()
            objCanvasPlate.putDot(curRssiDiff, 1)
            objCanvasPlate.putDot(curRssiDiffFir, 2)
            objCanvasPlate.putDot(FFoutPut, 3)
            myFile.write(" "+ str(curRssiDiff) +"  "+str(curRssiDiffFir)+"  "+ str(FFoutPut) +" "+ str(histMax)+" "+ str(clkTick) +  "  \n" )


            
            
                    
              
def extractID(inPutUpkt):
    ID=0;
    IDhi= (inPutUpkt[4]<<8)
    IDlo= inPutUpkt[5]
    ID = ID | (  IDhi | IDlo  )
    return ID 
    

# read thread        
def readSerialPort():
    while flagT:
        #print(rCounter)# for debuggung
        data = objSerialPort.mySer.read(1);
        parseByte(data.encode('hex'))
    print "readSerialPort is over" 

def pktProsses():
    print "File Opened"
    global  myFile 
    while flagPP:
        inPutUpkt = []
        if(0<len(RxQueue)):
            inPutUpkt=RxQueue.pop(0)
            #print "detected ID"
            ID = extractID(inPutUpkt)
            #print ID
            #Is that Id in Table
            sizeOfListOfReacon = len(ListOfBeacons)
            lackID=1
            for i in range(sizeOfListOfReacon):
                if (ID==ListOfBeacons[i].ID):
                    #update  RSSI
                    lackID=0 
                    ListOfBeacons[i].upDateBeacon(inPutUpkt)
                    ListOfBeacons[i].printRssiPlot() 
            #there are no ID in the list
            if 1==lackID:
                objBeacon=Beacon()
                objBeacon.upDateBeacon(inPutUpkt)
                #put ID in the list
                ListOfBeacons.append(objBeacon)
            
    print "pktProsses  is over"
    myFile.close()
    print("Файл закрыт: ")
        


def myClock():
    global clkTick
    while flagClk:
        clkTick=clkTick+1
        time.sleep(0.2)  
    print "myClock  is over"

 

myClockTread = threading.Thread(target=myClock, name='myClock')
myClockTread.daemon = True
flagClk=1       

myThread = threading.Thread(target=readSerialPort, name='readCOMportThread')
myThread.daemon = True
flagWr=1

writeThread = threading.Thread(target=writeSerialPort, name='writeCOMportThread')
writeThread.daemon = True
flagT=1

pktProssesTread = threading.Thread(target=pktProsses, name='pktProssesTread')
pktProssesTread.daemon = True
flagPP=1

root = Tk()

currentTime = datetime.datetime.now().time()

key= random.random()
fileName ="RSSIdiffLog"+str(currentTime) + ".txt"

print currentTime
print fileName
myFile = open(fileName, "w")


clkTick=0

widthM=400
heightM=400
        
expectedSizeOfPkt  = 0;
rCounter           = 0  
g_ch               = 0  
rxBuffer           = [] 
receivedPacket     = []
pollingOn          = 0
endOfSlaveResponse = 1;
TxQueue            = []
RxQueue            = []
cutTime            = 0
lenthOfPlotx       = 350
ListOfBeacons      = []
Tout = 100;


histMax =  10
histMin = -histMax
                                       

timeArray    = []
rawRssiArray = []
firRssiArray = []


objSerialPort        = MySerialPort()
objLBCOM             = LBCOM()
objConDisBut         = ConDis()
objLogTxt            = LogText()
objCleanLogBut       = CleanLogBut()
objQueryRadioButton0 = QueryRadioButton0()
objQueryRadioButton1 = QueryRadioButton1()
objPollingButton     = PollingButton()
objCanvasPlate       = CanvasPlate()
objFIRfilter=FIRfilter()
objSchmittFlipFlop = SchmittFlipFlop()


	



root.mainloop()
