"""
pro900.py

By Brian Lalor, 2011
Modified version of ieee.py to match specification of XBee-PRO 900 modules.

This module provides an XBee-PRO 900 API library.
"""
import struct
from xbee.base import XBeeBase

class XBeePro900(XBeeBase):
    """
    Provides an implementation of the XBee API for XBee-PRO 900 modules with
    recent firmware.
    
    Commands may be sent to a device by instansiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device syncronously by calling wait_read_frame. For
    asynchronous reads, see the definition of XBeeBase.
    """
    # Packets which can be sent to an XBee
    
    # Format: 
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name':'id',        'len':1,      'default':'\x08'},
                         {'name':'frame_id',  'len':1,      'default':'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "queued_at":
                        [{'name':'id',        'len':1,      'default':'\x09'},
                         {'name':'frame_id',  'len':1,      'default':'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "tx":
                        [{'name':'id',              'len':1,        'default':'\x10'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':None},
                         {'name':'reserved',        'len':2,        'default':'\xFF\xFE'},
                         {'name':'broadcast_radius','len':1,        'default':'\x00'},
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "tx_explicit":
                        [{'name':'id',              'len':1,        'default':'\x11'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':None},
                         {'name':'reserved',        'len':2,        'default':'\xFF\xFE'},
                         {'name':'source_endpoint', 'len':1,        'default':None},
                         {'name':'dest_endpoint',   'len':1,        'default':None},
                         {'name':'cluster_id',      'len':2,        'default':None},
                         {'name':'profile_id',      'len':2,        'default':None},
                         {'name':'broadcast_radius','len':1,        'default':'\x00'},
                         {'name':'options',         'len':1,        'default':'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                    "remote_at":
                        [{'name':'id',              'len':1,        'default':'\x17'},
                         {'name':'frame_id',        'len':1,        'default':'\x00'},
                         # dest_addr_long is 8 bytes (64 bits), so use an unsigned long long
                         {'name':'dest_addr_long',  'len':8,        'default':struct.pack('>Q', 0)},
                         {'name':'reserved',        'len':2,        'default':'\xFF\xFE'},
                         {'name':'options',         'len':1,        'default':'\x02'},
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}]
                    }
    
    # Packets which can be received from an XBee
    
    # Format: 
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
    #                  ...
    #                  ]
    #            parse_as_io_samples:name of field to parse as io
    #           }
    #           ...
    #        }
    #
    api_responses = {"\x88":
                        {'name':'at_response',
                         'structure':
                            [{'name':'frame_id',    'len':1},
                             {'name':'command',     'len':2},
                             {'name':'status',      'len':1},
                             {'name':'parameter',   'len':None}]},
                     "\x8A":
                        {'name':'status',
                         'structure':
                            [{'name':'status',      'len':1}]},
                     "\x8B":
                        {'name':'tx_status',
                         'structure':
                            [{'name':'frame_id',         'len':1},
                             {'name':'reserved',         'len':2},
                             {'name':'retry_count',      'len':1},
                             {'name':'status',           'len':1},
                             {'name':'discovery_status', 'len':1}]},
                     "\x90":
                        {'name':'rx',
                         'structure':
                            [{'name':'frame_id',         'len':1},
                             {'name':'source_addr',      'len':7}, # yes, seven!
                             {'name':'reserved',         'len':2},
                             {'name':'options',          'len':1},
                             {'name':'rf_data',          'len':None}]},
                     "\x91":
                        {'name':'rx_explicit',
                         'structure':
                            [{'name':'frame_id',         'len':1},
                             {'name':'source_addr',      'len':8}, # yes, eight!
                             {'name':'reserved',         'len':2},
                             {'name':'source_endpoint',  'len':1},
                             {'name':'dest_endpoint',    'len':1},
                             {'name':'cluster_id',       'len':2},
                             {'name':'profile_id',       'len':2},
                             {'name':'options',          'len':1},
                             {'name':'rf_data',          'len':None}]},
                     "\x95":
                        {'name':'node_id_indicator',
                         'structure':
                            [{'name':'sender_addr',       'len':8}, # yes, eight!
                             {'name':'sender_network',    'len':2},
                             {'name':'options',           'len':1},
                             {'name':'source_network',    'len':2},
                             {'name':'source_addr',       'len':8}, # yes, eight!
                             {'name':'node_id',           'len':'null_terminated'},
                             {'name':'parent_source_addr','len':2}]},
                     "\x97":
                        {'name':'remote_at_response',
                         'structure':
                            [{'name':'frame_id',        'len':1},
                             {'name':'source_addr',     'len':8},
                             {'name':'reserved',        'len':2},
                             {'name':'command',         'len':2},
                             {'name':'status',          'len':1},
                             {'name':'parameter',       'len':None}]},
                     }
    
    def __init__(self, *args, **kwargs):
        # Call the super class constructor to save the serial port
        super(XBeePro900, self).__init__(*args, **kwargs)
