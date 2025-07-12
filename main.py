import os
import io
import time
import cv2
import numpy as np
import pygetwindow as gw
import mss
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive.file']
#HI
# Prompt user for credentials file and Drive folder ID
CREDENTIALS_FILE = input("Enter path to Google API credentials JSON file: ").strip()
DRIVE_FOLDER_ID = input("Enter Google Drive folder ID: ").strip()
REFERENCE_IMAGE_PATH = input("Enter path to reference image: ").strip()

def authenticate_google_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def upload_to_google_drive(image, filename):
    service = authenticate_google_drive()
    image_buffer = io.BytesIO()
    success, encoded_image = cv2.imencode(".png", image)
    if not success:
        print("❌ Failed to encode image for upload.")
        return
    image_buffer.write(encoded_image.tobytes())
    image_buffer.seek(0)
    media = MediaIoBaseUpload(image_buffer, mimetype='image/png', resumable=True)
    file_metadata = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ Uploaded: {filename} (ID: {file['id']})")

def capture_specific_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]
        if not window.isActive:
            print("⏸️ Window not active — skipping this check.")
            return None, None
        left, top, width, height = window.left, window.top, window.width, window.height
        with mss.mss() as sct:
            screenshot = sct.grab({"left": left, "top": top, "width": width, "height": height})
            img = np.array(screenshot)
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (left, top, width, height)
    except IndexError:
        print(f"❌ Window '{window_title}' not found!")
        return None, None

def find_reference_in_window(screen_img, reference_img):
    result = cv2.matchTemplate(screen_img, reference_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return max_loc if max_val >= 0.3 else None

def resize_reference_image(reference_img, screen_width, screen_height):
    ref_height, ref_width = reference_img.shape[:2]
    if ref_width > screen_width or ref_height > screen_height:
        scale_width = screen_width / ref_width
        scale_height = screen_height / ref_height
        scale = min(scale_width, scale_height)
        new_width = int(ref_width * scale)
        new_height = int(ref_height * scale)
        resized_reference = cv2.resize(reference_img, (new_width, new_height))
        return resized_reference
    return reference_img

def image_hash(image):
    return hash(image.tobytes())

# Load reference image
reference_img = cv2.imread(REFERENCE_IMAGE_PATH, cv2.IMREAD_GRAYSCALE)
if reference_img is None:
    print("❌ Could not load reference image.")
    exit()

window_title = input("Enter the window title to capture: ").strip()
last_uploaded_hash = None
cooldown_seconds = 15
last_upload_time = 0

print("🔄 Starting scoreboard monitor loop...\n")

while True:
    screen_img, window_coords = capture_specific_window(window_title)
    if screen_img is not None:
        screen_height, screen_width = screen_img.shape[:2]
        resized_reference = resize_reference_image(reference_img, screen_width, screen_height)
        match_location = find_reference_in_window(screen_img, resized_reference)
        if match_location:
            x, y = match_location
            ref_h, ref_w = resized_reference.shape[:2]
            cropped_img = screen_img[y:y + ref_h, x:x + ref_w]

            current_hash = image_hash(cropped_img)
            current_time = time.time()
            if current_hash != last_uploaded_hash and (current_time - last_upload_time) > cooldown_seconds:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"captured_scoreboard_{timestamp}.png"
                upload_to_google_drive(cropped_img, filename)
                last_uploaded_hash = current_hash
                last_upload_time = current_time
            else:
                print("⚠️ Duplicate scoreboard or too soon — skipping.")
        else:
            print(f"[{time.strftime('%H:%M:%S')}] No scoreboard detected.")
    time.sleep(5)
