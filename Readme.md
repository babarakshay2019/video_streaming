# Video Streaming App

Video Streaming App is built using Python-DRF.

## Installation Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/babarakshay2019/video_streaming.git
    ```

2. Navigate to the project directory:

    ```bash
    cd video_streaming
    ```

3. Create a virtual environment (optional but recommended):

    ```bash
    python3 -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

5. Install requirements:
    ```bash
    pip install -r requirements.txt
    ```

6. Run the application:
    ```bash
    python manage.py runserver
    ```

#### Video Streaming

- **Register User**
  - Method: POST
  - URL: `/api/register/`
  - Description: Register a new user.

- **Login User**
  - Method: POST
  - URL: `/api/login/`
  - Description: Authenticate and log in a user.

- **Create Video**
  - Method: POST
  - URL: `/api/videos/`
  - Description: Create a video after login.

- **List of Videos**
  - Method: GET
  - URL: `/api/videos/`
  - Description: List of created videos after login.

- **Update Video**
  - Method: PUT/PATCH
  - URL: `/api/videos/video_id/`
  - Description: Update videos after login.

- **Delete Video**
  - Method: DELETE
  - URL: `/api/videos/video_id/`
  - Description: DELETE videos after login.

- **Search Video**
  - Method: GET
  - URL: `/api/videos/?search=video_name`
  - Description: Search videos by name.

- **Watch videos**
  - Method: GET
  - URL: `/api/stream/<int:video_id>/`
  - Description: Watch video after login.

7. Run test cases:
    ```bash
    python manage.py test
    ```