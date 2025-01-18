# LingoApp - Your Personal Vocabulary Builder

LingoApp is a modern web application designed to help users build and enhance their vocabulary. With features like word search, personal word collections, and interactive learning tools, LingoApp makes vocabulary learning engaging and effective.

## Features

- **Word Search**: Look up word definitions, pronunciations, and examples
- **Personal Word Library**: Save and organize your favorite words
- **User Authentication**: Secure login and registration system
- **Interactive Interface**: Modern, user-friendly design
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- Python 3.x
- Django
- Bootstrap 5
- SQLite
- Free Dictionary API

## Prerequisites

- Python 3.x
- Pipenv

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd wordapp
```

2. Install dependencies using Pipenv:

```bash
pipenv install
```

3. Activate the virtual environment:

```bash
pipenv shell
```

4. Run database migrations:

```bash
python manage.py migrate
```

5. Start the development server:

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Usage

1. **Registration/Login**

   - Create a new account or log in with existing credentials
   - Access your personal word collection

2. **Searching Words**

   - Use the search feature to look up word definitions
   - View detailed information including pronunciations and examples

3. **Managing Your Words**
   - Save interesting words to your collection
   - Review and organize your saved words
   - Remove words from your collection

## API Integration

LingoApp uses the Free Dictionary API to fetch word definitions and related information. The API provides:

- Word definitions
- Pronunciations
- Example usage
- Part of speech

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
