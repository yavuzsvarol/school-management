import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

tries = 3
print("\nOkul BYS")
while True:
    print("\nKalan deneme hakkınız:", tries)
    current_id = int(input("\nKullanici ID giriniz: "))
    current_passw = input("Şifreyi giriniz: ")
    data = [current_id, current_passw]
    users = cur.execute("SELECT id, password FROM users WHERE id=? AND password=?", data)
    if (users.fetchone() is None):
        print("Kullanici adi veya sifre hatali")
        tries -= 1
        if tries == 0:
            print("Çok fazla deneme yaptınız, program sonlandırılıyor.")
            con.close()
            exit()
        continue
    else:
        role = cur.execute("SELECT role FROM users WHERE id=?", (current_id,)).fetchone()[0]
        break

if role == "admin":
    import principal
    principal.menu()
elif role == "teacher":
    import teacher
    teacher.menu(current_id)
elif role == "student":
    import student
    student.menu(current_id)
