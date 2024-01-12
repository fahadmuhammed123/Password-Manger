from cryptography.fernet import Fernet
import random
import string
import json

class PasswordManager:
    def __init__(self, master_password):
        # Generate or load encryption key
        self.key = self.load_or_generate_key(master_password)
        # Initialize Fernet symmetric key encryption
        self.cipher_suite = Fernet(self.key)
        # Load or initialize password database
        self.passwords = self.load_passwords()

    def load_or_generate_key(self, master_password):
        key_file = 'encryption_key.key'
        try:
            # Try to load the key from the file
            with open(key_file, 'rb') as key_file:
                key = key_file.read()
        except FileNotFoundError:
            # If the file doesn't exist, generate a new key and save it
            key = Fernet.generate_key()
            with open(key_file, 'wb') as key_file:
                key_file.write(key)
        return Fernet(master_password.encode()[:32])

    def load_passwords(self):
        password_file = 'passwords.json'
        try:
            # Try to load the passwords from the file
            with open(password_file, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
                decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                passwords = json.loads(decrypted_data.decode())
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or cannot be decrypted, initialize an empty password dictionary
            passwords = {}
        return passwords

    def save_passwords(self):
        password_file = 'passwords.json'
        # Encrypt and save the password dictionary to the file
        encrypted_data = self.cipher_suite.encrypt(json.dumps(self.passwords).encode())
        with open(password_file, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)

    def generate_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for _ in range(length))

    def add_password(self, website, username, password):
        # Store the password securely
        self.passwords[website] = {'username': username, 'password': password}
        self.save_passwords()

    def get_password(self, website):
        # Retrieve the password for a given website
        return self.passwords.get(website, None)

if __name__ == "__main__":
    master_password = input("Enter your master password: ")
    password_manager = PasswordManager(master_password)

    while True:
        print("\nPassword Manager Menu:")
        print("1. Generate Password")
        print("2. Add Password")
        print("3. Get Password")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == '1':
            password_length = int(input("Enter the desired password length: "))
            generated_password = password_manager.generate_password(password_length)
            print(f"Generated Password: {generated_password}")

        elif choice == '2':
            website = input("Enter the website: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            password_manager.add_password(website, username, password)
            print("Password added successfully!")

        elif choice == '3':
            website = input("Enter the website: ")
            stored_password = password_manager.get_password(website)
            if stored_password:
                print(f"Username: {stored_password['username']}")
                print(f"Password: {stored_password['password']}")
            else:
                print(f"No password found for {website}")

        elif choice == '4':
            print("Exiting Password Manager. Goodbye!")
            break

        else:
            print("Invalid choice. Please enter a number between 1 and 4.")
