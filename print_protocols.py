import printers.protocol_c_printer as protocol_c_printer
import printers.protocol_c_sharp_printer as protocol_c_sharp_printer
import printers.protocol_cpp_printer as protocol_cpp_printer
import printers.protocol_types as protocol_types

import ethernet.ethernet as ethernet
import ethernet.arp as arp

import os
from shutil import copyfile


ethernet_protocol = protocol_types.Protocol("EthernetProtocol", [
    ethernet.Ethernet,
    arp.ARP,
])


if __name__ == "__main__":
    cs_output_dir = os.path.join("out", "cs")
    c_output_dir = os.path.join("out", "c")
    cpp_output_dir = os.path.join("out", "cpp")

    try: os.makedirs(cs_output_dir)
    except: pass
    try: os.makedirs(c_output_dir)
    except: pass
    try: os.makedirs(cpp_output_dir)
    except: pass
        
    protocol_c_sharp_printer.CSharpPrinter(ethernet_protocol).print_to_file(cs_output_dir)
    protocol_cpp_printer.CppPrinter(ethernet_protocol).print_to_file(cpp_output_dir)
    protocol_c_printer.CPrinter(ethernet_protocol).print_to_file(c_output_dir)
    copyfile(os.path.join("codec", "codec.hpp"), os.path.join(cpp_output_dir, "codec.hpp"))
