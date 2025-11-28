import sys
import os
import requests
from io import BytesIO
# Using the fpdf2 library as specified in the project README
from fpdf import FPDF

# --- Jar Class ---

class Jar:
    def __init__(self, capacity=12):
        # Default capacity is 12, as per your working code
        if not isinstance(capacity, int) or capacity < 0:
            raise ValueError("Capacity must be a non-negative integer")
        self._capacity = capacity
        self._size = 0
        self._name = "AREZOU" # Default name for certificate

    def __str__(self):
        # Uses the cookie emoji to show current size
        return "🍪" * self._size

    def deposit(self, n):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Deposit amount must be a positive integer")
        if self._size + n > self._capacity:
            raise ValueError("Exceeds jar capacity")
        self._size += n

    def withdraw(self, n):
        if not isinstance(n, int) or n <= 0:
            raise ValueError("Withdrawal amount must be a positive integer")
        if self._size - n < 0:
            raise ValueError("Not enough cookies in the jar")
        self._size -= n

    @property
    def capacity(self):
        return self._capacity

    @property
    def size(self):
        return self._size

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

# --- Top-Level Functions Required by test_project.py ---

def check_deposit(jar, amount):
    """Checks if a deposit is valid without modifying the jar state."""
    if not isinstance(amount, int) or amount <= 0:
        raise ValueError("Amount must be a positive integer")

    # Check if the deposit exceeds the remaining capacity
    return jar.size + amount <= jar.capacity

def get_current_status(jar):
    """Returns a formatted status string for the console."""
    if jar.size == 0:
        icon = "⚪"
        status = "Jar is empty. Time to deposit!"
    elif jar.size == jar.capacity:
        icon = "🟢"
        status = "Jar is FULL!"
    else:
        icon = "🟡"
        status = f"{jar.size}/{jar.capacity} cookies deposited"

    return f"Status: {icon} {status}"

def generate_certificate(name, cookies):
    """Generates a personalized PDF certificate using fpdf2 and robust image loading."""

    # 1. Setup PDF
    # Landscape orientation, A4 format
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Coordinates for design (A4 Landscape: 297mm wide, 210mm high)

    # 2. Design/Layout

    # Title
    pdf.set_font('Arial', 'B', 36)
    pdf.set_text_color(0, 0, 0) # Black
    # Center title at 20mm from top
    pdf.set_y(20)
    pdf.cell(w=0, h=20, text="CS50 COOKIE CERTIFICATE", border=0, align='C', new_x="LMARGIN", new_y="NEXT")

    # Separator Lines
    pdf.set_x(40)
    pdf.set_line_width(0.5)
    pdf.line(40, 45, 257, 45) # Top line
    pdf.line(40, 47, 257, 47) # Second line

    # Body Text
    pdf.set_y(60)
    pdf.set_font('Arial', '', 18)
    pdf.cell(w=0, h=10, text="This certifies that", border=0, align='C', new_x="LMARGIN", new_y="NEXT")

    # Name (similar style to your image)
    pdf.set_font('Arial', 'B', 48)
    pdf.set_text_color(165, 42, 42) # Brown
    pdf.cell(w=0, h=25, text=name.upper(), border=0, align='C', new_x="LMARGIN", new_y="NEXT")

    # Achievement Text
    pdf.set_font('Arial', '', 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(w=0, h=10, text=f"Successfully managed and earned a total of {cookies} cookies", border=0, align='C', new_x="LMARGIN", new_y="NEXT")


    IMAGE_URL = "https://cdn-icons-png.flaticon.com/512/1047/1047711.png"

    try:
        response = requests.get(IMAGE_URL)
        response.raise_for_status() # Check for bad response status
        image_data = BytesIO(response.content)

        # Place image roughly in the center of the free space
        # x=135 is center of A4 landscape, y=100 is about 1/2 way down
        pdf.image(image_data, x=135, y=100, w=30)

    except requests.exceptions.RequestException as e:
        # If the image fails to load, print a warning but continue
        print(f"Warning: Could not load celebration icon for certificate: {e}")

    # Signature/Footer
    pdf.set_y(-30) # Position 30mm from the bottom
    pdf.set_x(40)
    pdf.line(40, pdf.get_y(), 257, pdf.get_y()) # Signature line
    pdf.set_font('Arial', '', 12)
    pdf.cell(w=0, h=10, text="The Cookie Master", border=0, align='C')

    # 4. Output
    filename = f"{name.lower().replace(' ', '_')}_certificate.pdf"
    pdf.output(filename)
    return filename

# --- Main Interaction Loop ---

def main():
    # Set up the jar, with the 12 capacity you used
    jar = Jar(capacity=12)

    # Get user's name once at the start
    name = input("Enter your name: ").strip()
    if name:
        # Update jar's name property
        jar.name = name

    while True:
        print("=" * 30)
        print(get_current_status(jar))
        print("=" * 30)

        # Main action loop
        action = input("Action (D: deposit, W: withdraw, Q: quit): ").strip().upper()

        if action == 'Q':
            print("Thank you for playing!")
            sys.exit(0)

        elif action == 'D':
            try:
                amount = int(input("How many cookies to deposit? "))
                if not check_deposit(jar, amount):
                     # Error message reflecting remaining capacity
                     print(f"🛑 Error: Cannot deposit {amount}. Only {jar.capacity - jar.size} space left.")
                     continue

                jar.deposit(amount)
                print(f"✅ Deposited {amount} cookies. Jar now has {jar.size}.")

                # Check for FULL jar condition (which triggers your certificate)
                if jar.size == jar.capacity:
                    print("\n🎉 JAR IS FULL! Generating Certificate...")
                    filename = generate_certificate(jar.name, jar.size)
                    print("\n🥳 CONGRATULATION YOUR COOKIE CERTIFICATE IS READY")
                    print(f"Certificate saved as {filename}")

            except ValueError as e:
                print(f"🛑 Invalid input or operation: {e}")
            except Exception as e:
                print(f"🛑 An unexpected error occurred: {e}")

        elif action == 'W':
            try:
                amount = int(input("How many cookies to withdraw? "))
                jar.withdraw(amount)
                print(f"✅ Withdrew {amount} cookies. Jar now has {jar.size}.")

            except ValueError as e:
                print(f"🛑 Invalid input or operation: {e}")
            except Exception as e:
                print(f"🛑 An unexpected error occurred: {e}")

        else:
            print("❌ Invalid action. Please enter D, W, or Q.")

if __name__ == "__main__":
    main()
