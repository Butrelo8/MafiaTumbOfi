import json,struct
def load(p):
    d=open(p,'rb').read()
    L=struct.unpack('<I',d[12:16])[0]; j=json.loads(d[20:20+L])
    off=20+L; bl=struct.unpack('<I',d[off:off+4])[0]; b=d[off+8:off+8+bl]
    return j,b
def view(j,b,i):
    bv=j['bufferViews'][i]; o=bv.get('byteOffset',0); return b[o:o+bv['byteLength']]
def save(p,j,views):
    # views: list of bytes per bufferView, in order; rebuild buffer with 4-byte alignment
    out=bytearray()
    for i,v in enumerate(views):
        while len(out)%4: out+=b'\0'
        j['bufferViews'][i]['byteOffset']=len(out); j['bufferViews'][i]['byteLength']=len(v); out+=v
    while len(out)%4: out+=b'\0'
    j['buffers'][0]['byteLength']=len(out)
    js=json.dumps(j,separators=(',',':')).encode()
    js+=b' '*((4-len(js)%4)%4)
    total=12+8+len(js)+8+len(out)
    with open(p,'wb') as f:
        f.write(struct.pack('<4sII',b'glTF',2,total))
        f.write(struct.pack('<I4s',len(js),b'JSON')); f.write(js)
        f.write(struct.pack('<I4s',len(out),b'BIN\0')); f.write(out)
