import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

def menu(current_id):
    print("Öğretmen paneline hoşgeldiniz.")
    match input("\n1 - Not Yükle\n2 - Sınıf Notlarını Görüntüle\n3 - Ders Notlarını Görüntüle\n4 - Çıkış\n\nSeçim Yapınız: "):
        case "1":
            not_yukle(current_id)
        case "2":
            view_class_grades(current_id)
        case "3":
            view_subject_grades(current_id)
        case "4":
            import main
            main.menu()
        case _:
            print("Hatalı girdi")
            menu()

def not_yukle(current_id):
    stu_id = int(input("Not vermek istediğiniz öğrencinin ID'sini giriniz: "))
    taken_classes = cur.execute("""SELECT subjects.Name FROM grades 
                                LEFT JOIN subjects ON grades.subject_id = subjects.id 
                                WHERE grades.student_id=? AND teacher_id=?""", (stu_id, current_id,)).fetchall()
    if not taken_classes:
        new_student = input("Öğrenci sizin verdiğiniz dersleri almıyor. Eklemek ister misiniz? (Y/N): ").lower()
        if new_student != "y":
            menu(current_id)
        else:
            teacher_subjects = cur.execute("SELECT id, name FROM subjects WHERE teacher_id=?", (current_id,)).fetchall()
            print(teacher_subjects)
            new_subject = input("Öğrenciyi eklemek istediğiniz dersin IDsini yazınız: ")
            cur.execute("INSERT INTO grades (student_id, subject_id) VALUES (?, ?)", (stu_id, new_subject,))
            taken_classes = cur.execute("""SELECT subjects.Name FROM grades 
                                LEFT JOIN subjects ON grades.subject_id = subjects.id 
                                WHERE grades.student_id=? AND teacher_id=?""", (stu_id, current_id,)).fetchall()
    subject_names = [subject[0] for subject in taken_classes]
    print(subject_names)
    stu_subject = input("Not vermek istediğiniz dersi seçiniz: ")
    subject_id_row = cur.execute("SELECT id FROM subjects WHERE name=?", (stu_subject,)).fetchone()
    subject_id = subject_id_row[0] if subject_id_row else None
    if stu_subject not in subject_names:
        print("Hatalı girdi.")
        menu(current_id)
    new_grade = int(input("Girmek istediğiniz not: "))
    match input("Not Güncelleme Ekranı\n1 - 1. Sınav\n2 - 2. Sınav\n3 - Proje\n4 - Geri\nSeçim Yapınız: "):
        case "1":
            cur.execute("UPDATE grades SET exam1=? WHERE student_id=? AND subject_id=?", (new_grade, stu_id, subject_id))
        case "2":
            cur.execute("UPDATE grades SET exam2=? WHERE student_id=? AND subject_id=?", (new_grade, stu_id, subject_id))
        case "3":
            cur.execute("UPDATE grades SET project=? WHERE student_id=? AND subject_id=?", (new_grade, stu_id, subject_id))
        case "4":
            pass
        case _:
            print("Hatalı giriş.")
    grades = cur.execute("SELECT exam1, exam2, project FROM grades WHERE student_id=? AND subject_id=?", (stu_id, subject_id)).fetchall()
    average = 0
    for grade in grades[0]:
        if grade == None:
            break
        average += grade
    average /= len(grades[0])
    cur.execute("UPDATE grades SET average=? WHERE student_id=? AND subject_id=?", (average, stu_id, subject_id))
    con.commit()
    print("Not başarıyla güncenlendi.")
    menu(current_id)
    
def view_class_grades(current_id):
    classes = cur.execute("SELECT name FROM classes WHERE teacher_id=?", (current_id,)).fetchall()
    class_names = [a_class[0] for a_class in classes]
    print(class_names)
    selected_class = input("Görüntülemek istediğiniz sınıfı seçiniz: ")
    if selected_class not in class_names:
        print("Hatalı girdi.")
        menu(current_id)
    elif not classes:
        print("Hiçbir sınıfa atanmamışsınız.")
        menu(current_id)
    class_id_row = cur.execute("SELECT id FROM classes WHERE name=?", (selected_class,)).fetchone()
    class_id = class_id_row[0] if class_id_row else None
    class_to_view = cur.execute("""SELECT users.id, username, subjects.name, exam1, exam2, project, average
                                FROM users
                                LEFT JOIN grades ON users.id = grades.student_id
                                LEFT JOIN subjects ON grades.subject_id = subjects.id
                                LEFT JOIN students ON students.user_id = users.id 
                                WHERE class_id=?""", (class_id,)).fetchall()
    for grade in class_to_view:
        print(f"ID: {grade[0]} - Ad: {grade[1]} - Ders: {grade[2]} - Notlar: {grade[3]} - {grade[4]} - {grade[5]} - Ortalama: {grade[6]}")
    menu(current_id)

def view_subject_grades(current_id):
    subjects = cur.execute("SELECT name FROM subjects WHERE teacher_id=?", (current_id,)).fetchall()
    subject_names = [subject[0] for subject in subjects]
    if not subjects:
        print("Hiçbir derse atanmamışsınız.")
        menu(current_id)
    print(subject_names)
    selected_subject = input("Görüntülemek istediğiniz dersi seçiniz: ")
    if selected_subject not in subject_names:
        print("Hatalı girdi.")
        menu(current_id)
    subject_id_row = cur.execute("SELECT id FROM subjects WHERE name=?", (selected_subject,)).fetchone()
    subject_id = subject_id_row[0] if subject_id_row else None
    subject_to_view = cur.execute("""SELECT users.id, username, exam1, exam2, project, average
                                FROM users
                                LEFT JOIN grades ON users.id = grades.student_id
                                LEFT JOIN subjects ON grades.subject_id = subjects.id
                                LEFT JOIN students ON students.user_id = users.id 
                                WHERE grades.subject_id=?""", (str(subject_id))).fetchall()
    for grade in subject_to_view:
        print(f"ID: {grade[0]} - Ad: {grade[1]} - Notlar: {grade[2]} - {grade[3]} - {grade[4]} - Ortalama: {grade[5]}")
    menu(current_id)
