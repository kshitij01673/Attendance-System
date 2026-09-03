# Attendance System

A Python-based attendance management system that combines **QR-code identification**, **face detection**, a **FastAPI backend**, and a **SQLite database** to record attendance.

## Overview

The project is divided into three main components:

* **Client** — scans a user's QR code, captures a photo when exactly one face is detected, and sends attendance data to the server.
* **Server** — provides a FastAPI API that validates the device and user information before marking attendance.
* **Admin Panel** — provides a command-line interface for managing users and attendance devices.

The system uses SQLite to store users, registered devices, and daily attendance records.

## Features

* QR-code based user identification
* Face detection using OpenCV YuNet
* FastAPI attendance API
* SQLite database
* User management

  * Add users
  * View users
  * Delete users
* Device management

  * Add devices
  * View devices
  * Delete devices
* Automatically generated user authentication codes
* Automatically generated device IDs
* Daily attendance initialization
* Attendance records with date, time, status, and device information
* API health-check endpoint

## Project Structure

```text
Attendance-System/
│
├── admin_pannel.py              # Admin panel for managing users/devices
├── client.py                    # QR scanning, face detection and API client
├── server.py                    # FastAPI attendance server
│
├── utils/
│   ├── dbms_controller.py       # Database and attendance operations
│   ├── qrgen.py                 # QR code generation
│   ├── qrread.py                # QR code scanning
│   └── attendance.db            # SQLite database
│
├── files/
│   └── face_detection_yunet_2026may.onnx
│
├── .gitignore
├── LICENSE
└── README.md
```

## How It Works

### 1. Register a Device

Start the admin panel:

```bash
python admin_pannel.py
```

Select **Device Management → Add Device** and provide the device location.

The system generates a unique device ID which is stored in the database.

### 2. Register a User

From the admin panel, select:

```text
User Management
    └── Add User
```

Enter the user's name.

The system generates:

* A unique user ID
* A unique authentication code
* A QR code containing the user's information

The QR code can then be used by the client during attendance.

### 3. Start the Server

Run:

```bash
python server.py
```

The FastAPI server starts on port `8000`.

You can also run it using Uvicorn:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Run the Client

Before running the client, configure the server address and registered device ID in `client.py`.

Then run:

```bash
python client.py
```

The client will:

1. Scan the user's QR code.
2. Read the user's name, ID and authentication code.
3. Open the camera.
4. Detect faces using YuNet.
5. Capture a photo when exactly one face is detected.
6. Send the attendance request to the server.
7. Display the attendance result.

## System Flow

```text
             ┌─────────────────┐
             │    QR Code      │
             │     Scan        │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  User Details   │
             │ Name / ID / Key │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  Face Detection │
             │     (YuNet)     │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  FastAPI Server │
             └────────┬────────┘
                      │
             ┌────────┴────────┐
             ▼                 ▼
      Device Validation   User Validation
             │                 │
             └────────┬────────┘
                      ▼
             ┌─────────────────┐
             │ Mark Attendance  │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ SQLite Database │
             └─────────────────┘
```

## API

### Health Check

```http
GET /
```

Example response:

```json
{
  "status": "online",
  "message": "Attendance Server Running"
}
```

### Mark Attendance

```http
POST /attendance
```

Request body:

```json
{
  "name": "Student Name",
  "user_id": 1,
  "secret_code": "user-auth-code",
  "device_id": "device-id"
}
```

The server validates:

1. Whether the device is registered.
2. Whether the user exists with the provided details.
3. Whether the authentication code is valid.
4. Whether today's attendance record can be updated.

Possible responses include:

```text
Invalid Device
User Not Found
Invalid Security Code
Attendance Failed
Attendance Marked Successfully
```

## Database

The system uses **SQLite**.

### Users

Stores registered users:

| Field        | Description           |
| ------------ | --------------------- |
| `id`         | Unique user ID        |
| `name`       | User's name           |
| `hash`       | Authentication code   |
| `created_at` | Account creation time |

### Devices

Stores registered attendance devices:

| Field      | Description            |
| ---------- | ---------------------- |
| `S_no`     | Database serial number |
| `id`       | Unique device ID       |
| `location` | Device location        |

### Attendance

Stores daily attendance:

| Field         | Description            |
| ------------- | ---------------------- |
| `S_no`        | Database serial number |
| `id`          | User ID                |
| `date`        | Attendance date        |
| `time`        | Attendance time        |
| `presence`    | Present/Absent status  |
| `ab_approved` | Approval status        |
| `device_id`   | Device used            |

Daily attendance records are initialized with students marked absent. When a student successfully checks in, their record is updated to present with the current time and device ID.

## Requirements

The project is written in Python and uses libraries including:

* [FastAPI](https://fastapi.tiangolo.com/)
* [Uvicorn](https://www.uvicorn.org/)
* [Pydantic](https://docs.pydantic.dev/)
* [APScheduler](https://apscheduler.readthedocs.io/)
* [Requests](https://requests.readthedocs.io/)
* [OpenCV](https://opencv.org/)

Install the main dependencies with:

```bash
pip install fastapi uvicorn pydantic apscheduler requests opencv-python
```

Additional dependencies may be required by the QR-code utilities in `utils/qrgen.py` and `utils/qrread.py`.

## Configuration

Open `client.py` and configure:

```python
SERVER_URL = "http://<server-ip>:8000/attendance"
DEVICE_ID = "<registered-device-id>"
```

For example:

```python
SERVER_URL = "http://192.168.1.5:8000/attendance"
DEVICE_ID = "devf0XXXX"
```

The device ID must correspond to a device registered in the admin panel.

Make sure the client device can communicate with the machine running the FastAPI server.

## Face Detection

The client uses **OpenCV's YuNet face detector**.

The model file is expected at:

```text
files/face_detection_yunet_2026may.onnx
```

The client only captures an image when **exactly one face** is detected.

Captured images are saved in:

```text
photos/
```

## Running the Complete System

### Terminal 1 — Admin Panel

```bash
python admin_pannel.py
```

Register your users and devices.

### Terminal 2 — Server

```bash
python server.py
```

Start the FastAPI attendance server.

### Terminal 3 — Client

```bash
python client.py
```

Scan the user's QR code and complete attendance.

## Security Notes

This project is intended for development and controlled-network use.

For production deployment, consider adding:

* HTTPS
* Proper API authentication
* Secure secret storage
* Access control for the admin panel
* Better protection for authentication codes
* Secure storage and handling of captured photographs
* Input validation and rate limiting
* Environment variables for configuration and secrets

Do not expose the attendance API directly to the public internet without appropriate security measures.

## Future Improvements

Possible improvements include:

* Web-based admin dashboard
* Attendance reports and analytics
* Export attendance to CSV/Excel
* Student search and filtering
* Multiple attendance sessions per day
* Improved authentication
* Facial recognition instead of basic face detection
* Cloud database support
* Automated email/notification system
* Docker deployment
* Mobile application for attendance monitoring

## License

This project is licensed under the **MIT License**. See the [`LICENSE`](LICENSE) file for details.

## Author

**kshitij01673**

GitHub: https://github.com/kshitij01673
