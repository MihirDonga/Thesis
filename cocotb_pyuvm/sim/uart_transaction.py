from pyuvm import *
import random
from cocotb.triggers import Timer, RisingEdge

class UARTTransaction(uvm_sequence_item):
    def __init__(self, name="UARTTransaction"):
        super().__init__(name)
        # Input Signals of DUT for APB UART's transaction
        self.payload = 0                  # 32-bit data to be sent on DUT RX pin
        self.transmitter_reg = 0          # 32-bit data monitored from DUT TX pin
        self.bad_parity = False
        self.bad_parity_frame = 0         # Now an integer (7 bits)
        self.sb_corr = False
        self.sb_corr_frame = 0            # Now an integer (7 bits)
        self.sb_corr_bit = 0              # Now an integer (2 bits)
        self.start_bit = 0
        self.stop_bits = 0b11             # Default to binary 11 (2 bits)
        self.payld_func = 0               # 36-bit extended payload

    def __str__(self):
        return (f"UARTTransaction: payload=0x{self.payload:08x}, "
                f"bad_parity={self.bad_parity}, sb_corr={self.sb_corr}")

    def randomize(self):
        """Randomize all fields with constraints"""
        self.start_bit = 0                 # Constraint: always 0
        self.stop_bits = 0b11              # Constraint: always 11
        
        # Randomize with constraints
        self.payload = random.randint(0, 2**32-1)
        self.bad_parity = random.choice([True, False])
        self.sb_corr = random.choice([True, False])
        
        # Constraint: bad_parity_frame[3:0] > 0
        self.bad_parity_frame = random.randint(1, 2**4-1) | (random.randint(0, 7) << 4)
        
        # Constraint: sb_corr_frame[3:0] > 0
        self.sb_corr_frame = random.randint(1, 2**4-1) | (random.randint(0, 7) << 4)
        
        # Constraint: sb_corr_bit != 0
        self.sb_corr_bit = random.choice([1, 2, 3])
        
        return True

    def calc_parity(self, frame_len, ev_odd):
        """
        Calculate parity bits for the payload
        Args:
            frame_len: Number of bits per frame (5-9)
            ev_odd: True for even parity, False for odd
        Returns:
            Integer with parity bits (7 bits)
        """
        self.payld_func = self.payload  # Zero-padding happens automatically in slicing
        
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
            
        return parity_result

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