pip install -r requirements.txt

Google Drive Folder ID: 1x7KWkr3OsnbqVZeuExffUUNJiPUHshIg


1)
Install OpenCV and Other Required Libraries: Ensure that OpenCV, Google libraries (google-auth, google-api-python-client, etc.), and other libraries like pygetwindow, mss, and numpy are installed. These should be handled by the requirements.txt file, but it's good to double-check.

2) you'll need to set up Google Cloud credentials (OAuth client) on the new machine to allow the script to upload files to Google Drive.

a. Set Up Google Cloud Project: On the new machine, download the client_secret.json (OAuth credentials) from Google Cloud Console. Follow the same steps as you did initially to create and download credentials:

    Go to the Google Cloud Console.

    Create a project (if you haven’t already).

    Set up OAuth credentials and download the JSON file.

b. Update the client_secret.json Path:

    Make sure the path to the client_secret.json file is updated on the new machine.

    You can either put it in the same folder as your script, or update the path in your script to point to the correct location.

3. Set Up the Reference Image

The reference image (scoreboard_reference.jpg) should be copied to the new machine as well. Just make sure that the image is located in the correct path, or prompt the user to input the path to the reference image when running the script.

a. Update the Image Path in the Script: If you're using a path that’s different on the new machine, you can either:

    Manually set the path before running the script (by updating the script each time).

    Use input prompts to ask for the reference image’s path (already in your current code).