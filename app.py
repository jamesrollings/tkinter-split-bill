import tkinter as tk
from tkinter import ttk, messagebox, END, ACTIVE
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime 

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__()
        self.db = self.connect()
        self.grid(padx=20, pady=20)
        self.master.title('Split Bill and VAT Shopping Calculator')
        self.master.resizable(False, False)
        self.VAT = tk.IntVar()
        self.Split = tk.IntVar()
        self.defineWidgets()
        self.placeWidgets()
        self.master.bind('<Return>', self.addEntry)
        self.master.bind('<Control-a>', lambda event: self.listBox.select_set(0, tk.END))
        self.master.bind('<Delete>', self.deleteEntry)
        self.todayString = 'House_{}'.format(datetime.utcnow().strftime('%d_%m_%Y'))
        self.saveToDB = True

    def defineWidgets(self):
        self.listBoxFrame = tk.Frame(self, width=80)
        self.listBox = tk.Listbox(self.listBoxFrame, width=80, selectmode='multiple')
        self.labelTotal = tk.Label(self, text='£{:,.2f}'.format(0.00), width=80, fg='lime green', font='Helvetica 9 bold')
        self.frameEntry = tk.Frame(self, width=80)
        self.labelProduct = tk.Label(self.frameEntry, width=10, text='Product:')
        self.entryProduct = tk.Entry(self.frameEntry, width=20)
        self.labelCost = tk.Label(self.frameEntry, width=10, text='Cost:')
        self.entryCost = tk.Entry(self.frameEntry, width=20)
        self.radioVAT = tk.Checkbutton(self.frameEntry, width=5, text='VAT', onvalue=1, offvalue=0, variable=self.VAT)
        self.radioSplit = tk.Checkbutton(self.frameEntry, width=5, text='Split', onvalue=1, offvalue=0, variable=self.Split)
        self.buttonAdd = tk.Button(self, text='Add', default="active", command=self.addEntry)
        self.buttonDuplicate = tk.Button(self, text='Duplicate', command=self.duplicateEntry)
        self.buttonDelete = tk.Button(self, text='Delete', command=self.deleteEntry)
        self.listBoxScrollBar = tk.Scrollbar(self.listBoxFrame)

    def placeWidgets(self):
        self.listBoxFrame.grid(column=1, row=3)
        self.listBox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.labelTotal.grid(column=1, row=4)
        self.frameEntry.grid(column=1, row=2)
        self.labelProduct.pack(side=tk.LEFT, fill=tk.BOTH)
        self.entryProduct.pack(side=tk.LEFT, fill=tk.BOTH)
        self.labelCost.pack(side=tk.LEFT, fill=tk.BOTH)
        self.entryCost.pack(side=tk.LEFT, fill=tk.BOTH)
        self.radioVAT.pack(side=tk.LEFT, fill=tk.BOTH)
        self.radioSplit.pack(side=tk.LEFT, fill=tk.BOTH)
        self.buttonAdd.grid(column=2, row=2)
        self.buttonDuplicate.grid(column=2, row=3)
        self.buttonDelete.grid(column=2, row=4)
        self.listBoxScrollBar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.listBox.config(yscrollcommand = self.listBoxScrollBar.set)
        self.listBoxScrollBar.config(command = self.listBox.yview)
    
    def connect(self):
        client = MongoClient('localhost', 27017)
        db = client['HouseShopping']
        return db['History']
    
    def insertOne(self, document):
        insert = self.db.insert_one(document)
        return insert.inserted_id
    
    def findOne(self, query):
        find = self.db.find_one(query)
        return find
    
    def update(self, objFilter, query):
        update = self.db.update_one(objFilter, query)
        return update
    
    def checkDateArrayExists(self):
        query = { self.todayString: { '$exists': True } }
        result = self.findOne(query)
        return result
    
    def addEntry(self, event=None):
        product_name = self.entryProduct.get()
        if product_name == '':
            return tk.messagebox.showerror('Error', 'Product must not be empty')
        cost = self.entryCost.get()
        if cost == '':
            return tk.messagebox.showerror('Error', 'Cost must not be empty')
        try:
            cost = float(self.entryCost.get())
        except:
            tk.messagebox.showerror('Error', '{} is not a valid Cost'.format(cost))
            self.entryCost.delete(0, tk.END)
            return
        vat_state = True if self.VAT.get() == 1 else False
        split_state = True if self.Split.get() == 1 else False
        calculated_list = self.calculate([product_name, cost, vat_state, split_state])
        record = {
            '_id': ObjectId(),
            'Product': calculated_list['Product'],
            'InitialCost': calculated_list['InitialCost'],
            'VAT': calculated_list['VAT'],
            'Split': calculated_list['Split'],
            'FinalCost': calculated_list['FinalCost'],
            'DateAdded': datetime.utcnow()
        }
        todayExists = self.checkDateArrayExists()
        if todayExists != None:
            if self.saveToDB:
                document = self.update({ '_id': ObjectId(str(todayExists['_id'])) }, { '$push': { self.todayString: record } } )
        else:
            if self.saveToDB:
                result = self.insertOne({ self.todayString: [] })
                document = self.update({ '_id': result }, { '$push': { self.todayString: record } } )
        listBoxString = str({
            'Product': record['Product'],
            'FinalCost': record['FinalCost'],
            '_id': str(record['_id'])
        })
        self.listBox.insert(tk.END, listBoxString)
        self.entryProduct.delete(0, tk.END)
        self.entryCost.delete(0, tk.END)
        self.radioSplit.deselect()
        self.updateTotal(float(calculated_list['FinalCost']), '+')
        self.entryProduct.focus()
    
    def deleteEntry(self, event=None):
        if self.listBox.get(tk.ACTIVE) == '':
            return
        selected_text_list = [self.listBox.get(i) for i in self.listBox.curselection()]
        if len(selected_text_list) > 1:
            for i in selected_text_list:
                self.listBox.delete(self.listBox.get(0, tk.END).index(i))
                self.updateTotal(float(eval(i)['FinalCost']), '-')
                if self.saveToDB:
                    self.update({'_id': self.checkDateArrayExists()['_id']}, { '$pull': { self.todayString : {'_id': ObjectId(eval(i)['_id'])}}} )
            return
        listbox_value = self.listBox.get(tk.ACTIVE)
        cost_to_remove = eval(listbox_value)['FinalCost']
        idx = self.listBox.get(0, tk.END).index(listbox_value)
        self.listBox.delete(idx)
        self.updateTotal(cost_to_remove, '-')
        if self.saveToDB:
            self.update({'_id': self.checkDateArrayExists()['_id']}, { '$pull': { self.todayString : {'_id': ObjectId(eval(listbox_value)['_id'])}}} )

    def duplicateEntry(self):
        value = self.listBox.get(tk.ACTIVE)
        if value == '':
            return
        objValue = self.findOne({ self.todayString: { '$elemMatch': {'_id': ObjectId(eval(value)['_id']) } } } )[self.todayString]
        element = list(filter(lambda x: str(x['_id']) == eval(value)['_id'], objValue))[0]
        element['_id'] = ObjectId()
        element['DateAdded'] = datetime.utcnow()
        listBoxString = str({
            'Product': element['Product'],
            'FinalCost': element['FinalCost'],
            '_id': str(element['_id'])
        })
        self.listBox.insert(tk.END, listBoxString)
        self.updateTotal(element['FinalCost'], '+')
        if self.saveToDB:
            self.update({'_id': self.checkDateArrayExists()['_id']}, { '$push': { self.todayString: element }} )

    def updateTotal(self, value, operation):
        current = float(self.labelTotal['text'][1:].replace(',', ''))
        self.labelTotal.config(text = '£{:,.2f}'.format(round(current + value, 2) if operation == '+' else round(current - value, 2)))

    def calculate(self, array):
        base_array = ['Product', 'InitialCost', 'VAT', 'Split']
        obj = {base_array[i]: k for i, k in enumerate(array)}
        obj['FinalCost'] = round(obj['InitialCost'] * 1.20, 2) if array[2] == 1 and bool(obj['VAT']) else obj['InitialCost']
        obj['FinalCost'] = round(obj['FinalCost'] / 2, 2) if bool(obj['Split']) else obj['FinalCost']
        return obj
    
    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
