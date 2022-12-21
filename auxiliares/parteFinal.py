float_csv = []
first_float = []
for RAW_DATA in lista_raw:
    at = 0
    total = 0 
    while at < len(RAW_DATA):
        fin = at+4
        substrin = RAW_DATA[at:fin]
        resu = FourString_float(substrin)
        if total == 0:
            first_float.append(resu)

        float_csv.append(resu)
        new_file.write(str(resu) + "," +"\n")
        at = fin
        total += 1
tam = len(float_csv)
print(tam)
tot = 0
min = float_csv[0]
max = float_csv[0]
for al in float_csv:
    tot += al
    if al < min:
        min = al
    if al > max:
        max = al

media = tot/tam
print(f" media {media}")
print(f" Maxima {max} e Minima {min}")
print(f"Tamanho - {len(first_float)}")
print(first_float)