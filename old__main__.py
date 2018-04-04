import os
import os.path
import subprocess
import pandas
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty


# A dialog box for confirming you want to kill a session.
class ConfirmPopup(BoxLayout):
    text = StringProperty()
    title = StringProperty()
    data = StringProperty()

    def __init__(self, callback, **kwargs):
        self.callback = callback
        self.orientation = 'vertical'
        super(ConfirmPopup, self).__init__(**kwargs)
        self.add_widget(Label(text=self.text))
        yesno = GridLayout(cols=2)
        btnyes = Button(text='Yes')
        yesno.add_widget(btnyes)
        btnno = Button(text='No')
        yesno.add_widget(btnno)

        self.add_widget(yesno)

        self.popup = Popup(title=self.title,
                           content=self,
                           size_hint=(None, None),
                           size=(480, 200),
                           auto_dismiss=False)
        btnyes.bind(on_release=self.choseyesno)
        btnno.bind(on_release=self.popup.dismiss)
        self.popup.open()

    def choseyesno(self, yn):
        # print(yn.text)
        self.callback(self.data)
        self.popup.dismiss()


# Makes the main table of the app
class MakeTable(BoxLayout):
    def appeandtotable(self, output, server, table):
        for line in output.splitlines():
            # print(type(line))
            line = line.decode("utf-8")
            if line.startswith(' ica-cgp#'):
                for i in range(30, 1, -1):
                    line = line.replace(" " * i, "|")
                if line[-1:] == "|":
                    line = line + server
                else:
                    line = line + "|" + server
                cells = line.split("|")
                # print(line)
                table.append(cells)

    # Launches a dialog box for confirming you want to kill a session.
    def confirmkillsession(self, instance):
        data = instance.__name__

        ConfirmPopup(self.killsession, text='Do You Want To Kill This Session?', title="Kill Session?", data=data)

    # Kills a windows user session based on the ID
    def killsession(self, session):
        data = session.split("|")
        command = ("LOGOFF {} /server:{}").format(data[0], data[1])
        # print(command)
        os.system(command)
        self.__init__()

    # Refreshes the list of users
    def refreshsession(self, instance):
        instance.text = "Refreshing"

        df = self.filldata(self.txtservers.text)

        self.databox.clear_widgets()

        for index, row in df.iterrows():
            if row['SERVER'] is not None:
                grid = GridLayout()
                grid.cols = 3
                btnkill = Button(text="Kill Session: {}".format(row['ID']))
                btnkill.__name__ = "{}|{}".format(row['ID'], row['SERVER'])
                btnkill.bind(on_press=self.confirmkillsession)
                grid.add_widget(btnkill)
                lbluser = Label(text=row['USERNAME'])
                grid.add_widget(lbluser)
                lblserver = Label(text=row['SERVER'])
                grid.add_widget(lblserver)
                self.databox.add_widget(grid)

        instance.text = "Refresh"
        print("Refresh")

    # Gets the data from a windows QWINSTA command
    def filldata(self, svrs):
        if len(svrs) > 0:
            print(svrs)
            servers = svrs.split(" ")
            table = []
            for server in servers:
                try:
                    output = subprocess.check_output("QWINSTA /server:{}".format(server), shell=False)
                    self.appeandtotable(output, server, table)
                except:
                    print("Server: {} - Does Not Exists".format(server))
            if len(table) > 0:
                df = pandas.DataFrame(table)
                new_header = ["SESSIONAME", "USERNAME", "ID", "STATE", "TYPE", "SERVER"]
                df.columns = new_header  # set the header row as the df header
                df = df.sort_values(['USERNAME', "ID", 'SERVER'])
                # print(df)
                return df
            else:
                df = pandas.DataFrame()
                return df
        else:
            df = pandas.DataFrame()
            return df

    # Application Init
    def __init__(self, **kwargs):
        super(MakeTable, self).__init__(**kwargs)

        self.clear_widgets()
        self.orientation = 'vertical'

        header = BoxLayout()
        header.orientation = 'vertical'

        servergrid = GridLayout()
        servergrid.cols = 3
        lblservers = Label(text="Servers: ")
        servergrid.add_widget(lblservers)
        self.txtservers = TextInput(text='', multiline=True)
        servergrid.add_widget(self.txtservers)
        header.add_widget(servergrid)

        # Loads server names from a file if it exists
        fname = "servers.txt"
        if os.path.isfile(fname):
            with open(fname) as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            self.txtservers.text = " ".join(content)
        else:
            print("No Servers File Found")


        btnrefresh = Button(text="Refresh")
        btnrefresh.id = "btnRefresh"
        btnrefresh.bind(on_press=self.refreshsession)
        header.add_widget(btnrefresh)

        self.add_widget(header)

        self.databox = BoxLayout()
        self.databox.clear_widgets()
        self.databox.orientation = 'vertical'

        self.add_widget(self.databox)

        self.refreshsession(self)


class UserControl(App):
    def build(self):
        return MakeTable()


if __name__ == 'old__main__':
    UserControl().run()
