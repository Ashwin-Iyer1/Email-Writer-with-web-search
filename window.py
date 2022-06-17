import tkinter as tk
from tkinter import *
import os
import subprocess
import smtplib
from email.message import EmailMessage
import os.path
from os.path import exists
window = Tk()

username = tk.StringVar()
sites = tk.IntVar()
pages = tk.StringVar()
password = tk.StringVar()
window.geometry("1424x1024")
window.configure(bg = "#ffffff")
canvas = Canvas(
    window,
    bg = "#ffffff",
    height = 1024,
    width = 1424,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
canvas.place(x = 0, y = 0)

def btn_clicked():
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        try:
            smtp.login(username.get(), password.get())
            
            for widget in window.winfo_children():
                widget.destroy()
            f = open('login.txt', "w")
            f.write(username.get()+"\n"+ password.get())
            #subprocess.call(['python', 'window2.py'])
            f.close()
            window2()
        except:
           canvas.create_text(700, 712, text = "Your Username or Password is incorrect", fill="#BC3C3C", font=("Roboto", 25))
           canvas.pack()
def login():
    background_img = PhotoImage(file = f"Pictures/First Page/background.png")
    background = canvas.create_image(
        712.0, 512.0,
        image=background_img)

    entry0_img = PhotoImage(file = f"Pictures/First Page/img_textBox0.png")
    entry0_bg = canvas.create_image(
        1076.0, 332.0,
        image = entry0_img)

    entry0 = Entry(
        bd = 0,
        textvariable = username,
        bg = "#959595",
        highlightthickness = 0)
    entry0.configure(font =("Futura", 20))
    entry0.place(
        x = 881.0, y = 292,
        width = 390.0,
        height = 78)

    entry1_img = PhotoImage(file = f"Pictures/First Page/img_textBox1.png")
    entry1_bg = canvas.create_image(
        1076.0, 520.0,
        image = entry1_img)

    entry1 = Entry(
        bd = 0,
        textvariable = password,
        bg = "#959595",
        highlightthickness = 0)
    entry1.configure(font =("Futura", 20))

    entry1.place(
        x = 881.0, y = 480,
        width = 390.0,
        height = 78)

    img0 = PhotoImage(file = f"Pictures/First Page/img0.png")
    b0 = Button(
        image = img0,
        borderwidth = 0,
        highlightthickness = 0,
        command = btn_clicked,
        relief = "flat")

    b0.place(
        x = 971, y = 617,
        width = 176,
        height = 72)

    window.resizable(False, False)
    window.mainloop()
def window2():
    def btn_clicked1():
            
        entry0.place_forget()
        canvas.delete(entry0_img)
        canvas.delete(background_img)
        canvas.delete(background)
        canvas.delete(entry0_bg)
        b0.destroy()
        background_img1 = PhotoImage(file = f"Pictures/Second page/background1.png")
        background1 = canvas.create_image(
        670, 345.5,
        image=background_img1)
        b1 = Button(
            image = img0,
            borderwidth = 0,
            highlightthickness = 0,
            command = lambda:[btn_clicked2()],
            relief = "flat")

        b1.place(
            x = 604, y = 527,
            width = 142,
            height = 48)

        entry1_img = PhotoImage(file = f"Pictures/Second page/img_textBox1.png")
        entry1_bg = canvas.create_image(
        650.5, 434.5,
        image = entry1_img)

        entry1 = Entry(
            bd = 0,
            textvariable = sites,
            bg = "#d9d9d9",
            highlightthickness = 0)
        entry1.configure(font =("Futura", 20))
        entry1.place(
            x = 570.5, y = 390,
            width = 160.0,
            height = 87)
        img1 = PhotoImage(file = f"Pictures/Second page/img0.png")
        global web
        web = (pages.get())
        window.mainloop()

    def btn_clicked2():
            global page
            page = (sites.get())
            window.destroy()



    canvas = Canvas(
        window,
        bg = "#ffffff",
        height = 1024,
        width = 1424,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge")
    canvas.place(x = 0, y = 0)
    entry0 = Entry(
        bd = 0,
        textvariable = pages,
        bg = "#d9d9d9",
        highlightthickness = 0)
    entry0.configure(font =("Futura", 20))
    entry0.place(
        x = 265, y = 395,
        width = 950.0,
        height = 80)
    supback = PhotoImage(file=f"Pictures/Second page/SupBack.png")
    supbackround = canvas.create_image(
        712, 512,
        image = supback)
    entry0_img = PhotoImage(file = f"Pictures/Second page/img_textBox0.png")
    entry0_bg = canvas.create_image(
        712.0, 434.5,
        image = entry0_img)





    background_img = PhotoImage(file = f"Pictures/Second page/background.png")
    background = canvas.create_image(
        656.5, 345.5,
        image=background_img)

    img0 = PhotoImage(file = f"Pictures/Second page/img0.png")
    b0 = Button(
        image = img0,
        borderwidth = 0,
        highlightthickness = 0,
        command = lambda:[btn_clicked1()],
        relief = "flat")

    b0.place(
        x = 604, y = 527,
        width = 142,
        height = 48)


    window.resizable(False, False)
    window.mainloop()


if(exists("login.txt")):
    if(os.stat("login.txt").st_size > 0):
        file = open('login.txt') 
        content = file.readlines()
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            try:
                smtp.login(content[0], content[1])

                window2()


            except Exception:
                login()
else:
    login()

