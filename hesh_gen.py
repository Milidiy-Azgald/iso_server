import bcrypt
password = "admin"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
print(hashed) # Оцей рядок вставте в users.yaml