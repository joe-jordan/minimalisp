class sexpr(list):
    def __init__(self, *args, **kwargs):
        self.quoted = False
        super(sexpr, self).__init__(*args, **kwargs)

    def __repr__(self):
        outer = super(sexpr, self).__repr__()
        if self.quoted:
            return "'" + outer
        return outer

def parse(inp):
    toks = inp.split()
    parents = {}
    output_list = sexpr()
    current_list = output_list
    while True:
        try:
            tok = toks.pop(0)
        except IndexError:
            break
        while tok and tok[0] in "'(" and (tok[0] == '(' or tok[:2] == "'("):
            current_list.append(sexpr())
            parents[id(current_list[-1])] = current_list
            current_list = current_list[-1]
            if tok[0] == '(':
                tok = tok[1:]
            else:
                tok = tok[2:]
                current_list.quoted = True
                
        end_here = 0
        while tok and tok[-1] == ')':
            end_here += 1
            tok = tok[:-1]
        if tok:
            current_list.append(tok)
        while end_here:
            end_here -= 1
            current_list = parents[id(current_list)]
    assert id(current_list) == id(output_list), "s expressions not closed"
    return output_list



