# Scraping

Super Scraper is a modern web scraping solution built with FastAPI, Next.js, and LangChain. It allows users to scrape static and dynamic web pages, crawl multiple pages, generate scraping code using OpenAI, and store scraped data in DOC or Excel files. The frontend is built using Next.js and styled with Tailwind CSS for a modern user interface.


## Features

- Scrape static and dynamic web pages
- Crawl through multiple pages and follow links
- Generate scraping code using OpenAI's GPT-4
- Store scraped data in DOC or Excel files
- Perform advanced language model tasks with LangChain
- Modern and responsive frontend built with Next.js and Tailwind CSS


## Tech Stack

### Backend (`main.py`)
- **FastAPI**: A modern, fast (high-performance) web framework for building APIs with Python 3.6+.
- **Scrapy**: An open-source and collaborative web crawling framework for Python.
- **Selenium**: A portable framework for testing web applications.
- **BeautifulSoup**: A library for parsing HTML and XML documents.
- **OpenAI**: Integration for generating code using GPT-4.
- **LangChain**: Framework for language model tasks.
- **python-docx**: A library for creating and updating Microsoft Word (.docx) files.
- **pandas**: A powerful data manipulation library, used here to create Excel files.
- **BackgroundTasks**: Used for saving scraped data asynchronously.

### Frontend (`Next.js`)
- **Next.js**: A React framework for production, which makes it easy to build server-rendered React applications.
- **Tailwind CSS**: A utility-first CSS framework for rapid UI development.

### Forms (`Form.js`)
- A reusable form component that posts data to different endpoints (`scrape`, `crawl`, `generate_scraper`, and `langchain_task`).

### Main Page (`index.js`)
- Contains forms for scraping, crawling, generating scraper code, and performing LangChain tasks.
- Displays results in a formatted JSON view.


## Project Structure

```
scrapping/
├── backend/
│   ├── main.py              # FastAPI server
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── components/
│   │   └── Form.js          # Form component for user input
│   ├── pages/
│   │   └── index.js         # Main page
│   ├── public/              # Public assets
│   ├── styles/
│   │   └── globals.css      # Global styles
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   ├── postcss.config.js    # PostCSS configuration
│   └── package.json         # Node.js dependencies
└── .....
```


## Prerequisites

- Python 3.7+
- Node.js 12+
- Chrome browser (for Selenium)


## Installation

### Backend Setup
```bash
python -m venv venv
source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-api-key"
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Open your browser and navigate to `http://localhost:3000`.


## Usage
1. Use the forms on the main page to:
   - Scrape a webpage
   - Crawl a website
   - Generate scraping code
   - Perform a LangChain task
2. View the results in the Results section.
