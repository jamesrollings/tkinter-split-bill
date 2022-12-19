# pylint: disable=unused-import, cell-var-from-loop, attribute-defined-outside-init, line-too-long
""" App to calculate shopping costs """
import tkinter as tk
from tkinter import ttk, messagebox, END, ACTIVE, filedialog, IntVar, StringVar
from datetime import datetime
import ast

class Application(tk.Frame):
    """ Main application class """
    def __init__(self, master=None):
        super().__init__()
        self.grid(padx=20, pady=20)
        self.master.title('Split Bill and VAT Shopping Calculator')
        self.master.resizable(False, False)
        self.default_state()
        self.define_widgets()
        self.place_widgets()
        self.set_keyboard_bindings()
        self.items = []
        self.item_id = 0

    def default_state(self):
        """ Defines the default state """
        self.item_id = IntVar()
        self.vat_amount = IntVar()
        self.split_selected = IntVar()
        self.operation = StringVar()
        self.operation_text = StringVar()
        self.operation_text.set('Add')
        self.operation.set(0)
        self.selection_is_highlighted = False
        self.today_string = 'House_{}'.format(datetime.utcnow().strftime('%d_%m_%Y'))

    def define_widgets(self):
        """ Creates the widgets """
        self.list_box_frame = tk.Frame(self, width=80)
        self.list_box = tk.Listbox(self.list_box_frame, width=80, selectmode='multiple')
        self.label_total = tk.Label(self, text='£{:,.2f}'.format(0.00), width=80, fg='lime green', font='Helvetica 9 bold')
        self.frame_entry = tk.Frame(self, width=80)
        self.label_product = tk.Label(self.frame_entry, width=10, text='Product:')
        self.entry_product = tk.Entry(self.frame_entry, width=20)
        self.label_cost = tk.Label(self.frame_entry, width=10, text='Cost:')
        self.entry_cost = tk.Entry(self.frame_entry, width=20)
        self.radio_vat = tk.Checkbutton(self.frame_entry, width=5, text='VAT', onvalue=1, offvalue=0, variable=self.vat_amount)
        self.radio_split = tk.Checkbutton(self.frame_entry, width=5, text='Split', onvalue=1, offvalue=0, variable=self.split_selected)
        self.button_add = tk.Button(self, textvariable=self.operation_text, default="active", command=self.add_entry)
        self.button_duplicate = tk.Button(self, text='Duplicate', command=self.duplicate_entry)
        self.button_delete = tk.Button(self, text='Delete', command=self.delete_entry)
        self.list_box_scroll_bar = tk.Scrollbar(self.list_box_frame)
        self.button_export = tk.Button(self, text='Export', command=self.save_as)
        self.button_subtract = tk.Checkbutton(self, width=6, text='Subtract?', onvalue=1, offvalue=0, variable=self.operation, command=self.set_operation_text)

    def place_widgets(self):
        """ Places the widgets on the GUI """
        self.list_box_frame.grid(column=1, row=3)
        self.list_box.pack(side=tk.LEFT, fill=tk.BOTH)
        self.label_total.grid(column=1, row=4)
        self.frame_entry.grid(column=1, row=2)
        self.label_product.pack(side=tk.LEFT, fill=tk.BOTH)
        self.entry_product.pack(side=tk.LEFT, fill=tk.BOTH)
        self.label_cost.pack(side=tk.LEFT, fill=tk.BOTH)
        self.entry_cost.pack(side=tk.LEFT, fill=tk.BOTH)
        self.radio_vat.pack(side=tk.LEFT, fill=tk.BOTH)
        self.radio_split.pack(side=tk.LEFT, fill=tk.BOTH)
        self.button_add.grid(column=2, row=2)
        self.button_duplicate.grid(column=2, row=3)
        self.button_delete.grid(column=2, row=4)
        self.list_box_scroll_bar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.list_box.config(yscrollcommand = self.list_box_scroll_bar.set)
        self.list_box_scroll_bar.config(command = self.list_box.yview)
        self.button_export.grid(column=0, row=4)
        self.button_subtract.grid(column=0, row=2)

    def set_keyboard_bindings(self):
        """ Sets keyboard bindings """
        self.master.bind('<Return>', self.add_entry)
        self.master.bind('<Control-a>', self.toggle_select_box_highlighting)
        self.master.bind('<Delete>', self.delete_entry)
        self.master.bind('<Control-v>', self.paste_from_clipboard)

    def set_operation_text(self):
        """ Sets the operation text for adding or subtracting the entered product value """
        value = self.operation.get()
        if value == '1':
            self.operation_text.set('Subtract')
        else:
            self.operation_text.set('Add')

    def add_entry(self, event=None):
        """ Adds an entry to the list box """
        if event is None:
            del event
        product_name = self.entry_product.get()
        if product_name == '':
            return messagebox.showerror('Error', 'Product must not be empty')
        cost = self.entry_cost.get()
        if cost == '':
            return messagebox.showerror('Error', 'Cost must not be empty')
        try:
            cost = float(self.entry_cost.get())
        except ValueError:
            messagebox.showerror('Error', '{} is not a valid Cost'.format(cost))
            self.entry_cost.delete(0, END)
            return
        vat_state = True if self.vat_amount.get() == 1 else False
        split_state = True if self.split_selected.get() == 1 else False
        calculated_list = self.calculate([product_name, cost, vat_state, split_state])
        self.item_id = self.item_id + 1
        record = {
            'ItemID': self.item_id,
            'Product': calculated_list['Product'],
            'InitialCost': calculated_list['InitialCost'],
            'VAT': calculated_list['VAT'],
            'Split': calculated_list['Split'],
            'FinalCost': calculated_list['FinalCost'],
            'DateAdded': datetime.utcnow()
        }
        self.items.append(record)
        list_box_entry = str({
            'ItemID': record['ItemID'],
            'Product': record['Product'],
            'FinalCost': record['FinalCost']
        })
        self.list_box.insert(END, list_box_entry)
        self.entry_product.delete(0, END)
        self.entry_cost.delete(0, END)
        self.radio_split.deselect()
        row_operation = '-' if self.operation.get() == '1' else '+'
        self.update_total(float(calculated_list['FinalCost']), row_operation)
        self.entry_product.focus()

    def delete_entry(self, event=None):
        """ Deletes an entry from the list box """
        if event is None:
            del event
        if self.list_box.get(ACTIVE) == '':
            return
        selected_text_list = [self.list_box.get(i) for i in self.list_box.curselection()]
        if len(selected_text_list) > 1:
            for i in selected_text_list:
                self.list_box.delete(self.list_box.get(0, END).index(i))
                self.update_total(float(ast.literal_eval(i)['FinalCost']), '-')
                self.items = list(filter(lambda x: x['ItemID'] != ast.literal_eval(i)['ItemID'], self.items))
            return
        listbox_value = self.list_box.get(ACTIVE)
        cost_to_remove = ast.literal_eval(listbox_value)['FinalCost']
        idx = self.list_box.get(0, END).index(listbox_value)
        self.list_box.delete(idx)
        self.update_total(cost_to_remove, '-')

    def duplicate_entry(self):
        """ Duplicates an entry in the list box """
        value = self.list_box.get(ACTIVE)
        if value == '':
            return
        original_item_id = ast.literal_eval(value)['ItemID']
        copied_entry = self.items[list(x['ItemID'] == original_item_id for x in self.items).index(True)]
        copied_entry = copied_entry.copy()
        self.item_id = self.item_id + 1
        copied_entry['ItemID'] = self.item_id
        copied_entry['DateAdded'] = datetime.utcnow()
        list_box_string_value = str({
            'ItemID': copied_entry['ItemID'],
            'Product': copied_entry['Product'],
            'FinalCost': copied_entry['FinalCost'],
        })
        self.items.append(copied_entry)
        self.list_box.insert(END, list_box_string_value)
        self.update_total(copied_entry['FinalCost'], '+')

    def update_total(self, value, operation):
        """ Updates the running total """
        current = float(self.label_total['text'][1:].replace(',', ''))
        new_value = '£{:,.2f}'.format(round(current + value, 2) if operation == '+' else round(current - value, 2))
        if new_value.find('-') != -1:
            self.label_total.config(fg='red')

        self.label_total.config(text = new_value)

    @staticmethod
    def calculate(array):
        """ calculates the final cost of product based on options specified (VAT and split) """
        base_array = ['Product', 'InitialCost', 'VAT', 'Split']
        obj = {base_array[i]: k for i, k in enumerate(array)}
        obj['FinalCost'] = round(obj['InitialCost'] * 1.20, 2) if array[2] == 1 and bool(obj['VAT']) else obj['InitialCost']
        obj['FinalCost'] = round(obj['FinalCost'] / 2, 2) if bool(obj['Split']) else obj['FinalCost']
        return obj

    @staticmethod
    def format_entry(entry):
        """ returns a string of a formatted entry """
        entry = ast.literal_eval(entry)
        return 'ItemID: {}, Product: {}, Cost: {}\n'.format(entry['ItemID'], entry['Product'], entry['FinalCost'])

    def save_as(self):
        """ Opens a filedialog and saves current entries to disk """
        if self.list_box.size() > 0:
            new_file = filedialog.asksaveasfile(mode='w', defaultextension='.txt', filetypes=(("Text files","*.txt"),("All files","*.*")))
            if new_file is None:
                return

            contents = list(self.list_box.get(0, END))
            new_file_contents = ''
            for entry in contents:
                new_file_contents += self.format_entry(entry)

            new_file.write(new_file_contents)
            new_file.close()

    def paste_from_clipboard(self, event=None):
        """ function to handle pasting into the list box """
        if event is None:
            del event
        focused_widget = self.focus_get().__repr__()
        print(focused_widget)

    def toggle_select_box_highlighting(self, event=None):
        """ selects all the entries in the list box """
        if event is None:
            del event
        if self.selection_is_highlighted:
            self.list_box.selection_clear(0, END)
            self.selection_is_highlighted = False
        else:
            self.selection_is_highlighted = True
            self.list_box.select_set(0, END)


    def run(self):
        """ runs the app """
        self.mainloop()

if __name__ == "__main__":
    app = Application()
    app.run()
