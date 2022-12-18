from printers.protocol_types import *


Ethernet = Module("Ethernet")

Ethernet[""] = Line()
Ethernet["minPacketSize"] = Constant(64, uint8("dec"))
Ethernet["maxPacketSize"] = Constant(1518, uint8("dec"))
Ethernet["maxPayloadSize"] = Constant(1500, uint8("dec"))
Ethernet["headerSize"] = Constant(14, uint8("dec"))

Ethernet[""] = Line()
Ethernet["etherType_ARP"] = Constant(0x0806, uint8("hex"))
Ethernet["etherType_IPv4"] = Constant(0x0800, uint8("hex"))
Ethernet["etherType_IPv6"] = Constant(0x86DD, uint8("hex"))
Ethernet["etherType_PROFINET"] = Constant(0x8892, uint8("hex"))
Ethernet["etherType_EtherCAT"] = Constant(0x88A4, uint8("hex"))

Ethernet[""] = Line()
Ethernet["MACAddress"] = TypeAlias(Array(partbyte(), 6))
Ethernet["IPAddress"] = TypeAlias(Array(partbyte(), 4))

Ethernet[""] = Line()
Ethernet["Header"] = Structure(attributes = [PackedAttribute()], fields = [
    Field("sourceMAC", Reference("MACAddress", Ethernet)),
    Field("destinationMAC", Reference("MACAddress", Ethernet)),
    Field("typeOrLength", uint16()),
])
