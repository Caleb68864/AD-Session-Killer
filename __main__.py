import os
import os.path
import subprocess
import pandas
import wx
import FrmMain


class Main(wx.Frame):
    def btnRefershClick(self, instance):
        self.refreshsession()

    def btnKillClick(self, instance):
        index = self.lcUsers.GetFocusedItem()
        if index >= 0:
            print(index, self.lcUsers.GetItem(index, 2).GetText())
            id = self.lcUsers.GetItem(index, 2).GetText()
            server = self.lcUsers.GetItem(index, 5).GetText()
            self.killsession(id, server)
            self.refreshsession()
        else:
            print("No Session Selected")

    def btnClearClick(self, instance):
        self.lcUsers.DeleteAllItems()
        self.txtServers.SetValue("")

    def resizeCols(self, cols):
        for i in range(cols):
            self.lcUsers.SetColumnWidth(i, -2)
            # self.lcUsers.SetColumnWidth(i, -1)

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
        # print("Refresh")

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
                    print("Server: {} - Found!".format(server))
                    output = subprocess.check_output("QWINSTA /server:{}".format(server), shell=False)
                    # print(output)
                    self.appeandtotable(output, server, table)
                except:
                    print("Server: {} - Does Not Exists".format(server))

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
            print("No Servers Given")
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
