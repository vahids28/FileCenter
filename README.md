
# 📦 FileCenter v2.2

> Lightweight, secure file sharing platform built with pure Python - no external dependencies!

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.2-orange.svg)](https://github.com/yourusername/filecenter)

## ✨ Features

- 🔐 **Secure Authentication** - Username & password protected admin panel
- 📤 **Easy Upload** - Drag & drop or click to upload files
- 🔒 **Public/Private Files** - Control who can access each file
- 🌐 **Show on Home** - Toggle file visibility on public page (only for public files)
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

# Navigate to version 2.2
cd v2.2

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
v2.2/
├── server.py              # Main server application
├── static/
│   ├── css/
│   │   └── style.css      # Styles and themes
│   └── uploads/           # Uploaded files storage
├── templates/
│   ├── index.html         # Public file listing page
│   ├── admin.html         # Admin dashboard
│   └── login.html         # Login page
├── files.json             # File metadata database (auto-created)
├── settings.json          # Application settings (auto-created)
└── allowed_extensions.json # Allowed file types (auto-created)
```

## 🛠️ Configuration

### Admin Settings
| Section | Settings |
|---------|----------|
| **General** | Maximum file size (1-2048 MB) |
| **Security** | Change username/password |
| **Extensions** | Manage allowed file types |
| **Appearance** | Site name and description |

### Allowed File Types (Default)
```
pdf, jpg, jpeg, png, gif, mp4, mp3, webm, zip, rar, 7z, tar, gz,
txt, md, doc, docx, xls, xlsx, ppt, pptx, csv, json, xml, html, css, js
```

## 🎯 File Visibility Rules

| Status | Description |
|--------|-------------|
| **Private** | Only admin can view and download |
| **Public** | Anyone can download via direct link |
| **Show on Home** | Only public files can appear on public page |

## 🔧 Systemd Service (Permanent Run)

```bash
# Create service file
sudo nano /etc/systemd/system/filecenter.service
```

```ini
[Unit]
Description=FileCenter v2.2
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/filecenter/v2.2
ExecStart=/usr/bin/python3 /root/filecenter/v2.2/server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable filecenter
sudo systemctl start filecenter

# Check status
sudo systemctl status filecenter

# View logs
sudo journalctl -u filecenter -f
```

## 📊 Admin Panel Features

### Upload Section
- Drag & drop file upload
- Progress bar with percentage
- Default visibility setting
- Auto-public when "Show on Home" enabled

### File Management
- **Search** - Filter files by name
- **Sort** - By name, date, size, downloads
- **Filter** - All, Public, Private
- **Pagination** - 10/20/50/100 items per page
- **Actions** - Make public/private, delete, download, copy link

### Statistics Dashboard
- Total files count
- Public files count
- Private files count
- Total storage usage

## 🛡️ Security Features

- ✅ Filename sanitization (removes dangerous characters)
- ✅ File type validation by extension
- ✅ Basic header checks for malicious content
- ✅ Session-based authentication
- ✅ No external dependencies - minimal attack surface
- ✅ Rate limiting on login attempts
- ✅ Secure cookie handling

## 📡 API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
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
PORT = 8080

# Or kill existing process
sudo lsof -i :3000
sudo kill -9 <PID>
```

### Login issues
- Check credentials: `vahids28` / `1375123456`
- Clear browser cookies
- Ensure no trailing spaces

### Upload fails
- Check allowed extensions
- Verify file size limit
- Check disk space: `df -h`

### Show on Home not working
- File must be **Public** first
- Click on the toggle switch (not just text)
- Check browser console for errors

## 📝 Changelog

### v2.2 (Latest)
- ✅ Fixed Show on Home toggle - now works with click on slider
- ✅ Fixed copy link button with Clipboard API
- ✅ Added sort functionality (name, date, size, downloads)
- ✅ Added search filter in admin panel
- ✅ Added pagination (10/20/50/100 items per page)
- ✅ Fully responsive design for mobile/tablet
- ✅ Action buttons with text labels
- ✅ Wider layout for better content display

### v2.1
- Public/Private file visibility
- Copy download link button
- System settings management

### v2.0
- Complete rewrite with pure Python
- Session-based authentication
- File type validation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open Pull Request

## 📄 License

MIT License - Free to use and modify!

## ⚡ Performance

- Handles multiple concurrent uploads
- Efficient file streaming for downloads
- Lightweight memory footprint (~50MB RAM)
- No database required - JSON file storage

## 🙏 Support

- Create an issue on GitHub
- Check troubleshooting section
- Review systemd logs: `journalctl -u filecenter -f`

---

**Made with ❤️ using Python | Secure & Simple File Sharing**
```
