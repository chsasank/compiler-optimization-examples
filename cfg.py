import json
import sys
from collections import OrderedDict

TERMINATORS = {"jmp", "br", "ret"}

def form_blocks(body):
    """Block formation algorthm. 
    
    Ref: https://en.wikipedia.org/wiki/Basic_block
    """
    blocks = []
    current_block = []
    for instr in body:
        if "label" in instr:
            # label, new block
            if current_block:
                blocks.append(current_block)
            current_block = [instr]
        elif instr["op"] in TERMINATORS:
            # terminator, end block
            current_block.append(instr)
            blocks.append(current_block)
            current_block = []
        else:
            # just add to current block
            current_block.append(instr)

    if current_block:
        blocks.append(current_block)
    return blocks


def block_map(blocks):
    """Crate names for blocks"""
    out = OrderedDict()
    for idx, block in enumerate(blocks):
        first_instr = block[0]
        if 'label' in first_instr:
            name = first_instr['label']
            block = block[1:]
        else:
            name = f'b{len(out)}'

        out[name] = block

    return out


def get_cfg(named_blocks):
    successors = {}
    block_names = list(named_blocks.keys())
    for idx, (name, block) in enumerate(named_blocks.items()):
        last_instr = block[-1]
        if last_instr['op'] in {'jmp', 'br'}:
            successors[name] = last_instr['labels']
        elif last_instr['op'] == 'ret':
            # just the next block
            successors[name] = []
        else:
            try:
                successors[name] = [block_names[idx + 1]]
            except IndexError:
                # last block
                successors[name] = []

    return successors


def graphviz(cfg, func_name):
    print(f"digraph {func_name} {{")
    for name in cfg.keys():
        print(f'  {name};')

    for name, successors in cfg.items():
        for succ in successors:
            print(f'  {name} -> {succ}')
    print('}')


def mycfg():
    prog = json.load(sys.stdin)
    cfg = {}
    for func in prog["functions"]:
        blocks = form_blocks(func["instrs"])
        named_blocks = block_map(blocks)
        cfg = get_cfg(named_blocks)

        graphviz(cfg, func['name'])
        
        

if __name__ == "__main__":
    mycfg()
