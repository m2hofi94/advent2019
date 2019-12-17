from collections import deque

class VM:
    def __init__(self, program, inp=[]):
        self.iter = None
        if type(program) == str:
            self.codes = [int(i) for i in program.split(',')]
        else:
            self.codes = program
        self.inp = deque(inp)
        self.provided = False
        self.base = 0
        self.pos = 0
        self.ops = {
            1: self._add,
            2: self._multiply,
            #3: self._inpt,
            #4: self._outpt,
            5: self._jump_if_true,
            6: self._jump_if_false,
            7: self._less_than,
            8: self._equals,
            9: self._adjust_base,
            99: self._halt
        }
        
    def copy(self):
        vm = VM(self.codes, self.inp.copy())
        vm.provided = self.provided
        vm.base = self.base
        vm.pos = self.pos
        return vm
        
    def run(self):
        if self.iter is None:
            self.iter = self._run()
        return next(self.iter)
    
    def _run(self):
        while self.pos < len(self.codes):
            opcode = self.codes[self.pos] % 100

            if opcode == 4:
                self.pos, out = self._outpt()
                yield out
            elif opcode == 3:
                self.pos = self._inpt()
            else:
                self.pos = self.ops[opcode]()
                
    def add_input(self, *args):
        self.inp.extend(args)
        self.provided = False
        return self
    
    def provide_input(self, inp):
        self.inp = deque([inp]*3)
        self.provided = True
                
    def _get_params(self, num):
        res = []
        modes = list(str(self.codes[self.pos])[:-2])
        for arg in self.codes[self.pos+1:self.pos+num+1]:
            if len(modes) > 0:
                m = int(modes.pop())
            else:
                m = 0
            if m == 0:
                res.append(self._r(arg))
            elif m == 1:
                res.append(arg)
            elif m == 2:
                res.append(self._r(self.base + arg))
        return res if len(res) > 1 else res[0]

    def _get_out_pos(self, pos, offset):
        modes = list(str(self.codes[pos])[:-2])
        if len(modes) >= offset and modes[0] == "2":
            return self.base + self._r(pos+offset)
        return self.codes[pos + offset]
    
    def _expand(self, pos):
        if pos >= len(self.codes):
            self.codes.extend([0]*(pos-len(self.codes) + 1))

    def _r(self, pos):
        self._expand(pos)
        return self.codes[pos]

    def _w(self, pos, offset, val):
        write_pos = self._get_out_pos(pos, offset)
        self._expand(write_pos)
        self.codes[write_pos] = val
        
    def _outpt(self):
        a = self._get_params(1)
        return self.pos + 2, a
    
    def _inpt(self):
        self._w(self.pos, 1, self.inp.popleft())
        if self.provided:
            self.inp.append(self.inp[0])
        return self.pos + 2
    
    def _add(self):
        a,b = self._get_params(2)
        self._w(self.pos, 3, a + b)
        return self.pos + 4
    
    def _multiply(self):
        a,b = self._get_params(2)
        self._w(self.pos, 3, a * b)
        return self.pos + 4
    
    def _halt(self):
        return float("inf")

    def _jump_if_true(self):
        a,b = self._get_params(2)
        if a != 0:
            return b
        return self.pos+3

    def _jump_if_false(self):
        a,b = self._get_params(2)
        if a == 0:
            return b
        return self.pos+3

    def _less_than(self):
        a,b = self._get_params(2)
        self._w(self.pos, 3, int(a < b))
        return self.pos+4

    def _equals(self):
        a,b = self._get_params(2)
        self._w(self.pos, 3, int(a==b))
        return self.pos+4

    def _adjust_base(self):
        a = self._get_params(1)
        self.base += a
        return self.pos + 2
