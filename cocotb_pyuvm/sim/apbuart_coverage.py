from pyuvm import *
import cocotb

class UartConfigCoverage(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        
    def build_phase(self):
        # Baud rate coverage
        self.baud_cp = CoveragePoint("baud_cp")
        self.baud_cp.add_bins([
            CoverageBin("b4800", 4800),
            CoverageBin("b9600", 9600),
            CoverageBin("b19200", 19200),
            CoverageBin("b38400", 38400),
            CoverageBin("b57600", 57600),
            CoverageBin("b115200", 115200),
            CoverageBin("b128000", 128000),
            CoverageBin("b63", 63),
            CoverageBin("b0", 0)
        ])
        
        # Frame length coverage
        self.frame_cp = CoveragePoint("frame_cp")
        self.frame_cp.add_bins([
            CoverageBin("f5", 5),
            CoverageBin("f6", 6),
            CoverageBin("f7", 7),
            CoverageBin("f8", 8)
        ])
        
        # Parity coverage
        self.parity_cp = CoveragePoint("parity_cp")
        self.parity_cp.add_bins([
            CoverageBin("none", 0),
            CoverageBin("even", 1),
            CoverageBin("odd", 2)
        ])
        
        # Stop bits coverage
        self.stopbit_cp = CoveragePoint("stopbit_cp")
        self.stopbit_cp.add_bins([
            CoverageBin("one", 1),
            CoverageBin("two", 2)
        ])
        
        # Cross coverage
        self.cfg_cross = CoverageCross("cfg_cross", [
            self.baud_cp, self.frame_cp, self.parity_cp, self.stopbit_cp
        ])
        
    def sample(self, baud, frame, parity, stop):
        self.baud_cp.sample(baud)
        self.frame_cp.sample(frame)
        self.parity_cp.sample(parity)
        self.stopbit_cp.sample(stop)
        self.cfg_cross.sample()

class TxCoverage(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)

    def build_phase(self):
        # APB data coverage
        self.apb_cp = CoveragePoint("apb_cp")
        self.apb_cp.add_bins([
            CoverageBin("low_values", (0x00000000, 0x000000FF)),
            CoverageBin("mid_values", (0x00000100, 0x7FFFFFFF)),
            CoverageBin("high_values", (0x80000000, 0xFFFFFFFF)),
            CoverageBin("corner_values", [0x00000000, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ])
        
        # UART data coverage
        self.uart_cp = CoveragePoint("uart_cp")
        self.uart_cp.add_bins([
            CoverageBin("low_values", (0x00000000, 0x000000FF)),
            CoverageBin("mid_values", (0x00000100, 0x7FFFFFFF)),
            CoverageBin("high_values", (0x80000000, 0xFFFFFFFF)),
            CoverageBin("corner_values", [0x00000000, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ])
        
    def sample(self, apb_data, uart_data):
        self.apb_cp.sample(apb_data)
        self.uart_cp.sample(uart_data)

class RxCoverage(uvm_component):
    def __init__(self, name, parent):
        super().__init__(name, parent)

    def build_phase(self):
        # APB data coverage
        self.apb_cp = CoveragePoint("apb_cp")
        self.apb_cp.add_bins([
            CoverageBin("low_values", (0x00000000, 0x000000FF)),
            CoverageBin("mid_values", (0x00000100, 0x7FFFFFFF)),
            CoverageBin("high_values", (0x80000000, 0xFFFFFFFF)),
            CoverageBin("corner_values", [0x00000000, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ])
        
        # UART data coverage
        self.uart_cp = CoveragePoint("uart_cp")
        self.uart_cp.add_bins([
            CoverageBin("low_values", (0x00000000, 0x000000FF)),
            CoverageBin("mid_values", (0x00000100, 0x7FFFFFFF)),
            CoverageBin("high_values", (0x80000000, 0xFFFFFFFF)),
            CoverageBin("corner_values", [0x00000000, 0xFFFFFFFF, 0xAAAAAAAA, 0x55555555, 0xDEADBEEF])
        ])
        
        # Error coverage
        self.error_cp = CoveragePoint("error_cp")
        self.error_cp.add_bins([
            CoverageBin("error_set", True),
            CoverageBin("error_clear", False)
        ])
        
    def sample(self, apb_data, uart_data, error):
        self.apb_cp.sample(apb_data)
        self.uart_cp.sample(uart_data)
        self.error_cp.sample(error)
