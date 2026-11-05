# Django Password Manager

A web-based Password Manager developed using Python and Django. It allows users to securely store, manage, and organize their account credentials.

## Features

- User registration and login
- Secure password encryption using Fernet
- Add and save account credentials
- View and reveal saved passwords
- Edit and delete saved accounts
- Mark accounts as favourites
- Search by website or username
- Filter accounts by category
- User-specific password vault
- Django admin panel

## Technologies Used

- Python
- Django
- HTML
- CSS
- SQLite
- Cryptography (Fernet)
- python-dotenv

## Installation and Setup

1. Clone the repository:

   `git clone YOUR_REPOSITORY_URL`

2. Navigate into the project folder:

   `cd PasswordManager`

3. Install the required packages:

   `py -m pip install -r requirements.txt`

4. Create a `.env` file in the project root and add your own Fernet encryption key:

   `PASSWORD_ENCRYPTION_KEY=YOUR_GENERATED_KEY`

   Generate a key locally using Fernet's `generate_key()` function. Never share or upload your actual key.

5. Apply database migrations:

   `py manage.py migrate`

6. Start the development server:

   `py manage.py runserver`

7. Open `http://127.0.0.1:8000/` in your browser.

## Security Note

This project is developed for educational and demonstration purposes. Do not use it to store real or sensitive passwords without a thorough security review.

Keep your `.env` file and encryption key private. Losing the encryption key means encrypted passwords cannot be recovered.

## Developer

Developed as an academic project using Python and Django.
## TEST
