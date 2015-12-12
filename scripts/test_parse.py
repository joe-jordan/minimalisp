from parse import parse_program

if __name__ == "__main__":
    import sys
    fn = sys.argv[1]
    inp = open(fn, 'r').read()
    print repr(parse_program(inp))
