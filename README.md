# quantOnnx
Demonstração de como realizar a quantização do de uma modelo .onnx e sua validação.

Passo a passo:

1. Baixar o Protocol Buffer Compiler Installation para conseguir verificar as informações do modelo.
1.1 Acessar https://grpc.io/docs/protoc-installation/

2. Depois, devemos executar o comando

>> protoc --decode=onnx.ModelProto onnx.proto < {{nomeModelo}}.onnx  | tee {{nomeModelo}}.proto

![image](https://user-images.githubusercontent.com/21134353/208808208-4cfda95e-0c34-42ed-b0da-471c97510877.png)

Nota: o arquivo onnx.proto e {{nomeModelo}}.onnx  devem estar no local de execução se não será obrigado a colocar o caminho.

Esse comando irá produzir o arquivo **{{nomeModelo}}.proto** que deverá ser colocado na pasta **/onnxs**

3. Executar o comando:

>> python gerarInformacoesModelo.py

Esse comando irá gerar três artefatos que ficam em  **/onnxs/info/**
 * {{nomeModelo}}_float_data.csv: contem informações de todos os pesos do modelo.
 * {{nomeModelo}}_strings.py: arquivo que pode ser necessário em alguns caso para encontrar os pesos [não usual].
 * {{nomeModelo}}_info.txt: arquivo mais importante contendo as informações necessárias para realizar a quantização

4. Copiar o arquivo **{{nomeModelo}}_info.txt** para a pasta **/quant**

5. Depois disso será necessário entrar na pasta **/quant** e realizar a 'compilação' do programa em cpp "mount_onnx_info.cpp"

>> g++ -o onnxInfo mount_onnx_info.cpp

>> onnxInfo

5.1 Inserir informações pedidas pelo programa.

>> qual o nome do arquivo Configuracao a ser pesquisado? {{nomeModelo}}_info.txt

![image](https://user-images.githubusercontent.com/21134353/208809421-8bfcd9ac-4848-4953-bbdf-4a494d1f2bae.png)


>> qual o nome do arquivo ONNX a ser pesquisado ? {{nomeModelo}}.onnx

![image](https://user-images.githubusercontent.com/21134353/208809460-10183125-c7bc-4cc1-b75b-fb04fbdfbff6.png)


6. Por fim, será gerado o artefato **values_pass.txt** que é o último artefato importante, com esses artefatos será possível gerar novos .onnxs quantizados.

* read_and_encode_deadZoned.py
* read_and_encode_midrise.py
* read_and_encode_midtread.py
* read_and_encode_miniFloat.py
* read_and_encode_miniFloat.py

Esse cinco scripts irão produzir o novos modelos de acordo com o tipo de quantização que irão em colocar em cada respectiva pasta.

![image](https://user-images.githubusercontent.com/21134353/208809940-ae879046-9e65-4082-aa43-84e3a6339b25.png)

![image](https://user-images.githubusercontent.com/21134353/208809978-67621022-fb60-4e7b-9b27-57c2e98577ca.png)



Feito isso, o modelo está quantizado e depois disso começa a etapa de validação do modelo.

[  .... .... ]



