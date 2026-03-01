// tests/fixtures/simple_tasks.sv
// 简单的SystemVerilog task示例

module simple_tasks;

// 基础task（无参数）
task simple_write();
  // 简单的写操作
endtask

// 带参数的task
task write_register(input int value);
  // 写入寄存器
endtask

// 多个操作的task
task multiple_ops();
  // 多个操作
endtask

endmodule
