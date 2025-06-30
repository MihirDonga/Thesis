from pyuvm import *
import vsc

class APBTransaction(uvm_sequence_item):

    # uvm_object_utils(apb_transaction)
    
    # # Field automation (replaces uvm_field_int macros)
    # uvm_field_int('PWRITE')
    # uvm_field_int('PWDATA')
    # uvm_field_int('PADDR')
    # uvm_field_int('PREADY')
    # uvm_field_int('PSLVERR') 
    # uvm_field_int('PRDATA')

    def __init__(self, name="APBTransaction"):
        super().__init__(name)
        # Input Signals of DUT for APB UART's transaction
        self.PWRITE = vsc.rand_bit_t(1)  # 1-bit random
        self.PWDATA = vsc.rand_uint32_t()  # 32-bit random data
        self.PADDR = vsc.rand_uint32_t()  # 32-bit random address
        
        # Output Signals of DUT for APB UART's transaction
        self.PREADY = 0       # Transfer ready
        self.PSLVERR = 0      # Slave error
        self.PRDATA = 0           # Read data (32-bit)


    @vsc.constraint
    def apb_valid_c(self):
        # Basic APB protocol constraints
        self.PADDR % 4 == 0            # 32-bit aligned addresses
        self.PADDR <= 0xFFFF_FFFC       # Reasonable address range
        
        # Read/Write specific constraints
        with vsc.if_then(self.PWRITE == 1):
            self.PWDATA != 0            # No all-0 writes
            self.PWDATA != 0xFFFF_FFFF  # No all-1 writes
        with vsc.else_then:
            self.PWDATA == 0            # Reads should have 0 data
        
    def randomize(self, **kwargs):
        """
        Enhanced randomization with proper error handling
        Args:
            **kwargs: Additional constraints
        Returns:
            bool: True if randomization succeeded
        """
        try:
            if not vsc.randomize(self, kwargs):
                self.uvm_report_error("RAND_FAIL", "Randomization failed for APB transaction")
                return 0
            return 1
        except Exception as e:
            self.uvm_report_error("RAND_EXCEPT", f"Randomization exception: {str(e)}")
            return 0
        
    def __str__(self):
        return (f"APBTransaction: PWRITE={self.PWRITE}, PADDR=0x{self.PADDR:08x}, "
                f"PWDATA=0x{self.PWDATA:08x}, PREADY={self.PREADY}, "
                f"PSLVERR={self.PSLVERR}, PRDATA=0x{self.PRDATA:08x}")
