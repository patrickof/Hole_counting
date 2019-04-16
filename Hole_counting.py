# -*- coding: cp1252 -*-
from functools import partial
from tkinter import * 
import numpy as np
import cv2
import copy
import sys,os,string

GREEN = (0,255,0)
RED = (0,0,255)

font = cv2.FONT_HERSHEY_SIMPLEX
aux = 0
n_furos = 0
z=0
s = True
position=[]
cabecalho = [" MICRONEEDLES   LAYERS   NUMBER OF HOLES","\n"]
text =[cabecalho]
arq =open("Data.txt","w")

#REINICIAR O PROGRAMA
def restart_program():
    python = sys.executable
    os.execl(python, python, * sys.argv)

# mouse callback function
def detect_click(event,x,y,flags,param):
    
    global position,s
        
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(im,(x,y),5,(0,0,255),-1)
        position = [x, y]
        s = False

#JANELA_QUANTIDADE_DE_DADOS
def numero_furos(num,position):

    def bt_click(arg,position):

        n = int(N_furos1.get())

        if arg == 0 and n<361:
            n+=1
            num[position] = n
        elif arg == 1 and n>0:
            n-=1
            num[position] = n
            
        N_furos.configure(text=str(n))
        N_furos1.delete(0,4)
        N_furos1.insert(0,str(n))

    def sair():
        janela.destroy()
        cv2.destroyAllWindows()
        sys.exit()
        
    def prox():
        janela.destroy()
        cv2.destroyAllWindows()
    
    def refaz():
        global z
        janela.destroy()
        cv2.destroyAllWindows()
        z-=1
        
    janela = Tk()
    janela.title('Hole counting')
    janela.geometry('200x100+1200+100')

    Total_furos = Label(janela,text='Total of holes :')
    Total_furos.pack(side = 'top')

    principal=Menu(janela)
    principal.add_command(label="Remake",command = refaz)
    principal.add_command(label="Next", command = prox)
    principal.add_command(label="Exit", command = sair)

    janela.configure(menu=principal)

    N_furos1 = Entry(janela,justify = CENTER)
    N_furos1.pack(anchor = 'center')
    N_furos1.insert(10,str(num[position]))
    
    N_furos = Label(janela, text=str(num[position]))
    N_furos.pack(anchor = 'center')

    func = Label(janela, text = ' ')
    func.pack(side = 'right')
    
    func = Label(janela, text = ' ')
    func.pack(side = 'left')
    
    acres = Button(janela,width=8, text = '(+)')
    acres['command'] = partial(bt_click,0,position)
    acres['bg'] = 'GREEN'
    acres.pack(side = 'right',anchor = 'center')

    decres = Button(janela,width=8, text = '(-)')
    decres['command'] = partial(bt_click,1,position)
    decres['bg'] = 'RED'
    decres.pack(side = 'left',anchor = 'center')

    janela.mainloop()

local_prog = os.getcwd()                    #Endereço do programa
local_agulhas= local_prog+"\\Microagulhas"  #Endereço da pasta Agulhas
pasta_agulhas = os.listdir(local_agulhas)   #Arquivos dentro da pasta Agulhas_1
data =[]
for agulha in pasta_agulhas:
    local_medidas = local_agulhas+"\\"+agulha
    pasta_medidas = os.listdir(local_medidas)
    tipos = [] ##Quarda as medidas de um tipo
    for medidas in pasta_medidas:                   #Percorre todas as camdas
        local_imagens = local_medidas+"\\"+medidas  #Endereço das fotos de cada camada
        imagens = os.listdir(local_imagens)         #Arquivos dentro de cada camada
        z=0  ##Contador para percorrer as imagens
        num = [] ##Vetor que guarda as medidas de cada imagens
        while(z<len(imagens)):
            ####Tratamento da imagem
            im = cv2.imread(local_imagens+"\\"+imagens[z])
            im_copy = copy.copy(im)
            im_gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            im_gray = cv2.medianBlur(im_gray,5) ## AJUSTAR SE NECESSÁRIO
            _,im_gray = cv2.threshold(im_gray,120,255,cv2.THRESH_BINARY) ## AJUSTAR SE NECESSÁRIO
            ####Criacao da janela
            imagem = agulha+" - "+medidas+" - "+str(z+1)+"ªLayer"
            cv2.namedWindow(imagem,cv2.WINDOW_NORMAL)
            cv2.resizeWindow(imagem, 1000, 800)
            cv2.moveWindow(imagem, 50,50)
            cv2.putText(im,'Click on the first hole on the upper-left corner',(500,100),font,2,(255,255,255),2,cv2.LINE_AA)
            cv2.setMouseCallback(imagem,detect_click) ##Função que detecta um click
            ####Loop para a janela
            while s:
                k = cv2.waitKey(1) & 0xFF

                if k == ord('a'):
                    im = im_copy
                    print('a')
                
                cv2.imshow(imagem,im)

                if k == 27 or s == 'False':
                    break
                
            cv2.destroyAllWindows()

            ###Posição para o corte
            x = position[1]-35
            y = position[0]-35

            img = im_copy[x:x+1350,y:y+1350]
            img_gray = im_gray[x:x+1350,y:y+1350]


            ## Tratamento Pré
            for y in range(0,1261,70):
                for x in range(0,1261,70): ##Inicio,Limite,Tamanho do passo
                    im_crop = img_gray[y:y+70,x:x+70]
                    fator_branco = np.mean(im_crop/255)
                    if fator_branco <0.009: ## AJUSTAR SE NECESSÁRIO
                        img= cv2.rectangle(img,(x,y),(x+65,y+65),RED,2)
                    else:
                        img= cv2.rectangle(img,(x,y),(x+65,y+65),GREEN,2)
                        n_furos+=1
                        
            #### Adiona ou modifica a quantidade de furos em um imagem
            if(len(num)<=z):
                num.append(n_furos)
            else:
                num[z]=n_furos
                
            ####Criacao da janela    
            cv2.namedWindow(imagem,cv2.WINDOW_NORMAL)
            cv2.moveWindow(imagem, 50,50)
            cv2.resizeWindow(imagem, 900, 800)
            cv2.imshow(imagem, img)

            ####Inicialização de uma label com a quantidade furos identificados
            numero_furos(num, z)

            ####Soma um ao contador 
            z+=1
            ####Destroi a janela    
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            n_furos = 0
            s = 'True'
        ##Adiona as medicoes de um tipo    
        tipos.append(num)
     ###Adicionas todas as medições de todos os tipos   
    data.append(tipos)

###AMOUNT OF TYPES###
for types in range(0,len(data)):
    linha_1 = ["		"]
    linha_2 = ["-MN ",str(types+1),"                "]
    text.append(linha_1)
    text.append(linha_2)
    max = 0
    ####MAXIMUM NUMBER OF LAYERS###
    for i in range(0,len(data[types])):
        if(len(data[types][i])>max):
            max = len(data[types][i])
    for layers in range(0,max):
        linha_3 = ["            - ",str(layers+1),"ªLAYER:"]
        text.append(linha_3)
        

###RESULTS###
for types in range(0,len(data)):
    ###Numero max de camadas de todas as medições de um tipo
    max = 0
    for i in range(0,len(data[types])):
        if(len(data[types][i])>max):
            max = len(data[types][i])
            
    total=[0]*max
    
    for measures in range(0,len(data[types])):
        text[2+aux].append("     "+str(measures+1))
        for layers in range(0,len(data[types][measures])):
            total[layers]+=data[types][measures][layers]
            numero = str(data[types][measures][layers])
            if(len(numero)<2):
                numero = "00"+numero
            elif(len(numero)<3):
                numero = "0"+numero
                
            text[3+layers+aux].append("   "+numero)

    text[2+aux].append("   TOTAL")

    for layers in range(0,len(data[types][measures])):
        t = str(total[layers])
        if(len(t)<2):
                t = "00"+t
        elif(len(t)<3):
                t = "0"+t
        text[3+layers+aux].append("   "+t)

    ###Numero max de camadas de todas as medições de um tipo    
    max = 0
    for i in range(0,len(data[types])):
        if(len(data[types][i])>max):
            max = len(data[types][i])
    aux+=(max+2)          
            
###Escreve os dados em um arquivo .txt

for linha in text:
    for palavra in linha:
        arq.write(palavra)
    arq.write("\n")



arq.close()

