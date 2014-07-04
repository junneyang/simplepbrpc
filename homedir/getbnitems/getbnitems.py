#!/usr/bin/env python
#-*- coding: utf-8 -*-
from common.cmdLib import *

'''exp=u"[8344169398048163073,1,1.34343e+07,3.23096e+06,距离小于8KM][8344169398048163071,0.666667,1.34343e+07,3.23097e+06,乡间印象][8344169398048163070,0.333333,1.34343e+07,3.23096e+06,川妹火锅黎明旗舰店]"
status,output=cmd_execute("./getbnitem 10.48.55.39:7789 bnitems 0 13430985.75 3233968.82 178 9991479517896860251")
output=output.decode('gbk')
print output

output=output.strip()
output_list=output.split("\n")
output= "".join(output_list)
print output
print exp
assert(output == exp)'''

import unittest
import parsetestcase
ip_port="10.48.55.39:7789"
algorithm_id="bnitems"

class getbnitems(unittest.TestCase):
    def service_proc(self,test_case_id):
        case_name=parsetestcase.parsetestcase[test_case_id]['info']['name']
        case_input=parsetestcase.parsetestcase[test_case_id]['input']
        exp_data=parsetestcase.parsetestcase[test_case_id]['exp_data']
        status,output=cmd_execute("./getbnitem "+ip_port+" "+algorithm_id+" "+case_input)
        output=output.decode('gbk')
        output=output.strip()
        output_list=output.split("\n")
        output= "".join(output_list)
        '''print("\noutput:\n")
        print output.encode('utf-8')
        print("\nexp_data:\n")
        print exp_data'''
        assert(output == exp_data)

    for test_case_id in parsetestcase.parsetestcase:
        exec("def test_%s(self): self.service_proc('%s')" %(test_case_id,test_case_id))

if __name__ == '__main__':
    TestSuit=unittest.TestLoader().loadTestsFromTestCase(getbnitems)
    unittest.TextTestRunner(verbosity=2).run(TestSuit)
