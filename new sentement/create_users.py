from database import add_user, create_tables

create_tables()

add_user("student1", "123", "student")
add_user("student2", "123", "student")
add_user("student3", "123", "student")

add_user("VENKATARAMANA V", "123", "teacher")
add_user("SHENDE AMIT", "123", "teacher")
add_user("PRAVEEN", "123", "teacher")

add_user("admin", "123", "admin")

print("Users added successfully!")