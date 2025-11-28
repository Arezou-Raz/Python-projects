Final Project: CS50 Cookie Certificate Generator

The final video demo is available here: https://drive.google.com/file/d/1TryDnHgMCUoYek82F1iHLuAvyFK4vHEY/view?usp=sharing

Project Overview and Functionality

Goal and User Interaction The Cookie Certificate Generator is an interactive, console-based Python application designed around the theme of managing a virtual cookie jar. The primary goal is to provide a compelling, persistent loop of interaction that rewards the user upon task completion. The jar is initialized with a set capacity (default: 12), and the user is guided via simple, continuous terminal prompts to perform two main actions: Deposit (D) or Withdraw (W). The current state of the jar is displayed clearly in real-time using a visual representation of the cookies with 🍪 emojis. The program’s main loop ensures continuous interaction until the capacity is reached or the user quits (Q).

Object-Oriented Implementation (The Core Logic) The entire project logic is encapsulated within the Jar class, demonstrating strong Object-Oriented Programming (OOP) principles. The state (the number of cookies, or size) is strictly protected using Python's @property decorators and associated setter methods. This is a critical design choice for security and data integrity. Specifically, the setters for size and capacity ensure that:

Deposits are strictly validated to ensure the new size never exceeds the jar's fixed capacity.

Withdrawals are strictly validated to prevent the size from ever becoming a negative number.

Any violation of these rules immediately raises a ValueError, which is then caught and communicated to the user in the main application loop, preventing the program from crashing while giving the user helpful feedback.

Achievement and External Libraries The "fun payoff" is triggered immediately and only when the Jar reaches full capacity (size == capacity). The application then breaks out of the main interaction loop and calls a dedicated top-level function, generate_certificate. This function is responsible for all external operations:
It utilizes the fpdf2 library to programmatically design and draw a personalized PDF certificate in landscape orientation.

It dynamically places the user's name (collected at startup) and the project title onto the document.

The final, high-quality file ([name]_certificate.pdf) is saved directly into the project folder, creating a tangible, verifiable reward for the user's successful management of the virtual jar.

Project Structure and File Breakdown The project is structured with clean separation of concerns across two primary files:

project.py: This file contains the main application logic. It houses the Jar class definition and the main function that executes the core loop. Crucially, it also contains three required top-level functions, separate from the Jar class, that handle testable, distinct pieces of logic:

check_deposit: Handles pre-validation logic to confirm the input is a positive integer and that capacity won't be exceeded.

get_current_status: Handles all console output formatting, including the use of emojis (🍪, 🟢, 🟡, ⚪) and calculating the fraction (e.g., "5/12 cookies deposited").

generate_certificate: Manages the entire PDF creation process using fpdf2.

test_project.py: This companion file includes unit tests using the pytest framework, covering boundary conditions and edge cases for the core logic (e.g., attempting to withdraw from an empty jar, trying to exceed capacity, and confirming correct str output) for the Jar class and the three testable functions defined in project.py.

Design Choices and Justification

Separation of Concerns for Testing A key design decision was to separate the core state-changing logic (e.g., jar.deposit()) from the complex validation and formatting logic (e.g., check_deposit()). This was done to satisfy the CS50 requirement for at least three separate, testable, top-level functions other than main. By creating check_deposit and get_current_status, the main logic remains clean while providing defined endpoints for comprehensive unit testing in test_project.py.

Image Loading Robustness A notable challenge was ensuring the celebration icon image used in the PDF would load reliably in the checker's containerized environment. Relying on a local file path often fails. Therefore, the generate_certificate function was designed to use the requests library to download the image data from a public URL at runtime. This data is then wrapped in a BytesIO object and passed to pdf.image(). This design choice eliminates dependence on local file paths, making the certificate generation more robust and deployable.

How to Run the Program Ensure you have Python installed, along with the dependencies: pip install -r requirements.txt.

Run the application from your terminal: python project.py

Follow the prompts to Deposit (D), Withdraw (W), or Quit (Q).

Once the jar is full, the personalized certificate will be generated in the project directory.
