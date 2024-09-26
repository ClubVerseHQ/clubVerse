<h1 align="center">Club Verse</h1>

![Club Verse](https://github.com/user-attachments/assets/2155932f-204a-4c6f-ab43-c28526469aec "Club Verse Logo")


![Status](https://img.shields.io/badge/status-in%20production-red)

## Table of Contents
- [Tech Stack](#-tech-stack)
- [Installation](#installation)
- [Features (Soon...)](#features-soon)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

# 💻 Tech Stack:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) 
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)

## Installation

### Cloning from GitHub Repository

To get started with the clubVerse Web App, you can clone the repository from GitHub using the following steps:
 
1. **Clone the repository**:

   ```bash
   git clone https://github.com/fardin-faisal/clubVerse.git

2. Navigate to the project folder:
   ```bash
   cd clubVerse
   
3. Create and activate a virtual environment (optional but recommended):
   ```bash
   py -m venv myworld
   myworld\Scripts\activate.bat
4. Install project dependencies:
   ```bash
   pip install -r requirements.txt
   
5. Create a .env file in your project root & add keys:
   ```bash
   python generate_keys.py

6. Check .env file and follow the link for Email setup
   <a href="https://www.geeksforgeeks.org/setup-sending-email-in-django-project/">Geekforgeeks email setup in django</a>

7. Run database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   
8. Create a superuser account (for admin access)
   ```bash
   python manage.py createsuperuser
   
9. Start the development server:
   ```bash
   python manage.py runserver
   
10. Open your web browser and go to http://localhost:8000 to access the clubVerse Web App.

## Features (Soon...)
The Club Verse Web App includes the following key features:

- **User Authentication: Secure management with sign-in, sign-up, and password recovery options.
- **Admin Dashboard**: A centralized interface for managing users and clubs efficiently.
- **Profile Management**: Users can easily view and update their profile information.
- **Club Management**: Create and manage club details, including membership and settings.
- **Event Collaboration**: Enable clubs to collaborate on events, enhancing participation.
- **Activity Feeds**: Display recent activities and announcements from clubs to boost engagement.
- **Dark Mode**: A user-friendly dark theme for improved usability in low-light environments.

## Contributing

We welcome contributions to improve the clubVerse Web App. If you'd like to contribute, please follow these guidelines:

1. Fork the repository.

2. Create a new branch for your feature or bug fix.

3. Make your changes and test them thoroughly.

4. Submit a pull request with a clear description of your changes.

5. Ensure your code follows best practices and includes necessary tests if applicable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For any inquiries, please reach out to us at: [clubverse.dev@gmail.com](mailto:clubverse.dev@gmail.com)
