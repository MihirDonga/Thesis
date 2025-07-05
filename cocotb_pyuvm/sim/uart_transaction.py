from pyuvm import *
import vsc

class UARTTransaction(uvm_sequence_item):


    def __init__(self, name="UARTTransaction"):
        super().__init__(name)
        # Input Signals of DUT for APB UART's transaction
        self.payload = vsc.rand_uint32_t()  # 32-bit data to be sent on DUT RX pin
        self.transmitter_reg = vsc.rand_uint32_t()  # 32-bit data monitored from DUT TX pin
        self.bad_parity = vsc.rand_bit_t()
        self.bad_parity_frame = vsc.rand_bit_t(7)
        self.sb_corr = vsc.rand_bit_t()
        self.sb_corr_frame = vsc.rand_bit_t(7)
        self.sb_corr_bit = vsc.rand_bit_t(2)
        self.start_bit = vsc.rand_bit_t()
        self.stop_bits = vsc.rand_bit_t(2)
        
        self.payld_func = 0  # 36-bit value for calculations
        

        self._define_constraints()      #constraints


    def __str__(self):
        return (f"UARTTransaction: payload=0x{self.payload:08x}, "
                f"bad_parity={self.bad_parity}, sb_corr={self.sb_corr}")

    # def _define_constraints(self):
    """Randomize all fields with constraints"""
    @vsc.constraint
    def default_start_bit_c(self):
        self.start_bit == 0
        
    @vsc.constraint
    def default_stop_bits_c(self):
        self.stop_bits == 3  # Binary 11
        
    @vsc.constraint
    def corrupt_parity_frame_c(self):
        vsc.if_then(self.bad_parity,
            (self.bad_parity_frame[3:0] > 0))
        
    @vsc.constraint
    def corrupt_sb_frame_c(self):
        vsc.if_then(self.sb_corr,
            (self.sb_corr_frame[3:0] > 0))
        
    @vsc.constraint
    def corrupt_sb_bit_c(self):
        vsc.if_then(self.sb_corr,
            (self.sb_corr_bit != 0))
    
    def randomize(self):
        """
        Randomize all fields with constraints
        Returns:
            bool: True if randomization succeeded, False otherwise
        """
        try:
            if not vsc.randomize(self):
                self.uvm_report_error("RAND_FAIL", "Randomization failed")
                return 0
            self.payld_func = self.payload
            return 1
        except Exception as e:
            self.uvm_report_error("RAND_EXCEPT", f"Randomization exception: {str(e)}")
            return 0


    def calc_parity(self, frame_len, ev_odd):
        """
        Calculate parity bits for the payload
        Args:
            frame_len: Number of bits per frame (5-9)
            ev_odd: True for even parity, False for odd
        Returns:
            Integer with parity bits (7 bits)
        """
        self.payld_func = self.payload & 0xFFFFFFFF  # Zero-padding happens automatically in slicing
        
        parity_result = 0
        
        if frame_len == 5:
            for i in range(7):
                # Extract 5-bit chunks
                chunk = (self.payld_func >> (i*5)) & 0x1F
                parity_bit = self._calculate_single_parity(chunk, ev_odd)
                
                # Apply bad parity if needed
                if self.bad_parity and ((self.bad_parity_frame >> i) & 1):
                    parity_bit = not parity_bit
                
                parity_result |= (parity_bit << i)
                
        elif frame_len == 6:
            for i in range(6):
                chunk = (self.payld_func >> (i*6)) & 0x3F
                parity_bit = self._calculate_single_parity(chunk, ev_odd)
                if self.bad_parity and ((self.bad_parity_frame >> i) & 1):
                    parity_bit = not parity_bit
                parity_result |= (parity_bit << i)
                
        elif frame_len == 7:
            for i in range(5):
                chunk = (self.payld_func >> (i*7)) & 0x7F
                parity_bit = self._calculate_single_parity(chunk, ev_odd)
                if self.bad_parity and ((self.bad_parity_frame >> i) & 1):
                    parity_bit = not parity_bit
                parity_result |= (parity_bit << i)
                
        elif frame_len == 8:
            for i in range(4):
                chunk = (self.payld_func >> (i*8)) & 0xFF
                parity_bit = self._calculate_single_parity(chunk, ev_odd)
                if self.bad_parity and ((self.bad_parity_frame >> i) & 1):
                    parity_bit = not parity_bit
                parity_result |= (parity_bit << i)
                
        elif frame_len == 9:
            for i in range(4):
                chunk = (self.payld_func >> (i*9)) & 0x1FF
                parity_bit = self._calculate_single_parity(chunk, ev_odd)
                if self.bad_parity and ((self.bad_parity_frame >> i) & 1):
                    parity_bit = not parity_bit
                parity_result |= (parity_bit << i)
                
        else:
            self.logger.error(f"Incorrect frame length selected: {frame_len}")
            raise ValueError("Invalid frame length")
            
        return parity_result & 0x7F  # Ensure 7-bit return

    def _calculate_single_parity(self, chunk, ev_odd):
        """Calculate parity for a single chunk"""
        # Count set bits
        bits = bin(chunk).count('1')
        # Even parity: 1 if odd number of bits
        # Odd parity: 1 if even number of bits
        return (bits % 2) != ev_odd
    
# Concrete Example: Parity Calculation
# For frame_len = 5 and payload = 0xA5A5A5A5:
# Split into 5-bit chunks (as shown earlier):
# 00101, 01101, 01011, 01001, 11010, 10110, 00101
# Compute parity for each chunk:
# 00101 → 2 1s → Even parity = 1 (if configured)
# 01101 → 3 1s → Odd parity = 0
# ... and so on for all 7 chunks.    