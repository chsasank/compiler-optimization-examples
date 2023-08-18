"""Local Value Numbering"""
import json
import sys
from cfg import form_blocks


def lvn_pass(block, to_fold=False):
    """Do Local Value Numbering in a given block"""
    # value -> canonical var
    value_table = {}
    # mapping from variables to values
    current_env = {}

    optimized_block = []
    for instr in block:
        op = instr.get("op")
        if "label" in instr:
            # ignore label
            optimized_block.append(instr)
        elif op == "const":
            # symbol for constant
            value = ("const", instr["value"])
            if value not in value_table:
                value_table[value] = instr["dest"]

            current_env[instr["dest"]] = value

            # no transformations on const instructions
            optimized_block.append(instr)
        elif "args" in instr:
            # args need not be present in the current block
            # if so, create symbol for that
            for arg in instr["args"]:
                if arg not in current_env:
                    value = ("var", arg)
                    value_table[value] = arg
                    current_env[arg] = value

            if op in {"add", "mul"}:
                # symbol for add/mul: sorted because add is commutative
                value = (op,) + tuple(sorted(current_env[x] for x in instr["args"]))

                # see if we can do constant folding
                if to_fold and value[1][0] == "const" and value[2][0] == "const":
                    if op == "add":
                        value = ("const", value[1][1] + value[2][1])
                    elif op == "mul":
                        value = ("const", value[1][1] * value[2][1])                    

                if value not in value_table:
                    value_table[value] = instr["dest"]


                if value[0] == 'const':            
                    transformed_instr = {
                        "dest": instr['dest'],
                        "op": "const",
                        "type": "int",
                        "value": value[1]
                    }
                    optimized_block.append(transformed_instr)
                else:
                    # reconstruct the instr
                    transformed_instr = instr.copy()
                    for idx, arg in enumerate(transformed_instr["args"]):
                        if arg in current_env:
                            transformed_instr["args"][idx] = value_table[current_env[arg]]

                    optimized_block.append(transformed_instr)

            else:
                # reconstruct the instr
                transformed_instr = instr.copy()
                for idx, arg in enumerate(transformed_instr["args"]):
                    if arg in current_env:
                        transformed_instr["args"][idx] = value_table[current_env[arg]]

                    optimized_block.append(transformed_instr)

            try:
                current_env[instr["dest"]] = value
            except KeyError:
                pass
        else:
            optimized_block.append(instr)

    return optimized_block


def run_lvn():
    prog = json.load(sys.stdin)
    to_fold = '-f' in sys.argv
    for func in prog["functions"]:
        optimized = []
        # local optimization
        for block in form_blocks(func["instrs"]):
            optimized.extend(lvn_pass(block, to_fold))

        func["instrs"] = optimized

    print(json.dumps(prog))


if __name__ == "__main__":
    run_lvn()
