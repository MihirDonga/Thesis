`define UART_START_ADDR 32'd0
`define UART_END_ADDR 32'd5


class apb_config extends uvm_object;

    // Variables
    rand bit[31:0] slave_Addr;
         bit[2:0]  psel_Index;

    uvm_active_passive_enum is_active = UVM_ACTIVE;

    // UVM Factory Registration
    `uvm_object_utils_begin(apb_config)
        `uvm_field_int(slave_Addr, UVM_DEFAULT)
        `uvm_field_int(psel_Index, UVM_DEFAULT)
        `uvm_field_enum(uvm_active_passive_enum, is_active, UVM_ALL_ON)
    `uvm_object_utils_end

    // Constraint: Limit address to UART range only
    constraint addr_cst { slave_Addr inside { [`UART_START_ADDR:`UART_END_ADDR] }; }

    // Set psel_Index only for UART
    function void AddrCalcFunc();
        if ((slave_Addr >= `UART_START_ADDR) && (slave_Addr <= `UART_END_ADDR))
            psel_Index = 3'b001; // or just 1, depending on your APB multiplexer logic
        else
            psel_Index = 3'b000;
    endfunction

    // Constructor
    function new(string name = "apb_config");
        super.new(name);
    endfunction

endclass
