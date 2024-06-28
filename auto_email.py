
from cryptography.fernet import Fernet
from datetime import datetime
import flet as ft
import base64
import time
import json
import sys
import ast
import os
import re
import appdirs

from task_schedule import Task
from create_email import Email

status_timer = True
status_dados_agendamento = False
status_dados_email = False
status_exec= False
status_encerramento = False
status_envio = True

dados_tarefa={}
listaTarefas = []
arquivos = []
dias = []
out_dados = []
contador_tarefas = 1
tarefaSelecionada = f'Tarefa {contador_tarefas}'

chave = 'ykJZbqQFa7RJUoUbIqh0VqaFCHLzYJ9wo6ZbxjapOGw='


def encrypt_data(data, key):
    cipher_suite = Fernet(key)
    encrypted_data = cipher_suite.encrypt(json.dumps(data).encode())
    return encrypted_data

def decrypt_data(encrypted_data, key):
    cipher_suite = Fernet(key)
    decrypted_data = json.loads(cipher_suite.decrypt(encrypted_data).decode())
    return decrypted_data

def save_encrypted_data(data, key, filename):
    print(json.dumps(data, indent=4))
    encrypted_data = encrypt_data(data, key)
    # Converta os dados criptografados para base64
    encoded_data = base64.b64encode(encrypted_data)
    with open(filename, 'wb') as file:
        file.write(encoded_data)

def load_encrypted_data(key, filename):
    with open(filename, 'rb') as file:
        # Decode de volta para bytes antes de decifrar
        encoded_data = base64.b64decode(file.read())
    decrypted_data = decrypt_data(encoded_data, key)
    #print(json.dumps(decrypted_data, indent=4))
    return decrypted_data

def main(page: ft.Page):
    page.title = "AutoEmail"
    page.window_center()
    page.window_width = 500
    page.window_height = 940  
    page.window_min_width = 500   
    page.window_min_height = 720
    page.window_resizable = True 
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.theme_mode = ft.ThemeMode.DARK
    chave_usuario = Fernet.generate_key()
    page.window_prevent_close = True
   
    caminho_execucao = os.getcwd()
    caminho_dados = appdirs.user_data_dir(appname='AutoEmail')
    print('caminho',caminho_dados)
    os.makedirs(caminho_dados, exist_ok=True)
    #caminho_execucao = os.path.dirname(os.path.abspath(__file__))

    def window_event(e):
        if e.data == "close":
            page.dialog = confirm_dialog
            confirm_dialog.open = True
            page.update()
            
    page.on_window_event = window_event

    def yes_click(e):
        page.window_destroy()

    def no_click(e):
        confirm_dialog.open = False
        page.update()

    def theme_changed(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            bnt_tema.icon = ft.icons.DARK_MODE_OUTLINED
            bnt_tema.tooltip = 'Modo Escuro'
        else:
            page.theme_mode = ft.ThemeMode.DARK
            bnt_tema.icon = ft.icons.LIGHT_MODE_OUTLINED
            bnt_tema.tooltip = 'Modo Claro'
        bnt_tema.update()
        page.update()

    def set_tema(tema):
        if tema.find('LIGHT') >=0 and page.theme_mode == ft.ThemeMode.DARK:
            theme_changed(None)

        if tema.find('DARK') >=0 and page.theme_mode == ft.ThemeMode.LIGHT:
            theme_changed(None)
          
    def pick_files_result(e: ft.FilePickerResultEvent):
        arquivos.clear()
        files.current.controls.clear()
        if e.files is not None:            
            for f in e.files:
                arquivos.append([f.name, f.path])
                files.current.controls.append(
                    ft.Row(
                        [   
                            ft.Icon(
                                name = ft.icons.CHECK_OUTLINED,
                                size=10,
                                color=ft.colors.GREEN_400
                            ),
                            ft.Text(
                                f.name,
                                size= 10,
                                italic= True
                            ),
                        ]
                    )
                ) 

        page.update()
    
    def restaura_arquivos_salvos(lista_arquivos):
       
        files.current.controls.clear()
        if lista_arquivos is not None:   
            for f in lista_arquivos:
                arquivos.append(f)
                files.current.controls.append(
                    ft.Row(
                        [   
                            ft.Icon(
                                name = ft.icons.CHECK_OUTLINED,
                                size=10,
                                color=ft.colors.GREEN_400
                            ),
                            ft.Text(
                                f[0],
                                size = 10,
                                italic = True
                            ),
                        ]
                    )
                )
        page.update()

    def atualiza_texto_assunto(e):
        try: 

            in_assunto.error_text = ''
            in_assunto.update()
            out_assunto.value = ''
            if in_assunto.value.find('/data') >= 0:
                out_assunto.value = in_assunto.value.replace("/data", f"{datetime.now().strftime('%d/%m')}")
            else:
                out_assunto.value = in_assunto.value
            out_assunto.update()
        except: None

    def radiogroup_changed(e):
        if cg.value == '1':
            in_email.suffix_text = "@legalcontrol.com.br"
        if cg.value == '2':
            in_email.suffix_text = "@outlook.com"
        if cg.value == '3':
            in_email.suffix_text = "@gmail.com"
        if cg.value == '4':
            in_email.suffix_text = ""
        in_email.hint_text = 'user.example'
        in_email.focus()
        in_email.update()

    def radiogroup2_changed(e):
        if in_tipo_text.value == '2':
            in_texto.icon = ft.icons.HTML_OUTLINED
            in_texto.focus()
            in_texto.value = f'''<html>\n\t<body>\n\t\t<p style="font-size: 9px; color: rgba(255, 0, 0, 0.5);">\n\t\t\tE-mail enviado automaticamente.\n\t\t</p>\n\t</body>\n</html>\n'''
        else:
            in_texto.icon = ft.icons.TEXT_FIELDS
            in_texto.value = ''
            in_texto.focus()
        in_texto.update()
           
    def open_dlg_modal_confima(e):
        global status_encerramento
        status_encerramento = False
        if verifica_campos_email():

            page.dialog = out_alerta_confirma
            out_alerta_confirma.open = True
            texto_envio_tarefa.value = "Enviando..."

        page.update()

    def open_dlg_modal_confima_tarefa(e):
        page.dialog = out_alerta_confirma_tarefa
        out_alerta_confirma_tarefa.open = True
        page.update()
    
    def verifica_dados(e):
        global status_dados_email
        global status_dados_agendamento

        status_dados_email = verifica_campos_email()
            
        if status_dados_email and status_dados_agendamento:
            page.dialog = out_alerta_confirma_salvamento
            out_alerta_confirma_salvamento.open = True
        else:
            if not status_dados_email:
                
                page.dialog = out_alerta_dados_incorretos
                out_alerta_dados_incorretos.open = True

            elif not status_dados_agendamento:
                text_alerta_dados.value = "É necessario agendar uma tarefa!" 
                page.dialog = out_alerta_dados_incorretos
                out_alerta_dados_incorretos.open = True

        page.update()
    
    def open_dlg_modal_salvar(e):
        page.dialog = dlg_modal_salvar
        dlg_modal_salvar.open = True
        page.update()    

    def open_dlg_alerta_envio(e):
        global status_timer
        global status_envio

        status_timer = True
        progresso.color = None
        page.dialog = alerta_envio_tarefa
        alerta_envio_tarefa.open = True
        page.update()
        
        cor_fim = (17, 212, 23)  # Verde (R, G, B)
        cor_inicio = (255, 0, 0)  # Vermelho (R, G, B)
        if in_atraso.value == '': in_atraso.value = 1

        if in_tipo_exec.value == '1':
            alerta_envio_tarefa.modal = False
            texto_envio_tarefa.value = 'Enviando...'
            icon_envio_tarefa.name = ft.icons.SCHEDULE_SEND
            alerta_envio_tarefa.modal = False
            bnt_confirmar_envio.visible = False
            bnt_cancelar_envio.visible = True
            page.update()
            time.sleep(5)
            if status_envio:
                envia_email(None)

        elif in_tipo_exec.value == '2':
            icon_envio_tarefa.name = ft.icons.QUESTION_MARK
            texto_envio_tarefa.value = 'Aguardando confirmação...'
            bnt_confirmar_envio.visible = True
            bnt_cancelar_envio.visible = True
            page.update()

        elif in_tipo_exec.value == '3':
            bnt_confirmar_envio.visible = False
            bnt_cancelar_envio.visible = True
            progresso.visible = True
            icon_envio_tarefa.name = ft.icons.ACCESS_TIME_OUTLINED
            total_minutos = int(in_atraso.value)
            total_segundos = total_minutos * 60
            total_ring = total_segundos
            while  total_segundos >=  0:
                if (not status_envio) or (not status_timer):
                    break
                #tempo_inicio = time.time()
                minutos, segundos = divmod(total_segundos, 60)
                texto_envio_tarefa.value = f'Enviando em:  {minutos:02d}:{segundos:02d}'
                porcentagem = ((100/total_ring )* total_segundos)*0.01
                progresso.value = porcentagem

                total_segundos -= 1


                limiar = 1
                if total_segundos/total_ring < limiar: # 50% do progresso
                    cor_intermediaria = (
                        int(cor_inicio[0] + (porcentagem/limiar) * (cor_fim[0] - cor_inicio[0])),
                        int(cor_inicio[1] + (porcentagem/limiar) * (cor_fim[1] - cor_inicio[1])),
                        int(cor_inicio[2] + (porcentagem/limiar) * (cor_fim[2] - cor_inicio[2])),
                    )
                    progresso.color = "#{:02X}{:02X}{:02X}".format(*cor_intermediaria)
                page.update()
                #print(time.time()-tempo_inicio )
                time.sleep(0.9965)
            else:
                alerta_envio_tarefa.modal = False
                progresso.color = None
                page.update()
                time.sleep(2)
                if status_envio:
                    envia_email(None)

        elif in_tipo_exec.value == '4' :
            
            bnt_confirmar_envio.visible = True
            bnt_cancelar_envio.visible = True
            progresso.visible = True

            icon_envio_tarefa.name = ft.icons.ACCESS_TIME_OUTLINED
            total_minutos = int(in_atraso.value)
            total_segundos = total_minutos * 60
            total_ring = total_segundos

            while  total_segundos >= 0:
                if (not status_envio) or (not status_timer):
                    print('parou')
                    break
                #tempo_inicio = time.time()
                minutos, segundos = divmod(total_segundos, 60)
                texto_envio_tarefa.value = f'Enviando em:  {minutos:02d}:{segundos:02d}'
                #print(f'Enviando em:  {minutos:02d}:{segundos:02d}')
                porcentagem = ((100/total_ring )* total_segundos)*0.01
                progresso.value = porcentagem

                
                total_segundos -= 1

                
                limiar = 1
                if total_segundos/total_ring < limiar: # 50% do progresso
                    cor_intermediaria = (
                        int(cor_inicio[0] + (porcentagem/limiar) * (cor_fim[0] - cor_inicio[0])),
                        int(cor_inicio[1] + (porcentagem/limiar) * (cor_fim[1] - cor_inicio[1])),
                        int(cor_inicio[2] + (porcentagem/limiar) * (cor_fim[2] - cor_inicio[2])),
                    )
                    progresso.color = "#{:02X}{:02X}{:02X}".format(*cor_intermediaria)
                page.update()
                #print(time.time()-tempo_inicio )
                time.sleep(0.9965)
            else:
                print("aq")
                alerta_envio_tarefa.modal = False
                progresso.color = None
                page.update()
                time.sleep(2)
                if status_envio:
                    envia_email(None)
                bnt_cancelar_envio.visible = True
                bnt_cancelar_envio.text = 'Ok'
        
        page.update()

    def close_dlg_salvamento(e):
        out_alerta_confirma_salvamento.open = False
        page.update()

    def close_dlg(e):
        global status_timer
        out_alerta_confirma.open = False
        dlg_modal_salvar.open = False
        alerta_envio_tarefa.open = False
        out_alerta_confirma_tarefa.open = False
        out_alerta_dados_incorretos.open = False
        status_timer = False
        
        page.update()

    def aborta_acao(e):
        global status_envio
        bnt_cancelar_envio.disabled = True
        status_envio = False
        if bnt_cancelar_envio.text != 'Ok':
            icon_envio_tarefa.name = ft.icons.CANCEL_SCHEDULE_SEND
            icon_envio_tarefa.color = ft.colors.RED_200
            texto_envio_tarefa.value = 'Envio Abortado'
            page.update()
            time.sleep(1)
            alerta_envio_tarefa.open = False
            page.update()
        else:
            alerta_envio_tarefa.open = False
            page.update()

    def close_dlg_salvar(e):
        dlg_modal_salvar.open = False
        ckb_salvar.value = True
        print("Modal Fechado")
        page.update()

    def add_conteudo_pagina(e):
        global status_dados_email
        if verifica_campos_email():
            page.clean()
            page.add(out_header,
                ft.ResponsiveRow(
                    [
                        conteudo_email,
                        conteudo_agendamento    
                    ],
                )
            )
            page.window_width = 1000
            page.window_min_width = 1000 
            page.window_height = 940  
            bnt_agendar.visible = False
            status_dados_email = True
            
            # else:
            #     page.window_width = 500
            #     page.window_height = 900   
            #     page.add(out_header, conteudo_email)
        page.update()   
    
    def ativa_campo_tarefa(e):
        if e.control.value:
            in_descricao_tarefa.disabled =  False
            in_nome_tarefa.disabled = False
        else:
            in_descricao_tarefa.disabled =  True
            in_nome_tarefa.disabled = True
        in_descricao_tarefa.update()
        in_nome_tarefa.update()
    
    def tipo_agendamento(e):
        if in_tipo_tarefa.value == '1':
            chk_dias.visible = False
            in_intervalo.visible = False
            out_data_fim.visible = False
            out_data.visible = True
            out_hora.visible = True
            out_data.label = "Data"
            
        if in_tipo_tarefa.value == '2':
            chk_dias.visible = False
            out_data.visible = True
            out_data_fim.visible = True
            out_hora.visible = True
            in_intervalo.visible = True
            out_data.label = "Data Inicial"
            in_intervalo.suffix_text = 'Dias'
        
        if in_tipo_tarefa.value == '3':
            in_intervalo.visible = True
            out_data.visible = True
            out_data_fim.visible = True
            out_hora.visible = True
            chk_dias.visible = True
            out_data.label = "Data Inicial"
            in_intervalo.suffix_text = 'Semanas'

        page.update()

    def formata_agendamento(data, hora) -> str:
        try:
            return ('{}{}{}{}{}'.format(data.strftime("%Y-%m-%d"),"T", hora, '-',"03:00" ))
        except: return ''

    def adiciona_dia(e):
        global dias
        if e.control.value == True:
            
            dias.append(e.control.label.replace('Dom', '1').replace('Seg', '2').replace('Ter', '3').replace('Qua', '4').replace('Qui', '5').replace('Sex', '6').replace('Sab', '7'))
        else:
            dias.remove(e.control.label.replace('Dom', '1').replace('Seg', '2').replace('Ter', '3').replace('Qua', '4').replace('Qui', '5').replace('Sex', '6').replace('Sab', '7'))
        #print(dias)

    def configura_dados_tarefa():
        global dias
        global dados_tarefa
        in_tipo_tarefa.value = dados_tarefa['tipo']
        in_intervalo.value = dados_tarefa['intervalo']

        if dados_tarefa['data'] != '' and len(dados_tarefa['data']) == 25:
            date_picker.value = datetime.strptime(dados_tarefa['data'][:19], "%Y-%m-%dT%H:%M:%S")
            time_picker.value = datetime.strptime(dados_tarefa['data'][:19], "%Y-%m-%dT%H:%M:%S").strftime("%H:%M:%S")
            out_data.value = date_picker.value.strftime("%d/%m/%Y")
            out_hora.value = time_picker.value

        if dados_tarefa['dataFim'] != '' and len(dados_tarefa['dataFim']) == 25:
           date_picker_fim.value = datetime.strptime(dados_tarefa['dataFim'][:19], "%Y-%m-%dT%H:%M:%S")
           out_data_fim.value = date_picker_fim.value.strftime("%d/%m/%Y")
        tipo_agendamento(None)
        dias = eval(dados_tarefa['dias'])
        
        dias_variaveis = {0: dom, 1: seg, 2: ter, 3: qua, 4: qui, 5: sex, 6: sab}

        for valor in dias:
            indice = int(valor) - 1  
            if 0 <= indice < len(dias_variaveis):
                dias_variaveis[indice].value = True
                
        page.update()

    def limpa_campos(e):
        print('Limpando campos')
        global status_dados_agendamento
        global arquivos

        arquivos = []
        out_arquivos.clean()
        out_assunto.value = None

        in_nome_tarefa.value = f'Auto Email ({tarefaSelecionada})'

        cg.value = '1'
        in_email.value = ''
        in_senha.value = ''
        in_email_destino.value = ''
        in_email_CC.value = ''
        in_assunto.value = ''
        in_tipo_text.value ='1'
        in_texto.value = ''
        in_tipo_exec.value = '1'
        in_atraso.value = '1'
        
        bnt_salvar.icon_color = None
        bnt_salvar.text =  'Salvar configurações'

        text_alerta_salvamento.value = 'Você deseja salvar as configurações atuais?'
            
        in_tipo_tarefa.value = None
        in_tipo_tarefa.disabled = False

        ckb_sobrescrever_tarefa.visible = False
        btn_editar.disabled = False

        bnt_criar_tarefa.text = "Agendar tarefa"
        bnt_criar_tarefa.icon_color = None
        bnt_criar_tarefa.disabled = False

        icon_status_tarefa.name  = ft.icons.RADIO_BUTTON_UNCHECKED
        icon_status_tarefa.color = None

        dom.disabled = False
        seg.disabled = False
        ter.disabled = False
        qua.disabled = False
        qui.disabled = False
        sex.disabled = False
        sab.disabled = False

        dom.visible = False
        seg.visible = False
        ter.visible = False
        qua.visible = False
        qui.visible = False
        sex.visible = False
        sab.visible = False

        dom.value = None
        seg.value = None
        ter.value = None
        qua.value = None
        qui.value = None
        sex.value = None
        sab.value = None

        out_data.disabled = False
        out_data_fim.disabled = False
        out_hora.disabled = False
        in_intervalo.disabled = False

        out_data.visible = False
        out_data_fim.visible = False
        out_hora.visible = False
        in_intervalo.visible = False

        out_data.value = None
        out_data_fim.value = None
        out_hora.value = None
        in_intervalo.value = 1



        status_dados_agendamento = False
        page.update()

    def configura_campos(tarefa_selecionada: str, tipo_exec: bool):
        
        #print('Configurando', tarefa_selecionada)

        global status_encerramento
        global dados_tarefa
        global status_dados_agendamento
        global status_exec
        global chave
        global out_dados
        global listaTarefas
        global tarefaSelecionada

        tarefaSelecionada = tarefa_selecionada

        limpa_campos(None)
        try:
            nome_arquivo_json = "dados.bin"

            try:
                caminho_arquivo_json = os.path.join(caminho_dados, nome_arquivo_json)
                out_dados = load_encrypted_data(chave, caminho_arquivo_json)
                
            except:

                print('Nenhum arquivo de configuraçao foi encontrado')
                in_config = {}

            if not out_dados and not listaTarefas:
                listaTarefas.append(ft.dropdown.Option(key='Tarefa 1'))

            # Adiciona os identificadores na lista de options do dropDown
            for tarefa in out_dados:
                if tarefa['identificador'] not in (item.key for item in listaTarefas):
                    listaTarefas.append(ft.dropdown.Option(key=tarefa['identificador']))
                
            for index, tarefa in enumerate(out_dados):
                if  tarefa['identificador'] == tarefa_selecionada:
                    in_config = out_dados[index]
                    break
            else:
                in_config = {}

            if in_config['restauraConfig'] == 'True':
                #print('Restaurando dados')
                set_tema(in_config['temaPagina'])
                
                try:
                    chave_arquivo = re.compile(r"b'(.*?)'").search(in_config['chave']).group(1).encode()
                    senha_arquivo = re.compile(r"b'(.*?)'").search(in_config['senhaEmail']).group(1).encode()
                    in_senha.value = Fernet(chave_arquivo).decrypt(senha_arquivo).decode()
                except: 
                    in_senha.error_text = 'Falha ao descriptografar senha salva'

                cg.value = in_config['tipoEmail']
                in_email.value = in_config['emailUsuario']
                in_email_destino.value = in_config['emailDestino']
                in_email_CC.value = in_config['emailCC']
                in_assunto.value = in_config['emailAssunto']
                in_tipo_text.value = in_config['tipoTexto']
                in_texto.value = in_config['emailTexto']
                in_tipo_exec.value = in_config['tipoExec']
                in_atraso.value = in_config['atraso']
                
                if in_config['tarefa'] == {}:
                    ckb_sobrescrever_tarefa.visible = False
                else:
                    ckb_sobrescrever_tarefa.visible = True
                    bnt_criar_tarefa.text = 'Já existe uma tarefa salva.'
                    bnt_criar_tarefa.disabled = True
                    
                    in_tipo_tarefa.disabled = True
                    btn_editar.disabled = True
                    dom.disabled = True
                    seg.disabled = True
                    ter.disabled = True
                    qua.disabled = True
                    qui.disabled = True
                    sex.disabled = True
                    sab.disabled = True
                    out_data.disabled = True
                    out_data_fim.disabled = True
                    out_hora.disabled = True
                    in_intervalo.disabled = True

                    status_dados_agendamento = True
                    icon_status_tarefa.name  = ft.icons.CHECK_CIRCLE_OUTLINED
                    icon_status_tarefa.color = ft.colors.GREEN_500
                    dados_tarefa = in_config['tarefa']
                    configura_dados_tarefa()
        
                configura_tipo_execucao(None)
                restaura_arquivos_salvos(ast.literal_eval(in_config['anexos']))
                atualiza_texto_assunto(None)


                #print('statusExec', in_config['statusExec'])
                if tipo_exec: #Execução automatica do programa
                    status_encerramento = True
                    open_dlg_alerta_envio(None)
            page.update()
        except Exception as e:
            print(e)

        drop_tarefa.value = tarefa_selecionada
        page.update()   

    def salva_conteudo(e):
        global chave
        global out_dados
        global tarefaSelecionada

        if status_dados_email and status_dados_agendamento:

            out_config = {  
                "identificador": tarefaSelecionada,
                "restauraConfig": f"{ckb_salvar.value}",
                "temaPagina": f"{page.theme_mode}",
                "chave" : f"{chave_usuario}",
                "tipoEmail":f"{cg.value}",
                "emailUsuario":f"{in_email.value}",
                "senhaEmail":f"{Fernet(chave_usuario).encrypt(in_senha.value.encode())}",
                "emailDestino":f"{in_email_destino.value}",
                "emailCC":f"{in_email_CC.value}",
                "emailAssunto":f"{in_assunto.value}",
                "tipoTexto": f"{in_tipo_text.value}",
                "emailTexto":f"{in_texto.value}",
                "anexos": f"{arquivos}",
                "statusExec": "0", # 1 para execuçao normal, 0 para execuçao automatica
                "tipoExec": f"{in_tipo_exec.value}",
                "atraso":f"{in_atraso.value}",
                "tarefa": dados_tarefa
                }
            
            if out_dados:
                for index, tarefa in enumerate(out_dados):
                    if tarefa['identificador'] == tarefaSelecionada:    
                        out_dados[index] = out_config
                        break
                else:
                    out_dados.append(out_config) 
            else: 
                out_dados.append(out_config) 

            #print('dados gravados--->', out_dados)

            # Nome do arquivo JSON
            nome_arquivo_json = "dados.bin"

            # Criando o caminho completo para o arquivo JSON
            caminho_arquivo_json = os.path.join(caminho_dados, nome_arquivo_json)

            save_encrypted_data(out_dados, chave, caminho_arquivo_json)

            close_dlg(e)
            bnt_salvar.icon_color = ft.colors.GREEN_200
            bnt_salvar.text =  'Configurações Salvas'
        
        else:
            bnt_salvar.icon_color = ft.colors.RED_200
            if not status_dados_agendamento:
                bnt_criar_tarefa.icon_color = ft.colors.RED_100

        page.update()

    def checkbox_changed(e):
        if not ckb_salvar.value:
            open_dlg_modal_salvar(e)

    def pick_data(e):
        bnt_salvar.focus()
        date_picker.pick_date()
    
    def pick_data_fim(e):
        bnt_salvar.focus()
        date_picker_fim.pick_date()
    
    def pick_hora(e):
        bnt_salvar.focus()
        time_picker.pick_time()

    def change_date(e):
        bnt_salvar.focus()
        out_data.value = date_picker.value.strftime("%d/%m/%Y")
        time.sleep(0.2)
        page.update()

    def change_date_fim(e):
        bnt_salvar.focus()
        out_data_fim.value = date_picker_fim.value.strftime("%d/%m/%Y")
        time.sleep(0.2)
        page.update()
        
    def change_time(e):
        bnt_salvar.focus()
        out_hora.value = time_picker.value
        time.sleep(0.2)
        page.update()

    def dismissed(e):
        bnt_agendar.focus()
        page.update()

    def reset_campo(e):
        e.control.error_text = ''
        page.update()

    def salva_dados_tarefa(e):
        global dias
        global dados_tarefa
        global status_dados_agendamento

        status = 0 # Status do formulario da tarefa

        for var in [in_nome_tarefa,in_descricao_tarefa, out_data, out_hora]:
            if var.value is None or (isinstance(var.value, str) and not var.value.strip()):
                 var.error_text = 'Obrigatório'
            else:
                var.error_text = None
                status +=1
                
        if in_tipo_tarefa.value == None:
            icon_tipo.color= ft.colors.RED_200
            icon_tipo.update()
        else:
            icon_tipo.color = None
            

        if in_tipo_tarefa.value == '2':    
            if out_data_fim.value == None or out_data_fim.value == '':
                out_data_fim.error_text = 'Obrigatório'
            else:
                out_data_fim.error_text = None
                status +=1
                

        if in_tipo_tarefa.value == '3':
            if out_data_fim.value == None or out_data_fim.value == '':
                out_data_fim.error_text = 'Obrigatório'
            else:
                out_data_fim.error_text = None
                status +=1
                
            if not dias:
                dom.fill_color = ft.colors.RED_200
            else: 
                dom.fill_color = None
                status +=1

        if (in_tipo_tarefa.value == '1'  and status >= 4) or (in_tipo_tarefa.value == '2'  and status >= 5) or (in_tipo_tarefa.value == '3'  and status >= 6):
            
            dados_tarefa = {
                "nome": f"{in_nome_tarefa.value}",
                "descricao": f"{in_descricao_tarefa.value}",
                "tipo": f"{in_tipo_tarefa.value}",
                "data": f"{formata_agendamento(date_picker.value,time_picker.value)}",
                "dataFim": f"{formata_agendamento(date_picker_fim.value,time_picker.value)}",
                "intervalo": f"{in_intervalo.value}",
                "dias": f"{dias}",
            }
            open_dlg_modal_confima_tarefa(None)
            bnt_criar_tarefa.icon_color = ft.colors.GREEN_500
            status_dados_agendamento = True
        else:
            bnt_criar_tarefa.icon_color = ft.colors.RED_300

        page.update()

    def cria_tarefa(e):
        global dados_tarefa
        global tarefaSelecionada
        out_alerta_confirma_tarefa.open = False
        page.update()

        status = Task(
            task_name=dados_tarefa['nome'],
            task_description=dados_tarefa['descricao'],
            task_type=dados_tarefa['tipo'],
            interval= dados_tarefa['intervalo'],
            days=ast.literal_eval(dados_tarefa['dias']),
            start=dados_tarefa['data'], 
            end=dados_tarefa['dataFim'], 
            exec_path = caminho_execucao +'/AutoEmail.exe',
            argument = tarefaSelecionada.replace(' ', '_')
            ).run()
        
        if status:
            icon_alerta_tarefa.name = ft.icons.CHECK_CIRCLE_OUTLINED
            icon_alerta_tarefa.color = ft.colors.GREEN_500
            texto_alerta_tarefa.value = 'Tarefa criada com sucesso!'
            icon_status_tarefa.name  = ft.icons.CHECK_CIRCLE_OUTLINED
            icon_status_tarefa.color = ft.colors.GREEN_500

            page.dialog = alerta_tarefa
            alerta_tarefa.open = True
            page.update()
            time.sleep(1)
            alerta_tarefa.open = False
            page.update()
            
        else:
            icon_alerta_tarefa.name = ft.icons.ERROR_OUTLINE_OUTLINED
            icon_alerta_tarefa.color = ft.colors.RED_500
            texto_alerta_tarefa.value = "Falha ao criar tarefa."
            icon_status_tarefa.name  = ft.icons.ERROR_OUTLINE_OUTLINED
            icon_status_tarefa.color = ft.colors.RED_500

            page.dialog = alerta_tarefa
            alerta_tarefa.open = True
            page.update()

    def editar_tarefa_salva(e):
        if e.control.value:
            e.control.visible = False
            bnt_criar_tarefa.disabled = False
            icon_status_tarefa.name  = ft.icons.RADIO_BUTTON_UNCHECKED
            icon_status_tarefa.color = None
            bnt_criar_tarefa.text="Agendar tarefa"

            in_tipo_tarefa.disabled = False
            btn_editar.disabled = False
            dom.disabled = False
            seg.disabled = False
            ter.disabled = False
            qua.disabled = False
            qui.disabled = False
            sex.disabled = False
            sab.disabled = False
            out_data.disabled = False
            out_data_fim.disabled = False
            out_hora.disabled = False
            in_intervalo.disabled = False

        page.update()

    def configura_tipo_execucao(e):
        if in_tipo_exec.value == '3' or in_tipo_exec.value == '4':
            in_atraso.visible = True
        else:
            in_atraso.visible = False
        page.update()

    def envia_email(e):
        global status_encerramento
        global status_timer
        status_timer = False

        bnt_confirmar_envio.disabled = True
        bnt_cancelar_envio.disabled = True
        page.dialog = alerta_envio_tarefa
        alerta_envio_tarefa.open = True
        texto_envio_tarefa.value = 'Enviando...'
        icon_envio_tarefa.name = ft.icons.SCHEDULE_SEND
        progresso.visible = False

        page.update()
                
        if cg.value == '1':
            email_envio = in_email.value + '@legalcontrol.com.br'
        elif cg.value == '2':
            email_envio = in_email.value + '@outlook.com'
        elif cg.value == '3':
            email_envio = in_email.value + '@gmail.com'
        else:
            email_envio = in_email.value

        if arquivos != None:
           lista_anexos =  [sublista[1] for sublista in arquivos]

        status_email = Email(
        email_envio = email_envio ,
        senha = in_senha.value,
        email_destino = in_email_destino.value,
        email_cc = in_email_CC.value,
        assunto = out_assunto.value,
        mensagem = in_texto.value,
        caminho_anexo = lista_anexos
        ).run()

        bnt_confirmar_envio.disabled = False
        bnt_cancelar_envio.disabled = False
        
        page.update()
        if status_email == '1':
            icon_envio_tarefa.name = ft.icons.CHECK_CIRCLE_OUTLINE_OUTLINED
            icon_envio_tarefa.color = ft.colors.GREEN_500
            texto_envio_tarefa.value = 'Email enviado com sucesso!!'
            print('Email Enviado...')
        else:
            icon_envio_tarefa.name = ft.icons.ERROR_OUTLINE_OUTLINED
            icon_envio_tarefa.color = ft.colors.RED_500
            status_encerramento = False
            print('Falha ao enviar Email...')
            if status_email == '0':
                texto_envio_tarefa.value = 'Falha ao enviar.'

            if status_email.find('credentials were incorrect'):
                texto_envio_tarefa.value = 'Falha de Autenticação, credenciais incorretas.'

        if in_tipo_exec.value == '4':
            progresso.visible = False
       
        alerta_envio_tarefa.modal = False
        bnt_cancelar_envio.text = 'Ok'
        bnt_confirmar_envio.visible = False
        bnt_cancelar_envio.visible = True
        
        page.update()

        if status_encerramento:
            time.sleep(3)
            timer = 3
            while timer >= 0:
                texto_envio_tarefa.value = f'Encerrando em {timer}s'
                timer -= 1
                page.update()
                time.sleep(1)
            else:
                page.window_destroy()

    def verifica_campos_email() -> bool:
        if in_email.value !='' and in_senha.value != '' and in_email_destino.value != '' and in_assunto.value != '':
            return True
        else:
            if in_email.value == '':
                in_email.error_text = 'Obrigatorio'
            if in_senha.value == '':
                in_senha.error_text = 'Obrigatorio'
            if in_email_destino.value == '':
                in_email_destino.error_text = 'Obrigatorio'
            if in_assunto.value == '':
                in_assunto.error_text = 'Obrigatorio'
            return False

    def timer_fechamento(e):
        salva_conteudo(None)
        text_alerta_salvamento.value = 'Dados salvos'
        page.update()
        time.sleep(1)
        out_alerta_confirma_salvamento.open = False
        page.update()

    def cria_nova_tarefa(e):
        global tarefaSelecionada
        global contador_tarefas
        global listaTarefas

        contador_tarefas = len(listaTarefas)
        
        if contador_tarefas >= 5:
            in_nova_tarefa.disabled = True
        else:
            print('oi')
            contador_tarefas += 1
            listaTarefas.append(ft.dropdown.Option(key=f'Tarefa {contador_tarefas}'))
            tarefaSelecionada = f'Tarefa {contador_tarefas}'
            configura_campos(tarefaSelecionada, False)
        page.update()

    def atualiza_tarefa(e):
        global listaTarefas
        print (listaTarefas)
        global tarefaSelecionada
        tarefaSelecionada = drop_tarefa.value
        configura_campos(tarefaSelecionada, False)

    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por Favor Confirme"),
        content=ft.Text("Você deseja fechar o aplicativo?"),
        actions=[
            ft.ElevatedButton("Sim", on_click=yes_click),
            ft.OutlinedButton("Não", on_click=no_click),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    
    drop_tarefa = ft.Dropdown(
        options = listaTarefas,
        height=40,
        dense = True, 
        autofocus = False,
        text_size= 13,
        scale=0.8,
        on_change = atualiza_tarefa
    )

    # Cabeçalho do aplicativo
    out_header = ft.Row(
        [
            ft.Container(
                content = drop_tarefa,
                width = (page.window_width)/4
                
            ),
            ft.Container(
                content = ft.Text(
                    value = 'Auto Email',
                    size = 25,
                    height = 40,
                    weight = ft.FontWeight.W_900),
                alignment = ft.alignment.center,
                width = (page.window_width)/3,
            ),
            ft.Container(
                content = (bnt_tema := ft.IconButton(
                    icon= ft.icons.LIGHT_MODE_OUTLINED,
                    icon_size = 25,
                    tooltip='Modo Claro',
                    on_click= theme_changed,
                )),
                alignment = ft.alignment.center_right,
                width = (page.window_width)/4, 
                padding= ft.padding.only(right=20)

            )
        ], 
        alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    # Tipo de email
    cg = ft.RadioGroup( 
        content = ft.Row(
            [
                ft.TextField(
                    hint_text = 'Tipo',
                    icon= ft.icons.TYPE_SPECIMEN_OUTLINED,
                    border=ft.InputBorder.NONE,
                    disabled=True,
                    width= 80
                ),
                ft.Radio(value="1", label="LC", visible= True),
                ft.Radio(value="2", label="Outlook", visible= True),
                ft.Radio(value="3", label="Gmail", visible= True),
                ft.Radio(value="4", label="Outro")
            ],
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        on_change = radiogroup_changed,
        value = '1'
    )

   # Nome de Usuario e Senha
    in_email = ft.TextField(label="Usuario", 
                            icon = ft.icons.ALTERNATE_EMAIL,
                            hint_text = 'exemplo@email.com',
                            hint_style=ft.TextStyle(size = 11, italic = True),
                            on_focus  = radiogroup_changed,
                            on_change = reset_campo
                            )
    in_senha = ft.TextField(label="Senha",                            
                            icon=ft.icons.PASSWORD,
                            hint_text = 'senha do email',
                            hint_style=ft.TextStyle(size = 11, italic = True),
                            password=True,
                            can_reveal_password=True,
                            on_focus = reset_campo,
                            on_change = reset_campo
                            )
  
    # Container com os campos usuario e senha
    in_dados_email = ft.Container(
        content= ft.Column(
            [
                in_email, 
                in_senha, 
                ft.Divider()
            ]
        ),
    )
    
    # Informaçoes de destino
    in_email_destino = ft.TextField(label="Email destino",
                                    icon=ft.icons.OUTGOING_MAIL,
                                    hint_text = 'exemplo@email.com',
                                    hint_style=ft.TextStyle(size = 11, italic = True), 
                                    on_change=reset_campo
                                    
                                    )

    in_email_CC = ft.TextField(label="Email CC", 
                               icon=ft.icons.MARK_EMAIL_READ_ROUNDED,
                               hint_text = 'exemplo@email.com',
                               hint_style=ft.TextStyle(size = 11, italic = True)
                               )

    in_assunto = ft.TextField(label="Assunto",
                              icon = ft.icons.SUBJECT_OUTLINED,
                              hint_text = f'Use /data para inserir a data de envio automaticamente.',
                              hint_style=ft.TextStyle(size = 12, italic = True),
                              on_change = atualiza_texto_assunto,
                              max_length = 50,
                              multiline = True,
                              min_lines = 1,
                              max_lines = 2
                              )
    
    # Linha de saida do texto inserido no assunto
    out_linha_assunto = ft.Row(
        [
            out_assunto := ft.Text(italic = True, size = 11, height=20, color=ft.colors.GREEN_500)
        ],
        bottom = 0,
        left = 50
    )

    stk_assunto = ft.Stack(
        [
            in_assunto,
            out_linha_assunto
        ],
        height = 80
    )

    # Grupo com o campo de mensagem do email e tipo de mensagem
    stk_msg = ft.Stack(
        [
            in_texto := ft.TextField(
                label="Mensagem",
                icon = ft.icons.TEXT_FIELDS,
                hint_text= f'''Digite a mensagem aqui''',
                hint_style=ft.TextStyle(size = 12, italic = True),
                max_length = 500,
                multiline = True,
                max_lines=8,
                min_lines=8,
                text_style=ft.TextStyle(size = 12, italic = True),
            ),
            ft.Row(
                [
                    in_tipo_text := ft.RadioGroup(
                        content = ft.Row(
                            [
                                ft.Radio(value="1", label="Texto", visible= True),
                                ft.Radio(value="2", label="HTML", visible= True)
                            ]
                        ), 
                        on_change= radiogroup2_changed,
                        value= 1
                    )
                ], 
                bottom = 0, 
                left = 40
            )
        ],
        height= 210, 
    )

    # Captura de arquivos
    pick_files_dialog = ft.FilePicker(on_result=pick_files_result)
    file = ft.ElevatedButton(
        "Escolher Anexos",
        icon=ft.icons.UPLOAD_FILE,
        on_click=lambda _: pick_files_dialog.pick_files(allow_multiple=True)
    )

    # Arquivos selecionados
    files = ft.Ref[ft.Column]
    out_arquivos = ft.Column(ref = files)

    ckb_salvar = ft.Checkbox(
        label_position= ft.LabelPosition.LEFT,
        label= 'Lembrar',
        tooltip='Salvar configurações',
        fill_color={
            ft.MaterialState.SELECTED: ft.colors.GREEN,
        },
        value = True,
        on_change=checkbox_changed,
    )

    # Botao para agendar o envio
    bnt_agendar = ft.ElevatedButton(
        text="Agendamento",
        on_click=add_conteudo_pagina,
        icon= ft.icons.SCHEDULE_SEND_SHARP,
        width= 170
    )

    # Botao para enviar na hora
    bnt_enviar = ft.ElevatedButton(
        text="Enviar agora",
        on_click=open_dlg_modal_confima,
        icon= ft.icons.SEND,
        width= 170
    )
    bnt_salvar = ft.ElevatedButton(
        text = 'Salvar configurações',
        icon= ft.icons.SAVE_OUTLINED,
        on_click = verifica_dados, 
        width= 250,
        )
    
    in_nova_tarefa = ft.ElevatedButton(
        text="Nova tarefa",
        icon= ft.icons.ADD_TO_PHOTOS, 
        on_click= cria_nova_tarefa, 
        #height= 40, 
        #width= 200, 
        disabled= False, 
    )
    

    # Linha de botoes
    out_botoes = ft.Container(
        ft.Stack(
            [   
                #ft.Container(ckb_salvar, right=10),
                ft.Container(ft.Icon(name=ft.icons.ATTACH_EMAIL_ROUNDED), top= 40, ),
                ft.Container(file, top= 0, left = 40),
                ft.Container(out_arquivos, left = 40,top = 40, width= 230, height=80, border= ft.border.all(1, ft.colors.BLACK), border_radius= 5, padding= 4),
                ft.Container(bnt_agendar, right = 0, top = 40 ),
                ft.Container(bnt_enviar, bottom= 50, right = 0),
                ft.Container(bnt_salvar, bottom= 0, right= 0),
                ft.Container(ckb_salvar, top= 0, right = 0, ),
                ft.Container(in_nova_tarefa, bottom= 0, left=40),       
            ]
        ),
        
        height = 170,
        #bgcolor= ft.colors.RED

    )

    # Alerta ao clicar nos botoes
    out_alerta_confirma = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Voce realmente quer fazer o envio?"),
        actions=[
            ft.OutlinedButton("Sim", on_click = envia_email),
            ft.TextButton("Não", on_click = close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    out_alerta_confirma_salvamento = ft.AlertDialog(
        modal=True,
        title=ft.Text("Tudo pronto"),
        content= (text_alerta_salvamento := ft.Text("Você deseja salvar as configurações atuais?")),
        actions=[
            ft.OutlinedButton("Sim", on_click = timer_fechamento),
            ft.TextButton("Não", on_click = close_dlg_salvamento),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    out_alerta_dados_incorretos= ft.AlertDialog(
        modal=True,
        title=ft.Text("Atenção"),
        content= (text_alerta_dados := ft.Text("É necessário preencher ou alterar os campos obrigatórios e agendar uma tarefa antes de salvar!")),
        actions=[
            ft.TextButton("Ok", on_click = close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    out_alerta_confirma_tarefa = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Deseja criar uma tarefa agendada? "),
        actions=[
            ft.OutlinedButton("Sim", on_click = cria_tarefa),
            ft.TextButton("Não", on_click = close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END
    )

    # Alerta ao tentar desativar o checkbox de salvamento automatico
    dlg_modal_salvar = ft.AlertDialog(
        modal=True,
        title=ft.Text("Por favor confirme"),
        content=ft.Text("Para envios agendados é necessário salvar as configurações, deseja desabilitar o salvamento?"),
        actions=[
            ft.TextButton("Sim", on_click=close_dlg),
            ft.OutlinedButton("Não", on_click=close_dlg_salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,

    )   

    # Conteudo da janela do email
    conteudo_email = ft.Container(
        content = ft.Column(
            [
                cg,
                in_dados_email,
                in_email_destino,
                in_email_CC,
                stk_assunto,
                stk_msg,
                out_botoes,
            ]
        ),
        padding = ft.padding.only(right=20),
        col = 6
    )

    # Dados da Tarefa
    in_nome_tarefa = ft.TextField(
        label="Nome da Tarefa", 
        icon = ft.icons.DRIVE_FILE_RENAME_OUTLINE_OUTLINED,
        hint_text = 'Nome da Tarefa',
        hint_style=ft.TextStyle(size = 11, italic = True),
        value = f'Auto Email ({tarefaSelecionada})',
        disabled= True
    )
    in_descricao_tarefa = ft.TextField(
        label="Descrição da Tarefa", 
        icon = ft.icons.DESCRIPTION_OUTLINED,
        hint_text = 'Descrição da Tarefa',
        hint_style=ft.TextStyle(size = 11, italic = True),
        value= 'Tarefa agendada do Auto Email',
        disabled= True
        
    )

    # Botao para editar o nome e descricao padrao da tarefa
    btn_editar = ft.Container(
        content = ft.Checkbox(
            label="Editar",
            value = False,
            on_change = ativa_campo_tarefa, 
        ),
        padding = ft.padding.only(left=40),
    ) 
    
    # Grupo de botoes de tipos de tarefas
    stk_tarefa = ft.Stack(
        [   
            ft.Container(
                icon_tipo := ft.Icon(
                    name=ft.icons.TIMER_OUTLINED, 
                    
                ),
                top=5),
                in_tipo_tarefa := ft.RadioGroup(
                    content = ft.Row(
                        [   
                            ft.Radio(value="1", label="Uma vez", visible= True),
                            ft.Radio(value="2", label="Diariamente", visible= True),
                            ft.Radio(value="3", label="Semanalmente", visible= True)
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_EVENLY,   
                    ),
                    on_change = tipo_agendamento,
            
                ),
             
        ]        
    )
            
    
    date_picker = ft.DatePicker(
        confirm_text="Confirmar",
        cancel_text="Cancelar",
        error_invalid_text="Data fora do intervalo",
        help_text="Escolha a data",
        on_change=change_date,
        on_dismiss=dismissed,
    )
    date_picker_fim = ft.DatePicker(
        confirm_text="Confirmar",
        cancel_text="Cancelar",
        error_invalid_text="Data fora do intervalo",
        help_text="Escolha a data final",
        on_change=change_date_fim,
        on_dismiss=dismissed,
    )
    time_picker = ft.TimePicker(
        confirm_text="Confirmar",
        cancel_text="Cancelar",
        error_invalid_text="Horario fora do intervalo",
        help_text="Escolha o horario",
        on_change=change_time,
        on_dismiss=dismissed,
    )
    
    # Adiciona o modais
    page.overlay.append(time_picker)
    page.overlay.append(date_picker)
    page.overlay.append(date_picker_fim)
    page.overlay.append(pick_files_dialog)

    # Campo que mostra a data escolhida 
    out_data = ft.TextField(
        label= 'Data',
        icon = ft.icons.DATE_RANGE_OUTLINED,
        on_focus=pick_data,
        visible= False,
        width= 200,
        text_align=ft.TextAlign.CENTER,
        col=6
    )

    out_data_fim = ft.TextField(
        label= 'Data Final',
        icon = ft.icons.DATE_RANGE_OUTLINED,
        on_focus= pick_data_fim,
        visible= False,
        width= 200,
        text_align=ft.TextAlign.CENTER,
        col=6
    )

    out_hora = ft.TextField(
        label= 'Horário',
        icon = ft.icons.ACCESS_TIME_OUTLINED,
        visible = False,
        on_focus= pick_hora,
        width= 200,
        text_align=ft.TextAlign.CENTER,
        col=6
    )

    in_intervalo = ft.TextField(
        label= 'Intervalo',
        value= '1',
        icon = ft.icons.UPDATE_DISABLED_OUTLINED,
        visible = False,
        width= 200,
        text_align=ft.TextAlign.CENTER,
        col=6,
        input_filter= ft.InputFilter(allow=True, regex_string=r"^[2-9]$", replacement_string="1")
    )

    chk_dias= ft.Row(
                    [   
                        dom:= ft.Checkbox(label="Dom", value=False, on_change= adiciona_dia, key = 0),
                        seg:=ft.Checkbox(label="Seg", value=False, on_change= adiciona_dia, key = 1),
                        ter:=ft.Checkbox(label="Ter", value=False, on_change= adiciona_dia),
                        qua:=ft.Checkbox(label="Qua", value=False, on_change= adiciona_dia),
                        qui:=ft.Checkbox(label="Qui", value=False, on_change= adiciona_dia),
                        sex:=ft.Checkbox(label="Sex", value=False, on_change= adiciona_dia),
                        sab:=ft.Checkbox(label="Sab", value=False, on_change= adiciona_dia),
                    ],
                    visible = False,
                    alignment = ft.MainAxisAlignment.CENTER,
                    spacing = 2,
    )


    bnt_criar_tarefa = ft.ElevatedButton(
        text="Agendar tarefa",
        icon= ft.icons.PLAYLIST_ADD_CHECK_OUTLINED, 
        on_click= salva_dados_tarefa, 
        #height= 40, 
        #width= 200, 
        disabled= False, 
    )

    ckb_sobrescrever_tarefa = ft.Checkbox(label='Sobrescrever', disabled= False, on_change=editar_tarefa_salva)

 

    stk_config = ft.Stack(
        [   
            ft.Container(
                ft.Row([
                ft.Icon(name=ft.icons.SETTINGS),
                ft.Text(value='Quando o programa for executado:')]
            ),
                top=5
            ),
            ft.Container(
                in_tipo_exec:=ft.RadioGroup(
                    content = ft.Column(
                        [   
                            ft.Radio(value="1", label="Enviar e-mail", visible= True, tooltip='O email será enviado assim que o programa for executado'),
                            ft.Radio(value="2", label="Aguardar confirmação", visible= True, tooltip= 'Uma janela de confirmação ficará visivel para confirmação'),
                            ft.Radio(value="3", label="Aguardar um periodo", visible= True, tooltip= 'O email será enviado após um periodo de tempo determinado'),
                            ft.Radio(value="4", label="Aguardar um periodo ou confirmação", visible= True, tooltip = 'O email será enviado após a confirmação ou um perido de tempo execução')
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_EVENLY,   
                    ),
                    on_change =  configura_tipo_execucao,
                    value= 1
                ),
             
                top= 30, left= 25
            ),
            ft.Container(
                in_atraso := ft.TextField(
                    label='Periodo',
                    width=200,
                    icon= ft.icons.AV_TIMER_OUTLINED, 
                    visible= False,
                    suffix_text= 'minutos',
                    input_filter= ft.InputFilter(allow=True, regex_string=r"^(?:[1-9]|[1-9][0-9]|[1][01][0-9]|120)$", replacement_string="120")
                ),
                bottom=40,
                right=20
            )
        ], height=160      
    )

    # Conteudo da pagina de agendamento de tarefa
    conteudo_agendamento = ft.Container(
        content=ft.Column(
            [
                in_nome_tarefa,
                in_descricao_tarefa,
                btn_editar,
                stk_tarefa,
                ft.ResponsiveRow(
                    [
                        out_data,
                        out_data_fim,
                        out_hora,
                        in_intervalo, 
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    spacing= 50,
                    col = 10
                ),
                chk_dias, 
                ft.Divider(opacity=0),
                ft.Stack(
                    [   
                        ft.Container(
                            bnt_criar_tarefa, 
                            alignment = ft.alignment.center
                        ), 
                        ft.Container(
                            icon_status_tarefa := ft.Icon(
                                name = ft.icons.RADIO_BUTTON_UNCHECKED,
                            ),
                            right=10,
                            top = 5
                        ),
                        ckb_sobrescrever_tarefa,  
                    ]  
                ),
                #ft.Divider(),
                ft.Stack(
                    [   ft.TextField(height=0, opacity= 0),
                        stk_config,    
                    ]
                ),     
            ]
        ),
        col=6,
        padding=ft.padding.only(top=57),
    )

    alerta_tarefa = ft.AlertDialog(
        title=ft.Text("Status da Tarefa"), 
        content= ft.Row(
            [
                icon_alerta_tarefa:=ft.Icon(),
                texto_alerta_tarefa:=ft.Text()
            ]
        )
    )
    alerta_envio_tarefa = ft.AlertDialog(
        title=ft.Text("Status de Envio"), 
        modal= True,
        content= ft.Row(
            [   
                ft.Stack([progresso := ft.ProgressRing(
                    width=25,
                    height=25,
                    stroke_width = 4,
                    visible = False
                    ),
                    icon_envio_tarefa := ft.Icon(size=25),
                    
                    ]),
                
                texto_envio_tarefa := ft.Text()
            ]
        ),
        actions=[
            bnt_cancelar_envio := ft.ElevatedButton("Cancelar", on_click=aborta_acao, visible = False),
            bnt_confirmar_envio := ft.OutlinedButton("Enviar", on_click=envia_email, visible = False),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Adiciona o cabeçalho e o conteudo do email por padrao
    page.add(out_header, conteudo_email)

    if len(sys.argv) > 1:
        #Execucao com argumentos passados
        argumento = sys.argv[1].replace('_', ' ')
        print('Execuçao programada: ', argumento )
        configura_campos(argumento, True) # O segundo arqumento informa se é uma execuçao programada

    elif len(sys.argv) == 1:
        print('Execuçao normal')
        configura_campos('Tarefa 1', False)

    page.update()
    

if __name__ == '__main__':
    ft.app(target = main)