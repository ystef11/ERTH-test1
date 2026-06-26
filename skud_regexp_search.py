import os
import re
import sys
import chardet
import datetime
import xlwt

path='d:/Downloads/4'

class rObj:
    def __init__(self):
        self.errors = {}
        self.ci = 1
        self.book = xlwt.Workbook(encoding="utf-8")
        self.sheet=self.book.add_sheet('res')
        self.sheet.write(0, 0, "ФИО") 
        self.sheet.write(0, 1, "Дата") 
        self.sheet.write(0, 2, "Интервал")
        self.sheet.write(0, 3, "Рабочее время")
        self.sheet.write(0, 4, "Интервалы")
    
    def get_obj_list(self, dir):
        if not os.path.isdir(dir):
            self.get_obj_one(dir)
        for i in os.listdir(dir):
            if i == 'notused': continue
            if os.path.isdir(dir + '/' + i):
                self.get_obj_list(dir + '/' + i)
            else:
                self.get_obj_one(dir + '/' + i)

    def get_obj_one(self, fn):
        if os.path.isdir(fn):
            self.get_obj_list(fn)
        else:
            if '.csv' not in fn: return
            #print(fn)
            with open(fn, 'rb') as f:
                encoding = chardet.detect(f.read()).get("encoding")
            # print(encoding)
            try:
                f = open(fn, encoding=encoding).read()
            except Exception as ex:
                self.err('codec', fn, ex)
            self.get_regex(fn, f)

    def get_regex(self, fn, f):
        tn = ['']
        try:
            tn = re.findall('(\d{2}\.\d{2}\.\d{4} \d{1,2}:\d{2}:\d{2});.*Проход.*(Вход|Выход).*[\r\n]', f, re.IGNORECASE)
        except:
            pass
        # print(tn)
        if len(tn) > 0:
            print('    ',fn)
            self.check_time(fn,tn)

    def err(self, t, fn, er):
        # print('---',t,fn,er)
        # er.startswith('risk.') or \
        # er.startswith('analytics.') or \
        if t not in self.errors:
            self.errors[t] = {}
        if fn not in self.errors[t]:
            self.errors[t][fn] = []
        if er not in self.errors[t][fn]:
            self.errors[t][fn].append(er)
            
    def check_time(self,fn,tn):
        db={}
        for i in tn:
            dt = datetime.datetime.strptime(i[0], '%d.%m.%Y %H:%M:%S')
            day=dt.strftime("%Y/%m/%d")
            if day not in db:
                db[day]=[dt,dt,datetime.timedelta(0),dt,0,[]]
                # вход, выход, время, последний вход, статус
                # заполняем вход, если сначала был выход
            if i[1]=='Вход':
                db[day][4]=1
                db[day][3]=dt
            if i[1]=='Выход':
                if dt>db[day][1]:
                    db[day][1]=dt
                if db[day][4]==1 and dt>db[day][3]:
                    db[day][2]+=dt-db[day][3]
                    db[day][5].append('%s-%s'%(db[day][3].strftime("%H:%M"),dt.strftime("%H:%M")))
                db[day][4]=0
        i2=0
        for i in db:
            print(i,'%s-%s'%(db[i][0].strftime("%H:%M"),db[i][1].strftime("%H:%M")),"%.2f" % (db[i][2].seconds/3600),db[i][5])
            self.sheet.write(self.ci, 0, fn.split('/')[-1].split('.')[0]) 
            self.sheet.write(self.ci, 1, i) 
            self.sheet.write(self.ci, 2, '%s-%s'%(db[i][0].strftime("%H:%M"),db[i][1].strftime("%H:%M")))
            self.sheet.write(self.ci, 3, "%.2f" % (db[i][2].seconds/3600))
            self.sheet.write(self.ci, 4, ','.join(db[i][5]))
            self.ci += 1

if __name__ == '__main__':
    obj = rObj()
    obj.get_obj_list(path)
    obj.book.save(path+"/res.xls")