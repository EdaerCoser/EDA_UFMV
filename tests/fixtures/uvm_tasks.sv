// tests/fixtures/uvm_tasks.sv
// UVM寄存器模型操作示例

// 模式1: 基本FrontDoor写入
task automatic basic_write(input logic [31:0] value);
  uvm_status_e status;
  reg_model.REG_NAME.write(status, value, UVM_FRONTDOOR);
endtask

// 模式2: BackDoor写入
task automatic backdoor_write(input logic [31:0] value);
  uvm_status_e status;
  reg_model.REG_NAME.write(status, value, UVM_BACKDOOR);
endtask

// 模式3: 单索引数组
task automatic array_write(input int channel, input logic [31:0] value);
  uvm_status_e status;
  reg_model.REG_CH[channel].write(status, value, UVM_FRONTDOOR);
endtask

// 模式4: 多维数组
task automatic multidim_write(input int ch, input int bank, input logic [31:0] value);
  uvm_status_e status;
  reg_model.BANK[ch][bank_id].write(status, value);
endtask

// 模式5: 读取操作
task automatic read_operation();
  uvm_status_e status;
  uvm_reg_data_t value;
  reg_model.REG_NAME.read(status, value, UVM_FRONTDOOR);
endtask

// 模式6: Set/Get操作
task automatic set_get_operation(input logic [31:0] value);
  reg_model.REG_NAME.set(value);
  value = reg_model.REG_NAME.get();
endtask

// 模式7: Reset
task automatic reset_operation();
  uvm_status_e status;
  reg_model.REG_NAME.reset(status);
endtask

// 完整示例: DMA初始化
task automatic init_dma(
  input int channel,
  input logic [31:0] base_addr,
  input int length
);
  uvm_status_e status;

  // Enable DMA channel
  dma_reg_model.DMA_CTRL[channel].write(status, 32'h0000_0001, UVM_FRONTDOOR);

  // Set address and length
  dma_reg_model.DMA_ADDR[channel].write(status, base_addr);
  dma_reg_model.DMA_LEN[channel].write(status, length);

  // Start transfer
  dma_reg_model.DMA_CMD[channel].write(status, 32'h0000_0001);
endtask
