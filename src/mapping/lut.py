class Lut:
    def __init__(self, value, size, inputs, truth_table, packed_luts=[]):
        self.value = value
        self.size = size
        self.inputs = inputs
        self.packed_luts = packed_luts
        self.truth_table = truth_table
