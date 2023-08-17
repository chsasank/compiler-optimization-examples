"""Deadcode Elimination"""
import json
import sys
from cfg import form_blocks, name_blocks


def is_same_instrs(instrs_1, instrs_2):
    return len(instrs_1) == len(instrs_2) and all(
        x == y for x, y in zip(instrs_1, instrs_2)
    )


def remove_unused_vars(block):
    """Delete any variable assignment instr which is not used by other instrs"""

    def optimization_step(block):
        unsed_vars = set()

        # get all the variable declarations
        for instr in block:
            try:
                unsed_vars.add(instr["dest"])
            except KeyError:
                pass

        # remove used variables
        for instr in block:
            try:
                unsed_vars -= set(instr["args"])
            except KeyError:
                pass

        # now delete all the instructions which have their dest in this
        block = [instr for instr in block if instr.get("dest") not in unsed_vars]
        return block

    # return optimization_step(block)
    while True:
        optimized = optimization_step(block)
        if optimized == block:
            return optimized
        else:
            # redo the optimization
            block = optimized


def flatten_named_blocks(named_blocks):
    instrs = []
    for block_name, block in named_blocks.items():
        instrs.append({"label": block_name})
        instrs.extend(block)

    return instrs


def run_tdce():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        blocks = form_blocks(func["instrs"])
        named_blocks = name_blocks(blocks)
        for block_name, block in named_blocks.items():
            named_blocks[block_name] = remove_unused_vars(block)

        func["instrs"] = flatten_named_blocks(named_blocks)

    print(json.dumps(prog))


if __name__ == "__main__":
    run_tdce()
