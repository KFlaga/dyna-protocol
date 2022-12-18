import ethernet.ethernet as ethernet
from printers.protocol_types import *

ARP = Module("ARP")
ARP.add_import(ethernet.Ethernet)

ARP[""] = Line()
ARP["headerSize"] = Constant(28, uint8("dec"))

ARP["hardwareType_Ethernet"] = Constant(1, uint8("hex"))
ARP["protocolType_IPv4"] = Constant(0x0800, uint8("hex"))
ARP["hardwareAddressLength_Ethernet"] = Constant(6, uint8("dec"))
ARP["protocolAddressLength_IPv4"] = Constant(4, uint8("dec"))

ARP["operation_request"] = Constant(1, uint16("dec"))
ARP["operation_reply"] = Constant(2, uint16("dec"))
ARP["operation_requestReverse"] = Constant(3, uint16("dec"))
ARP["operation_replyReverse"] = Constant(4, uint16("dec"))
ARP["operation_InARP_request"] = Constant(8, uint16("dec"))
ARP["operation_InARP_reply"] = Constant(9, uint16("dec"))
ARP["operation_ARP_NAK"] = Constant(10, uint16("dec"))

ARP[""] = Line()
ARP["Header"] = Structure(attributes = [PackedAttribute()], fields = [
    Field("hardwareType", uint16()),
    Field("protocolType", uint16()),
    Field("hardwareAddressLength", uint8()),
    Field("protocolAddressLength", uint8()),
    Field("operation", uint16()),
    Field("senderHardwareAddress", Reference("MACAddress", ethernet.Ethernet)),
    Field("senderProtocolAddress", Reference("IPAddress", ethernet.Ethernet)),
    Field("targetHardwareAddress", Reference("MACAddress", ethernet.Ethernet)),
    Field("targetProtocolAddress", Reference("MACAddress", ethernet.Ethernet)),
])
