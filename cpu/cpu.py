"""
Nathanael Davidson CS211 2025-11-5

Duck Machine model DM2022 CPU
"""

# import context  #  Python import search from project root
from typing import Callable
from instruction_set.instr_format import Instruction, OpCode, CondFlag, decode
from cpu.memory import Memory
from cpu.register import Register, ZeroRegister
from cpu.mvc import MVCEvent, MVCListenable
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

class ALU(object):
    """The arithmetic logic unit (also called a "functional unit"
    in a modern CPU) executes a selected function but does not
    otherwise manage CPU state. A modern CPU core may have several
    ALUs to boost performance by performing multiple operatons
    in parallel, but the Duck Machine has just one ALU in one core.
    """
    # The ALU chooses one operation to apply based on a provided
    # operation code.  These are just simple functions of two arguments;
    # in hardware we would use a multiplexer circuit to connect the
    # inputs and output to the selected circuitry for each operation.
    ALU_OPS: dict[OpCode, Callable[[int, int], int]] = {
        OpCode.ADD: lambda x, y: x + y,
        OpCode.SUB: lambda x, y: x - y,
        OpCode.MUL: lambda x, y: x * y,
        OpCode.DIV: lambda x, y: x // y,

        # For memory access operations load, store, the ALU
        # performs the address calculation
        OpCode.LOAD: lambda x, y: x + y,
        OpCode.STORE: lambda x, y: x + y,
        # Some operations perform no operation
        OpCode.HALT: lambda x, y: 0
    }

    def exec(self, op: OpCode, in1: int, in2: int) -> tuple[int, CondFlag]:
        try:
            result = self.ALU_OPS[op](in1, in2)
            flag = CondFlag.Z if result == 0 else CondFlag.M if result < 0 else CondFlag.P
            return(result, flag)
        except:
            return(0, CondFlag.V)


class CPUStep(MVCEvent):
    """CPU is beginning step with PC at a given address"""
    def __init__(self, subject: "CPU", pc_addr: int,
                 instr_word: int, instr: Instruction)-> None:
        self.subject = subject
        self.pc_addr = pc_addr
        self.instr_word = instr_word
        self.instr = instr


class CPU(MVCListenable):
    """Duck Machine central processing unit (CPU)
    has 16 registers (including r0 that always holds zero
    and r15 that holds the program counter), a few
    flag registers (condition codes, halted state),
    and some logic for sequencing execution.  The CPU
    does not contain the main memory but has a bus connecting
    it to a separate memory.
    """

    def __init__(self, memory: Memory):
        super().__init__()
        self.memory = memory  # Not part of CPU; what we really have is a connection
        self.registers: list[Register] = [ ZeroRegister(), Register(), Register(), Register(),
                           Register(), Register(), Register(), Register(),
                           Register(), Register(), Register(), Register(),
                           Register(), Register(), Register(), Register() ]
        self.cpu = self.registers[15]
        self.condition = CondFlag.ALWAYS
        self.halted = False
        self.alu = ALU()

    def step(self):
        """One fetch/decode/execute step"""
        instr_address = self.cpu.get()
        instr_from_memory = self.memory.get(instr_address)
        # Decode
        instr_decoded = decode(instr_from_memory)
        # Display the CPU state when we have decoded the instruction,
        # before we have executed it
        self.notify_all(CPUStep(self, instr_address, instr_from_memory, instr_decoded))
        # Execute 
        if self.condition.value & instr_decoded.cond.value >= 0:
            left = self.registers[instr_decoded.reg_src1].get()
            right = instr_decoded.offset + self.registers[instr_decoded.reg_src2].get()
            # calculate
            result = self.alu.exec(instr_decoded.op, left, right)
            # increment reg 15
            self.cpu.put(self.cpu.get() + 1)
            # execute operation
            if instr_decoded.op == OpCode.STORE:
                self.memory.put(result[0], self.registers[instr_decoded.reg_target].get())
            elif instr_decoded.op == OpCode.LOAD:
                self.registers[instr_decoded.reg_target].put(self.memory.get(result[0]))
            elif instr_decoded.op == OpCode.HALT:
                self.halted = True
            elif instr_decoded.op == OpCode.ADD or OpCode.SUB or OpCode.MUL or OpCode.DIV:
                self.registers[instr_decoded.reg_target].put(result[0])
                self.condition = instr_decoded.op
        else:
            # increment reg 15
            self.cpu.put(self.cpu.get() + 1)
    
    def run(self, from_addr: int = 0, single_step: bool = False) -> None:
        """Step the CPU until it executes a HALT"""
        self.halted = False
        self.cpu.put(from_addr)
        step_count = 0
        while not self.halted:
            if single_step:
                input(f"Step {step_count}; press enter")
            self.step()
            step_count += 1


