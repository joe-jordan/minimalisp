import re

class sexpr(list):
    def __init__(self, *args, **kwargs):
        self.quoted = False
        super(sexpr, self).__init__(*args, **kwargs)

    def __repr__(self):
        outer = super(sexpr, self).__repr__()
        if self.quoted:
            return "'" + outer
        return outer

def remove_comments(inp):
    commentless_lines = []
    
    # kill comment characters ; onwards, when not inside a string.
    for l in inp.split("\n"):
        splits = l.split(';')
        if len(splits) == 1:
            commentless_lines.append(l)
            continue
        
        previous_string = splits.pop(0)
        
        while len(re.findall(r'(?<!\\)"', previous_string)) % 2 != 0:
            previous_string += ';' + splits.pop()
        
        commentless_lines.append(previous_string)
    return "\n".join(commentless_lines)


def clever_split(inp):
    commentless_inp = remove_comments(inp)
    
    # rather than splitting on all whitespace, we want to split only on 
    # whitespace not inside a string.
    # strings cannot contain newlines, so start by splitting on those:
    lines = commentless_inp.split("\n")
    tokens = []
    for i, l in enumerate(lines):
        splits = [s for s in l.split('"')]

        # if there were no "s in this line, split the whole thing by whitespace:
        if len(splits) == 1:
            tokens.extend(l.split())
            continue
        
        # first " can't be escaped.
        tokens.extend(splits.pop(0).split())

        while splits:
            this_string = splits.pop(0)
            # while the quotes are escaped:
            while this_string[-1] == "\\":
                assert len(splits) > 0, "string on line %d is not terminated correctly." % i
                this_string = this_string[:-1] + '"' + splits.pop(0)
            # we've got to the end of this string, add it as its own token:
            tokens.append('"' + this_string + '"')

            # the next tokens are not strings, so just extend them (if any):
            if splits:
                tokens.extend(splits.pop(0).split())

    return tokens

    

def parse(inp):
    toks = clever_split(inp)
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



