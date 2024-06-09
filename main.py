import os
from tkinter import Tk, ttk, Menu, Toplevel, Label, messagebox, simpledialog


class KnownHostsEditor:
    def __init__(self, master):
        self.master = master
        master.title("Known Hosts Editor")

        self.menu_bar = Menu(master)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Restart", command=self.load_known_hosts)
        self.file_menu.add_command(label="Exit", command=master.quit)
        self.file_menu.add_command(label="About", command=self.show_about)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        master.config(menu=self.menu_bar)

        self.frame = ttk.Frame(master)
        self.frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            self.frame, columns=("IP Address", "Key Type", "Key Value"), show="headings"
        )
        self.tree.heading("IP Address", text="IP Address")
        self.tree.heading("Key Type", text="Key Type")
        self.tree.heading("Key Value", text="Key Value")

        # Adjusting column sizes as per user request
        self.tree.column("IP Address", width=150)
        self.tree.column("Key Type", width=100)

        self.tree.pack(fill="both", expand=True)

        self.deleted_items_frame = ttk.Frame(master)
        self.deleted_items_frame.pack(fill="x", expand=False)
        self.deleted_button = ttk.Button(
            self.deleted_items_frame,
            text="Show Deleted Entries",
            command=self.show_deleted_entries,
        )
        self.deleted_button.pack(side="left", padx=(20, 10), pady=10)

        self.delete_button = ttk.Button(
            master, text="Delete Entry", command=self.delete_entry
        )
        self.delete_button.pack(side="left", padx=(20, 10), pady=10)

        self.edit_button = ttk.Button(
            master, text="Edit IP Address", command=self.edit_ip_address
        )
        self.edit_button.pack(side="left", padx=(10, 10), pady=10)

        self.refresh_button = ttk.Button(
            master, text="Refresh", command=self.load_known_hosts
        )
        self.refresh_button.pack(side="right", padx=(10, 20), pady=10)

        self.deleted_entries = []  # Store tuples of (position, entry)
        self.load_known_hosts()

    def get_known_hosts_path(self):
        home_path = os.path.expanduser("~")
        known_hosts_path = os.path.join(home_path, ".ssh", "known_hosts")
        return known_hosts_path

    def load_known_hosts(self):
        for entry in self.tree.get_children():
            self.tree.delete(entry)

        known_hosts_path = self.get_known_hosts_path()
        if not os.path.exists(known_hosts_path):
            messagebox.showerror("Error", "The known_hosts file does not exist.")
            return

        with open(known_hosts_path, "r") as file:
            for line in file:
                parts = line.strip().split(" ", 2)
                if len(parts) == 3:
                    self.tree.insert("", "end", values=(parts[0], parts[1], parts[2]))

    def delete_entry(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an entry to delete.")
            return

        response = messagebox.askyesno(
            "Confirm Deletion", "Are you sure you want to delete the selected entry?"
        )
        if response:
            for item in selected_item:
                entry = self.tree.item(item)["values"]
                position = self.tree.index(
                    item
                )  # Get the position of the item in the Treeview
                self.deleted_entries.append((position, entry))
                self.tree.delete(item)

            self.update_known_hosts()

    def update_known_hosts(self):
        entries = []
        for child in self.tree.get_children():
            item = self.tree.item(child)["values"]
            entry = f"{item[0]} {item[1]} {item[2]}\n"
            entries.append(entry)

        known_hosts_path = self.get_known_hosts_path()
        with open(known_hosts_path, "w") as file:
            file.writelines(entries)

    def show_about(self):
        about_window = Toplevel(self.master)
        about_window.title("About")
        Label(
            about_window,
            text="Known Hosts Editor\nVersion 1.0\nFor managing SSH known_hosts file.",
        ).pack(padx=20, pady=20)

    def show_deleted_entries(self):
        deleted_window = Toplevel(self.master)
        deleted_window.title("Deleted Entries")

        tree = ttk.Treeview(
            deleted_window,
            columns=("IP Address", "Key Type", "Key Value"),
            show="headings",
        )
        tree.heading("IP Address", text="IP Address")
        tree.heading("Key Type", text="Key Type")
        tree.heading("Key Value", text="Key Value")
        tree.pack(fill="both", expand=True)

        for position, entry in self.deleted_entries:
            tree.insert("", "end", values=(entry[0], entry[1], entry[2]))

        restore_button = ttk.Button(
            deleted_window,
            text="Restore Selected Entry",
            command=lambda: self.restore_entry(tree, deleted_window),
        )
        restore_button.pack(pady=10)

    def restore_entry(self, tree, window):
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an entry to restore.")
            return

        for item in selected_item:
            entry = tree.item(item)["values"]
            for pos, orig_entry in enumerate(self.deleted_entries):
                if orig_entry[1] == entry:
                    # Restore the entry to its original position in the main Treeview
                    self.tree.insert(
                        "", orig_entry[0], values=(entry[0], entry[1], entry[2])
                    )
                    del self.deleted_entries[pos]  # Remove from deleted entries list
                    break
            tree.delete(item)

        self.update_known_hosts()
        if not tree.get_children():  # Close the window if no deleted entries left
            window.destroy()

    def edit_ip_address(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an entry to edit.")
            return

        new_ip = simpledialog.askstring("Edit IP Address", "Enter new IP address:")
        if not new_ip:
            return

        for item in selected_item:
            entry = self.tree.item(item)["values"]
            self.tree.item(item, values=(new_ip, entry[1], entry[2]))

        self.update_known_hosts()


def main():
    root = Tk()
    root.geometry("1000x400")  # Sets the initial window size
    app = KnownHostsEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
