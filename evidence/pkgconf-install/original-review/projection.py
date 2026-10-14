import struct

def project_macho(original):
    data=bytearray(original)
    u32=lambda buf,off: int.from_bytes(buf[off:off+4],"little")
    assert u32(data,0)==0xfeedfacf
    count,size=u32(data,16),u32(data,20)
    off=32;first=len(data);commands=[];changed=0
    replacements=[(b"@@HOMEBREW_PREFIX@@",b"/opt/homebrew"),(b"@@HOMEBREW_CELLAR@@",b"/opt/homebrew/Cellar")]
    for _ in range(count):
        cmd,cs=u32(data,off),u32(data,off+4);assert cs>=8 and off+cs<=32+size
        part=bytearray(data[off:off+cs])
        if cmd==0x19:
            for i in range(u32(part,64)):
                sec=72+i*80;assert sec+80<=cs
                f=u32(part,sec+48)
                if f:first=min(first,f)
        if cmd in {0xc,0xd,0x80000018,0x8000001f,0x20,0x80000023,0x8000001c}:
            start=u32(part,8);stop=part.find(0,start)
            assert 0<=start<cs and stop>=start
            old=bytes(part[start:stop]);new=old
            for a,b in replacements:new=new.replace(a,b)
            if old!=new:
                end=max(cs,((start+len(new)+1+7)//8)*8)
                rebuilt=part[:start]+new+bytes(end-start-len(new));rebuilt[4:8]=end.to_bytes(4,"little");part=rebuilt;changed+=1
        commands.append(part);off+=cs
    assert off==32+size and sum(map(len,commands))==size and changed==1
    data[32:first]=bytes(first-32);data[32:32+size]=b"".join(commands)
    for a,b in replacements:assert a not in data
    assert len(data)==len(original)
    return data
