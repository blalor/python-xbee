#! /usr/bin/python
"""
test_ieee.py

By Brian Lalor, 2011
blalor@bravo5.org

Tests the XBee-PRO 900 implementation class for XBee API compliance
"""
import unittest
from xbee.tests.Fake import FakeDevice, FakeReadDevice
from xbee.pro900 import XBeePro900

class InitXBee(unittest.TestCase):
    """
    Base initalization class
    """
    def setUp(self):
        """
        Initialize XBee object
        """
        self.xbee = XBeePro900(None)

class TestBuildCommand(InitXBee):
    """
    _build_command should properly build a command packet
    """
    
    def test_build_at_data_mismatch(self):
        """
        if not enough or incorrect data is provided, an exception should
        be raised.
        """
        try:
            self.xbee._build_command("at")
        except KeyError:
            # Test passes
            return
    
        # No exception? Fail.
        self.fail(
            "An exception was not raised with improper data supplied"
        )
        
    def test_build_at_data_len_mismatch(self):
        """
        if data of incorrect length is provided, an exception should be 
        raised
        """
        try:
            self.xbee._build_command("at", frame_id="AB", command="MY")
        except ValueError:
            # Test passes
            return
    
        # No exception? Fail.
        self.fail(
            "An exception was not raised with improper data length"
        )
        
    def test_build_at(self):
        """
        _build_command should build a valid at command packet which has
        no parameter data to be saved
        """
        
        at_command = "MY"
        frame = chr(43)
        data = self.xbee._build_command(
            "at", 
            frame_id=frame, 
            command=at_command
        ) 

        expected_data = '\x08+MY'
        self.assertEqual(data, expected_data)
        
    def test_build_at_with_default(self):
        """
        _build_command should build a valid at command packet which has
        no parameter data to be saved and no frame specified (the 
        default value of \x00 should be used)
        """
        
        at_command = "MY"
        data = self.xbee._build_command("at", command=at_command) 

        expected_data = '\x08\x00MY'
        self.assertEqual(data, expected_data)
        
class TestSplitResponse(InitXBee):
    """
    _split_response should properly split a response packet
    """
    
    def test_unrecognized_response(self):
        """
        if a response begins with an unrecognized id byte, 
        _split_response should raise an exception
        """
        data = '\x23\x00\x00\x00'
        
        try:
            self.xbee._split_response(data)
        except KeyError:
            # Passes
            return
            
        # Test Fails
        self.fail()
    
    def test_bad_data_long(self):
        """
        if a response doesn't match the specification's layout, 
        _split_response should raise an exception
        """
        # Over length
        data = '\x8a\x00\x00\x00'
        self.assertRaises(ValueError, self.xbee._split_response, data)
        
    def test_bad_data_short(self):
        """
        if a response doesn't match the specification's layout, 
        _split_response should raise an exception
        """
        # Under length
        data = '\x8a'
        self.assertRaises(ValueError, self.xbee._split_response, data)
    
    def test_split_status_response(self):
        """
        _split_response should properly split a status response packet
        """
        data = '\x8a\x01'
        
        info = self.xbee._split_response(data)
        expected_info = {'id':'status',
                         'status':'\x01'}
        
        self.assertEqual(info, expected_info)
        
    def test_split_short_at_response(self):
        """
        _split_response should properly split an at_response packet which
        has no parameter data
        """
        
        data = '\x88DMY\x01'
        info = self.xbee._split_response(data)
        expected_info = {'id':'at_response',
                         'frame_id':'D',
                         'command':'MY',
                         'status':'\x01'}
        self.assertEqual(info, expected_info)
        
    def test_split_at_resp_with_param(self):
        """
        _split_response should properly split an at_response packet which
        has parameter data
        """
        
        data = '\x88DMY\x01ABCDEF'
        info = self.xbee._split_response(data)
        expected_info = {'id':'at_response',
                         'frame_id':'D',
                         'command':'MY',
                         'status':'\x01',
                         'parameter':'ABCDEF'}
        self.assertEqual(info, expected_info)
        
        
class TestWriteToDevice(unittest.TestCase):
    """
    XBee class should properly write binary data in a valid API
    frame to a given serial device, including a valid command packet.
    """
    
    def test_send_at_command(self):
        """
        calling send should write a full API frame containing the
        API AT command packet to the serial device.
        """
        
        serial_port = FakeDevice()
        xbee = XBeePro900(serial_port)
        
        # Send an AT command
        xbee.send('at', frame_id='A', command='MY')
        
        # Expect a full packet to be written to the device
        expected_data = '\x7E\x00\x04\x08AMY\x10'
        self.assertEqual(serial_port.data, expected_data)
        
        
    def test_send_at_command_with_param(self):
        """
        calling send should write a full API frame containing the
        API AT command packet to the serial device.
        """
        
        serial_port = FakeDevice()
        xbee = XBeePro900(serial_port)
        
        # Send an AT command
        xbee.send(
            'at', 
            frame_id='A', 
            command='MY', 
            parameter='\x00\x00'
        )
        
        # Expect a full packet to be written to the device
        expected_data = '\x7E\x00\x06\x08AMY\x00\x00\x10'
        self.assertEqual(serial_port.data, expected_data)
        
class TestSendShorthand(unittest.TestCase):
    """
    Tests shorthand for sending commands to an XBee provided by
    XBee.__getattr__
    """
    
    def setUp(self):
        """
        Prepare a fake device to read from
        """
        self.ser = FakeDevice()
        self.xbee = XBeePro900(self.ser)
    
    def test_send_at_command(self):
        """
        Send an AT command with a shorthand call
        """
        # Send an AT command
        self.xbee.at(frame_id='A', command='MY')
        
        # Expect a full packet to be written to the device
        expected_data = '\x7E\x00\x04\x08AMY\x10'
        self.assertEqual(self.ser.data, expected_data)
        
    def test_send_at_command_with_param(self):
        """
        calling send should write a full API frame containing the
        API AT command packet to the serial device.
        """
        
        # Send an AT command
        self.xbee.at(frame_id='A', command='MY', parameter='\x00\x00')
        
        # Expect a full packet to be written to the device
        expected_data = '\x7E\x00\x06\x08AMY\x00\x00\x10'
        self.assertEqual(self.ser.data, expected_data)
        
    def test_shorthand_disabled(self):
        """
        When shorthand is disabled, any attempt at calling a 
        non-existant attribute should raise AttributeError
        """
        self.xbee = XBeePro900(self.ser, shorthand=False)
        
        try:
            self.xbee.at
        except AttributeError:
            pass
        else:
            self.fail("Specified shorthand command should not exist")

class TestReadFromDevice(unittest.TestCase):
    """
    XBee class should properly read and parse binary data from a serial 
    port device.
    """
    def test_read_90(self):
        """
        Read and parse an RX packet from an XBee-Pro 900MHz module.
        """
        data = '~\x00L\x90\x00}3\xa2\x00@x\xcd9\xff\xfe\x02\x00\x0f\x0e/AccelX\x00\x00\x00\x00\x00\x00\xc0L?AccelY\x00\x00\x00\x00\x00\x00\xc0L?AccelZ\x00\x00\x00\x00\x00\x00\xc0L?Yaw\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0L?\xc1'

        device = FakeReadDevice(data)
        xbee = XBeePro900(device, escaped=True)
        
        info = xbee.wait_read_frame()

        # import pprint
        # pprint.pprint(info)
        ## {'frame_id': '\x00',
        ##  'id': 'rx_pro',
        ##  'reserved': '\xfe\x02',
        ##  'rf_data': '\x0f\x0e/AccelX\x00\x00\x00\x00\x00\x00\xc0L?AccelY\x00\x00\x00\x00\x00\x00\xc0L?AccelZ\x00\x00\x00\x00\x00\x00\xc0L?Yaw\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0L?',
        ##  'rx_opt': '\x00',
        ##  'source_addr_long': '\x13\xa2\x00@x\xcd9\xff'}

        expected_info = {
            'id'         :'rx',
            'frame_id'   :'\x00',
            'source_addr':'\x13\xa2\x00\x40\x78\xcd\x39',
            'reserved'   :'\xff\xfe',
            'options'    :'\x02',
            'rf_data'    :'\x00\x0f\x0e/AccelX\x00\x00\x00\x00\x00\x00\xc0L?AccelY\x00\x00\x00\x00\x00\x00\xc0L?AccelZ\x00\x00\x00\x00\x00\x00\xc0L?Yaw\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc0L?'
        }

        self.maxDiff = None
        self.assertEqual(info, expected_info)
        

    def test_read_at(self):
        """
        read and parse a parameterless AT command
        """
        device = FakeReadDevice('\x7E\x00\x05\x88DMY\x01\x8c')
        xbee = XBeePro900(device)
        
        info = xbee.wait_read_frame()
        expected_info = {'id':'at_response',
                         'frame_id':'D',
                         'command':'MY',
                         'status':'\x01'}
        self.assertEqual(info, expected_info)
        
    def test_read_at_params(self):
        """
        read and parse an AT command with a parameter
        """
        device = FakeReadDevice(
            '\x7E\x00\x08\x88DMY\x01\x00\x00\x00\x8c'
        )
        xbee = XBeePro900(device)
        
        info = xbee.wait_read_frame()
        expected_info = {'id':'at_response',
                         'frame_id':'D',
                         'command':'MY',
                         'status':'\x01',
                         'parameter':'\x00\x00\x00'}
        self.assertEqual(info, expected_info)


if __name__ == '__main__':
    unittest.main()
