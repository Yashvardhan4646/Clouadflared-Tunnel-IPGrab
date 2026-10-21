# Cloudflare Tunnel Telemetry & Header Logger

> **Disclaimer**: For educational purposes only. This project is intended solely for demonstrating web networking concepts, reverse-proxy headers, and client-side browser APIs in a controlled environment.

A lightweight experimental project demonstrating how a local Python HTTP server interacts with Cloudflare Tunnels (`cloudflared`), processes edge reverse-proxy headers (`CF-Connecting-IP`), and logs client-reported telemetry.

---

## Architecture Overview

```
[ Client Browser ]
        │  (HTTPS)
        ▼
[ Cloudflare Edge ]
        │  (Secure Tunnel)
        ▼
[ cloudflared daemon ]
        │  (HTTP / localhost:6767)
        ▼
[ Python HTTP Server (server.py) ] ──► writes to ──► [ visits.txt ]
                                                             │
                                                     [ ip.py (ipinfo.io) ]
```

1. **Client Interaction (`index.html`)**: When the page is loaded and interaction occurs, client-side JavaScript queries device telemetry (e.g., Battery Status API) and sends a `POST` request to `/record`.
2. **Reverse Proxy Tunnel (`cloudflared`)**: Exposes the local development port `6767` to the public web via an outbound tunnel. Cloudflare attaches proxy headers such as `CF-Connecting-IP` representing the client's public IP address.
3. **Backend Processing (`server.py`)**: A native Python `http.server` instance handles incoming requests, extracts headers, parses JSON payloads, and appends records into `visits.txt`.
4. **Log Enrichment (`ip.py`)**: A utility script that parses `visits.txt` and queries the `ipinfo.io` API to retrieve geolocation and network provider metadata for recorded IP addresses.

---

## File Structure

| File | Description |
|------|-------------|
| [`server.py`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/server.py) | Python HTTP server listening on port `6767`, serving `index.html` and handling `/record` endpoints. |
| [`index.html`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/index.html) | Responsive front-end interface implementing client-side telemetry via the Battery Status API. |
| [`ip.py`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/ip.py) | Offline log processor that parses `visits.txt` and enriches IPs via the IPInfo REST API. |
| [`visits.txt`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/visits.txt) | Plaintext append-only log file recording timestamps, client IP, and telemetry. |
| [`firstrun.bat`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/firstrun.bat) | Windows batch script to install `cloudflared` using `winget`. |
| [`start.bat`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/start.bat) | Automation script to initialize the server and start the Cloudflare tunnel. |

---

## Prerequisites

- **Python 3.8+**
- **Cloudflare Tunnel CLI (`cloudflared`)**:
  - Install via Windows Package Manager:
    ```cmd
    winget install --id Cloudflare.cloudflared
    ```
- **Python Dependencies**:
  - `requests` (required for `ip.py`):
    ```cmd
    pip install requests
    ```

---

## Setup and Usage

### 1. Launching the Backend Server

Start `server.py` directly using Python:

```cmd
python server.py
```

The server binds to `0.0.0.0:6767`. You can test it locally in your browser by visiting:
```
http://localhost:6767
```

### 2. Exposing via Cloudflare Tunnel

To create a temporary public tunnel to your local server without configuring port forwarding:

```cmd
cloudflared tunnel --url http://localhost:6767
```

`cloudflared` will generate a public URL (e.g., `https://<random-subdomain>.trycloudflare.com`) that routes traffic directly to your local instance.

*(Alternatively, run `start.bat` after updating the project directory path inside the file).*

### 3. Reviewing Logs & Enriching Data

Incoming visits are logged in real time to [`visits.txt`](file:///d:/CERN/Clouadflare-Tunnel-IPGrab/visits.txt) in the following format:
```text
2026-10-21T09:11:37.414715 | IP: 102.432.117.xx (example ip) | Battery: 84% | Charging: No
```

To resolve geolocation and ASN details for all logged IPs:

```cmd
python ip.py
```

---

## Technical & Privacy Notes

- **Proxy Header Detection**: When accessed through Cloudflare, the client's actual remote address is preserved in the `CF-Connecting-IP` header. `server.py` checks this header first before falling back to `self.client_address[0]`.
- **Battery Status API Support**: `navigator.getBattery()` is supported primarily in Chromium-based browsers. Firefox and Safari have intentionally deprecated or disabled this API due to device fingerprinting and user privacy considerations.
- **Privacy Compliance**: Logging public IP addresses and device metrics constitutes personal data collection under frameworks such as GDPR and CCPA. Ensure appropriate user consent and privacy notices are provided when deploying telemetry collectors.
