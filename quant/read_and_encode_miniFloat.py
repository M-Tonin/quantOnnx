from struct import unpack, pack
import numpy as np
import sys, re, binascii, os, math, json
from datetime import datetime

def infos_mini_float( dicionario ):

    infos = { }

    for x in dicionario.keys():
        abs_val = np.max(dicionario[x]['positivo'])
        infos[x] = {}
        infos[x]['max'] =  abs_val
        infos[x]['min'] =  - abs_val
        infos[x]['list_sort'] = np.sort(dicionario[x]['positivo'])
    

    return infos

def find_closest_num(A, target):
    min_diff = float("inf")
    low = 0
    high = len(A) - 1
    closest_num = None

    # Edge cases for empty list of list
    # with only one element:
    if len(A) == 0:
        return None
    if len(A) == 1:
        return A[0]

    while low <= high:
        mid = (low + high)//2

        # Ensure you do not read beyond the bounds
        # of the list.
        if mid+1 < len(A):
            min_diff_right = abs(A[mid + 1] - target)
        if mid > 0:
            min_diff_left = abs(A[mid - 1] - target)

        # Check if the absolute value between left
        # and right elements are smaller than any
        # seen prior.
        if min_diff_left < min_diff:
            min_diff = min_diff_left
            closest_num = A[mid - 1]

        if min_diff_right < min_diff:
            min_diff = min_diff_right
            closest_num = A[mid + 1]

        # Move the mid-point appropriately as is done
        # via binary search.
        if A[mid] < target:
            low = mid + 1
        elif A[mid] > target:
            high = mid - 1
        # If the element itself is the target, the closest
        # number to it is itself. Return the number.
        else:
            return A[mid]
    return closest_num

def find_the_best_value( info , value): 

    if  value > info['max']  :
        return info['max']
    if value < info['min']:
        return info['min']
    
    signal = 1 if value < 0 else 0
    value = np.abs(value)
    retornando = find_closest_num(info['list_sort'],value)
    
    return (-1) ** signal * retornando



def decompose(value): 
    """decomposes a float32 into negative, exponent, and significand"""
    sinal = (value >> 31)
    expoente = ((value & 0x7F800000) >> 23)
    st_exp = format(expoente, '#04x')
    mant = ((value & 0x007FFFFF))
    st_mant = format(mant, '#04x')
    return (sinal, expoente, st_exp, mant, st_mant)

def new_onnx_filename(thepath, only_name, chaves):
    liname = []
    for chave in chaves:
        st = ""
        st = thepath + only_name_file + "_enc_" + str(chave) + "bits.onnx"
        liname.append(st)
    
    return liname

def printLog(*args, **kwargs):
    print(*args, **kwargs)
    with open(loggname,'a') as file2:
        print(*args, **kwargs, file=file2)

def float_litlle_edian_write(float_back,file2write):
    packed = pack('!f', float_back)
    integers = [c for c in packed]
    byte3 = integers[3].to_bytes(1, "big" )
    byte2 = integers[2].to_bytes(1, "big" )
    byte1 = integers[1].to_bytes(1, "big" )
    byte0 = integers[0].to_bytes(1, "big" )
    #printLog(integers)
    #printLog((float_back))
    #printLog((byte3, byte2, byte1, byte0))
    file2write.write(byte3)
    file2write.write(byte2)
    file2write.write(byte1)
    file2write.write(byte0)

def open_onnx_files(list_name):
    open_onnx = []
    for i in range (len(list_name)):
        #printLog(list_name[i])
        open_onnx.append(open(list_name[i], "wb"))
    
    return open_onnx

def close_onnx_files(all_onnx_files):
    for onnx_file in all_onnx_files:
        onnx_file.close()

def write_same_byte(files_o, bytewrite):
    
    for item in (files_o):
        item.write(bytewrite)
        

def encoder(value:np.float32, maxi, mini, files_onnx, infos):
    # Q = 1 / 2 ** N
    #  q = round ((value + 0.6) / Q))
    # xq = q * Q - 0.6
    intervalo = maxi - mini
    list_float_desquant = []
    for floats_mini in infos.keys():
        if(math.isnan(value)):
            printLog("Problema - IsNan Encontrado!")
        
        if(floats_mini == 'float_16'):
            new_float = np.float16(value)
        else:
            new_float = find_the_best_value(infos[floats_mini], value)
        list_float_desquant.append(float(new_float))

    for r in range(len(list_float_desquant)):
        float_litlle_edian_write(list_float_desquant[r],files_onnx[r] )

    float_back = list_float_desquant[0]
    return float_back
  
def parseLine(linha,inteiro):
    linha = re.sub(r"\s+", "", linha)
    IndexList = []
    stringlist = []
    stringlist = linha.split (",")
    for i in range(len(stringlist)):
        if inteiro:
            IndexList.append(int(stringlist[i],0))
        else:
            IndexList.append(float(stringlist[i]))
   
    return IndexList
  
def mount_list(file_name_arg):
    printLog("Montando lista essencial")
    lstart = []
    lstop = []
    lqnt = []
    lflt = []
    onnx_name = "not provide"
    fp = open(file_name_arg,"r")
    contents = fp.readlines()
    for line in contents:
        split_line = line.split(":")
        # Obtencao da lista index_start: 
        if split_line[0] == "index_start":
            lstart = parseLine(split_line[1],True)
        # Obtencao da lista index_final: 
        elif split_line[0] == "index_final":
            lstop = parseLine(split_line[1],True)
                    # Obtencao da lista quantite: 
        elif split_line[0] == "first_floats":
            lflt = parseLine(split_line[1],False)
        # Obtencao da lista quantite: 
        elif split_line[0] == "quantite":
            lqnt = parseLine(split_line[1],True)
        elif split_line[0] == "ONNX":
            onnx_name = split_line[1]
            onnx_name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', onnx_name)
            printLog(onnx_name)
    if len(lstart) != len(lqnt) or len(lstart) != len(lstop):
        printLog("Erro no parser da lista")
        return -1, -1, -1, "not provide"
    
    return lstart, lstop, lqnt, onnx_name, lflt

def new_variables(inx):
    inx = inx + 1
    if inx >= len(list_of_start):
        printLog("Valor de indice errado, final ? ({})".format(inx))
        return 1, 1, 1 , 1, 1
    start = list_of_start[inx]
    end = list_of_end[inx]
    quant2 = quant[inx]
    aflot = list_float_st[inx]
    
    return inx, start, end, quant2, aflot


def define_max_min (comp, maxA, minA):
    
    if (comp > maxA):
        maxA = comp
    if(comp < minA):
        minA = comp
    
    return maxA, minA


raiz = os.path.dirname(os.path.realpath(__file__))
raiz = raiz.replace("\\" ,"/") 
raiz += "/"

now = datetime.now()
date_time = now.strftime("%m_%d_%Y-%H_%M_%S")
loggname = 'LogMini'+date_time+'.txt'
loggname = raiz + loggname
printLog(loggname)

float_confere = True 
# arquivos com as definicoes deve estar no diretorio do script

if(len(sys.argv) > 2):
    file_name_arg = sys.argv[1]
else:
    file_name_arg = "values_pass.txt"
    
file_name_arg = raiz + file_name_arg

list_of_start, list_of_end, quant, main_dot_onnx, list_float_st  = mount_list(file_name_arg)
printLog(list_of_start, list_of_end, quant, main_dot_onnx)

for x in quant:
    print(f"tamanho = {x} - type = {type(x)}")

print(f"tamanho {len(quant)}")

only_name_file = main_dot_onnx[:-5]

#arquivos para serem criados .... 
new_onnxs_diretory = raiz+"onnxs_encoded_minifloat/"
if not os.path.exists(new_onnxs_diretory):
    os.makedirs(new_onnxs_diretory)


with open('floats_mini.json', 'r') as f:
    mini = json.load(f)

infos_floats = infos_mini_float(mini)
print(infos_floats)
infos_floats['float_16'] = ['numpy']
print(infos_floats.keys())
print(mini.keys())
names_file = new_onnx_filename(new_onnxs_diretory,only_name_file, infos_floats.keys())
onnx_files = open_onnx_files(names_file)
printLog(onnx_files)

main_dot_onnx_path = raiz + main_dot_onnx 


MAXIMUM = - math.inf
MINIMUN =  math.inf
i = 0

final_size = []
cont_qnt = 0

# ler a primeira vez e achar minimo e máximo
with open(main_dot_onnx_path, "rb") as f:
    byte = f.read(1)
    indx = 0
    i = 0
    act_start = list_of_start[indx]
    act_end = list_of_end[indx]
    act_quant = quant[indx]
    act_flt = list_float_st[indx]
    while byte:
        # Do stuff with byte.
        if  i == act_start:
            printLog("Start [{}]".format(i))
            byte_3 = f.read(3)
            i = i + 3
            byte_c = b"".join([byte, byte_3])
            bytec_int = int.from_bytes(byte_c, "little")
            numc_f = (unpack("<f",byte_c))[0]
            if (abs(numc_f - act_flt) < 0.1 ):
                printLog(f"{numc_f} - {act_flt} = {(numc_f - act_flt)} (OK_Passou)")
                float_confere = float_confere and True
            else:
                printLog(f"{numc_f} - {act_flt} = {abs(numc_f - act_flt)} (Falhou!!)")
                float_confere = float_confere and False
            
            MAXIMUM, MINIMUN = define_max_min (numc_f, MAXIMUM, MINIMUN)
            for cont_qnt in range (act_quant - 1):
                byte_4 = f.read(4)
                byte_4_int = int.from_bytes(byte_4,"little")
                num_f = (unpack("<f",byte_4))[0]
                MAXIMUM, MINIMUN = define_max_min (num_f, MAXIMUM, MINIMUN)
                i = i + 4
            printLog ("[",indx+1,"]","Maximo = ", MAXIMUM, "minimo ", MINIMUN )
            indx, act_start, act_end, act_quant,act_flt = new_variables(indx)
            print(f"Encontrar act_start {act_start} - estamos em {i} act_quant {act_quant}")
            if(i > act_start):
                print(f"ERRO ao tentar encontrar o float {act_flt}! Atual inx eh {i} e procurando está em {act_quant}")
        byte = f.read(1)
        i = i + 1
    print(f"byte fim {byte} --  {i}")
f.close()
i = 0
byte = 0
byte_3 = 0
byte_4 = 0

printLog("Encontrado o máximo e o minímo!! \n Máximo {0} e \n Minimo {1}".format(MAXIMUM, MINIMUN))
printLog("Fim primeira leitura -- começo da segunda etapa \n valores encontrados")
with open(main_dot_onnx_path, "rb") as f:
    byte = f.read(1)
    indx = 0
    act_start = list_of_start[indx]
    act_end = list_of_end[indx]
    act_quant = quant[indx]
    act_flt = list_float_st[indx]
    while byte:
        # Do stuff with byte.
        if  i == act_start:
            byte_3 = f.read(3)
            i = i + 3
            byte_c = b"".join([byte, byte_3])
            bytec_int = int.from_bytes(byte_c, "little")
            numc_f = (unpack("<f",byte_c))[0]
            printLog("[",hex(i-3),"]",hex(bytec_int), "float rep = ", numc_f )
            new_value = encoder(numc_f,MAXIMUM, MINIMUN,onnx_files,infos_floats)
            #new_csv.write(hex(bytec_int) +  "," + str(numc_f) +","+ hex(new_value) + "," + str(new_float) + "\n")
            for cont_qnt in range (act_quant - 1):
                byte_4 = f.read(4)
                byte_4_int = int.from_bytes(byte_4,"little")
                num_f = (unpack("<f",byte_4))[0]
                new_value = encoder(num_f,MAXIMUM, MINIMUN,onnx_files,infos_floats)
                #new_csv.write(hex(byte_4_int) + "," + str(num_f)+"," + hex(new_value)+"," + str(new_float)  + "\n")
                i = i + 4
            r_size = cont_qnt + 2
            print(f"Quantidade = {r_size}")
            final_size.append(r_size)
            #printLog(r_size)
            indx, act_start, act_end, act_quant,act_flt = new_variables(indx)
            #printLog(new_float_inx)
            #printLog("Index: ", indx, " start ", hex(act_start), " stop ", hex(act_end), " quantizacao ", (act_quant))
        else:
            write_same_byte(onnx_files, byte)


        byte = f.read(1)
        i = i + 1
    f.close()
    

    close_onnx_files(onnx_files)
    total_float = sum(quant)
    printLog("------ Estatisticas -------------\n Total  de floats = ", total_float)
    sizetotal = os.stat(main_dot_onnx_path).st_size
    printLog(f"Tamanho total em Bytes {sizetotal}B ({sizetotal/1024})KB - sendo {total_float*4}B ({(total_float*4)/1024}KB) floats")
    printLog(f"Proporção de floats por total {((total_float*4)/sizetotal)*100}%")
    printLog("Conferindo valores .... ")
    printLog(f"First floats conferes ???  {float_confere}")
    printLog(f"Tamanho das lista conferes ???  {len(quant) == len(final_size)}")
    for v in range(len(final_size)):
        printLog("[",v ,"]", final_size[v], "eee", quant[v] , "OK?", (quant[v] == final_size[v]))
        
        

