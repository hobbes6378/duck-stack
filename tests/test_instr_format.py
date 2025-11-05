"""Test cases for the binary encoding of 
instructions. 
"""

import context
from instruction_set.instr_format import *
import unittest

class TestCondCodes(unittest.TestCase):
    """Condition flags are essentially like single bit bitfields"""

    def test_combine_flags(self):
        non_zero = CondFlag.P | CondFlag.M
        self.assertEqual(str(non_zero), "MP")
        positive = CondFlag.P
        self.assertEqual(str(positive), "P")
        self.assertEqual(str(CondFlag.ALWAYS), "ALWAYS")
        self.assertEqual(str(CondFlag.NEVER), "NEVER")
        # We test overlap of two CondFlag values using bitwise AND
        self.assertTrue(positive & non_zero)
        zero = CondFlag.Z
        self.assertFalse(zero & non_zero)

class TestInstructionString(unittest.TestCase):
    """Check that we can print Instruction objects like assembly language"""

    def test_str_predicated_MUL(self):
        instr = Instruction(OpCode.MUL, CondFlag.P | CondFlag.Z,
                        NAMED_REGS["r1"], NAMED_REGS["r3"], NAMED_REGS["pc"], 42)
        self.assertEqual("MUL/ZP   r1,r3,r15[42]", str(instr))

    def test_str_always_ADD(self):
        """Predication is not printed for the common value of ALWAYS"""
        instr = Instruction(OpCode.ADD, CondFlag.ALWAYS,
                            NAMED_REGS["zero"], NAMED_REGS["pc"], NAMED_REGS["r15"], 0)
        self.assertEqual("ADD   r0,r15,r15[0]", str(instr))
    
class TestDecode(unittest.TestCase):
    """Encoding and decoding should be inverses"""
    def test_encode_decode(self):
        instr = Instruction(OpCode.SUB, CondFlag.M | CondFlag.Z, NAMED_REGS["r2"], NAMED_REGS["r1"], NAMED_REGS["r3"], -12)
        word = instr.encode()
        text = str(decode(word))
        self.assertEqual(text, str(instr))
        

class TestCondFlagExtras(unittest.TestCase):
    def test_combined_flag_logic(self):
        """Check multiple bit combinations"""
        combo = CondFlag.M | CondFlag.V
        self.assertTrue(combo & CondFlag.M)
        self.assertTrue(combo & CondFlag.V)
        self.assertFalse(combo & CondFlag.Z)
        self.assertEqual(str(combo), "MV")

class TestInstructionEncodeDecode(unittest.TestCase):
    def test_encode_decode_negative_offset(self):
        """Encoding and decoding with negative offset works"""
        instr = Instruction(OpCode.ADD, CondFlag.ALWAYS, 2, 4, 8, -5)
        word = instr.encode()
        decoded = decode(word)
        self.assertEqual(decoded.offset, -5)

    def test_encode_decode_large_offset(self):
        """Encoding and decoding with large positive offset"""
        instr = Instruction(OpCode.MUL, CondFlag.ALWAYS, 1, 2, 3, 511)
        word = instr.encode()
        decoded = decode(word)
        self.assertEqual(decoded.offset, 511)

    def test_named_register_mappings(self):
        """Named register aliases should map correctly"""
        self.assertEqual(NAMED_REGS["pc"], 15)
        self.assertEqual(NAMED_REGS["zero"], 0)
        self.assertEqual(NAMED_REGS["r10"], 10)

    def test_str_representation_complex(self):
        """Verify string formatting of predicated instruction"""
        instr = Instruction(OpCode.DIV, CondFlag.M | CondFlag.V, 10, 8, 9, 7)
        self.assertEqual(str(instr), "DIV/MV   r10,r8,r9[7]")

    def test_encode_decode_inverse_random(self):
        """Multiple round-trip encodings"""
        for op in OpCode:
            instr = Instruction(op, CondFlag.ALWAYS, 5, 6, 7, -15)
            self.assertEqual(str(decode(instr.encode())), str(instr))
            
if __name__ == "__main__":
    unittest.main()
