#           SolarEdge modbus over TCP/IP Python Plugin for Domoticz
#

# Below is what will be displayed in Domoticz GUI under HW
#
"""
<plugin key="SolarEdgeModBus" name="SolarEdge Modbus over TCP/IP" author="pawcio" version="1.0.0" wikilink="no" >
    <params>
        <param field="Address" label="IP Address" width="200px" required="true" default="192.168.1.25"/>
        <param field="Port" label="Port" width="40px" required="true" default="502"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="True" />
            </options>
        </param>
    </params>
</plugin>
"""
#
# Main Import
import Domoticz

class BasePlugin:

    conn = None
    config = None
    id = 0
    power = "0;0"
    currentL1L2L3 = "0;0;0"

    # Domoticz call back functions
    #
            
    # Executed once at HW creation/ update. Can create up to 255 devices.
    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)
            DumpConfigToLog()

        # Do not change below UNIT constants!

        self.UNIT_L1_POWER = 1
        self.UNIT_L2_POWER = 2
        self.UNIT_L3_POWER = 3
        self.UNIT_ALL_POWER = 4
        self.UNIT_CURRENT_L1_L2_L3 = 5

        if (len(Devices) == 0):
            Domoticz.Device(Name="Power", Unit=self.UNIT_ALL_POWER, TypeName="kWh").Create()
            Domoticz.Device(Name="Current", Unit=self.UNIT_CURRENT_L1_L2_L3, Type=89).Create() 
            Domoticz.Log("Devices created.")
        else:
            self.power = Devices[self.UNIT_ALL_POWER].sValue 
            self.currentL1L2L3 = Devices[self.UNIT_CURRENT_L1_L2_L3].sValue 

        Domoticz.Heartbeat(60)

        self.config = {
            "description": "Domoticz",
            "host": Parameters["Address"],
            "port": Parameters["Port"],
        }

        Domoticz.Log("SolarEdge onStart: " + Parameters["Address"] + ":" + Parameters["Port"])

        return True
            
    def onConnect(self, Connection, Status, Description):
        success = False

        if (Connection == self.conn):
            if (Status == 0):
                if Parameters["Mode6"] == "Debug":
                    Domoticz.Log("SolarEdge plugin -> Connected successfully to: "+Connection.Address)
                success = True
                #todo if needed...

        if False == success:
            Domoticz.Log("SolarEdge plugin -> Failed to connect ("+str(Status)+") to: "+Parameters["Address"]+" with error: "+Description)
            self.conn = None
            self.SyncDevices(1)


    def refreshData(self):
        
        if self.conn:
            b = b'\x00\x00\x00\x06\x01\x03\x9c\x85\x00\x32'
            self.conn.Send(self.id.to_bytes(2, byteorder='big') + b) 
            self.id += 1
        else:
            if self.conn == None:
                self.handleConnect()
        
    def onHeartbeat(self):
        #Domoticz.Log("onHeartbeat called")

        #Disabled temporary
        #self.refreshData()

        return True

    def onMessage(self, Connection, Data):
        
        #Domoticz.Log("onMessage called: " + str(Data) + " , Connection: " + str(Connection))

        # out = ''
        # for i in range(10):
        #     out += (str(Data[i]) + ', ')
        # Domoticz.Log(out)

        typeDID = int.from_bytes(Data[9:11], byteorder='big')
        current = int.from_bytes(Data[13:15], byteorder='big')
        currentA = int.from_bytes(Data[15:17], byteorder='big')
        currentB = int.from_bytes(Data[17:19], byteorder='big')
        currentC = int.from_bytes(Data[19:21], byteorder='big')
        currentSF = int.from_bytes(Data[21:23], byteorder='big', signed=True)

        voltageAB = int.from_bytes(Data[23:25], byteorder='big')
        voltageBC = int.from_bytes(Data[25:27], byteorder='big')
        voltageCA = int.from_bytes(Data[27:29], byteorder='big')
        voltageAN = int.from_bytes(Data[29:31], byteorder='big')
        voltageBN = int.from_bytes(Data[31:33], byteorder='big')
        voltageCN = int.from_bytes(Data[33:35], byteorder='big')
        voltageSF = int.from_bytes(Data[35:37], byteorder='big', signed=True)

        power = int.from_bytes(Data[37:39], byteorder='big', signed=True)
        powerSF = int.from_bytes(Data[39:41], byteorder='big', signed=True)

        freq = int.from_bytes(Data[41:43], byteorder='big')
        freqSF = int.from_bytes(Data[43:45], byteorder='big', signed=True)

        energy = int.from_bytes(Data[57:61], byteorder='big')
        energySF = int.from_bytes(Data[61:63], byteorder='big')

        dcCurrent = int.from_bytes(Data[63:65], byteorder='big')
        dcCurrentSF = int.from_bytes(Data[65:67], byteorder='big', signed=True)
        dcVoltage = int.from_bytes(Data[67:69], byteorder='big')
        dcVoltageSF = int.from_bytes(Data[69:71], byteorder='big', signed=True)
        dcPower = int.from_bytes(Data[71:73], byteorder='big', signed=True)
        dcPowerSF = int.from_bytes(Data[73:75], byteorder='big', signed=True)

        # I've problem with reading those values
        # temp = int.from_bytes(Data[75:77], byteorder='big', signed=True)
        # tempSF = int.from_bytes(Data[77:79], byteorder='big', signed=True)

        if Parameters["Mode6"] == "Debug":
            Domoticz.Log("Type DID: " + str(typeDID))
            Domoticz.Log("Current: " + str(current * (10**currentSF)))
            Domoticz.Log("CurrentA: " + str(currentA * (10**currentSF)))
            Domoticz.Log("CurrentB: " + str(currentB * (10**currentSF)))
            Domoticz.Log("CurrentC: " + str(currentC * (10**currentSF)))

            Domoticz.Log("voltageAN: " + str(voltageAN * (10**voltageSF)))
            Domoticz.Log("voltageBN: " + str(voltageBN * (10**voltageSF)))
            Domoticz.Log("voltageCN: " + str(voltageCN * (10**voltageSF)))

            Domoticz.Log("Power: " + str(power * (10**powerSF)))
            Domoticz.Log("Freq: " + str(freq * (10**freqSF)))
            Domoticz.Log("Energy: " + str(energy * (10**energySF)))
            
            Domoticz.Log("dc voltage: " + str(dcVoltage * (10**dcVoltageSF)))
            Domoticz.Log("dc current: " + str(dcCurrent * (10**dcCurrentSF)))
            Domoticz.Log("dc power: " + str(dcPower * (10**dcPowerSF)))
            # Domoticz.Log("temp: " + str(temp))
            # Domoticz.Log("tempSF: " + str(tempSF))

        self.power = str(power * (10**powerSF)) + ";" + str(energy * (10**energySF))
        self.currentL1L2L3 = str(currentA * (10**currentSF)) + ";" + str(currentB * (10**currentSF)) + ";" +str(currentC * (10**currentSF))

        self.SyncDevices(0)
            
        return

    # def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
    #     Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(
    #         Priority) + "," + Sound + "," + ImageFile)
    #     return

    def onDisconnect(self, Connection):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Log("Device has disconnected")
        self.conn = None
        return

    def onStop(self):
        Domoticz.Log("onStop called")
        return True

    def handleConnect(self):
        self.id = 0
        self.conn = Domoticz.Connection(Name="SolarEdge", Transport="TCP/IP", Protocol="None", Address=self.config["host"], Port=self.config["port"])

        self.conn.Connect()

    def SyncDevices(self, TimedOut):
    
        UpdateDevice(self.UNIT_ALL_POWER, 0, self.power, TimedOut)
        UpdateDevice(self.UNIT_CURRENT_L1_L2_L3, 0, self.currentL1L2L3, TimedOut)        

        return

#    def onCommand(self, Unit, Command, Level, Hue):
#       Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
#       
#       if 99 == Level:
#           self.refreshData()

    def onDeviceModified(self, Unit):
        
        Device = Devices[Unit]
        Domoticz.Log("onDeviceModified called for Unit " + str(Unit) + " " + str(Device))
        if 99 == Device.nValue:
            Domoticz.Log("Refresh data")
            self.refreshData()
            
            
            
################ base on example ######################
global _plugin
_plugin = BasePlugin()


def onStart():
    global _plugin
    _plugin.onStart()


def onStop():
    global _plugin
    _plugin.onStop()


def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)


def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)


#def onCommand(Unit, Command, Level, Hue):
#   global _plugin
#   _plugin.onCommand(Unit, Command, Level, Hue)

def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)

# def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
#     global _plugin
#     _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)


def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)


def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()


# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    #Domoticz.Debug("Settings count: " + str(len(Settings)))
    # for x in Settings:
    #     Domoticz.Debug("'" + x + "':'" + str(Settings[x]) + "'")
    Domoticz.Debug("Image count: " + str(len(Images)))
    for x in Images:
        Domoticz.Debug("'" + x + "':'" + str(Images[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device Image:     " + str(Devices[x].Image))
    return


def UpdateDevice(Unit, nValue, sValue, TimedOut):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue=nValue, sValue=str(sValue), TimedOut=TimedOut)
            Domoticz.Log("Update " + str(nValue) + ":'" + str(sValue) + "' (" + Devices[Unit].Name + ")")
    return
    