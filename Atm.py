from db import get_connection

class ATM:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()
        self.login = False

    def valid_number(self, num):
        return len(num) == 10 and num[0] in ['6','7','8','9']

    def valid_pin(self, pin):
        return len(pin) == 4

    def password(self):
        self.num = input("\nEnter your mobile number: ")

        if not self.valid_number(self.num):
            print("Invalid number!")
            return

        query = "SELECT * FROM users WHERE account_number=%s"
        self.cursor.execute(query, (self.num,))
        user = self.cursor.fetchone()

        if not user:
            print("Account not found! Creating new account...")

            while True:
                pin = input("Set 4-digit PIN: ")

                if not self.valid_pin(pin):
                    print("Invalid PIN!")
                    continue

                self.cursor.execute("SELECT * FROM users WHERE pin=%s", (pin,))
                existing_pin = self.cursor.fetchone()

                if existing_pin:
                    print("This PIN is already used! Try different PIN.")
                else:
                    break

            insert_query = "INSERT INTO users (account_number, pin, balance) VALUES (%s, %s, %s)"
            self.cursor.execute(insert_query, (self.num, pin, 0))
            self.conn.commit()

            print("\nAccount created successfully!")
            print("------ Welcome To ATM ------\n")

            self.login = True
            return

        attempt = 0
        while attempt < 3:
            pin = input("Enter PIN: ")
            if pin == str(user[1]):
                print("Login successful")
                self.login = True
                break
            else:
                attempt += 1
                print("Wrong PIN")

    def menu(self):
        print("1. Balance\n2. Deposit\n3. Withdraw\n4. Change PIN\n5. Exit")

    def check_balance(self):
        self.cursor.execute("SELECT balance FROM users WHERE account_number=%s",(self.num,))
        print("Balance:", self.cursor.fetchone()[0])

    def deposit(self):
        amt = int(input("Enter amount: "))
        if amt > 0:
            self.cursor.execute("UPDATE users SET balance=balance+%s WHERE account_number=%s",(amt,self.num))
            self.conn.commit()
            print("Deposited")

    def withdraw(self):
        amt = int(input("Enter amount: "))
        self.cursor.execute("SELECT balance FROM users WHERE account_number=%s",(self.num,))
        bal = self.cursor.fetchone()[0]

        if amt <= bal:
            self.cursor.execute("UPDATE users SET balance=balance-%s WHERE account_number=%s",(amt,self.num))
            self.conn.commit()
            print("Withdrawn")
        else:
            print("Insufficient balance")

    def change_pin(self):
        old = input("Old PIN: ")
        self.cursor.execute("SELECT pin FROM users WHERE account_number=%s",(self.num,))
        if old == str(self.cursor.fetchone()[0]):
            new = input("New PIN: ")
            if self.valid_pin(new):
                self.cursor.execute("UPDATE users SET pin=%s WHERE account_number=%s",(new,self.num))
                self.conn.commit()
                print("PIN changed")

    def run(self):
        self.password()
        if not self.login:
            return

        while True:
            self.menu()
            ch = input("Choice: ")

            if ch == "1":
                self.check_balance()
            elif ch == "2":
                self.deposit()
            elif ch == "3":
                self.withdraw()
            elif ch == "4":
                self.change_pin()
            elif ch == "5":
                break