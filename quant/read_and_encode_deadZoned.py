from struct import unpack, pack
import numpy as np
import sys, re, binascii, os, math, random
from datetime import datetime

def decompose(value): 
    """decomposes a float32 into negative, exponent, and significand"""
    sinal = (value >> 31)
    expoente = ((value & 0x7F800000) >> 23)
    st_exp = format(expoente, '#04x')
    mant = ((value & 0x007FFFFF))
    st_mant = format(mant, '#04x')
    return (sinal, expoente, st_exp, mant, st_mant)

def new_onnx_filename(thepath, only_name,dezoned):
    liname = []
    for i in range (24,1,-1):
        for dz in dezoned:
            st = ""
            st = thepath + only_name + "_enc_" + str(i) + f"bits_{str(dz).replace('.','p')}dz.onnx"
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
        

def encoderDZ(value:np.float32, maxi, mini, files_onnx,deadZone):
    # Q = 1 / 2 ** N
    #  q = round ((value + min) / Q))
    # xq = q * Q - min
    
    ###########
    # Q = 1/ (2^N)
    # intervalo = max - min
    # q = round((value + min)/ (Q * intervalo))
    # xq = q * intervalo * Q + min 
    intervalo = maxi - mini
    list_int_quant = []
    list_float_desquant = []
    for q_inx in range(24,1,-1):
        Q = (1/(2**q_inx))
        passos = Q * intervalo
        if(math.isnan(value)):
            printLog("Problema - IsNan Encontrado!")
        abs_zoned = 0
        for dzoned in deadZone:
            signal = 1 if value >= 0 else -1
            q_int = signal * np.floor((abs(value)/passos) + 0.5)
            xq = signal * ( (passos/2) + (passos * (abs(q_int) - 1 + dzoned )))
            if(random.randint(1,5487334) == 33):
                print('**@'*30)
                print(f'[{q_int}] <=> [{dzoned}] | Antigo -> {value} | Reconstructed -> {xq}')
            #abs_zoned = 1 + dzoned
            #if abs(value / passos) < abs_zoned:
            #if abs(value) < passos * abs_zoned:
            #    q_int = 0
            #    xq = 0
            #else:
            #    yaux = abs((value - mini)/passos) - 1 - dzoned # - abs_zoned
            #    q_int = np.floor(yaux) + 0.5 + 1 + dzoned # + abs_zoned
            #    xq = float(q_int * passos + mini)
            #    if(random.randint(1,54334) == 33):
            #        print('**@'*30)
            #        print(f'{q_int} | {value} | {xq}')
        
            list_int_quant.append(int(q_int))
            list_float_desquant.append(float(xq))
    
    for r in range(len(list_float_desquant)):
        float_litlle_edian_write(list_float_desquant[r],files_onnx[r] )
    
    val_23b = list_int_quant[0]
    float_back = list_float_desquant[0]
    return val_23b, float_back

    
def encoder(value:np.float32, maxi, mini, files_onnx):
    # Q = 1 / 2 ** N
    #  q = round ((value + 0.6) / Q))
    # xq = q * Q - 0.6
    intervalo = maxi - mini
    list_int_quant = []
    list_float_desquant = []
    for q_inx in range(24,1,-1):
        Q = (1/(2**q_inx))
        if Q >= 1/4:
            prun = 2 * Q
        if(math.isnan(value)):
            printLog("Problema - IsNan Encontrado!")
        q_int = int(round((value - (mini))/(intervalo*Q)))
        xq = float(q_int* intervalo * Q + mini)
        if (xq == maxi):
            xq_last =  float((q_int - 1) * intervalo * Q + mini)
            if xq > 0.0 and xq_last < 0.0:
                xq = 0.0
        elif xq == mini:
            xq_next =  float((q_int + 1) * intervalo * Q + mini)
            if xq_next > 0.0 and xq < 0.0:
                xq = 0.0
        else:
            xq_next =  float((q_int + 1) * intervalo * Q + mini)
            xq_last =  float((q_int - 1) * intervalo * Q + mini)
            if (xq_next > 0.0 and xq < 0.0) or (xq > 0.0 and xq_last < 0.0):
                xq = 0.0            
        list_int_quant.append(int(q_int))
        '''
        if (abs(xq) <= prun):
            #print(f' prunning {xq}')
            xq = 0.0
        '''            
        list_float_desquant.append(float(xq))

    '''
    list_int_quant = [q[0](q24),q[1](q23),q[2](q22), q[3](q21),q[4](q20), q[5](q19), q[6](q18), q[7](q17), q[8](q16), q[9](q15), q[10](q14), q[11](q13),
    , q[12](q12), q[13](q11), q[14](q10), q[15](q9), q[16](q8), q[17](q7), q[18](q6)]
    '''
    txtquant = ""
    for t_i in range(len(list_int_quant)):
        if i != (len(list_int_quant) - 1) :
            txtquant = txtquant + str(list_int_quant[t_i]) + ","
        else:
            txtquant = txtquant + str(list_int_quant[t_i])
    #printLog(txtquant)        
    enconder_csv.write(txtquant  + "\n")
    
    txtfloat = str(value) + ","
    for t_i in range(len(list_float_desquant)):
        if i != (len(list_int_quant) - 1):
            txtfloat = txtfloat + str(list_float_desquant[t_i]) + ","
        else:
            txtfloat = txtfloat + str(list_float_desquant[t_i])
    #printLog(txtfloat)   
    f_enconder_csv.write(txtfloat  + "\n")
    
    
    for r in range(len(list_float_desquant)):
        float_litlle_edian_write(list_float_desquant[r],files_onnx[r] )
    
    #val_23b = (sign_bit << 23) | val
    #printLog("Sinal - ", sign_bit, "val - ", hex(val_23b),"float_back =",  float_back)
    #byte3 = (val_23b & 0xFF0000) >> 16 
    #byte3 = byte3.to_bytes(1, "big" )
    #byte2 = (val_23b & 0x00FF00) >> 8
    #byte2 = byte2.to_bytes(1, "big" )
    #byte1 = (val_23b & 0x0000FF)
    #byte1 = byte1.to_bytes(1, "big" )

    val_23b = list_int_quant[0]
    float_back = list_float_desquant[0]
    return val_23b, float_back
  
def parseLine(linha):
    linha = re.sub(r"\s+", "", linha)
    IndexList = []
    stringlist = []
    stringlist = linha.split (",")
    for i in range(len(stringlist)):
        IndexList.append(int(stringlist[i],0))
    #printLog ("list: ", IndexList)
    return IndexList
  
def mount_list(file_name_arg):
    printLog("Montando lista essencial")
    lstart = []
    lstop = []
    lqnt = []
    onnx_name = "not provide"
    fp = open(file_name_arg,"r")
    contents = fp.readlines()
    for line in contents:
        split_line = line.split(":")
        # Obtencao da lista index_start: 
        if split_line[0] == "index_start":
            lstart = parseLine(split_line[1])
        # Obtencao da lista index_final: 
        elif split_line[0] == "index_final":
            lstop = parseLine(split_line[1])
        # Obtencao da lista quantite: 
        elif split_line[0] == "quantite":
            lqnt = parseLine(split_line[1])
        elif split_line[0] == "ONNX":
            onnx_name = split_line[1]
            onnx_name = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', onnx_name)
            printLog(onnx_name)
    if len(lstart) != len(lqnt) or len(lstart) != len(lstop):
        printLog("Erro no parser da lista")
        return -1, -1, -1, "not provide"
    
    return lstart, lstop, lqnt, onnx_name

def new_variables(inx):
    inx = inx + 1
    if inx >= len(list_of_start):
        printLog("Valor de indice errado, final ? ({})".format(inx))
        return 1, 1, 1 , 1
    start = list_of_start[inx]
    end = list_of_end[inx]
    quant2 = quant[inx]
    
    return (inx, start, end, quant2)


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
loggname = 'Log_deadzone_'+date_time+'.txt'
loggname = raiz + loggname
printLog(loggname)

# arquivos com as definicoes deve estar no diretorio do script

if(len(sys.argv) > 2):
    file_name_arg = sys.argv[1]
else:
    file_name_arg = "values_pass.txt"
    
file_name_arg = raiz + file_name_arg

list_of_start, list_of_end, quant, main_dot_onnx  = mount_list(file_name_arg)
printLog(list_of_start, list_of_end, quant, main_dot_onnx)
only_name_file = main_dot_onnx[:-5]

new_onnxs_diretory = raiz+"onnxs_encoded_deadzoned/"
if not os.path.exists(new_onnxs_diretory):
    os.makedirs(new_onnxs_diretory)

dzonas = [0.1,0.25,0.4,0.7]

names_file = new_onnx_filename(new_onnxs_diretory,only_name_file,dzonas)
onnx_files = open_onnx_files(names_file)

main_dot_onnx_path = raiz + main_dot_onnx 

MAXIMUM = - math.inf
MINIMUN =  math.inf
i = 0

#list_of_start =     [0x5df,  0x19f9,  0x1a43   , 0x481a5e, 0x481c7e,  0x493c9b, 0x493dbc, 0X494257]
#list_of_end =       [0x19db, 0x1a1d,  0x481a3F,  0x481c5A, 0x493C7a   , 0x493d97, 0X494238, 0x4942D3 ]
#quant =         [128*10, 10*1,    9216 * 128, 128    , 64 * 32 * 9, 64     , 32 * 9  , 32    ]
final_size = []
cont_qnt = 0
# ler a primeira vez e achar minimo e máximo
i = 0
byte = 0
byte_3 = 0
byte_4 = 0
MAXIMUM, MINIMUN = 1, -1
printLog("Encontrado o máximo e o minímo!! \n Máximo {0} e \n Minimo {1}".format(MAXIMUM, MINIMUN))
printLog("Fim primeira leitura -- começo da segunda etapa \n valores encontrados")
with open(main_dot_onnx_path, "rb") as f:
    byte = f.read(1)
    indx = 0
    act_start = list_of_start[indx]
    act_end = list_of_end[indx]
    act_quant = quant[indx]
    while byte:
        # Do stuff with byte.
        if  i == act_start:
            byte_3 = f.read(3)
            i = i + 3
            byte_c = b"".join([byte, byte_3])
            bytec_int = int.from_bytes(byte_c, "little")
            numc_f = (unpack("<f",byte_c))[0]
            printLog("[",hex(i-3),"]",hex(bytec_int), "float rep = ", numc_f )
            new_value, new_float = encoderDZ(numc_f,MAXIMUM, MINIMUN,onnx_files,dzonas)
            #new_csv.write(hex(bytec_int) +  "," + str(numc_f) +","+ hex(new_value) + "," + str(new_float) + "\n")
            for cont_qnt in range (act_quant - 1):
                byte_4 = f.read(4)
                byte_4_int = int.from_bytes(byte_4,"little")
                num_f = (unpack("<f",byte_4))[0]
                new_value, new_float = encoderDZ(num_f,MAXIMUM, MINIMUN,onnx_files,dzonas)
                #new_csv.write(hex(byte_4_int) + "," + str(num_f)+"," + hex(new_value)+"," + str(new_float)  + "\n")
                i = i + 4
            r_size = cont_qnt + 2
            final_size.append(r_size)
            #printLog(r_size)
            indx, act_start, act_end, act_quant = new_variables(indx)
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
    for v in range(len(final_size) - 1):
        printLog("[",v ,"]", final_size[v], "eee", quant[v] , "OK?", (quant[v] == final_size[v]))
        
        

