"""Deadcode Elimination"""
import json
import sys
from cfg import form_blocks


def is_same_instrs(instrs_1, instrs_2):
    return len(instrs_1) == len(instrs_2) and all(
        x == y for x, y in zip(instrs_1, instrs_2)
    )


def remove_unused_vars(func_instrs):
    """Delete any variable assignment instr which is not used by other instrs"""

    def optimization_step(func_instrs):
        unsed_vars = set()

        # get all the variable declarations
        for instr in func_instrs:
            try:
                unsed_vars.add(instr["dest"])
            except KeyError:
                pass

        # remove used variables
        for instr in func_instrs:
            try:
                unsed_vars -= set(instr["args"])
            except KeyError:
                pass

        # now delete all the instructions which have their dest in this
        func_instrs = [
            instr for instr in func_instrs if instr.get("dest") not in unsed_vars
        ]
        return func_instrs

    # return optimization_step(block)
    while True:
        optimized = optimization_step(func_instrs)
        if optimized == func_instrs:
            return optimized
        else:
            # redo the optimization
            func_instrs = optimized


def remove_unused_reassigned_vars(block):
    """Remove assignments that are overwritten before use.
    Local optimization.
    """
    # {var: instr} for all vars that are unused until now
    last_def = {}
    instrs_to_remove = []
    for instr in block:
        # remove used vars
        try:
            for arg in instr["args"]:
                last_def.pop(arg, None)
        except KeyError:
            pass

        try:
            # remove previous instruction, if dest is unused before
            if instr["dest"] in last_def:
                instrs_to_remove.append(last_def[instr["dest"]])

            # book keeping for current instr
            last_def[instr["dest"]] = instr
        except KeyError:
            pass

    block = [x for x in block if x not in instrs_to_remove]
    return block


def flatten_named_blocks(named_blocks):
    instrs = []
    for block_name, block in named_blocks.items():
        instrs.append({"label": block_name})
        instrs.extend(block)

    return instrs


def run_tdce():
    prog = json.load(sys.stdin)
    for func in prog["functions"]:
        # global optimization on tdce
        func["instrs"] = remove_unused_vars(func["instrs"])

        optimized = []
        # local optimization
        for block in form_blocks(func["instrs"]):
            optimized.extend(remove_unused_reassigned_vars(block))

        func["instrs"] = optimized

    print(json.dumps(prog))


if __name__ == "__main__":
    run_tdce()
