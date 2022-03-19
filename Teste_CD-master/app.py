import os
from flask import Flask, request
import requests
from h11 import Data
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import os
from twilio.rest import Client

while True:

    print("ABRINDO NAVEGADOR")
    options = Options()
    options.add_argument('--headless')
    navegador = webdriver.Chrome(options=options)


    Data_hoje = date.today()
    Data = Data_hoje.strftime('%d/%m/%Y')
   


    horario = datetime.strptime('00:19:00', '%H:%M:%S').time()
    dataco = datetime.combine(Data_hoje, horario)
    print(dataco)



    parte1 = "https://appatend.brq.com/atend/relat/relat_layout_analitico_global.php?ttt=0&cp=1&l1i="
    parte2 = Data
    parte3 = "&l1f="
    parte4 = Data
    parte5 = "&t=200000"
    link = parte1 + parte2 + parte3 + parte4 + parte5


    navegador.get('https://appatend.brq.com/atend/funcionais/lg.php?e=')
            
    empresa = "coelbase"
    login = "1416"
    senha = "neo2020"
    captcha = navegador.find_element(By.XPATH, "//td[@class='text10g3 f16 strcinza']//strong[1]").text


    # INSERE OS DADOS NOS CAMPOS DE LOGIN
    navegador.find_element(By.NAME, 'SNempresa').send_keys(empresa)
    navegador.find_element(By.NAME, 'SNlogin').send_keys(login)
    navegador.find_element(By.NAME, 'S*pass').send_keys(senha)
    navegador.find_element(By.NAME, 'SNcaptcha').send_keys(captcha.replace(" ", ""))
    navegador.find_element(By.XPATH, "//input[@name='btnsalvar']").click()
    print("Logado")

    while True:
        
        navegador.get(link)
        print("CAPTURANDO HTML")
        soup = BeautifulSoup(navegador.page_source, 'lxml')
        

        
        # VERIFICANDO SE ESTAMOS LOGADOS NA PÁGINA DOS DADOS
        tables = soup.find_all('table')
        if not tables:
            sel = ("Erro")
        else :
            sel = ("Normal")



        if sel == ("Normal") :
            
            tabela = pd.read_html(str(tables), keep_default_na=False, header=0, index_col=0)
            df = tabela[2]
            print(" - INICIANDO FILTROS")

            # FILTRAR POR STATUS DE SENHA
            df_mask=(df['Situação']=='Pendente')
            filtro_df = df[df_mask]


            # FILTRO MAIOR QUE 19 MINUTOS
            filtro_df['TE'] = pd.to_datetime(filtro_df['TE'])
            filtro = filtro_df[filtro_df['TE'] >= dataco]

            # CLASSIFICAR EM DECRESCENTE
            df = filtro.sort_values(by='TE', ascending=False)
            df['TE'] = df['TE'].dt.strftime('%M')



            if (df.count().sum())>0:
                print("SERÁ NECESSÁRIO ENVIAR MENSAGEM - INICIANDO PROCEDIMENTO")

                for i in range(len(df)) :
                    municipio = df["Agência"].iloc[i]
                    tempo = df["TE"].iloc[i]
                    tempo = int(tempo)
                    tempo = (tempo + 2)

                    aviso1 = ("OLÁ, UM TÉMÁXXS FOI DETECTADO EM ")
                    aviso2 = str(municipio)
                    aviso3 = (" COM ")
                    aviso4 = str(tempo)
                    aviso5 = (" MINUTOS ")

                    aviso = aviso1 + aviso2 + aviso3 + aviso4 + aviso5
                    aviso = str(aviso)

                    mensagem1 = """
                        <Response>
                        <Say language="pt-BR">""" 
                        
                    mensagem2 ="""</Say>
                        </Response>
                        """
                    mensagem = mensagem1 + aviso + mensagem2
                    
                    account_sid = "AC17180312ebb1fffe1cbc9d85a48a77e1"
                    auth_token = "d79b36d326aad63cf000b3ebe0e1ebd5"
                    meu_numero = "+5577998622534"
                    numerofilipe = "+5577988562655"
                    numero_twilio = "+19033214282"

                    cliente = Client(account_sid, auth_token)

                    ligacao = cliente.calls.create(
                        to=meu_numero,
                        from_=numero_twilio,
                        twiml=mensagem
                    )
                    sleep(35)
                    print(aviso)
                sleep(250)

            else:

                print('NENHUMA SENHA PENDENTE - NÃO FOI NECESSÁRIO ENVIAR MENSAGEM')

        else :

            print("DESLOGADO")
            navegador.quit()
            break