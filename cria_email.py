import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class Email:
    def __init__(self, email_envio: str, senha: str, email_destino: str, email_cc: str, assunto: str, mensagem: str, caminho_anexo: list = None ) -> None:
        self.email_envio = email_envio
        self.senha = senha
        self.email_destino = email_destino
        self.email_cc = email_cc
        self.assunto = assunto
        self.mensagem = mensagem
        self.caminho_anexo = caminho_anexo
        self.connection = smtplib.SMTP(host='smtp.office365.com', port=587)
        self.mimemsg = MIMEMultipart()

    
    def cria_email(self) -> None:
        try:
            self.mimemsg['From'] = self.email_envio
            self.mimemsg['To'] = self.email_destino
            self.mimemsg['Cc'] = self.email_cc
            self.mimemsg['Subject'] = f'{self.assunto}'
            msg_html =  self.mensagem
            self.mimemsg.attach(MIMEText(msg_html, 'html'))

            for caminho_anexo in self.caminho_anexo:
                if caminho_anexo:
                    with open(caminho_anexo, 'rb') as anexo:
                        parte_anexo = MIMEApplication(anexo.read())
                        parte_anexo.add_header('Content-Disposition', f'attachment; filename={os.path.basename(caminho_anexo)}')

                    self.mimemsg.attach(parte_anexo)

        except Exception as e:
            print(e)


    def envia_email(self) -> bool:
        try: 
            self.connection.starttls()
            self.connection.login(self.email_envio,self.senha)
            self.connection.send_message(self.mimemsg)
            self.connection.quit()
            return True
        except Exception as e:
            print(e)
            return False


    def run(self) -> str:
        try:
            self.cria_email()
            if self.envia_email():
                #print('Email enviado com sucesso!')
                return '1'
            else:
                #print('Falha ao enviar o e-mail.')
                return '0'
                
        except Exception as e:
            #print('Falha: ', e)
            return e
            
        



if __name__ == '__main__':
    
    diretorio = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(dotenv_path= f'{diretorio}/.env', override=True)

    Email(
        email_envio= os.getenv('EMAIL'),
        senha=os.getenv('SENHA_EMAIL'),
        email_destino= os.getenv('EMAIL_DESTINO'),
        email_cc=os.getenv('EMAIL_CC'),
        assunto=f'Planilha de Atividades - Hiago Santos',
        mensagem="Mensagem teste",
        caminho_anexo=r'C:\Users\hiago\Downloads\1VIA-00020443157243.pdf'
        ).run()