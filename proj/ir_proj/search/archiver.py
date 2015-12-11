VARBYTE = 1
SIMPLE9 = 2
import base64


def to_flat(element):
    res = []
    res.append(len(element))
    for v in sorted(element.keys()):
        res.append(v)
        res.append(element[v][0])
        res.append(len(element[v][1]))
        for x in element[v][1]:
            res.append(x)
    return res

def from_flat(element):
    res = [None] * element[0]
    res_d = {}
    cp = 1
    for i in xrange(element[0]):
        res[i] = element[cp]
        t = element[cp]
        cp += 1
        res_d[t] = (element[cp], [])
        cp += 1
        x = element[cp]
        cp += 1
        for j in xrange(x):
            res_d[t][1].append(element[cp])
            cp += 1
    return res, res_d

def encode_one_varbyte(n):
    res = str()
    res += chr((n % 128) | (1 << 7))
    n /= 128
    while n:
        res += chr(n % 128)
        n /= 128
    return res[::-1]

def encode_varbyte(values):
    values_comp = str()
    for i in values:
        values_comp += encode_one_varbyte(i)
    return values_comp

def binlen(x):
    i = 1
    p = 1 << i
    while p <= x:
        i += 1
        p <<= 1
    return i

def chunk2bytes(x):
    l = 4
    a = [0] * l
    for i in xrange(l):
        a[l - i - 1] = x % (1 << 8)
        x /= (1 << 8)
    return ''.join(map(chr, a))

def encode_simple9(values):
    schema = [[28, 1], [14, 2], [9, 3], [7, 4], [5, 5], [4, 7], [3, 9], [2, 14], [1, 28]]
    values_comp = bytes()
    sz = [0] * len(values)
    for i in xrange(len(values)):
        sz[i] = binlen(values[i])
        if sz[i] > 28:
            print "Number is too large!"
            exit(1)

    i = 0
    while i < len(values):
        #choose schema
        s = -1
        good = False
        while not good:
            s += 1
            if i + schema[s][0] > len(values):
                continue
            good = True
            for j in xrange(i, min(i + schema[s][0], len(values))):
                if sz[j] > schema[s][1]:
                    good = False
                    break
        chunk = 0
        chunk |= s << 28
        for j in xrange(i, min(i + schema[s][0], len(values))):
            chunk |= values[j] << (28 - schema[s][1] * (j - i + 1))
        values_comp += chunk2bytes(chunk)
        i += schema[s][0]
    return values_comp

def decode_simple9(code):
    schema = [[28, 1], [14, 2], [9, 3], [7, 4], [5, 5], [4, 7], [3, 9], [2, 14], [1, 28]]
    res = []
    ind = 0
    while ind < len(code):
        dat = 0
        for j in xrange(4):
            dat = dat * (1 << 8) + ord(code[ind + j])
        ind += 4
        s = (dat & (((1 << 4) - 1) << (32 - 4))) >> (32 - 4)
        for j in xrange(schema[s][0]):
            shift = 28 - (j + 1) * schema[s][1]
            res.append((dat & (((1 << schema[s][1]) - 1) << shift)) >> shift)
    return res

def decode_varbyte(code):
    res = []
    cur_res = 0
    for byte in code:
        if ord(byte) & (1 << 7):
            res.append(cur_res * 128 + (ord(byte) ^ (1 << 7)))
            cur_res = 0
        else:
            cur_res = cur_res * 128 + (ord(byte) & ((1 << 7) - 1))
    return res
    
def join(a, b):
    res = []
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        while i < len(a) and j < len(b) and a[i] < b[j]:
            res.append(a[i])
            i += 1
        while i < len(a) and j < len(b) and a[i] > b[j]:
            res.append(b[j])
            j += 1
        if i < len(a) and j < len(b) and a[i] == b[j]:
            res.append(b[j])
            i += 1
            j += 1
    while i < len(a):
        res.append(a[i])
        i += 1
    while j < len(b):
        res.append(b[j])
        j += 1
    return res