## FastAPI Final Project - Fashion Store

**GOAL:** *Build a **real-world FastAPI backend application** demonstrating strong API development skills*

**Requirements:**
-   Python **3.8 or higher** (project tested with **Python 3.12**)
-   Git
-   pip (comes with Python)

***Setup and installation***

**1. Clone the repository**

    git clone  
    cd

**2. Create a virtual environment**

Windows:

    python -m venv venv

Mac/Linux:

    python3 -m venv venv


**3. Activate the virtual environment**

Windows (PowerShell):

    venv\Scripts\activate

Windows (cmd):

    venv\Scripts\activate.bat

Mac/Linux:

    source venv/bin/activate

After activation you should see `(venv)` in your terminal.

 **4. Upgrade pip (optional but recommended)**

    python -m pip install --upgrade pip


**5. Install dependencies**

    pip install -r requirements.txt

This installs all required libraries such as FastAPI, Uvicorn, and Pydantic.

** 6. Run the FastAPI server**

    uvicorn main:app --reload

Explanation:

-   **main** → name of the Python file (`main.py`)
-   **app** → FastAPI instance inside the file (`app = FastAPI()`)
-   **--reload** → automatically reloads the server when code changes

*Access the API*

Once the server is running, open the browser:

Swagger Documentation (recommended):

    http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Alternative documentation:

    http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

* Testing Endpoints*

Using Swagger UI you can test endpoints such as:

-   

    GET /products
    -   POST /orders
    -   GET /orders
    -   POST /cart/add
    -   GET /cart
    -   POST /cart/checkout

* Stopping the Server*

Press:

    CTRL + C

in the terminal.


