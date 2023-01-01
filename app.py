# pylint: disable=cell-var-from-loop, attribute-defined-outside-init, line-too-long
""" App to calculate shopping costs """
import tkinter as tk
from tkinter import ttk, messagebox, END, filedialog, IntVar, StringVar, CENTER
from ast import literal_eval

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

    def define_widgets(self):
        """ Creates the widgets """
        self.tree_view_frame = tk.Frame(self, width=80)
        self.list_box = tk.Listbox(self.tree_view_frame, width=80, selectmode='multiple')
        self.label_total = tk.Label(self, text='£{:,.2f}'.format(0.00), width=80, fg='lime green', font='Helvetica 9 bold')
        self.frame_entry = tk.Frame(self, width=80)
        self.label_product = tk.Label(self.frame_entry, width=10, text='Product:')
        self.entry_product = tk.Entry(self.frame_entry, width=20)
        self.label_cost = tk.Label(self.frame_entry, width=10, text='Cost:')
        self.entry_cost = tk.Entry(self.frame_entry, width=20)
        self.radio_vat = tk.Checkbutton(self.frame_entry, width=5, text='VAT', onvalue=1, offvalue=0, variable=self.vat_amount)
        self.radio_split = tk.Checkbutton(self.frame_entry, width=5, text='Split', onvalue=1, offvalue=0, variable=self.split_selected)
        self.button_add = tk.Button(self, textvariable=self.operation_text, default="active", command=self.add_entry)
        self.button_duplicate = tk.Button(self, text='Duplicate', command=self.duplicate_entry, state='disabled')
        self.button_delete = tk.Button(self, text='Delete', command=self.delete_entry, state='disabled')
        self.button_import = tk.Button(self, text='Import', command=self.open_file)
        self.button_export = tk.Button(self, text='Export', command=self.save_as)
        self.button_subtract = tk.Checkbutton(self, width=6, text='Subtract?', onvalue=1, offvalue=0, variable=self.operation, command=self.set_operation_text)
        self.tree_view = ttk.Treeview(self.tree_view_frame, column=("c1", "c2", "c3"), show='headings', height=5)
        self.tree_view_scrollbar = ttk.Scrollbar(self.tree_view_frame, orient ="vertical", command = self.tree_view.yview)

    def place_widgets(self):
        """ Places the widgets on the GUI """
        self.tree_view_frame.grid(column=1, row=3, pady=5)
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
        self.tree_view_scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
        self.tree_view.config(yscrollcommand=self.tree_view_scrollbar.set)
        self.button_import.grid(column=0, row=3)
        self.button_export.grid(column=0, row=4)
        self.button_subtract.grid(column=0, row=2)
        self.tree_view.column("# 1", anchor=CENTER)
        self.tree_view.heading("# 1", text="ItemId")
        self.tree_view.column("# 2", anchor=CENTER)
        self.tree_view.heading("# 2", text="Product")
        self.tree_view.column("# 3", anchor=CENTER)
        self.tree_view.heading("# 3", text="Cost")
        self.tree_view.pack(side=tk.LEFT, fill=tk.BOTH)

    def set_keyboard_bindings(self):
        """ Sets keyboard bindings """
        self.master.bind('<Return>', self.add_entry)
        self.master.bind('<Control-a>', self.toggle_select_box_highlighting)
        self.master.bind('<Delete>', self.delete_entry)
        self.master.bind('<Control-v>', self.paste_from_clipboard)
        self.tree_view.bind('<<TreeviewSelect>>', self.on_select)

    def on_select(self, evt):
        """ handles selecting inside the listbox, enables the duplicate button if a row has been selected """
        has_one_selected = len(evt.widget.selection()) == 1
        has_at_least_one_selected = len(evt.widget.selection()) >= 1
        self.button_delete.config(state='normal' if has_at_least_one_selected else 'disabled')
        self.button_duplicate.config(state='normal' if has_one_selected else 'disabled')

    def set_operation_text(self):
        """ Sets the operation text for adding or subtracting the entered product value """
        value = self.operation.get()
        if value == '1':
            self.operation_text.set('Subtract')
        else:
            self.operation_text.set('Add')

    def get_next_id(self):
        """ Gets the next id to use, otherwise deleted entries would result in gaps """
        if len(self.items) == 0:
            return 1

        highest_current_value = sorted(self.items, key=lambda x: x[0], reverse=True)[0][0]
        return highest_current_value + 1

    def create_entry(self, product, cost):
        """ Creates an entry """
        self.item_id = self.get_next_id()
        return (self.item_id, product, cost)

    def add_entry(self, event=None):
        """ Adds an entry to the list box """
        if event is None:
            del event
        product_name = self.entry_product.get()
        if product_name == '':
            messagebox.showerror('Error', 'Product must not be empty')
            return
        cost = self.entry_cost.get()
        if cost == '':
            messagebox.showerror('Error', 'Cost must not be empty')
            return
        try:
            cost = float(self.entry_cost.get())
        except ValueError:
            messagebox.showerror('Error', '{} is not a valid Cost'.format(cost))
            self.entry_cost.delete(0, END)
            return
        vat_state = self.vat_amount.get() == 1
        split_state = self.split_selected.get() == 1
        calculated_list = self.calculate([product_name, cost, vat_state, split_state])
        record = self.create_entry(product_name, calculated_list['FinalCost'])
        self.items.append(record)
        self.tree_view.insert("", 'end', values=record)
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
        selection = self.tree_view.selection()[0]
        entry = self.tree_view.item(selection)
        if entry['values'] == '':
            return
        self.tree_view.delete(selection)
        self.items = list(filter(lambda x: x[0] != entry['values'][0], self.items))
        self.update_total(float(entry['values'][2]), '-')

    def duplicate_entry(self):
        """ Duplicates an entry in the list box """
        entry = self.tree_view.item(self.tree_view.focus())
        if entry['values'] == '':
            return

        product = entry['values'][1]
        cost = entry['values'][2]
        copied_entry = self.create_entry(product, cost)
        self.items.append(copied_entry)
        self.tree_view.insert("", 'end', values=copied_entry)
        self.update_total(float(cost), '+')

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
        entry = literal_eval(entry)
        return "'ItemID': '{}', 'Product': '{}', 'Cost': '{}'\n".format(entry['ItemID'], entry['Product'], entry['FinalCost'])

    def save_as(self):
        """ Opens a filedialog and saves current entries to disk """
        if self.list_box.size() > 0:
            new_file = filedialog.asksaveasfile(mode='w', defaultextension='.txt', filetypes=(("Text files","*.txt"),("All files","*.*")))
            if new_file is None:
                return

            contents = list(self.list_box.get(0, END))
            new_file_contents = 'Shopping Calculator\n'
            for entry in contents:
                new_file_contents += self.format_entry(entry)

            new_file.write(new_file_contents)
            new_file.close()

    def open_file(self):
        """ Opens a filedialog to select a file """

        existing_file = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
        contents = open(existing_file, 'r').read()

        if contents is None or len(contents) == 0:
            messagebox.showerror('Error', 'This file contains no data to import')
            return

        contents = contents.split('\n')

        if contents[0] != 'Shopping Calculator':
            messagebox.showerror('Error', 'This file cannot be imported')
            return

        del contents[0]

        for line in contents:
            if len(line) == 0:
                continue

            line = '{} {} {}'.format('{', line, '}')
            object_line = literal_eval(line)
            self.items.append(object_line)
            self.list_box.insert(END, line.replace('"', '').replace('{', '').replace('}', ''))
            row_operation = '-' if self.operation.get() == '1' else '+'
            self.update_total(float(object_line['Cost']), row_operation)
            self.entry_product.focus()

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
