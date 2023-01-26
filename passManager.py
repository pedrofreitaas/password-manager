from cryptography.fernet import Fernet
from shelve import open as shopen
from tkinter import Label, Entry, Button, Tk, Text, END, INSERT
from tkinter.font import Font
from re import match, sub
from os import remove, mkdir, system, path

configFileDisclaimer = '@Disclaimer: if the program is not working correctly, delete this file.'

class InvChar( ValueError ):
    def __init__(self, msg: str):
        self.msg = msg

class LongPassw( ValueError ):
    def __init__(self):
        return

class EmptyPassw( ValueError ):
    def __init__(self) -> None:
        return

class EmptyLogin( ValueError ):
    def __init__(self) -> None:
        return

class WrongMasterK( ValueError ):
    def __init__(self):
        return

class LoginAlredyExists( RuntimeWarning ):
    def __init__(self) -> None:
        return

class Pass_Manager():

    path = path.abspath(path.sep)+'/shelve'
    
    try:
        mkdir(path)
    except FileExistsError:
        pass
    
    system( f"attrib +h {path}" )
    shelve = shopen(f'{path}/passwords')
    
    fernet = 0
    masterK = b''
    passwSize = 10
    possibleChars = 'abcdefghijklmnopqrstuvwxyz1234567890-_ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    window_size = (1280,720)

    main_window = Tk()
    main_window.title('PassManager')
    main_window.geometry(str(window_size[0])+'x'+str(window_size[1]))
    main_window.minsize(window_size[0],window_size[1])
    main_window.state('zoomed')

    font = Font(main_window, family='Arial Black', size=8)
    
    # aux variable.
    temp_widgets = []

    # values.
    button_size = 248

# initialization procedures:
    def __init__(self):

        # main label.
        self.label = Label(self.main_window, text="Welcome to the password manager.", font=self.font)
        self.label.place(x=self.window_size[0]/2-125,y=20, width=250)

        # random password generator buttom.
        self.Rpassw_Button = Button(self.main_window, anchor='n', text="Click to create a random password.", command=lambda:self.demandMasterKey_begin(self.createRandomPassword_begin), font=self.font, borderwidth=3)
        self.Rpassw_Button.place(x=20,y=80,width=self.button_size)

        # delete register button.
        self.delete_register = Button(self.main_window, anchor='n', text="Click to delete a login/password.", command=lambda:self.demandMasterKey_begin(self.deleteRegister_begin), font=self.font, borderwidth=3)
        self.delete_register.place(x=268,y=80,width=self.button_size)

        # passwords's display button.
        self.see_passw_Button = Button(self.main_window, text="Click to see your passwords.", command=lambda:self.demandMasterKey_begin(self.displayPasswords), font=self.font, borderwidth=3)
        self.see_passw_Button.place(x=516,y=80,width=self.button_size)

        # user insert password button.
        self.user_input_pass = Button(self.main_window, text="Click to input a password.", command=lambda:self.demandMasterKey_begin(self.userInputPassword_begin), font=self.font, borderwidth=3)
        self.user_input_pass.place(x=764,y=80,width=self.button_size)

        # user set instance configs.
        self.change_configs = Button(self.main_window, text="Change configs.", command=lambda:self.demandMasterKey_begin(self.changeConfig), font=self.font, borderwidth=3)
        self.change_configs.place(x=1012,y=80,width=self.button_size)

        self.setFernet()
        self.setMasterK_begin()
        self.setConfig()

    def setFernet(self) -> None:
        """Sets a fernet for the passM instance."""

        if len(self.shelve) == 0:
            fernet_key = Fernet.generate_key()
            self.fernet = Fernet(fernet_key)

            self.shelve[ 'fernet_key' ] = fernet_key

            return

        self.fernet = Fernet( self.shelve['fernet_key'] )

    def masterK_key(self) -> str:
        """Returns the key to access if the masterK can be obtained, and \'\' otherwise."""

        for key in self.shelve:

            if key == 'fernet_key':
                continue

            if self.fernet.decrypt(key.encode()) == b'master_key':
                return key

        return ''

    def setConfig(self) -> None:
        """Sets the configs according to the config.txt file."""

        try:
            with open('configs.txt','r+') as fl:
                line = fl.readline()

                if len(line) == 0:
                    fl.write(f'Password max size = {self.passwSize}\n' + f'Allowed characters for passwords = "{self.possibleChars}"\n' + configFileDisclaimer)
                    fl.close()
                    self.setConfig()
                    return

                if match('Password max size = [1-9]{1}[0-9]*$', line):
                    self.passwSize = int(sub('Password max size = ', '', line))
                else:
                    raise AssertionError 
                
                line = fl.readline()

                if match('Allowed characters for passwords = "[a-zA-Z0-9-_]+"$', line):
                    self.possibleChars = sub('Allowed characters for passwords = "','',line)
                    self.possibleChars = sub('"\n','',self.possibleChars)
                else:
                    raise AssertionError            

        except FileNotFoundError:
            with open('configs.txt', 'w') as fl:
                pass

            self.setConfig()

        except AssertionError:
            with open('configs.txt', 'w') as fl:
                pass

            self.setConfig()
# ------------------------------------------------------------------------------------------------------

    def checkLogin(self, login_enc: bytes) -> None:
        """Checks if the login is valid, and launches the according exception based on the found invalidation."""
        
        if self.fernet.decrypt(login_enc) == b'':
            raise EmptyLogin

        keysList = list(self.shelve.keys())

        for index, key in enumerate(keysList):
            if key!='fernet_key':
                keysList[index] = self.fernet.decrypt(key.encode())

        # checking if the decryption of the login in alredy storaged.
        if self.fernet.decrypt(login_enc) in keysList:
            raise LoginAlredyExists

    def checkPassword(self, passw: str) -> None:
        """Checks if the passw is valid, and throws exceptions according to invalidation, if it exists."""

        if passw == '':
            raise EmptyPassw

        if len(passw) > self.passwSize:
            raise LongPassw()

        for char in passw:
            if char not in self.possibleChars:
                raise InvChar( 'Character not allowed: ' + char )

    def demandConfirmation(self, pos: tuple, func_yes, func_no):
        """Create a confirm and deny button.\n
           If the deny is pressed, the func_no method is called.\n
           If the confirm is pressed, the func_yes method is called."""

        yesB = Button(self.main_window, text='Confirm', command=func_yes)
        yesB.place(x=pos[0],y=pos[1],width=80)
        self.temp_widgets.append(yesB)

        noB = Button(self.main_window, text='Deny', command=func_no)
        noB.place(x=pos[0]+80,y=pos[1],width=80)
        self.temp_widgets.append(noB)
       
    def getLogin(self, entry: Entry, pos: tuple, func_success, func_error) -> None:
        """Gets the login and checks it.\n
           
           pos -> indicates position of the labels indicating possible login input erros.\n
           func_sucess -> function to be called if the login is valid.\n
           func_error -> function to be called if a login input error is found."""
        
        login_enc = self.fernet.encrypt( entry.get().encode() )

        # OBS: all the labels below self destruct after 5 seconds.
        try:
            self.checkLogin(login_enc)

        except LoginAlredyExists:
            lb = Label(self.main_window, text='Login alredy exists in the system. Delete the existing one to conclude this operation.')
            lb.place(x=pos[0],y=pos[1])
            self.temp_widgets.append(lb)
            
            lb.after(5000, lambda: lb.destroy())

            return func_error()

        except EmptyLogin:
            lb = Label(self.main_window, text='Login is empty. Please digit it again.')
            lb.place(x=pos[0],y=pos[1])
            self.temp_widgets.append(lb)

            lb.after(5000, lambda: lb.destroy())
            
            return func_error()

        return func_success()

    def getPassword(self, entry: Entry, pos: tuple, func_success, func_error) -> None:
        """Gets the password and checks it.\n
           
           pos -> indicates position of the labels indicating possible password input erros.\n
           func_sucess -> function to be called if the password is valid.\n
           func_error -> function to be called if a password input error is found"""
        
        try:
            self.checkPassword(entry.get())

        except LongPassw:
            text = f'Password digited is too long. The max size is: {self.passwSize}.'
            lb = Label(self.main_window, text=text)
            lb.place(x=pos[0],y=pos[1])
            
            lb.after(5000, lambda: lb.destroy())

            return func_error()        

        except InvChar as e:
            lb = Label(self.main_window, text=e.msg)
            lb.place(x=pos[0],y=pos[1])
            
            lb.after(5000, lambda: lb.destroy())

            return func_error()

        except EmptyPassw:
            lb = Label(self.main_window, text='Empty password.')
            lb.place(x=pos[0],y=pos[1])
            
            lb.after(5000, lambda: lb.destroy())

            return func_error()

        return func_success()

    def destroyWidgets(self, WidgList: list) -> None:
        """Destroy all the widgets inside a list of widgets."""

        for widg in WidgList:
            widg.destroy()

    def destroyTempWidgets(self) -> None:
        """Calls the self.destroyWidgets method for the temp_widgets of the instance."""

        self.destroyWidgets( self.temp_widgets )
   
    def run(self) -> None:
        """Run the tk.Tk() loop."""

        self.main_window.mainloop()

    def __del__(self):
        self.shelve.close()
# ------------------------------------------------------------------------------------------------------

# procedures that are core:
# Register removal:
    def deleteRegister_begin(self) -> None:
        """Creates the entry for the user to input the Register to be deleted."""
        
        self.destroyTempWidgets()

        entry = Entry(self.main_window, width=50)
        self.temp_widgets.append(entry)
        entry.insert(0, 'Digit the login to delete register.')
        entry.bind('<Return>', lambda event: self.deleteRegister_final(entry) )
        entry.place(x=20,y=150)

    def deleteRegister_final(self, entry: Entry) -> None:
        """If the Register of the input exists, demand the masterK. If the masterK is right, deletes the register.\n
           If the Register of the input doesn't exits, show an error message."""

        for key in self.shelve.keys():
            if key == 'fernet_key':
                continue
            
            if self.fernet.decrypt( key.encode() ).decode() == entry.get():
                deny = lambda: self.destroyWidgets(self.temp_widgets[len(self.temp_widgets)-2:])
                confirm = lambda: (self.destroyTempWidgets(), self.shelve.pop(key))

                self.demandConfirmation([20,200], confirm , deny) 
                return

        entry.delete(0, END)
        entry.insert(0, 'Register not found.')
# ------------------------------------------------------------------------------------------------------
# Passwords display:
    def displayPasswords(self) -> None:
            """Displays the passwords."""

            self.destroyTempWidgets()

            # the widgets here declared are only destroyed by the hideButton's command.

            pos = [780, 180]

            TextWidget = Text(self.main_window) 
            TextWidget.place(x=pos[0],y=pos[1])

            # getting all login/password into one string.
            for login in list(self.shelve):

                if login in ['fernet_key']:
                    continue
                
                if self.fernet.decrypt( login.encode() ) == b'master_key':
                    continue

                TextWidget.insert(INSERT, self.fernet.decrypt( login.encode() ).decode() + ': ' + self.fernet.decrypt(self.shelve[login]).decode() + '\n')

            TextWidget.config(state='disabled')

            hideButton = Button(self.main_window, text='Hide.', borderwidth=5)
            hideButton.config(command= lambda x=[TextWidget, hideButton]: self.destroyWidgets(x))
            hideButton.place(x=pos[0]+70,y=pos[1]-60)
# ------------------------------------------------------------------------------------------------------
# Random password generator:
    def createRandomPassword_begin(self) -> None:
        """Creates a random password and saves it in the instance."""

        self.destroyTempWidgets()

        pos = [20, 250]

        entry = Entry(self.main_window, width=45)
        entry.insert(0, 'Digit the login for the password here.')
        entry.bind('<Return>', lambda event: self.getLogin(entry, [0,200], lambda: self.createRandomPassword_final(entry), lambda: None ) )
        entry.place(x=pos[0],y=pos[1])
        self.temp_widgets.append(entry)
    
    def createRandomPassword_final(self, entry: Entry()) -> None:
        """Generates random passw for the entry and saves the register."""

        # getting login and generating passw.
        login = self.fernet.encrypt( entry.get().encode() ).decode()
        random_passw = self.fernet.encrypt( self.fitPassword(Fernet.generate_key().decode()).encode() )

        success_lb = Label(self.main_window, text='Added random password for login: '+entry.get())
        success_lb.place(x=0,y=200)
        success_lb.after(5000, lambda: success_lb.destroy())
        self.temp_widgets.append(success_lb)

        self.shelve[login] = random_passw

    def fitPassword(self, passw: str) -> str:
        """Makes sure that the propreties of the parameter don't violate the terms of the instance,
           such as passw size, passw allowed chars..."""

        # only allowed chars are going to be in the final passw.
        for char in passw:
            if char not in self.possibleChars:
                passw = passw.replace(char, '', 1)

        # the passw won't be longer than the instance defined size.
        passw = passw[0:self.passwSize]
        
        return passw
# ------------------------------------------------------------------------------------------------------
# User input password:
    def userInputPassword_begin(self) -> None:
        """Creates the entry responsible for getting the login for the user input password.\n
           Creates an entry that calls the middle part of the proccess if the login is valid.\n
           If it isn't valid call itselft again."""

        self.destroyTempWidgets()

        pos = [20,150]

        login_entry = Entry(self.main_window)
        login_entry.insert(0, 'Digit login.')
        login_entry.bind( '<Return>', lambda ev, ent=login_entry: self.getLogin(ent, [pos[0], pos[1]+50], lambda: self.userInputPassword_middle(ent), lambda: self.userInputPassword_begin) )
        login_entry.place(x=pos[0], y=pos[1])
        self.temp_widgets.append(login_entry)

    def userInputPassword_middle(self, login_entry: Entry) -> None:
        """Creates the entry responsible for getting the password for the user input password.\n
           Creates an entry that calls the middle part of the proccess if the password digited is valid.\n
           If it isn't valid call itselft again."""

        pos = [20,200]
        
        text = f'Allowed chars: "{self.possibleChars}".\nMax size: {self.passwSize}.'
        lb = Label(self.main_window, text=text)
        lb.place(x=pos[0], y=pos[1])
        self.temp_widgets.append(lb)

        passw_entry = Entry(self.main_window)
        passw_entry.insert(0, 'Digit password.')
        passw_entry.bind( '<Return>', lambda event: self.getPassword( passw_entry, [pos[0], pos[1]+150], lambda: self.userInputPassword_final(login_entry, passw_entry), lambda: self.userInputPassword_middle(login_entry) ) )
        passw_entry.place(x=pos[0], y=pos[1]+100)
        self.temp_widgets.append(passw_entry)

    def userInputPassword_final(self, login_ent: Entry, passw_entry: Entry) -> None:
        """Sets the password and destroys all the auxiliar created widgets."""

        self.shelve[ self.fernet.encrypt( login_ent.get().encode() ).decode() ] = self.fernet.encrypt( passw_entry.get().encode() )
        
        self.destroyTempWidgets()
# ------------------------------------------------------------------------------------------------------
# Set Master Key:
    def setMasterK_begin(self) -> None:
        """Checks if there is a masterK in the system, if so just sets the instance masterK to be the storaged one.
           If there is no masterK, continues the process to the middle function to create one."""

        # getting the key to the masterK.
        key = self.masterK_key()

        # verifying if the masterK is alredy defined
        if key != '':
            self.masterK = self.shelve [ key ]
            return
        
        # creating the masterK.
        text = """The master key of this program is not yet set. Digit it in the camp bellow\nand remember to note this password. If you can\'t digit it when needed, for\nany reason, you won\'t be able to use the program, and you will have to reset it."""
        lb = Label(self.main_window, text=text)

        lbSize = [425,100]
        lbPos = [ self.window_size[0]/2-lbSize[0]/2, self.window_size[1]/2 - lbSize[1]/2 ]

        lb.place(x=lbPos[0],y=lbPos[1],width=lbSize[0],height=lbSize[1])

        self.temp_widgets.append( lb )

        entry = Entry(self.main_window, width=60)
        entry.insert(0, 'Digit the master key in here.')
        entry.bind('<Return>', lambda event, entry = entry: self.setMasterK_middle(entry) )
        
        entrySize = [250,20]
        entryPos = [lbSize[0]/2-entrySize[0]/2 + lbPos[0], lbPos[1]+lbSize[1]]
        
        entry.place(x=entryPos[0],y=entryPos[1],width=entrySize[0],height=entrySize[1])
        
        self.temp_widgets.append( entry )

    def setMasterK_middle(self, entry: Entry()) -> None:
        """Confirms if the user really wants to use the digited masterK.
           If false: restarts the obtaining of the masterK.
           If true: calls the final part of the process."""

        lb = Label(self.main_window, text='Are you sure?')
        lb.place(x=entry.winfo_x(), y=entry.winfo_y()+20)
        self.temp_widgets.append(lb)

        confirmButton = Button(self.main_window, text='Yes',borderwidth=5)
        self.temp_widgets.append(confirmButton)

        denyButton = Button(self.main_window, text='No',borderwidth=5)
        self.temp_widgets.append(denyButton)

        confirmButton.config( command= lambda passw = entry.get(): self.setMasterK_final(passw) )
        denyButton.config( command=lambda list = [denyButton,confirmButton, lb]: self.destroyWidgets(list) )

        confirmButton.place(x=entry.winfo_x(), y=entry.winfo_y()+40,width=40)
        denyButton.place(x=entry.winfo_x()+40, y=entry.winfo_y()+40,width=40)

    def setMasterK_final(self, passw: str) -> None:
        """Sets the masterK digited by the user."""

        self.destroyTempWidgets()
        self.masterK = self.fernet.encrypt( passw.encode() )
        self.shelve[ self.fernet.encrypt(b'master_key').decode() ] = self.masterK
# ------------------------------------------------------------------------------------------------------
# Demand master Key:
    def demandMasterKey_begin(self, func) -> None:
        """Creates the entry that will take the input from the user."""

        self.destroyTempWidgets()

        pos = [20,150]

        entry = Entry(self.main_window)
        entry.insert(0, 'Digit master key.')
        entry.bind('<Return>', lambda event: self.demandMasterKey_final(entry, func))
        entry.place(x=pos[0],y=pos[1], width=400, height=20)
        self.temp_widgets.append(entry)

    def demandMasterKey_final(self, entry: Entry, func) -> None:
        """Executes the func : function in the parameter if the masterK was correctly digited.\n
           If the digited masterK isn't right, shows an error message."""

        # if masterK isn't set.
        if self.masterK == b'':
            entry.delete(0, END)
            entry.insert('Master Key isn\'t yet set.')
            return

        # executing if the masterK is correct.
        if entry.get() == self.fernet.decrypt(self.masterK).decode():
            func()
            entry.destroy()
            return
        
        # masterK incorrect msg.
        entry.delete(0,END)
        entry.insert(0, 'Incorrect master Key.')
# ------------------------------------------------------------------------------------------------------
# Change configuration procedure:
    def changeConfig(self) -> None:
        """Creates the buttons for changing the configs of the instance."""

        temp = Entry(self.main_window)
        temp.insert(0, 'Allowed Chars: '+self.possibleChars+'\tMax password size: '+str(self.passwSize))
        temp.config(state='readonly')
        self.temp_widgets.append(temp)
        temp.place(x=20,y=160,width=700)

        charsEntry = Entry(self.main_window)
        self.temp_widgets.append(charsEntry)
        charsEntry.insert(0, 'Digit the new allowed chars.')
        charsEntry.bind('<Return>', lambda event: self.changeAllowedChars(charsEntry))
        charsEntry.place(x=20,y=200,width=600)

        sizeEntry = Entry(self.main_window)
        self.temp_widgets.append(sizeEntry)
        sizeEntry.insert(0, 'Digit the new max size for passwords.')
        sizeEntry.bind('<Return>', lambda event: self.changePasswordSize(sizeEntry))
        sizeEntry.place(x=20,y=250,width=300)

    def changeAllowedChars(self, entry: Entry) -> None:
        """Checks if the digited chars in the entry are valid.
           If so, change the possibleChars to make passwords.
           If not, show an error message in the entry box."""

        temp = entry.get()

        # checking if it matches the program permited chars.
        if not match("[a-zA-Z0-9-_]+$", temp):
            entry.delete(0, END)
            entry.insert(0, '[a-z] or [A-Z] or - or _ .')
            return

        self.possibleChars = temp
        entry.delete(0, END)
        entry.insert(0, 'Possible characters altered.')
        remove('configs.txt')

        self.setConfig()

    def changePasswordSize(self, entry: Entry) -> None:
        """Checks if the digited chars in the entry are valid.
           If so, change the passwSize to make passwords.
           If not, show an error message in the entry box."""
        
        # checking if it can be converted to a positive integer.
        if not match('[1-9]{1}[0-9]*$', entry.get()):
            entry.delete(0, END)
            entry.insert(0, 'Should be a positive integer.')
            return

        self.passwSize = int(entry.get())
        entry.delete(0, END)
        entry.insert(0, 'Max size altered.')
        remove('configs.txt')

        self.setConfig()
# ------------------------------------------------------------------------------------------------------