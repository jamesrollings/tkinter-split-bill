import tkinter as tk
from tkinter import ttk, END, messagebox, ACTIVE

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid(padx=20, pady=20)
        self.master.title('Split Bill and VAT Shopping Calculator')
        self.master.resizable(False, False)
        self.product_type = tk.IntVar()
        self.boolean_values = ['True', 'true']
        self.createWidgets()
        self.master.bind('<Return>', self.addEntry)
        self.master.bind('<Control-a>', lambda event: self.listBox.select_set(0, tk.END))
        self.master.bind('<Delete>', self.deleteEntry)

    def createWidgets(self):
        self.labeltext = tk.Label(self, text='Products', width=80)
        self.labeltext.grid(column=1, row=1)
        self.checkButtonCostco = tk.Checkbutton(self, text='Costco', onvalue=1, offvalue=0, variable=self.product_type)
        self.checkButtonCostco.grid(column=0, row=0)
        self.listBox = tk.Listbox(self, width=80, selectmode='multiple')
        self.listBox.grid(column=1, row=3)
        self.labelTotal = tk.Label(self, text='£0.00', width=80)
        self.labelTotal.grid(column=1, row=4)
        self.entryBox = tk.Entry(self, width=80)
        self.entryBox.grid(column=1, row=2)
        self.addButton = tk.Button(self, text='Add', default="active", command=self.addEntry)
        self.addButton.grid(column=2, row=2)
        self.duplicateButton = tk.Button(self, text='Duplicate', command=self.duplicateEntry)
        self.duplicateButton.grid(column=2, row=3)
        self.deleteButton = tk.Button(self, text='Delete', command=self.deleteEntry)
        self.deleteButton.grid(column=2, row=4)

    def addEntry(self, event=None):
        if self.entryBox.get() == '':
            return
        validated_entries = self.validateEntryString(self.entryBox.get().split(','))
        if isinstance(validated_entries, str):
            return
        calculated_list = self.calculate(validated_entries)
        self.listBox.insert(tk.END, str(calculated_list))
        self.entryBox.delete(0, tk.END)
        self.updateTotal(float(calculated_list['FinalCost']), '+')
    
    def deleteEntry(self, event=None):
        if self.listBox.get(tk.ACTIVE) == '':
            return
        selected_text_list = [self.listBox.get(i) for i in self.listBox.curselection()]
        if len(selected_text_list) > 1:
            for i in selected_text_list:
                self.listBox.delete(self.listBox.get(0, tk.END).index(i))
                self.updateTotal(float(eval(i)['FinalCost']), '-')
            return
        listbox_value = self.listBox.get(tk.ACTIVE)
        cost_to_remove = eval(listbox_value)['FinalCost']
        idx = self.listBox.get(0, tk.END).index(listbox_value)
        self.listBox.delete(idx)
        self.updateTotal(cost_to_remove, '-')

    def duplicateEntry(self):
        value = self.listBox.get(tk.ACTIVE)
        if value == '':
            return
        self.listBox.insert(tk.END, value)
        self.updateTotal(eval(value)['FinalCost'], '+')

    def updateTotal(self, value, operation):
        current = float(self.labelTotal['text'][1:].replace(',', ''))
        self.labelTotal.config(text = '£{:,.2f}'.format(round(current + value, 2) if operation == '+' else round(current - value, 2)))
    
    def validateEntryString(self, entered_value):
        checkboxValue = self.product_type.get()
        if checkboxValue == 1:
            if len(entered_value) != 4:
                return tk.messagebox.showerror('Error', 'Value: "{}" is invalid'.format(', '.join(entered_value)))
            base_array = ['Product', 'InitialCost', 'VAT', 'Split']
            entriesArray = [
                entered_value[0],
                float(entered_value[1]),
                True if entered_value[2] in self.boolean_values else False,
                True if entered_value[3] in self.boolean_values else False
            ]
            return list([base_array, entriesArray, checkboxValue])
        if checkboxValue == 0:
            if len(entered_value) != 3:
                return tk.messagebox.showerror('Error', 'Value: "{}" is invalid'.format(', '.join(entered_value)))
            base_array = ['Product', 'InitialCost', 'Split']
            entriesArray = [entered_value[0], float(entered_value[1]), True if entered_value[2] in self.boolean_values else False]
            return list([base_array, entriesArray, checkboxValue])

    def calculate(self, array):
        obj = {array[0][i]: k for i, k in enumerate(array[1])}
        obj['FinalCost'] = round(obj['InitialCost'] * 1.20, 2) if array[2] == 1 and bool(obj['VAT']) else obj['InitialCost']
        obj['FinalCost'] = round(obj['FinalCost'] / 2, 2) if bool(obj['Split']) else obj['FinalCost']
        return obj
    
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
