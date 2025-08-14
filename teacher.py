import sqlite3, os

path = os.path.dirname(os.path.realpath(__file__))
con = sqlite3.connect(path + "\\db1.db")
cur = con.cursor()

def menu(current_id):
    while True:
        print("Öğretmen paneline hoşgeldiniz.")
        match input("\n1 - Not Yükle\n2 - Sınıfımın Notlarını Görüntüle\n3 - Ders Notlarını Görüntüle\n4 - Çıkış\n\nSeçim Yapınız: "):
            case "1":
                not_yukle(current_id)
            case "2":
                view_class_grades(current_id)
            case "3":
                view_subject_grades(current_id)
            case "4":
                return
            case _:
                print("Hatalı girdi")

def not_yukle(current_id):
    view_subject_grades(current_id)
    class_ids = [row[0] for row in cur.execute("SELECT class_id FROM class_subjects WHERE teacher_id=?", (current_id,)).fetchall()]
    if not class_ids:
        print("Bu öğretmenin sınıfı yok.")
        return
    stu_id = input("Not vermek istediğiniz öğrencinin ID'sini giriniz: ")

    i = 0
    for a_class in class_ids:
        student_ids = [row[0] for row in cur.execute("SELECT user_id FROM students WHERE class_id=?", (a_class,)).fetchall()]
        if int(stu_id) in student_ids:
            break
        else:
            i += 1
            if i == len(class_ids):
                print("Öğrenci sınıfınızda değil")
                return
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
        return
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
    
def view_class_grades(current_id):
    classes = cur.execute("""SELECT name FROM classes WHERE teacher_id=?""", (current_id,)).fetchall()
    classes += cur.execute("""SELECT name FROM class_subjects
                               LEFT JOIN classes ON classes.id = class_subjects.class_id
                               WHERE class_subjects.teacher_id=?""", (current_id,)).fetchall()
    class_names = [a_class[0] for a_class in classes]
    if not classes:
        print("Hiçbir sınıfa atanmamışsınız.")
        return
    print(class_names)
    selected_class = input("Görüntülemek istediğiniz sınıfı seçiniz: ")
    if selected_class not in class_names:
        print("Hatalı girdi.")
        return
    class_id_row = cur.execute("SELECT id FROM classes WHERE name=?", (selected_class,)).fetchone()
    class_id = class_id_row[0] if class_id_row else None
    class_to_view = cur.execute("""SELECT users.id, username, subjects.name, exam1, exam2, project, average 
                                FROM users LEFT JOIN grades ON users.id = grades.student_id 
                                LEFT JOIN subjects ON grades.subject_id = subjects.id 
                                LEFT JOIN students ON students.user_id = users.id 
                                LEFT JOIN class_subjects ON class_subjects.class_id = students.class_id 
                                WHERE students.class_id=? AND class_subjects.teacher_id=? """, (class_id, current_id,)).fetchall()
    for grade in class_to_view:
        print(f"ID: {grade[0]} - Ad: {grade[1]} - Ders: {grade[2]} - Notlar: {grade[3]} - {grade[4]} - {grade[5]} - Ortalama: {grade[6]}")

def view_subject_grades(current_id):
    subjects = cur.execute("SELECT subject_id FROM class_subjects WHERE teacher_id=?", (current_id,)).fetchall()
    if not subjects:
        print("Hiçbir derse atanmamışsınız.")
        return
    subject_ids = [row[0] for row in subjects]
    placeholders = ",".join("?" for _ in subject_ids)
    subjects_names = cur.execute(f"SELECT name FROM subjects WHERE id IN ({placeholders})", subject_ids).fetchall()
    given_subject_names = [subject[0] for subject in subjects_names]
    print(given_subject_names)
    selected_subject = input("Görüntülemek istediğiniz dersi seçiniz: ")
    if selected_subject not in given_subject_names:
        print("Hatalı girdi.")
        return
    subject_id_row = cur.execute("SELECT id FROM subjects WHERE name=?", (selected_subject,)).fetchone()
    subject_id = subject_id_row[0] if subject_id_row else None
    subject_to_view = cur.execute("""
        SELECT users.id, username, exam1, exam2, project, average
        FROM users
        LEFT JOIN grades ON users.id = grades.student_id
        LEFT JOIN students ON students.user_id = users.id
        LEFT JOIN class_subjects ON class_subjects.class_id = students.class_id
        WHERE grades.subject_id=? AND class_subjects.teacher_id=?
    """, (subject_id, current_id)).fetchall()
    for grade in subject_to_view:
        print(f"ID: {grade[0]} - Ad: {grade[1]} - Notlar: {grade[2]} - {grade[3]} - {grade[4]} - Ortalama: {grade[5]}")
