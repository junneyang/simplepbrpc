#include <iostream>
#include <fstream>
#include <string>

using namespace std;

int main()
{
 ifstream in("test.data");               //注意这里symmetry.txt为你当前工程目录下的文件内容
 for(string s;getline(in,s);)
  cout<<s<<endl;
}

