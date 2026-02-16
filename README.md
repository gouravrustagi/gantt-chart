# 📊 Gantt Chart Generator

A powerful, mobile-first Progressive Web App (PWA) for creating professional Gantt charts with AI-powered features. Built with Flask and powered by Google Gemini AI.

![Version](https://img.shields.io/badge/version-2.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

### 🎨 Visualization
- **14 Chart Types**: Standard, Timeline, Milestone, Compact, Waterfall, Critical Path, Resource View, Progress, Dependencies, Baseline, Swimlane, Calendar, Gantt Bars, Comparison
- **14 Color Schemes**: Corporate, Vibrant, Pastel, Ocean, Sunset, Forest, Monochrome, Neon, Autumn, Spring, Midnight, Candy, Earth, Tropical
- **High-Quality Charts**: Export charts as PNG images

### 📱 Mobile-First Design
- **Fully Responsive**: Works seamlessly on all devices (phones, tablets, desktops)
- **PWA Support**: Install as native app on iOS and Android
- **Adaptive UI**: Responsive logout button and controls that scale with screen size
- **Touch-Optimized**: Easy task management with touch gestures

### 🔒 Security & Privacy
- **User Isolation**: Each user sees only their own data
- **Session-Based Auth**: Secure API key authentication with Google Gemini
- **No Data Sharing**: Complete privacy between users

### ⚡ Task Management
- **Sequential Mode**: Automatic task chaining - tasks follow each other automatically
- **Task Editing**: Modify task names, dates, and durations with automatic sequence updates
- **Smart Duration**: Support for days (d), hours (h), and minutes (m)
- **Real-Time Updates**: Instant task list and chart regeneration
- **Bulk Actions**: Clear all tasks at once

### 🎯 User Experience
- **Clean Dropdown Menus**: Easy access to all 14 chart types and color schemes
- **Emoji Icons**: Visual indicators for better navigation
- **Instant Feedback**: Success and error messages
- **Downloadable Charts**: One-click download of generated charts

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/gouravrustagi/gantt-chart.git
cd gantt-chart
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the app**
- **Desktop**: http://localhost:5000
- **Mobile**: http://YOUR_IP_ADDRESS:5000 (same WiFi network)

5. **Enter your API key**
- On first visit, enter your Google Gemini API key
- The app will authenticate and you can start creating charts

## 📖 Usage Guide

### Adding Tasks

1. Enter task details:
   - **Task Name**: Descriptive name for your task
   - **Start Date**: When the task begins
   - **Duration**: Format: `5d`, `3h`, `2d 4h` (days, hours, minutes)

2. Click **➕ Add Task**

3. Tasks appear in the list with edit (✏️) and delete (✖) buttons

### Sequential Mode

- **Toggle On**: Tasks automatically follow each other
- **Toggle Off**: Manually set start dates for each task
- When enabled, editing a task updates all subsequent tasks

### Editing Tasks

1. Click the **✏️** button on any task
2. Modify name, start date, or duration
3. Click **💾 Save Changes**
4. If Sequential Mode is on, subsequent tasks adjust automatically

### Generating Charts

1. Select **Chart Type** from dropdown (14 options)
2. Select **Color Scheme** from dropdown (14 options)
3. Click **🎨 Generate Chart**
4. View the chart and click **⬇️ Download Chart** to save

### Installing as PWA

#### On Android/Chrome:
1. Click the "Install App" button that appears
2. Or use browser menu → "Install App" / "Add to Home Screen"

#### On iOS/Safari:
1. Tap the Share button (⬆️)
2. Select "Add to Home Screen"
3. Confirm installation

## 🎨 Chart Types Explained

| Chart Type | Description |
|------------|-------------|
| 📊 Standard | Classic Gantt chart with horizontal bars |
| ⏱️ Timeline | Enhanced view with date labels on bars |
| 🎯 Milestone | Marker-based view for key deliverables |
| 📦 Compact | Space-efficient minimal design |
| 💧 Waterfall | Sequential progress tracking |
| 🔴 Critical Path | Highlights critical project dependencies |
| 👥 Resource View | Team/resource allocation visualization |
| 📈 Progress | Shows completion status and progress |
| 🔗 Dependencies | Displays task relationships |
| 📏 Baseline | Compares planned vs actual timelines |
| 🏊 Swimlane | Organized by categories/departments |
| 📅 Calendar | Calendar-based timeline view |
| ▬ Gantt Bars | Traditional bar chart style |
| ⚖️ Comparison | Side-by-side comparison view |

## 🎨 Color Schemes

- **🏢 Corporate**: Professional blue-gray tones
- **🌈 Vibrant**: Bold, energetic colors
- **🎨 Pastel**: Soft, gentle hues
- **🌊 Ocean**: Cool blue-cyan gradient
- **🌅 Sunset**: Warm orange-red palette
- **🌲 Forest**: Natural green tones
- **⚫ Monochrome**: Grayscale elegance
- **💡 Neon**: Bright, electric colors
- **🍂 Autumn**: Warm brown-orange tones
- **🌸 Spring**: Fresh, light pastels
- **🌙 Midnight**: Dark purple shades
- **🍬 Candy**: Sweet pink tones
- **🌍 Earth**: Natural brown palette
- **🏝️ Tropical**: Bright, exotic colors

## 📱 Screen Size Optimization

The app adapts to your screen:

- **Large Desktop (1200px+)**: Maximum space utilization
- **Desktop (default)**: Balanced layout
- **Tablet (768px)**: Touch-optimized controls
- **Mobile (600px)**: Compact, efficient design
- **Small Phones (360px)**: Ultra-compact interface

## 🔧 Technical Details

### Tech Stack
- **Backend**: Flask (Python)
- **AI**: Google Gemini API
- **Charts**: Matplotlib
- **Frontend**: Vanilla JavaScript (ES6+)
- **UI**: Responsive CSS with media queries
- **Storage**: In-memory session-based storage

### Architecture
- Session-based user isolation
- RESTful API endpoints
- Progressive Web App with Service Worker
- Base64 image encoding for charts
- Dynamic chart generation with multiple renderers

### API Endpoints
- `POST /verify_api_key` - Authenticate user
- `POST /logout` - End user session
- `POST /add_task` - Add new task
- `GET /get_tasks` - Retrieve user tasks
- `PUT /update_task/<index>` - Edit task
- `DELETE /remove_task/<index>` - Delete task
- `POST /clear_tasks` - Remove all tasks
- `POST /generate_chart` - Create chart image
- `POST /download_chart` - Download chart file
- `GET /get_progressive_mode` - Get mode status
- `POST /toggle_progressive_mode` - Toggle sequential mode

## 📂 Project Structure

```
gantt-chart/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── ganttchrt.py          # Desktop version (optional)
├── requirements.txt       # Python dependencies
├── package.json          # Node/npm config (if needed)
├── vercel.json           # Vercel deployment config
├── templates/
│   └── index.html        # Main UI template
├── static/
│   ├── styles.css        # Responsive CSS
│   ├── manifest.json     # PWA manifest
│   ├── service-worker.js # PWA service worker
│   └── icon-*.png        # App icons (various sizes)
├── downloads/            # Generated chart files
└── docs/
    ├── API_SETUP.md      # API configuration guide
    ├── DEPLOYMENT.md     # Deployment instructions
    ├── APK_GUIDE.md      # Android packaging guide
    └── iOS_INSTALL.md    # iOS installation guide
```

## 🌐 Deployment

### Vercel (Recommended)
```bash
vercel --prod
```

### Heroku
```bash
heroku create gantt-chart-app
git push heroku master
```

### Local Network
```bash
# Find your IP address
ipconfig  # Windows
ifconfig  # Mac/Linux

# Access from mobile: http://YOUR_IP:5000
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Gourav Rustagi**
- GitHub: [@gouravrustagi](https://github.com/gouravrustagi)

## 🙏 Acknowledgments

- Google Gemini AI for API support
- Matplotlib for chart generation
- Flask framework
- All contributors and users

## 📞 Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the documentation files in the docs/ folder
- Review the API_SETUP.md for API configuration help

---

Made with ❤️ by Gourav Rustagi | © 2026
