import context
from cpu.cpu import *
import unittest

class TestALU(unittest.TestCase):
    """Simple smoke test of each ALU op"""

    def test_each_op(self):
        alu = ALU()
        # The main computational ops
        # Addition  (Overflow is not modeled)
        self.assertEqual(alu.exec(OpCode.ADD, 5, 3), (8, CondFlag.P))
        self.assertEqual(alu.exec(OpCode.ADD, -5, 3), (-2, CondFlag.M))
        self.assertEqual(alu.exec(OpCode.ADD, -10, 10), (0, CondFlag.Z))
        # Subtraction (Overflow is not modeled)
        self.assertEqual(alu.exec(OpCode.SUB, 5, 3), (2, CondFlag.P))
        self.assertEqual(alu.exec(OpCode.SUB, 3, 5), (-2, CondFlag.M))
        self.assertEqual(alu.exec(OpCode.SUB, 3, 3), (0, CondFlag.Z))
        # Multiplication (Overflow is not modeled)
        self.assertEqual(alu.exec(OpCode.MUL, 3, 5), (15, CondFlag.P))
        self.assertEqual(alu.exec(OpCode.MUL, -3, 5), (-15, CondFlag.M))
        self.assertEqual(alu.exec(OpCode.MUL, 0, 22), (0, CondFlag.Z))
        # Division (can overflow with division by zero
        self.assertEqual(alu.exec(OpCode.DIV, 5, 3), (1, CondFlag.P))
        self.assertEqual(alu.exec(OpCode.DIV, 12, -3), (-4, CondFlag.M))
        self.assertEqual(alu.exec(OpCode.DIV, 3, 4), (0, CondFlag.Z))
        self.assertEqual(alu.exec(OpCode.DIV, 12, 0), (0, CondFlag.V))
        #
        # For other ops, we just want to make sure they have table
        # entries and perform the right operation. Condition code is returned but not used
        self.assertEqual(alu.exec(OpCode.LOAD, 12, 13), (25, CondFlag.P))
        self.assertEqual(alu.exec(OpCode.STORE, 27, 13), (40, CondFlag.P))
        self.assertEqual(alu.exec(OpCode.HALT, 99, 98), (0, CondFlag.Z))

class TestALUExtended(unittest.TestCase):
    def setUp(self):
        self.alu = ALU()

    def test_add_extremes(self):
        self.assertEqual(self.alu.exec(OpCode.ADD, 2**31 - 1, 1)[1], CondFlag.P)
        self.assertEqual(self.alu.exec(OpCode.ADD, -2**31, -1)[1], CondFlag.M)

    def test_sub_negative_result(self):
        self.assertEqual(self.alu.exec(OpCode.SUB, 3, 7), (-4, CondFlag.M))

    def test_mul_zero_handling(self):
        self.assertEqual(self.alu.exec(OpCode.MUL, 1234, 0), (0, CondFlag.Z))

    def test_div_zero_handling(self):
        """Division by zero should set overflow condition"""
        result, flag = self.alu.exec(OpCode.DIV, 10, 0)
        self.assertEqual(flag, CondFlag.V)
        self.assertEqual(result, 0)

    def test_store_and_load_behaviors(self):
        """ALU treats LOAD/STORE as addition for address computation"""
        res, flag = self.alu.exec(OpCode.LOAD, 100, 50)
        self.assertEqual((res, flag), (150, CondFlag.P))

    def test_halt_returns_zero(self):
        """HALT should return zero result and Z flag"""
        res, flag = self.alu.exec(OpCode.HALT, 5, 9)
        self.assertEqual((res, flag), (0, CondFlag.Z))
        
if __name__ == "__main__":
    unittest.main()