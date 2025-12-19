import tkinter as tk
from tkinter import messagebox as tkmb
import customtkinter as ctk
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import csv
import os
import sys
import qrcode


csv_file_path = "users.csv"


def safe_open(path, size=None):
    try:
        img = Image.open(path).convert("RGBA")
        if size:
            return img.resize(size, Image.LANCZOS)
        return img
    except Exception:
        if size:
            return Image.new("RGBA", size, (255, 255, 255, 0))
        return Image.new("RGBA", (1, 1), (255, 255, 255, 0))

def init_csv(): #akses excel
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=[
                "username", "password", "item", "join_date", "harga", "saldo", "expired"
            ])
            writer.writeheader()

def read_users(file_path): #membaca excel
    users = {}
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row["username"]] = row["password"]
    except FileNotFoundError:
        init_csv()
    return users

def load_user_saldo(username, file_path="users.csv"): #memuat saldo user yang telah dirubah
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return int(row["saldo"]) if row["saldo"] else 0
    return 0

def get_user_saldo(username):
    return load_user_saldo(username)

def write_user(file_path, username, password): #tulis excel: user,password,item,join_date,saldo,expired
    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "username", "password", "item", "join_date", "harga", "saldo", "expired"
        ])
        writer.writerow({
            "username": username,
            "password": password,
            "item": "",
            "join_date": "",
            "harga": "",
            "saldo": 0,
            "expired": ""   
        })

def save_user_data(username, item, price, saldo, file_path="users.csv"): #menyimpan users.csv setiap ada perubahan
    rows = []
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                duration = DURASI_MEMBERSHIP.get(item, 0)
                if item: 
                    row["expired"] = hitung_join_date_expired(row.get("expired", ""), duration)
                    row["item"] = item
                    row["harga"] = price
                    row["join_date"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
                row["saldo"] = str(saldo)
            rows.append(row)

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["username","password","item","join_date","harga","saldo","expired"])
        writer.writeheader()
        writer.writerows(rows)

DURASI_MEMBERSHIP = {
    "Bronze": 1,
    "Silver": 7,
    "Gold": 30
}

def hitung_join_date_expired(expired_lama, tambah_hari): #hitung sisa membership dari expired - datetime
    sekarang = datetime.now()
    if not expired_lama:
        return (sekarang + timedelta(days=tambah_hari)).strftime("%d-%m-%Y")
    try:
        expired_obj = datetime.strptime(expired_lama, "%d-%m-%Y")
        if expired_obj > sekarang:
            expired_baru = expired_obj + timedelta(days=tambah_hari)
        else:
            expired_baru = sekarang + timedelta(days=tambah_hari)
        return expired_baru.strftime("%d-%m-%Y")
    except:
        return (sekarang + timedelta(days=tambah_hari)).strftime("%d-%m-%Y")
    
def generate_qr(username, expired):
    data = f"GYMEMAS|USER:{username}|EXPIRED:{expired}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=6,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img

def center_window(root, width, height): #untuk window gui
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x}+{y}")





class LoginApp:
    def __init__(self, root, csv_path): #mengatur tampilan window
        self.root = root
        self.csv_path = csv_path
        self.root.title("Login - GymEmas")
        center_window(self.root, 388, 824)
        
        bg_img = safe_open("bg login.png", size=(388, 824))
        self.bg_image = ctk.CTkImage(light_image=bg_img, size=(388, 824)) 
        self.bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.loginname = ctk.CTkLabel(self.root, text="Login", 
                                      font=("Crimson Text", 32), 
                                      text_color="#000000",
                                      fg_color="#FFFFFF")
        self.loginname.place(x=150, y=200)

        self.entry_username = ctk.CTkEntry(self.root, placeholder_text="Username",
                                           fg_color="#FFFFFF",
                                           text_color="#000000",
                                           placeholder_text_color="#A99090", 
                                           border_color="#FFFFFF",
                                           bg_color="#FFFFFF", 
                                           corner_radius=10, width=250, height=34)
        self.entry_username.place(x=90, y=325)
        

        self.entry_password = ctk.CTkEntry(self.root, placeholder_text="Password", show="*", 
                                           fg_color="#FFFFFF", 
                                           text_color="#000000", 
                                           placeholder_text_color="#A99090", 
                                           border_color="#FFFFFF",
                                           bg_color="transparent", corner_radius=10, width=250, height=21)
        self.entry_password.place(x=90, y=395)

        ctk.CTkButton(self.root, text="Login", width=170, height=42, 
                      fg_color="#FF9D00", 
                      hover_color="#B90000",
                      bg_color="#FFF1F3",
                      command=self.login).place(x=110, y=450)
        
        dont = ctk.CTkLabel(self.root, text="Don't have an account?",
                            font=("Crimson Text", 12), 
                            width=111, height=16, 
                            text_color="#000000", 
                            bg_color="#FFFFFF")
        dont.place(x=88, y=505)

        signup = ctk.CTkButton(self.root, text="Sign Up", 
                               font=("Crimson Text", 12), 
                               width=40, height=16, text_color="#0092FA", fg_color="#FFFFFF", bg_color="#FFFFFF",
                               command=self.open_register)
        signup.place(x=210, y=503)

        info_img = safe_open("infobutton.png", size=(33, 33))
        self.info_photo = ctk.CTkImage(light_image=info_img, size=(22,22))
        ctk.CTkButton(self.root, image=self.info_photo, text="", width=22, height=22, 
                      fg_color=("#C96E05"), hover_color=("#04103A"), bg_color=("#ffffff"), 
                      command=self.open_info).place(x=20, y=20)

        signup.bind("<Enter>", self.on_hover)
        signup.bind("<Leave>", self.on_leave)
        self.root.bind('<Return>', self.login)

    def login(self, event=None): #fungsi login
        username = self.entry_username.get()
        password = self.entry_password.get()

        users = read_users(self.csv_path)
        if username in users and users[username] == password:
             tkmb.showinfo("Login", "Login berhasil! Selamat datang di GymEmas.")
             self.root.withdraw()
             saldo_user = get_user_saldo(username)
             try:
                 gym_menu.update_username(username)
                 gym_menu.update_saldo(saldo_user)
                 menu_app.deiconify()
             except Exception as e:
                 tkmb.showerror("ERROR", f"Terjadi error: {e}")
                 self.root.deiconify()
        else:
            tkmb.showerror("Login", "Username atau password salah!")

    def open_register(self): #buka gui register
        self.root.withdraw()
        register_window = ctk.CTkToplevel(self.root)
        register_window.lift()
        register_window.attributes('-topmost', True)
        register_window.focus_force()
        register_window.grab_set()
        RegisterApp(register_window, self, self.csv_path)

    def open_info(self): #buka gui info kelompok
        self.root.withdraw()
        info_window = ctk.CTkToplevel(self.root)
        info_window.lift()
        info_window.attributes('-topmost', True)
        info_window.focus_force()
        info_window.grab_set()
        InfoKelompok(info_window)

    def on_hover(self, event):
        try: event.widget.configure(font=("Crimson Text", 8, "underline"))
        except: pass

    def on_leave(self, event):
        try: event.widget.configure(font=("Crimson Text", 8))
        except: pass




class InfoKelompok:
    def __init__(self, root): #inisiasi GUI info kelompok
        self.root = root
        self.root.title("Info Kelompok - GymEmas")
        center_window(self.root, 400, 300)

        bgidentitas = safe_open("bg identitas.png", size=(800, 600))
        self.bgphoto = ctk.CTkImage(light_image=bgidentitas, size=(800, 600))
        bg_label = ctk.CTkLabel(self.root, image=self.bgphoto, text="")  
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        developedby = ctk.CTkLabel(self.root, text="DEVELOPED BY:", font=("Crimson Text", 27,),
                                   width=165, height=32, text_color="#000000", fg_color="transparent")
        developedby.place(x=118, y=15)

        Alfath = ctk.CTkLabel(self.root, text="Akeyla Fadillah Alfath Herliyanantha (25031554074)",
                              font=("Crimson Text", 12,), text_color="#000000", fg_color="transparent")
        Alfath.place(x=84, y=70)

        Aryo = ctk.CTkLabel(self.root, text="Nabil Aryo Suharnoto (25031554092)",
                            font=("Crimson Text", 12,), text_color="#000000", fg_color="transparent")
        Aryo.place(x=84, y=120)

        Dinda = ctk.CTkLabel(self.root, text="Adinda Atsilla Salsabilah (25031554262)",
                             font=("Crimson Text", 12,), text_color="#000000", fg_color="transparent")
        Dinda.place(x=84, y=170)

        back = safe_open("tombolbacktb.png", size=(27, 27))
        self.backphoto = ctk.CTkImage(light_image=back, size=(27, 27))
        ctk.CTkButton(self.root, image=self.backphoto, text="", width=27, height=27, 
                      fg_color=("#FF9D00"), hover_color=("#3E5879"), bg_color=("#FFffff"), 
                      command=self.go_back).place(x=29, y=14)

    def go_back(self): #kembali
        self.root.destroy()
        try:
            login_app.deiconify()
        except:
            pass




class RegisterApp:
    def __init__(self, root, login_app, csv_path): #inisiasi windows GUI reister
        self.root = root
        self.login_app = login_app
        self.csv_path = csv_path
        self.root.title("Register - GymEmas")
        center_window(self.root, 388, 824)

        bg_reg = safe_open("bg register.png", size=(388, 824))
        self.bg_image = ctk.CTkImage(light_image=bg_reg, size=(388, 824))
        self.bg_label = ctk.CTkLabel(self.root, image=self.bg_image, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.registername = ctk.CTkLabel(self.root, text="Sign Up", font=("Crimson Text", 30),
                                         text_color="#FFFFFF", bg_color="#000000")
        self.registername.place(x=150, y=200)

        self.create_username = ctk.CTkEntry(self.root, placeholder_text="Create Username",
                                            fg_color="#000000", text_color="#FFFFFF", 
                                            placeholder_text_color="#A99090", border_color="#D9D9D9",
                                            bg_color="transparent", corner_radius=10, width=250, height=34)
        self.create_username.place(x=90, y=325)
        
        self.create_password = ctk.CTkEntry(self.root, placeholder_text="Create Password", show="*", 
                                            fg_color="#000000", text_color="#FFFFFF", 
                                            placeholder_text_color="#A99090", border_color="#D9D9D9",
                                            bg_color="transparent", corner_radius=10, width=250, height=34)
        self.create_password.place(x=90, y=395)

        self.button_create = ctk.CTkButton(self.root, text="Create", width=170, height=42, corner_radius=10,
                                           fg_color="#FB8B0B", hover_color="#FB8B0B", bg_color="#000000",
                                           command=self.register)
        self.button_create.place(x=110, y=450)

        self.i_have_account = ctk.CTkLabel(self.root, text="I have an account,", font=("Crimson Text", 12),
                                           width=85, height=16, text_color="#FFFFFF", fg_color="#000000")
        self.i_have_account.place(x=95, y=505)
        
        self.loginnow = ctk.CTkButton(self.root, text="Login Here!", font=("Crimson Text", 12),
                                      width=60, height=16, text_color="#0092FA", fg_color="#000000", bg_color="#000000",
                                     command=self.go_back)
        self.loginnow.place(x=190, y=505)

        self.loginnow.bind("<Enter>", self.on_hover)
        self.loginnow.bind("<Leave>", self.on_leave)
        self.root.bind('<Return>', self.register)

    def register(self, event=None): #masukkan username, password
        username = self.create_username.get()
        password = self.create_password.get()

        if not username or not password:
            tkmb.showerror("Error", "Semua field harus diisi!",parent=self.root)
            return

        users = read_users(self.csv_path)
        if username in users:
            tkmb.showerror("Error", "Username sudah terdaftar!",parent=self.root)
        else:
            write_user(self.csv_path, username, password)
            tkmb.showinfo("Sukses", "Registrasi berhasil! Silakan login.",parent=self.root)
            self.go_back()

    def go_back(self):
        self.root.destroy()
        try:
            self.login_app.root.deiconify() 
        except Exception:
            pass

    def on_hover(self, event):
        try: event.widget.configure(font=("Crimson Text", 8, "underline"))
        except: pass

    def on_leave(self, event):
        try: event.widget.configure(font=("Crimson Text", 8))
        except: pass



class GymMenu:
    def __init__(self, root, username): #GUI gym menu
        self.root = root
        self.username = username
        self.expired_date = self.load_expired(self.username)
        self.expired_var = tk.StringVar(value=f"Expired: {self.expired_date}")
    
        self.root.title("Menu Utama - GymEmas")
        center_window(self.root, 398, 824)
        bgimage = safe_open("bg gymmenu.png", size=(398, 824))
        self.bgphoto = ctk.CTkImage(light_image=bgimage, size=(398, 824))
        self.bglabel = ctk.CTkLabel(self.root, image=self.bgphoto, text="")
        self.bglabel.place(x=0, y=0, relwidth=1, relheight=1)
        self.profil = safe_open("profilegym.png", size=(48,48))
        self.profilphoto = ctk.CTkImage(light_image=self.profil, size=(48,48)) 
        self.profilbutton = ctk.CTkButton(
                self.root, image=self.profilphoto,
                text="", width=48, height=48,
                bg_color="#ffbd59", fg_color="#ffbd59" ,hover_color="#faa422",
                command=self.open_profile
        )
        self.profilbutton.place(x=5, y=10)

        self.lbl_nama = ctk.CTkLabel(self.root, text=f"Hi, {self.username}", 
                                     font=("Inter", 16, "bold"), text_color="#FFFFFF", bg_color="#ffbd59")
        self.lbl_nama.place(x=65, y=10)

        self.saldo = load_user_saldo(self.username)
        self.saldo_var = tk.StringVar()
        self.update_saldo(self.saldo) 
        self.gym_saldo = ctk.CTkLabel(self.root, textvariable=self.saldo_var,     #entry saldo
                                      font=("Inter", 14), text_color="#00FF00", 
                                      bg_color="#ffbd59")
        self.gym_saldo.place(x=65, y=35)

        topup = ctk.CTkButton(self.root, text="+ TOP UP", width=80, height=30,  #tombol topup
                              font=("Inter", 12, "bold"),
        hover_color="#353333", bg_color="#000000", fg_color="#000000",
                              text_color="#FFFFFF", command=self.open_topup)
        topup.place(x=300, y=25)
        
        ctk.CTkLabel(self.root, text="PILIH MEMBERSHIP", font=("Inter", 20, "bold"), 
                     text_color="#000000", bg_color="#FFFFFF").place(x=44, y=150)

        bronze_btn = ctk.CTkButton(self.root, text="BRONZE\nRp 75.000", width=300, height=80,
                                   font=("Inter", 18, "bold"),
                                   fg_color="#A97142", hover_color="#7A522F", text_color="white",
                                   command=lambda: self.buy_item("Bronze", 75000))
        bronze_btn.place(x=44, y=200)

        silver_btn = ctk.CTkButton(self.root, text="SILVER\nRp 125.000", width=300, height=80,
                                   font=("Inter", 18, "bold"),
                                   fg_color="#C0C0C0", hover_color="#8F8F8F", text_color="black",
                                   command=lambda: self.buy_item("Silver", 125000))
        silver_btn.place(x=44, y=300)

        gold_btn = ctk.CTkButton(self.root, text="GOLD\nRp 250.000", width=300, height=80,
                                 font=("Inter", 18, "bold"),
                                 fg_color="#FFD700", hover_color="#B89D00", text_color="black",
                                 command=lambda: self.buy_item("Gold", 250000))
        gold_btn.place(x=44, y=400)
    
    def open_profile(self): #buka gui profile
        profil_window = ctk.CTkToplevel(self.root)
        profil_window.lift()
        profil_window.attributes('-topmost', True)
        profil_window.focus_force()
        profil_window.grab_set()
        ProfilePage(profil_window, self.username)

    def update_saldo(self, saldo):
        self.saldo = saldo
        self.saldo_var.set(f"Rp {saldo:,}".replace(",", "."))

    def logout(self, event=None):
        try:
            self.root.withdraw()
            login_app.deiconify()
        except Exception:
            pass

    def open_topup(self): #buka gui topup
        topup_window = ctk.CTkToplevel(self.root)
        topup_window.lift()
        topup_window.attributes('-topmost', True)
        topup_window.focus_force()
        topup_window.grab_set()
        TopUpApp(topup_window, self)

    def update_username(self, username): #ambil username dari users.csv
        self.username = username
        self.lbl_nama.configure(text=f"Hi, {self.username}")

    def on_hover(self, event):
        pass

    def on_leave(self, event):
        pass
    
    def buy_item(self, item, price):
        if self.saldo >= price:
             self.saldo -= price
             self.update_saldo(self.saldo)
             save_user_data(self.username, item, price, self.saldo)
             self.expired_date = (datetime.now() + timedelta(days=DURASI_MEMBERSHIP[item])).strftime('%d-%m-%Y')
             self.expired_var.set(f"Expired: {self.expired_date}")
             join_date_beli = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
             tkmb.showinfo("Pembelian Berhasil",
                    f"{item} berhasil dibeli!\nHarga: Rp {price:,}\njoin_date: {join_date_beli}".replace(",", "."))
        else:
             tkmb.showerror("Gagal", "Saldo tidak mencukupi!\nSilakan Top Up terlebih dahulu.")

    def load_expired(self, username): #ambil dan simpan expired dari csv
        with open("users.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == username:
                    return row.get("expired", "")
        return ""
    
    def get_remaining_days(self): #expired dikurangi tanggal sekarang
        try:
            if not self.expired_date: return "Tidak ada membership"
            expired = datetime.strptime(self.expired_date, "%d-%m-%Y")
            now = datetime.now()
            if expired < now: return "Expired"
            sisa = expired - now
            return f"{(exp_date - now).days} hari"
        except:
            return "Data tidak valid"
    
 




class TopUpApp:
    def __init__(self, root, main_app,): #inisiasi gui topup
        self.root = root
        self.main_app = main_app
        self.root.title("TopUp - GymEmas")
        center_window(self.root, 300, 400)

        self.bgtopup = safe_open("bg topupnew.png", size=(300, 400))
        self.bgphoto = ctk.CTkImage(light_image=self.bgtopup, size=(300, 400)) 
        self.bglabel = ctk.CTkLabel(self.root, image=self.bgphoto, text="")
        self.bglabel.place(x=0, y=0, relwidth=1, relheight=1)

        ctk.CTkLabel(self.root, text="Masukkan Jumlah Top up", font=("Crimson Text", 12, "bold"),
                     fg_color="#ffbd59", text_color=("#000000"), bg_color="#ffbd59").place(x=80, y=133)

        self.amount_entry = ctk.CTkEntry(self.root, width=111, height=21, border_color=("#FFFFFF"),
                                         placeholder_text="0", bg_color=("#ffbd59"), fg_color=("#767676"))
        self.amount_entry.place(x=94, y=164)

        ctk.CTkButton(self.root, text="topup", width=68, height=24, corner_radius=10,
                      text_color=("#FFFFFF"), fg_color=("#000000"), hover_color=("#6b6262"), 
                      bg_color=("#ffbd59"), command=self.topup).place(x=115, y=233)
        
        home = safe_open("hometopup.png", size=(262, 49))
        self.homephoto = ctk.CTkImage(light_image=home, size=(262, 49)) 
        
    

    def topup(self): #menambah jumlah top up dan disimpan di users.csv
        try:
            amount = int(self.amount_entry.get())
            if amount <= 0: raise ValueError
            self.main_app.saldo += amount
            saldo_baru = self.main_app.saldo
            self.main_app.update_saldo(saldo_baru)
            save_user_data(self.main_app.username, "", "", saldo_baru)
            tkmb.showinfo("Top-Up Berhasil", f"Saldo berhasil ditambahkan sebesar Rp {amount:,}",parent=self.root)
            self.go_back()
        except ValueError:
            tkmb.showerror("Error", "Masukkan jumlah yang valid.",parent=self.root)

    def go_back(self):
        self.root.destroy()




class ProfilePage:
    def __init__(self, root, username):
        self.root = root
        self.username = username
        center_window(self.root, 388, 824)
        self.root.title("Profil Pengguna - GymEmas")
        
        self.bgprofile = safe_open("bg profile.png", size=(688, 1424))
        self.bgphoto = ctk.CTkImage(light_image=self.bgprofile, size=(388, 824)) 
        self.bglabel = ctk.CTkLabel(self.root, image=self.bgphoto, text="")
        self.bglabel.place(x=0, y=0, relwidth=1, relheight=1)

        self.user_data = self.get_user_data()
        
        qr_img = generate_qr(
            self.user_data["username"],
            self.user_data["expired"]
)

        qr_img = qr_img.resize((300, 300))
        self.qr_photo = ImageTk.PhotoImage(qr_img)

        tk.Label(
            self.root,
            image=self.qr_photo,
            bg="white"
).place(x=90, y=425)

        ctk.CTkLabel(self.root, text="Profil", font=("Crimson Text", 32),
                     fg_color="#FFFFFF", text_color=("#000000"), bg_color="#FFFFFF").place(x=150, y=35)

        ctk.CTkLabel(self.root, text=f"Username : {self.user_data['username']}", font=("Crimson Text", 18),
                     fg_color="#FFFFFF", text_color=("#000000"), bg_color="#FFFFFF").place(x=150, y=70)
        
        ctk.CTkLabel(self.root, text=f"Membership : {self.user_data['item'] or '-'}", font=("Crimson Text", 18),
                     fg_color="#FFFFFF", text_color=("#000000"), bg_color="#FFFFFF").place(x=150, y=95)

        ctk.CTkLabel(self.root, text=f"Saldo : Rp {int(self.user_data['saldo']):,}".replace(",", "."),
                     font=("Crimson Text", 18), fg_color="#FFFFFF", text_color=("#000000"), bg_color="transparent").place(x=150, y=120)

        exp = self.user_data["expired"] if self.user_data["expired"] else "-"
        ctk.CTkLabel(self.root, text=f"Expired : {exp}", font=("Crimson Text", 18),
                     fg_color="#FFFFFF", text_color=("#000000"), bg_color="transparent").place(x=150, y=145)

        sisa = self.get_remaining_days()
        ctk.CTkLabel(self.root, text=f"Sisa Waktu : {sisa}", font=("Crimson Text", 18),
                     fg_color="#FFFFFF", text_color=("#000000"), bg_color="transparent").place(x=150, y=170)

        ctk.CTkButton(self.root, text="Logout", fg_color="#B90000",
                      command=self.logout).place(x=125, y=675)

    def get_user_data(self): #ambil data dari users.csv
        with open("users.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["username"] == self.username:
                    return row
        return {"username": "-", "item": "-", "saldo": "0", "expired": "-"}

    def get_remaining_days(self): #tampilkan remaining days
        try:
            expired = self.user_data["expired"]
            if not expired: return "Tidak ada membership"
            exp_date = datetime.strptime(expired, "%d-%m-%Y")
            now = datetime.now()
            if exp_date < now: return "Expired"
            return f"{(exp_date - now).days} hari"
        except:
            return "Data tidak valid"

    def logout(self):
        self.root.destroy()
        login_app.deiconify()
        menu_app.withdraw()


#PROGRAM UTAMA
if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    login_app = ctk.CTk()
    LoginApp(login_app, csv_file_path)   
    init_csv()
    
    menu_app = ctk.CTkToplevel(login_app)
    gym_menu = GymMenu(menu_app, "")
    menu_app.withdraw()
    
    def exit_app():
        sys.exit(0)
        
    login_app.protocol('WM_DELETE_WINDOW', exit_app)
    menu_app.protocol('WM_DELETE_WINDOW', exit_app)
    
    login_app.mainloop()