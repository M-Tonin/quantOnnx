import struct, os, sys

def charToHex(s):
    #check if string is unicode
    if isinstance(s, str):
        return format(ord(s), '02x')
    #check if input is already a byte
    elif isinstance(s, bytes):
        return format(ord(s), '02x')
def FourString_float(single):
    conc = ''
    for x1 in single:
        r_hex = charToHex(x1)
        conc += r_hex

    byt_emsi = bytes.fromhex(conc)
    #print(byt_emsi)
    x = struct.unpack("f", byt_emsi)
    x = x[0]
    #print("X - ", x)
    return x


# Arquivos .txt no path
print('sys.argv[0] =', sys.argv[0])             
pathname = os.path.dirname(sys.argv[0])        
raiz = os.path.abspath(pathname)
raiz = raiz.replace("\\" ,"/")        
print('path =', raiz)

text_files = [fileX for fileX in os.listdir(raiz) if fileX.endswith('proto_strings.py')]
basename = text_files[0][:-23]
new_file_name = raiz + "/" + basename + "_float_data.csv"
print("Novo float:: ", new_file_name)
new_file = open(new_file_name, "w+")

