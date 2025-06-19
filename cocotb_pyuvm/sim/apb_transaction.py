from pyuvm import *

class APBTransaction(uvm_sequence_item):
    def __init__(self, name="APBTransaction"):
        super().__init__(name)
        # Input Signals of DUT for APB UART's transaction
        self.PWRITE = False       # Read/Write flag
        self.PWDATA = 0           # Write data (32-bit)
        self.PADDR = 0            # Address (32-bit)
        
        # Output Signals of DUT for APB UART's transaction
        self.PREADY = False       # Transfer ready
        self.PSLVERR = False      # Slave error
        self.PRDATA = 0           # Read data (32-bit)

    def __str__(self):
        return (f"APBTransaction: PWRITE={self.PWRITE}, PADDR=0x{self.PADDR:08x}, "
                f"PWDATA=0x{self.PWDATA:08x}, PREADY={self.PREADY}, "
                f"PSLVERR={self.PSLVERR}, PRDATA=0x{self.PRDATA:08x}")

    def randomize(self):
        """Randomize transaction fields"""
        import random
        self.PWRITE = random.choice([True, False])
        self.PWDATA = random.randint(0, 0xFFFFFFF)
        self.PADDR = random.randint(0, 0xFFFFFFF)
        # Note: Output signals typically wouldn't be randomized in driver
        return True