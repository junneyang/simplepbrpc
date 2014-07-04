#!/usr/bin/env python
#-*- coding: utf-8 -*-
import json

#测试用例路径
testcasefilepath=u"./testcase.data"
parsetestcase=json.load(open(testcasefilepath, "r"),encoding='utf-8')

if __name__ == "__main__":
    print parsetestcase
