
from time import sleep
import time
import sys

#---------------------------

class Loading:

#LD Loading:
    def LD (Txt=str('Loading'),A='\033[1;37m┊',Start='\033[1;31m▊',End='\033[1;37m▒',B='\033[1;37m┊',Time=0.1,Repeat=40,TextC='\033[1;37m'):
        for Num in range(0,Repeat):
            Num+=1
            Len_Txt=len (Txt)
            Number=Repeat+Len_Txt+1
            txt=End*Number
            F=Num*Start
            print (txt+B,end='\r')
            print (TextC+Txt,A+'{}'.format(F),end='\r')
            time.sleep (Time)

#DL Loading:
    def DL (Txt="\033[1;37mTxt...\033[1;34m",Time=0.1,Repeat=5):
        for x in range (Repeat):
            ss="|"
            sc="/"
            sd="-"
            sf="\\"
            time.sleep (Time)
            print (Txt+ss,end='\r')
            time.sleep (Time)
            print (Txt+sc,end='\r')
            time.sleep (Time)
            print (Txt+sd,end='\r')
            time.sleep (Time)
            print (Txt+sf,end='\r')
            time.sleep (Time)

#Counterup Loading:
    def Counterup(Txt='\033[1;31mT\033[1;32mx\033[1;33mt..',Spase=False,C='\033[1;32m',Number=10,Time=0.1,Txt2='\033[1;37m%',Repeat=5):
        for x in range (Repeat):
            for i in range (Number):
                i+=1
                number=str (i)
                time.sleep (Time)
                print (Txt+C,number+Txt2,'\r',end='\r')
                time.sleep (Time)
        if Spase ==True:
            print ()
        elif Spase == False:
             pass

#Counterdown Loading:
    def Counterdown(Txt='\033[1;31mT\033[1;32mx\033[1;33mt..',Spase=False,C='\033[1;32m',Number=10,Txt2='\033[1;37m%',Time=0.1,Repeat=1):
        for i in range (Repeat):
            for x in range (0,Number+1):
                Counter=int(Number-x)
                time.sleep (Time)
                print (Txt,Counter,Txt2,'\r',end='\r')
                time.sleep(Time)
        if Spase ==True:
           print ()
        elif Spase == False:
             pass

#---------------------------------------------

class Animation :
    def __init__(self,Txt=' \033[1;34mTxt..'):
        self.Txt=Txt

#SlowIndex Animation:
    def SlowIndex (Animation,Time=0.001):
        txt=Animation.Txt
        for x in txt:
            time.sleep (Time)
            print (x,end='')

#SlowText Animation:
    def SlowText (Animation,Time=0.1):
        for chat in Animation.Txt:
            sys. stdout.write(chat)
            sys.stdout. flush ()
            time.sleep (Time)

#Text_Line Animation:
    def Text_Line (Animation,Time=0.1,Repeat=1,CLT='\033[1;37m',CUL='\033[1;34m'):
         txt=Animation.Txt
         cs=len (txt)
         for n in range (Repeat):
             time.sleep (Time)
             print (CUL+txt[0].upper ()+CLT+txt[1::].lower(),end='\r')
             for x in range (0,cs):
                 v=x+1
                 time.sleep (Time)
                 print (CLT+txt[0:x].lower()+CUL+txt[x].upper()+CLT+txt[v::].lower(),end='\r')
                 time.sleep (Time)
                 print (CLT+txt[0:x].lower()+CUL+txt[x].upper()+CLT+txt[v::].lower(),end='\r')
                 time.sleep (Time)
             print (CLT+txt.lower(),end='\r')
             time.sleep (Time)

#---------------------------------------------
#Class D7s_Style:
#---------------
class D7s_Style:
    def __init__(self,*Txt):
       self.Txt=Txt
       for var in self.Txt:
           self.Txt=list(*Txt)
    def Style(Ds_Style,Cols=1,Taps=0,Color='\033[1;31m',Space=0,Equal=False,TxtC='\033[1;37m',Plus=''):
    #Equal False:
        if Equal == False:
            #Cols==1
            if Cols==1:
               txt=Ds_Style.Txt
               Len_Txt=len (Ds_Style.Txt)
               taps=' '*Taps
               #Style:
               for x in range (0,Len_Txt):
                   Len_List=len (txt[x])
                   sd1=str('╭');sd2=str('─')*Len_List;sd3=str('╮')
                   sd4=str(Color+'│'+TxtC)
                   sd5=str ('╰');sd6=str('╯')
                   #Print Style:
                   print (taps+Color+sd1+sd2+sd3)
                   print (taps+Color+sd4+txt[x]+Color+sd4)
                   print (taps+Color+sd5+sd2+sd6)
                   vip=str(Plus)
                   if vip =='':
                       pass
                   else:
                       print (vip)

#Equal False:
        if Equal == False:
            #Cols==2
            if Cols==2:
                Len_Txt=len (Ds_Style.Txt)
                bb=Len_Txt%2
                s7=Len_Txt-bb
                #Taps && Spase:
                tap=' '*Space
                taps=' '*Taps
                if bb%2==bb:
                    txt=Ds_Style.Txt
                    for x in range (0,s7,2):
                        #Len Txt In List:
                        Num=x+1
                        Len_List=len(txt[x])
                        Len_Next=len(txt[Num])

                  #Style:
                        ssc=str('─')*Len_List
                        ssc2=str('─')*Len_Next

                        sd1=str('╭');sd3=str('╮')
                        sd4=str(Color+'│'+TxtC)
                        sd5=str ('╰');sd6=str('╯')
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc2+sd3)
                        print (taps+Color+sd4+txt[x]+sd4+tap+sd4+txt[Num]+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc2+sd6)
                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                   #Style:
                    for i in range(bb):
                        if bb==1:
                            lk=len (txt[-1]);
                            ssc=str('─')*lk
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1]+Color+sd4)
                            print (taps+Color+sd5+ssc+sd6)
#Equal False:
        if Equal == False:
            #Cols==3:
            if Cols==3:
                Len_Txt=len (Ds_Style.Txt)
                bb=Len_Txt%3
                s7=Len_Txt-bb
                #Taps && Spase:
                tap=' '*Space
                taps=' '*Taps
                if bb%3==bb:
                    txt=Ds_Style.Txt
                    for x in range (0,s7,3):
                        #Len Txt In List:
                        Num1=x+1
                        Num2=Num1+1
                        Len_List1=len(txt[x])
                        Len_List2=len(txt[Num1])
                        Len_List3=len(txt[Num2])
                        #Style:
                        ssc=str('─')*Len_List1
                        ssc2=str('─')*Len_List2
                        ssc3=str('─')*Len_List3

                        sd1=str('╭');sd3=str('╮')
                        sd4=str(Color+'│'+TxtC)
                        sd5=str ('╰');sd6=str('╯')
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc2+sd3+tap+sd1+ssc3+sd3)
                        print (taps+Color+sd4+txt[x]+sd4+tap+sd4+txt[Num1]+sd4+tap+sd4+txt[Num2]+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc2+sd6+tap+sd5+ssc3+sd6)

                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                    for i in range(bb):
                        if bb==1:
                            #Len Txt In List:
                            Len_Txt=len (txt[-1])
                            ssc=str('─')*Len_Txt
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1]+sd4)
                            print (taps+Color+sd5+ssc+sd6)

                        if bb==2:
                            #Len Txt In List:
                            Len_Txt=len (txt[-2])
                            Len_Txt2=len (txt[-1])
                            #Style:
                            ssc=str('─')*Len_Txt
                            ssc2=str('─')*Len_Txt2
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc2+sd3)
                            print (taps+Color+sd4+txt[-2]+sd4+tap+sd4+txt[-1]+sd4)
                            print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc2+sd6)
                            break

#Equal True:
        if Equal ==True:
            #Cols==1
            if Cols==1:
               txt=Ds_Style.Txt
               Len_Txt=len(txt)
               #sv ===Len_Txt
               max1=0 ;num=0
               for x in range (0,Len_Txt):
                   num=len(txt[x])
                   if num > max1:
                      max1 = num

               Num=max1+2
               for n in range (0,Len_Txt):
                   #Len Txt && Taps:
                   taps=' '*Taps
                   Len_List=len(txt[n])
                   smm=Num-Len_List+Len_List
                   #Style:
                   ssc=str('─')*Num
                   sd1=str('╭');sd3=str('╮')
                   sd4=str(Color+'│'+TxtC)
                   sd5=str ('╰');sd6=str('╯')
                   #Print Style:
                   print (taps+Color+sd1+ssc+sd3)
                   print (taps+Color+sd4+txt[n].center(smm)+sd4)
                   print (taps+Color+sd5+ssc+sd6)

                   vip=str(Plus)
                   if vip =='':
                       pass
                   else:
                       print (vip)

#Equal True:
        if Equal ==True:
            #Cols ==2
            if Cols ==2:
                Number=len (Ds_Style.Txt)
                bb=Number%2
                s7=Number-bb
                if bb%2==bb:
                    txt=Ds_Style.Txt
                    Len_Txt=len (Ds_Style.Txt)
                    max1=0 ;num=0

                    for n in range (0,Len_Txt):
                        num=len(txt[n])
                        if num > max1:
                            max1 = num

                    ss=max1+2
                    bg=max1
                    for x in range (0,s7,2):
                        tap=' '*Space
                        taps=' '*Taps
                        VR2=x+1
                        #Len Txt In List:
                        Len_List=len(txt[x])
                        VR=ss-Len_List+Len_List
                        Len_List2=len(txt[VR2])
                        VR3=ss-Len_List2+Len_List2
                        #Style:
                        ssc=str('─')*ss
                        sd1=str('╭');sd3=str('╮')
                        sd4=str(Color+'│'+TxtC)
                        sd5=str ('╰');sd6=str('╯')
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                        print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[VR2].center(VR3)+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                    for i in range(bb):
                        if bb==1:
                            #Len Txt In List:
                            Len_txt=len (txt[-1])
                            Number=ss-Len_txt+Len_txt
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1].center(Number)+sd4)
                            print (taps+Color+sd5+ssc+sd6)
#Equal True:
        if Equal ==True:
            #Cols==3:
            if Cols ==3:
                Len_Text=len (Ds_Style.Txt)
                Number=Len_Text%3
                s7=Len_Text-Number

                if Number%3==Number:
                    txt=Ds_Style.Txt
                    Len_Txt=len (Ds_Style.Txt)
                    max1=0 ;num=0
                    for n in range (0,Len_Text):
                        num=len(txt[n])
                        if num > max1:
                            max1 = num
                    ss=max1+2
                    for x in range (0,s7,3):
                        tap=' '*Space
                        taps=' '*Taps

                        CR=x+1
                        CR2=x+2
                        #Len Txt in List:
                        Len_List=len(txt[x])
                        Len_List2=len(txt[CR])
                        Len_List3=len (txt[CR2])
                        ##
                        VR=ss-Len_List+Len_List
                        VR2=ss-Len_List2+Len_List2
                        VR3=ss-Len_List3+Len_List3

                        #Style:
                        ssc=str('─')*ss
                        sd1=str('╭');sd3=str('╮')
                        sd4=str(Color+'│'+TxtC)
                        sd5=str ('╰');sd6=str('╯')
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                        print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[CR].center(VR2)+sd4+tap+sd4+txt[CR2].center(VR3)+sd4);
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                    for i in range(Number):
                        if Number==1:
                            #Len Txt In List:
                            Len_List=len (txt[-1])
                            Num=ss-Len_List+Len_List
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1].center(Num)+sd4)
                            print (taps+Color+sd5+ssc+sd6)

                        if Number==2:
                            #Len Txt In List:
                            Len_List=len (txt[-2])
                            Len_List2=len (txt[-1])
                            Num=ss-Len_List+Len_List
                            CR=ss-Len_List2+Len_List2
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-2].center(Num)+Color+sd4+tap+sd4+txt[-1].center(CR)+sd4)
                            print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                            break
##Center Style:
    def Center (Ds_Style,Cols=3,Taps=0,Color='\033[1;31m',Space=0,TxtC='\033[1;37m',Plus=''):
        #Cols ==2:
        if Cols==2:
            Len_Text=len (Ds_Style.Txt)
            bb=Len_Text%2
            s7=Len_Text-bb
            if bb%2==bb:
                txt=Ds_Style.Txt
                Len_Txt=len (Ds_Style.Txt)
                max1=0 ;num=0
                for n in range (0,Len_Txt):
                    num=len(txt[n])
                    if num > max1:
                        max1 = num
                hh=max1
                if hh == hh:
                    ss=max1+2
                for x in range (0,s7,2):
                    tap=' '*Space
                    taps=' '*Taps
                    CR=x+1
                    #Len Txt In List:
                    Len_List=len(txt[x])
                    Len_List2=len(txt[CR])
                    VR=ss-Len_List+Len_List
                    VR2=ss-Len_List2+Len_List2
                    #Style:
                    ssc=str('─')*ss
                    sd1=str('╭');sd3=str('╮')
                    sd4=str(Color+'│'+TxtC)
                    sd5=str ('╰');sd6=str('╯')
                    #Print Style:
                    print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                    print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[CR].center(VR2)+sd4)
                    print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)

                    vip=str(Plus)
                    if vip =='':
                        pass
                    else:
                        print (vip)

                for i in range(bb):
                    if bb==1:
                        Len_List=len (txt[-1])
                        VR=ss-Len_List+Len_List
                        pp=max1//2
                        Sc=Space//2
                        Md=max1-pp+Sc+2
                        Mc=str(' ')*Md
                        print (taps+Color+Mc+sd1+ssc+sd3)
                        print (taps+Color+Mc+sd4+txt[-1].center(VR)+sd4)
                        print (taps+Color+Mc+sd5+ssc+sd6)

        #Cols==3:
        if Cols==3:
             Len_Text=len (Ds_Style.Txt)
             bb=Len_Text%3
             s7=Len_Text-bb
             if bb%3==bb:
                 txt=Ds_Style.Txt
                 Len_Txt=len (Ds_Style.Txt)
                 max1=0 ;num=0

                 for n in range (0,Len_Txt):
                     num=len(txt[n])
                     if num > max1:
                         max1 = num

                 ss=max1+2
                 for x in range (0,s7,3):
                     tap=' '*Space
                     taps=' '*Taps
                     CR=x+1
                     CR2=x+2
                     #Len Txt in List:
                     Len_List=len(txt[x])
                     Len_List2=len(txt[CR])
                     Len_List3=len (txt[CR2])
                     #VR Spase Center
                     VR=ss-Len_List+Len_List
                     VR2=ss-Len_List2+Len_List2
                     VR3=ss-Len_List3+Len_List3
                     #Style:
                     ssc=str('─')*ss
                     sd1=str('╭');sd3=str('╮')
                     sd4=str(Color+'│'+TxtC)
                     sd5=str ('╰');sd6=str('╯')
                     #Print Style:
                     print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                     print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[CR].center(VR2)+sd4+tap+sd4+txt[CR2].center(VR3)+sd4)
                     print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                     vip=str(Plus)
                     if vip =='':
                         pass
                     else:
                         print (vip)


                 for i in range(bb):
                     if bb==1:
                        #Len Txt In List:
                        Len_List=len (txt[-1])
                        VR=ss-Len_List+Len_List
                        Num=max1+4+Space
                        Mc=' '*Num
                        #Print Style:
                        print (taps+Color+Mc+sd1+ssc+sd3)
                        print (taps+Color+Mc+sd4+txt[-1].center(VR)+sd4)
                        print (taps+Color+Mc+sd5+ssc+sd6)

                     if bb==2:
                        # Len Txt In List:
                        Len_List=len (txt[-2])
                        Len_List2=len (txt[-1])
                        ##VR
                        VR=ss-Len_List+Len_List
                        VR2=ss-Len_List2+Len_List2
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                        print (taps+Color+sd4+txt[-2].center(VR)+sd4+tap+sd4+txt[-1].center(VR2)+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                        break

#---------------------------------------------
# Class My_Style:
#----------------
class My_Style:
    def __init__(self,*Txt):
        self.Txt=Txt
        for x in Txt:
            self.Txt=list(*Txt)

#Square My_Style:
    def Style(My_Style,Cols=2,Color='\033[1;31m',TxtC='\033[1;37m',Taps=0,Space=0,Equal=False,Plus='',Ds1='╭',
        Ds2='─',Ds3='╮',Ds4='│',Ds5='╰',Ds6='╯'):
#Equal False:
        if Equal == False:
            #Cols==1
            if Cols==1:
               txt=My_Style.Txt
               Len_Txt=len (My_Style.Txt)
               taps=' '*Taps
               #Style:
               for x in range (0,Len_Txt):
                   Len_List=len (txt[x])
                   sd1=str(Ds1);sd2=str(Ds2)*Len_List;sd3=str(Ds3)
                   sd4=str(Color+Ds4+TxtC)
                   sd5=str (Ds5);sd6=str(Ds6)
                   #Print Style:
                   print (taps+Color+sd1+sd2+sd3)
                   print (taps+Color+sd4+txt[x]+Color+sd4)
                   print (taps+Color+sd5+sd2+sd6)
                   vip=str(Plus)
                   if vip =='':
                       pass
                   else:
                       print (vip)

#Equal False:
        if Equal == False:
            #Cols==2
            if Cols==2:
                Len_Txt=len (My_Style.Txt)
                bb=Len_Txt%2
                s7=Len_Txt-bb
                #Taps && Spase:
                tap=' '*Space
                taps=' '*Taps
                if bb%2==bb:
                    txt=My_Style.Txt
                    for x in range (0,s7,2):
                        #Len Txt In List:
                        Num=x+1
                        Len_List=len(txt[x])
                        Len_Next=len(txt[Num])

                  #Style:
                        ssc=str(Ds2)*Len_List
                        ssc2=str(Ds2)*Len_Next

                        sd1=str(Ds1);sd3=str(Ds3)
                        sd4=str(Color+Ds4+TxtC)
                        sd5=str (Ds5);sd6=str(Ds6)
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc2+sd3)
                        print (taps+Color+sd4+txt[x]+sd4+tap+sd4+txt[Num]+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc2+sd6)
                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                   #Style:
                    for i in range(bb):
                        if bb==1:
                            lk=len (txt[-1]);
                            ssc=str(Ds2)*lk
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1]+Color+sd4)
                            print (taps+Color+sd5+ssc+sd6)
#Equal False:
        if Equal == False:
            #Cols==3:
            if Cols==3:
                Len_Txt=len (My_Style.Txt)
                bb=Len_Txt%3
                s7=Len_Txt-bb
                #Taps && Spase:
                tap=' '*Space
                taps=' '*Taps
                if bb%3==bb:
                    txt=My_Style.Txt
                    for x in range (0,s7,3):
                        #Len Txt In List:
                        Num1=x+1
                        Num2=Num1+1
                        Len_List1=len(txt[x])
                        Len_List2=len(txt[Num1])
                        Len_List3=len(txt[Num2])
                        #Style:
                        ssc=str(Ds2)*Len_List1
                        ssc2=str(Ds2)*Len_List2
                        ssc3=str(Ds2)*Len_List3

                        sd1=str(Ds1);sd3=str(Ds3)
                        sd4=str(Color+Ds4+TxtC)
                        sd5=str (Ds5);sd6=str(Ds6)
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc2+sd3+tap+sd1+ssc3+sd3)
                        print (taps+Color+sd4+txt[x]+sd4+tap+sd4+txt[Num1]+sd4+tap+sd4+txt[Num2]+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc2+sd6+tap+sd5+ssc3+sd6)

                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                    for i in range(bb):
                        if bb==1:
                            #Len Txt In List:
                            Len_Txt=len (txt[-1])
                            ssc=str(Ds2)*Len_Txt
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1]+sd4)
                            print (taps+Color+sd5+ssc+sd6)

                        if bb==2:
                            #Len Txt In List:
                            Len_Txt=len (txt[-2])
                            Len_Txt2=len (txt[-1])
                            #Style:
                            ssc=str(Ds2)*Len_Txt
                            ssc2=str(Ds2)*Len_Txt2
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc2+sd3)
                            print (taps+Color+sd4+txt[-2]+sd4+tap+sd4+txt[-1]+sd4)
                            print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc2+sd6)
                            break

#Equal True:
        if Equal ==True:
            #Cols==1
            if Cols==1:
               txt=My_Style.Txt
               Len_Txt=len(txt)
               #sv ===Len_Txt
               max1=0 ;num=0
               for x in range (0,Len_Txt):
                   num=len(txt[x])
                   if num > max1:
                      max1 = num

               Num=max1+2
               for n in range (0,Len_Txt):
                   #Len Txt && Taps:
                   taps=' '*Taps
                   Len_List=len(txt[n])
                   smm=Num-Len_List+Len_List
                   #Style:
                   ssc=str(Ds2)*Num
                   sd1=str(Ds1);sd3=str(Ds3)
                   sd4=str(Color+Ds4+TxtC)
                   sd5=str (Ds5);sd6=str(Ds6)
                   #Print Style:
                   print (taps+Color+sd1+ssc+sd3)
                   print (taps+Color+sd4+txt[n].center(smm)+sd4)
                   print (taps+Color+sd5+ssc+sd6)

                   vip=str(Plus)
                   if vip =='':
                       pass
                   else:
                       print (vip)

#Equal True:
        if Equal ==True:
            #Cols ==2
            if Cols ==2:
                Number=len (My_Style.Txt)
                bb=Number%2
                s7=Number-bb
                if bb%2==bb:
                    txt=My_Style.Txt
                    Len_Txt=len (My_Style.Txt)
                    max1=0 ;num=0

                    for n in range (0,Len_Txt):
                        num=len(txt[n])
                        if num > max1:
                            max1 = num

                    ss=max1+2
                    bg=max1
                    for x in range (0,s7,2):
                        tap=' '*Space
                        taps=' '*Taps
                        VR2=x+1
                        #Len Txt In List:
                        Len_List=len(txt[x])
                        VR=ss-Len_List+Len_List
                        Len_List2=len(txt[VR2])
                        VR3=ss-Len_List2+Len_List2
                        #Style:
                        ssc=str(Ds2)*ss
                        sd1=str(Ds1);sd3=str(Ds3)
                        sd4=str(Color+Ds4+TxtC)
                        sd5=str (Ds5);sd6=str(Ds6)
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                        print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[VR2].center(VR3)+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                    for i in range(bb):
                        if bb==1:
                            #Len Txt In List:
                            Len_txt=len (txt[-1])
                            Number=ss-Len_txt+Len_txt
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1].center(Number)+sd4)
                            print (taps+Color+sd5+ssc+sd6)
#Equal True:
        if Equal ==True:
            #Cols==3:
            if Cols ==3:
                Len_Text=len (My_Style.Txt)
                Number=Len_Text%3
                s7=Len_Text-Number

                if Number%3==Number:
                    txt=My_Style.Txt
                    Len_Txt=len (My_Style.Txt)
                    max1=0 ;num=0
                    for n in range (0,Len_Text):
                        num=len(txt[n])
                        if num > max1:
                            max1 = num
                    ss=max1+2
                    for x in range (0,s7,3):
                        tap=' '*Space
                        taps=' '*Taps

                        CR=x+1
                        CR2=x+2
                        #Len Txt in List:
                        Len_List=len(txt[x])
                        Len_List2=len(txt[CR])
                        Len_List3=len (txt[CR2])
                        ##
                        VR=ss-Len_List+Len_List
                        VR2=ss-Len_List2+Len_List2
                        VR3=ss-Len_List3+Len_List3

                        #Style:
                        ssc=str(Ds2)*ss
                        sd1=str(Ds1);sd3=str(Ds3)
                        sd4=str(Color+Ds4+TxtC)
                        sd5=str (Ds5);sd6=str(Ds6)
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                        print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[CR].center(VR2)+sd4+tap+sd4+txt[CR2].center(VR3)+sd4);
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                        vip=str(Plus)
                        if vip =='':
                            pass
                        else:
                            print (vip)

                    for i in range(Number):
                        if Number==1:
                            #Len Txt In List:
                            Len_List=len (txt[-1])
                            Num=ss-Len_List+Len_List
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-1].center(Num)+sd4)
                            print (taps+Color+sd5+ssc+sd6)

                        if Number==2:
                            #Len Txt In List:
                            Len_List=len (txt[-2])
                            Len_List2=len (txt[-1])
                            Num=ss-Len_List+Len_List
                            CR=ss-Len_List2+Len_List2
                            #Print Style:
                            print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                            print (taps+Color+sd4+txt[-2].center(Num)+Color+sd4+tap+sd4+txt[-1].center(CR)+sd4)
                            print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                            break
##Center Style:
    def Center (My_Style,Cols=3,Taps=0,Color='\033[1;31m',Space=0,Plus='',TxtC='\033[1;37m',Ds1='╭',Ds2='─',Ds3='╮',Ds4='│',Ds5='╰',Ds6='╯'):
        #Cols ==2:
        if Cols==2:
            Len_Text=len (My_Style.Txt)
            bb=Len_Text%2
            s7=Len_Text-bb
            if bb%2==bb:
                txt=My_Style.Txt
                Len_Txt=len (My_Style.Txt)
                max1=0 ;num=0
                for n in range (0,Len_Txt):
                    num=len(txt[n])
                    if num > max1:
                        max1 = num
                hh=max1
                if hh == hh:
                    ss=max1+2
                for x in range (0,s7,2):
                    tap=' '*Space
                    taps=' '*Taps
                    CR=x+1
                    #Len Txt In List:
                    Len_List=len(txt[x])
                    Len_List2=len(txt[CR])
                    VR=ss-Len_List+Len_List
                    VR2=ss-Len_List2+Len_List2
                    #Style:
                    ssc=str(Ds2)*ss
                    sd1=str(Ds1);sd3=str(Ds3)
                    sd4=str(Color+Ds4+TxtC)
                    sd5=str (Ds5);sd6=str(Ds6)
                    #Print Style:
                    print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                    print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[CR].center(VR2)+sd4)
                    print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)

                    vip=str(Plus)
                    if vip =='':
                        pass
                    else:
                        print (vip)

                for i in range(bb):
                    if bb==1:
                        Len_List=len (txt[-1])
                        VR=ss-Len_List+Len_List
                        pp=max1//2
                        Sc=Space//2
                        Md=max1-pp+Sc+2
                        Mc=str(' ')*Md
                        print (taps+Color+Mc+sd1+ssc+sd3)
                        print (taps+Color+Mc+sd4+txt[-1].center(VR)+sd4)
                        print (taps+Color+Mc+sd5+ssc+sd6)

        #Cols==3:
        if Cols==3:
             Len_Text=len (My_Style.Txt)
             bb=Len_Text%3
             s7=Len_Text-bb
             if bb%3==bb:
                 txt=My_Style.Txt
                 Len_Txt=len (My_Style.Txt)
                 max1=0 ;num=0

                 for n in range (0,Len_Txt):
                     num=len(txt[n])
                     if num > max1:
                         max1 = num

                 ss=max1+2
                 for x in range (0,s7,3):
                     tap=' '*Space
                     taps=' '*Taps
                     CR=x+1
                     CR2=x+2
                     #Len Txt in List:
                     Len_List=len(txt[x])
                     Len_List2=len(txt[CR])
                     Len_List3=len (txt[CR2])
                     #VR Spase Center
                     VR=ss-Len_List+Len_List
                     VR2=ss-Len_List2+Len_List2
                     VR3=ss-Len_List3+Len_List3
                     #Style:
                     ssc=str(Ds2)*ss
                     sd1=str(Ds1);sd3=str(Ds3)
                     sd4=str(Color+Ds4+TxtC)
                     sd5=str (Ds5);sd6=str(Ds6)
                     #Print Style:
                     print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                     print (taps+Color+sd4+txt[x].center(VR)+sd4+tap+sd4+txt[CR].center(VR2)+sd4+tap+sd4+txt[CR2].center(VR3)+sd4)
                     print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                     vip=str(Plus)
                     if vip =='':
                         pass
                     else:
                         print (vip)


                 for i in range(bb):
                     if bb==1:
                        #Len Txt In List:
                        Len_List=len (txt[-1])
                        VR=ss-Len_List+Len_List
                        Num=max1+4+Space
                        Mc=' '*Num
                        #Print Style:
                        print (taps+Color+Mc+sd1+ssc+sd3)
                        print (taps+Color+Mc+sd4+txt[-1].center(VR)+sd4)
                        print (taps+Color+Mc+sd5+ssc+sd6)

                     if bb==2:
                        # Len Txt In List:
                        Len_List=len (txt[-2])
                        Len_List2=len (txt[-1])
                        ##VR
                        VR=ss-Len_List+Len_List
                        VR2=ss-Len_List2+Len_List2
                        #Print Style:
                        print (taps+Color+sd1+ssc+sd3+tap+sd1+ssc+sd3)
                        print (taps+Color+sd4+txt[-2].center(VR)+sd4+tap+sd4+txt[-1].center(VR2)+sd4)
                        print (taps+Color+sd5+ssc+sd6+tap+sd5+ssc+sd6)
                        break

#---------------------------------------------
#This Library Is A Gift Form The "DARK7STORM"
#---------------------------------------------
