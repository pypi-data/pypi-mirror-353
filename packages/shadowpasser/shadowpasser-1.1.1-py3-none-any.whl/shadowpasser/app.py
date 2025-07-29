import sys
import os
import random
import math

from PyQt5.QtCore import (QUrl, Qt, QPropertyAnimation, QEasingCurve, QTimer, 
                         QRect, QParallelAnimationGroup, QPoint, QSize)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QHBoxLayout, 
                            QVBoxLayout, QWidget, QStyle, QLabel, 
                            QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtGui import (QColor, QPixmap, QIcon, QPainter, QBrush, QRadialGradient, 
                         QLinearGradient, QFont, QFontDatabase, QPainterPath, QPen)

BASE_DOMAIN = "service-fb-examly-io-7tvaoi4e5q-uk.a.run.app"
BLOCK_PATH_PREFIX = "/api"
ALLOWED_DOMAIN = "extensionvalidator-341302862392.asia-south1.run.app"

CHROME_USER_AGENT = (
    b"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.40 Safari/537.36"
)

class UrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl()
        domain = url.host()
        path = url.path()
        full = url.toString()

        if ALLOWED_DOMAIN in domain:
            info.redirect(QUrl("about:blank"))
            print(f"[PyQt Allowed] {full}")
        elif BASE_DOMAIN in domain and path.startswith(BLOCK_PATH_PREFIX):
            info.block(True)
            print(f"[PyQt Blocked] {full}")
        else:
            info.setHttpHeader(b"User-Agent", CHROME_USER_AGENT)
            info.setHttpHeader(b"Sec-Ch-Ua", b"\"Not;A=Brand\";v=\"24\", \"Chromium\";v=\"137\"")
            info.setHttpHeader(b"Sec-Ch-Ua-Mobile", b"?0")
            info.setHttpHeader(b"Sec-Ch-Ua-Platform", b"\"Windows\"")
            info.setHttpHeader(b"Accept", b"*/*")
            info.setHttpHeader(b"Accept-Encoding", b"gzip, deflate, br")
            info.setHttpHeader(b"Accept-Language", b"en-US")
            info.setHttpHeader(b"Upgrade-Insecure-Requests", b"1")

class WebEnginePage(QWebEnginePage):
    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        domain = url.host()
        path = url.path()
        if ALLOWED_DOMAIN in domain:
            return True
        if BASE_DOMAIN in domain and path.startswith(BLOCK_PATH_PREFIX):
            print(f"[Blocked Navigation] {url.toString()}")
            return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def javaScriptConsoleMessage(self, level, msg, line, sourceID):
        print(f"[JS] Line {line}: {msg}")

def create_cyan_icon(size=32):
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("gray"))
    return QIcon(pixmap)

class HexagonGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hex_size = 60
        self.offset_x = 0
        self.offset_y = 0
        self.active_hexagons = []
        self.connections = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_grid)
        self.timer.start(50)
        
        self.generate_hexagons()
        
    def generate_hexagons(self):
        self.active_hexagons = []
        width = self.width()
        height = self.height()
        
        cols = width // (self.hex_size * 1.5) + 2
        rows = height // (self.hex_size * 0.866) + 2
        
        for col in range(int(cols)):
            for row in range(int(rows)):
                x = col * self.hex_size * 1.5
                y = (row * self.hex_size * 0.866) + (col % 2) * self.hex_size * 0.433
                if random.random() < 0.3:
                    self.active_hexagons.append({
                        'x': x,
                        'y': y,
                        'alpha': random.randint(10, 40),
                        'pulse': random.random()
                    })
        
        self.connections = []
        for i in range(len(self.active_hexagons)):
            if random.random() < 0.2:
                j = random.randint(0, len(self.active_hexagons)-1)
                if i != j:
                    self.connections.append((i, j))
    
    def update_grid(self):
        self.offset_x = (self.offset_x + 0.5) % (self.hex_size * 1.5)
        self.offset_y = (self.offset_y + 0.2) % (self.hex_size * 0.866)
        
        for hexagon in self.active_hexagons:
            hexagon['pulse'] = (hexagon['pulse'] + 0.01) % 1.0
        
        self.update()
    
    def resizeEvent(self, event):
        self.generate_hexagons()
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for i, j in self.connections:
            hex1 = self.active_hexagons[i]
            hex2 = self.active_hexagons[j]
            
            x1 = hex1['x'] - self.offset_x
            y1 = hex1['y'] - self.offset_y
            x2 = hex2['x'] - self.offset_x
            y2 = hex2['y'] - self.offset_y
            
            if x1 < -self.hex_size: x1 += (self.width() // (self.hex_size * 1.5) + 1) * self.hex_size * 1.5
            if x2 < -self.hex_size: x2 += (self.width() // (self.hex_size * 1.5) + 1) * self.hex_size * 1.5
            if y1 < -self.hex_size: y1 += (self.height() // (self.hex_size * 0.866) + 1) * self.hex_size * 0.866
            if y2 < -self.hex_size: y2 += (self.height() // (self.hex_size * 0.866) + 1) * self.hex_size * 0.866
            
            if (0 <= x1 <= self.width() or 0 <= x2 <= self.width()) and \
               (0 <= y1 <= self.height() or 0 <= y2 <= self.height()):
                alpha = min(hex1['alpha'], hex2['alpha']) * (0.5 + 0.5 * abs(hex1['pulse'] - hex2['pulse']))
                
                pen = QPen(QColor(0, 255, 255, int(alpha)))
                pen.setWidthF(1.5)
                painter.setPen(pen)
                painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        for hexagon in self.active_hexagons:
            x = hexagon['x'] - self.offset_x
            y = hexagon['y'] - self.offset_y
            
            if x < -self.hex_size: x += (self.width() // (self.hex_size * 1.5) + 1) * self.hex_size * 1.5
            if y < -self.hex_size: y += (self.height() // (self.hex_size * 0.866) + 1) * self.hex_size * 0.866
            
            if 0 <= x <= self.width() and 0 <= y <= self.height():
                path = QPainterPath()
                size = self.hex_size * (0.8 + 0.2 * hexagon['pulse'])
                
                for i in range(6):
                    angle_deg = 60 * i - 30
                    angle_rad = angle_deg * (math.pi / 180)
                    x_i = x + size * math.cos(angle_rad)
                    y_i = y + size * math.sin(angle_rad)
                    
                    if i == 0:
                        path.moveTo(x_i, y_i)
                    else:
                        path.lineTo(x_i, y_i)
                
                path.closeSubpath()
                
                painter.setPen(QPen(QColor(0, 255, 255, hexagon['alpha']), 1))
                painter.setBrush(QColor(0, 255, 255, hexagon['alpha'] // 3))
                painter.drawPath(path)

class MatrixRain(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.chars = " "
        self.columns = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rain)
        self.timer.start(50)
        
        self.font = QFont("Courier New", 12)
        self.font.setBold(True)
        
        self.init_columns()
    
    def init_columns(self):
        self.columns = []
        col_width = 20
        num_cols = self.width() // col_width + 1
        
        for i in range(num_cols):
            col_length = random.randint(5, 30)
            speed = random.uniform(1.0, 3.0)
            start_delay = random.randint(0, 50)
            brightness = random.uniform(0.3, 1.0)
            
            self.columns.append({
                'x': i * col_width,
                'drops': [{
                    'y': random.randint(-1000, 0),
                    'char': random.choice(self.chars),
                    'brightness': max(0, brightness - (j * (1.0 / col_length))),
                    'speed': speed
                } for j in range(col_length)],
                'speed': speed,
                'delay': start_delay,
                'counter': 0
            })
    
    def update_rain(self):
        for col in self.columns:
            col['counter'] += 1
            if col['counter'] >= col['delay']:
                for drop in col['drops']:
                    drop['y'] += drop['speed']
                    if random.random() < 0.05:
                        drop['char'] = random.choice(self.chars)
                
                if col['drops'][0]['y'] > self.height():
                    col['drops'].pop(0)
                    col['drops'].append({
                        'y': -20,
                        'char': random.choice(self.chars),
                        'brightness': col['drops'][-1]['brightness'] if col['drops'] else 1.0,
                        'speed': col['speed']
                    })
        
        self.update()
    
    def resizeEvent(self, event):
        self.init_columns()
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font)
        
        for col in self.columns:
            if col['counter'] >= col['delay']:
                for i, drop in enumerate(col['drops']):
                    alpha = int(255 * drop['brightness'])
                    color = QColor(0, 255, 0, alpha) if i == len(col['drops']) - 1 else QColor(100, 255, 100, alpha)
                    painter.setPen(color)
                    painter.drawText(int(col['x']), int(drop['y']), drop['char'])

class CyberParticles(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)
        
        self.init_particles()
    
    def init_particles(self):
        self.particles = []
        for _ in range(10):
            self.particles.append({
                'x': random.randint(0, self.width()),
                'y': random.randint(0, self.height()),
                'vx': random.uniform(-1.5, 1.5),
                'vy': random.uniform(-1.5, 1.5),
                'size': random.randint(2, 8),
                'alpha': random.randint(30, 180),
                'color': random.choice([
                    QColor(0, 255, 255),
                    QColor(255, 0, 255),
                    QColor(255, 255, 0),
                    QColor(0, 255, 0)
                ]),
                'trail': [(0, 0)] * random.randint(3, 10)
            })
    
    def update_particles(self):
        for p in self.particles:
            p['trail'].pop(0)
            p['trail'].append((p['x'], p['y']))
            
            p['x'] += p['vx']
            p['y'] += p['vy']
            
            if p['x'] < 0 or p['x'] > self.width():
                p['vx'] = -p['vx']
                p['x'] = max(0, min(self.width(), p['x']))
            if p['y'] < 0 or p['y'] > self.height():
                p['vy'] = -p['vy']
                p['y'] = max(0, min(self.height(), p['y']))
        
        self.update()
    
    def resizeEvent(self, event):
        self.init_particles()
        super().resizeEvent(event)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for p in self.particles:
            for i, (tx, ty) in enumerate(p['trail']):
                if i > 0:
                    alpha = int(p['alpha'] * (i / len(p['trail'])))
                    trail_color = QColor(p['color'])
                    trail_color.setAlpha(alpha // 2)
                    painter.setPen(QPen(trail_color, 1))
                    prev_x, prev_y = p['trail'][i-1]
                    painter.drawLine(int(tx), int(ty), int(prev_x), int(prev_y))
            
            particle_color = QColor(p['color'])
            particle_color.setAlpha(p['alpha'])
            painter.setPen(Qt.NoPen)
            painter.setBrush(particle_color)
            painter.drawEllipse(int(p['x']), int(p['y']), p['size'], p['size'])

class CRTFilter(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.scanline_pos = 0
        self.noise_opacity = 0.05
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_filter)
        self.timer.start(16)
    
    def update_filter(self):
        self.scanline_pos = (self.scanline_pos + 2) % 12
        self.noise_opacity = 0.03 + 0.02 * random.random()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        for y in range(self.scanline_pos, self.height(), 4):
            alpha = 20 if y % 8 == self.scanline_pos % 8 else 10
            painter.setPen(QColor(0, 0, 0, alpha))
            painter.drawLine(0, y, self.width(), y)
        
        painter.setPen(Qt.NoPen)
        for _ in range(100):
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            size = random.randint(1, 3)
            alpha = random.randint(0, 50)
            painter.setBrush(QColor(255, 255, 255, alpha))
            painter.drawEllipse(x, y, size, size)

class CyberButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(300, 80)
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(20, 25, 40, 180);
                color: #00FFFF;
                border: 3px solid #00FFFF;
                border-radius: 10px;
                font-size: 24px;
                font-family: 'Orbitron', 'Courier New', monospace;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(40, 50, 80, 200);
                border: 3px solid #FF00FF;
                color: #FF00FF;
            }
            QPushButton:pressed {
                background-color: rgba(60, 70, 100, 220);
                border: 3px solid #00FF00;
                color: #00FF00;
            }
        """)
        
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setColor(QColor(0, 255, 255))
        self.glow.setBlurRadius(20)
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
        self.glow_anim = QPropertyAnimation(self.glow, b"blurRadius")
        self.glow_anim.setDuration(1500)
        self.glow_anim.setLoopCount(-1)
        self.glow_anim.setEasingCurve(QEasingCurve.InOutSine)
        self.glow_anim.setStartValue(15)
        self.glow_anim.setEndValue(30)
        self.glow_anim.start()
        
        self.color_anim = QPropertyAnimation(self.glow, b"color")
        self.color_anim.setDuration(2000)
        self.color_anim.setLoopCount(-1)
        self.color_anim.setKeyValueAt(0.0, QColor(0, 255, 255))
        self.color_anim.setKeyValueAt(0.5, QColor(255, 0, 255))
        self.color_anim.setKeyValueAt(1.0, QColor(0, 255, 255))
        self.color_anim.start()

class WelcomeScreen(QWidget):
    def __init__(self, enter_callback):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.enter_callback = enter_callback
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("background-color: black;")
        
        self.hex_grid = HexagonGrid(self)
        self.matrix_rain = MatrixRain(self)
        self.particles = CyberParticles(self)
        self.crt_filter = CRTFilter(self)
        
        self.content = QWidget(self)
        self.content.setStyleSheet("background: transparent;")
        
        main_layout = QVBoxLayout(self.content)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title = QLabel("ShadowPasser")
        self.title.setStyleSheet("""
            color: #00FFFF;
            font-size: 72px;
            font-weight: bold;
            font-family: 'Orbitron', 'Courier New', monospace;
            background: transparent;
        """)
        
        title_glow = QGraphicsDropShadowEffect()
        title_glow.setColor(QColor(0, 255, 255))
        title_glow.setBlurRadius(30)
        title_glow.setOffset(0, 0)
        self.title.setGraphicsEffect(title_glow)
        self.title.setAlignment(Qt.AlignCenter)
        
        self.subtitle = QLabel("Developed by Team ShadowCryptics")
        self.subtitle.setStyleSheet("""
            color: limegreen;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Orbitron', 'Courier New', monospace;
            padding: 10px;
            background: transparent;
        """)
        subtitle_glow = QGraphicsDropShadowEffect()
        subtitle_glow.setColor(QColor(0, 183, 235))
        subtitle_glow.setBlurRadius(15)
        subtitle_glow.setOffset(0, 0)
        self.subtitle.setGraphicsEffect(subtitle_glow)
        self.subtitle.setAlignment(Qt.AlignCenter)
        
        self.enter_button = CyberButton("ENTER", self)
        self.enter_button.clicked.connect(self.enter_callback)
        
        main_layout.addStretch()
        main_layout.addWidget(self.title)
        main_layout.addWidget(self.subtitle)
        main_layout.addSpacing(40)
        main_layout.addWidget(self.enter_button, 0, Qt.AlignCenter)
        main_layout.addStretch()
        
        self.setup_animations()
        self.content.show()
    
    def setup_animations(self):
        self.title_glitch = QPropertyAnimation(self.title, b"pos")
        self.title_glitch.setDuration(100)
        self.title_glitch.setLoopCount(-1)
        self.title_glitch.setKeyValueAt(0.0, QPoint(0, 0))
        self.title_glitch.setKeyValueAt(0.1, QPoint(2, 0))
        self.title_glitch.setKeyValueAt(0.3, QPoint(-2, 0))
        self.title_glitch.setKeyValueAt(0.5, QPoint(0, 0))
        self.title_glitch.setKeyValueAt(0.7, QPoint(0, 2))
        self.title_glitch.setKeyValueAt(0.9, QPoint(0, -2))
        
        self.subtitle_flicker = QPropertyAnimation(self.subtitle, b"windowOpacity")
        self.subtitle_flicker.setDuration(300)
        self.subtitle_flicker.setLoopCount(-1)
        self.subtitle_flicker.setKeyValueAt(0.0, 1.0)
        self.subtitle_flicker.setKeyValueAt(0.1, 0.9)
        self.subtitle_flicker.setKeyValueAt(0.2, 1.0)
        self.subtitle_flicker.setKeyValueAt(0.8, 0.95)
        self.subtitle_flicker.start()
    
    def resizeEvent(self, event):
        self.hex_grid.resize(event.size())
        #self.matrix_rain.resize(event.size())
        self.particles.resize(event.size())
        self.crt_filter.resize(event.size())
        self.content.resize(event.size())
        super().resizeEvent(event)

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ShadowPasser")
        self.setStyleSheet("QMainWindow { background-color: #1e1e1e; }")
        self.setWindowIcon(create_cyan_icon())

        self.welcome_screen = WelcomeScreen(self.show_main_interface)
        self.setCentralWidget(self.welcome_screen)

    def show_main_interface(self):
        self.profile = QWebEngineProfile()
        self.profile.setHttpUserAgent(CHROME_USER_AGENT.decode())

        interceptor = UrlRequestInterceptor()
        self.profile.setUrlRequestInterceptor(interceptor)

        self.web_view = QWebEngineView()
        self.page = WebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.page)
        self.web_view.loadFinished.connect(self.inject_block_script)

        nav_bar = QWidget()
        nav_bar.setFixedHeight(40)
        nav_bar.setStyleSheet("QWidget { background-color: #252526; }")

        back = QPushButton()
        back.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))
        back.clicked.connect(self.web_view.back)

        forward = QPushButton()
        forward.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))
        forward.clicked.connect(self.web_view.forward)

        reload = QPushButton()
        reload.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        reload.clicked.connect(self.web_view.reload)

        for btn in [back, forward, reload]:
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    border: none; border-radius: 16px;
                    background-color: #252526; color: white;
                }
                QPushButton:hover { background-color: #3c3c3c; }
                QPushButton:pressed { background-color: #505050; }
            """)

        label = QLabel("      ShadowPasser v1.0.0  |  Developed by Team ShadowCryptics")
        label.setStyleSheet("color: cyan; font-weight: bold;")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout = QHBoxLayout()
        layout.addWidget(back)
        layout.addWidget(forward)
        layout.addWidget(reload)
        layout.addWidget(label)
        layout.addStretch()
        nav_bar.setLayout(layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(nav_bar)
        main_layout.addWidget(self.web_view)
        container = QWidget()
        container.setLayout(main_layout)

        self.setCentralWidget(container)
        self.web_view.setUrl(QUrl("https://rmk685.examly.io/"))

    def inject_block_script(self):
        js_code = f"""
            const domain = "{BASE_DOMAIN}";
            const pathPrefix = "{BLOCK_PATH_PREFIX}";
            const allowedDomain = "{ALLOWED_DOMAIN}";

            const fake403 = new Response("403 Forbidden", {{
                status: 403,
                statusText: "Forbidden",
                headers: {{ "Content-Type": "text/plain" }}
            }});

            const fake200 = new Response(JSON.stringify({{status: "success"}}), {{
                status: 200,
                statusText: "OK",
                headers: {{ "Content-Type": "application/json" }}
            }});

            const originalFetch = window.fetch;
            window.fetch = function(input, init) {{
                const url = typeof input === 'string' ? input : input.url;
                if (url.includes(allowedDomain)) {{
                    console.warn("[JS Allowed fetch] " + url);
                    return Promise.resolve(fake200.clone());
                }}
                if (url.includes(domain) && new URL(url).pathname.startsWith(pathPrefix)) {{
                    console.warn("[JS Blocked fetch] " + url);
                    return Promise.resolve(fake403.clone());
                }}
                return originalFetch(input, init);
            }};

            const originalXHROpen = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function(method, url) {{
                if (url.includes(allowedDomain)) {{
                    console.warn("[JS Allowed XHR] " + url);
                    this.send = function() {{
                        this.readyState = 4;
                        this.status = 200;
                        this.statusText = "OK";
                        this.responseText = JSON.stringify({{status: "success"}});
                        this.onreadystatechange && this.onreadystatechange();
                        this.onload && this.onload();
                    }};
                    return;
                }}
                if (url.includes(domain) && new URL(url).pathname.startsWith(pathPrefix)) {{
                    console.warn("[JS Blocked XHR] " + url);
                    this.send = function() {{
                        this.readyState = 4;
                        this.status = 403;
                        this.statusText = "Forbidden";
                        this.responseText = "403 Forbidden";
                        this.onreadystatechange && this.onreadystatechange();
                        this.onload && this.onload();
                    }};
                    return;
                }}
                return originalXHROpen.apply(this, arguments);
            }};

            // Enhanced paste restriction bypass
            (function() {{
                // Function to remove paste restrictions
                function enablePaste() {{
                    const elements = document.querySelectorAll('input, textarea');
                    elements.forEach(el => {{
                        el.onpaste = null; // Remove onpaste handlers
                        el.removeAttribute('onpaste');
                        // Add paste event listener to allow pasting
                        el.addEventListener('paste', (e) => {{
                            e.stopImmediatePropagation(); // Prevent other listeners from blocking
                            console.log('[Paste Enabled] Paste event allowed on:', e.target);
                        }}, true);
                    }});
                }}

                // Run initially
                enablePaste();

                // Override addEventListener to block paste event listeners
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {{
                    if (type === 'paste') {{
                        console.log('[Blocked] Attempt to add paste event listener blocked');
                        return;
                    }}
                    return originalAddEventListener.apply(this, arguments);
                }};

                // Use MutationObserver to handle dynamically added elements
                const observer = new MutationObserver((mutations) => {{
                    mutations.forEach((mutation) => {{
                        if (mutation.addedNodes.length) {{
                            mutation.addedNodes.forEach((node) => {{
                                if (node.nodeType === 1) {{ // Element nodes only
                                    if (node.matches('input, textarea')) {{
                                        node.onpaste = null;
                                        node.removeAttribute('onpaste');
                                        node.addEventListener('paste', (e) => {{
                                            e.stopImmediatePropagation();
                                            console.log('[Paste Enabled] Paste event allowed on dynamically added:', e.target);
                                        }}, true);
                                    }}
                                    // Check for nested inputs or textareas
                                    node.querySelectorAll('input, textarea').forEach((el) => {{
                                        el.onpaste = null;
                                        el.removeAttribute('onpaste');
                                        el.addEventListener('paste', (e) => {{
                                            e.stopImmediatePropagation();
                                            console.log('[Paste Enabled] Paste event allowed on nested:', e.target);
                                        }}, true);
                                    }});
                                }}
                            }});
                        }}
                    }});
                }});

                // Observe DOM changes
                observer.observe(document.body, {{
                    childList: true,
                    subtree: true
                }});

                // Periodically re-apply paste enabling (every 1 second)
                setInterval(enablePaste, 1000);

                // Log when script runs
                console.log('[Paste Bypass] Paste restriction bypass script initialized');
            }})();
        """
        self.web_view.page().runJavaScript(js_code)

def main():
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = '--enable-media-stream --use-fake-ui-for-media-stream'
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font_db = QFontDatabase()
    if "Orbitron" not in [fam for fam in font_db.families()]:
        orbitron_path = os.path.join(os.path.dirname(__file__), "Orbitron-Regular.ttf")
        if os.path.exists(orbitron_path):
            font_db.addApplicationFont(orbitron_path)

    palette = app.palette()
    palette.setColor(palette.Window, Qt.black)
    palette.setColor(palette.WindowText, Qt.white)
    palette.setColor(palette.Base, Qt.darkGray)
    palette.setColor(palette.Text, Qt.white)
    palette.setColor(palette.Button, Qt.darkGray)
    palette.setColor(palette.ButtonText, Qt.white)
    app.setPalette(palette)

    window = BrowserWindow()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()