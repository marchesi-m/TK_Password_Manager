# -*- coding: utf-8 -*-
"""
@author: Martina Marchesi
"""

import tkinter as tk
from tkinter import ttk, RAISED, END, font
import sqlite3
import hashlib
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet

# =============================================================================
# STRING VARIABLES FOR BUTTONS LALBELS AND SETTINGS
# =============================================================================

# message variables
ac_describe = """Hi! This is a password manager. Instert your
 information down here to create your account.
 Use at least 8 characters for your password.
 Remember: note down your username and password."""

agree = "'I agree to\nTerms and Conditions'"
pwd = "Show Password"

lock_emoji = chr(9621)
login_msg = """This is the login section.
 Insert your account info\nto access the database."""

unfilled_fields = "Not all fields are flled.\nPlease try again."
different_pw = "The password you have chosen was not re-inserted well."
short_pw = "Your passwod is shorter than 8 characters."
agree_to_data = """To create an account you need to agree with our data
 treatment policy."""
account_exists = "An account exists already!"
creation_ok = "Your account was created and stored successfully."
wrong_pw = "The password is incorrect!"
wrong_name = "The username is incorrect!"
error = "ERROR!"
more_info = """This program creates two tables, one for the user's information
 and one for the passwords. All information is encrypted with a symmetric
 method which uses a key generated by the master password. The master password
 itself is used to generate the encryption key, and its hashed value stored in
 the database to check if the user's input password is correct. Even if
 a third party obtains the hashed value it would be impossible for them to
 find the key that produced it."""

# style settings
bbb = "black"           # application background color
fff = "Consolas Bold"   # font for all words
www = "white"           # foreground color (text)

# list of avatars to choose from
avatars = [chr(9889), chr(9973), chr(9752), chr(9876), chr(9883), chr(9829),
           chr(9836), chr(9823), chr(9733), chr(9917)]
avatar_names = ["bolt", "boat", "clover", "swords", "atom", "heart", "music",
                "chess", "star", "football"]

creation_ok = """The website and password are stored successfully in the
 database. To update the display press the 'SHOW ALL RECORDS' 
 button again."""
 
ID_not_exist = "This ID does not exist.\nPlease insert a valid ID."

delete_ID = """Are you sure you want to delete the information
 associated with this ID?"""
instructions = """Each record is assigned a unique ID number.
 To delete a record or copy the password to your
 clipboard, you simply need to put its ID number
 in the entry box below. To refresh the records you
 can press the 'SHOW ALL RECORDS' button again."""

# =============================================================================
# PRIMARY WINDOW SETTINGS
# =============================================================================

window = tk.Tk()
window.geometry("702x683")
window.title("Password Manager")
window.config(background=bbb)
window.resizable(width=0, height=0)     # can't resize master window

# =============================================================================
# CREATING THE TABS INSIDE LOGIN WINDOW
# =============================================================================

nb_style = ttk.Style()
nb_style.theme_use("default")
nb_style.configure("TNotebook.Tab", bg=bbb, fg=www, font=(fff, 15),
                   ipadx=30, pady=2)
nb_style.map("TNotebook.tab", bg=[("selected", bbb)])

notebook = ttk.Notebook(window)
notebook.pack(expand=True, fill="both")

create_ac_tab = tk.Frame(notebook, bg=bbb)
notebook.add(create_ac_tab, text="Create Account")

logged_in_tab = tk.Frame(notebook, bg=bbb)
notebook.add(logged_in_tab, text="Login Tab")

# =============================================================================
# CREATING THE SQLITE3 DATABASE WITH 2 TABLES AND CREATE TEMPORARY KEY VARIABLE
# =============================================================================

# if there is NO database in the script's folder, then create one
if not os.path.exists("passwords.db"):
    
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()   # create a cursor to connect to database
    
    # bytes as a text input are ok with sqlite3
    c.execute("""CREATE TABLE login_info (
            username text,
            email text,
            avatar text,
            pass_word text
            )""")
    c.execute("""CREATE TABLE password_table (
            website text, 
            email text,
            pass_word text
            )""")
  
    conn.commit()       # commit changes to database
    conn.close()        # explicitly close database connection
    
KEY = ""    # encryption key generated by the program

# =============================================================================
# FUNCTIONS
# =============================================================================


def generate_key(plainpassword):
    """ 
    Change the global KEY parameter by generating it INSIDE the program 
    with the user's password input. The plain password is the only input,
    and it is given in plain text.
    """
    global KEY
    password = plainpassword.encode("utf-8") # encoding the password used
    salt = b'C\x0e\xf9,\xe1\xf1\x90r`\xba\x93\xaa4U~x'  # = os.urandom(16)
    key_derivation_function = PBKDF2HMAC(algorithm=hashes.SHA256(),
                                         length=32, salt=salt,
                                         iterations=390_000,
                                         backend=default_backend())
    # global key parameter is generated according to password in the function
    KEY = base64.urlsafe_b64encode(key_derivation_function.derive(password))
    # KEY is already encoded into bytes
    return KEY


def encrypt_f(message_PLAIN):
    """ 
    Generate Fernet key with the global KEY parameter. Turn the message into
    bytes then use the KEY to encrypt it. The input message is in plain text.
    """
    f_key = Fernet(KEY)         # alternative: use generate_key function
    encoded_msg = message_PLAIN.encode("utf-8")  # encoding the plain message
    encrypted_msg = f_key.encrypt(encoded_msg)
    return encrypted_msg


def decrypt_f(message_ENC):
    """ 
    Generate Fernet key with the global KEY parameter, then decrypt message 
    and convert it back into plain text. The input message is in bytes.
    """
    f_key = Fernet(KEY)         # alternative: use generate_key function
    decrypted_msg = f_key.decrypt(message_ENC)
    decoded_msg = decrypted_msg.decode("utf-8")
    return decoded_msg


def hashing(fernet_key):
    """
    Produce a hash of the complete fernet key generated by the password.
    The fernet key is the only input. In the program it is assigned to the 
    'KEY' variable, which is already in bytes. 
    """
    hash1 = hashlib.md5(fernet_key)
    hash1 = hash1.hexdigest()
    return hash1


def submit_profile():
    """ 
    This function creates a profile in the first row of the 'login_info' table
    of the database. Input check is performed before encrypting the data and
    writing them into the database.
    """
    # grab the inputs
    name = name_entry.get()
    user = user_entry.get()     # the email input 
    pw1 = pw1_entry.get()
    pw2 = pw2_entry.get()
    data_check = D.get()
    avatar_emoji = ""
    
    # no empty fields
    if (name == "" or user == "" or pw1 == "" or pw2 == ""):
        return tk.messagebox.showerror(title=error, message=unfilled_fields)
    # password is coherent
    if pw1 != pw2:
        return tk.messagebox.showerror(title=error, message=different_pw)
    # password is >8 characters
    if pw1 == pw2 and len(pw1) < 8:
        return tk.messagebox.showerror(title=error, message=short_pw)
    # checked off data policy consent
    if data_check != True:
        return tk.messagebox.showerror(title=error, message=agree_to_data)
    
    # else if successful, grab avatar character then encrypt data
    for item in zip(avatar_names, avatars):
        if clicked.get() == item[0]:
            avatar_emoji = item[1]
            
    # generate secret key with pw1 that was inserted
    pw_KEY = generate_key(pw1)
    # hash the secret key
    pw_HASH = hashing(pw_KEY)
    
    # encrypted information to put in database
    name_ENC = encrypt_f(name)
    user_ENC = encrypt_f(user)
    
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    
    # retrieve the contents of the login_info table
    login_info = c.execute("SELECT * from login_info")
    log_fetch = c.fetchall()
    
    # check an account login file is not there already by checking contents
    if log_fetch is not []:
        
        conn.commit()
        conn.close()
        
        return tk.messagebox.showerror(title=error, message=account_exists)
    
    elif login_info is []:
        c.execute("""INSERT INTO login_info VALUES
                  (:name_entry, :email_entry, :avatar, :password_entry)""",
                  {
                      'name_entry': name_ENC,       # encrypted
                      'email_entry': user_ENC,      # encrypted
                      'avatar': avatar_emoji,       # not encrypted
                      'password_entry': pw_HASH     # hashed master password
                      })
    conn.commit()
    conn.close()
    
    clear_fields()
    
    return tk.messagebox.showinfo(title="SUCCESS!", message=creation_ok)


def login_func():
    """ 
    Takes the password inserted by user, generated a key with it, then hashes
    it. Later it checks if it's the same as the one in the database, then it
    checks if the username is correct. If both are correct it will open the
    login window.
    """
    
    input_name = enter_username.get()
    input_pw = enter_password.get()
    
    # generate unique key with input password
    pw_input_KEY = generate_key(input_pw)
    # hash the key before adding it to database
    pw_input_HASH = hashing(pw_input_KEY)

    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()

    # retrieve the only row where the master password & login info are
    c.execute("SELECT * from login_info")
    login_tuple = c.fetchall()  # use double indexing and fetchall method

    # grab hashed password from database
    db_pw_HASH = login_tuple[0][3]

    # check if hashed passwords are a match
    if db_pw_HASH == pw_input_HASH:
        # decrypt username with the fernet key generated with input password
        username_DEC = decrypt_f(login_tuple[0][0])
        # check if the username is correct
        if username_DEC == input_name:
            
            conn.commit()
            conn.close()
            
            enter_username.delete(0, tk.END)
            enter_password.delete(0, tk.END)
            
            return login_window()
        
        else:
            conn.commit()
            conn.close()
            
            enter_username.delete(0, tk.END)
            enter_password.delete(0, tk.END)
            return tk.messagebox.showerror(title=error, message=wrong_name)
    
    else:
        conn.commit()
        conn.close()
        
        enter_username.delete(0, tk.END)
        enter_password.delete(0, tk.END)
        
        return tk.messagebox.showerror(title=error, message=wrong_pw)


def login_window():
    """ 
    Contains all the functionalities and front-end for the database interface
    once the user is logged in successfully. It creates the window, defines
    the functions and creates the window's widgets.
    """
    
    # CREATING AND CONFIGURING Log-In-Window (LIW) --------------------------
    liw = tk.Toplevel()
    liw.minsize(902, 660)          # minimum window size
    liw.config(background=bbb)
    liw.title("Personal Profile")
    liw.grab_set()                  # disables parent window when child opens
    
    liw.grid_rowconfigure(0, weight=1)
    liw.grid_rowconfigure(1, weight=1)
    liw.grid_rowconfigure(2, weight=1)
    liw.grid_rowconfigure(3, weight=1)
    liw.grid_columnconfigure(0, weight=1)
    liw.grid_columnconfigure(1, weight=1)
    
    # LOGIN WINDOW FUNCTIONS ------------------------------------------------
    
    
    def show_all_records():
        """ 
        Adds all the records in plain text to a variable (print_Records) 
        which is assigned as the text of a label. This will make the records
        appear in the 'records_frame' frame.
        """
        
        all_records_lbl = tk.Label(records_frame, text="", font=(fff, 12), 
                                   fg=www, bg=bbb)
        all_records_lbl.grid(row=1, column=0, padx=30, pady=15, sticky="NEW")
        
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        
        c.execute("SELECT *, oid FROM password_table")
        all_records = c.fetchall()
        
        print_records = ''
        for record in all_records:
                website_ENC, email_ENC = record[0], record[1]
                pw_ENC, rec_ID = record[2] , record[3]
                
                # decripting database output
                website_DEC = decrypt_f(website_ENC)
                email_DEC = decrypt_f(email_ENC)
                pw_DEC = decrypt_f(pw_ENC)
                
                print_records += (website_DEC+'\t '+email_DEC+
                                  '\t '+pw_DEC+'\t '+str(rec_ID)+'\n')
            
        all_records_lbl.config(text=print_records)  # filling the empty label
        
        conn.commit()
        conn.close()
  
    
    def del_record():
        """ 
        Deletes a record based on the unique index associated with the row
        in which it is entered. This index is generated automatically by the 
        program. To check the record associated with the index, the user can 
        press the show_all_records button.
        """
        
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        
        ask_if_sure = tk.messagebox.askokcancel(title="Just Checking", 
                                                message=delete_ID)
        if ask_if_sure:
            c.execute("DELETE FROM password_table WHERE oid = " 
                      + id_entry.get())
        
        conn.commit() 
        conn.close()
    
    
    def add_record():
        """ 
        This function adds a record to the database by encrypting user entries.
        Password entry must not be empty.
        """
        
        web = web_entry.get()
        password = web_password_entry.get()
        email_user = email_entry.get()
        
        # empty password field is not allowed
        if password == "":
            return tk.messagebox.showerror(title="Empty Fields ERROR!", 
                                           message=unfilled_fields)
        
        # encrypting the data (could also use the map function for more data)
        web_ENC = encrypt_f(web)
        email_user_ENC = encrypt_f(password)
        password_ENC = encrypt_f(email_user)
        
        # open database and write encrypted data to it
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        c.execute("""INSERT INTO password_table VALUES 
                  (:website_entry, :email_entry, :password_entry)""",
                  {
                      'website_entry': web_ENC,
                      'email_entry': email_user_ENC,
                      'password_entry': password_ENC 
                      })
        conn.commit()
        conn.close()
        
        # empty out entry boxes after use
        web_entry.delete(0, END)
        web_password_entry.delete(0, END)
        email_entry.delete(0, END)
        
        return tk.messagebox.showinfo(title="Success!", message=creation_ok)
    
    
    def copy_record_pw():
        """ 
        Clears the clipboard and copies the decrypted password associated 
        with an ID given by the user.
        """
        
        conn = sqlite3.connect('passwords.db')
        c = conn.cursor()
        
        # used to be called 'associated record'
        c.execute("SELECT * FROM password_table WHERE oid = " + id_entry.get())
        line_record = c.fetchall() 
        
        associated_pw_ENC = line_record[0][1]  # pw is second element of tuple 
        associated_pw_DEC = decrypt_f(associated_pw_ENC)  # decrypt password
        
        liw.clipboard_clear()
        liw.clipboard_append(associated_pw_DEC)
        
        conn.commit() 
        conn.close()
    
    
    # retrieve personal information to put in the window
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM login_info WHERE oid = 1")
    profile_tuple = c.fetchall() 
    
    name_ENC = profile_tuple[0][0]          # encrypted
    email_ENC = profile_tuple[0][1]         # encrypted
    account_avatar = profile_tuple[0][2]    # not encrypted
    
    conn.commit()
    conn.close()
    
    name_DEC = decrypt_f(name_ENC)    # decrypt from login data
    email_DEC = decrypt_f(email_ENC)
    personal_msg = f"Hello {name_DEC}!"
    text_entry = tk.StringVar()
    text_entry.set(email_DEC)
    
    # FRAMES CREATION AND PLACING -------------------------------------------
    instructions_frame = tk.Frame(liw, background=bbb, highlightthickness=1)
    instructions_frame.grid(row=0, column=0, columnspan=3, sticky="", 
                            padx=(10, 5), pady=(10, 5))
    
    select_record_frame = tk.Frame(liw, background=bbb, highlightthickness=1)
    select_record_frame.grid(row=1, column=0, columnspan=3, sticky="", 
                             padx=(10, 5), pady=5)
    
    add_record_frame = tk.Frame(liw, background=bbb, highlightthickness=1)
    add_record_frame.grid(row=2, column=0, columnspan=3, sticky="", 
                          padx=(10, 5), pady=(5, 10))
    
    records_frame = tk.Frame(liw, background=bbb, highlightthickness=1)
    records_frame.grid(row=0, column=3, rowspan=3, sticky="NS", padx=(5, 10), 
                       pady=(10, 10))
    
    # LABELS CREATION AND PLACING --------------------------------------------

    account_avatar_lbl = tk.Label(instructions_frame, text=account_avatar, 
                                  font=(fff, 20), fg=www, bg=bbb)
    instructions_lbl = tk.Label(instructions_frame, text=instructions, 
                                font=(fff, 10), fg=www, bg=bbb)
    unique_id_lbl = tk.Label(select_record_frame, text="ID", font=(fff, 15), 
                             fg=www, bg=bbb)
    webpage_lbl = tk.Label(add_record_frame, text="Website", font=(fff, 15), 
                           fg=www, bg=bbb)
    site_password_lbl = tk.Label(add_record_frame, text="Password", 
                                 font=(fff, 15), fg=www, bg=bbb)
    records_lbl = tk.Label(records_frame, text="           \n\n\n", 
                           font=(fff, 49), fg=www, bg=bbb)
    account_name_lbl = tk.Label(instructions_frame, text=personal_msg, 
                                font=(fff, 15), fg=www, bg=bbb)
    user_email_lbl = tk.Label(add_record_frame, text="Email", font=(fff, 15), 
                              fg=www, bg=bbb)
    
    account_avatar_lbl.grid(row=0, column=1, ipadx=30, pady=(7, 0), 
                            sticky="SE")
    instructions_lbl.grid(row=1, column=0, columnspan=3, padx=(25, 25), 
                          pady=(15, 25))
    unique_id_lbl.grid(row=0, column=0, ipadx=30, ipady=10, pady=(0, 5), 
                       sticky="SE")
    webpage_lbl.grid(row=0, column=0, ipadx=30, ipady=15, pady=(20, 0), 
                     sticky="S")
    site_password_lbl.grid(row=1, column=0, ipadx=30, ipady=15, sticky="NSEW")
    records_lbl.grid(row=1, column=0, ipadx=30, ipady=15, sticky="S")
    account_name_lbl.grid(row=0, column=0, padx=30, pady=(20, 0), sticky="SE")
    user_email_lbl.grid(row=2, column=0, ipadx=30, ipady=15, sticky="NSEW")
    
    # ENTRY BOX CREATION AND PLACING ----------------------------------------
    id_entry = tk.Entry(select_record_frame, font=(fff, 15), fg=www, bg=bbb, 
                        highlightthickness=2, width=15)
    web_entry = tk.Entry(add_record_frame, font=(fff, 15), fg=www, bg=bbb, 
                         highlightthickness=2, width=16)
    web_password_entry = tk.Entry(add_record_frame, font=(fff, 15), fg=www, 
                                  bg=bbb, highlightthickness=2, width=16)
    email_entry = tk.Entry(add_record_frame, font=(fff, 15), fg=www, bg=bbb, 
                           highlightthickness=2, width=16, 
                           textvariable=text_entry)
    
    id_entry.grid(row=0, column=1, columnspan=1, ipadx=5, ipady=5, sticky="E", 
                  padx=(20, 115), pady=(30, 10))
    web_entry.grid(row=0, column=1, columnspan=1, ipadx=5, ipady=5, 
                   sticky="NW", padx=10, pady=(30, 0))
    web_password_entry.grid(row=1, column=1, columnspan=1, ipadx=5, ipady=5, 
                            sticky="W", padx=(10, 47), pady=(5, 5))
    email_entry.grid(row=2, column=1, columnspan=1, ipadx=5, ipady=5, 
                     sticky="W", padx=(10, 47), pady=(5, 5))
    
    # BUTTONS CREATION AND PLACING ------------------------------------------
    show_all_records = tk.Button(records_frame, text="SHOW ALL RECORDS", 
                                 font=(fff, 13), width=15, bg=bbb, fg=www, 
                                 relief=RAISED, command=show_all_records, 
                                 bd=5, height=1)
    del_record_btn = tk.Button(select_record_frame, text="DELETE\nRecord", 
                               font=(fff, 10), width=15, bg=bbb, fg=www, 
                               relief=RAISED, command=del_record, bd=5, 
                               height=1, activebackground="red", 
                               activeforeground=bbb)
    copy_pw_btn = tk.Button(select_record_frame, text="COPY\nPASSWORD", 
                            font=(fff, 10), width=13, bg=bbb, fg=www, 
                            relief=RAISED, command=copy_record_pw, bd=5, 
                            height=1, activebackground="green", 
                            activeforeground=bbb)
    add_record_btn = tk.Button(add_record_frame, text="ADD\nRecord", 
                               font=(fff, 10), width=15, bg=bbb, fg=www, 
                               relief=RAISED, command=add_record, bd=5, 
                               height=1)
    
    show_all_records.grid(row=0, column=0, columnspan=1, ipadx=10, ipady=10, 
                          padx=(100, 100), pady=(50, 20), sticky="")
    del_record_btn.grid(row=2, column=1, columnspan=2, ipadx=2, ipady=10, 
                        padx=20, pady=(15, 25), sticky="W")
    copy_pw_btn.grid(row=2, column=1, columnspan=2, ipadx=0, ipady=10, padx=20, 
                     pady=(15, 25), sticky="E")
    add_record_btn.grid(row=4, column=1, columnspan=1, ipadx=2, ipady=10, 
                        padx=20, pady=(15, 35), sticky="")
    
    # END CHILD LOOP WINDOW AND DISABLE REACTIVATE PARENT WINDOW -------------
    liw.mainloop()
    # liw.grab_release()  # try to check how it works without


def more_instructions():
    """ Makes a window pop up with extra instructions about the program """
    tk.messagebox.showinfo(title="FYI", message=more_info)


def goto_login():
    """ Change tab from 'create account' to 'login' """
    notebook.select(logged_in_tab)


def show_password():
    """
    Function that replaces the asterisks with letters typed into the
    password entry boxes. It takes care of login tab as well as the
    account creation tab.
    """
    global pw_see_btn, P, pw_see_btn1, P1
    if P.get():
        pw1_entry['show'] = ''
        pw2_entry['show'] = ''
    else:
        pw1_entry['show'] = '*'
        pw2_entry['show'] = '*'
    if P1.get():
        enter_password['show'] = ''
    else:
        enter_password['show'] = '*'

        
def show_avatar():
    """Show the correct avatar emoji on the page."""
    for item in zip(avatar_names, avatars):
        if clicked.get() == item[0]:
            avatar_img_lbl.config(text=item[1])


def clear_fields():
    """Erase all values selected by the user in the account creation tab. """
    global P, D, clicked
    
    P.set(0)
    D.set(0)
    clicked.set('')
    avatar_img_lbl.config(text='')
    
    name_entry.delete(0, tk.END)
    user_entry.delete(0, tk.END)
    pw1_entry.delete(0, tk.END)
    pw2_entry.delete(0, tk.END)
    

# =============================================================================
# CREATING AND POSITIONING THE LABELS
# =============================================================================
    
avatar_frame = tk.Frame(create_ac_tab, bg=bbb)
avatar_frame.grid(row=0, column=2, rowspan=3, sticky="S")

intro_lbl = tk.Label(create_ac_tab, text=ac_describe, font=(fff, 11), fg=www,
                     bg=bbb)
name_lbl = tk.Label(create_ac_tab, text="Username", font=(fff, 15), fg=www,
                    bg=bbb)
user_lbl = tk.Label(create_ac_tab, text="Email", font=(fff, 15), fg=www,
                    bg=bbb)

pw1_lbl = tk.Label(create_ac_tab, text="Enter Password", font=(fff, 15),
                   fg=www, bg=bbb)
pw2_lbl = tk.Label(create_ac_tab, text="Repeat Password", font=(fff, 15),
                   fg=www, bg=bbb)

data_lbl = tk.Label(create_ac_tab, text=agree, font=(fff, 10), fg=www, bg=bbb)
pw_chk_lbl = tk.Label(create_ac_tab, text=pwd, font=(fff, 12), fg=www, bg=bbb)

avatar_lbl = tk.Label(create_ac_tab, text="Avatar", font=(fff, 15),
                      fg=www, bg=bbb)
avatar_img_lbl = tk.Label(avatar_frame, text="", font=(fff, 80),
                          fg=www, bg=bbb)

top_l_corn = tk.Label(create_ac_tab, text=chr(9627), font=(fff, 10),
                      fg=www, bg=bbb)
bottom_l_corn = tk.Label(create_ac_tab, text=chr(9625), font=(fff, 10),
                         fg=www, bg=bbb)
top_r_corn = tk.Label(create_ac_tab, text=chr(9628), font=(fff, 10),
                      fg=www, bg=bbb)
bottom_r_corn = tk.Label(create_ac_tab, text=chr(9631), font=(fff, 10),
                         fg=www, bg=bbb)

enter_username_lbl = tk.Label(logged_in_tab, text="Username",
                              font=(fff, 15), fg=www, bg=bbb)
enter_password_lbl = tk.Label(logged_in_tab, text="Password",
                              font=(fff, 15), fg=www, bg=bbb)
lock_lbl = tk.Label(create_ac_tab, text=lock_emoji, font=(fff, 60),
                    fg=www, bg=bbb)

top_l_corn1 = tk.Label(logged_in_tab, text=chr(9627), font=(fff, 10),
                       fg=www, bg=bbb)
bottom_l_corn1 = tk.Label(logged_in_tab, text=chr(9625), font=(fff, 10),
                          fg=www, bg=bbb)
top_r_corn1 = tk.Label(logged_in_tab, text=chr(9628), font=(fff, 10),
                       fg=www, bg=bbb)
bottom_r_corn1 = tk.Label(logged_in_tab, text=chr(9631), font=(fff, 10),
                          fg=www, bg=bbb)
    
 
login_lbl = tk.Label(logged_in_tab, text=login_msg, font=(fff, 13), fg=www,
                     bg=bbb)
pw_login_chk_lbl = tk.Label(logged_in_tab, text=pwd, font=(fff, 12), fg=www,
                            bg=bbb)
end_page_lbl = tk.Label(logged_in_tab, text='', font=(fff, 40), fg=www, bg=bbb)
lock_lbl1 = tk.Label(logged_in_tab, text=lock_emoji, font=(fff, 60), fg=www,
                     bg=bbb)


intro_lbl.grid(row=0, column=0, columnspan=3, ipadx=10, ipady=25, pady=19)
name_lbl.grid(row=1, column=0, ipadx=30, ipady=5, sticky="E")
user_lbl.grid(row=2, column=0, ipadx=30, ipady=5, sticky="E")

pw1_lbl.grid(row=4, column=0, ipadx=30, ipady=5, sticky="E")
pw2_lbl.grid(row=5, column=0, ipadx=30, ipady=5, sticky="E")

data_lbl.grid(row=7, column=0, sticky="")
pw_chk_lbl.grid(row=5, column=2, ipadx=10, ipady=10)

avatar_lbl.grid(row=3, column=0, ipadx=30, ipady=5, sticky="E")
avatar_img_lbl.pack()

top_l_corn.grid(row=0, column=0, padx=5, pady=5, sticky="NW")
bottom_l_corn.grid(row=9, column=0, padx=5, pady=5, sticky="SW")
top_r_corn.grid(row=0, column=3, padx=5, pady=5, sticky="NE")
bottom_r_corn.grid(row=9, column=3, padx=5, pady=5, sticky="SE")

enter_username_lbl.grid(row=1, column=0, ipadx=30, ipady=5, sticky="E",
                        padx=(65, 0))
enter_password_lbl.grid(row=2, column=0, ipadx=30, ipady=5, sticky="E",
                        padx=(65, 0))
lock_lbl.grid(row=0, column=0, padx=(50, 0), pady=(30, 0), sticky="NW")

top_l_corn1.grid(row=0, column=0, padx=5, pady=5, sticky="NW")
bottom_l_corn1.grid(row=9, column=0, padx=5, pady=5, sticky="SW")
top_r_corn1.grid(row=0, column=3, padx=(20, 0), pady=5, sticky="NE")
bottom_r_corn1.grid(row=9, column=3, padx=(20, 0), pady=5, sticky="SE")

login_lbl.grid(row=0, column=0, columnspan=4, pady=(70, 60))
pw_login_chk_lbl.grid(row=1, column=2, rowspan=2, ipadx=10, ipady=10,
                      sticky="S")
end_page_lbl.grid(row=3, column=1, rowspan=2, ipadx=10, sticky="S")
lock_lbl1.grid(row=0, column=0, padx=(50, 0), pady=(47, 0), sticky="NE")

# =============================================================================
# ENTRY BOXES CREATING AND PLACING
# =============================================================================

name_entry = tk.Entry(create_ac_tab, font=(fff, 15), fg=www, bg=bbb,
                      highlightthickness=2)
user_entry = tk.Entry(create_ac_tab, font=(fff, 15), fg=www, bg=bbb,
                      highlightthickness=2)
pw1_entry = tk.Entry(create_ac_tab, font=(fff, 15), fg=www, bg=bbb,
                     highlightthickness=2, show='*')
pw2_entry = tk.Entry(create_ac_tab, font=(fff, 15), fg=www, bg=bbb,
                     highlightthickness=2, show='*')
enter_username = tk.Entry(logged_in_tab, font=(fff, 15), fg=www, bg=bbb,
                          highlightthickness=2)
enter_password = tk.Entry(logged_in_tab, font=(fff, 15), fg=www, bg=bbb,
                          highlightthickness=2, show='*')

name_entry.grid(row=1, column=1, ipadx=5, ipady=5, sticky="W", padx=10, pady=5)
user_entry.grid(row=2, column=1, ipadx=5, ipady=5, sticky="W", padx=10, pady=5)
pw1_entry.grid(row=4, column=1, ipadx=5, ipady=5, sticky="W", padx=10, pady=5)
pw2_entry.grid(row=5, column=1, ipadx=5, ipady=5, sticky="W", padx=10, pady=5)
enter_username.grid(row=1, column=1, ipadx=5, ipady=5, sticky="E", padx=10,
                    pady=5)
enter_password.grid(row=2, column=1, ipadx=5, ipady=5, sticky="E", padx=10,
                    pady=5)

# =============================================================================
# AVATAR DROP-DOWN MENU CREATING AND POSITIONING
# =============================================================================

clicked = tk.StringVar()
avatar_menu = tk.OptionMenu(create_ac_tab, clicked, *avatar_names)
avatar_menu.config(width=10)
avatar_menu.grid(row=3, column=1, ipadx=5, ipady=5, sticky="W", padx=10,
                 pady=5)

consolas13 = tk.font.Font(family=fff, size=13)
avatar_menu.config(font=consolas13, bg=bbb, fg=www, activebackground=bbb,
                   activeforeground=www)
menu_names = create_ac_tab.nametowidget(avatar_menu.menuname)
menu_names.config(font=consolas13, bg=bbb, fg=www)

# =============================================================================
# CREATE AND POSITION THE BUTTONS FOR PASSWORD AND DATA POLICY
# =============================================================================

D = tk.IntVar()
data_chk_btn = tk.Checkbutton(create_ac_tab, variable=D, bg=bbb, offvalue=0,
                              onvalue=1)
data_chk_btn.grid(row=6, column=0, pady=(20, 0), sticky="S")

P = tk.IntVar()
pw_see_btn = tk.Checkbutton(create_ac_tab, variable=P, bg=bbb,
                            command=show_password, onvalue=1, offvalue=0)
pw_see_btn.grid(row=4, column=2, rowspan=2, pady=15)

P1 = tk.IntVar()
pw_see_btn1 = tk.Checkbutton(logged_in_tab, variable=P1, bg=bbb, 
                             command=show_password, onvalue=1, offvalue=0)
pw_see_btn1.grid(row=1, column=2, rowspan=2, pady=15)

# =============================================================================
# CREATE THE BUTTONS, ASSOCIATING FUNCTIONS AND PLACING THEM
# =============================================================================

create_ac_btn = tk.Button(create_ac_tab, text="CREATE ACCOUNT",
                          font=(fff, 20), width=20, bg=bbb, fg=www,
                          relief=RAISED, bd=5, command=submit_profile)
avatar_btn = tk.Button(create_ac_tab, text="SHOW AVATAR", font=(fff, 10),
                       highlightthickness=5, width=20, bg=bbb, fg=www,
                       relief=RAISED, bd=3, command=show_avatar)
reset_page_btn = tk.Button(create_ac_tab, text="Clear\nFields", font=(fff, 10),
                           highlightthickness=2, width=15, bg=bbb, fg=www,
                           relief=RAISED, bd=3, command=clear_fields)
goto_login_page_btn = tk.Button(create_ac_tab, text="GO TO LOGIN",
                                font=(fff, 11), highlightthickness=2, width=13,
                                bg=bbb, fg=www, relief=RAISED, bd=3,
                                command=goto_login, highlightcolor=www)
login_btn = tk.Button(logged_in_tab, text="LOG IN", font=(fff, 20), width=18,
                      bg=bbb, fg=www, relief=RAISED, command=login_func, bd=5,
                      height=1)
more_instructions_btn = tk.Button(logged_in_tab, text="How does\nit work?",
                                  font=(fff, 13), width=7, bg=bbb, fg=www,
                                  relief=RAISED, command=more_instructions,
                                  bd=5, height=1, activeforeground=bbb,
                                  activebackground="light yellow")

create_ac_btn.grid(row=6, rowspan=2, column=1, columnspan=2, ipadx=40, 
                   ipady=5, padx=(5, 15), pady=(40, 25))
avatar_btn.grid(row=3, column=2, padx=10, pady=5)
reset_page_btn.grid(row=8, column=2, pady=5)
goto_login_page_btn.grid(row=8, column=1, columnspan=2, ipady=5, pady=5)
login_btn.grid(row=4, column=1, columnspan=3, ipadx=10, ipady=15,
               padx=(0, 45), pady=(70, 20), sticky="E")
more_instructions_btn.grid(row=5, rowspan=2, column=2, columnspan=2, ipadx=40,
                           ipady=15, padx=(0, 57), pady=(13, 55))

# =============================================================================
# CLOSING THE WINDOW MAIN LOOP
# =============================================================================

window.mainloop()

if __name__ == '__main__':
    print("Running script directly")