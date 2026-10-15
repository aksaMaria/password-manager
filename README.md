# Password Manager 🔐

A simple password manager project designed to help users organize and manage their passwords in one place.

## 📌 About the Project

The Password Manager is a software project focused on making password management easier. It provides a foundation for storing and managing password-related information through an application built with Python and Django.

This project is also useful for learning about web application development, database management, and user data handling.

## ✨ Features

- Password management in one place
- Organized project structure using Django
- Database integration with SQLite
- Python-based application
- Simple foundation for further development

*Features depend on the current implementation of the project.*

## 🛠️ Technologies Used

- **Python** — Application logic
- **Django** — Web application framework
- **SQLite** — Database
- **HTML, CSS and JavaScript** — User interface, if included in the application

## 📂 Project Structure

```text
password-manager/
├── config/       # Project configuration
├── vault/        # Password manager application
├── db.sqlite3    # SQLite database
└── manage.py     # Django management script
```

## 🚀 Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.10 or later
- pip
- Git

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/aksaMaria/password-manager.git
```

**2. Navigate to the project directory**

```bash
cd password-manager
```

**3. Create a virtual environment**

```bash
python -m venv venv
```

**4. Activate the virtual environment**

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

**5. Install dependencies**

If a `requirements.txt` file is available:

```bash
pip install -r requirements.txt
```

**6. Apply database migrations**

```bash
python manage.py migrate
```

**7. Start the development server**

```bash
python manage.py runserver
```

Open the following address in your browser:

http://127.0.0.1:8000/

## 🔒 Security Note

Password managers handle sensitive information. Do not store real passwords in an unverified or untrusted application. Review the project's authentication, password storage, and encryption mechanisms before using it for personal credentials.

## 🔮 Future Improvements

- Password generation
- Search and filter options
- Password strength checking
- Improved authentication
- Secure password encryption
- Responsive user interface

## 👩‍💻 Author

**aksaMaria**

GitHub: [@aksaMaria](https://github.com/aksaMaria)

## 📄 License

No license information has been specified here. Check the repository for licensing details before redistributing or modifying the project.
