from pyuvm import *
import vsc
@vsc.covergroup
class ConfigCoverage(object):
    def __init__(self):
        self.with_sample(dict(
                    bRate=vsc.bit_t(32),
                    frame_len=vsc.bit_t(32),
                    parity=vsc.bit_t(32),
                    n_sb=vsc.bit_t(32)
                ))        
        
        # Baud rate coverpoint
        self.bRate_cp = vsc.coverpoint(self.bRate, bins=dict(
            b4800 = vsc.bin(4800),
            b9600 = vsc.bin(9600),
            b14400 = vsc.bin(14400),
            b19200 = vsc.bin(19200),
            b38400 = vsc.bin(38400),
            b57600 = vsc.bin(57600),
            b115200 = vsc.bin(115200),
            b128000 = vsc.bin(128000),
            b63 = vsc.bin(63),
            b0 = vsc.bin(0)
        ))
        
        # Frame length coverpoint
        self.frame_len_cp = vsc.coverpoint(self.frame_len, bins=dict(
            f5 = vsc.bin(5),
            f6 = vsc.bin(6),
            f7 = vsc.bin(7),
            f8 = vsc.bin(8)
        ))
        
        # Parity coverpoint
        self.parity_cp = vsc.coverpoint(self.parity, bins=dict(
            none = vsc.bin(0),
            even = vsc.bin(1),
            odd = vsc.bin(2),
            other = vsc.bin(3)
        ))
        
        # Stop bits coverpoint
        self.n_sb_cp = vsc.coverpoint(self.n_sb, bins=dict(
            one = vsc.bin(0),
            two = vsc.bin(1)
        ))
        
        # Cross coverage
        self.cfg_cross = vsc.cross([self.bRate_cp, self.frame_len_cp, 
                                  self.parity_cp, self.n_sb_cp])

@vsc.covergroup
class TxCoverage(object):
    def __init__(self):
        self.with_sample(dict(
            apb_data=vsc.bit_t(32),
            uart_data=vsc.bit_t(32)
        ))
        
        # APB data coverage
        self.apb_cp = vsc.coverpoint(self.apb_data, bins=dict(
            low = vsc.bin_array(['low'], [(0x00000000, 0x00000010)]),
            mid = vsc.bin_array(['mid'], [(0x00000010, 0x00000020)]),
            high = vsc.bin_array(['high'], [(0x80000020, 0x000000FF)]),
            corners = vsc.bin([0x00000000, 0x00000FF])
        ))
        
        # UART data coverage
        self.uart_cp = vsc.coverpoint(self.uart_data, bins=dict(
            low = vsc.bin_array(['low'], [(0x00000000, 0x000000FF)]),
            mid = vsc.bin_array(['mid'], [(0x00000100, 0x7FFFFFFF)]),
            high = vsc.bin_array(['high'], [(0x80000000, 0xFFFFFFFF)]),
            corners = vsc.bin([0x00000000, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ))

@vsc.covergroup
class RxCoverage(object):
    def __init__(self):
        self.with_sample(dict(
            apb_data=vsc.bit_t(32),
            uart_data=vsc.bit_t(32),
            error=vsc.bit_t(1)
        ))
        
        # APB data coverage (same as Tx)
        self.apb_cp = vsc.coverpoint(self.apb_data, bins=dict(
            low = vsc.bin_array(['low'], [(0x00000000, 0x000000FF)]),
            mid = vsc.bin_array(['mid'], [(0x00000100, 0x7FFFFFFF)]),
            high = vsc.bin_array(['high'], [(0x80000000, 0xFFFFFFFF)]),
            corners = vsc.bin([0x00000000, 0xFFFFFFFF,0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ))
        
        # UART data coverage (same as Tx)
        self.uart_cp = vsc.coverpoint(self.uart_data, bins=dict(
            low = vsc.bin_array(['low'], [(0x00000000, 0x000000FF)]),
            mid = vsc.bin_array(['mid'], [(0x00000100, 0x7FFFFFFF)]),
            high = vsc.bin_array(['high'], [(0x80000000, 0xFFFFFFFF)]),
            corners = vsc.bin([0x00000000, 0xFFFFFFFF,0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ))
        
        # Error coverage
        self.error_cp = vsc.coverpoint(self.error, bins=dict(
            error_set = vsc.bin(1),
            error_clear = vsc.bin(0)
        ))