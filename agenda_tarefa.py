import pythoncom
import win32com.client as st

class Tarefa():
    def __init__(self,
                nome_tarefa: str = "Auto Email",
                desc_tarefa: str = "Tarefa agendada para executar o Auto Email",
                tipo_tarefa: str = "1",
                intervalo: int = '1',
                dias: list = [],
                inicio: str = "2100-01-01T08:00:00-00:00",
                fim: str = "2101-01-01T08:00:00-00:00",
                caminho_executavel:str = r'/',
                argumento: str = ''
                ):
        
        self.nome = nome_tarefa # Nome da Tarefa que será agendada, padrao é 'Auto Email'
        self.descricao = desc_tarefa
        self.tipo = tipo_tarefa # Tipo da tarefa (1) ->Uma vez, (2) ->Diariamente, (3) ->Semanalmente
        self.intervalo = int(intervalo)
        self.inicio = inicio
        self.dias = dias
        self.fim = fim
        self.exec_path = caminho_executavel
        self.argumento = argumento
        print('\nNome:',self.nome,'\nDesc:', self.descricao,'\nTipo:', self.tipo,'\nIntervalo:', self.intervalo,'\nInicio:', self.inicio,'\nDias:', self.dias,'\nFim:', self.fim,'\nPath:', self.exec_path)
   

    def converter_dias_para_valor(self, days_list: list) -> int:
        """
        Metodo responsavel por converter uma lista de dias da semana para o valor necessario para o agendador conforme a logica binaria.\n
        \tArgumentos: Lista de valores que representam os dias da semana escolhidos\n
        \tRetorno: Valor inteiro que representa o conjunto de dias escolhido\n
        \tExp.: (Seg, Ter, Sex, Dom) -> (2+3+32+1)
        \t \t         [2, 3, 6, 1]   ->    39
        """
        try:

            if isinstance(days_list[0], str) and days_list[0].isdigit():
                for i in range(len(days_list)):
                        days_list[i] = int(days_list[i])

            # Mapeamento dos dias da semana para os valores correspondentes
            dias_para_valor = {
                1 : 1,   # Domingo
                2 : 2,   # Segunda-feira
                3 : 4,   # Terça-feira
                4 : 8,   # Quarta-feira
                5 : 16,  # Quinta-feira
                6 : 32,  # Sexta-feira
                7 : 64   # Sábado
            }
            # Calcula o valor total somando os valores correspondentes aos dias selecionados
            valor_total = sum(dias_para_valor[dia] for dia in days_list)
            return valor_total
        except Exception as e:
            print(e)
            return 0


    def cria_tarefa(self) -> bool:
        try:
            pythoncom.CoInitialize()
            scheduler = st.Dispatch("Schedule.Service")
            scheduler.Connect('' or None, '' or None, '' or None, '' or None)
            self.rootFolder = scheduler.GetFolder("\\")
            
            taskDef = scheduler.NewTask(0)
            colTriggers = taskDef.Triggers
            
            # Tarefa de unica execuçao
            if self.tipo == '1': 
                trigger = colTriggers.Create(1)

            # Tarefa diaria
            if self.tipo == '2': 
                trigger = colTriggers.Create(2)
                trigger.DaysInterval = self.intervalo
                
            # Tarefa Semanal
            if self.tipo == '3':
                trigger = colTriggers.Create(3)
                trigger.WeeksInterval = self.intervalo
                trigger.DaysOfWeek = self.converter_dias_para_valor(self.dias)
            
            trigger.StartBoundary = self.inicio
            trigger.EndBoundary = self.fim
            trigger.Enabled = True
            
            colActions = taskDef.Actions
            action = colActions.Create(0) # Acao de Iniciar um programa
            action.Path = self.exec_path  # Caminho do programa
            action.Arguments = self.argumento # Argumento
            
            info = taskDef.RegistrationInfo
            info.Author = 'AutoEmail'
            info.Description = self.descricao
            
            
            taskDef.Settings.Hidden = False
            taskDef.Settings.StopIfGoingOnBatteries = False
            taskDef.Settings.Enabled = True
            
            resultado  = self.rootFolder.RegisterTaskDefinition(self.nome, taskDef, 6, "", "", 0)
            return True
        except Exception as e:
            print(e)
            return False


    def test_task(self) -> bool:
        try:
            task = self.rootFolder.GetTask(self.nome)
            task.Enabled = True
            task.Run("")
            task.Enabled = False
            #print('Tarefa verificada ')
            return True
        except Exception as e: 
            print(e)
            return False


    def run(self) -> bool:
        try:
            if self.cria_tarefa():
                #self.test_task()
                return True
            
            else: return False
        except: return False



if __name__ == '__main__':
    #print(Tarefa(tipo_tarefa = '3', dias=[1, 2, 3]).run())

    print(Tarefa(
        nome_tarefa='Auto Email',
        desc_tarefa='Tarefa agendada do Auto Email',
        tipo_tarefa='1',
        intervalo= '1',
        dias="[]",
        inicio='2023-11-25T17:39:00-03:00', 
        fim='', 
        #caminho_executavel= caminho_execucao~
        ).run())