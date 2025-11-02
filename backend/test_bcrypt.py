import bcrypt

# Test bcrypt
password = "test1234"
password_bytes = password.encode('utf-8')
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password_bytes, salt)

print(f"Password: {password}")
print(f"Salt: {salt}")
print(f"Hashed: {hashed}")

# Test verification
is_valid = bcrypt.checkpw(password_bytes, hashed)
print(f"Verification: {is_valid}")