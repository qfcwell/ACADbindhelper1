# -*- coding: utf-8 -*- 运行python
import acadbindhelper
import warnings

if __name__=="__main__":
    warnings.simplefilter("once")
    helper=acadbindhelper.helper()
    #helper.AutoRun(Auto=True)
    while 1:
        try:
            helper.AutoRun(Auto=True)
        except:
            pass


