// // helloworld.sv
// module helloworld;

//   initial begin
//     $display("Hello, World!");
//     $finish;
//   end

// endmodule
module full_adder(
    input a,
    input b,
    input cin,
    output sum,
    output cout
);
    assign sum = a ^ b ^ cin;
    assign cout = (a & b) | (cin & (a ^ b));
endmodule