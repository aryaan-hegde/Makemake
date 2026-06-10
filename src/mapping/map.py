from frontend.ast import Assignment, BinaryOp, UnaryOp, Inputs, Outputs
from .lut import Lut

class Mapper:
    def __init__(self, trees, K):
        self.trees = trees
        self.K = K
        self.circuit = {}
        self.counter = 0

    def map_trees(self):
        for tree in self.trees:
            self.traverse(tree)
        return self.circuit

    def traverse(self, node):
        if isinstance(node, BinaryOp):
            self.traverse(node.left)
            self.traverse(node.right)
            self.circuit[id(node)] = self.map_node(node)

        elif isinstance(node, UnaryOp):
            self.traverse(node.operand)
            self.circuit[id(node)] = self.map_node(node)

        else:
            lut = Lut(node.value, 1, [node], [0, 1])
            lut.packed_luts = [lut]
            self.circuit[id(node)] = [lut]

    def map_node(self, node):
        fanin_nodes = self.get_fanin(node)
        fanin_luts = []
        for f in fanin_nodes:
            fanin_luts += self.circuit[id(f)]
        decompose_tree = self.decompose_node(node, fanin_luts)
        return decompose_tree

    def get_fanin(self, node):
        if isinstance(node, BinaryOp):
            return [node.left, node.right]
        elif isinstance(node, UnaryOp):
            return [node.operand]
        return []

    # def compute_pack_truth_table(self, node, inputs):
    #     tt = []
    #     for i in range(2 ** len(inputs)):
    #         inputs_case = []
    #         for j in range(len(inputs)):
    #             inputs_case.append((i >> (len(inputs) - 1 - j)) & 1)
    #         if isinstance(node, BinaryOp):
    #             tt.append(self.eval_bin_case(inputs_case, node.op.value))
    #         elif isinstance(node, UnaryOp):
    #             if node.op.value == '~':
    #                 tt.append(1 - inputs_case[0])
    #             else:
    #                 raise ValueError(f"Unsupported operation: {node.op.value}")
    #     return tt

    def eval_node(self, node, vals):
        if isinstance(node, BinaryOp):
            left  = self.eval_node(node.left, vals)
            right = self.eval_node(node.right, vals)
            if node.op.value == '+': return left | right
            if node.op.value == '*': return left & right
            if node.op.value == '^': return left ^ right
        elif isinstance(node, UnaryOp):
            operand = self.eval_node(node.operand, vals)
            if node.op.value == '~': return 1 - operand
        else:
            return vals.get(node.value, 0)

    # def compute_pack_truth_table(self, node, inputs):
    #     print("Entered packing")
    #     print(inputs)
    #     tt = []
    #     for i in range(2 ** len(inputs)):
    #         vals = {
    #             inputs[j].value: (i >> (len(inputs) - 1 - j)) & 1
    #             for j in range(len(inputs))
    #         }
    #         tt.append(self.eval_node(node, vals))
    #     return tt

    def compute_pack_truth_table(self, node, inputs, packed_luts):
        n = len(inputs)
        tt = []
        
        for i in range(2 ** n):
            # assign bits to each primary input
            primary_vals = {
                inputs[j].value: (i >> (n - 1 - j)) & 1
                for j in range(n)
            }
            
            # evaluate each packed LUT by indexing into its truth table
            lut_outputs = []
            for lut in packed_luts:
                # build the index into this lut's truth table
                idx = 0
                for inp in lut.inputs:
                    idx = (idx << 1) | primary_vals[inp.value]
                lut_outputs.append(lut.truth_table[idx])
            
            # apply node's operation across all lut outputs
            tt.append(self.eval_bin_case(lut_outputs, node.op.value))
        
        return tt

    def eval_bin_case(self, input_case, op):
        result = input_case[0]
        for bit in input_case[1:]:
            if op == '+':
                result |= bit
            elif op == '*':
                result &= bit
            elif op == '^':
                result ^= bit
            else:
                raise ValueError(f"Unsupported operation: {op}")
        
        return result

    def recompute_truth_table(self, prev_tt, op, node, inputs):
        if len(prev_tt) == 0:
            tt = []
            for i in range(2 ** len(inputs)):
                inputs_case = []
                for j in range(len(inputs)):
                    inputs_case.append((i >> (len(inputs) - 1 - j)) & 1)
                if isinstance(node, BinaryOp):
                    tt.append(self.eval_bin_case(inputs_case, node.op.value))
                elif isinstance(node, UnaryOp):
                    if node.op.value == '~':
                        tt.append(1 - inputs_case[0])
                    else:
                        raise ValueError(f"Unsupported operation: {node.op.value}")
            
            return tt

        # extended_tt = prev_tt * 2
        # zeroes = [0] * len(prev_tt)
        # ones = [1] * len(prev_tt)
        # new_col = []
        # new_col += zeroes + ones
        # new_tt = []
        # for entry_idx in range(len(new_col)):
        #     input_case = []
        #     input_case.append(new_col[entry_idx])
        #     input_case.append(extended_tt[entry_idx])
        
        #     new_tt.append(self.eval_bin_case(input_case, op))
        
        # return new_tt

        extended_tt = prev_tt * 2    # new input=0: first half, new input=1: second half
        new_tt = []
        for entry_idx in range(len(extended_tt)):
            new_input = entry_idx // len(prev_tt)  # 0 for first half, 1 for second
            prev_output = extended_tt[entry_idx]
            new_tt.append(self.eval_bin_case([prev_output, new_input], op))
        return new_tt

    def first_fit_decreasing(self, node, fanin_luts):
        box_list = sorted(fanin_luts, key=lambda lut: lut.size, reverse=False)
        bin_list = []
        while len(box_list) != 0:
            largest_box = box_list.pop()
            found_idx = -1
            for idx in range(len(bin_list)):
                if bin_list[idx].size + largest_box.size <= self.K:
                    found_idx = idx
                    break
            
            if found_idx == -1:
                new_bin = Lut(str(self.counter), 0, [], [], [])
                bin_list.append(new_bin)
                self.counter += 1
                found_idx = len(bin_list) - 1
            
            bin_list[found_idx].size += largest_box.size
            bin_list[found_idx].packed_luts.append(largest_box)
            bin_list[found_idx].inputs += largest_box.inputs
        for bin_ in bin_list:
            if len(bin_.packed_luts) == 1:
                original_lut = bin_.packed_luts[0]
                if isinstance(node, UnaryOp) and node.op.value == '~':
                    bin_.truth_table = [1 - b for b in original_lut.truth_table]
                else:
                    bin_.truth_table = original_lut.truth_table.copy()
            else:
                bin_.truth_table = self.compute_pack_truth_table(node, bin_.inputs, bin_.packed_luts)
        return bin_list

    def decompose_node(self, node, fanin_luts):
        packed_luts = self.first_fit_decreasing(node, fanin_luts)
        look_list = sorted(packed_luts, key=lambda lut: lut.size, reverse=False)
        while len(look_list) > 1:
            look_list = sorted(look_list, key=lambda lut: lut.size, reverse=False)
            source = look_list.pop()
            found_idx = -1
            for idx in range(len(look_list)):
                if look_list[idx].size + 1 <= self.K:
                    found_idx = idx
                    break
            if found_idx == -1:
                empty_lut = Lut(str(self.counter), 0, [], [])
                look_list.append(empty_lut)
                self.counter += 1
                found_idx = len(look_list) - 1

            look_list[found_idx].size += 1
            look_list[found_idx].inputs.append(source)
            prev_tt = look_list[found_idx].truth_table
            look_list[found_idx].truth_table = self.recompute_truth_table(prev_tt, node.op.value, node, look_list[found_idx].inputs)
        return look_list

    def print_lut(self, lut):
        print(f"var:         {lut.value}")
        print(f"size:        {lut.size}")
        print(f"truth_table: {lut.truth_table}")
        print(f"inputs:      {[i.value for i in lut.inputs]}")
        print(f"packed_luts: {[l.value for l in lut.packed_luts]}")

    def print_circuit(self, lut, visited=None):
        if visited is None:
            visited = set()
        
        if lut.value in visited:
            return
        visited.add(lut.value)
        
        self.print_lut(lut)
        print()
        
        for inp in lut.inputs:
            if isinstance(inp, Lut):
                self.print_circuit(inp, visited)