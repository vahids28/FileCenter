# 📦 FileCenter v2.1

> A lightweight, secure file sharing platform built with pure Python - no external dependencies!

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1-orange.svg)](https://github.com/yourusername/filecenter)

## ✨ Features

- 🔐 **Secure Authentication** - Username & password protected admin panel
- 📤 **Easy Upload** - Drag & drop or click to upload files
- 🔒 **Public/Private Files** - Control who can access each file
- 🌐 **Show on Home** - Toggle file visibility on public page
- 📋 **Copy Links** - One-click copy of download links
- 🔍 **Search & Sort** - Find files quickly with search and sorting options
- 📱 **Fully Responsive** - Works perfectly on desktop, tablet, and mobile
- 🌙 **Dark/Light Mode** - Choose your preferred theme
- ⚙️ **Admin Settings** - Configure max file size, allowed extensions, site appearance
- 📊 **Statistics Dashboard** - Track total files, downloads, and storage usage
- 🚀 **Pure Python** - No external dependencies, runs on any Python 3 installation

## 🚀 Quick Start

### Prerequisites
- Python 3.6 or higher
- Linux/Unix system (Ubuntu 22.04 recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/filecenter.git
cd filecenter

# Navigate to version 2.1
cd v2.1

# Run the server
python3 server.py
```

### Default Login
- **Username:** `vahids28`
- **Password:** `1375123456`

### Access Points
- **Public Page:** `http://localhost:3000`
- **Admin Panel:** `http://localhost:3000/admin`

## 📁 Project Structure

```
v2.1/
├── server.py              # Main server application
├── static/
│   ├── css/
│   │   └── style.css      # Styles and themes
│   └── uploads/           # Uploaded files storage
├── templates/
│   ├── index.html         # Public file listing page
│   ├── admin.html         # Admin dashboard
│   └── login.html         # Login page
├── files.json             # File metadata database
├── settings.json          # Application settings
└── allowed_extensions.json # Allowed file types
```

## 🛠️ Configuration

### Admin Settings
- **General:** Maximum file size (1-2048 MB)
- **Security:** Change username/password
- **Extensions:** Manage allowed file types
- **Appearance:** Site name and description

### Allowed File Types (Default)
```
pdf, jpg, jpeg, png, gif, mp4, mp3, webm,
zip, rar, 7z, tar, gz, txt, md, doc, docx,
xls, xlsx, ppt, pptx, csv, json, xml, html, css, js
```

## 🔧 Systemd Service (Optional)

For permanent running:

```bash
sudo nano /etc/systemd/system/filecenter.service
```

```ini
[Unit]
Description=FileCenter v2.1
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/v2.1
ExecStart=/usr/bin/python3 /path/to/v2.1/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable filecenter
sudo systemctl start filecenter
```

## 🎯 Features in Detail

### Public Page
- Browse all public files marked for home display
- Search files by name
- Click file names to download (opens in new tab)
- Pagination (10/20/50 files per page)

### Admin Panel
- Upload files with drag & drop
- Set default visibility (public/private)
- Toggle "Show on Home" for public files
- Copy download links with one click
- Search, sort, and filter files
- File statistics dashboard
- System settings management

### File Visibility Rules
- **Private:** Only admin can view and download
- **Public:** Anyone can download
- **Show on Home:** Only public files can appear on the public page

## 🛡️ Security Features

- Filename sanitization (removes dangerous characters)
- File type validation by extension
- Basic header checks for malicious content
- Session-based authentication
- No external dependencies - minimal attack surface
- Rate limiting on login attempts

## 📊 API Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/files` | GET | Get public files | No |
| `/api/files/all` | GET | Get all files | Yes |
| `/api/upload` | POST | Upload file | Yes |
| `/api/login` | POST | User login | No |
| `/api/check-auth` | GET | Check auth status | No |
| `/api/settings` | GET/PUT | Get/update settings | Yes |
| `/api/allowed-extensions` | GET/PUT | Manage extensions | Yes |
| `/api/visibility/:id` | PUT | Change file visibility | Yes |
| `/api/showonhome/:id` | PUT | Toggle home display | Yes |
| `/api/delete/:id` | DELETE | Delete file | Yes |
| `/download/:id` | GET | Download file | Varies |

## 🐛 Troubleshooting

### Port already in use
```bash
# Change port in server.py
PORT = 8080  # or any available port

# Or kill existing process
sudo lsof -i :3000
sudo kill -9 <PID>
```

### Login issues
- Check credentials: `vahids28` / `1375123456`
- Clear browser cookies
- Ensure no trailing spaces in username

### Upload fails
- Check allowed extensions
- Verify file size limit
- Check disk space: `df -h`

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing`)
5. Open a Pull Request

## ⚡ Performance

- Handles multiple concurrent uploads
- Efficient file streaming for downloads
- Lightweight memory footprint
- No database required - JSON file storage

## 🎨 Customization

### Change Default Credentials
Edit `server.py`:
```python
DEFAULT_USERNAME = 'your_username'
DEFAULT_PASSWORD = 'your_password'
```

### Modify Allowed Extensions
Via admin panel or edit `allowed_extensions.json`

### Custom Styling
Edit `static/css/style.css` to match your brand

## 📞 Support

- Create an issue on GitHub
- Check troubleshooting section above
- Review systemd logs: `journalctl -u filecenter -f`

---

**Made with ❤️ using Python | Secure & Simple File Sharing**
```
