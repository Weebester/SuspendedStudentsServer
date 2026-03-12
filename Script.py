import bcrypt

#Script to genrate app admins accounts hashed passwords
def hash_password(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def check_password(password: str, hashed_password: str) -> bool:
    
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


if __name__ == "__main__":
    password = "test2"
    hashed_password = hash_password(password)
    print(f"Hashed Password: {hashed_password}")
    
    is_valid = check_password(password, hashed_password)
    print(f"Password is valid: {is_valid}")
    print(None == -200)