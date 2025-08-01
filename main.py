import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

class User:
    def __init__(self, username, role):
        self.username = username
        self.role = role

class Principal(User): pass
class VicePrincipal(User): pass
class Teacher(User):
    def __init__(self, username):
        super().__init__(username, "teacher")
        self.subjects = []
        self.classes = []

class Student(User):
    def __init__(self, username, student_class):
        super().__init__(username, "student")
        self.student_class = student_class
        self.grades = {}

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
elif role == "vice_admin":
    pass
elif role == "teacher":
    import teacher
    teacher.menu(current_id)
elif role == "student":
    import student
    student.menu(current_id)
