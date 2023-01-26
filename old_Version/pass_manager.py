from os import system as s
from random import SystemRandom
import os

all_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
all_numbers = "1234567890"
all_symbols = ".,;:!@#+-*/[]=$%&()^"

# aux functions
# find first occurence of subs and cuts every char before it (including the subs), if the subs not found, returns the given str.
def cut_str(str, subs):
        index = str.find(subs)
        if index == -1:
            return str
        
        return str[ index + len(subs) : ]

# Pre-condition: str has to have length that % 9 == 0. 
# changes the order of the string if flag, changes back if not flag
def change_str(str, flag):
    # not possible to operate
    if len(str) % 9 != 0:
        return str

    str2 = ""
    old_index = 0

    if flag == True:
        for index in range(0,len(str),9):
            str2 += str[index+5] + str[index+3] + str[index+1] + str[index+8] + str[index+6] + str[index+2] + str[index+4] + str[index] + str[index+7]
            old_index += 9
    else: 
        for index in range(0,len(str),9):
            str2 += str[index+7] + str[index+2] + str[index+5] + str[index+1] + str[index+6] + str[index] + str[index+4] + str[index+8] + str[index+3]
            old_index += 9
    
    return str2

# Class that will manage the passwords, needs a config.txt file.
class Pass_Manager():
    def __init__(self):
        #creating the passwords folder
        if not os.path.exists("passwords"):
            os.mkdir("passwords")

        self.master_password_file = "passwords/password_master.psw"
        self.passwords_file = "passwords/passwords.psw"
        self.config_file = "configs.txt"

        #creating the files
        if not os.path.exists(self.config_file):
            self.set_config_default()
        if not os.path.exists(self.master_password_file):
            file = open(self.master_password_file,"w")
            file.close()
        if not os.path.exists(self.passwords_file):
            file = open(self.passwords_file,"w")
            file.close()

        self.file_line_length = 207

        self.master_key = ""

        self.reset_warning_msg = """*********************************************************************
                                  \r* Você digitou a super senha incorretamente. Por isso o processo    *
                                  \r* não pôde ser concluído.                                           * 
                                  \r* -> Caso tenha perdido a super senha por algum motivo, nada nesse  *  
                                  \r* programa poderá ser acessado. Logo, é recomendado que você reins- *
                                  \r* tale o programa, reiniciando seus dados no processo.              *
                                  \r*********************************************************************\n"""

        self.back_to_start_page_msg = """***************************************************
                                       \r*        Voltando a tela inicial.                 *
                                       \r***************************************************\n"""

        self.master_key_msg = """*************************************************************
                               \r*              Digite a super senha:                        *
                               \r* -> Observações:                                           * 
                               \r* Lembre-se dessa senha, já que sem ela você não terá aces- *  
                               \r* so a boa parte das funcionalidades do programa, e se você *
                               \r* optar por redefinir a super senha, todos os dados do pro- *
                               \r* grama serão reiniciados com a redefinição.                *
                               \r************************************************************\n"""

        self.change_master_key_msg = """***************************************************************
                                      \r* Observações para mudança de super senha:                    * 
                                      \r* -> Para muda-la, será necessária a antiga super senha.      *  
                                      \r* -> Todas as configurações e senhas salvas nesse programa    *
                                      \r* permanecerão intactas no final do processo.                 *
                                      \r* -> Caso não se lembre da senha, tente continuar o processo  *
                                      \r* e considere realizar o procedimento descrito ao final dele. *
                                      \r*                                                             *
                                      \r* -> Tem certeza que deseja mudar sua super senha? (Sim,Não)  *
                                      \r**************************************************************\n"""

        self.start_message = """***************************************
                              \r* Bem vindo ao gerenciador de senhas! *
                              \r***************************************\n"""

        self.reconfiguration_msg = """***************************************
                                    \r*      Página de reconfiguração       *
                                    \r***************************************\n
                                    \r-> Você gostaria de?
                                    \r# Mudar caracteres disponíveis (1)
                                    \r# Configurar o tamanho das senhas geradas (2)
                                    \r# Mudar super senha. (3)
                                    \r# Voltar à página inicial (4)\n"""
                                
        self.chars_change_msg = """**********************************************************
                                 \r* Deseja digitar quais são os caracteres permitidos? (1) *
                                 \r* Deseja excluir os caracteres que serão digitados?  (2) *
                                 \r* Deseja adicionar os caracteres digitados?          (3) * 
                                 \r* Deseja resetar para a configuração original?       (4) *
                                 \r* Deseja voltar à página anterior?                   (5) *                                                      
                                 \r**********************************************************\n"""

        self.add_password_msg = """**********************************************************
                                 \r* Deseja digitar a senha?                            (1) *
                                 \r* Deseja definir aleatoriamente?        (recomendado)(2) *  
                                 \r* Deseja cancelar operação?                          (3) *                                                     
                                 \r**********************************************************\n"""
        
        self.existing_login_msg = """**********************************************************
                                   \r* Login digitado já existe no sistema!                   *
                                   \r* Deseja redefinir senha? (Exige super senha)        (1) *  
                                   \r* Deseja excluir senha?   (Exige super senha)        (2) *
                                   \r* Deseja voltar a página anterior?                   (3) *                                                   
                                   \r**********************************************************\n"""
        
        self.numbers = ""
        self.letters = ""
        self.symbols = ""
        self.password_lenght = 0

        self.set_chars()

        self.passwords = dict()
        self.get_passwords()

    def save_password_in_file(self, enc_password, file_path):
        # generate random numbers safely
        crypto = SystemRandom()

        rand = crypto.randint(0, self.file_line_length - len(enc_password))
        rest = self.file_line_length - rand - len(enc_password)

        all_chars = self.all_available_caracteres().replace(" ","")

        self.mess_the_file(file_path)

        str = ""
        for x in range(rand):
            str += ( all_chars[crypto.randint(0, len(all_chars) - 1)] )

        str += enc_password

        for x in range(rest):
            str += ( all_chars[crypto.randint(0, len(all_chars) - 1)] )

        str = change_str(str, True)

        with open(file_path, "a") as passwords_file:
            passwords_file.write(str + "\n")

        self.mess_the_file(file_path)

# master key --------------------------------#
    #checks if it exists in the system
    def check_master_key(self):
        #define master key

        self.get_master_key()

        #master key not defined yet
        if self.master_key == "":
            flag = "UNDEFINED"

            while flag != "Sim" and flag != "S" and flag != "s" and flag != "sim":
                s("cls")
                key = input( self.master_key_msg )
                flag = input(f"Tem certeza que deseja utilizar {key} como sua super senha? (Sim / Não)\n")

                if not self.check_if_valid( key ):
                    flag = "Não valida"
            
            self.master_key = self.password_encrypt( key )

            self.save_master_key_in_file()

            self.clear_the_file(self.passwords_file)
            self.passwords = dict()

            self.clear_the_file(self.master_password_file)

            input("Super senha definida com sucesso, pressione enter para prosseguir.")
            
            #master key was defined here
            return 1

        #master key was alredy defined
        return 0

    def get_master_key(self):

        with open(self.master_password_file,"r") as passwords_file:
            line = passwords_file.readline()

            while line != "":
                line = change_str(line.replace("\n",""), False)

                cutted_line = cut_str(line, "<")

                # there isn't a password in this line
                if line == cutted_line:
                    line = passwords_file.readline()
                    continue

                self.master_key = cutted_line[ : cutted_line.find("<")]
                line = passwords_file.readline()
            
                return 1
            return 0

    def save_master_key_in_file(self):
        self.clear_the_file( self.master_password_file )
        self.save_password_in_file("<" + self.master_key + "<", self.master_password_file)

    def demand_master_key(self):
        tries = 0

        while True:
            if tries >= 3:
                input("""*****************************************
                       \r*Você errou três vezes, operação falhou.*
                       \r*****************************************\n""")
                return 0

            s("cls")
            answer = input(f"""******************************************
                            \r*  Digite a super senha. ({3-tries} tentativas)  *
                            \r******************************************\n""")

            if self.password_encrypt( answer ) == self.master_key:
                return 1
            else:
                tries += 1

    def change_master_key(self):
        invalid_option = False

        while True:
            s("cls")
            answer = (input(self.change_master_key_msg))

            #checking answer
            if invalid_option:
                print('Opção anterior inválida, por favor, redigite o comando.')
                invalid_option = False
            
            #Deseja redefinir super senha
            if answer == "Sim" or answer == "S" or answer == "sim" or answer == "s":
                
                if not self.demand_master_key():
                    input( self.reset_warning_msg )
                    break

                while True:
                    master_key = input("Digite a nova super senha: ")

                    if self.check_if_valid(master_key):
                        self.master_key = self.password_encrypt( master_key )
                        self.save_master_key_in_file()

                        input("Super senha redefinida com sucesso, e dados do programa permaneceram intactos.")

                        break
                break

            #Deseja não redefinir a senha
            if answer == "Não" or answer == "N" or answer == "não" or answer == "n":
                break

            else:
                invalid_option = True
                continue
#--------------------------------------------#

    # self.numbers + self.letters + self.symbols + " "
    def all_available_caracteres(self):
        return self.numbers + self.letters + self.symbols + " "

    def crypto_login(self):
        # The messy str is the result of the change between the odd indexes and the pair ones
        str = all_numbers + all_symbols + all_letters

        pair_indexes = str[0:len(str):2][::-1]
        odd_indexes = str[1:len(str):2]

        messy_str = pair_indexes + odd_indexes

        return messy_str

    def crypto_password(self):
        str = self.crypto_login()

        pair_indexes = str[0:len(str):2]
        odd_indexes = str[1:len(str):2][::-1]

        messy_str = pair_indexes + odd_indexes

        return messy_str

    def set_chars(self):
        with open( self.config_file, "r" ) as configs_file:
            #numbers setup
            numbers_line = configs_file.readline()[8:-1]

            for number in numbers_line:
                if number in all_numbers:
                    self.numbers += str(number)

                if number == '\n':
                    break
            
            #letters setup
            letters_line = configs_file.readline()[8:-1]
            
            for letter in letters_line:
                if letter in all_letters:
                    self.letters += str(letter)

                if letter == '\n':
                    break
                
            #symbols setup
            symbols_line = configs_file.readline()[8:-1]
            
            for symbol in symbols_line:
                if symbol in all_symbols:
                    self.symbols += str(symbol)

                if symbol == '\n':
                    break
            
            #pass len
            pass_len_line = configs_file.readline()[14:-1]
            self.password_lenght = int(pass_len_line)

    def set_config_default(self):
        with open( self.config_file, "w" ) as configs_file:
            configs_file.write("Numbers: " + "\"" + all_numbers + "\"\n")
            configs_file.write("Letters: " + "\"" + all_letters + "\"\n")
            configs_file.write("Simbols: " + "\"" + all_symbols + "\"\n")
            configs_file.write("Password size: " + str(10) + "\n")

    def set_config(self):
        with open( self.config_file, "w" ) as configs_file:
            configs_file.write("Numbers: " + "\"" + self.numbers + "\"\n")
            configs_file.write("Letters: " + "\"" + self.letters + "\"\n")
            configs_file.write("Simbols: " + "\"" + self.symbols + "\"\n")
            configs_file.write("Password size: " + str(self.password_lenght) + "\n")

#encrypt <-> decrypt login, passwords
    def login_encrypt(self, login):
        enc_login = ""

        crypto = self.crypto_login()

        for char in login:
            index = self.all_available_caracteres().find(char)
            enc_login += crypto[index]
        
        enc_login = enc_login[::-1]
    
        return enc_login
    
    def login_decrypt(self, enc_login):
        login = "" 

        crypto = self.crypto_login()

        all_chars = self.all_available_caracteres()

        for char in enc_login[::-1]:
            index = crypto.find(char)
            login += all_chars[index]

        return login

    def password_encrypt(self, password):
        enc_password = ""

        crypto = self.crypto_password()

        for char in password:
            index = self.crypto_login().find(char)
            enc_password += crypto[index]

        return enc_password

    def password_decrypt(self, enc_password):
        password = "" 

        crypto = self.crypto_password()

        for char in enc_password:
            index = crypto.find(char)
            password += self.crypto_login()[index]

        return password
#-----------------------------------------------------#

#handling passwords
    #doesn't decrypt
    def get_passwords(self):
        with open( self.passwords_file, "r" ) as passwords_file:
            line = passwords_file.readline()
            while line != "":
                line = change_str(line.replace("\n",""), False)

                cutted_line = cut_str(line, "<")
                
                # if there isn't any password in this line
                if line == cutted_line:
                    line = passwords_file.readline()
                    continue
                    
                login = cutted_line[ : cutted_line.find("<") ]

                cutted_line = cut_str(cutted_line, login + "<" )

                password = cutted_line[ : cutted_line.find("<") ]

                self.passwords[ login ] = password

                line = passwords_file.readline()
            
    def mess_the_file(self, file_name): 
        # safe random number generator
        crypto = SystemRandom()

        with open(file_name, "a") as file:
            random_chars = self.all_available_caracteres().replace(" ","")
            len_ = len(random_chars)

            random_number = crypto.randint(5000,50000)
            while random_number % self.file_line_length != 0:
                random_number = crypto.randint(5000,50000)

            for x in range(random_number):
                if x % self.file_line_length == 0 and x != 0:
                    file.write( "\n" )

                #writting random chars
                file.write( random_chars[crypto.randint(0, len_ - 1)] )

            file.write( "\n" )

    def clear_the_file(self, filename):
        with open(filename, "w") as file:
            file.write("")
        
    def save_passwords(self):
        #alredy cleans the file
        s("cls")
        msg = "Salvando dados do programa"
        
        self.save_master_key_in_file()

        # cleaning the passwords file
        self.clear_the_file(self.passwords_file)

        for key in self.passwords.keys():
            msg += "."
            s("cls")
            print(msg)

            self.save_password_in_file( "<" + key + "<" + self.passwords[ key ] + "<", self.passwords_file)
#---------------------------------------------#

#reconfig ------------------------------------------------#
    def set_password_length(self):
        invalid_option2 = False
        while True:
            if invalid_option2:
                print('Opção anterior era inválida, digite novamente.')
                invalid_option2 = False
            
            length = int(input("Digite o tamanho desejado para senha: (max=50) "))

            if length >= 1 and length <= 50:
                self.password_lenght = length
                break
            else:
                invalid_option2 = True
        
        #saving new info
        self.set_config()

    def change_chars(self, allowed_chars):
        self.numbers = self.letters = self.symbols = ""

        for char in allowed_chars:
            #checking if it's alredy the inserted
            if char in self.all_available_caracteres():
                continue

            if char in all_numbers:
                self.numbers += char
            elif char in all_letters:
                self.letters += char
            elif char in all_symbols:
                self.symbols += char

        #setting the update of configuration
        self.set_config()

    def exclude_chars(self, not_allowed_chars):
        for char in not_allowed_chars:
            if char in all_numbers:
                self.numbers = self.numbers.replace(char,"")

            if char in all_letters:
                self.letters = self.letters.replace(char,"")

            if char in all_symbols:
                self.symbols = self.symbols.replace(char,"")
        
        #setting the update of configuration
        self.set_config()

    def include_chars(self, new_allowed_chars):
        for char in new_allowed_chars:
            #checking if it's alredy the inserted
            if char in self.all_available_caracteres():
                continue

            if char in all_numbers:
                self.numbers += char
            
            if char in all_letters:
                self.letters += char
            
            if char in all_symbols:
                self.symbols += char
            
        #setting the update of configuration
        self.set_config()

    def set_all_possible_chars(self):
        self.numbers = all_numbers
        self.letters = all_letters
        self.symbols = all_symbols

    def change_available_chars( self ):
        invalid_option = False
        
        while True:
            #start procedure
            s("cls")
            print("\n-> Caracteres válidos: " + "\"" + self.letters + self.numbers + self.symbols + "\"\n")
            print(self.chars_change_msg)

            #invalid option procedure
            if invalid_option:
                print('Opção anterior inválida, por favor, redigite o comando.')
                invalid_option = False

            answer = int(input())

            #digit all the allowed chars
            if answer == 1:
                all_allowed_chars = input('Digite os caracteres permitidos: ')
                self.change_chars( str(all_allowed_chars) )
                continue
            
            #exclude the digited chars
            elif answer == 2:
                not_allowed_chars = input('Digite os caracteres que deseja excluir: ')
                self.exclude_chars( str(not_allowed_chars) )
                continue
            
            #add the digited chars
            elif answer == 3:
                new_allowed_chars = input('Digite os caracteres que deseja adicionar: ')
                self.include_chars( str(new_allowed_chars) )
                continue
            
            #set all the possible chars
            elif answer == 4:
                self.set_all_possible_chars()
                continue

            #go back to anterior page
            elif answer == 5:
                break
                
            # invalid_option
            else:
                invalid_option = True
                continue
#---------------------------------------------------------#

    # prints the passwords with the master key is digited correctly
    def print_all_passwords(self):
        if not self.demand_master_key():
            input(self.back_to_start_page_msg)
            return 0

        #digited the master key sucessfully
        s("cls")
        print("""-> Aqui estão todas as senhas registradas, exceto a super senha. 
               \r************************************************************************""")

        for password_key in self.passwords.keys():
            print("Login:", self.login_decrypt( password_key ) , "->", self.password_decrypt( self.passwords[password_key] ), '\n')

        input("************************************************************************")

    # generates random password
    def generate_password(self):
        password = ""

        #safe random number generator
        crypto = SystemRandom()

        for index in range(self.password_lenght):
            randomizer = crypto.randint(0, 600)
            random_char = ''

            if randomizer >= 0 and randomizer < 200:
                random_char = self.numbers[ crypto.randint(0, len(self.numbers) - 1) ]

            elif randomizer >= 200 and randomizer < 500:
                random_char = self.letters[ crypto.randint(0, len(self.letters) - 1) ]

            elif randomizer >= 500 and randomizer < 600:
                random_char = self.symbols[ crypto.randint(0, len(self.symbols) - 1) ]

            password += random_char

        return password

    #for the manually digited passwords
    def check_if_valid(self, password):
        for char in password:
            if not char in all_numbers and not char in all_letters and not char in all_symbols:
                input( "( " + char + " )" + " -> Não é possível usar esse caractere. " )
                return False
        return True

#existing login procedures --------------------#
    def change_password(self):
        if not self.demand_master_key():
            return 0

        return 1

    def exclude_password(self, enc_login):
        if not self.demand_master_key():
            input("""***************************************
                   \r* Senha não foi excluída com sucesso. *
                   \r***************************************\n""")
            return 0
        
        self.passwords.pop(enc_login)

        self.save_passwords()

        input("""***************************************
               \r*   Senha foi excluída com sucesso.   *
               \r***************************************\n""")

        return 0
        
    def existing_login(self, enc_login):
        invalid_option = False

        while True:
            s("cls")
            if invalid_option:
                print('Opção anterior inválida, por favor, redigite o comando.')
                invalid_option = False
            answer = int( input( self.existing_login_msg ) )
            
            #redefinir senha
            if answer == 1:
                return self.change_password()
            
            #excluir senha
            elif answer == 2:
                return self.exclude_password( enc_login )
            
            #voltar página
            elif answer == 3:
                break

            else:
                invalid_option = True
#----------------------------------------------#

    # adds a new normal password (doesn't deal with the master key)
    def add_password(self):
        #getting the login
        login = input("""*************************************************
                       \r* Digite o login, ou para que vai usar a senha. *
                       \r*************************************************\n""").replace(" ","")

        if self.login_encrypt(login) in self.passwords.keys():
            continue_function = self.existing_login( self.login_encrypt(login) )

            if not continue_function:
                return

        while True:
            invalid_option = False

            if invalid_option:
                print("-> Opção anterior inválida, favor digitar novamente.\n")
                invalid_option = False
            
            answer = int( input( self.add_password_msg ) )

            if answer == 1:
                password = input("Digite a senha desejada: ")

                while not self.check_if_valid(password):
                    password = input("Digite a senha desejada: ")

                break

            elif answer == 2:
                password = self.generate_password()
                break
            
            elif answer == 3:
                return

            elif login in self.passwords.keys():
                invalid_option = True
                continue

            else:
                invalid_option = True

        login = self.login_encrypt( login )
        password = self.password_encrypt( password )

        self.passwords[ login ] = password
        self.save_password_in_file( "login<" + login + ">,password<" + password + ">", self.passwords_file )

        input( "-> " + self.password_decrypt( password ) + " foi adicionada para o login: " + self.login_decrypt( login ) + ".(Press enter)")
       
#loops
    def config_loop( self ):
        is_reconfigurating = True
        invalid_option = False
        
        while is_reconfigurating:
            #start procedure
            s("cls")
            print(self.reconfiguration_msg)

            #invalid option procedure
            if invalid_option:
                print('Opção anterior inválida, por favor, redigite o comando.')
                invalid_option = False

            answer = int(input())

            #change available chars
            if answer == 1:
                self.change_available_chars()
                continue
            
            #change the size of the generated passwords
            elif answer == 2:
                #setting only possible values
                self.set_password_length()
                continue
            
            #change master key
            elif answer == 3:
                self.change_master_key()
                continue

            #go back to initial page
            elif answer == 4:
                break
            
            # invalid_option
            else:
                invalid_option = True
                continue

    def run(self):
        running = True

        invalid_option = False

        while running:
            #start procedure
            self.check_master_key()

            s("cls")

            print(self.start_message)
            print("Utilizando caracteres: \"" + self.all_available_caracteres() + "\".\n" +
                "Tamanho da senha: ", str(self.password_lenght) + ".\n")

            answer = int(input( "#Deseja criar uma senha? (1)\n" +
                                "#Deseja ver suas senhas? (2)\n" +
                                "#Reconfigurar gerador (3)\n"    +
                                "#Sair do programa (4)\n" ))

            #checking answer
            if invalid_option:
                print('Opção anterior inválida, por favor, redigite o comando.')
                invalid_option = False
            
            #Deseja criar senha
            if answer == 1:
                self.add_password()
                continue

            #Deseja ver senhas
            elif answer == 2:
                self.print_all_passwords()
                continue

            #Deseja reconfigurar
            elif answer == 3:
                self.config_loop()
                continue
            
            #Deseja sair
            elif answer == 4:
                running = False
                continue
            
            else:
                invalid_option = True
                continue
            
        self.save_passwords()