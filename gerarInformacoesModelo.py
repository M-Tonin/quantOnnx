import sys, os, re, struct

def copyFileContent(fin,fout):
    with open(fin) as f:
        for line in f:
            fout.write(line)


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

def main():
    # Arquivos .txt no path
    print('sys.argv[0] =', sys.argv[0])             
    pathname = os.path.dirname(sys.argv[0])        
    raiz = os.path.abspath(pathname)
    print('full path =', raiz)
    raiz = raiz.replace("\\" ,"/")        
    path = raiz+"/onnxs"
    pathAux = raiz + "/auxiliares"
    print('path =', path)
    initial_py =  pathAux + "/parteInicial.py"
    end_py = pathAux + "/parteFinal.py"
    text_files = [fileX for fileX in os.listdir(path) if fileX.endswith('.proto')]
    print(text_files)
    for base_name in text_files:
        initi = False
        dims_bool = False
        data_b = False
        dim = 1
        fst_float = []
        dim_l = []
        # Criacao do arquivo bat para gravacao do fw
        #  com as novas chaves do arquivo de chaves
        base_file = open(path+'/'+base_name, "r")
        new_file_name = path+ "/info/" + base_name[:-4] + "_float_data.csv"
        new_info_file = path+'/info/' + base_name[:-4] + "_info.txt"
        raw_data_info = path+'/info/' + base_name[:-4] + "_strings"
        raw_data_info = raw_data_info.replace(".", "")
        raw_data_info += ".py"
        print("Hekki - ", raw_data_info)
        raw_info = open(raw_data_info, "w+")
        copyFileContent(initial_py,raw_info)
        new_file = open(new_file_name, "w+")
        file_info = open(new_info_file, "w+")
        

        raw_info.write("lista_raw = [] \n")
                # Nome do arquivo de configuracao
        print("+ Config file " + base_name + "float file -" + new_file_name) 
        # Leitura do arquivo base linha a linha
        lines = base_file.readlines()

        for line in lines:
            # Filtragem das linhas que possuem as chaves
            #if line.startswith("float_data:"):
            if re.match("\s{0,100}float_data:",line):
                split_line = line.split(":")
                float_type = split_line[1]
                float_type = re.sub(r'\n', '', float_type)
                float_type = re.sub(r'\r', '', float_type)
                if(initi and data_b and dims_bool ):
                    dim_l.append(dim)
                    fst_float.append((float)(float_type))
                    initi = False
                    data_b = False
                    dims_bool = False
                    dim = 1
                # Retirada do antigo checksum das linhas que possuem as chaves
                new_file.write(float_type + "," +"\n")
            if re.match("\s{0,100}raw_data: ",line):
                if(initi and data_b and dims_bool ):
                    print("achei")
                    split_line = line.split("raw_data:")
                    raw_string = split_line[1]
                    raw_info.write("st_aux = \"\" \n")
                    raw_info.write(f"st_aux = {raw_string} \n")
                    raw_info.write("lista_raw.append(st_aux) \n")
                    dim_l.append(dim)
                    initi = False
                    data_b = False
                    dims_bool = False
                    dim = 1

            if re.match("\s{0,100}initializer {",line):
                print("Init")
                initi = True

            if re.match("\s{0,100}dims: ",line):
                split_line = line.split(": ")
                dim_v = (int)(split_line[1])
                dim *= dim_v
                print("dims ", dim)
                dims_bool = True
            
            if re.match("\s{0,100}data_type: ",line):
                split_line = line.split(": ")
                data_type = (int)(split_line[1])
                if (data_type == 1):
                    print("data_va")
                    data_b = True     
            if re.match("\s{0,100}}",line):
                #print("dimensao = 1 novamente")
                dim = 1
        base_file.close()
        new_file.close()
        print(fst_float)
        print(dim_l)
        file_info.write("first_floats: ")
        i = 1
        for inx in fst_float:
            print(inx)
            file_info.write(str(inx))
            if i < len(fst_float):
                 file_info.write(", ")
            i += 1
        file_info.write("\n")
        file_info.write("quantite: ")
        i = 1
        for inx in dim_l:
            print(inx)
            file_info.write(str(inx))
            if i < len(dim_l):
                 file_info.write(", ")
            i +=1
        file_info.write("\n")
        file_info.write(f"Camadas floats: {len(dim_l)}\n")
        file_info.close()
        copyFileContent(end_py,raw_info)


if __name__ == "__main__":
    main()