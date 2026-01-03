import os
import json


DATA = "data/students.json"


def ensure_data_dir():
    """Ensure the directory for DATA exists."""
    dirpath = os.path.dirname(DATA)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)


def load_data():
    if not os.path.exists(DATA):
        return {}
    try:
        with open(DATA, "r") as file:
            return json.load(file) or {}
    except (json.JSONDecodeError, ValueError):
        # Corrupted or empty file -> treat as empty store
        return {}


def save_data(students: dict):
    ensure_data_dir()
    with open(DATA, "w") as file:
        json.dump(students, file, indent=4)


def students_list():
    print("\n------- Students List -------\n")
    print("1. add student")
    print("2. view students")
    print("3. update student")
    print("4. delete student")
    print("5. exit")


def add_student():
    students = load_data()
    # simple numeric id generation (string keys)
    student_id = str(len(students) + 1)
    name = input("Enter student name: ").strip()
    age = input("Enter student age: ").strip()
    class_name = input("Enter class: ").strip()
    phone = input("Enter phone number: ").strip()

    students[student_id] = {
        "name": name,
        "age": age,
        "class": class_name,
        "phone": phone,
    }

    save_data(students)
    print("Student added successfully!!!")


def view_student():
    students = load_data()
    if not students:
        print("No students found on record")
        return
    print("ID\tName\tAge\tClass\tPhone")
    print("-" * 45)
    for sid, info in students.items():
        print(f"{sid}\t{info.get('name','')}\t{info.get('age','')}\t{info.get('class','')}\t{info.get('phone','')}")


def update_student():
    students = load_data()
    student_id = input("Enter the id of the student: ").strip()
    if student_id not in students:
        print("Student not found")
        return
    students[student_id]["name"] = input("Enter new name: ").strip() or students[student_id]["name"]
    students[student_id]["age"] = input("Enter new age: ").strip() or students[student_id]["age"]
    students[student_id]["class"] = input("Enter new class: ").strip() or students[student_id]["class"]
    students[student_id]["phone"] = input("Enter new phone number: ").strip() or students[student_id]["phone"]
    save_data(students)
    print("Student updated successfully!!!")


def delete_student():
    students = load_data()
    student_id = input("Enter the id of the student to delete: ").strip()
    if student_id in students:
        del students[student_id]
        save_data(students)
        print("Student deleted successfully!!!")
    else:
        print("Student not found")


def main():
    while True:
        students_list()
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            add_student()
        elif choice == "2":
            view_student()
        elif choice == "3":
            update_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()