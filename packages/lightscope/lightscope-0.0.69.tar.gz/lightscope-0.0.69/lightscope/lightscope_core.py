# Standard library imports
import argparse
import collections
import configparser
import datetime
import hashlib
import ipaddress
import json
import logging
import multiprocessing
import os
import queue
import random
import re
import socket
import string
import sys
import threading
import time
from collections import defaultdict, deque, OrderedDict
from sys import platform

# Third-party imports
import dpkt
import platform as platforminfo
import psutil
import requests


benchmark_times=[]

def create_manager_with_retry(max_retries=3):
    """Create multiprocessing Manager with retry logic"""
    import time
    
    for attempt in range(max_retries):
        try:
            print(f"[Manager] Creating Manager (attempt {attempt + 1}/{max_retries})")
            manager = multiprocessing.Manager()
            
            # Test the manager by creating and accessing a simple dict
            test_dict = manager.dict()
            test_dict['test'] = 'value'
            _ = test_dict['test']  # This will fail if Manager is broken
            del test_dict['test']
            
            print("[Manager] Successfully created and tested Manager")
            return manager
            
        except Exception as e:
            print(f"[Manager] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
            else:
                print("[Manager] All attempts failed, processes will use local dictionaries")
                return None
    
    return None

verbose=1
if verbose == 0:
    logging.root.setLevel(logging.NOTSET)
    logging.basicConfig(level=logging.NOTSET)
elif verbose == 1:
    logging.root.setLevel(logging.WARNING)
    logging.basicConfig(level=logging.WARNING)
elif verbose == 2:
    logging.root.setLevel(logging.ERROR)
    logging.basicConfig(level=logging.ERROR)





# packet_info.py
import dpkt
import datetime
import socket
import struct
from collections import namedtuple


def parse_ethernet(packet_bytes, datalink):
    """
    Parse the packet bytes using the appropriate dpkt class based on the datalink type.
    """
    # DLT_EN10MB = 1: Standard Ethernet.
    if datalink == dpkt.pcap.DLT_EN10MB:
        try:
            eth = dpkt.ethernet.Ethernet(packet_bytes)
        except Exception as e:
            raise Exception(f"Ethernet parsing failed: {e}")
    # DLT_LINUX_SLL = 113: Linux cooked capture.
    elif datalink == 113:
        try:
            # dpkt.sll.SLL parses Linux cooked capture packets.
            # Note: SLL packets don't automatically convert to an Ethernet frame,
            # so we might need to adjust how we extract the IP packet.
            sll = dpkt.sll.SLL(packet_bytes)
            # sll.data should contain the encapsulated packet. In many cases it is already an IP packet.
            if not isinstance(sll.data, dpkt.ip.IP):
                raise Exception("Not an IP packet inside SLL")
            eth = sll  # We use the SLL object as our 'eth' equivalent.
        except Exception as e:
            raise Exception(f"Linux cooked capture parsing failed: {e}")
    else:
        raise Exception(f"Unsupported datalink type: {datalink}")
    return eth

#begin packetin
# Define the namedtuple for packet information.
PacketInfo = namedtuple("PacketInfo", [
    "packet_num", "proto", "packet_time",
    "ip_version", "ip_ihl", "ip_tos", "ip_len", "ip_id", "ip_flags", "ip_frag",
    "ip_ttl", "ip_proto", "ip_chksum", "ip_src", "ip_dst", "ip_options",
    "tcp_sport", "tcp_dport", "tcp_seq", "tcp_ack", "tcp_dataofs",
    "tcp_reserved", "tcp_flags", "tcp_window", "tcp_chksum", "tcp_urgptr", "tcp_options"
])


def tcp_flags_to_str(flags_value):
    """Convert dpkt TCP flags value to a comma-separated string."""
    flag_names = []
    if flags_value & dpkt.tcp.TH_FIN:
        flag_names.append("FIN")
    if flags_value & dpkt.tcp.TH_SYN:
        flag_names.append("SYN")
    if flags_value & dpkt.tcp.TH_RST:
        flag_names.append("RST")
    if flags_value & dpkt.tcp.TH_PUSH:
        flag_names.append("PSH")
    if flags_value & dpkt.tcp.TH_ACK:
        flag_names.append("ACK")
    if flags_value & dpkt.tcp.TH_URG:
        flag_names.append("URG")
    return ",".join(flag_names) if flag_names else ""


import struct, socket, datetime
import dpkt

ETH_HDR_LEN = 14
ETH_P_IP    = 0x0800
ETH_P_IPV6  = 0x86DD
ETH_P_8021Q = 0x8100

def parse_packet_info_fast(buf: bytes, pkt_no: int) -> PacketInfo:
    # --- L2 ----------------------------------------------------------------
    eth_type = struct.unpack('!H', buf[12:14])[0]
    off = ETH_HDR_LEN
    if eth_type == ETH_P_8021Q:          # optional VLAN tag
        eth_type = struct.unpack('!H', buf[16:18])[0]
        off += 4

    # --- IPv4 path ---------------------------------------------------------
    if eth_type == ETH_P_IP:
        ip4 = dpkt.ip.IP(buf[off:])
        if ip4.p != dpkt.ip.IP_PROTO_TCP:
            raise Exception(f"Not TCP (IPv4 proto={ip4.p})")
        ip_hdr_len = ip4.hl * 4
        tcp = dpkt.tcp.TCP(buf[off + ip_hdr_len:])
        src = socket.inet_ntoa(ip4.src)
        dst = socket.inet_ntoa(ip4.dst)
        ip_opts = ip4.opts.hex() if ip4.opts else ""

        # Build flags string from individual flag properties
        flags = []
        if ip4.df:
            flags.append("DF")
        if ip4.mf:
            flags.append("MF")
        ip_flags_str = ",".join(flags) if flags else ""

        return PacketInfo(
            packet_num   = pkt_no,
            proto        = "TCP",
            packet_time  = datetime.datetime.now().timestamp(),

            ip_version   = ip4.v,
            ip_ihl       = ip4.hl,
            ip_tos       = ip4.tos,
            ip_len       = ip4.len,
            ip_id        = ip4.id,
            ip_flags     = ip_flags_str,
            ip_frag      = ip4.offset >> 3,  # offset is in bytes, convert to 8-byte units
            ip_ttl       = ip4.ttl,
            ip_proto     = ip4.p,
            ip_chksum    = ip4.sum,
            ip_src       = src,
            ip_dst       = dst,
            ip_options   = ip_opts,

            tcp_sport    = tcp.sport,
            tcp_dport    = tcp.dport,
            tcp_seq      = tcp.seq,
            tcp_ack      = tcp.ack,
            tcp_dataofs  = tcp.off * 4,
            tcp_reserved = 0,
            tcp_flags    = tcp_flags_to_str(tcp.flags),
            tcp_window   = tcp.win,
            tcp_chksum   = tcp.sum,
            tcp_urgptr   = tcp.urp,
            tcp_options  = tcp.opts
        )

   # --- IPv6 path ---------------------------------------------------------
    elif eth_type == ETH_P_IPV6:
        # pull out the fixed 40-byte IPv6 header
        hdr = buf[off:off+40]

        # next header is at hdr[6]
        nh = hdr[6]
        # drop anything that's not TCP
        if nh != dpkt.ip.IP_PROTO_TCP:
            raise Exception(f"Not TCP (IPv6 next header={nh})")

        # now you know it's TCP, so parse the 40-byte header + TCP
        tcphdr_start = off + 40
        ip6 = dpkt.ip6.IP6(hdr + buf[tcphdr_start:])  # or just use hdr+buf and slice as you like
        tcp = dpkt.tcp.TCP(buf[tcphdr_start:])

        src = socket.inet_ntop(socket.AF_INET6, hdr[8:24])
        dst = socket.inet_ntop(socket.AF_INET6, hdr[24:40])

        # pack our IPv6 header summary into ip_options
        ver_tc_fl = struct.unpack('!I', hdr[0:4])[0]
        tc    = (ver_tc_fl >> 20) & 0xFF
        flow  = ver_tc_fl & 0xFFFFF
        plen  = struct.unpack('!H', hdr[4:6])[0]
        hlim  = hdr[7]
        ip_opts = f"tc={tc},flow={flow},plen={plen},nh={nh},hlim={hlim}"

        return PacketInfo(
            packet_num   = pkt_no,
            proto        = "TCP",
            packet_time  = datetime.datetime.now().timestamp(),

            ip_version   = 6,
            ip_ihl       = None,
            ip_tos       = None,
            ip_len       = plen,
            ip_id        = None,
            ip_flags     = "",
            ip_frag      = 0,
            ip_ttl       = hlim,
            ip_proto     = nh,
            ip_chksum    = None,
            ip_src       = src,
            ip_dst       = dst,
            ip_options   = ip_opts,

            tcp_sport    = tcp.sport,
            tcp_dport    = tcp.dport,
            tcp_seq      = tcp.seq,
            tcp_ack      = tcp.ack,
            tcp_dataofs  = tcp.off * 4,
            tcp_reserved = 0,
            tcp_flags    = tcp_flags_to_str(tcp.flags),
            tcp_window   = tcp.win,
            tcp_chksum   = tcp.sum,
            tcp_urgptr   = tcp.urp,
            tcp_options  = tcp.opts
        )

    else:
        raise Exception(f"Unsupported ethertype 0x{eth_type:04x}")



# Expanded mapping from IANA Kind values  names
TCP_OPT_NAMES = {
    0:  "EOL",
    1:  "NOP",
    2:  "MSS",
    3:  "WSCALE",
    4:  "SACK_PERMITTED",
    5:  "SACK",
    6:  "ECHO",
    7:  "ECHO_REPLY",
    8:  "TIMESTAMP",
    9:  "PARTIAL_ORDER",
    10: "PARTIAL_ORDER_SERVICE_PROFILE",
    11: "CC",
    12: "CC.NEW",
    13: "CC.ECHO",
    14: "ALT_CHECKSUM_REQUEST",
    15: "ALT_CHECKSUM_DATA",
    16: "TCP_MD5_SIG",
    17: "TCP_FASTOPEN",
    18: "TCP_FASTOPEN_COOKIE",
    19: "TCP_AUTHENTICATION",  # RFC 5925
    # and any future ones will be rendered as OPT<kind>
}

def human_readable_tcp_opts(raw_opts: bytes) -> list[str]:
    """
    Turn the raw TCP-options bytes into a list of humanreadable strings.
    Unknown kinds become "OPT<kind>".
    """
    out = []
    if not raw_opts:
        return out

    for kind, data in dpkt.tcp.parse_opts(raw_opts):
        name = TCP_OPT_NAMES.get(kind, f"OPT{kind}")

        # Endoflist
        if kind == 0:
            out.append(name)
            break

        # Noop
        if kind == 1:
            out.append(name)
            continue

        # All the singlevalue options:
        if kind == 2 and len(data) == 2:  # MSS
            (mss,) = struct.unpack("!H", data)
            out.append(f"{name}={mss}")
        elif kind == 3 and len(data) == 1:  # Window Scale
            w = data[0]
            out.append(f"{name}={w}")
        elif kind == 4:  # SACK Permitted
            out.append(name)
        elif kind == 5:  # SACK blocks
            sacks = []
            for i in range(0, len(data), 8):
                start, end = struct.unpack("!II", data[i : i + 8])
                sacks.append(f"{start}-{end}")
            out.append(f"{name}={'|'.join(sacks)}")
        elif kind in (6, 7):  # Echo / Echo Reply (each 4bytes)
            if len(data) == 4:
                (val,) = struct.unpack("!I", data)
                out.append(f"{name}={val}")
            else:
                out.append(name)
        elif kind == 8 and len(data) == 8:  # Timestamp
            tsval, tsecr = struct.unpack("!II", data)
            out.append(f"{name} val={tsval}, echo={tsecr}")
        elif kind in (9, 10):  # Partial Order (no payload)
            out.append(name)
        elif kind in (11, 12, 13):  # CC, CC.NEW, CC.ECHO (each 4bytes)
            if len(data) == 4:
                (ccv,) = struct.unpack("!I", data)
                out.append(f"{name}={ccv}")
            else:
                out.append(name)
        elif kind in (14, 15):  # Alternate checksum
            out.append(f"{name} len={len(data)}")
        elif kind == 16 and len(data) == 16:  # MD5 Signature
            out.append(f"{name}={data.hex()}")
        elif kind == 17:  # Fast Open
            out.append(f"{name} cookie_len={len(data)}")
        elif kind == 18:  # Fast Open Cookie (server)
            out.append(f"{name} cookie_len={len(data)}")
        elif kind == 19:  # TCP Authentication (timestamp + signature)
            out.append(f"{name} len={len(data)}")
        else:
            # any future or unhandled option
            out.append(f"{name} len={len(data)}")

    return out

def parse_packet_info(packet_bytes, packet_number, datalink=dpkt.pcap.DLT_EN10MB):
    """
    Parse raw packet bytes using dpkt and return a PacketInfo namedtuple.
    
    Raises:
        Exception: if the packet is not Ethernet/IP/TCP.
    """
    # Use current timestamp (you could use a timestamp from a pcap if available)
    packet_time = datetime.datetime.now().timestamp()
    
    # Parse the Ethernet frame.
    try:
        eth = dpkt.ethernet.Ethernet(packet_bytes)
    except Exception as e:
        raise Exception(f"Could not parse Ethernet frame: {e}")
    
    # Depending on the datalink type, the IP packet may be in different attributes.
    # For Ethernet, the payload is in eth.data.
    if not isinstance(eth.data, dpkt.ip.IP):
        raise Exception("Not an IP packet")
    ip = eth.data

    # Ensure the IP payload is a TCP segment.
    if not isinstance(ip.data, dpkt.tcp.TCP):
        raise Exception("Not a TCP packet")
    tcp = ip.data
    tcp = ip.data

    # Extract IP header fields.
    ip_version = ip.v
    ip_ihl = ip.hl
    ip_tos = ip.tos
    ip_len = ip.len
    ip_id = ip.id
    # ip.off encodes the flags in the upper 3 bits and fragment offset in the lower 13 bits.
    # Use modern dpkt properties instead of deprecated ip.off
    flags = []
    if ip.df:
        flags.append("DF")
    if ip.mf:
        flags.append("MF")
    ip_flags = ",".join(flags) if flags else ""
    ip_frag = ip.offset >> 3  # offset is in bytes, convert to 8-byte units
    ip_ttl = ip.ttl
    ip_proto = ip.p if hasattr(ip, 'p') else ip.proto
    ip_chksum = ip.sum if hasattr(ip, 'sum') else ip.chksum
    ip_src = socket.inet_ntoa(ip.src)
    ip_dst = socket.inet_ntoa(ip.dst)
    ip_options = ip.opts.hex() if hasattr(ip, 'opts') and ip.opts else ""

    # Extract TCP header fields.
    tcp_sport = tcp.sport
    tcp_dport = tcp.dport
    tcp_seq = tcp.seq
    tcp_ack = tcp.ack
    tcp_dataofs = tcp.off * 4  # dpkt.tcp.TCP.off is in 32-bit words.
    tcp_reserved = 0  # dpkt does not provide reserved bits directly.
    tcp_flags = tcp_flags_to_str(tcp.flags)
    tcp_window = tcp.win
    tcp_chksum = tcp.sum if hasattr(tcp, 'sum') else tcp.chksum
    tcp_urgptr = tcp.urp
    tcp_options = tcp.opts

    # Return the PacketInfo named tuple.
    return PacketInfo(
        packet_num=packet_number,
        proto="TCP",
        packet_time=packet_time,
        ip_version=ip_version,
        ip_ihl=ip_ihl,
        ip_tos=ip_tos,
        ip_len=ip_len,
        ip_id=ip_id,
        ip_flags=ip_flags,
        ip_frag=ip_frag,
        ip_ttl=ip_ttl,
        ip_proto=ip_proto,
        ip_chksum=ip_chksum,
        ip_src=ip_src,
        ip_dst=ip_dst,
        ip_options=ip_options,
        tcp_sport=tcp_sport,
        tcp_dport=tcp_dport,
        tcp_seq=tcp_seq,
        tcp_ack=tcp_ack,
        tcp_dataofs=tcp_dataofs,
        tcp_reserved=tcp_reserved,
        tcp_flags=tcp_flags,
        tcp_window=tcp_window,
        tcp_chksum=tcp_chksum,
        tcp_urgptr=tcp_urgptr,
        tcp_options=tcp_options
    )

        
class Honeypot:
    def __init__(self, 
                 unverified_ips,
                 full_handshake_ips,
                 syn_only_ips,
                 no_further_traffic_ips,
                 current_honeypot_ports,
                 up_producer,
                 internal_ips,
                 interface):
        
        self.unverified_ips = unverified_ips
        self.full_handshake_ips = full_handshake_ips
        self.syn_only_ips = syn_only_ips
        self.no_further_traffic_ips = no_further_traffic_ips
        self.current_honeypot_ports = current_honeypot_ports
        self.up_producer = up_producer
        self.internal_ips = internal_ips
        self.interface = interface
        
        # Fallback local dictionaries if Manager fails
        self.local_unverified_ips = {}
        self.local_full_handshake_ips = {}
        self.local_syn_only_ips = {}
        self.local_no_further_traffic_ips = {}
        self.local_current_honeypot_ports = {}
        self.manager_failed = False
        
        # Track active honeypot sockets
        self.active_listeners = {}  # port -> socket object
        self.max_listeners = 150
        
        # Statistics tracking
        self.connection_count = 0
        self.unique_attackers = set()
        
        # Bind to all available IPs
        self.bind_ips = []
        if internal_ips.get('ipv4'):
            self.bind_ips.extend(internal_ips['ipv4'])
        if internal_ips.get('ipv6'):
            self.bind_ips.extend(internal_ips['ipv6'])
            
    def get_targeted_ports(self):
        """Extract all ports currently being targeted by unverified IPs"""
        targeted_ports = set()
        
        unverified_copy = self.get_unverified_dict()
        for ip_src, port_dict in unverified_copy.items():
            if isinstance(port_dict, dict):
                targeted_ports.update(port_dict.keys())
                
        return targeted_ports
        
    def create_listener(self, port):
        """Create a honeypot listener on the specified port"""
        try:
            # Try IPv4 first
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1.0)  # Non-blocking with timeout
            
            # Bind to first available internal IP
            bind_ip = self.bind_ips[0] if self.bind_ips else '0.0.0.0'
            sock.bind((bind_ip, port))
            sock.listen(10)  # Increased backlog for multiple connections
            
            self.active_listeners[port] = sock
            self.update_honeypot_ports(port, True)  # Update shared dictionary safely
            print(f"[Honeypot] Created listener on {bind_ip}:{port}")
            return True
            
        except Exception as e:
            print(f"[Honeypot] Failed to create listener on port {port}: {e}")
            if port in self.active_listeners:
                del self.active_listeners[port]
            self.update_honeypot_ports(port, False)  # Remove from shared dictionary safely
            return False
            
    def close_listener(self, port):
        """Close a honeypot listener"""
        if port in self.active_listeners:
            try:
                self.active_listeners[port].close()
                del self.active_listeners[port]
                self.update_honeypot_ports(port, False)  # Remove from shared dictionary safely
                print(f"[Honeypot] Closed listener on port {port}")
            except Exception as e:
                print(f"[Honeypot] Error closing port {port}: {e}")
                
    def handle_connection(self, port, client_sock, client_addr):
        """Handle an incoming connection to a honeypot"""
        client_ip = client_addr[0]
        connection_time = time.time()
        
        print(f"[Honeypot] Connection from {client_ip}:{client_addr[1]} to port {port}")
        
        # Update statistics
        self.connection_count += 1
        self.unique_attackers.add(client_ip)
        
        # Move IP from unverified to full_handshake
        if client_ip in self.unverified_ips:
            # Remove from unverified
            if port in self.unverified_ips[client_ip]:
                del self.unverified_ips[client_ip][port]
                if not self.unverified_ips[client_ip]:  # No more ports for this IP
                    del self.unverified_ips[client_ip]
            
            # Add to full_handshake_ips
            if client_ip in self.full_handshake_ips:
                if port in self.full_handshake_ips[client_ip]:
                    self.full_handshake_ips[client_ip][port].append(connection_time)
                else:
                    self.full_handshake_ips[client_ip][port] = [connection_time]
            else:
                self.full_handshake_ips[client_ip] = {port: [connection_time]}
                
            print(f"[Honeypot] Moved {client_ip} from unverified to full_handshake for port {port}")
        else:
            # Also track repeated connections from already verified IPs
            if client_ip in self.full_handshake_ips:
                if port in self.full_handshake_ips[client_ip]:
                    self.full_handshake_ips[client_ip][port].append(connection_time)
                else:
                    self.full_handshake_ips[client_ip][port] = [connection_time]
            else:
                self.full_handshake_ips[client_ip] = {port: [connection_time]}
        
        # Handle the connection - only listen, don't send any data
        try:
            client_sock.settimeout(10.0)  # Timeout for reading data
            
            # Listen for data from the attacker without sending anything back
            bytes_received = 0
            total_data = b""
            
            while bytes_received < 4096:  # Limit total data to prevent memory issues
                try:
                    data = client_sock.recv(1024)
                    if not data:  # Connection closed by client
                        break
                    
                    total_data += data
                    bytes_received += len(data)
                    
                    # Log received data in chunks for monitoring
                    if len(data) > 0:
                        print(f"[Honeypot] Received {len(data)} bytes from {client_ip}:{client_addr[1]} on port {port}")
                        
                except socket.timeout:
                    break  # No more data received
                except Exception as e:
                    print(f"[Honeypot] Error reading data from {client_ip}: {e}")
                    break
            
            # Log summary of interaction
            if bytes_received > 0:
                # Show first 100 bytes for analysis (safely handle binary data)
                try:
                    data_preview = total_data[:100].decode('utf-8', errors='replace')
                    print(f"[Honeypot] Total {bytes_received} bytes received from {client_ip}:{client_addr[1]} on port {port}")
                    print(f"[Honeypot] Data preview: {repr(data_preview)}")
                except:
                    print(f"[Honeypot] Total {bytes_received} bytes (binary) received from {client_ip}:{client_addr[1]} on port {port}")
            else:
                print(f"[Honeypot] No data received from {client_ip}:{client_addr[1]} on port {port}")
            
            print(f"[Honeypot] Closing connection from {client_ip}:{client_addr[1]} on port {port}")
            
        except Exception as e:
            print(f"[Honeypot] Error handling connection from {client_ip}: {e}")
        finally:
            try:
                client_sock.close()
            except:
                pass
            
    def check_for_connections(self):
        """Check all active listeners for incoming connections"""
        for port, sock in list(self.active_listeners.items()):
            # Check for multiple connections on each port
            connections_handled = 0
            max_connections_per_check = 5  # Limit to prevent overwhelming
            
            while connections_handled < max_connections_per_check:
                try:
                    client_sock, client_addr = sock.accept()
                    connections_handled += 1
                    
                    # Handle in background to avoid blocking
                    threading.Thread(
                        target=self.handle_connection,
                        args=(port, client_sock, client_addr),
                        daemon=True
                    ).start()
                    
                except socket.timeout:
                    # No more connections, move to next port
                    break
                except OSError as e:
                    if e.errno == 11:  # EAGAIN/EWOULDBLOCK - no more connections
                        break
                    print(f"[Honeypot] Socket error on port {port}: {e}")
                    break
                except Exception as e:
                    print(f"[Honeypot] Error accepting connection on port {port}: {e}")
                    # Remove problematic listener
                    self.close_listener(port)
                    break
                
    def manage_listeners(self):
        """Add/remove listeners based on targeted ports"""
        targeted_ports = self.get_targeted_ports()
        current_ports = set(self.active_listeners.keys())
        
        # Remove listeners for ports no longer targeted
        for port in current_ports - targeted_ports:
            self.close_listener(port)
            
        # Add listeners for new targeted ports (up to max limit)
        new_ports = targeted_ports - current_ports
        available_slots = self.max_listeners - len(self.active_listeners)
        
        for port in list(new_ports)[:available_slots]:
            if 1025 <= port <= 65535:  # Valid port range, avoid privileged ports below 1025
                # Create listener (port conflict checking removed - honeypots are now independent)
                self.create_listener(port)
                
    def check_for_timeouts(self):
        """Check for IPs that should be moved to different categories based on timeouts"""
        current_time = time.time()
        timeout_4_hours = 4 * 3600  # 4 hours in seconds
        
        try:
            # Check unverified IPs for 4-hour timeout
            unverified_copy = dict(self.unverified_ips)
            for ip_src, port_dict in unverified_copy.items():
                if isinstance(port_dict, dict):
                    ports_to_remove = []
                    for port, timestamps in port_dict.items():
                        if timestamps and (current_time - timestamps[0]) > timeout_4_hours:
                            # Move to no_further_traffic_ips
                            if ip_src in self.no_further_traffic_ips:
                                if port in self.no_further_traffic_ips[ip_src]:
                                    self.no_further_traffic_ips[ip_src][port].extend(timestamps)
                                else:
                                    self.no_further_traffic_ips[ip_src][port] = timestamps[:]
                            else:
                                self.no_further_traffic_ips[ip_src] = {port: timestamps[:]}
                            
                            ports_to_remove.append(port)
                            print(f"[Honeypot] Moved {ip_src}:{port} to no_further_traffic (4-hour timeout)")
                    
                    # Remove timed-out ports from unverified
                    for port in ports_to_remove:
                        if port in self.unverified_ips[ip_src]:
                            del self.unverified_ips[ip_src][port]
                    
                    # Remove IP if no ports left
                    if ip_src in self.unverified_ips and not self.unverified_ips[ip_src]:
                        del self.unverified_ips[ip_src]
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Honeypot] Error during timeout check: {e}")

    def run(self):
        """Main honeypot loop"""
        print(f"[Honeypot] Starting honeypot monitor for interface {self.interface}")
        
        last_timeout_check = time.time()
        last_stats_report = time.time()
        
        while True:
            try:
                # Update listeners based on current threats
                self.manage_listeners()
                
                # Check for incoming connections
                self.check_for_connections()
                
                # Check for timeouts every 60 seconds
                current_time = time.time()
                if current_time - last_timeout_check > 60:
                    self.check_for_timeouts()
                    last_timeout_check = current_time
                
                # Report statistics every 10 minutes
                if current_time - last_stats_report > 600:
                    print(f"[Honeypot] Stats - Active listeners: {len(self.active_listeners)}, "
                          f"Total connections: {self.connection_count}, "
                          f"Unique attackers: {len(self.unique_attackers)}")
                    last_stats_report = current_time
                
                # Brief sleep to prevent excessive CPU usage
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("[Honeypot] Shutting down...")
                break
            except Exception as e:
                print(f"[Honeypot] Error in main loop: {e}")
                time.sleep(1)
                
        # Cleanup
        for port in list(self.active_listeners.keys()):
            self.close_listener(port)

    def safe_dict_access(self, shared_dict, local_dict, operation, *args, **kwargs):
        """Safely access shared dictionary with fallback to local copy"""
        if self.manager_failed:
            return operation(local_dict, *args, **kwargs)
        
        try:
            return operation(shared_dict, *args, **kwargs)
        except (ConnectionResetError, BrokenPipeError, OSError, AttributeError) as e:
            print(f"[Honeypot] Manager connection failed, switching to local mode: {e}")
            self.manager_failed = True
            # Copy any existing data from shared dict to local before switching
            try:
                local_dict.update(dict(shared_dict))
            except:
                pass
            return operation(local_dict, *args, **kwargs)
    
    def get_unverified_dict(self):
        """Get unverified IPs dictionary safely"""
        if self.manager_failed:
            return self.local_unverified_ips
        try:
            return dict(self.unverified_ips)
        except (ConnectionResetError, BrokenPipeError, OSError, AttributeError):
            self.manager_failed = True
            return self.local_unverified_ips
            
    def update_honeypot_ports(self, port, active=True):
        """Update honeypot ports safely"""
        if self.manager_failed:
            if active:
                self.local_current_honeypot_ports[port] = True
            else:
                self.local_current_honeypot_ports.pop(port, None)
        else:
            try:
                if active:
                    self.current_honeypot_ports[port] = True
                else:
                    self.current_honeypot_ports.pop(port, None)
            except (ConnectionResetError, BrokenPipeError, OSError, AttributeError):
                self.manager_failed = True
                if active:
                    self.local_current_honeypot_ports[port] = True
                else:
                    self.local_current_honeypot_ports.pop(port, None)


class Ports:
    def __init__(self,
            producer_upload_conn,
            internal_ips,
            internal_ip_equals_external_ip,
            interface,
            external_network_information,
            config_settings,
            system_info,
            unverified_ips,
            full_handshake_ips,
            syn_only_ips,
            no_further_traffic_ips,
            current_honeypot_ports
            ):
        

        self.producer_upload_conn=producer_upload_conn
        self.unprocessed_packed_buffer=[]
        self.currently_open_ip_list = {}  # Use local dictionary for legitimate ports
        self.previously_open_ip_list_A = {}
        self.previously_open_ip_list_B = {}
        self.previously_open_ip_list_ptr=self.previously_open_ip_list_A
        self.previously_open_ip_list_ptr["time_started"]=0

        self.packets_to_watch = OrderedDict()      # key -> list[Packet]

        # Add socket tracking for automatically opened ports
        self.auto_opened_sockets = {}  # port -> socket object
        self.auto_opened_ports = set()  # track which ports we've opened automatically
        self.max_auto_open_ports = 150   # limit to prevent resource exhaustion

        self.system_info=system_info
        self.ARP_requests = collections.deque()
        self.ARP_same_timestamp = collections.deque()
        self.timer=0
        self.SYN_reply_timeout=10
        self.ARP_reply_timeout=0.5
        self.Recently_closed_port_timeout=600
        
        
        self.num_total_tcp_packets=0
        self.num_unwanted_tcp_packets=0
        

        self.check_if_ip_changed_packet_interval=2000
        self.external_ip= external_network_information["queried_ip"]
        self.internal_ips=internal_ips
        self.asn=0
        self.external_network_information=external_network_information
        #self.internal_network_information=internal_network_information
        self.max_unwanted_buffer_size=5000
        self.interface=interface

        self.database=config_settings['database']
        self.randomization_key=config_settings['randomization_key']
        self.verbose=verbose
        self.os_info=""
        self.packet_number=0

        self.unwanted_packet_count=0

        #self.internal_ip_randomized = [ self.randomize_ip(ip) for ip in internal_ips ]
        
        self.internal_ip_randomized_v4 = [ self.randomize_ip(ip) for ip in self.internal_ips['ipv4'] ]
        self.internal_ip_randomized_v6 = [ self.randomize_ip(ip) for ip in self.internal_ips['ipv6'] ]

        self.external_ip_randomized=self.randomize_ip(self.external_ip)
        #TODO check for ipv6 and randomize that
        self.initial_calibration_duration=200
        self.initial_calibration_begin=time.monotonic()

        self.interface_human_readable=self.interface

        ##TODO DEBUG
        self.initial_calibration_complete=False

        # Data structures for tracking unverified attackers and honeypots (shared)
        self.unverified_ips = unverified_ips
        self.full_handshake_ips = full_handshake_ips
        self.syn_only_ips = syn_only_ips        
        self.no_further_traffic_ips = no_further_traffic_ips
        self.current_honeypot_ports = current_honeypot_ports     


        if platforminfo.system() == "Windows":
            import re, wmi

            # initialize WMI once
            _wmi = wmi.WMI()
            m = re.search(r'\{([0-9A-Fa-f-]+)\}', self.interface)
            if m:
                guid = m.group(1).lower()
                # search the *adapter* class (not the Configuration class!)
                for nic in _wmi.Win32_NetworkAdapter():
                    if not nic.GUID:
                        continue
                    if nic.GUID.strip('{}').lower() == guid:
                        friendly = (
                            nic.NetConnectionID
                            or nic.Name
                            or nic.Description
                            or self.interface
                        )
                        # *** assignment, not comparison! ***
                        self.interface_human_readable = friendly +self.interface_human_readable
                        break

        ###print(f"Monitoring {internal_ips} on {self.interface_human_readable}")
        


    def log_local_terminal_and_GUI_WARN(self,event_string,level):
        pass
        ###print(event_string, flush=True)



    
    def open_port(self,local_ip,local_port,remote_ip,pkt_info):
        ####print(f"open_port:local_ip {local_ip} local_port {local_port} remote_ip {remote_ip}",flush=True)
        if local_port not in self.currently_open_ip_list:
            self.currently_open_ip_list[local_port] = set()
        # add the remote IP
        self.currently_open_ip_list[local_port].add(remote_ip)
        ####print(f"open_port: {local_port} {self.currently_open_ip_list.keys()}",flush=True)

            
    def close_port(self,local_ip,local_port,remote_ip,historical_unacked_syn):
        remotes = self.currently_open_ip_list.get(local_port)
        if not remotes:
            return

        remotes.discard(remote_ip)  # discard() is safe if not present
        if not remotes:
            # no more connections  delete key, preserving order of the rest
            del self.currently_open_ip_list[local_port]

        # still record for previously open logic
        self.add_port_to_previously_open(local_ip, local_port, remote_ip, historical_unacked_syn)


    def num_open_connections(self, local_port) -> int:
        """
        Number of distinct remote IPs currently connected.
        """
        return len(self.currently_open_ip_list.get(local_port, ()))    

    def num_previously_open_connections(self, local_port) -> int:
        """
        Return the number of distinct remote IPs that were previously
        open on local_port, across both A and B windows.
        """
        a = self.previously_open_ip_list_A.get(local_port, set())
        b = self.previously_open_ip_list_B.get(local_port, set())
        # union so we dont doublecount an IP seen in both windows
        return len(a | b)

    def add_port_to_previously_open(self, local_ip, local_port, remote_ip, pkt_info):
        
        ####print(f"add_port_to_previously_open:local_port {local_port} remote_ip {remote_ip}",flush=True)
        # rollingwindow switch (unchanged)
        if pkt_info.packet_time - self.previously_open_ip_list_ptr["time_started"] > \
           self.Recently_closed_port_timeout:

            tmp = (
                self.previously_open_ip_list_B
                if self.previously_open_ip_list_ptr is self.previously_open_ip_list_A
                else self.previously_open_ip_list_A
            )
            tmp.clear()
            tmp["time_started"] = pkt_info.packet_time
            self.previously_open_ip_list_ptr = tmp

        # now record the remote_ip in a set for that port
        wins = self.previously_open_ip_list_ptr
        if local_port not in wins:
            wins[local_port] = set()
        wins[local_port].add(remote_ip)
        ####print(f"add_port_to_previously_open:self.previously_open_ip_list_A {self.previously_open_ip_list_A}",flush=True)
        ####print(f"add_port_to_previously_open:self.previously_open_ip_list_B {self.previously_open_ip_list_B}",flush=True)




    def was_port_previously_open(self, local_ip, local_port, remote_ip):
        # look in both windows A and B:
        for window in (self.previously_open_ip_list_A,
                       self.previously_open_ip_list_B):
            remotes = window.get(local_port)
            if remotes and remote_ip in remotes:
                return True
        return False
        


            
    def is_port_open(self, local_ip, local_port, remote_ip):
        # Check if the local IP is present.
        if local_port in self.currently_open_ip_list :
            return True
        return False


    
    
    
    def is_ip_dst_on_local_network(self,ip_dst):
        if ip_dst in self.internal_ips['ipv4'] or ip_dst in self.internal_ips['ipv6'] or ip_dst==self.external_ip:
            return True
        else:
            return False
        
    def is_ip_src_on_local_network(self,ip_src):
        if ip_src in self.internal_ips['ipv4'] or ip_src in self.internal_ips['ipv6'] or ip_src==self.external_ip:
            return True
        else:
            return False
    
    def add_L2_reachable_host(self,ip,MAC,current_packet):
        if not self.is_ip_dst_on_local_network(ip):
            self.currently_open_ip_list[ip]={}
            #self.log_local_terminal_and_GUI_WARN(f"ARP: Added add_L2_reachable_host {ip} based on num {current_packet.packet_num} {current_packet.packet}",4)
            justification=f"Justification: Packet Number {current_packet.packet_num}  {current_packet.packet.payload}"
            #self.gui_sock.send(f"ARP: Added add_L2_reachable_host {ip} based on num {current_packet.packet_num} {current_packet.packet}")
            
    def remove_L2_reachable_host(self,ip,MAC):
        if self.is_ip_dst_on_local_network(ip):
            #self.currently_open_ip_list.remove(ip)
            del self.currently_open_ip_list[ip]

    

    
    def print_currently_open_ports(self): 
        return
        if self.verbose ==0:
            #self.log_local_terminal_and_GUI_WARN("----- Currently Open Ports -----",0)
            for ip, ports in self.currently_open_ip_list.items():
                #self.log_local_terminal_and_GUI_WARN(f"IP: {ip}", 0)
                # Check if the value is a dictionary (it should be in your design)
                if isinstance(ports, dict):
                    for port, pkt_list in ports.items():
                        #self.log_local_terminal_and_GUI_WARN(f"  Port: {port}", 0)
                        # Each item in pkt_list is assumed to be a Packet_info object.
                        for remote_ip in pkt_list:
                            pass
                            #self.log_local_terminal_and_GUI_WARN(f"    remote_ip {remote_ip}", 0)
                else:
                    pass
                    # ###print the value directly if it's not a dictionary.
                    #self.log_local_terminal_and_GUI_WARN(f"  {ports}",0)
            #self.log_local_terminal_and_GUI_WARN("----- End of Currently Open Ports -----",0)
      
           

    '''                
    def Remove_ARP_from_watch(self,Matching_ARP):
        for x in range(len(self.ARP_requests) - 1, -1, -1):
            historical_ARP= self.ARP_requests[x]
            if  historical_ARP.packet[ARP].pdst == Matching_ARP.packet[ARP].psrc :
                    #self.log_local_terminal_and_GUI_WARN(f"Removed answered ARP self.ARP_requests[x] {self.ARP_requests[x].packet} after {Matching_ARP.packet.time - self.ARP_requests[x].packet.time} delay"+\f" due to Matching_ARP.packet {Matching_ARP.packet} {Matching_ARP.packet.time} with {self.ARP_requests[x].packet} {self.ARP_requests[x].packet.time}",1)
                    #self.log_local_terminal_and_GUI_WARN(f"Matching_ARP.packet[ARP].psrc {Matching_ARP.packet[ARP].psrc} Matching_ARP.packet[ARP].pdst {Matching_ARP.packet[ARP].pdst} self.ARP_requests[x].packet[ARP].psrc {self.ARP_requests[x].packet[ARP].psrc} self.ARP_requests[x].packet[ARP].pdst {self.ARP_requests[x].packet[ARP].pdst}",1)
                    del self.ARP_requests[x]
    '''
                    
    
    def Check_SYN_watch(self,current_packet):
        pass

        
    def Process_ACK(self,pkt_info):
        #TODO: find the SYN and remove it before timer expires, if port closed mark as open
        self.remove_pkt_from_watch(pkt_info)
        
    def Process_Outgoing_TCP(self,pkt_info):
        if  pkt_info.tcp_flags == "SA":
            #logging.info(f"Outgoing SA detected, so remove corresponding syn from list of unacked syns and process it as an open port{current_packet.packet}")
            #self.log_local_terminal_and_GUI_WARN(f" Process_Outgoing_TCP: Outgoing non R or F detected, so remove corresponding pckts from list of unacked and process it as an open port",1)
            self.Process_ACK(pkt_info)
            self.open_port(pkt_info.ip_src,pkt_info.tcp_sport,pkt_info.ip_dst, pkt_info)
        #This isn't exact, but it's close enough since we don't use ports being open to determine if a packet is unwanted
        if "F" in pkt_info.tcp_flags or "R" in pkt_info.tcp_flags:
            #self.log_local_terminal_and_GUI_WARN(f"Process_Outgoing_TCP: Fin flag, add_port_to_previously_open(pkt_info.ip_src,pkt_info.tcp_sport,pkt_info.ip_dst)",0)
            self.close_port(pkt_info.ip_src,pkt_info.tcp_sport,pkt_info.ip_dst,pkt_info)
            #self.add_port_to_previously_open(pkt_info.ip_src,pkt_info.tcp_sport,pkt_info.ip_dst,pkt_info)
            




    #only called if we got an ack, so we can remove all if duplicates so we error on the side of false negatives
    def remove_pkt_from_watch(self, pkt):
        key = (pkt.ip_dst, pkt.tcp_dport,pkt.ip_src, pkt.tcp_sport)
        ####print(f"remove_pkt_from_watch: {key}",flush=True)
        #bucket = self.packets_to_watch.get(key)
        ####print(f"is in watch? {bucket}",flush=True)
        try:
            if pkt.tcp_dport in self.current_honeypot_ports:
                self.Report_unwanted_traffic(pkt, "honeypot_port_syn", "")
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Ports] Error accessing current_honeypot_ports: {e}")
        self.packets_to_watch.pop(key, None)
        #bucket = self.packets_to_watch.get(key)
        ####print(f"how about now? {bucket}",flush=True)

    # ---------- hotpath: add packet ------------------------------------
    def add_pkt_to_watch(self, pkt):
        key = (pkt.ip_src, pkt.tcp_sport, pkt.ip_dst, pkt.tcp_dport)
        bucket = self.packets_to_watch.get(key)
        if bucket is None:              # new flow
            self.packets_to_watch[key] = [pkt]     # key goes to the end (newest)
        else:
            bucket.append(pkt)          # duplicates keep flow position

    # ---------- coldpath: reap expired ---------------------------------
    def clear_expired_pkts(self, now):

        while self.packets_to_watch:
            key, bucket = next(iter(self.packets_to_watch.items()))  # oldest flow
            first_pkt = bucket[0]

            # stop if the oldest packet is still within the timeout
            if now - first_pkt.packet_time <= self.SYN_reply_timeout:
                break

            # unpack our flow-key
            src_ip, src_port, dst_ip, dst_port = key

            

            # if the port is open *now*, drop this entire bucket
            if self.is_port_open(dst_ip, dst_port, src_ip):
                # removes the oldest item
                self.packets_to_watch.popitem(last=False)
                ####print(f"clear_expired_pkts:was going to report but port is open now, bucket dropped {key}",flush=True)
                continue
            
            # if the port is open *now*, drop this entire bucket
            if self.was_port_previously_open(dst_ip, dst_port, src_ip):
                # removes the oldest item
                self.packets_to_watch.popitem(last=False)
                ####print(f"clear_expired_pkts:was going to report but port was previously open, bucket dropped {key}",flush=True)
                continue

            # otherwise, this port truly never opened-report *all* expired packets
            while bucket and now - bucket[0].packet_time > self.SYN_reply_timeout:
                un_acked_pkt = bucket.pop(0)
                ####print(f"clear_expired_pkts:reporting packet to port {dst_port}, open ports are {self.currently_open_ip_list.keys} prev open are {self.previously_open_ip_list_A.keys} {self.previously_open_ip_list_B}",flush=True)
                
                # Check if this was a SYN to a honeypot port
                if dst_port in self.current_honeypot_ports:
                    # Move to syn_only_ips instead of just reporting
                    self.move_to_syn_only(un_acked_pkt)
                else:
                    self.Report_unwanted_traffic(un_acked_pkt, "expired_syn", "")

            # if nothing left in this bucket, remove the key
            if not bucket:
                self.packets_to_watch.popitem(last=False)
            else:
                # still has newer packets: move this key to the newest position
                self.packets_to_watch.move_to_end(key)


    def clear_and_report_all_watched_packets(self):
        # flush everything still being watched
        while self.packets_to_watch:
            key, bucket = self.packets_to_watch.popitem(last=False)  # oldest flow
            src_ip, src_port, dst_ip, dst_port = key

            # if the port is open now, skip reporting this bucket entirely
            if self.is_port_open(dst_ip, dst_port, src_ip):
                ####print(f"clear_and_report_all_watched_packets:was going to report but port is open now, bucket dropped {key}",flush=True)
                continue
            
            # if the port is open *now*, drop this entire bucket
            if self.was_port_previously_open(dst_ip, dst_port, src_ip):
                # removes the oldest item
                #self.packets_to_watch.popitem(last=False)
                #TODO veridfy this logic
                ####print(f"clear_and_report_all_watched_packets:was going to report but port was previously open, bucket dropped {key}",flush=True)
                continue

            # otherwise, report every packet in the bucket
            for un_acked_pkt in bucket:
                # Check if this was a SYN to a honeypot port
                if un_acked_pkt.tcp_dport in self.current_honeypot_ports:
                    # Move to syn_only_ips instead of just reporting
                    self.move_to_syn_only(un_acked_pkt)
                else:
                    self.Report_unwanted_traffic(un_acked_pkt, "shutdown_syn", "")




    def Clear_unreplied_ARPs(self,current_packet):
        while len(self.ARP_requests):
            if current_packet.packet.time - self.ARP_requests[0].packet.time >= self.ARP_reply_timeout :
                if self.is_ip_dst_on_local_network(self.ARP_requests[0].packet[ARP].pdst):
                    #self.log_local_terminal_and_GUI_WARN(f"ARP: Remove ip {self.ARP_requests[0].packet[ARP].pdst} from local hosts  ARP TIMEOUT: self.ARP_requests was never replied to, packet number :{self.ARP_requests[0].packet_num} {self.ARP_requests[0].packet} ",4)
                    unwanted_packet=self.ARP_requests.popleft()
                    self.remove_L2_reachable_host(unwanted_packet.packet[ARP].pdst,"")
                else:
                    #self.log_local_terminal_and_GUI_WARN(f"ARP:would remove ip {self.ARP_requests[0].packet[ARP].pdst} but it's not in local hosts. TIMEOUT: self.ARP_requests was never replied to, packet number :{self.ARP_requests[0].packet_num} {self.ARP_requests[0].packet}, ",4)
                    self.ARP_requests.popleft()

            else:
                break
    
    def Process_TCP(self,pkt_info):
        #incoming packets,we onlcy care about those to enpoints we monitor
        if self.is_ip_dst_on_local_network(pkt_info.ip_dst):
            self.num_total_tcp_packets=self.num_total_tcp_packets+1

            #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: ***************** packet_num:{pkt_info.packet_num} seq:{pkt_info.tcp_seq} Incoming Seen at Process_TCP ******************",0)
            #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: Incoming pkt_info.ip_src:{pkt_info.ip_src} pkt_info.ip_dst:{pkt_info.ip_dst} pkt_info.tcp_sport:{pkt_info.tcp_sport} pkt_info.tcp_dport:{pkt_info.tcp_dport} pkt_info.tcp_seq:{pkt_info.tcp_seq} ",0)
            #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: ***************** {pkt_info.tcp_seq} self.###print_currently_open_ports() ******************",0)
            #self.log_local_terminal_and_GUI_WARN(self.###print_currently_open_ports(),0)
            #self.log_local_terminal_and_GUI_WARN(f"Process_TCP:  ***************** {pkt_info.tcp_seq} end currently_open_ports() ******************",0)

            '''if self.is_port_open(pkt_info.ip_dst,pkt_info.tcp_dport,pkt_info.ip_src):
                #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: ***************** {pkt_info.tcp_seq} self.is_port_open came back true {pkt_info.ip_dst} ,{ pkt_info.tcp_dport} ",0)
                pass
            #error on side of caution, if port was previously open there's a chance packets may not be unwanted
            elif self.was_port_previously_open(pkt_info.ip_dst,pkt_info.tcp_dport,pkt_info.ip_src,pkt_info ) is True:
                #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: ***************** {pkt_info.tcp_seq} self.is_port_open false, but self.was_port_previously_open came back true {pkt_info.ip_dst} ,{ pkt_info.tcp_dport} ",0)
                pass          
            else:
                #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: ***************** {pkt_info.tcp_seq} self.was_port_previously_open came back false {pkt_info.ip_dst} ,{ pkt_info.tcp_dport} ",0)
                #strrr=self.###print_previously_open_ports()
                #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: entries in was_port_previously_open {strrr}",0)
            '''
            #add to watch only if a new syn. Maybe make a new thread to handle the connections and opening the ports
            if pkt_info.tcp_flags == "S":
                self.add_pkt_to_watch(pkt_info)          
        #outgoing packets
        elif self.is_ip_src_on_local_network(pkt_info.ip_src):
            #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: ***************** packet_num:{pkt_info.packet_num} seq:{pkt_info.tcp_seq} Outgoing Seen at Process_TCP ******************",0)
            #self.log_local_terminal_and_GUI_WARN(f"Process_TCP: Outgoing pkt_info.ip_src:{pkt_info.ip_src} pkt_info.ip_dst:{pkt_info.ip_dst} pkt_info.tcp_sport:{pkt_info.tcp_sport} pkt_info.tcp_dport:{pkt_info.tcp_dport} pkt_info.tcp_seq:{pkt_info.tcp_seq} ",0)
            self.Process_Outgoing_TCP(pkt_info)
        #self.log_local_terminal_and_GUI_WARN(f"\n\n=============================\n\n",0)


    def print_previously_open_ports(self):
        if self.verbose ==0:
            strrr=""
            for outer_key  in self.previously_open_ip_list_A.keys():
                strrr+="A"+str(outer_key)+","
            for outer_key in self.previously_open_ip_list_B.keys():
                strrr+="B"+str(outer_key)+","
        
            
            #self.log_local_terminal_and_GUI_WARN(f"###print_previously_open_ports: {strrr}",0)
            
        
    def hash_segment(self, segment, key):
        """
        Hash a segment (an int or string) together with the key,
        and map to 0255.
        """
        combined = f"{segment}-{key}"
        h = hashlib.sha256(combined.encode()).hexdigest()
        return int(h[:2], 16) % 256

    def randomize_ip(self, ip_str):
        """
        Randomize an IPv4 *or* IPv6 address, returning a string
        in the same notation (dotted-quad or compressed IPv6).
        """
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            raise ValueError(f"Invalid IP address: {ip_str!r}")

        key = self.randomization_key
        # operate on the raw bytes of the address
        orig_bytes = ip.packed  # b'\xC0\xA8\x00\x01' for 192.168.0.1, or 16 bytes for IPv6

        # hash each byte  new byte
        new_bytes = bytes(self.hash_segment(b, key) for b in orig_bytes)

        # reconstruct an IP object from those bytes
        rand_ip = ipaddress.IPv4Address(new_bytes) if ip.version == 4 else ipaddress.IPv6Address(new_bytes)
        return str(rand_ip)
    

    def move_to_syn_only(self, pkt_info):
        """Move an IP from unverified to syn_only_ips"""
        client_ip = pkt_info.ip_src
        port = pkt_info.tcp_dport
        
        try:
            # Remove from unverified if present
            if client_ip in self.unverified_ips:
                if port in self.unverified_ips[client_ip]:
                    del self.unverified_ips[client_ip][port]
                    if not self.unverified_ips[client_ip]:  # No more ports for this IP
                        del self.unverified_ips[client_ip]
            
            # Add to syn_only_ips
            if client_ip in self.syn_only_ips:
                if port in self.syn_only_ips[client_ip]:
                    self.syn_only_ips[client_ip][port].append(pkt_info.packet_time)
                else:
                    self.syn_only_ips[client_ip][port] = [pkt_info.packet_time]
            else:
                self.syn_only_ips[client_ip] = {port: [pkt_info.packet_time]}
                
            print(f"[Ports] Moved {client_ip} to syn_only for port {port} (SYN to honeypot, no completion)")
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Ports] Error accessing shared dictionaries in move_to_syn_only: {e}")

    def add_to_verification_list(self,pkt_info):
        # Skip if IP is already verified in other categories
        try:
            if pkt_info.ip_src in self.full_handshake_ips or pkt_info.ip_src in self.syn_only_ips or pkt_info.ip_src in self.no_further_traffic_ips:
                return

            if pkt_info.ip_src in self.unverified_ips:
                if pkt_info.tcp_dport in self.unverified_ips[pkt_info.ip_src]:
                    self.unverified_ips[pkt_info.ip_src][pkt_info.tcp_dport].append(pkt_info.packet_time)
                else:
                    self.unverified_ips[pkt_info.ip_src][pkt_info.tcp_dport] = [pkt_info.packet_time]
            else:
                self.unverified_ips[pkt_info.ip_src] = {pkt_info.tcp_dport: [pkt_info.packet_time]}
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Ports] Error accessing shared dictionaries in add_to_verification_list: {e}")

    def Report_unwanted_traffic(self,pkt_info,honeypot_status,payload):
        if self.initial_calibration_complete:
            self.num_unwanted_tcp_packets+=1
            self.add_to_verification_list(pkt_info) 
            self.prepare_data(pkt_info,honeypot_status,payload)
       
    
    def cleanup_verification_dictionaries(self):
        """Clean up old entries from verification dictionaries"""
        current_time = time.time()
        cleanup_age = 24 * 3600  # 24 hours
        
        try:
            # Clean up full_handshake_ips
            for ip_src in list(self.full_handshake_ips.keys()):
                port_dict = self.full_handshake_ips[ip_src]
                if isinstance(port_dict, dict):
                    for port in list(port_dict.keys()):
                        timestamps = port_dict[port]
                        if timestamps and (current_time - timestamps[-1]) > cleanup_age:
                            del port_dict[port]
                            print(f"[Cleanup] Removed old entry {ip_src}:{port} from full_handshake_ips")
                    
                    if not port_dict:  # Remove IP if no ports left
                        del self.full_handshake_ips[ip_src]
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Cleanup] Error accessing full_handshake_ips: {e}")
        
        try:
            # Clean up syn_only_ips
            for ip_src in list(self.syn_only_ips.keys()):
                port_dict = self.syn_only_ips[ip_src]
                if isinstance(port_dict, dict):
                    for port in list(port_dict.keys()):
                        timestamps = port_dict[port]
                        if timestamps and (current_time - timestamps[-1]) > cleanup_age:
                            del port_dict[port]
                            print(f"[Cleanup] Removed old entry {ip_src}:{port} from syn_only_ips")
                    
                    if not port_dict:  # Remove IP if no ports left
                        del self.syn_only_ips[ip_src]
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Cleanup] Error accessing syn_only_ips: {e}")
        
        try:
            # Clean up no_further_traffic_ips
            for ip_src in list(self.no_further_traffic_ips.keys()):
                port_dict = self.no_further_traffic_ips[ip_src]
                if isinstance(port_dict, dict):
                    for port in list(port_dict.keys()):
                        timestamps = port_dict[port]
                        if timestamps and (current_time - timestamps[-1]) > cleanup_age:
                            del port_dict[port]
                            print(f"[Cleanup] Removed old entry {ip_src}:{port} from no_further_traffic_ips")
                    
                    if not port_dict:  # Remove IP if no ports left
                        del self.no_further_traffic_ips[ip_src]
        except (ConnectionResetError, BrokenPipeError, OSError) as e:
            print(f"[Cleanup] Error accessing no_further_traffic_ips: {e}")

    def send_heartbeat(self):
        current_open_common_ports = []
        for port, remotes in self.currently_open_ip_list.items():
            # skip non-numeric keys (like "time_started" in your prev lists) if any
            if not isinstance(port, int):
                continue
            
            count = len(remotes)
            current_open_common_ports.append(f"{port}x{count}")

        previosuly_open_common_ports = []
        # gather all ports seen in either A or B
        all_prev_ports = set(self.previously_open_ip_list_A) | set(self.previously_open_ip_list_B)
        for port in all_prev_ports:
            if port == "time_started" or not isinstance(port, int):
                continue
            
            # union the two sets so we count each remote IP only once
            remotes_a = self.previously_open_ip_list_A.get(port, set())
            remotes_b = self.previously_open_ip_list_B.get(port, set())
            count = len(remotes_a | remotes_b)
            previosuly_open_common_ports.append(f"{port}x{count}")

        

        heartbeat_message = {
            "db_name":                        "heartbeats",
            "unwanted_db":                    self.database,
            "pkts_last_hb":                   self.num_total_tcp_packets,
            "ext_dst_ip_country":             self.external_network_information['country'],
            "type":                           self.external_network_information['type'],
            "ASN":                            self.external_network_information['ASN'],
            "domain":                         self.external_network_information['domain'],
            "city":                           self.external_network_information['city'],
            "as_type":                        self.external_network_information['as_type'],
            
            "external_is_private":            check_ip_is_private(self.external_ip) ,
            "open_ports":                     ",".join(current_open_common_ports), 
            "previously_open_ports":          ",".join(previosuly_open_common_ports),        
            "interface":                      self.interface_human_readable,
            "internal_ip_randomized":         ",".join(str(v) for v in self.internal_ip_randomized_v4 + self.internal_ip_randomized_v6),
            "external_ip_randomized":         self.external_ip_randomized,

            "System_info":                   self.system_info['System'],
            "Release_info":                  self.system_info['Release'],
            "Version_info":                  self.system_info['Version'],
            "Machine_info":                       self.system_info['Machine'],
            "Total_Memory":                  self.system_info['Total_Memory'],
            "processor":                     self.system_info['processor'],
            "architecture" :                 self.system_info['architecture']
        }

        ####print(payload,flush=True)
        self.num_total_tcp_packets=0
        self.producer_upload_conn.send(heartbeat_message)                
    

    def prepare_data(self,pkt_info,honeypot_status,payload):
        current_open_common_ports = []
        for port, remotes in self.currently_open_ip_list.items():
            # skip non-numeric keys (like "time_started" in your prev lists) if any
            if not isinstance(port, int):
                continue

            count = len(remotes)
            current_open_common_ports.append(f"{port}x{count}")

        previosuly_open_common_ports = []
        # gather all ports seen in either A or B
        all_prev_ports = set(self.previously_open_ip_list_A) | set(self.previously_open_ip_list_B)
        for port in all_prev_ports:
            if port == "time_started" or not isinstance(port, int):
                continue

            # union the two sets so we count each remote IP only once
            remotes_a = self.previously_open_ip_list_A.get(port, set())
            remotes_b = self.previously_open_ip_list_B.get(port, set())
            count = len(remotes_a | remotes_b)
            previosuly_open_common_ports.append(f"{port}x{count}")

        

        payload = {
            "db_name":                        self.database,
            "system_time":                    str(pkt_info.packet_time),
            "ip_version":                     pkt_info.ip_version,
            "ip_ihl":                         pkt_info.ip_ihl,
            "ip_tos":                         pkt_info.ip_tos,
            "ip_len":                         pkt_info.ip_len,
            "ip_id":                          pkt_info.ip_id ,
            "ip_flags":                       ",".join(str(v) for v in pkt_info.ip_flags),
            "ip_frag":                        pkt_info.ip_frag,
            "ip_ttl":                         pkt_info.ip_ttl,
            "ip_proto":                       pkt_info.ip_proto,
            "ip_chksum":                      pkt_info.ip_chksum,
            "ip_src":                         pkt_info.ip_src,
            "ip_dst_randomized":              self.randomize_ip(pkt_info.ip_dst), #todo ipv6?
            "ip_options":                     ",".join(str(v) for v in pkt_info.ip_options ),
            "tcp_sport":                      pkt_info.tcp_sport,           
            "tcp_dport":                      pkt_info.tcp_dport,           
            "tcp_seq":                        pkt_info.tcp_seq ,            
            "tcp_ack":                        pkt_info.tcp_ack ,            
            "tcp_dataofs":                    pkt_info.tcp_dataofs ,        
            "tcp_reserved":                   pkt_info.tcp_reserved,   
            "tcp_flags":                      pkt_info.tcp_flags,
            "tcp_window":                     pkt_info.tcp_window,
            "tcp_chksum":                     pkt_info.tcp_chksum,
            "tcp_urgptr":                     pkt_info.tcp_urgptr,
            
            "ext_dst_ip_country":             self.external_network_information['country'],
            "type":                           self.external_network_information['type'],
            "ASN":                            self.external_network_information['ASN'],
            "domain":                         self.external_network_information['domain'],
            "city":                           self.external_network_information['city'],
            "as_type":                        self.external_network_information['as_type'],
            
            "ip_dst_is_private":              check_ip_is_private(pkt_info.ip_dst) ,
            "external_is_private":            check_ip_is_private(self.external_ip) ,
            "open_ports":                     ",".join(current_open_common_ports), 
            "previously_open_ports":          ",".join(previosuly_open_common_ports),        
            "tcp_options":                     ",".join(str(v) for v in human_readable_tcp_opts(pkt_info.tcp_options) ),
            "interface":                      self.interface_human_readable,
            "internal_ip_randomized":         ",".join(str(v) for v in self.internal_ip_randomized_v4 + self.internal_ip_randomized_v6),
            "external_ip_randomized":         self.external_ip_randomized,

            "System_info":                   self.system_info['System'],
            "Release_info":                  self.system_info['Release'],
            "Version_info":                  self.system_info['Version'],
            "Machine_info":                       self.system_info['Machine'],
            "Total_Memory":                  self.system_info['Total_Memory'],
            "processor":                     self.system_info['processor'],
            "architecture" :                 self.system_info['architecture'],
            "honeypot_status":               honeypot_status,
            "payload":                       payload
        }

        ####print(payload,flush=True)

        self.producer_upload_conn.send(payload)
        self.unwanted_packet_count=self.unwanted_packet_count+1
        '''if self.unwanted_packet_count % 1000 ==0:
            #self.log_local_terminal_and_GUI_WARN(f"self.unwanted_packet_count {self.unwanted_packet_count}",0)
        '''

 


    def ARP_add_hosts(self,current_packet):
        #logging.info(f"AAAAAAAAAAAAAAA current_packet.packet[ARP] {current_packet.packet[ARP].show(dump=True)}")
        #logging.warning(f"AAAAAAAAAAAAAAA  {dir(current_packet.packet[ARP])}")
        self.add_L2_reachable_host(current_packet.packet[ARP].psrc,current_packet.packet[ARP].hwsrc,current_packet)
        
    
    def ARP_add_request_watch(self,current_packet):
        #Track the ARP request, if it goes unanswered remove the requested host from L2 reachable
        #current_packet.packet[ARP].op == 2 means it was an ARP reply, ==1 is a request
        matching_out_of_order_reply=0
        self.ARP_same_timestamp.append(current_packet)
        if self.ARP_same_timestamp[0].packet.time != current_packet.packet.time:
            self.ARP_same_timestamp.clear()
            self.ARP_same_timestamp.append(current_packet)
        else:
            self.ARP_same_timestamp.append(current_packet)
        
        if current_packet.packet[ARP].op == 1:
            if self.ARP_same_timestamp:
                if self.ARP_same_timestamp[0].packet.time == current_packet.packet.time:
                    for ARP_with_same_timestamp in self.ARP_same_timestamp:
                        if  current_packet.packet[ARP].pdst == ARP_with_same_timestamp.packet[ARP].psrc :
                            matching_out_of_order_reply=1
                            #self.log_local_terminal_and_GUI_WARN(f"Out of order ARP reply for num {current_packet.packet_num} {current_packet.packet} and {ARP_with_same_timestamp.packet_num} {ARP_with_same_timestamp.packet} ",1)  
                if not matching_out_of_order_reply:
                    self.ARP_requests.append(current_packet)
            
    

                    
    def Process_ARP(self,current_packet):
        #if collecting on all IPs use ARP method
        pass
        '''if self.collection_ip == "all":
            if current_packet.packet.haslayer(ARP):# 
                #Add the sender of the ARP request, we know they are there
                self.ARP_add_hosts(current_packet)
                self.ARP_add_request_watch(current_packet)
                #TODO: maybe change logic here to detect MAC issues with ip addresses and ARP, for now if it's responding/originating ARP then you can remove unreplied ARPs
                self.Clear_unreplied_ARPs(current_packet)
                self.Remove_ARP_from_watch(current_packet)'''
            
    
        
      
        
    def Process_packet(self,pkt_info):
        #self.Process_ARP(pkt_info)
        self.Process_TCP(pkt_info)
        

    def ensure_directory(self,directory_name):
        """Ensure the directory exists, and if not, create it."""
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)



    
            
            
    def packet_handler(self, unprocessed_packets):
        next_hb = time.monotonic()  
        next_cleanup = time.monotonic()

        work_deque  = deque()

        packets_processed=0
        prior_time=time.monotonic()

        def fill_work_deque():
            while True:
                batch = unprocessed_packets.recv()    # blocks until a batch arrives
                work_deque.append(batch)           # atomic in CPython

        # start receiver…
        t = threading.Thread(target=fill_work_deque, daemon=True)
        t.start()

        while True:

            now = time.monotonic()
            #heartbeats
            if now >= next_hb:
                self.send_heartbeat()
                next_hb = now + 3600
            
            # cleanup verification dictionaries every 6 hours
            if now >= next_cleanup:
                self.cleanup_verification_dictionaries()
                next_cleanup = now + 6 * 3600


            



            # 1) wait up to self.SYN_reply_timeout for the next batch, if it takes longer than that you can clear all the packets from the watch, they didn't get acked in time
            if now - self.initial_calibration_begin >self.initial_calibration_duration:
                self.initial_calibration_complete=True


            try:
                batch = work_deque.popleft()      # atomic pop from left
            except IndexError:
                # no work right now
                time.sleep(1)
                #time.sleep(0.1)
                #self.clear_and_report_all_watched_packets()
                continue
 

            # 2) process it
            for pkt in batch:
                self.Process_packet(pkt)
                packets_processed+=1
            self.clear_expired_pkts(batch[-1].packet_time)

            if (now - prior_time) >= 1:
                ###print(f" len(work_deque) {len(work_deque)} pps {packets_processed} { self.interface_human_readable}",flush=True)
                packets_processed=0
                prior_time=now
                    



                    


        
        

from collections import deque
import time
import requests
from requests.adapters import HTTPAdapter

from collections import deque
import time
import threading
import requests
from requests.adapters import HTTPAdapter

def send_data(consumer_upload_conn):
    DATA_URL      = "https://thelightscope.com/log_mysql_data"
    HEARTBEAT_URL = "https://thelightscope.com/heartbeat"
    HEADERS       = {
        "Content-Type": "application/json",
        "X-API-Key":    "lightscopeAPIkey2025_please_dont_distribute_me_but_im_write_only_anyways"
    }

    BATCH_SIZE     = 600
    IDLE_FLUSH_SEC = 5.0    # flush data if idle this long
    RETRY_BACKOFF  = 5      # seconds to wait on failure

    session = requests.Session()
    adapter = HTTPAdapter(pool_connections=4, pool_maxsize=4)
    session.mount("https://", adapter)
    session.mount("http://",  adapter)

    queue = deque()
    last_activity = time.monotonic()
    stop_event    = threading.Event()

    # --------------------------- reader thread ---------------------------
    def reader():
        nonlocal last_activity
        while not stop_event.is_set():
            try:
                item = consumer_upload_conn.recv()
            except (EOFError, OSError):
                stop_event.set()
                break
            queue.append(item)
            last_activity = time.monotonic()
        # drain any leftover
        while True:
            try:
                item = consumer_upload_conn.recv()
                queue.append(item)
            except Exception:
                break

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    # --------------------------- flush loop ---------------------------
    try:
        while not stop_event.is_set() or queue:
            # 1) first, pull out _all_ pending heartbeats and send them
            hb_count = 0
            n = len(queue)
            for _ in range(n):
                item = queue.popleft()
                if item.get("db_name") == "heartbeats":
                    hb_count += 1
                    try:
                        resp = session.post(
                            HEARTBEAT_URL,
                            json=item,
                            headers=HEADERS,
                            timeout=10,
                            
                        )
                        if resp.status_code != 200:
                            ###print(f"[heartbeat] rejected ({resp.status_code}): {resp.text}", flush=True)
                            pass
                        resp.raise_for_status()
                    except requests.RequestException as e:
                        ###print(f"[heartbeat] error, will drop: {e}", flush=True)
                        pass
                else:
                    queue.append(item)
            if hb_count:
                ###print(f"[heartbeat] sent {hb_count} message(s)", flush=True)
                pass

            # 2) now, see if it's time to flush a batch of normal data records
            now     = time.monotonic()
            elapsed = now - last_activity

            if queue and (len(queue) >= BATCH_SIZE or elapsed >= IDLE_FLUSH_SEC):
                to_send = min(len(queue), BATCH_SIZE)
                batch   = [queue.popleft() for _ in range(to_send)]
                try:
                    resp = session.post(
                        DATA_URL,
                        json={"batch": batch},
                        headers=HEADERS,
                        timeout=10,
                        
                    )
                    if resp.status_code != 200:
                        ###print(f"[data] rejected ({to_send} items): {resp.status_code} {resp.text}", flush=True)
                        pass
                    else:
                        ###print(f"[data] flushed {to_send} items", flush=True)
                        pass
                    resp.raise_for_status()
                    last_activity = time.monotonic()
                except requests.RequestException as e:
                    # push them back on front, and retry later
                    ####print(f"[data] error, will retry batch: {e}", flush=True)
                    pass
                    for item in reversed(batch):
                        queue.appendleft(item)
                    time.sleep(RETRY_BACKOFF)
                    # note: we do _not_ update last_activity so idle timer will trigger again
            else:
                time.sleep(0.1)

    finally:
        stop_event.set()
        t.join()





                
def read_from_interface_mac_linux(network_interface,
                        unprocessed_packets,         # duplex Pipe
                        promisc_mode=False):

    import pylibpcap.base
    BATCH_SIZE      = 280
    IDLE_FLUSH_SECS = 1.0
    SLEEP_DELAY     = 0.001  # 1ms when no flush condition met
    send_deque   = deque()
    last_activity = time.monotonic()

    # --------------------------- sender thread ---------------------------
    def sender_thread():
        nonlocal last_activity
        
        #todo remove debug

        prior_time=time.monotonic()
        packets_processed=0

        

        while True:
            now = time.monotonic()
            to_send = 0

            if (now - prior_time) >= IDLE_FLUSH_SECS:
                ###print(f" len(send_deque) {len(send_deque)} pps {packets_processed} {network_interface}",flush=True)
                packets_processed=0
                prior_time=now



            # 1) full batch ready?
            if len(send_deque) >= BATCH_SIZE:
                to_send = BATCH_SIZE

            # 2) idle timeout expired & buffer non-empty?
            elif send_deque and (now - last_activity) >= IDLE_FLUSH_SECS:
                to_send = len(send_deque)

            # 3) nothing to do right now
            else:
                time.sleep(SLEEP_DELAY)
                continue
            
            
            # build and send batch
            batch = [send_deque.popleft() for _ in range(to_send)]
            try:
                unprocessed_packets.send(batch)       # send to handler
            except Exception as e:
                ###print("pipe send error:", e, file=sys.stderr)
                return



            #todo remove debug code
            packets_processed+=to_send

           

    threading.Thread(target=sender_thread, daemon=True).start()

    # --------------------------- sniffer init ----------------------------
    try:
        sniffobj = pylibpcap.base.Sniff(
            network_interface,
            count=-1,
            promisc=int(promisc_mode),
            #todo may need to allow ARP again if discovering
            filter="ip and tcp",
            buffer_size=1 << 20,
            snaplen=256
        )
    except Exception as e:
        ###print(f"ERROR initializing capture: {e}", file=sys.stderr)
        sys.exit(1)

    # --------------------------- capture loop ---------------------------
    packet_number = 0
    for plen, ts, buf in sniffobj.capture():
        packet_number += 1
        try:
            try:
                pkt_info = parse_packet_info_fast(buf, packet_number)
            except Exception as a:
                pkt_info = parse_packet_info(buf, packet_number)
                ####print(f"parse_packet_info_fast {a}",flush=True)
        except Exception as v:
            # could be VLAN, ARP, IPv6, malformedjust drop it
            ####print(f"parse_packet_info_ slow {v}",flush=True)
            continue

        send_deque.append(pkt_info)
        last_activity = time.monotonic()


import sys
import time
import threading
from collections import deque



def read_from_interface_windows(network_interface,
                                unprocessed_packets,  # duplex Pipe
                                promisc_mode=False):

    interface_human_readable=""
    import re, wmi

    # initialize WMI once
    _wmi = wmi.WMI()
    m = re.search(r'\{([0-9A-Fa-f-]+)\}', network_interface)
    if m:
        guid = m.group(1).lower()
        # search the *adapter* class (not the Configuration class!)
        for nic in _wmi.Win32_NetworkAdapter():
            if not nic.GUID:
                continue
            if nic.GUID.strip('{}').lower() == guid:
                friendly = (
                    nic.NetConnectionID
                    or nic.Name
                    or nic.Description
                )
                # *** assignment, not comparison! ***
                interface_human_readable = friendly +network_interface
                break

    import pcap
    # --- 1) Discover all raw NPF device names ---
    devs = pcap.findalldevs()
    if not devs:
        ###print("No capture devices found. Is Npcap installed and running?", file=sys.stderr)
        sys.exit(1)

    # If the caller passed a friendly name (e.g. "Ethernet"), try to match it:
    if network_interface not in devs:
        ###print(f"Warning: '{network_interface}' is not one of the NPF devices.", file=sys.stderr)
        ###print("Available devices:", file=sys.stderr)
        for i, d in enumerate(devs, 1):
            ###print(f"  {i}. {d}", file=sys.stderr)
            pass
        # fall back to first device
        network_interface = devs[0]
        ###print(f"Falling back to first device: {network_interface!r}", file=sys.stderr)

    BATCH_SIZE      = 280
    IDLE_FLUSH_SECS = 1.0
    SLEEP_DELAY     = 0.001  # 1ms when no flush condition met
    send_deque      = deque()
    last_activity   = time.monotonic()

    # --------------------------- sender thread ---------------------------
    def sender_thread():
        nonlocal last_activity
        prior_time = time.monotonic()
        packets_processed = 0

        while True:
            now = time.monotonic()
            to_send = 0

            if (now - prior_time) >= IDLE_FLUSH_SECS:
                ###print(f"len(send_deque) {len(send_deque)} pps {packets_processed} {interface_human_readable}", flush=True)
                packets_processed = 0
                prior_time = now

            if len(send_deque) >= BATCH_SIZE:
                to_send = BATCH_SIZE
            elif send_deque and (now - last_activity) >= IDLE_FLUSH_SECS:
                to_send = len(send_deque)
            else:
                time.sleep(SLEEP_DELAY)
                continue

            batch = [send_deque.popleft() for _ in range(to_send)]
            try:
                unprocessed_packets.send(batch)
            except Exception as e:
                ###print("pipe send error:", e, file=sys.stderr)
                return

            packets_processed += to_send
            

    threading.Thread(target=sender_thread, daemon=True).start()

    # --------------------------- sniffer init ----------------------------
    try:
        sniffer = pcap.pcap(
            name=network_interface,
            snaplen=256,
            promisc=bool(promisc_mode),
            immediate=True,
            timeout_ms=50
        )
    except Exception as e:
        ###print(f"ERROR initializing capture: {e}", file=sys.stderr)
        sys.exit(1)

    # --- verify it really opened ---
    linktype = sniffer.datalink()
    if linktype < 0:
        ###print(f"ERROR: Failed to open '{network_interface}' (datalink() returned {linktype})", file=sys.stderr)
        sys.exit(1)

    # --- install the BPF filter ---
    try:
        sniffer.setfilter("ip and tcp")
    except Exception as e:
        ###print(f"ERROR setting filter: {e}", file=sys.stderr)
        sys.exit(1)

    # --------------------------- capture loop ----------------------------
    packet_number = 0
    for ts, buf in sniffer:
        packet_number += 1
        try:
            try:
                pkt_info = parse_packet_info_fast(buf, packet_number)
            except Exception:
                pkt_info = parse_packet_info(buf, packet_number)
        except Exception:
            continue

        send_deque.append(pkt_info)
        last_activity = time.monotonic()



import re

def fix_npf_name(s: str) -> str:
    # 1) collapse '\\'  '\'
    s = s.replace('\\\\', '\\')
    # 2) collapse '{{GUID}}'  '{GUID}'
    return re.sub(r'\{\{(.*?)\}\}', r'{\1}', s)

def is_npcap_installed():
            try:
                import ctypes
                # Attempt to load both DLLs
                ctypes.WinDLL("wpcap.dll")
                ctypes.WinDLL("Packet.dll")
                ###print("Npcap is installed and available on Windows!")
                return True
            except OSError:
                ###print(f"\n\n\n**Error detected*** \n",flush=True)
                ###print(f"Please install Npcap, which can be found here! https://npcap.com/#download",flush=True)
                ###print(f"Please choose 'Npcap 1.81 installer for Windows 7/2008R2, 8/2012, 8.1/2012R2, 10/2016, 2019, 11 (x86, x64, and ARM64)'",flush=True)
                ###print(f"When installing, make sure you select Install Npcap in WinPcap API-compatible Mode. This should be selected by default.",flush=True)
                ###print(f"\n***Exiting***\n",flush=True)
                sys.exit(1)
            

def choose_windows_interface():
    import pcap, wmi, re
    from ipaddress import ip_address

    # 1) get raw NPF names
    devs = pcap.findalldevs()

    # 2) build a GUID → {ipv4, ipv6} map from WMI
    c = wmi.WMI()
    guid_ip_map = {}
    for cfg in c.Win32_NetworkAdapterConfiguration():
        if not cfg.SettingID:
            continue
        guid = cfg.SettingID.strip('{}').lower()
        addrs = cfg.IPAddress or []
        v4, v6 = [], []
        for ip in addrs:
            try:
                ip_obj = ip_address(ip)
            except ValueError:
                continue
            if ip_obj.version == 4:
                v4.append(ip)
            else:
                v6.append(ip)
        guid_ip_map[guid] = {'ipv4': v4, 'ipv6': v6}

    # 3) produce final mapping from NPF name → its IP lists
    result = {}
    for dev in devs:
        m = re.search(r'\{([0-9A-Fa-f-]+)\}', dev)
        if m:
            guid = m.group(1).lower()
            result[dev] = guid_ip_map.get(guid, {'ipv4': [], 'ipv6': []})
        else:
            result[dev] = {'ipv4': [], 'ipv6': []}

    return result



import psutil
import socket
import time

def choose_mac_linux_interface():
    """
    Returns a dict mapping each up network interface
    to a dict containing its non-loopback IPv4 and IPv6 addresses.
    Example return value:
      {
        'en0': {
          'ipv4': ['192.168.1.42'],
          'ipv6': ['fe80::1234:abcd:5678:9ef0']
        },
        'eth0': {
          'ipv4': ['10.0.0.5'],
          'ipv6': []
        },
        ...
      }
    """
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    result = {}

    for iface, s in stats.items():
        if not s.isup:
            continue

        ipv4s = [
            a.address for a in addrs.get(iface, [])
            if a.family == socket.AF_INET
            and not a.address.startswith("127.")
        ]
        ipv6s = [
            a.address for a in addrs.get(iface, [])
            if a.family == socket.AF_INET6
            and not (a.address == '::1' or a.address.startswith('fe80::1'))
        ]

        if ipv4s or ipv6s:
            result[iface] = {
                'ipv4': ipv4s,
                'ipv6': ipv6s
            }

    return result

        
def check_ip_is_private(ip_str):
    try:
        # Create an IP address object (works for both IPv4 and IPv6)
        ip_obj = ipaddress.ip_address(ip_str)
    
        if ip_obj.is_private:
            return(f"True")
        else:
            return(f"False")
    except ValueError:
        return(f" is not a valid IP address.")

def fetch_light_scope_info(url="https://thelightscope.com/ipinfo"):
    resp = requests.get(url, timeout=5,)
    resp.raise_for_status()
    data = resp.json()

    # Top-level
    queried_ip = data.get("queried_ip")

    # Drill into the asn and location and company buckets:
    asn_rec      = data["results"].get("asn",      {}).get("record", {})
    loc_rec      = data["results"].get("location",  {}).get("record", {})
    company_rec  = data["results"].get("company",   {}).get("record", {})

    return {
        "queried_ip": queried_ip,
        "ASN":         asn_rec.get("asn"),
        "domain":      asn_rec.get("domain"),
        "city":        loc_rec.get("city"),
        "country":     loc_rec.get("country"),
        "as_type":     company_rec.get("as_type"),
        "type":        asn_rec.get("type")
    }



def lightscope_run():
    if  platforminfo.system() != "Windows":
        config_reader = configuration_reader()
        config_settings = config_reader.get_config()
        system_info = get_system_info()
        external_network_information = fetch_light_scope_info()

        # helper to spawn the three subprocesses for one interface
        def spawn_for_interface_mac_linux(iface, internal_ips):
            # 1) make the two duplex pipes
            unproc_consumer, unproc_producer = multiprocessing.Pipe(duplex=True)
            up_consumer, up_producer     = multiprocessing.Pipe(duplex=False)

            # 2) create shared dictionaries for tracking unwanted IPs (multiprocess safe)
            manager = create_manager_with_retry()
            if manager:
                unverified_ips = manager.dict()  # ip_src -> {port: [timestamps...]}
                full_handshake_ips = manager.dict()   # ip_src -> {port: [timestamps...]}
                syn_only_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                no_further_traffic_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                current_honeypot_ports = manager.dict()  # port -> True (tracks active honeypot ports)
            else:
                # Fallback to empty dicts if Manager fails - processes will use local copies
                unverified_ips = {}
                full_handshake_ips = {}
                syn_only_ips = {}
                no_further_traffic_ips = {}
                current_honeypot_ports = {}

            port_status = Ports(
                up_producer,
                internal_ips,
                False,              # internal == external
                iface,
                external_network_information,
                config_settings,
                system_info,
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports
            )

            # Create honeypot instance
            honeypot = Honeypot(
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports,
                up_producer,
                internal_ips,
                iface
            )

            p_lscope = multiprocessing.Process(
                target=port_status.packet_handler,
                args=(unproc_consumer,),
                name=f"lightscope[{iface}]"
            )
            p_reader = multiprocessing.Process(
                target=read_from_interface_mac_linux,
                args=(iface, unproc_producer),
                name=f"reader[{iface}]"
            )
            p_uploader = multiprocessing.Process(
                target=send_data,
                args=(up_consumer,),
                name=f"uploader[{iface}]"
            )
            p_honeypot = multiprocessing.Process(
                target=honeypot.run,
                name=f"honeypot[{iface}]"
            )

            for p in (p_lscope, p_reader, p_uploader, p_honeypot):
                p.start()
                
            # Give processes time to initialize, especially Manager connections
            time.sleep(0.5)

        # --- initial discovery & spawn ---
        interfaces_and_ips = choose_mac_linux_interface()
        processes_per_interface = {}
        for iface, ips in interfaces_and_ips.items():
            ###print(f"Spawning processes for {iface}: {ips}")
            processes_per_interface[iface] = spawn_for_interface_mac_linux(iface, ips)

        ###print("Live interfaces:", list(processes_per_interface))

        # --- monitor loop ---
        while True:
            time.sleep(60)

            new_mapping = choose_mac_linux_interface()
            old_ifaces = set(interfaces_and_ips)
            new_ifaces = set(new_mapping)
            external_network_information = fetch_light_scope_info()

            # 1) clean up removed interfaces
            for gone in old_ifaces - new_ifaces:
                ###print(f"[+] Interface {gone!r} went away, terminating its processes")
                ctx = processes_per_interface.pop(gone)
                for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                    p = ctx[pname]
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=1)
                interfaces_and_ips.pop(gone)

            # 2) detect interfaces whose IP list changed
            for same in old_ifaces & new_ifaces:
                old_ips = interfaces_and_ips[same]
                new_ips = new_mapping[same]
                if old_ips != new_ips:
                    ###print(f"[+] Interface {same!r} IPs changed {old_ips} -> {new_ips}; restarting")
                    # terminate old procs
                    ctx = processes_per_interface.pop(same)
                    for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                        p = ctx[pname]
                        if p.is_alive():
                            p.terminate()
                            p.join(timeout=1)
                    interfaces_and_ips.pop(same)
                    # spawn fresh
                    processes_per_interface[same] = spawn_for_interface_mac_linux(same, new_ips)
                    interfaces_and_ips[same] = new_ips

            # 3) spawn any brand new interfaces
            for born in new_ifaces - old_ifaces:
                ips = new_mapping[born]
                ###print(f"[+] New interface {born!r} with IPs {ips}: spawning")
                processes_per_interface[born] = spawn_for_interface_mac_linux(born, ips)
                interfaces_and_ips[born] = ips

            # (optionally) ###print status
            ###print("-> active interfaces:", list(processes_per_interface.keys()))





    if  platforminfo.system() == "Windows":
        config_reader = configuration_reader()
        config_settings = config_reader.get_config()
        system_info = get_system_info()
        external_network_information = fetch_light_scope_info()

        # helper to spawn the three subprocesses for one interface
        def spawn_for_interface_windows(iface, internal_ips):
            # 1) make the two duplex pipes
            unproc_consumer, unproc_producer = multiprocessing.Pipe(duplex=True)
            up_consumer, up_producer     = multiprocessing.Pipe(duplex=False)

            # 2) create shared dictionaries for tracking unwanted IPs (multiprocess safe)
            manager = create_manager_with_retry()
            if manager:
                unverified_ips = manager.dict()  # ip_src -> {port: [timestamps...]}
                full_handshake_ips = manager.dict()   # ip_src -> {port: [timestamps...]}
                syn_only_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                no_further_traffic_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                current_honeypot_ports = manager.dict()  # port -> True (tracks active honeypot ports)
            else:
                # Fallback to empty dicts if Manager fails - processes will use local copies
                unverified_ips = {}
                full_handshake_ips = {}
                syn_only_ips = {}
                no_further_traffic_ips = {}
                current_honeypot_ports = {}

            port_status = Ports(
                up_producer,
                internal_ips,
                False,              # internal == external
                iface,
                external_network_information,
                config_settings,
                system_info,
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports
            )

            # Create honeypot instance
            honeypot = Honeypot(
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports,
                up_producer,
                internal_ips,
                iface
            )

            p_lscope = multiprocessing.Process(
                target=port_status.packet_handler,
                args=(unproc_consumer,),
                name=f"lightscope[{iface}]"
            )
            p_reader = multiprocessing.Process(
                target=read_from_interface_windows,
                args=(iface, unproc_producer),
                name=f"reader[{iface}]"
            )
            p_uploader = multiprocessing.Process(
                target=send_data,
                args=(up_consumer,),
                name=f"uploader[{iface}]"
            )
            p_honeypot = multiprocessing.Process(
                target=honeypot.run,
                name=f"honeypot[{iface}]"
            )

            for p in (p_lscope, p_reader, p_uploader, p_honeypot):
                p.start()
                
            # Give processes time to initialize, especially Manager connections
            time.sleep(0.5)

        # --- initial discovery & spawn ---
        interfaces_and_ips = choose_windows_interface()
        processes_per_interface = {}
        for iface, ips in interfaces_and_ips.items():
            ###print(f"Spawning processes for {iface}: {ips}")
            processes_per_interface[iface] = spawn_for_interface_windows(iface, ips)

        ###print("Live interfaces:", list(processes_per_interface))

        # --- monitor loop ---
        while True:
            time.sleep(60)

            external_network_information = fetch_light_scope_info()
            new_mapping = choose_windows_interface()
            old_ifaces = set(interfaces_and_ips)
            new_ifaces = set(new_mapping)

            # 1) clean up removed interfaces
            for gone in old_ifaces - new_ifaces:
                ###print(f"[+] Interface {gone!r} went away, terminating its processes")
                ctx = processes_per_interface.pop(gone)
                for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                    p = ctx[pname]
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=1)
                interfaces_and_ips.pop(gone)

            # 2) detect interfaces whose IP list changed
            for same in old_ifaces & new_ifaces:
                old_ips = interfaces_and_ips[same]
                new_ips = new_mapping[same]
                if old_ips != new_ips:
                    ###print(f"[+] Interface {same!r} IPs changed {old_ips} -> {new_ips}; restarting")
                    # terminate old procs
                    ctx = processes_per_interface.pop(same)
                    for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                        p = ctx[pname]
                        if p.is_alive():
                            p.terminate()
                            p.join(timeout=1)
                    interfaces_and_ips.pop(same)
                    # spawn fresh
                    processes_per_interface[same] = spawn_for_interface_windows(same, new_ips)
                    interfaces_and_ips[same] = new_ips

            # 3) spawn any brand new interfaces
            for born in new_ifaces - old_ifaces:
                ips = new_mapping[born]
                ###print(f"[+] New interface {born!r} with IPs {ips}: spawning")
                processes_per_interface[born] = spawn_for_interface_windows(born, ips)
                interfaces_and_ips[born] = ips

            # (optionally) ###print status
            ###print("-> active interfaces:", list(processes_per_interface.keys()))
    



def get_system_info():
        system_info = {
                "System": platforminfo.system(),
                "Release": platforminfo.release(),
                "Version": platforminfo.version(),
                "Machine": platforminfo.machine(),
                "Total_Memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
                'processor'    : platforminfo.processor(),
                'architecture' : platforminfo.architecture()[0]
                #'uname'        : platform.uname()._asdict()
        }

        return system_info

class configuration_reader:
    def __init__(self, config_file='config.ini'):
        # Default values
        #this is the value in the config file
        self.database = "uninitialized"
        self.self_telnet_and_ssh_honeypot_ports_to_forward=[]
        self.osinfo=""
        self.lookup_network_information_list={}
        self.autoupdate=""
        self.randomization_key="uninitialized"
        self.initialize_config("config.ini")
        self.load_config(config_file)
        print(f"***SAVE THIS URL:To view your lightscope reports, please visit https://thelightscope.com/tables/{self.database}")


    def get_config(self):
        config={'database':self.database,'self_telnet_and_ssh_honeypot_ports_to_forward':self.self_telnet_and_ssh_honeypot_ports_to_forward,
        'autoupdate':self.autoupdate,'randomization_key':self.randomization_key}
        return config

    
    def load_config(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        # Assuming all configuration is under the [Settings] section.
        if 'Settings' in config:
            self.database = config.get('Settings', 'database', fallback="Can't read config").lower()
            self.randomization_key=config.get('Settings', 'randomization_key', fallback="Can't read config").lower()
            self.autoupdate=config.get('Settings', 'autoupdate', fallback="Can't read config").lower()
            self.self_telnet_and_ssh_honeypot_ports_to_forward=config.get('Settings', 'self_telnet_and_ssh_honeypot_ports_to_forward', fallback=[])



                
    def initialize_config(self,config_file):
        # Create a ConfigParser object and read the file (if it exists)
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            # If the file doesn't exist, create it with a default [Settings] section.
            config.add_section('Settings')

        # Ensure the "Settings" section exists.
        if not config.has_section('Settings'):
            config.add_section('Settings')

        # Check for the 'database' option. If it does not exist or is empty, generate one.
        #This one doesn't get overwritten, a db name should be the same no matter the other changes the
        #user makes
        # Check for the 'database' option.
        if 'database' not in config['Settings'] or not config['Settings']['database'].strip():
            today = datetime.date.today().strftime("%Y%m%d")        # 8 chars
            max_len = 63                                   # leave room under 64
            rand_len = max_len - len(today) - 1            # "-1" for the underscore
            rand_part = ''.join(random.choices(string.ascii_lowercase, k=rand_len))
            config['Settings']['database'] = f"{today}_{rand_part}"
            ###print(f"Database not found; generated random database name: {config['Settings']['database']}")


        # Check for the 'randomization_key' option.
        if 'randomization_key' not in config['Settings'] or not config['Settings']['randomization_key'].strip():
            randomization_key="randomization_key_"+''.join(random.choices(string.ascii_lowercase, k=46))
            config['Settings']['randomization_key'] = randomization_key
            ###print(f"randomization_key not found; generated random randomization_key name: {randomization_key}")


        # Check for the 'self_telnet_and_ssh_honeypot_ports_to_forward' option.
        if 'self_telnet_and_ssh_honeypot_ports_to_forward' not in config['Settings'] or not config['Settings']['self_telnet_and_ssh_honeypot_ports_to_forward'].strip():
            self_telnet_and_ssh_honeypot_ports_to_forward="no"
            config['Settings']['self_telnet_and_ssh_honeypot_ports_to_forward'] = self_telnet_and_ssh_honeypot_ports_to_forward
            ###print(f"self_telnet_and_ssh_honeypot_ports_to_forward not found; generated : {self_telnet_and_ssh_honeypot_ports_to_forward}")

        # Check for the 'autoupdate' option.
        if 'autoupdate' not in config['Settings'] or not config['Settings']['autoupdate'].strip():
            autoupdate="no"
            config['Settings']['autoupdate'] = autoupdate
            ###print(f"autoupdate not found; : {autoupdate}")


        # Optionally, you can also add the comment as a separate step manually 
        # (Comments are not preserved automatically by configparser when writing back.)
        # Write the configuration back to the file.
        with open(config_file, 'w') as f:
            config.write(f)
        ###print(f"Configuration updated and saved to {config_file}")
        


      


def create_manager_with_retry(max_retries=3):
    """Create multiprocessing Manager with retry logic"""
    import time
    
    for attempt in range(max_retries):
        try:
            print(f"[Manager] Creating Manager (attempt {attempt + 1}/{max_retries})")
            manager = multiprocessing.Manager()
            
            # Test the manager by creating and accessing a simple dict
            test_dict = manager.dict()
            test_dict['test'] = 'value'
            _ = test_dict['test']  # This will fail if Manager is broken
            del test_dict['test']
            
            print("[Manager] Successfully created and tested Manager")
            return manager
            
        except Exception as e:
            print(f"[Manager] Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
            else:
                print("[Manager] All attempts failed, processes will use local dictionaries")
                return None
    
    return None





                
def read_from_interface_mac_linux(network_interface,
                        unprocessed_packets,         # duplex Pipe
                        promisc_mode=False):

    import pylibpcap.base
    BATCH_SIZE      = 280
    IDLE_FLUSH_SECS = 1.0
    SLEEP_DELAY     = 0.001  # 1ms when no flush condition met
    send_deque   = deque()
    last_activity = time.monotonic()

    # --------------------------- sender thread ---------------------------
    def sender_thread():
        nonlocal last_activity
        
        #todo remove debug

        prior_time=time.monotonic()
        packets_processed=0

        

        while True:
            now = time.monotonic()
            to_send = 0

            if (now - prior_time) >= IDLE_FLUSH_SECS:
                ###print(f" len(send_deque) {len(send_deque)} pps {packets_processed} {network_interface}",flush=True)
                packets_processed=0
                prior_time=now



            # 1) full batch ready?
            if len(send_deque) >= BATCH_SIZE:
                to_send = BATCH_SIZE

            # 2) idle timeout expired & buffer non-empty?
            elif send_deque and (now - last_activity) >= IDLE_FLUSH_SECS:
                to_send = len(send_deque)

            # 3) nothing to do right now
            else:
                time.sleep(SLEEP_DELAY)
                continue
            
            
            # build and send batch
            batch = [send_deque.popleft() for _ in range(to_send)]
            try:
                unprocessed_packets.send(batch)       # send to handler
            except Exception as e:
                ###print("pipe send error:", e, file=sys.stderr)
                return



            #todo remove debug code
            packets_processed+=to_send

           

    threading.Thread(target=sender_thread, daemon=True).start()

    # --------------------------- sniffer init ----------------------------
    try:
        sniffobj = pylibpcap.base.Sniff(
            network_interface,
            count=-1,
            promisc=int(promisc_mode),
            #todo may need to allow ARP again if discovering
            filter="ip and tcp",
            buffer_size=1 << 20,
            snaplen=256
        )
    except Exception as e:
        ###print(f"ERROR initializing capture: {e}", file=sys.stderr)
        sys.exit(1)

    # --------------------------- capture loop ---------------------------
    packet_number = 0
    for plen, ts, buf in sniffobj.capture():
        packet_number += 1
        try:
            try:
                pkt_info = parse_packet_info_fast(buf, packet_number)
            except Exception as a:
                pkt_info = parse_packet_info(buf, packet_number)
                ####print(f"parse_packet_info_fast {a}",flush=True)
        except Exception as v:
            # could be VLAN, ARP, IPv6, malformedjust drop it
            ####print(f"parse_packet_info_ slow {v}",flush=True)
            continue

        send_deque.append(pkt_info)
        last_activity = time.monotonic()


import sys
import time
import threading
from collections import deque



def read_from_interface_windows(network_interface,
                                unprocessed_packets,  # duplex Pipe
                                promisc_mode=False):

    interface_human_readable=""
    import re, wmi

    # initialize WMI once
    _wmi = wmi.WMI()
    m = re.search(r'\{([0-9A-Fa-f-]+)\}', network_interface)
    if m:
        guid = m.group(1).lower()
        # search the *adapter* class (not the Configuration class!)
        for nic in _wmi.Win32_NetworkAdapter():
            if not nic.GUID:
                continue
            if nic.GUID.strip('{}').lower() == guid:
                friendly = (
                    nic.NetConnectionID
                    or nic.Name
                    or nic.Description
                )
                # *** assignment, not comparison! ***
                interface_human_readable = friendly +network_interface
                break

    import pcap
    # --- 1) Discover all raw NPF device names ---
    devs = pcap.findalldevs()
    if not devs:
        ###print("No capture devices found. Is Npcap installed and running?", file=sys.stderr)
        sys.exit(1)

    # If the caller passed a friendly name (e.g. "Ethernet"), try to match it:
    if network_interface not in devs:
        ###print(f"Warning: '{network_interface}' is not one of the NPF devices.", file=sys.stderr)
        ###print("Available devices:", file=sys.stderr)
        for i, d in enumerate(devs, 1):
            ###print(f"  {i}. {d}", file=sys.stderr)
            pass
        # fall back to first device
        network_interface = devs[0]
        ###print(f"Falling back to first device: {network_interface!r}", file=sys.stderr)

    BATCH_SIZE      = 280
    IDLE_FLUSH_SECS = 1.0
    SLEEP_DELAY     = 0.001  # 1ms when no flush condition met
    send_deque      = deque()
    last_activity   = time.monotonic()

    # --------------------------- sender thread ---------------------------
    def sender_thread():
        nonlocal last_activity
        prior_time = time.monotonic()
        packets_processed = 0

        while True:
            now = time.monotonic()
            to_send = 0

            if (now - prior_time) >= IDLE_FLUSH_SECS:
                ###print(f"len(send_deque) {len(send_deque)} pps {packets_processed} {interface_human_readable}", flush=True)
                packets_processed = 0
                prior_time = now

            if len(send_deque) >= BATCH_SIZE:
                to_send = BATCH_SIZE
            elif send_deque and (now - last_activity) >= IDLE_FLUSH_SECS:
                to_send = len(send_deque)
            else:
                time.sleep(SLEEP_DELAY)
                continue

            batch = [send_deque.popleft() for _ in range(to_send)]
            try:
                unprocessed_packets.send(batch)
            except Exception as e:
                ###print("pipe send error:", e, file=sys.stderr)
                return

            packets_processed += to_send
            

    threading.Thread(target=sender_thread, daemon=True).start()

    # --------------------------- sniffer init ----------------------------
    try:
        sniffer = pcap.pcap(
            name=network_interface,
            snaplen=256,
            promisc=bool(promisc_mode),
            immediate=True,
            timeout_ms=50
        )
    except Exception as e:
        ###print(f"ERROR initializing capture: {e}", file=sys.stderr)
        sys.exit(1)

    # --- verify it really opened ---
    linktype = sniffer.datalink()
    if linktype < 0:
        ###print(f"ERROR: Failed to open '{network_interface}' (datalink() returned {linktype})", file=sys.stderr)
        sys.exit(1)

    # --- install the BPF filter ---
    try:
        sniffer.setfilter("ip and tcp")
    except Exception as e:
        ###print(f"ERROR setting filter: {e}", file=sys.stderr)
        sys.exit(1)

    # --------------------------- capture loop ----------------------------
    packet_number = 0
    for ts, buf in sniffer:
        packet_number += 1
        try:
            try:
                pkt_info = parse_packet_info_fast(buf, packet_number)
            except Exception:
                pkt_info = parse_packet_info(buf, packet_number)
        except Exception:
            continue

        send_deque.append(pkt_info)
        last_activity = time.monotonic()



import re

def fix_npf_name(s: str) -> str:
    # 1) collapse '\\'  '\'
    s = s.replace('\\\\', '\\')
    # 2) collapse '{{GUID}}'  '{GUID}'
    return re.sub(r'\{\{(.*?)\}\}', r'{\1}', s)

def is_npcap_installed():
            try:
                import ctypes
                # Attempt to load both DLLs
                ctypes.WinDLL("wpcap.dll")
                ctypes.WinDLL("Packet.dll")
                ###print("Npcap is installed and available on Windows!")
                return True
            except OSError:
                ###print(f"\n\n\n**Error detected*** \n",flush=True)
                ###print(f"Please install Npcap, which can be found here! https://npcap.com/#download",flush=True)
                ###print(f"Please choose 'Npcap 1.81 installer for Windows 7/2008R2, 8/2012, 8.1/2012R2, 10/2016, 2019, 11 (x86, x64, and ARM64)'",flush=True)
                ###print(f"When installing, make sure you select Install Npcap in WinPcap API-compatible Mode. This should be selected by default.",flush=True)
                ###print(f"\n***Exiting***\n",flush=True)
                sys.exit(1)
            

def choose_windows_interface():
    import pcap, wmi, re
    from ipaddress import ip_address

    # 1) get raw NPF names
    devs = pcap.findalldevs()

    # 2) build a GUID → {ipv4, ipv6} map from WMI
    c = wmi.WMI()
    guid_ip_map = {}
    for cfg in c.Win32_NetworkAdapterConfiguration():
        if not cfg.SettingID:
            continue
        guid = cfg.SettingID.strip('{}').lower()
        addrs = cfg.IPAddress or []
        v4, v6 = [], []
        for ip in addrs:
            try:
                ip_obj = ip_address(ip)
            except ValueError:
                continue
            if ip_obj.version == 4:
                v4.append(ip)
            else:
                v6.append(ip)
        guid_ip_map[guid] = {'ipv4': v4, 'ipv6': v6}

    # 3) produce final mapping from NPF name → its IP lists
    result = {}
    for dev in devs:
        m = re.search(r'\{([0-9A-Fa-f-]+)\}', dev)
        if m:
            guid = m.group(1).lower()
            result[dev] = guid_ip_map.get(guid, {'ipv4': [], 'ipv6': []})
        else:
            result[dev] = {'ipv4': [], 'ipv6': []}

    return result



import psutil
import socket
import time

def choose_mac_linux_interface():
    """
    Returns a dict mapping each up network interface
    to a dict containing its non-loopback IPv4 and IPv6 addresses.
    Example return value:
      {
        'en0': {
          'ipv4': ['192.168.1.42'],
          'ipv6': ['fe80::1234:abcd:5678:9ef0']
        },
        'eth0': {
          'ipv4': ['10.0.0.5'],
          'ipv6': []
        },
        ...
      }
    """
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    result = {}

    for iface, s in stats.items():
        if not s.isup:
            continue

        ipv4s = [
            a.address for a in addrs.get(iface, [])
            if a.family == socket.AF_INET
            and not a.address.startswith("127.")
        ]
        ipv6s = [
            a.address for a in addrs.get(iface, [])
            if a.family == socket.AF_INET6
            and not (a.address == '::1' or a.address.startswith('fe80::1'))
        ]

        if ipv4s or ipv6s:
            result[iface] = {
                'ipv4': ipv4s,
                'ipv6': ipv6s
            }

    return result

        
def check_ip_is_private(ip_str):
    try:
        # Create an IP address object (works for both IPv4 and IPv6)
        ip_obj = ipaddress.ip_address(ip_str)
    
        if ip_obj.is_private:
            return(f"True")
        else:
            return(f"False")
    except ValueError:
        return(f" is not a valid IP address.")

def fetch_light_scope_info(url="https://thelightscope.com/ipinfo"):
    resp = requests.get(url, timeout=5,)
    resp.raise_for_status()
    data = resp.json()

    # Top-level
    queried_ip = data.get("queried_ip")

    # Drill into the asn and location and company buckets:
    asn_rec      = data["results"].get("asn",      {}).get("record", {})
    loc_rec      = data["results"].get("location",  {}).get("record", {})
    company_rec  = data["results"].get("company",   {}).get("record", {})

    return {
        "queried_ip": queried_ip,
        "ASN":         asn_rec.get("asn"),
        "domain":      asn_rec.get("domain"),
        "city":        loc_rec.get("city"),
        "country":     loc_rec.get("country"),
        "as_type":     company_rec.get("as_type"),
        "type":        asn_rec.get("type")
    }



def lightscope_run():
    if  platforminfo.system() != "Windows":
        config_reader = configuration_reader()
        config_settings = config_reader.get_config()
        system_info = get_system_info()
        external_network_information = fetch_light_scope_info()

        # helper to spawn the three subprocesses for one interface
        def spawn_for_interface_mac_linux(iface, internal_ips):
            # 1) make the two duplex pipes
            unproc_consumer, unproc_producer = multiprocessing.Pipe(duplex=True)
            up_consumer, up_producer     = multiprocessing.Pipe(duplex=False)

            # 2) create shared dictionaries for tracking unwanted IPs (multiprocess safe)
            manager = create_manager_with_retry()
            if manager:
                unverified_ips = manager.dict()  # ip_src -> {port: [timestamps...]}
                full_handshake_ips = manager.dict()   # ip_src -> {port: [timestamps...]}
                syn_only_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                no_further_traffic_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                current_honeypot_ports = manager.dict()  # port -> True (tracks active honeypot ports)
            else:
                # Fallback to empty dicts if Manager fails - processes will use local copies
                unverified_ips = {}
                full_handshake_ips = {}
                syn_only_ips = {}
                no_further_traffic_ips = {}
                current_honeypot_ports = {}

            port_status = Ports(
                up_producer,
                internal_ips,
                False,              # internal == external
                iface,
                external_network_information,
                config_settings,
                system_info,
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports
            )

            # Create honeypot instance
            honeypot = Honeypot(
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports,
                up_producer,
                internal_ips,
                iface
            )

            p_lscope = multiprocessing.Process(
                target=port_status.packet_handler,
                args=(unproc_consumer,),
                name=f"lightscope[{iface}]"
            )
            p_reader = multiprocessing.Process(
                target=read_from_interface_mac_linux,
                args=(iface, unproc_producer),
                name=f"reader[{iface}]"
            )
            p_uploader = multiprocessing.Process(
                target=send_data,
                args=(up_consumer,),
                name=f"uploader[{iface}]"
            )
            p_honeypot = multiprocessing.Process(
                target=honeypot.run,
                name=f"honeypot[{iface}]"
            )

            for p in (p_lscope, p_reader, p_uploader, p_honeypot):
                p.start()
                
            # Give processes time to initialize, especially Manager connections
            time.sleep(0.5)

        # --- initial discovery & spawn ---
        interfaces_and_ips = choose_mac_linux_interface()
        processes_per_interface = {}
        for iface, ips in interfaces_and_ips.items():
            ###print(f"Spawning processes for {iface}: {ips}")
            processes_per_interface[iface] = spawn_for_interface_mac_linux(iface, ips)

        ###print("Live interfaces:", list(processes_per_interface))

        # --- monitor loop ---
        while True:
            time.sleep(60)

            new_mapping = choose_mac_linux_interface()
            old_ifaces = set(interfaces_and_ips)
            new_ifaces = set(new_mapping)
            external_network_information = fetch_light_scope_info()

            # 1) clean up removed interfaces
            for gone in old_ifaces - new_ifaces:
                ###print(f"[+] Interface {gone!r} went away, terminating its processes")
                ctx = processes_per_interface.pop(gone)
                for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                    p = ctx[pname]
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=1)
                interfaces_and_ips.pop(gone)

            # 2) detect interfaces whose IP list changed
            for same in old_ifaces & new_ifaces:
                old_ips = interfaces_and_ips[same]
                new_ips = new_mapping[same]
                if old_ips != new_ips:
                    ###print(f"[+] Interface {same!r} IPs changed {old_ips} -> {new_ips}; restarting")
                    # terminate old procs
                    ctx = processes_per_interface.pop(same)
                    for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                        p = ctx[pname]
                        if p.is_alive():
                            p.terminate()
                            p.join(timeout=1)
                    interfaces_and_ips.pop(same)
                    # spawn fresh
                    processes_per_interface[same] = spawn_for_interface_mac_linux(same, new_ips)
                    interfaces_and_ips[same] = new_ips

            # 3) spawn any brand new interfaces
            for born in new_ifaces - old_ifaces:
                ips = new_mapping[born]
                ###print(f"[+] New interface {born!r} with IPs {ips}: spawning")
                processes_per_interface[born] = spawn_for_interface_mac_linux(born, ips)
                interfaces_and_ips[born] = ips

            # (optionally) ###print status
            ###print("-> active interfaces:", list(processes_per_interface.keys()))





    if  platforminfo.system() == "Windows":
        config_reader = configuration_reader()
        config_settings = config_reader.get_config()
        system_info = get_system_info()
        external_network_information = fetch_light_scope_info()

        # helper to spawn the three subprocesses for one interface
        def spawn_for_interface_windows(iface, internal_ips):
            # 1) make the two duplex pipes
            unproc_consumer, unproc_producer = multiprocessing.Pipe(duplex=True)
            up_consumer, up_producer     = multiprocessing.Pipe(duplex=False)

            # 2) create shared dictionaries for tracking unwanted IPs (multiprocess safe)
            manager = create_manager_with_retry()
            if manager:
                unverified_ips = manager.dict()  # ip_src -> {port: [timestamps...]}
                full_handshake_ips = manager.dict()   # ip_src -> {port: [timestamps...]}
                syn_only_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                no_further_traffic_ips = manager.dict()    # ip_src -> {port: [timestamps...]}
                current_honeypot_ports = manager.dict()  # port -> True (tracks active honeypot ports)
            else:
                # Fallback to empty dicts if Manager fails - processes will use local copies
                unverified_ips = {}
                full_handshake_ips = {}
                syn_only_ips = {}
                no_further_traffic_ips = {}
                current_honeypot_ports = {}

            port_status = Ports(
                up_producer,
                internal_ips,
                False,              # internal == external
                iface,
                external_network_information,
                config_settings,
                system_info,
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports
            )

            # Create honeypot instance
            honeypot = Honeypot(
                unverified_ips,
                full_handshake_ips,
                syn_only_ips,
                no_further_traffic_ips,
                current_honeypot_ports,
                up_producer,
                internal_ips,
                iface
            )

            p_lscope = multiprocessing.Process(
                target=port_status.packet_handler,
                args=(unproc_consumer,),
                name=f"lightscope[{iface}]"
            )
            p_reader = multiprocessing.Process(
                target=read_from_interface_windows,
                args=(iface, unproc_producer),
                name=f"reader[{iface}]"
            )
            p_uploader = multiprocessing.Process(
                target=send_data,
                args=(up_consumer,),
                name=f"uploader[{iface}]"
            )
            p_honeypot = multiprocessing.Process(
                target=honeypot.run,
                name=f"honeypot[{iface}]"
            )

            for p in (p_lscope, p_reader, p_uploader, p_honeypot):
                p.start()
                
            # Give processes time to initialize, especially Manager connections
            time.sleep(0.5)

            return {
                "internal_ips":           internal_ips,
                "pipes": {
                    "unprocessed": (unproc_consumer, unproc_producer),
                    "upload":      (up_consumer, up_producer),
                },
                "lightscope_process":         p_lscope,
                "read_from_interface_process": p_reader,
                "upload_process":             p_uploader,
                "honeypot_process":           p_honeypot,
            }

        # --- initial discovery & spawn ---
        interfaces_and_ips = choose_windows_interface()
        processes_per_interface = {}
        for iface, ips in interfaces_and_ips.items():
            ###print(f"Spawning processes for {iface}: {ips}")
            processes_per_interface[iface] = spawn_for_interface_windows(iface, ips)

        ###print("Live interfaces:", list(processes_per_interface))

        # --- monitor loop ---
        while True:
            time.sleep(60)

            external_network_information = fetch_light_scope_info()
            new_mapping = choose_windows_interface()
            old_ifaces = set(interfaces_and_ips)
            new_ifaces = set(new_mapping)

            # 1) clean up removed interfaces
            for gone in old_ifaces - new_ifaces:
                ###print(f"[+] Interface {gone!r} went away, terminating its processes")
                ctx = processes_per_interface.pop(gone)
                for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                    p = ctx[pname]
                    if p.is_alive():
                        p.terminate()
                        p.join(timeout=1)
                interfaces_and_ips.pop(gone)

            # 2) detect interfaces whose IP list changed
            for same in old_ifaces & new_ifaces:
                old_ips = interfaces_and_ips[same]
                new_ips = new_mapping[same]
                if old_ips != new_ips:
                    ###print(f"[+] Interface {same!r} IPs changed {old_ips} -> {new_ips}; restarting")
                    # terminate old procs
                    ctx = processes_per_interface.pop(same)
                    for pname in ("lightscope_process", "read_from_interface_process", "upload_process", "honeypot_process"):
                        p = ctx[pname]
                        if p.is_alive():
                            p.terminate()
                            p.join(timeout=1)
                    interfaces_and_ips.pop(same)
                    # spawn fresh
                    processes_per_interface[same] = spawn_for_interface_windows(same, new_ips)
                    interfaces_and_ips[same] = new_ips

            # 3) spawn any brand new interfaces
            for born in new_ifaces - old_ifaces:
                ips = new_mapping[born]
                ###print(f"[+] New interface {born!r} with IPs {ips}: spawning")
                processes_per_interface[born] = spawn_for_interface_windows(born, ips)
                interfaces_and_ips[born] = ips

            # (optionally) ###print status
            ###print("-> active interfaces:", list(processes_per_interface.keys()))
    



def get_system_info():
        system_info = {
                "System": platforminfo.system(),
                "Release": platforminfo.release(),
                "Version": platforminfo.version(),
                "Machine": platforminfo.machine(),
                "Total_Memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
                'processor'    : platforminfo.processor(),
                'architecture' : platforminfo.architecture()[0]
                #'uname'        : platform.uname()._asdict()
        }

        return system_info

class configuration_reader:
    def __init__(self, config_file='config.ini'):
        # Default values
        #this is the value in the config file
        self.database = "uninitialized"
        self.self_telnet_and_ssh_honeypot_ports_to_forward=[]
        self.osinfo=""
        self.lookup_network_information_list={}
        self.autoupdate=""
        self.randomization_key="uninitialized"
        self.initialize_config("config.ini")
        self.load_config(config_file)
        print(f"***SAVE THIS URL:To view your lightscope reports, please visit https://thelightscope.com/tables/{self.database}")


    def get_config(self):
        config={'database':self.database,'self_telnet_and_ssh_honeypot_ports_to_forward':self.self_telnet_and_ssh_honeypot_ports_to_forward,
        'autoupdate':self.autoupdate,'randomization_key':self.randomization_key}
        return config

    
    def load_config(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        # Assuming all configuration is under the [Settings] section.
        if 'Settings' in config:
            self.database = config.get('Settings', 'database', fallback="Can't read config").lower()
            self.randomization_key=config.get('Settings', 'randomization_key', fallback="Can't read config").lower()
            self.autoupdate=config.get('Settings', 'autoupdate', fallback="Can't read config").lower()
            self.self_telnet_and_ssh_honeypot_ports_to_forward=config.get('Settings', 'self_telnet_and_ssh_honeypot_ports_to_forward', fallback=[])



                
    def initialize_config(self,config_file):
        # Create a ConfigParser object and read the file (if it exists)
        config = configparser.ConfigParser()
        if os.path.exists(config_file):
            config.read(config_file)
        else:
            # If the file doesn't exist, create it with a default [Settings] section.
            config.add_section('Settings')

        # Ensure the "Settings" section exists.
        if not config.has_section('Settings'):
            config.add_section('Settings')

        # Check for the 'database' option. If it does not exist or is empty, generate one.
        #This one doesn't get overwritten, a db name should be the same no matter the other changes the
        #user makes
        # Check for the 'database' option.
        if 'database' not in config['Settings'] or not config['Settings']['database'].strip():
            today = datetime.date.today().strftime("%Y%m%d")        # 8 chars
            max_len = 63                                   # leave room under 64
            rand_len = max_len - len(today) - 1            # "-1" for the underscore
            rand_part = ''.join(random.choices(string.ascii_lowercase, k=rand_len))
            config['Settings']['database'] = f"{today}_{rand_part}"
            ###print(f"Database not found; generated random database name: {config['Settings']['database']}")


        # Check for the 'randomization_key' option.
        if 'randomization_key' not in config['Settings'] or not config['Settings']['randomization_key'].strip():
            randomization_key="randomization_key_"+''.join(random.choices(string.ascii_lowercase, k=46))
            config['Settings']['randomization_key'] = randomization_key
            ###print(f"randomization_key not found; generated random randomization_key name: {randomization_key}")


        # Check for the 'self_telnet_and_ssh_honeypot_ports_to_forward' option.
        if 'self_telnet_and_ssh_honeypot_ports_to_forward' not in config['Settings'] or not config['Settings']['self_telnet_and_ssh_honeypot_ports_to_forward'].strip():
            self_telnet_and_ssh_honeypot_ports_to_forward="no"
            config['Settings']['self_telnet_and_ssh_honeypot_ports_to_forward'] = self_telnet_and_ssh_honeypot_ports_to_forward
            ###print(f"self_telnet_and_ssh_honeypot_ports_to_forward not found; generated : {self_telnet_and_ssh_honeypot_ports_to_forward}")

        # Check for the 'autoupdate' option.
        if 'autoupdate' not in config['Settings'] or not config['Settings']['autoupdate'].strip():
            autoupdate="no"
            config['Settings']['autoupdate'] = autoupdate
            ###print(f"autoupdate not found; : {autoupdate}")


        # Optionally, you can also add the comment as a separate step manually 
        # (Comments are not preserved automatically by configparser when writing back.)
        # Write the configuration back to the file.
        with open(config_file, 'w') as f:
            config.write(f)
        ###print(f"Configuration updated and saved to {config_file}")
        


      

