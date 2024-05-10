import tkinter as tk
import os, requests
from tkinter import messagebox, Listbox, Scrollbar

root = tk.Tk()
root.title("Guardabot - Log in")
root.geometry("640x360")
root.minsize(640, 360)

# Log in screen
online_log_in_username_tkstr = tk.StringVar()
online_log_in_password_tkstr = tk.StringVar()

online_log_in_label_username = tk.Label(root, text="Username:")
online_log_in_label_username.place(x=150, y=100, width=90, height=30)
online_log_in_entry_username = tk.Entry(root, textvariable=online_log_in_username_tkstr)
online_log_in_entry_username.place(x=240, y=100, width=240, height=30)

online_log_in_label_password = tk.Label(root, text="Password:")
online_log_in_label_password.place(x=150, y=135, width=90, height=30)
online_log_in_entry_password = tk.Entry(root, textvariable=online_log_in_password_tkstr)
online_log_in_entry_password.place(x=240, y=135, width=240, height=30)

online_base_api_url = ""
online_server_passcode = ""

def online_log_in():
    global online_log_in_label_username, online_log_in_label_password, online_log_in_entry_username, online_log_in_entry_password
    online_username = online_log_in_username_tkstr.get()
    online_password = online_log_in_password_tkstr.get()
    if online_username.strip() == "" or online_password.strip() == "":
        messagebox.showwarning("Warning", "Please fill ALL the fields.")
        return

    try:
        response = requests.post(
            online_base_api_url + "account/login",
            headers = {'Content-Type': 'application/json'},
            json = {"auth": online_server_passcode, "username": online_username, "password": online_password}
        )

        data = response.json()
        #data = {"message": f"Logged in as {online_username}", "token": "cl-askfjdalksdfjalksdjfalksjdflaksjdf"}
        if 'message' in data and data['message'].strip():
            messagebox.showinfo("Server Message", data['message'])
            online_session_token = data['token']
            print(online_session_token)

            online_log_in_label_username.destroy()
            online_log_in_label_password.destroy()
            online_log_in_entry_username.destroy()
            online_log_in_entry_password.destroy()
            online_log_in_button.destroy()
        else:
            messagebox.showerror("Error", "Could not log in. Try again.")
    except requests.exceptions.RequestException:
        messagebox.showerror("Error", "Could not connect to the server.")

online_log_in_button = tk.Button(root, text="Log In", command=online_log_in)
online_log_in_button.place(x=240, y=170, width=240, height=30)
tk.Button(root, text="Log in", command=online_log_in)


local_stages_frame = tk.Frame(root)
#local_stages_frame.place(x=0, y=0, width=640, height=280)
local_stages_scrollbar = Scrollbar(local_stages_frame, orient=tk.VERTICAL)
#local_stages_scrollbar.place(x=620, y=10, width=10, height=270)
local_stages_listbox = Listbox(local_stages_frame, width=50, yscrollcommand=local_stages_scrollbar.set)
#local_stages_listbox.place(x=10, y=10, width=600, height=280)
local_stages_scrollbar.config(command=local_stages_listbox.yview)

stages_directory = os.path.join(os.path.expandvars('%APPDATA%'), 'SMM-CL', 'Niveles') # os.path.join(os.getcwd(), 'stages')

if not os.path.isdir(stages_directory):
    messagebox.showerror("Error", "Stages folder was not found.\nHave you ever played the game?")
    exit()

try:
    files = os.listdir(stages_directory)
    for archivo in files:
        if os.path.isfile(os.path.join(stages_directory, archivo)):
            local_stages_listbox.insert(tk.END, archivo)
except OSError:
    messagebox.showerror("Error", "Error while loading stages.")

root.mainloop()