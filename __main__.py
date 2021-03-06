import os
import os.path
import subprocess
import pandas
import wx
import datetime
import FrmMain


class Main(wx.Frame):
    def btnRefershClick(self, instance):
        self.refreshsession()

    def btnKillClick(self, instance):
        index = self.lcUsers.GetFocusedItem()
        if index >= 0:
            #print(index, self.lcUsers.GetItem(index, 2).GetText())
            user = self.lcUsers.GetItem(index, 1).GetText()
            sess_id = self.lcUsers.GetItem(index, 2).GetText()
            server = self.lcUsers.GetItem(index, 5).GetText()
            dlg = wx.MessageDialog(None, "Do you want to kill {}'s session?".format(user), 'Kill Session?', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()

            if result == wx.ID_YES:
                self.killsession(sess_id, server)
                self.refreshsession()
        else:
            self.statusBar.SetStatusText("No Session Selected")

    def btnClearClick(self, instance):
        self.lcUsers.DeleteAllItems()
        self.txtServers.SetValue("")
        self.statusBar.SetStatusText("")

    def resizeCols(self, cols):
        for i in range(cols):
            self.lcUsers.SetColumnWidth(i, -2)
            # self.lcUsers.SetColumnWidth(i, -1)

    def appeandtotable(self, output, server, table):
        for line in output.splitlines():
            # print(type(line))
            line = line.decode("utf-8")
            if line.startswith((' ica-cgp#', ' rdp-tcp#')):
                for i in range(30, 1, -1):
                    line = line.replace(" " * i, "|")

                line = line.rstrip("|")
                if line.startswith(' rdp-tcp#'):
                    line = line + "|RDP"

                line = line + "|" + server
                cells = line.split("|")
                # print(line)
                # print(cells)
                table.append(cells)

    # Refreshes the list of users
    def refreshsession(self):
        self.lcUsers.DeleteAllItems()
        df = self.filldata(self.txtServers.GetValue())

        new_header = ["SESSIONNAME", "USERNAME", "ID", "STATE", "TYPE", "SERVER"]
        df.columns = new_header  # set the header row as the df header
        df = df.sort_values(['USERNAME', "ID", 'SERVER'])

        for index, row in df.iterrows():
            if row['SERVER'] is not None:
                self.lcUsers.Append(row)

        self.resizeCols(len(df.columns))
        self.statusBar.SetStatusText("Table Updated: {}".format(datetime.datetime.now().strftime('%m-%d-%Y %H:%M:%S')))

    # Gets the data from a windows QWINSTA command
    def filldata(self, svrs):
        table = [["", "", "", "", "", ""]]
        # table = [["Test 1", "Test 2", "Test 3", "Test 4", "Test 5", "Test 6"],
        #          ["Test 1", "Test 2", "Test 3", "Test 4", "Test 5", "Test 6"]]
        df = pandas.DataFrame(table)
        new_header = ["SESSIONNAME", "USERNAME", "ID", "STATE", "TYPE", "SERVER"]
        df.columns = new_header  # set the header row as the df header
        table = []
        if len(svrs) > 0:
            # print(svrs)
            servers = svrs.split(" ")

            for server in servers:
                try:
                    self.statusBar.SetStatusText("Server: {} - Found!".format(server))
                    output = subprocess.check_output("QWINSTA /server:{}".format(server), shell=False)
                    # print(output)
                    self.appeandtotable(output, server, table)
                except:
                    self.statusBar.SetStatusText("Server: {} - Does Not Exists".format(server))

            # print(len(table))
            if len(table) > 0:
                # print(table)
                df = pandas.DataFrame(table)
                # df = df.sort_values(['USERNAME', "ID", 'SERVER'])
                print(df)
                return df
            else:
                print("DF Table is Empty")
                return df
        else:
            self.statusBar.SetStatusText("No Servers Given")
            return df

    # Kills a windows user session based on the ID
    def killsession(self, id, server):
        command = ("LOGOFF {} /server:{}").format(id, server)
        print(command)
        os.system(command)

    def __init__(self, parent):
        FrmMain.FrmMain.__init__(self, parent)
        df = self.filldata("")
        ldf = list(df)
        for header in ldf:
            self.lcUsers.AppendColumn(header)

        self.resizeCols(len(ldf))

        # print(self.lcUsers.GetColumnCount())

        # Loads server names from a file if it exists
        fname = "servers.txt"
        if os.path.isfile(fname):
            with open(fname) as f:
                content = f.readlines()
            content = [x.strip() for x in content]
            self.txtServers.SetValue(" ".join(content))
        else:
            print("No Servers File Found")

        self.refreshsession()

        self.Show(True)


if __name__ == '__main__':
    app = wx.App(False)
    frame = Main(None)
    app.MainLoop()
