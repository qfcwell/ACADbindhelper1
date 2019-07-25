# -*- coding: utf-8 -*- 运行python
import os,sys,stat,time
from pyautocad import *
import pywinauto
#import pymysql,pymssql
import pymssql
import sysinfo
import json
import socket,itertools

#host,port = "localhost",8097
from config import *

os.chdir('D:\\')

def main():
    #username = "Username",
    #password = "Password"
    #warnings.simplefilter("once")
    #h = helper(mysql = "superset1.minitech.site")
    #e = h.GetExceptions_list()
    #print(e)
    #bind.RunBind()
    pass

def print_func(func):#装饰器，打印func名
    def inner(*args,**kwargs):
        print(func.__name__+':')
        print(args,kwargs)
        return func(*args,**kwargs)
    return inner  

class Exception():
    def __init__(self,title_re,operation,content_re='',app_path='',treatment=''):
        self.app=pywinauto.application.Application()
        self.app_path=app_path
        self.title_re=title_re
        self.content_re=content_re
        self.operation=operation
        self.click_dlg=''
        self.result=0
        self.treatment=treatment
        try:
            if self.app_path:
                self.app.connect(path=self.app_path)
            else:
                self.app.connect(title_re=self.title_re) 
            self.window=self.app.window(title_re=self.title_re)
            if self.content_re:
                crash = self.window.window(title_re=self.content_re)
                crash.print_control_identifiers()
            else:
                self.window.print_control_identifiers()
            if self.treatment in ['bind','CloseErrorReportWindow']:
                self.result=1
            elif self.treatment=='click':
                self.click_dlg=self.window[self.operation]
                self.click_dlg.print_control_identifiers()
                self.result=1
        except (pywinauto.findbestmatch.MatchError,pywinauto.findwindows.ElementNotFoundError):
            self.result=0
            self.treatment='pass'
        except (pywinauto.findwindows.ElementAmbiguousError,pywinauto.application.ProcessNotFoundError):
            self.result=1
            self.treatment='restart'

    def click(self):
        if self.click_dlg and self.treatment=='click':
            print('click')
            self.click_dlg.click()
            return 1
        else:
            return 0   

class helper():

    
    def __init__(self,mysql='',server='shenzhen',method=0):
        self.ACSPath_dict=rpc_conf["ACSPath_dict"]
        self.Server_dict=rpc_conf["Server_dict"]
        self.cpath='D:\\ACADbindhelper'#sys.path[0]
        self.arx_path=arx_path
        self.lsp_path=lsp_path
        self.r_path='C:\\Users\\virtual\\AppData\\Local\\Temp\\AcsTempFile\\提资接收区'
        self.Exceptions=rpc_conf["Exception_list"]
        self.Hostname=socket.gethostname()
        if self.Hostname in rpc_conf["Server"]:
            self.Server=rpc_conf["Server"][self.Hostname]
        else:
            print("Server error, this computer is not registed")
            self.Server="shenzhen"
        if self.Hostname in rpc_conf["Method"]:
            self.Method=rpc_conf["Method"][self.Hostname]
        else:
            print("Method error, this computer is not registed")
            self.Method=1
        if self.Server:
            #self.Create_RestartACS()
            #self.restartCAD='restartCAD.bat'
            self.acs_path=self.ACSPath_dict[self.Server]
            if self.Method==2:
                self.acs_exe=os.path.join(self.ACSPath_dict[self.Server],'AcsTakeoutFileTool.exe')
            else:
                self.acs_exe=os.path.join(self.ACSPath_dict[self.Server],'AcsTools.exe')
            self.EmptyDwg=os.path.join(self.acs_path,'EmptyDwg.dwg')
            self.APP_dict={'CAD':'C:\\Program Files\\Autodesk\\AutoCAD 2012 - Simplified Chinese\\acad.exe','ACS':self.acs_exe,'NOAPP':''}
        else:
            print("No Server Set!")

    def StartACS(self):
        while 1:
            #print(self.restartACS)
            os.system('tskill acstools')
            os.system('tskill AcsTakeoutFileTool')
            os.system('start "acstools" "%s"' % self.acs_exe)
            time.sleep(10)
            dlg=self.Check_ACS()
            if dlg:
                break
        if self.Method==0:
            dlg['绑定失败跳过'].click()
            dlg['优先处理绑定失败的文件'].click()
            dlg['开始绑定'].click()
        elif self.Method==1:
            dlg['开始绑定'].click()
        elif self.Method==2:
            dlg['开始'].click()

    def Check_ACS(self):
        app=pywinauto.application.Application()
        try:
            app.connect(path=self.acs_exe)
        except pywinauto.application.ProcessNotFoundError:
            return 0
        if self.Method in [0,1]:
            dlg=app.window(title_re='工具管理器')
            try:
                dlg['开始绑定'].print_control_identifiers()
                return dlg
            except pywinauto.findbestmatch.MatchError:
                return 0
        elif self.Method in [2]:
            dlg=app.window(title_re='提资文件检查')
            try:
                dlg['开始'].print_control_identifiers()
                return dlg
            except pywinauto.findbestmatch.MatchError:
                return 0
        else:
            return 0

    def StartCAD(self): 
        while 1:
            #print(self.restartCAD)
            #os.system(self.restartCAD)
            os.system('tskill acad')
            os.system('start "acad" "%s"' % self.APP_dict['CAD'])
            print("Waiting for ACAD")
            t=30
            while t>0:
                time.sleep(1)
                t=t-1
            t=1
            while t<90:
                try:
                    acad =Autocad(create_if_not_exists=False)
                    print(self.arx_path)
                    acad.Application.LoadARX(self.arx_path)
                    return 1
                except:
                    time.sleep(2)
                    t+=1

    def AutoRun(self,Auto=True):
        self.Auto=Auto
        self.restart()
        while 1:
            time.sleep(1)
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
            for (app_path,title_re,content_re,operation,treatment) in self.Exceptions:
                ex=Exception(title_re=title_re,operation=operation,content_re=content_re,app_path=app_path,treatment=treatment)
                if ex.treatment=='bind':
                    bind=Binding()
                    bind.RunBind(try_times=2)
                    #self.log_result(file_name=bind.name,file_path=bind.path,result=str(bind.result))
                    if bind.result:
                        ex.window["确定"].click()
                    else:
                        ex.window["取消"].click()
                elif ex.treatment=='restart':
                    self.restart()
                elif ex.treatment=='CloseErrorReportWindow':
                    res=CloseErrorReportWindow()
                    if res=='restart':
                        self.restart()
                elif ex.treatment=='click':
                    ex.click()
                else:
                    pass
            CheckMEM()
            bc=BindCleaner(f_path=self.r_path,not_binded=self.GetNotBinded())
            bc.clean() 
    '''
    def log_result(self,file_name,file_path,result):
        with open("d:\\result_log.txt","a") as txt:
            txt.write("#".join(['file name',file_name,'file path',file_path,'result',result]))
            txt.write("\n")
        try:
            
            with pymysql.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db) as cur:
                hostname=socket.gethostname()
                cur.execute(u"INSERT INTO BindHelperRecord(file_name,file_path,result,hostname) VALUES(%s,%s,%s,%s)",[file_name,file_path,result,hostname])
            print("#".join(['file name',file_name,'file path',file_path,'result',result]))
            return 1
        except:
            print("log_result Failed")
            return 0
    '''
    def GetNotBinded(self):
        try:
            (host,user,password,database)=self.Server_dict[self.Server]
            with pymssql.connect(host=host, user=user, password=password,database=database) as conn:
                cur=conn.cursor()
                cur.execute(u"SELECT ID FROM ProductFile where RecordState='A' and IsCurrent is null and BindState<>'Binded'")
                return set(cur.fetchall())
        except pymssql.OperationalError:
            return set()

    def restart(self):
        if self.Auto:
            self.StartCAD()
            self.StartACS()
        else:
            print('NEED RESTART')

class Binding():
    def __init__(self):
        self.acad =Autocad(create_if_not_exists=False)
        self.acad.Application.LoadARX(arx_path)
        self.result=0

    def get_doc(self):
        self.doc=self.acad.doc
        self.path,self.name=self.doc.Path,self.doc.Name
        return self.doc

    def has_xref(self):
        self.get_all_xref()
        if self.a_xref_name:
            return True
        else:
            return False

    def get_all_xref(self):#获取所有外参
        lst=[]
        self.a_xref_name=[]
        self.a_xref_path=[]
        self.a_xref_name_path=[]
        self.Blocks=self.doc.Blocks
        for i in range(self.Blocks.Count):
            obj=self.Blocks.item(i)
            if obj.IsXRef:
                lst.append(obj) 
                xname,xpath=obj.Name,obj.Path
                self.a_xref_name.append(xname)
                self.a_xref_path.append(xpath)
                self.a_xref_name_path.append((xname,xpath))
        return lst

    @print_func
    def get_lv1_xref(self):#获取一级外参
        lst=[]
        self.lv1_xref_name=[]
        self.lv1_xref_path=[]
        self.lv1_xref_name_path=[]
        self.get_all_xref()
        self.ModelSpace=self.doc.ModelSpace
        for i in range(self.ModelSpace.Count):
            obj=self.ModelSpace.item(i)
            if obj.ObjectName=="AcDbBlockReference":
                if obj.Name in self.a_xref_name:
                    lst.append(obj)
                    xname,xpath=obj.Name,obj.Path
                    self.lv1_xref_name.append(xname)
                    self.lv1_xref_path.append(xpath)
                    self.lv1_xref_name_path.append((xname,xpath))
        return lst

    def load(self):
        self.doc.SendCommand('(load "%s") ' % lsp_path)

    def audit(self):
        self.doc.SendCommand('(command "audit" "y") ')

    @print_func
    def close_other(self):
        self.get_doc()
        lst=[]
        docs=Autocad(create_if_not_exists=True).app.documents
        for i in range(docs.count):
            if docs[i].Name != self.name and docs[i].Name[0:7] !='Drawing':
                lst.append(docs[i].Name)
        for doc in lst:
            docs[doc].close()

    @print_func
    def xref_purge(self):
        self.load()
        self.get_all_xref()
        if self.a_xref_path:
            for path in self.a_xref_path:
                if path and path!=EmptyDwg: 
                    fpath=FindFile(path,self.path)
                    if fpath:
                        if os.path.getsize(fpath)>1000000:
                            print("purge file: " +fpath)
                            fpath=SetWrite(fpath)
                            self.purgefile(fpath)
    
    @print_func
    def purgefile(self,fpath):
        self.doc.SendCommand('(purgefile "'+fpath+'") ')

    def count0_lst(self):#获取未参照
        lst=[]
        objs=self.doc.Blocks
        for i in range(objs.Count):
            if objs.item(i).IsXRef:
                if objs.item(i).Count==0:
                    lst.append(objs.item(i))
        return lst

    @print_func
    def remove_count0(self):#拆离未参照
        lst=self.count0_lst()
        if lst:    
            for item in lst:
                self.doc.SendCommand('(command "-xref" "d" "'+item.Name+'") ')
            self.doc.SendCommand('(command "-xref" "r" "*") ')
            lst=self.count0_lst()
            return lst
        else:
            return False

    @print_func
    def remove_unload_xref(self):
        for i in range(5):
            if not self.remove_count0():
                return True
        return False

    @print_func
    def FixFile(self,path):
        fpath=FindFile(path,self.path)
        print(fpath)
        if fpath==self.path or fpath==EmptyDwg or fpath=='':
            return 1
        else:
            fpath=SetWrite(fpath)
            doc2=OpenFile(fpath)
            if doc2:
                print(doc2)
                doc2.doc.SendCommand('(command "netload" "%s") ' % RemoveProxy_dll)
                doc2.doc.SendCommand('RemoveProxy ')
                doc2.audit()
                doc2.doc.close(True)
            return 0

    @print_func
    def FixlAll(self):
        for path in self.a_xref_path:
            self.FixFile(path)
        return 0
        
    @print_func
    def bind_xref_1(self):#快速绑定
        self.load()
        self.audit()
        self.doc.SendCommand('(bind-fix) ')
        self.get_all_xref()
        if self.has_xref():
            self.result=0
        else:
            self.result=1
        return self.result

    @print_func
    def bind_xref_2(self):#逐个绑定
        self.load()
        self.audit()
        self.get_lv1_xref()
        if self.lv1_xref_name:
            self.doc.SendCommand('(command "-xref" "r" "*") ')
            for name in self.lv1_xref_name:
                self.doc.SendCommand('(command "-xref" "b" "'+name+'") ')
            self.get_all_xref()
        if self.has_xref():
            self.result=0
        else:
            self.result=2
        return self.result 

    def bind_xref_3(self,method=0):
        print('bind_xref_3')
        self.load()
        self.audit()
        self.get_lv1_xref()
        method_lst=[self.lv1_xref_path,self.a_xref_path]
        if self.has_xref():
            for path in method_lst[method]:
                self.FixFile(path)
            self.doc.SendCommand('(command "-xref" "r" "*") ')       
            self.bind_xref_1()
            if self.has_xref():
                self.bind_xref_2()
        if self.has_xref():
            self.result=0
        else:
            self.result=3
        return self.result 

    def bind_xref_4(self):#一级深度绑定
        print('bind_xref_4')
        self.load()
        self.audit()
        self.get_lv1_xref()
        if self.has_xref():
            for path in self.lv1_xref_path:
                fpath=FindFile(path,self.path)
                fpath=SetWrite(fpath)
                if fpath:
                    doc2=OpenFile(fpath)
                    if doc2:
                        print(doc2)
                        doc2.bind_xref_1()
                        if doc2.has_xref():
                            doc2.bind_xref_2()
                        if doc2.has_xref():
                            print("Can not bind xref: "+doc2.doc.Name)
                            doc2.doc.close(False)
                        else:
                            doc2.doc.close(True)
            self.doc.SendCommand('(command "-xref" "r" "*") ')       
            self.bind_xref_1()
            if self.has_xref():
                self.bind_xref_2()
        if self.has_xref():
            self.result=0
        else:
            self.result=4
        return self.result 

    def RunBind(self,try_times=1):
        while try_times>0 and self.result==0:
            try_times = try_times-1
            self.get_doc()
            print(self.name)
            self.close_other()
            self.xref_purge()
            if self.result==0:
                self.bind_xref_1()
            if self.result==0:
                self.bind_xref_2()
            if self.result==0:
                self.bind_xref_3()
            if self.result==0:
                self.bind_xref_3(method=1)
            if self.result==0:
                self.bind_xref_4()
        return self

class BindCleaner():
    
    def __init__(self,f_path,not_binded):
        self.lst=[]
        self.sorted_list=[]
        self.not_binded=not_binded
        self.f_path=f_path
    
    def clean(self,keep=10):
        self.GetFolders()
        self.sorted_list=self.BubbleSort(self.lst)
        for (ctime,f,nd) in self.sorted_list[keep:]:
            if (f,) not in self.not_binded: 
                print(f)
                os.system('rmdir /s/q "%s"' % nd)

    def BubbleSort(self,blist):
        count = len(blist)
        for i in range(0, count):
            for j in range(i + 1, count):
                if blist[i][0] > blist[j][0]:
                    blist[i], blist[j] = blist[j], blist[i]
        return blist

    def GetFolders(self):
        f_path=self.f_path
        if os.path.isdir(f_path):
            dirs=os.listdir(f_path)
            self.lst=[]
            for f in dirs:
                nd=os.path.join(f_path,f)
                if os.path.isdir(nd):
                    ctime=os.stat(nd).st_ctime
                    self.lst.append((ctime,f,nd))
            return self.lst
        else:
            return 0
        
class JSONClient(object):
    def __init__(self, HOST,PORT):
        self.socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.socket.connect((HOST,PORT))
        self.id_counter = itertools.count()

    def __del__(self):
        self.socket.close()

    def call(self, name, *params):
        request = dict(id=next(self.id_counter),params=list(params),method=name)
        self.socket.sendall(json.dumps(request).encode())
        # This must loop if resp is bigger than 4K
        response = self.socket.recv(4096)
        response = json.loads(response.decode())
        if response.get('id') != request.get('id'):
            raise Exception("expected id=%s, received id=%s: %s"
                            %(request.get('id'), response.get('id'),
                              response.get('error')))
        if response.get('error') is not None:
            raise Exception(response.get('error'))
        return response.get('result')

def FindFile(path,find_path):
    if path and find_path:
        (fpath,fname)=os.path.split(path)
        fpath=os.path.join(find_path,fname)
        if os.path.isfile(fpath):
            return fpath
        elif path[1:2]==':':
            return path
        else:
            return ""
    else:
        return ""

def SetWrite(path):
    try:
        with open(path,"r+") as fr:
            return path
    except PermissionError:
        try:
            os.chmod(path, stat.S_IWRITE)
            return path
        except:
            print("Can not SetWrite:"+path)
            return False

def OpenFile(path,open_bat='D:\\OpenFile.bat'):
    if os.path.isfile(path) and path[-4:]=='.dwg':
        print("try open :"+path)
        new_doc=Binding()
        try:
            new_doc.doc=new_doc.acad.Application.documents.open(path)
            return new_doc
        except:
            #with open(open_bat,'w') as f:
            #    f.write('"'+path+'"')
            #run_bat=os.system(open_bat) 
            run_bat=os.system('"'+path+'"') 
            for i in range(60):
                time.sleep(1)
                try:
                    new_doc.get_doc()
                    print(os.path.join(new_doc.path,new_doc.name))
                    if path.upper() == os.path.join(new_doc.path,new_doc.name).upper():
                        if os.path.isfile(open_bat):
                            os.remove(open_bat)
                        return new_doc
                except:
                    pass
        print("open file time out!")
    else:
        print("path is not a dwg file!")
    if os.path.isfile(open_bat):
        os.remove(open_bat)
    return 0

def CloseErrorReportWindow():
    title1=" AutoCAD 错误报告"
    title2="错误报告 - 已取消"
    try:
        app1=pywinauto.application.Application()
        app1.connect(title_re=title1)
        dlg1=app1.window(title_re=title1)
        dlg1.print_control_identifiers()
        try:
            dlg1.Close()
        except pywinauto.timings.TimeoutError:
            try:
                app2=pywinauto.application.Application()
                app2.connect(title_re=title2)
                dlg2=app2.window(title_re=title2)
                dlg2.print_control_identifiers()
                dlg2.Close()
                return 1
            except (pywinauto.findbestmatch.MatchError,pywinauto.findwindows.ElementNotFoundError):
                return 0
    except (pywinauto.findbestmatch.MatchError,pywinauto.findwindows.ElementNotFoundError):
        return 0
    except pywinauto.findwindows.ElementAmbiguousError:
        return 'restart'

def CheckMEM():
        try:
            if sysinfo.getSysInfo()['memFree']<600:
                bind=Binding()
                bind.get_doc()
                bind.close_other()
        except:
            pass

while 1:
	try:
		rpc = JSONClient(host,port)
		rpc_conf = rpc.call("ACADBindhelper.GetConfig","")
		arx_path,lsp_path,EmptyDwg,RemoveProxy_dll = rpc_conf["Arx_path"],rpc_conf["Lsp_path"],rpc_conf["EmptyDwg"],rpc_conf["RemoveProxy_dll"]
		break
	except:
		time.sleep(1)

if __name__=="__main__":
    main()


