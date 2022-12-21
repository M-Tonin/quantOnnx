
#include <iostream>
#include<fstream>
#include <string>
#include <time.h>
#include <iomanip>
#include <vector> 
#include <stdint.h>
#include <cstring>
#include <vector>
#include <algorithm>
#include <sstream>

using namespace std;
struct isSpace
{
	bool operator()(unsigned c)
	{
		return (c == ' ' || c == '\n' || c == '\r' ||
				c == '\t' || c == '\v' || c == '\f');
	}
};

void dumphex(const std::vector<char>& v);
static float InputFloat(std::string label);
vector<float> read_meta(fstream& f, std::string nomeArquivo);

int main()
{
	cout << "read meta " << endl;
	
	fstream fout;
	fout.open("values_pass.txt", ios::out | ios::app); 
	string arquivoConfiguracao;
	cout << "qual o nome do arquivo Configuracao a ser pesquisado?";
	cin >> arquivoConfiguracao;
	vector<float> init_floats = read_meta(fout,arquivoConfiguracao);  
	

	string fileonnx;
	cout << "qual o nome do arquivo ONNX a ser pesquisado ?";
	cin >> fileonnx;
    ifstream ifd(fileonnx, ios::binary | ios::ate);
    int size = ifd.tellg();
    cout << "Size :" << size;
    ifd.seekg(0, ios::beg);
    vector<char> buffer;
    buffer.resize(size); // << resize not reserve
    ifd.read(buffer.data(), size);

    cout.write(buffer.data(), buffer.size()); // you cannot just output buffer to cout as the buffer won't have '\0' ond-of-string terminator
 	cout << "HEX FORMAT" << endl;   
 	
	vector<uint8_t> hex_buffer;
	for (int j = 0; j < buffer.size(); j++) {

		hex_buffer.push_back(static_cast<uint8_t>(buffer[j]));
		//printf("%02X ", hex_buffer.at(j));

	} 
	vector<int> posvect;
	fout << "index_start: ";
	printf("Size - %d\n",init_floats.size() );
	vector<uint8_t> pattern;
	auto start_search = std::begin(hex_buffer);
    unsigned int position = 0;
	for(int ti = 0; ti <init_floats.size(); ti++) {
		uint8_t bytes[sizeof(float)];
	   *(float*)(bytes) = init_floats.at(ti);  // convert float to bytes
	    printf("bytes = [ 0x%.2x, 0x%.2x, 0x%.2x, 0x%.2x ]\r\n", bytes[0], bytes[1], bytes[2], bytes[3]);
		pattern.clear();
		for (int k = 0; k < 4 ; k++ ){
			pattern.push_back(static_cast<uint8_t>(bytes[k]));
			printf("%02X ", pattern.at(k));
		}
		
		auto res = std::search(start_search, std::end(hex_buffer), std::begin(pattern), std::end(pattern));
	    if(res == std::end(hex_buffer)) {
	        std::cout << "Couldn't find it.\n";
	    } else {
	        std::cout << "Found it.\n";
	        position = res - hex_buffer.begin();
	        start_search = res;
	        printf("Na posicao %u = 0x%X ", position , position);
	        posvect.push_back(position);
	        fout << position;
	        if (ti <  (init_floats.size() - 1)) {
				fout << ", ";
			}

	    } 		
	}
	fout<<"\nindex_final: ";
	for (int y = 0; y < posvect.size(); y++ ) {
		fout << posvect.at(y);
		if(y < (posvect.size() - 1)) {
			fout << ", ";
		}
	}
	
	fout << "\nONNX:" << fileonnx <<endl;
    //dumphex(buffer);
	fout.close();    
    printf("FIM DE PROGRAMA!!!!\n");
}


void dumphex(const std::vector<char>& v)
{
    const int N = 16;
    const char hex[] = "0123456789ABCDEF";
    char buf[N*4+5+2];
    for (int i = 0; i < v.size(); ++i)
    {
        int n = i % N;
        if (n == 0)
        {
            if (i)
                puts(buf);
            memset(buf, 0x20, sizeof(buf));
            buf[sizeof(buf) - 2] = '\n';
            buf[sizeof(buf) - 1] = '\0';
        }
        unsigned char c = (unsigned char)v[i];
        buf[n*3+0] = hex[c / 16];
        buf[n*3+1] = hex[c % 16];
        buf[3*N+5+n] = (c>=' ' && c<='~') ? c : '.';
    }
    puts(buf);
	
}

static float InputFloat(std::string label)
{
    std::string input;
    std::cout << label;
    std::cin >> input;
    return atof(input.c_str());
}

vector<float> read_meta(fstream& f,std::string nomeArquivo) {
	
	// File pointer 
    fstream fin; 
  
    // Open an existing file 
    fin.open(nomeArquivo, ios::in); 
	
	vector<float> values;
	vector<int> qnt;
    string line, word, temp; 
  	cout << "opa";
  	// i = 1  ---- floats
  	// i = 2 ----- quantity
  	int i = 1;
    while (fin >> temp) { 
     	printf("------ Nova linha ------------\n");
        // read an entire row and 
        // store it in a string variable 'line' 
        getline(fin, line); 
        cout << line;
        // used for breaking words 
        stringstream s(line); 

        // read every column data of a row and 
        // store it in a string variable, 'word'
        if (i == 2){
			f << "quantite: "; 
		}

        while (std::getline(s, word,',')) { 
  			word.erase(std::remove_if(word.begin(), word.end(), isSpace()), word.end());
  			cout << "S |" << word << "|" << endl;
            // add all the column data 
            // of a row to a vector 
            if(i == 1) {
				values.push_back(strtof(word.c_str(),NULL));	   	
			}
			if( i == 2) {
				qnt.push_back(stoi(word));
			}
        } 
        i++;		
   	}  
	
	for(int k=0; k < qnt.size(); k++){
		
		f << qnt.at(k);
		if(k < (qnt.size() - 1)) {
			f << ", ";
		}
	
	}

	f << "\n";
	
	return values;

}
