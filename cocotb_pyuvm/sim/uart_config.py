from pyuvm import *
import vsc
from enum import Enum, auto


from enum import Enum
class uvm_active_passive_enum(Enum):
    UVM_ACTIVE = auto()
    UVM_PASSIVE = auto()
    
@vsc.randobj
class uart_config(uvm_object):
    def __init__(self, name="uart_config"):
        super().__init__(name)
        # From APB AGENTs (randomizable)
        self.frame_len = vsc.rand_uint32_t()
        self.n_sb = vsc.rand_uint32_t()
        self.parity = vsc.rand_uint32_t()
        self.bRate = vsc.rand_uint32_t()
        # To UART Monitor
        self.baud_rate = 0

        # Constants (Addresses)
        self.baud_config_addr      = 0x0
        self.frame_config_addr     = 0x4
        self.parity_config_addr    = 0x8
        self.stop_bits_config_addr = 0xc
        self.trans_data_addr       = 0x10
        self.receive_data_addr     = 0x14

        self.loop_time             = 1

        # UVM active/passive enum equivalent
        self.is_active = uvm_active_passive_enum.UVM_ACTIVE

        # self._setup_constraints()

    # def _setup_constraints(self):
    # Apply constraints
    @vsc.constraint
    def frame_len_c(self):
        self.frame_len.inside(vsc.rangelist(5, 6, 7, 8))
        
    @vsc.constraint
    def n_sb_c(self):
        self.n_sb.inside(vsc.rangelist(0, 1))
        
    @vsc.constraint
    def parity_c(self):
        self.parity.inside(vsc.rangelist(0, 1, 2, 3))
        
    @vsc.constraint
    def bRate_c(self):
        self.bRate.inside(vsc.rangelist(4800, 9600, 14400, 19200, 
                            38400, 57600, 115200, 128000, 63, 0))

    def randomize(self):
        """Randomize the configuration using VSC"""
        try:
            vsc.randomize(self)
            self.baudRateFunc()  # Update baud rate after randomization
            return True
        except Exception as e:
            print(f"Randomization failed: {e}")
            return False

    def baudRateFunc(self):
        bRate_to_baud = {
            4800:   10416,
            9600:   5208,
            14400:  3472,
            19200:  2604,
            38400:  1302,
            57600:   868,
            115200:  434,
            128000:  392,
        }
        self.baud_rate = bRate_to_baud.get(self.bRate, 5208)

    def __str__(self):
        return (f"UART Config:\n"
                f"  frame_len: {self.frame_len}\n"
                f"  n_sb: {self.n_sb}\n"
                f"  parity: {self.parity}\n"
                f"  bRate: {self.bRate}\n"
                f"  baud_rate: {self.baud_rate}\n"
                f"  is_active: {self.is_active.name}")


