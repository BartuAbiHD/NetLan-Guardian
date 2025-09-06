"""
DPI Bypass GUI - NetLan Guardian
Ana merkez platform butonları ve ayrı ayarlar sayfası ile
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import sys
import os
from pathlib import Path
import pystray
from PIL import Image, ImageDraw

# Parent dizini path'e ekle
sys.path.append(str(Path(__file__).parent.parent))
from dpi_bypass import DPIBypass
from config_manager import ConfigManager
from updater import UpdateManager, get_current_version

class UltraModernDPIGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌐 NetLan Guardian")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)  # Daha küçük minimum boyut
        self.root.configure(bg='#0F0F0F')
        
        # Responsive variables
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.current_width = 1200
        self.current_height = 800
        
        # Bind resize event
        self.root.bind('<Configure>', self.on_window_resize)
        
        # Modern 2025 renk paleti
        self.colors = {
            'bg_primary': '#0F0F0F',        # Çok koyu siyah
            'bg_secondary': '#1A1A1A',      # Koyu gri
            'bg_tertiary': '#2D2D2D',       # Orta gri
            'accent_primary': '#00D9FF',     # Neon mavi
            'accent_secondary': '#FF6B6B',   # Neon kırmızı
            'accent_success': '#4ECDC4',     # Neon yeşil
            'accent_warning': '#FFE66D',     # Neon sarı
            'text_primary': '#FFFFFF',       # Beyaz
            'text_secondary': '#B0B0B0',     # Açık gri
            'text_muted': '#666666',         # Koyu gri
            'border': '#333333',             # Kenarlık
            'hover': '#404040'               # Hover rengi
        }
        
        # Uygulama durumu
        self.bypass_active = False
        self.current_page = "main"
        
        # İndirme durumu
        self.download_dialog = None
        self.download_progress_var = None
        self.download_status_var = None
        self.progress_percent_var = None
        
        # System tray desteği
        self.tray_icon = None
        self.in_tray = False
        
        # Config manager ve DPI bypass
        self.config_manager = ConfigManager()
        self.dpi_bypass = DPIBypass(self.config_manager)
        
        # Güncelleme yöneticisi
        self.current_version = get_current_version()
        self.update_manager = UpdateManager(self.current_version)
        
        # Platform verileri - genişletilmiş (çoklu domain destekli)
        self.platforms = {
            'Discord': {
                'icon': '🎮', 
                'domains': ['discord.com', 'discordapp.com', 'discord.gg', 'cdn.discordapp.com'], 
                'color': '#7289DA', 
                'category': 'social'
            },
            'YouTube': {
                'icon': '📺', 
                'domains': [
                    'youtube.com', 'youtu.be', 'googlevideo.com', 'youtubei.googleapis.com', 
                    'ytimg.com', 'yt3.ggpht.com', 'yt4.ggpht.com', 'youtubeembeddedplayer.googleapis.com',
                    'ytimg.l.google.com', 'jnn-pa.googleapis.com', 'youtube-nocookie.com',
                    'youtube-ui.l.google.com', 'yt-video-upload.l.google.com', 'wide-youtube.l.google.com'
                ], 
                'color': '#FF0000', 
                'category': 'media'
            },
            'Netflix': {
                'icon': '🎬', 
                'domains': ['netflix.com', 'nflxext.com', 'nflximg.net', 'nflxso.net', 'nflxvideo.net'], 
                'color': '#E50914', 
                'category': 'media'
            },
            'Spotify': {
                'icon': '🎵', 
                'domains': ['spotify.com', 'scdn.co', 'spoti.fi', 'spotifycdn.com'], 
                'color': '#1DB954', 
                'category': 'media'
            },
            'Twitch': {
                'icon': '🟣', 
                'domains': ['twitch.tv', 'twitchcdn.net', 'jtvnw.net', 'ttvnw.net'], 
                'color': '#9146FF', 
                'category': 'media'
            },
            'Kick': {
                'icon': '⚡', 
                'domains': ['kick.com', 'kick.stream', 'cdn.kick.com', 'assets.kick.com', 'live-video.net', 'global-contribute.live-video.net'], 
                'color': '#53FC18', 
                'category': 'media'
            },
            'Instagram': {
                'icon': '📷', 
                'domains': ['instagram.com', 'cdninstagram.com', 'instagramstatic-a.akamaihd.net'], 
                'color': '#E4405F', 
                'category': 'social'
            },
            'Facebook': {
                'icon': '📘', 
                'domains': ['facebook.com', 'fb.com', 'fbcdn.net', 'fbsbx.com'], 
                'color': '#1877F2', 
                'category': 'social'
            },
            'Twitter/X': {
                'icon': '🐦', 
                'domains': ['twitter.com', 'x.com', 't.co', 'twimg.com', 'twitter.co'], 
                'color': '#1DA1F2', 
                'category': 'social'
            },
            'TikTok': {
                'icon': '🎭', 
                'domains': ['tiktok.com', 'tiktokcdn.com', 'tiktokv.com', 'muscdn.com', 'musical.ly'], 
                'color': '#FE2C55', 
                'category': 'social'
            },
            'GitHub': {
                'icon': '💻', 
                'domains': ['github.com', 'githubusercontent.com', 'githubassets.com', 'github.io'], 
                'color': '#333333', 
                'category': 'dev'
            },
            'Steam': {
                'icon': '🎮', 
                'domains': ['steampowered.com', 'steamcommunity.com', 'steamstatic.com', 'steamcdn-a.akamaihd.net'], 
                'color': '#1B2838', 
                'category': 'gaming'
            },
            'Roblox': {
                'icon': '🎲', 
                'domains': ['roblox.com', 'rbxcdn.com', 'rbxbxcdn.com', 'rbximg.com'], 
                'color': '#00A2FF', 
                'category': 'gaming'
            },
            'Epic Games': {
                'icon': '🚀', 
                'domains': ['epicgames.com', 'unrealengine.com', 'fortnite.com', 'epicgames.dev'], 
                'color': '#313131', 
                'category': 'gaming'
            },
            'PlayStation': {
                'icon': '🎮', 
                'domains': ['playstation.com', 'sonyentertainmentnetwork.com', 'psn.com', 'playstation.net'], 
                'color': '#003791', 
                'category': 'gaming'
            },
            'Xbox Live': {
                'icon': '🎮', 
                'domains': ['xbox.com', 'xboxlive.com', 'live.com', 'microsoft.com'], 
                'color': '#107C10', 
                'category': 'gaming'
            },
            'Pastebin': {
                'icon': '📝', 
                'domains': ['pastebin.com', 'pastebin.pl', 'paste.org'], 
                'color': '#02A9F1', 
                'category': 'tools'
            },
        }
        
        self.setup_modern_styles()
        self.create_navigation()
        self.create_main_page()
        self.load_initial_config()  # Sadece kritik ayarları yükle
        
        # İlk açılışta window boyutunu güncelle ve responsive elementleri ayarla
        self.root.update_idletasks()  # Widget'ların render edilmesini bekle
        self.current_width = self.root.winfo_width()
        self.current_height = self.root.winfo_height()
        
        # Responsive elementleri ayarla
        self.adjust_responsive_elements()
        
        # Platform displayini de güncelle - biraz gecikmeyle
        self.root.after(100, self.update_platform_display)
        
        # Program tam başlatıldıktan sonra tray ayarını kontrol et
        self.root.after(200, self.check_and_setup_tray)
        
        # Kapatma protokolünü ayarla (güvenlik için erken ayarla)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def check_and_setup_tray(self):
        """Program tam yüklendikten sonra tray ayarını kontrol et"""
        minimize_to_tray = self.config_manager.get_setting('minimize_to_tray', False)
        if minimize_to_tray and not self.tray_icon:
            # Tray değişkenini oluştur ve ayarla (eğer yoksa)
            if not hasattr(self, 'minimize_to_tray'):
                self.minimize_to_tray = tk.BooleanVar(value=True)
            else:
                self.minimize_to_tray.set(True)
                
            # Tray'i kurulumla
            self.setup_tray()
            # Tray icon'u background thread'de başlat
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()

    def on_window_resize(self, event):
        """Window resize olayını handle et"""
        if event.widget == self.root:
            self.current_width = self.root.winfo_width()
            self.current_height = self.root.winfo_height()
            self.adjust_responsive_elements()
    
    def get_responsive_font_size(self, base_size):
        """Ekran boyutuna göre responsive font size hesapla"""
        scale_factor = min(self.current_width / 1200, self.current_height / 800)
        # Minimum ve maksimum font boyutları belirle
        min_size = max(8, int(base_size * 0.7))
        max_size = int(base_size * 1.2)
        responsive_size = max(min_size, min(max_size, int(base_size * scale_factor)))
        return responsive_size
    
    def get_responsive_padding(self, base_padding):
        """Ekran boyutuna göre responsive padding hesapla"""
        scale_factor = min(self.current_width / 1200, self.current_height / 800)
        return max(5, int(base_padding * scale_factor))
    
    def adjust_responsive_elements(self):
        """Responsive elementleri yeniden ayarla"""
        try:
            # Font boyutlarını güncelle
            if hasattr(self, 'welcome_title'):
                new_font_size = self.get_responsive_font_size(28)
                self.welcome_title.configure(font=('Segoe UI', new_font_size, 'bold'))
            
            if hasattr(self, 'welcome_subtitle'):
                new_font_size = self.get_responsive_font_size(14)
                self.welcome_subtitle.configure(font=('Segoe UI', new_font_size))
            
            # Platform displayını güncelle
            if hasattr(self, 'platform_container') and hasattr(self, 'selected_category'):
                self.update_platform_display()
            
            # Control panel'i yeniden oluştur eğer gerekirse
            if hasattr(self, 'main_frame') and self.current_page == 'main':
                # Control paneli responsive olarak yeniden ayarla
                self.recreate_control_panel()
                
        except Exception as e:
            pass  # Resize sırasında hataları görmezden gel
    
    def recreate_control_panel(self):
        """Control panelini yeniden oluştur"""
        try:
            # Mevcut control panel'i bul ve sil
            for child in self.main_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    # Alt kısımda pack edilmiş frame'leri kontrol et
                    if hasattr(child, 'winfo_manager') and child.winfo_manager() == 'pack':
                        pack_info = child.pack_info()
                        if pack_info.get('side') == 'bottom':
                            child.destroy()
                            self.create_control_panel()
                            return
        except Exception as e:
            pass
        
    def setup_modern_styles(self):
        """2025 tarzı ultra modern stiller"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ultra modern buton stilleri
        style.configure('UltraModern.TButton',
                       background=self.colors['bg_tertiary'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat')
        
        style.map('UltraModern.TButton',
                 background=[('active', self.colors['hover']),
                           ('pressed', self.colors['bg_secondary'])])
        
        # Neon aksan butonları
        style.configure('Accent.TButton',
                       background=self.colors['accent_primary'],
                       foreground=self.colors['bg_primary'],
                       font=('Segoe UI', 12, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
    def create_navigation(self):
        """Modern navigasyon çubuğu - Responsive"""
        # Responsive nav height
        nav_height = max(50, self.get_responsive_padding(60))
        
        nav_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=nav_height)
        nav_frame.pack(fill='x', side='top')
        nav_frame.pack_propagate(False)
        
        # Logo ve başlık
        logo_frame = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        logo_frame.pack(side='left', fill='y', padx=self.get_responsive_padding(20))
        
        title_font_size = self.get_responsive_font_size(16)
        title = tk.Label(logo_frame, 
                        text="🌐 NETLAN GUARDIAN",
                        font=('Segoe UI', title_font_size, 'bold'),
                        bg=self.colors['bg_secondary'],
                        fg=self.colors['accent_primary'])
        title.pack(side='top', pady=self.get_responsive_padding(8))
        
        # Navigasyon butonları
        nav_buttons_frame = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        nav_buttons_frame.pack(side='right', fill='y', padx=self.get_responsive_padding(20))
        
        button_font_size = self.get_responsive_font_size(10)
        button_padding = self.get_responsive_padding(15)
        
        # Ana sayfa butonu - referans olarak sakla
        self.main_btn = tk.Button(nav_buttons_frame,
                            text="🏠 Ana Sayfa",
                            font=('Segoe UI', button_font_size, 'bold'),
                            bg=self.colors['accent_primary'] if self.current_page == 'main' else self.colors['bg_tertiary'],
                            fg=self.colors['bg_primary'] if self.current_page == 'main' else self.colors['text_primary'],
                            activebackground=self.colors['accent_primary'],
                            relief='flat',
                            cursor='hand2',
                            command=lambda: self.switch_page('main'))
        self.main_btn.pack(side='left', padx=10, pady=button_padding, ipadx=15)
        
        # Ayarlar butonu - referans olarak sakla
        self.settings_btn = tk.Button(nav_buttons_frame,
                               text="⚙️ Ayarlar",
                               font=('Segoe UI', button_font_size, 'bold'),
                               bg=self.colors['accent_primary'] if self.current_page == 'settings' else self.colors['bg_tertiary'],
                               fg=self.colors['bg_primary'] if self.current_page == 'settings' else self.colors['text_primary'],
                               activebackground=self.colors['accent_primary'],
                               relief='flat',
                               cursor='hand2',
                               command=lambda: self.switch_page('settings'))
        self.settings_btn.pack(side='left', padx=5, pady=button_padding, ipadx=15)
        
        # Durum göstergesi
        self.status_frame = tk.Frame(nav_frame, bg=self.colors['bg_secondary'])
        self.status_frame.pack(side='right', fill='y', padx=self.get_responsive_padding(20))
        
        indicator_font_size = self.get_responsive_font_size(16)
        status_font_size = self.get_responsive_font_size(10)
        
        self.status_indicator = tk.Label(self.status_frame,
                                       text="●",
                                       font=('Segoe UI', indicator_font_size),
                                       bg=self.colors['bg_secondary'],
                                       fg=self.colors['accent_secondary'])
        self.status_indicator.pack(side='left', pady=18, padx=(0, 8))
        
        self.status_text = tk.Label(self.status_frame,
                                  text="Devre Dışı",
                                  font=('Segoe UI', status_font_size, 'bold'),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_secondary'])
        self.status_text.pack(side='left', pady=18)
        
    def create_main_page(self):
        """Ana sayfa - Merkez platform butonları - Responsive"""
        self.main_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_frame.page_type = 'content'  # Sayfa tipi işaretle
        self.main_frame.pack(fill='both', expand=True)
        
        # Hoş geldiniz metni - Kompakt
        welcome_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        welcome_frame.pack(fill='x', pady=self.get_responsive_padding(15))  # Daha az padding
        
        title_font_size = self.get_responsive_font_size(20)  # Daha küçük başlık
        subtitle_font_size = self.get_responsive_font_size(11)
        
        self.welcome_title = tk.Label(welcome_frame,
                               text="Platform Seçimi",
                               font=('Segoe UI', title_font_size, 'bold'),
                               bg=self.colors['bg_primary'],
                               fg=self.colors['text_primary'])
        self.welcome_title.pack()
        
        self.welcome_subtitle = tk.Label(welcome_frame,
                                  text="Bypass etmek istediğiniz platformu seçin",
                                  font=('Segoe UI', subtitle_font_size),
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_secondary'])
        self.welcome_subtitle.pack(pady=(3, self.get_responsive_padding(10)))
        
        # Platform kategorileri - Kompakt
        categories = {
            'social': '👥 Sosyal',
            'media': '🎬 Medya', 
            'gaming': '🎮 Oyun',
            'dev': '💻 Dev',
            'tools': '🛠️ Araçlar'
        }
        
        # Kategoriler için kompakt tab sistemi
        self.category_frame = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.category_frame.pack(fill='x', padx=self.get_responsive_padding(15), pady=5)
        
        self.selected_category = tk.StringVar(value='social')
        
        # Responsive kategori butonları
        self.create_responsive_category_buttons(categories)
        
        # Platform butonları için normal frame (scrollbar yok)
        self.platform_container = tk.Frame(self.main_frame, bg=self.colors['bg_primary'])
        self.platform_container.pack(fill='both', expand=True, 
                                   padx=self.get_responsive_padding(15), 
                                   pady=self.get_responsive_padding(8))
        
        # Alt kontrol paneli (fixed position)
        self.create_control_panel()
    
    def create_responsive_category_buttons(self, categories):
        """Responsive kategori butonları oluştur - Daha kompakt"""
        # Mevcut butonları temizle
        for widget in self.category_frame.winfo_children():
            widget.destroy()
        
        cat_font_size = self.get_responsive_font_size(10)  # Daha küçük font
        
        # Çok küçük ekranlarda dropdown, büyük ekranlarda butonlar
        if self.current_width < 600:
            # Dropdown menü kullan
            self.create_category_dropdown(categories)
        elif self.current_width < 900:
            # Kompakt butonlar - üç satıra böl
            self.create_compact_category_buttons(categories, cat_font_size)
        else:
            # Normal butonlar - tek satırda
            self.create_normal_category_buttons(categories, cat_font_size)
    
    def create_category_dropdown(self, categories):
        """Çok küçük ekranlar için dropdown kategori seçici"""
        dropdown_frame = tk.Frame(self.category_frame, bg=self.colors['bg_primary'])
        dropdown_frame.pack(fill='x', pady=5)
        
        tk.Label(dropdown_frame,
                text="Kategori:",
                font=('Segoe UI', self.get_responsive_font_size(10), 'bold'),
                bg=self.colors['bg_primary'],
                fg=self.colors['text_primary']).pack(side='left', padx=(0, 10))
        
        # Combobox için değerleri hazırla
        category_values = list(categories.values())
        category_keys = list(categories.keys())
        
        self.category_combo = ttk.Combobox(dropdown_frame,
                                         values=category_values,
                                         state='readonly',
                                         font=('Segoe UI', self.get_responsive_font_size(9)))
        self.category_combo.pack(side='left', fill='x', expand=True)
        
        # İlk değeri seç
        current_key = self.selected_category.get()
        if current_key in category_keys:
            index = category_keys.index(current_key)
            self.category_combo.set(category_values[index])
        
        # Seçim değiştiğinde callback
        def on_category_change(event):
            selected_text = self.category_combo.get()
            if selected_text in category_values:
                index = category_values.index(selected_text)
                selected_key = category_keys[index]
                self.selected_category.set(selected_key)
                self.update_platform_display()
        
        self.category_combo.bind('<<ComboboxSelected>>', on_category_change)
    
    def create_compact_category_buttons(self, categories, font_size):
        """Kompakt kategori butonları - çoklu satır"""
        category_items = list(categories.items())
        items_per_row = 3 if self.current_width < 700 else 2
        
        rows_needed = (len(category_items) + items_per_row - 1) // items_per_row
        
        for row in range(rows_needed):
            row_frame = tk.Frame(self.category_frame, bg=self.colors['bg_primary'])
            row_frame.pack(fill='x', pady=2)
            
            start_idx = row * items_per_row
            end_idx = min(start_idx + items_per_row, len(category_items))
            
            for i in range(start_idx, end_idx):
                cat_key, cat_name = category_items[i]
                cat_btn = tk.Radiobutton(row_frame,
                                       text=cat_name,
                                       variable=self.selected_category,
                                       value=cat_key,
                                       font=('Segoe UI', font_size, 'bold'),
                                       bg=self.colors['bg_primary'],
                                       fg=self.colors['text_primary'],
                                       activebackground=self.colors['bg_primary'],
                                       activeforeground=self.colors['accent_primary'],
                                       selectcolor=self.colors['accent_primary'],
                                       command=self.update_platform_display)
                cat_btn.pack(side='left', padx=5, pady=2, expand=True)
    
    def create_normal_category_buttons(self, categories, font_size):
        """Normal kategori butonları - tek satır"""
        for cat_key, cat_name in categories.items():
            cat_btn = tk.Radiobutton(self.category_frame,
                                   text=cat_name,
                                   variable=self.selected_category,
                                   value=cat_key,
                                   font=('Segoe UI', font_size, 'bold'),
                                   bg=self.colors['bg_primary'],
                                   fg=self.colors['text_primary'],
                                   activebackground=self.colors['bg_primary'],
                                   activeforeground=self.colors['accent_primary'],
                                   selectcolor=self.colors['accent_primary'],
                                   command=self.update_platform_display)
            cat_btn.pack(side='left', padx=10, pady=5)
        
    def update_platform_display(self):
        """Seçilen kategoriye göre platform butonlarını güncelle - Responsive"""
        # Mevcut butonları temizle
        for widget in self.platform_container.winfo_children():
            widget.destroy()
            
        selected_cat = self.selected_category.get()
        
        # Seçilen kategorideki platformları filtrele
        filtered_platforms = {name: data for name, data in self.platforms.items() 
                            if data['category'] == selected_cat}
        
        # Responsive grid layout
        # Ekran genişliğine göre sütun sayısını belirle
        if self.current_width >= 1200:
            max_cols = 4
        elif self.current_width >= 900:
            max_cols = 3
        elif self.current_width >= 600:
            max_cols = 2
        else:
            max_cols = 1
        
        row = 0
        col = 0
        
        for name, data in filtered_platforms.items():
            platform_btn = self.create_responsive_platform_button(name, data)
            platform_btn.grid(row=row, column=col, padx=15, pady=15, sticky='nsew')
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Grid ağırlıklarını ayarla
        for i in range(max_cols):
            self.platform_container.grid_columnconfigure(i, weight=1)
        
        # Kategori butonlarını da güncelle
        if hasattr(self, 'category_frame'):
            categories = {
                'social': '👥 Sosyal Medya',
                'media': '🎬 Medya & Eğlence', 
                'gaming': '🎮 Oyun Platformları',
                'dev': '💻 Geliştirici Araçları',
                'tools': '🛠️ Araçlar'
            }
            self.create_responsive_category_buttons(categories)
            
    def create_responsive_platform_button(self, name, data):
        """Ultra modern responsive platform butonu - Daha kompakt"""
        btn_frame = tk.Frame(self.platform_container, bg=self.colors['bg_secondary'])
        btn_frame.configure(relief='solid', borderwidth=1, highlightbackground=self.colors['border'])
        
        # Daha küçük responsive font sizes
        icon_font_size = max(20, self.get_responsive_font_size(28))  # Daha küçük ikonlar
        name_font_size = self.get_responsive_font_size(10)
        domain_font_size = self.get_responsive_font_size(8)
        button_font_size = self.get_responsive_font_size(8)
        
        # Daha küçük responsive padding
        top_padding = max(8, self.get_responsive_padding(12))
        bottom_padding = max(8, self.get_responsive_padding(10))
        side_padding = max(6, self.get_responsive_padding(8))
        
        # İkon - çok küçük
        icon_label = tk.Label(btn_frame,
                            text=data['icon'],
                            font=('Segoe UI', icon_font_size),
                            bg=self.colors['bg_secondary'],
                            fg=data['color'])
        icon_label.pack(pady=(top_padding, 3))
        
        # Platform adı - kısa isim
        display_name = name
        if self.current_width < 800:
            # Uzun isimleri kısalt
            name_mapping = {
                'Twitter/X': 'Twitter',
                'Epic Games': 'Epic',
                'PlayStation': 'PS',
                'Xbox Live': 'Xbox'
            }
            display_name = name_mapping.get(name, name)
        
        name_label = tk.Label(btn_frame,
                            text=display_name,
                            font=('Segoe UI', name_font_size, 'bold'),
                            bg=self.colors['bg_secondary'],
                            fg=self.colors['text_primary'])
        name_label.pack()
        
        # Domain bilgisi - çok kısa format
        domains = data['domains']
        if self.current_width < 600:
            # Çok küçük ekranlarda domain gösterme
            domain_text = f"({len(domains)} site)"
        elif len(domains) == 1:
            domain_text = domains[0][:15] + ("..." if len(domains[0]) > 15 else "")
        else:
            domain_text = f"{len(domains)} site"
        
        if self.current_width >= 600:  # Sadece büyük ekranlarda domain göster
            domain_label = tk.Label(btn_frame,
                                  text=domain_text,
                                  font=('Segoe UI', domain_font_size),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_muted'])
            domain_label.pack(pady=(1, 3))
        
        # Platform'un listede olup olmadığını kontrol et
        sites = self.config_manager.get_bypass_sites()
        platform_domains = data['domains']
        is_added = any(domain in sites for domain in platform_domains)
        
        # Aktivasyon butonu - mini
        if is_added:
            if self.current_width < 600:
                button_text = "✓"
            elif self.current_width < 800:
                button_text = "Eklendi"
            else:
                button_text = "✅ Eklendi"
            button_color = self.colors['accent_success']
            button_command = lambda d=data['domains']: self.remove_platform_site(d)
        else:
            if self.current_width < 600:
                button_text = "+"
            elif self.current_width < 800:
                button_text = "Ekle"
            else:
                button_text = "🚀 Ekle"
            button_color = data['color']
            button_command = lambda d=data['domains']: self.add_platform_site(d)
        
        activate_btn = tk.Button(btn_frame,
                               text=button_text,
                               font=('Segoe UI', button_font_size, 'bold'),
                               bg=button_color,
                               fg='white',
                               activebackground=button_color,
                               relief='flat',
                               cursor='hand2',
                               command=button_command)
        activate_btn.pack(pady=(0, bottom_padding), ipadx=side_padding)
        
        # Hover efektleri
        def on_enter(e):
            btn_frame.configure(highlightbackground=button_color, borderwidth=2)
            
        def on_leave(e):
            btn_frame.configure(highlightbackground=self.colors['border'], borderwidth=1)
            
        # Hover efektlerini tüm elementlere bind et
        widgets_to_bind = [btn_frame, icon_label, name_label, activate_btn]
        if self.current_width >= 600:
            widgets_to_bind.append(domain_label)
        
        for widget in widgets_to_bind:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        return btn_frame
        
    def create_control_panel(self):
        """Alt kontrol paneli - Responsive - Fixed position"""
        # Önce mevcut control panel'leri kontrol et ve kaldır
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                pack_info = widget.pack_info() if hasattr(widget, 'pack_info') else {}
                if (pack_info.get('side') == 'bottom' and 
                    widget.cget('bg') == self.colors['bg_secondary']):
                    widget.destroy()
        
        # Responsive height - daha küçük
        control_height = max(50, self.get_responsive_padding(70))
        
        # Control paneli root'a ekle (fixed position)
        control_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=control_height)
        control_frame.pack(fill='x', side='bottom')
        control_frame.pack_propagate(False)
        
        # Control frame'e özel bir işaret ekle
        control_frame._is_control_panel = True
        
        # Responsive layout
        if self.current_width < 650:  # Daha düşük threshold
            self.create_compact_control_layout(control_frame)
        else:
            self.create_horizontal_control_layout(control_frame)
    
    def create_horizontal_control_layout(self, parent):
        """Büyük ekranlar için horizontal kontrol layout"""
        # Başlat/Durdur butonları (Ortalanmış)
        button_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        button_frame.pack(expand=True, pady=self.get_responsive_padding(20))
        
        button_font_size = self.get_responsive_font_size(14)
        button_padding = self.get_responsive_padding(30)
        
        self.start_button = tk.Button(button_frame,
                                    text="🚀 DPI BYPASS BAŞLAT",
                                    font=('Segoe UI', button_font_size, 'bold'),
                                    bg=self.colors['accent_success'],
                                    fg=self.colors['bg_primary'],
                                    activebackground=self.colors['accent_success'],
                                    relief='flat',
                                    cursor='hand2',
                                    command=self.start_bypass)
        self.start_button.pack(side='left', padx=10, ipadx=button_padding)
        
        self.stop_button = tk.Button(button_frame,
                                   text="⏹️ DURDUR",
                                   font=('Segoe UI', button_font_size, 'bold'),
                                   bg=self.colors['accent_secondary'],
                                   fg='white',
                                   activebackground=self.colors['accent_secondary'],
                                   relief='flat',
                                   cursor='hand2',
                                   state='disabled',
                                   command=self.stop_bypass)
        self.stop_button.pack(side='right', padx=10, ipadx=button_padding)
    
    def create_compact_control_layout(self, parent):
        """Küçük ekranlar için compact kontrol layout"""
        # Ana container
        main_container = tk.Frame(parent, bg=self.colors['bg_secondary'])
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Kontrol butonları - ortalanmış
        button_frame = tk.Frame(main_container, bg=self.colors['bg_secondary'])
        button_frame.pack(expand=True, pady=5)
        
        button_font_size = self.get_responsive_font_size(12)
        
        self.start_button = tk.Button(button_frame,
                                    text="🚀 BAŞLAT",
                                    font=('Segoe UI', button_font_size, 'bold'),
                                    bg=self.colors['accent_success'],
                                    fg=self.colors['bg_primary'],
                                    activebackground=self.colors['accent_success'],
                                    relief='flat',
                                    cursor='hand2',
                                    command=self.start_bypass)
        self.start_button.pack(side='left', padx=5, ipadx=20)
        
        self.stop_button = tk.Button(button_frame,
                                   text="⏹️ DURDUR",
                                   font=('Segoe UI', button_font_size, 'bold'),
                                   bg=self.colors['accent_secondary'],
                                   fg='white',
                                   activebackground=self.colors['accent_secondary'],
                                   relief='flat',
                                   cursor='hand2',
                                   state='disabled',
                                   command=self.stop_bypass)
        self.stop_button.pack(side='right', padx=5, ipadx=20)
        
    def create_settings_page(self):
        """Ayarlar sayfası - Responsive"""
        self.settings_frame = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.settings_frame.page_type = 'content'  # Sayfa tipi işaretle
        self.settings_frame.pack(fill='both', expand=True)
        
        # Responsive başlık - DPI aracını göster
        title_frame = tk.Frame(self.settings_frame, bg=self.colors['bg_primary'])
        title_frame.pack(fill='x', pady=self.get_responsive_padding(30))
        
        title_font_size = self.get_responsive_font_size(24)
        
        # Seçili DPI aracını al
        current_tool = self.config_manager.get_dpi_tool().title()
        title_text = f"⚙️ Ayarlar - {current_tool}"
        
        title = tk.Label(title_frame,
                        text=title_text,
                        font=('Segoe UI', title_font_size, 'bold'),
                        bg=self.colors['bg_primary'],
                        fg=self.colors['text_primary'])
        title.pack()
        
        # Responsive ayarlar container
        settings_container = tk.Frame(self.settings_frame, bg=self.colors['bg_primary'])
        settings_container.pack(fill='both', expand=True, padx=self.get_responsive_padding(50))
        
        # Responsive layout - küçük ekranlarda stacked, büyük ekranlarda side by side
        if self.current_width < 1000:
            # Küçük ekranlarda vertical layout
            self.create_stacked_settings_layout(settings_container)
        else:
            # Büyük ekranlarda horizontal layout
            self.create_horizontal_settings_layout(settings_container)
    
    def create_horizontal_settings_layout(self, parent):
        """Büyük ekranlar için horizontal ayarlar layout"""
        label_font_size = self.get_responsive_font_size(14)
        text_font_size = self.get_responsive_font_size(12)
        
        # DPI Araç Seçimi - En üstte
        dpi_tool_frame = tk.LabelFrame(parent,
                                     text="🛠️ DPI Aracı Seçimi",
                                     font=('Segoe UI', label_font_size, 'bold'),
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['text_primary'],
                                     borderwidth=2,
                                     relief='solid')
        dpi_tool_frame.pack(fill='x', pady=(0, self.get_responsive_padding(20)))
        
        # DPI araç seçimi içeriği
        tool_content = tk.Frame(dpi_tool_frame, bg=self.colors['bg_secondary'])
        tool_content.pack(fill='x', padx=self.get_responsive_padding(20), pady=self.get_responsive_padding(15))
        
        self.dpi_tool_var = tk.StringVar(value=self.config_manager.get_dpi_tool())
        
        # GoodbyeDPI seçeneği
        goodbyedpi_radio = tk.Radiobutton(tool_content,
                                        text="GoodbyeDPI (Standart) - Windows için optimize edilmiş",
                                        variable=self.dpi_tool_var,
                                        value="goodbyedpi",
                                        font=('Segoe UI', text_font_size),
                                        bg=self.colors['bg_secondary'],
                                        fg=self.colors['text_primary'],
                                        activebackground=self.colors['bg_secondary'],
                                        activeforeground=self.colors['accent_primary'],
                                        selectcolor=self.colors['accent_primary'],
                                        command=self.on_dpi_tool_change)
        goodbyedpi_radio.pack(anchor='w', pady=3)
        
        # Zapret seçeneği
        zapret_radio = tk.Radiobutton(tool_content,
                                    text="Zapret (Önerilen) - Gelişmiş konfigürasyon",
                                    variable=self.dpi_tool_var,
                                    value="zapret",
                                    font=('Segoe UI', text_font_size),
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_primary'],
                                    activebackground=self.colors['bg_secondary'],
                                    activeforeground=self.colors['accent_primary'],
                                    selectcolor=self.colors['accent_primary'],
                                    command=self.on_dpi_tool_change)
        zapret_radio.pack(anchor='w', pady=3)
        
        # Alt kısımda paneller
        panels_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        panels_frame.pack(fill='both', expand=True)
        
        # Sol panel - Domain yönetimi
        left_panel = tk.LabelFrame(panels_frame,
                                 text="🌐 Domain Yönetimi",
                                 font=('Segoe UI', label_font_size, 'bold'),
                                 bg=self.colors['bg_secondary'],
                                 fg=self.colors['text_primary'],
                                 borderwidth=2,
                                 relief='solid')
        left_panel.pack(side='left', fill='both', expand=True, 
                       padx=(0, self.get_responsive_padding(25)), 
                       pady=self.get_responsive_padding(20))
        
        # Domain listesi
        tk.Label(left_panel,
                text="Aktif Domainler:",
                font=('Segoe UI', text_font_size, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', 
                                                   padx=self.get_responsive_padding(20), 
                                                   pady=(self.get_responsive_padding(20), 10))
        
        # Listbox container
        list_container = tk.Frame(left_panel, bg=self.colors['bg_secondary'])
        list_container.pack(fill='both', expand=True, 
                          padx=self.get_responsive_padding(20), 
                          pady=10)
        
        # Scrollbar ile listbox
        scrollbar = tk.Scrollbar(list_container, bg=self.colors['bg_tertiary'])
        scrollbar.pack(side='right', fill='y')
        
        listbox_font_size = self.get_responsive_font_size(11)
        self.domain_listbox = tk.Listbox(list_container,
                                       yscrollcommand=scrollbar.set,
                                       font=('Consolas', listbox_font_size),
                                       bg=self.colors['bg_tertiary'],
                                       fg=self.colors['text_primary'],
                                       selectbackground=self.colors['accent_primary'],
                                       selectforeground=self.colors['bg_primary'],
                                       borderwidth=0,
                                       highlightthickness=0)
        self.domain_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.domain_listbox.yview)
        
        # Domain kontrol butonları
        self.create_domain_buttons(left_panel)
        
        # Sağ panel - Ülke ve diğer ayarlar
        self.create_right_settings_panel(panels_frame)
    
    def create_stacked_settings_layout(self, parent):
        """Küçük ekranlar için stacked ayarlar layout"""
        # DPI Araç Seçimi - En üstte
        dpi_tool_frame = tk.LabelFrame(parent,
                                     text="🛠️ DPI Aracı Seçimi",
                                     font=('Segoe UI', self.get_responsive_font_size(14), 'bold'),
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['text_primary'],
                                     borderwidth=2,
                                     relief='solid')
        dpi_tool_frame.pack(fill='x', pady=(0, 10))
        
        # DPI araç seçimi içeriği
        tool_content = tk.Frame(dpi_tool_frame, bg=self.colors['bg_secondary'])
        tool_content.pack(fill='x', padx=10, pady=10)
        
        self.dpi_tool_var = tk.StringVar(value=self.config_manager.get_dpi_tool())
        
        # GoodbyeDPI seçeneği
        goodbyedpi_radio = tk.Radiobutton(tool_content,
                                        text="GoodbyeDPI (Standart)",
                                        variable=self.dpi_tool_var,
                                        value="goodbyedpi",
                                        font=('Segoe UI', self.get_responsive_font_size(12)),
                                        bg=self.colors['bg_secondary'],
                                        fg=self.colors['text_primary'],
                                        activebackground=self.colors['bg_secondary'],
                                        activeforeground=self.colors['accent_primary'],
                                        selectcolor=self.colors['accent_primary'],
                                        command=self.on_dpi_tool_change)
        goodbyedpi_radio.pack(anchor='w', pady=2)
        
        # Zapret seçeneği
        zapret_radio = tk.Radiobutton(tool_content,
                                    text="Zapret (Önerilen)",
                                    variable=self.dpi_tool_var,
                                    value="zapret",
                                    font=('Segoe UI', self.get_responsive_font_size(12)),
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_primary'],
                                    activebackground=self.colors['bg_secondary'],
                                    activeforeground=self.colors['accent_primary'],
                                    selectcolor=self.colors['accent_primary'],
                                    command=self.on_dpi_tool_change)
        zapret_radio.pack(anchor='w', pady=2)
        
        # Domain yönetimi (orta)
        domain_frame = tk.LabelFrame(parent,
                                   text="🌐 Domain Yönetimi",
                                   font=('Segoe UI', self.get_responsive_font_size(14), 'bold'),
                                   bg=self.colors['bg_secondary'],
                                   fg=self.colors['text_primary'],
                                   borderwidth=2,
                                   relief='solid')
        domain_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Kompakt domain listesi
        tk.Label(domain_frame,
                text="Aktif Domainler:",
                font=('Segoe UI', self.get_responsive_font_size(12), 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', padx=10, pady=(10, 5))
        
        # Küçük listbox
        list_container = tk.Frame(domain_frame, bg=self.colors['bg_secondary'])
        list_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_container, bg=self.colors['bg_tertiary'])
        scrollbar.pack(side='right', fill='y')
        
        self.domain_listbox = tk.Listbox(list_container,
                                       yscrollcommand=scrollbar.set,
                                       height=6,  # Sabit küçük height
                                       font=('Consolas', self.get_responsive_font_size(10)),
                                       bg=self.colors['bg_tertiary'],
                                       fg=self.colors['text_primary'],
                                       selectbackground=self.colors['accent_primary'],
                                       selectforeground=self.colors['bg_primary'],
                                       borderwidth=0,
                                       highlightthickness=0)
        self.domain_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.domain_listbox.yview)
        
        # Kompakt butonlar
        self.create_compact_domain_buttons(domain_frame)
        
        # Ayarlar paneli (alt)
        settings_frame = tk.LabelFrame(parent,
                                     text="⚙️ Genel Ayarlar",
                                     font=('Segoe UI', self.get_responsive_font_size(14), 'bold'),
                                     bg=self.colors['bg_secondary'],
                                     fg=self.colors['text_primary'],
                                     borderwidth=2,
                                     relief='solid')
        settings_frame.pack(fill='x', pady=(10, 0))
        
        self.create_compact_settings_panel(settings_frame)
    
    def create_domain_buttons(self, parent):
        """Domain kontrol butonları"""
        domain_btn_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        domain_btn_frame.pack(fill='x', 
                            padx=self.get_responsive_padding(20), 
                            pady=self.get_responsive_padding(20))
        
        button_font_size = self.get_responsive_font_size(10)
        
        tk.Button(domain_btn_frame,
                 text="➕ Domain Ekle",
                 font=('Segoe UI', button_font_size, 'bold'),
                 bg=self.colors['accent_success'],
                 fg=self.colors['bg_primary'],
                 relief='flat',
                 cursor='hand2',
                 command=self.add_domain_dialog).pack(side='left', padx=5, ipadx=15, pady=5)
        
        tk.Button(domain_btn_frame,
                 text="➖ Domain Sil",
                 font=('Segoe UI', button_font_size, 'bold'),
                 bg=self.colors['accent_secondary'],
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 command=self.remove_selected_domain).pack(side='left', padx=5, ipadx=15, pady=5)
        
        tk.Button(domain_btn_frame,
                 text="🗑️ Tümünü Temizle",
                 font=('Segoe UI', button_font_size, 'bold'),
                 bg=self.colors['accent_warning'],
                 fg=self.colors['bg_primary'],
                 relief='flat',
                 cursor='hand2',
                 command=self.clear_all_domains).pack(side='left', padx=5, ipadx=15, pady=5)
    
    def create_compact_domain_buttons(self, parent):
        """Kompakt domain butonları"""
        domain_btn_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        domain_btn_frame.pack(fill='x', padx=10, pady=10)
        
        button_font_size = self.get_responsive_font_size(9)
        
        # Üst satır
        top_row = tk.Frame(domain_btn_frame, bg=self.colors['bg_secondary'])
        top_row.pack(fill='x', pady=(0, 5))
        
        tk.Button(top_row,
                 text="➕ Ekle",
                 font=('Segoe UI', button_font_size, 'bold'),
                 bg=self.colors['accent_success'],
                 fg=self.colors['bg_primary'],
                 relief='flat',
                 cursor='hand2',
                 command=self.add_domain_dialog).pack(side='left', fill='x', expand=True, padx=(0, 2))
        
        tk.Button(top_row,
                 text="➖ Sil",
                 font=('Segoe UI', button_font_size, 'bold'),
                 bg=self.colors['accent_secondary'],
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 command=self.remove_selected_domain).pack(side='right', fill='x', expand=True, padx=(2, 0))
        
        # Alt satır
        tk.Button(domain_btn_frame,
                 text="🗑️ Tümünü Temizle",
                 font=('Segoe UI', button_font_size, 'bold'),
                 bg=self.colors['accent_warning'],
                 fg=self.colors['bg_primary'],
                 relief='flat',
                 cursor='hand2',
                 command=self.clear_all_domains).pack(fill='x', pady=(5, 0))
    
    def create_right_settings_panel(self, parent):
        """Sağ ayarlar paneli"""
        right_panel = tk.LabelFrame(parent,
                                  text="🌍 Ülke & Genel Ayarlar",
                                  font=('Segoe UI', self.get_responsive_font_size(14), 'bold'),
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_primary'],
                                  borderwidth=2,
                                  relief='solid')
        right_panel.pack(side='right', fill='both', expand=True, 
                       padx=(self.get_responsive_padding(25), 0), 
                       pady=self.get_responsive_padding(20))
        
        # Ülke seçimi
        country_frame = tk.Frame(right_panel, bg=self.colors['bg_secondary'])
        country_frame.pack(fill='x', 
                         padx=self.get_responsive_padding(20), 
                         pady=self.get_responsive_padding(20))
        
        country_font_size = self.get_responsive_font_size(12)
        tk.Label(country_frame,
                text="🌍 Ülke Seçimi:",
                font=('Segoe UI', country_font_size, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 10))
        
        countries = [
            ("🇹🇷 Türkiye", "TR"),
            ("🇺🇸 Amerika", "US"),
            ("🇩🇪 Almanya", "DE"),
            ("🇬🇧 İngiltere", "GB"),
            ("🇷🇺 Rusya", "RU"),
            ("🇫🇷 Fransa", "FR"),
            ("🇳🇱 Hollanda", "NL"),
            ("🇸🇪 İsveç", "SE"),
            ("🇨🇭 İsviçre", "CH"),
            ("🇯🇵 Japonya", "JP"),
            ("🇸🇬 Singapur", "SG")
        ]
        
        self.selected_country = tk.StringVar(value="TR")
        radio_font_size = self.get_responsive_font_size(11)
        
        for country_name, country_code in countries[:5]:  # İlk 5 ülke
            rb = tk.Radiobutton(country_frame,
                              text=country_name,
                              variable=self.selected_country,
                              value=country_code,
                              font=('Segoe UI', radio_font_size),
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'],
                              activebackground=self.colors['bg_secondary'],
                              activeforeground=self.colors['accent_primary'],
                              selectcolor=self.colors['accent_primary'])
            rb.pack(anchor='w', pady=2)
        
        # Gelişmiş ayarlar
        advanced_frame = tk.Frame(right_panel, bg=self.colors['bg_secondary'])
        advanced_frame.pack(fill='x', 
                          padx=self.get_responsive_padding(20), 
                          pady=(self.get_responsive_padding(30), self.get_responsive_padding(20)))
        
        advanced_font_size = self.get_responsive_font_size(12)
        tk.Label(advanced_frame,
                text="🔧 Gelişmiş Ayarlar:",
                font=('Segoe UI', advanced_font_size, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        # Ayar seçenekleri
        checkbox_font_size = self.get_responsive_font_size(10)
        
        self.auto_start = tk.BooleanVar()
        tk.Checkbutton(advanced_frame,
                      text="🚀 Otomatik başlat",
                      variable=self.auto_start,
                      font=('Segoe UI', checkbox_font_size),
                      bg=self.colors['bg_secondary'],
                      fg=self.colors['text_primary'],
                      activebackground=self.colors['bg_secondary'],
                      activeforeground=self.colors['text_primary'],
                      selectcolor=self.colors['accent_primary']).pack(anchor='w', pady=3)
        
        self.show_notifications = tk.BooleanVar(value=True)
        tk.Checkbutton(advanced_frame,
                      text="🔔 Bildirimler",
                      variable=self.show_notifications,
                      font=('Segoe UI', checkbox_font_size),
                      bg=self.colors['bg_secondary'],
                      fg=self.colors['text_primary'],
                      activebackground=self.colors['bg_secondary'],
                      activeforeground=self.colors['text_primary'],
                      selectcolor=self.colors['accent_primary']).pack(anchor='w', pady=3)
        
        self.minimize_to_tray = tk.BooleanVar()
        tk.Checkbutton(advanced_frame,
                      text="📌 System tray'e küçült",
                      variable=self.minimize_to_tray,
                      command=self.on_tray_setting_change,
                      font=('Segoe UI', checkbox_font_size),
                      bg=self.colors['bg_secondary'],
                      fg=self.colors['text_primary'],
                      activebackground=self.colors['bg_secondary'],
                      activeforeground=self.colors['text_primary'],
                      selectcolor=self.colors['accent_primary']).pack(anchor='w', pady=3)
        
        # Kaydet butonu
        save_frame = tk.Frame(right_panel, bg=self.colors['bg_secondary'])
        save_frame.pack(fill='x', 
                      padx=self.get_responsive_padding(20), 
                      pady=self.get_responsive_padding(30))
        
        save_font_size = self.get_responsive_font_size(12)
        tk.Button(save_frame,
                 text="💾 Ayarları Kaydet",
                 font=('Segoe UI', save_font_size, 'bold'),
                 bg=self.colors['accent_primary'],
                 fg=self.colors['bg_primary'],
                 relief='flat',
                 cursor='hand2',
                 command=self.save_all_settings).pack(ipadx=30, pady=10)
    
    def create_compact_settings_panel(self, parent):
        """Kompakt ayarlar paneli"""
        # İki sütun layout
        main_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Sol sütun - Ülke seçimi
        left_col = tk.Frame(main_frame, bg=self.colors['bg_secondary'])
        left_col.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        font_size = self.get_responsive_font_size(11)
        tk.Label(left_col,
                text="🌍 Ülke:",
                font=('Segoe UI', font_size, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))
        
        # Ülke seçimi combobox ile
        self.selected_country = tk.StringVar(value="TR")
        country_combo = ttk.Combobox(left_col,
                                   textvariable=self.selected_country,
                                   values=["TR", "US", "DE", "GB", "FR", "RU", "NL", "SE", "CH", "JP", "SG"],
                                   state='readonly',
                                   font=('Segoe UI', self.get_responsive_font_size(10)))
        country_combo.pack(fill='x', pady=(0, 10))
        
        # Sağ sütun - Genel ayarlar
        right_col = tk.Frame(main_frame, bg=self.colors['bg_secondary'])
        right_col.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        tk.Label(right_col,
                text="⚙️ Ayarlar:",
                font=('Segoe UI', font_size, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 5))
        
        checkbox_font_size = self.get_responsive_font_size(9)
        
        self.auto_start = tk.BooleanVar()
        tk.Checkbutton(right_col,
                      text="🚀 Otomatik başlat",
                      variable=self.auto_start,
                      font=('Segoe UI', checkbox_font_size),
                      bg=self.colors['bg_secondary'],
                      fg=self.colors['text_primary'],
                      activebackground=self.colors['bg_secondary'],
                      activeforeground=self.colors['text_primary'],
                      selectcolor=self.colors['accent_primary']).pack(anchor='w', pady=1)
        
        self.show_notifications = tk.BooleanVar(value=True)
        tk.Checkbutton(right_col,
                      text="🔔 Bildirimler",
                      variable=self.show_notifications,
                      font=('Segoe UI', checkbox_font_size),
                      bg=self.colors['bg_secondary'],
                      fg=self.colors['text_primary'],
                      activebackground=self.colors['bg_secondary'],
                      activeforeground=self.colors['text_primary'],
                      selectcolor=self.colors['accent_primary']).pack(anchor='w', pady=1)
        
        # Kaydet butonu - alt
        save_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        save_frame.pack(fill='x', padx=10, pady=(10, 10))
        
        save_font_size = self.get_responsive_font_size(11)
        tk.Button(save_frame,
                 text="💾 Ayarları Kaydet",
                 font=('Segoe UI', save_font_size, 'bold'),
                 bg=self.colors['accent_primary'],
                 fg=self.colors['bg_primary'],
                 relief='flat',
                 cursor='hand2',
                 command=self.save_all_settings).pack(expand=True)
    
    def switch_page(self, page):
        """Sayfa değiştir"""
        self.current_page = page
        
        # Mevcut control panel'leri temizle (özel işarete göre)
        for widget in list(self.root.winfo_children()):
            if (isinstance(widget, tk.Frame) and 
                hasattr(widget, '_is_control_panel')):
                widget.destroy()
        
        # Sadece içerik sayfalarını kaldır, navigasyonu koru
        for widget in list(self.root.winfo_children()):
            if isinstance(widget, tk.Frame) and hasattr(widget, 'page_type'):
                widget.destroy()
        
        # Canvas ve scrollbar'ları da temizle
        for widget in list(self.root.winfo_children()):
            if isinstance(widget, (tk.Canvas, tk.Scrollbar)):
                widget.destroy()
        
        # Yeni sayfayı oluştur
        if page == 'main':
            self.create_main_page()
            # Platform displayini güncelle
            self.root.after(50, self.update_platform_display)
        elif page == 'settings':
            self.create_settings_page()
            # Ayarlar sayfası oluşturulduktan sonra config'i yükle
            self.load_config()
            try:
                self.update_domain_list()
            except Exception:
                # Widget yoksa veya hata varsa sessizce geç
                pass
        
        # Navigasyon butonlarının durumunu güncelle
        self.update_navigation_buttons()
        
    def update_navigation_buttons(self):
        """Navigasyon butonlarının görünümünü güncelle"""
        if hasattr(self, 'main_btn') and hasattr(self, 'settings_btn'):
            # Ana sayfa butonu
            if self.current_page == 'main':
                self.main_btn.config(
                    bg=self.colors['accent_primary'],
                    fg=self.colors['bg_primary']
                )
                self.settings_btn.config(
                    bg=self.colors['bg_tertiary'],
                    fg=self.colors['text_primary']
                )
            else:  # settings page
                self.main_btn.config(
                    bg=self.colors['bg_tertiary'],
                    fg=self.colors['text_primary']
                )
                self.settings_btn.config(
                    bg=self.colors['accent_primary'],
                    fg=self.colors['bg_primary']
                )
        
    def add_platform_site(self, domains):
        """Platform sitelerini bypass listesine ekle (çoklu domain destekli)"""
        # Eğer tek bir string gelirse, listeye çevir
        if isinstance(domains, str):
            domains = [domains]
        
        sites = self.config_manager.get_bypass_sites()
        added_domains = []
        
        for domain in domains:
            if domain not in sites:
                sites.append(domain)
                added_domains.append(domain)
        
        if added_domains:
            self.config_manager.update_bypass_sites(sites)
            if self.show_notifications.get() if hasattr(self, 'show_notifications') else True:
                if len(added_domains) == 1:
                    messagebox.showinfo("✅ Başarılı", 
                                      f"🚀 {added_domains[0]} bypass listesine eklendi!\n"
                                      f"Toplam {len(sites)} site aktif.")
                else:
                    messagebox.showinfo("✅ Başarılı", 
                                      f"🚀 {len(added_domains)} domain bypass listesine eklendi:\n" +
                                      "\n".join(f"• {d}" for d in added_domains[:5]) + 
                                      (f"\n... ve {len(added_domains)-5} tane daha" if len(added_domains) > 5 else "") +
                                      f"\n\nToplam {len(sites)} site aktif.")
            
            # Platform butonlarını güncelle
            self.update_platform_display()
            
            # Domain listesini güncelle (eğer ayarlar sayfasındaysak)
            try:
                self.update_domain_list()
            except Exception:
                # Widget yoksa veya hata varsa sessizce geç
                pass
            
            # Eğer bypass aktifse, yeniden başlat
            if hasattr(self, 'dpi_bypass') and hasattr(self.dpi_bypass, 'active') and self.dpi_bypass.active:
                threading.Thread(target=self._restart_bypass, daemon=True).start()
        else:
            if self.show_notifications.get() if hasattr(self, 'show_notifications') else True:
                messagebox.showwarning("ℹ️ Bilgi", "Tüm domainler zaten listede mevcut!")
    
    def remove_platform_site(self, domains):
        """Platform sitelerini bypass listesinden çıkar (çoklu domain destekli)"""
        # Eğer tek bir string gelirse, listeye çevir
        if isinstance(domains, str):
            domains = [domains]
        
        sites = self.config_manager.get_bypass_sites()
        removed_domains = []
        
        for domain in domains:
            if domain in sites:
                sites.remove(domain)
                removed_domains.append(domain)
        
        if removed_domains:
            self.config_manager.update_bypass_sites(sites)
            if self.show_notifications.get() if hasattr(self, 'show_notifications') else True:
                if len(removed_domains) == 1:
                    messagebox.showinfo("✅ Başarılı", 
                                      f"🗑️ {removed_domains[0]} bypass listesinden çıkarıldı!\n"
                                      f"Toplam {len(sites)} site aktif.")
                else:
                    messagebox.showinfo("✅ Başarılı", 
                                      f"🗑️ {len(removed_domains)} domain bypass listesinden çıkarıldı:\n" +
                                      "\n".join(f"• {d}" for d in removed_domains[:5]) + 
                                      (f"\n... ve {len(removed_domains)-5} tane daha" if len(removed_domains) > 5 else "") +
                                      f"\n\nToplam {len(sites)} site aktif.")
            
            # Platform butonlarını güncelle
            self.update_platform_display()
            
            # Domain listesini güncelle (eğer ayarlar sayfasındaysak)
            try:
                self.update_domain_list()
            except Exception:
                # Widget yoksa veya hata varsa sessizce geç
                pass
            
            # Eğer bypass aktifse, yeniden başlat
            if hasattr(self, 'dpi_bypass') and hasattr(self.dpi_bypass, 'active') and self.dpi_bypass.active:
                threading.Thread(target=self._restart_bypass, daemon=True).start()
        else:
            if self.show_notifications.get() if hasattr(self, 'show_notifications') else True:
                messagebox.showwarning("ℹ️ Bilgi", "Bu domainler zaten listede yok!")
    
    def add_domain_dialog(self):
        """Domain ekleme dialogu"""
        domain = simpledialog.askstring("🌐 Domain Ekle", 
                                       "Domain adresini girin:\n(örn: example.com)")
        if domain:
            domain = domain.strip().replace('https://', '').replace('http://', '').replace('www.', '')
            if '/' in domain:
                domain = domain.split('/')[0]
            self.add_platform_site(domain)
            try:
                self.update_domain_list()
            except Exception:
                # Widget yoksa veya hata varsa sessizce geç
                pass
    
    def remove_selected_domain(self):
        """Seçili domain'i sil"""
        selection = self.domain_listbox.curselection()
        if selection:
            selected_text = self.domain_listbox.get(selection[0])
            # "01. example.com" formatından sadece "example.com" kısmını al
            domain = selected_text.split('. ', 1)[1] if '. ' in selected_text else selected_text
            sites = self.config_manager.get_bypass_sites()
            if domain in sites:
                sites.remove(domain)
                self.config_manager.update_bypass_sites(sites)
                try:
                    self.update_domain_list()
                except Exception:
                    # Widget yoksa veya hata varsa sessizce geç
                    pass
                if self.show_notifications.get() if hasattr(self, 'show_notifications') else True:
                    messagebox.showinfo("✅ Başarılı", f"❌ {domain} listeden kaldırıldı!")
                
                # Eğer bypass aktifse, yeniden başlat
                if hasattr(self, 'dpi_bypass') and hasattr(self.dpi_bypass, 'active') and self.dpi_bypass.active:
                    threading.Thread(target=self._restart_bypass, daemon=True).start()
            else:
                messagebox.showwarning("⚠️ Uyarı", f"Domain bulunamadı: {domain}")
        else:
            messagebox.showwarning("⚠️ Uyarı", "Lütfen silmek istediğiniz domain'i seçin!")
    
    def clear_all_domains(self):
        """Tüm domain'leri temizle"""
        if messagebox.askyesno("⚠️ Onay", "Tüm domain'leri silmek istediğinizden emin misiniz?"):
            self.config_manager.update_bypass_sites([])
            try:
                self.update_domain_list()
            except Exception:
                # Widget yoksa veya hata varsa sessizce geç
                pass
            messagebox.showinfo("✅ Başarılı", "🗑️ Tüm domain'ler temizlendi!")
            
            # Eğer bypass aktifse, yeniden başlat
            if hasattr(self, 'dpi_bypass') and hasattr(self.dpi_bypass, 'active') and self.dpi_bypass.active:
                threading.Thread(target=self._restart_bypass, daemon=True).start()
    
    def update_domain_list(self):
        """Domain listesini güncelle"""
        if hasattr(self, 'domain_listbox'):
            try:
                # Widget'ın hala geçerli olup olmadığını kontrol et
                self.domain_listbox.winfo_exists()
                self.domain_listbox.delete(0, tk.END)
                sites = self.config_manager.get_bypass_sites()
                for i, site in enumerate(sites, 1):
                    self.domain_listbox.insert(tk.END, f"{i:02d}. {site}")
            except tk.TclError:
                # Widget silinmişse, referansı da temizle
                if hasattr(self, 'domain_listbox'):
                    delattr(self, 'domain_listbox')
    
    def save_all_settings(self):
        """Tüm ayarları kaydet"""
        # Ülke ayarını kaydet
        country = self.selected_country.get()
        self.config_manager.set_country_code(country)
        
        # DPI tool ayarını kaydet 
        selected_tool = self.dpi_tool_var.get()
        self.config_manager.set_dpi_tool(selected_tool)
        
        # Diğer ayarları kaydet
        # Auto-start ayarı
        if hasattr(self, 'auto_start'):
            self.config_manager.set_setting('auto_start', self.auto_start.get())
        
        # Notification ayarı  
        if hasattr(self, 'show_notifications'):
            self.config_manager.set_setting('show_notifications', self.show_notifications.get())
        
        messagebox.showinfo("✅ Başarılı", 
                           f"🌍 Ülke: {country}\n"
                           f"🔧 DPI Aracı: {selected_tool.title()}\n"
                           f"⚙️ Tüm ayarlar başarıyla kaydedildi!")
    
    def show_download_dialog(self):
        """İndirme progress dialog'unu göster"""
        if self.download_dialog:
            return  # Zaten açık
            
        self.download_dialog = tk.Toplevel(self.root)
        self.download_dialog.title("📥 İndirme")
        self.download_dialog.geometry("500x200")
        self.download_dialog.configure(bg=self.colors['bg_secondary'])
        self.download_dialog.resizable(False, False)
        self.download_dialog.transient(self.root)
        self.download_dialog.grab_set()
        
        # Center the dialog
        self.download_dialog.geometry(f"+{self.root.winfo_x() + 350}+{self.root.winfo_y() + 300}")
        
        # Ana frame
        main_frame = tk.Frame(self.download_dialog, bg=self.colors['bg_secondary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = tk.Label(main_frame, 
                              text="DPI Bypass Aracı İndiriliyor",
                              bg=self.colors['bg_secondary'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 14, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # Durum metni
        self.download_status_var = tk.StringVar()
        self.download_status_var.set("Hazırlanıyor...")
        status_label = tk.Label(main_frame,
                               textvariable=self.download_status_var,
                               bg=self.colors['bg_secondary'],
                               fg=self.colors['text_secondary'],
                               font=('Segoe UI', 10))
        status_label.pack(pady=(0, 10))
        
        # Progress bar
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Download.Horizontal.TProgressbar",
                       background=self.colors['accent_primary'],
                       troughcolor=self.colors['bg_tertiary'],
                       borderwidth=0,
                       lightcolor=self.colors['accent_primary'],
                       darkcolor=self.colors['accent_primary'])
        
        self.download_progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame,
                                      variable=self.download_progress_var,
                                      maximum=100,
                                      style="Download.Horizontal.TProgressbar",
                                      length=400)
        progress_bar.pack(pady=(0, 15))
        
        # Progress yüzde metni
        self.progress_percent_var = tk.StringVar()
        self.progress_percent_var.set("0%")
        percent_label = tk.Label(main_frame,
                                textvariable=self.progress_percent_var,
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['accent_primary'],
                                font=('Segoe UI', 12, 'bold'))
        percent_label.pack()
    
    def update_download_progress(self, message, progress):
        """İndirme progress'ini güncelle"""
        if not self.download_dialog:
            return
            
        # UI thread'inde çalıştır
        self.root.after(0, lambda: self._update_progress_ui(message, progress))
    
    def _update_progress_ui(self, message, progress):
        """Progress UI'sini güncelle (main thread'de)"""
        if not self.download_dialog or not self.download_status_var:
            return
            
        self.download_status_var.set(message)
        self.download_progress_var.set(progress)
        if self.progress_percent_var:
            self.progress_percent_var.set(f"{progress:.1f}%")
        
        # İndirme tamamlandıysa dialog'u kapat
        if progress >= 100 or "başarıyla" in message.lower() or "hata" in message.lower():
            self.root.after(1500, self.close_download_dialog)  # 1.5 saniye bekle
    
    def close_download_dialog(self):
        """İndirme dialog'unu kapat"""
        if self.download_dialog:
            self.download_dialog.grab_release()
            self.download_dialog.destroy()
            self.download_dialog = None
            self.download_progress_var = None
            self.download_status_var = None
            self.progress_percent_var = None
    
    def start_bypass(self):
        """DPI Bypass başlat"""
        if not self.bypass_active:
            threading.Thread(target=self._start_bypass_thread, daemon=True).start()
    
    def _start_bypass_thread(self):
        """Bypass başlatma thread'i"""
        try:
            # İndirme gerekip gerekmediğini kontrol et
            current_tool = self.config_manager.get_dpi_tool()
            needs_download = False
            
            if current_tool == 'zapret':
                needs_download = not self.dpi_bypass.zapret.is_available()
            else:  # goodbyedpi
                needs_download = not self.dpi_bypass.goodbyedpi.is_available()
            
            # İndirme gerekiyorsa dialog göster
            if needs_download:
                self.root.after(0, self.show_download_dialog)
            
            # DPI Bypass başlat ve progress callback'ini ver
            success = self.dpi_bypass.start_bypass(
                progress_callback=self.update_download_progress if needs_download else None
            )
            
            if success:
                self.bypass_active = True
                self.root.after(0, self._update_ui_started)
            else:
                self.root.after(0, lambda: messagebox.showerror("❌ Hata", "DPI Bypass başlatılamadı!"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("❌ Hata", f"Başlatma hatası: {str(e)}"))
    
    def _update_ui_started(self):
        """UI'yi başlatılmış duruma güncelle"""
        self.status_indicator.configure(fg=self.colors['accent_success'])
        
        # DPI araç ismini al ve göster
        current_tool = self.config_manager.get_dpi_tool()
        tool_names = {'goodbyedpi': 'GoodbyeDPI', 'zapret': 'Zapret'}
        tool_name = tool_names.get(current_tool, current_tool)
        
        self.status_text.configure(text=f"Aktif ({tool_name})", fg=self.colors['accent_success'])
        if hasattr(self, 'start_button'):
            self.start_button.configure(state='disabled')
        if hasattr(self, 'stop_button'):
            self.stop_button.configure(state='normal')
        
        # Tray menüsünü güncelle
        self.update_tray_menu()
            
    def update_status(self):
        """Status göstergesini güncelle"""
        current_tool = self.config_manager.get_dpi_tool()
        tool_names = {'goodbyedpi': 'GoodbyeDPI', 'zapret': 'Zapret'}
        tool_name = tool_names.get(current_tool, current_tool)
        
        if self.bypass_active:
            self.status_indicator.configure(fg=self.colors['accent_success'])
            self.status_text.configure(text=f"Aktif ({tool_name})", fg=self.colors['accent_success'])
        else:
            self.status_indicator.configure(fg=self.colors['accent_secondary'])
            self.status_text.configure(text=f"Devre Dışı ({tool_name})", fg=self.colors['accent_secondary'])
    
    def stop_bypass(self):
        """DPI Bypass durdur"""
        if self.bypass_active:
            threading.Thread(target=self._stop_bypass_thread, daemon=True).start()
    
    def _stop_bypass_thread(self):
        """Bypass durdurma thread'i"""
        try:
            self.dpi_bypass.stop_bypass()
            self.bypass_active = False
            self.root.after(0, self._update_ui_stopped)
        except Exception as e:
            messagebox.showerror("❌ Hata", f"Durdurma hatası: {str(e)}")
    
    def _restart_bypass(self):
        """Bypass'ı yeniden başlat"""
        try:
            if hasattr(self, 'dpi_bypass') and self.dpi_bypass.active:
                self.dpi_bypass.stop_bypass()
                time.sleep(1)  # Kısa bekleme
                
                # İndirme gerekip gerekmediğini kontrol et
                current_tool = self.config_manager.get_dpi_tool()
                needs_download = False
                
                if current_tool == 'zapret':
                    needs_download = not self.dpi_bypass.zapret.is_available()
                else:  # goodbyedpi
                    needs_download = not self.dpi_bypass.goodbyedpi.is_available()
                
                # İndirme gerekiyorsa dialog göster
                if needs_download:
                    self.root.after(0, self.show_download_dialog)
                
                # DPI Bypass başlat ve progress callback'ini ver
                self.dpi_bypass.start_bypass(
                    progress_callback=self.update_download_progress if needs_download else None
                )
        except Exception as e:
            messagebox.showerror("❌ Hata", f"Yeniden başlatma hatası: {str(e)}")
    
    def _update_ui_stopped(self):
        """UI'yi durdurulmuş duruma güncelle"""
        # DPI araç ismini al ve göster
        current_tool = self.config_manager.get_dpi_tool()
        tool_names = {'goodbyedpi': 'GoodbyeDPI', 'zapret': 'Zapret'}
        tool_name = tool_names.get(current_tool, current_tool)
        
        self.status_indicator.configure(fg=self.colors['accent_secondary'])
        self.status_text.configure(text=f"Devre Dışı ({tool_name})", fg=self.colors['accent_secondary'])
        if hasattr(self, 'start_button'):
            self.start_button.configure(state='normal')
        if hasattr(self, 'stop_button'):
            self.stop_button.configure(state='disabled')
        
        # Tray menüsünü güncelle
        self.update_tray_menu()
    
    def load_initial_config(self):
        """Program başlarken sadece kritik ayarları yükle"""
        # Bu metod şimdilik boş - tray ayarı check_and_setup_tray'de kontrol edilecek
        pass
    
    def load_config(self):
        """Konfigürasyonu yükle"""
        # Blacklist dosyası ihtiyaç anında oluşturulacak
        
        # Kaydedilmiş ülke kodunu yükle
        saved_country = self.config_manager.get_country_code()
        if hasattr(self, 'selected_country'):
            self.selected_country.set(saved_country)
            
        # Kaydedilmiş DPI tool'u yükle
        saved_tool = self.config_manager.get_dpi_tool()
        if hasattr(self, 'dpi_tool_var'):
            self.dpi_tool_var.set(saved_tool)
        
        # Diğer ayarları yükle
        if hasattr(self, 'auto_start'):
            auto_start = self.config_manager.get_setting('auto_start', False)
            self.auto_start.set(auto_start)
            
        if hasattr(self, 'show_notifications'):
            show_notifications = self.config_manager.get_setting('show_notifications', True)
            self.show_notifications.set(show_notifications)
            
        # System tray ayarını yükle
        if hasattr(self, 'minimize_to_tray'):
            minimize_to_tray = self.config_manager.get_setting('minimize_to_tray', False)
            self.minimize_to_tray.set(minimize_to_tray)
            # Eğer ayar açıksa tray'i kurulum yap
            if minimize_to_tray:
                self.on_tray_setting_change()
    
    def on_dpi_tool_change(self):
        """DPI aracı değiştirildiğinde"""
        try:
            selected_tool = self.dpi_tool_var.get()
            
            # Eğer DPI bypass aktifse, önce durdur
            was_active = self.bypass_active
            if was_active:
                self.stop_bypass()
                
            # Yeni aracı config'e kaydet
            self.config_manager.set_dpi_tool(selected_tool)
            
            # Ayarlar sayfası title'ını güncelle
            self.update_settings_title()
            
            # Durumu güncelle
            self.update_status()
            
            # Bilgi mesajı göster
            tool_names = {'goodbyedpi': 'GoodbyeDPI', 'zapret': 'Zapret'}
            tool_name = tool_names.get(selected_tool, selected_tool)
            
            # Araç durumunu kontrol et
            tools = self.dpi_bypass.get_available_tools()
            tool_info = tools.get(selected_tool, {})
            
            # Başarı mesajı
            status_msg = "✅ Mevcut" if tool_info.get('available') else "🔄 İlk kullanımda indirilecek"
            messagebox.showinfo("DPI Aracı Değişti", 
                f"DPI aracı {tool_name} olarak ayarlandı.\n"
                f"{status_msg}")
            
            # Eğer daha önce aktifse, yeni araçla yeniden başlat
            if was_active:
                self.root.after(1000, self.start_bypass)  # 1 saniye bekle
                
        except Exception as e:
            messagebox.showerror("Hata", f"DPI aracı değiştirilemedi: {e}")
    
    def update_settings_title(self):
        """Ayarlar sayfası title'ını güncelle"""
        if hasattr(self, 'settings_frame') and self.current_page == 'settings':
            # Title frame'i bul ve güncelle
            for child in self.settings_frame.winfo_children():
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Label) and "⚙️ Ayarlar" in grandchild.cget("text"):
                            current_tool = self.config_manager.get_dpi_tool().title()
                            new_title = f"⚙️ Ayarlar - {current_tool}"
                            grandchild.configure(text=new_title)
                            break
    
    def on_tray_setting_change(self):
        """Tray ayarı değiştiğinde"""
        # Ayarı kaydet
        self.config_manager.set_setting('minimize_to_tray', self.minimize_to_tray.get())
        self.config_manager.save_config()
        
        if self.minimize_to_tray.get():
            # İlk kez açıldığında tray'i kurulumla
            if not self.tray_icon:
                self.setup_tray()
                # Tray icon'u background thread'de başlat
                tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
                tray_thread.start()
            # self.log("📌 System tray desteği etkinleştirildi")
        else:
            # Tray icon'u kapat
            if self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
            # self.log("📌 System tray desteği devre dışı bırakıldı")
    
    def create_tray_icon(self):
        """System tray icon oluştur"""
        # Basit bir ikon oluştur (32x32 mavi daire)
        image = Image.new('RGBA', (32, 32), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([2, 2, 30, 30], fill=(0, 217, 255, 255))  # Mavi daire
        draw.ellipse([8, 8, 24, 24], fill=(15, 15, 15, 255))   # İç kısmı
        draw.text((10, 12), "D", fill=(0, 217, 255, 255))      # D harfi
        
        return image
    
    def setup_tray(self):
        """System tray kurulumu"""
        if self.tray_icon:
            return
            
        icon_image = self.create_tray_icon()
        
        def get_menu():
            """Dinamik menü oluştur"""
            status_text = "🟢 Bypass Aktif" if self.bypass_active else "🔴 Bypass Pasif"
            return pystray.Menu(
                pystray.MenuItem("NetLan Guardian", self.show_window, default=True),
                pystray.MenuItem("Göster", self.show_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(status_text, None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Çıkış", self.quit_app)
            )
        
        self.tray_icon = pystray.Icon(
            "NetLan_Guardian",
            icon_image,
            "NetLan Guardian - Tray'de çalışıyor",
            menu=get_menu()
        )
    
    def update_tray_menu(self):
        """Tray menüsünü güncelle"""
        if self.tray_icon:
            status_text = "🟢 Bypass Aktif" if self.bypass_active else "🔴 Bypass Pasif"
            new_menu = pystray.Menu(
                pystray.MenuItem("NetLan Guardian", self.show_window, default=True),
                pystray.MenuItem("Göster", self.show_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem(status_text, None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Çıkış", self.quit_app)
            )
            self.tray_icon.menu = new_menu
    
    def show_window(self, icon=None, item=None):
        """Pencereyi göster"""
        if self.in_tray:
            self.root.deiconify()
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after_idle(self.root.attributes, '-topmost', False)
            self.in_tray = False
    
    def hide_to_tray(self):
        """System tray'e gizle"""
        if not self.minimize_to_tray.get():
            return False
            
        if not self.tray_icon:
            self.setup_tray()
            # Tray icon'u background thread'de başlat
            tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            tray_thread.start()
        
        self.root.withdraw()  # Pencereyi gizle
        self.in_tray = True
        return True
    
    def quit_app(self, icon=None, item=None):
        """Uygulamayı tamamen kapat"""
        try:
            print("🛑 Uygulama tamamen kapatılıyor...")
            
            # DPI bypass aktifse durdur
            if hasattr(self, 'bypass_active') and self.bypass_active:
                print("🛑 DPI bypass durduruluyor...")
                if hasattr(self, 'dpi_bypass'):
                    self.dpi_bypass.stop_bypass()
                self.bypass_active = False
                print("✅ DPI bypass durduruldu")
            
            # Tray icon'u durdur
            if hasattr(self, 'tray_icon') and self.tray_icon:
                print("🛑 Tray icon durduruluyor...")
                self.tray_icon.stop()
                self.tray_icon = None
                print("✅ Tray icon durduruldu")
            
            # Tkinter penceresini kapat
            if hasattr(self, 'root'):
                self.root.quit()  # Mainloop'u sonlandır
                self.root.destroy()  # Pencereyi yok et
                print("✅ GUI penceresi kapatıldı")
                
        except Exception as e:
            print(f"❌ Kapatma sırasında hata: {e}")
        finally:
            # Python processini tamamen sonlandır
            print("🛑 Python process sonlandırılıyor...")
            os._exit(0)  # Zorla çık
    
    def on_closing(self):
        """Uygulama kapatılırken (pencere kapatma tuşu ile)"""
        try:
            # Eğer tray'e küçültme aktifse, sadece tray'e gizle
            if hasattr(self, 'minimize_to_tray') and self.minimize_to_tray.get():
                if self.hide_to_tray():
                    return  # Kapatma işlemini durdur
            
            # Normal kapatma işlemi (tray'den değilse)
            self.quit_app()
            
        except Exception as e:
            print(f"Kapatma işlemi sırasında hata: {e}")
            # Hata olsa bile pencereyi zorla kapat
            try:
                self.root.destroy()
                os._exit(0)
            except:
                pass
    
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

# Geriye uyumluluk için alias
ModernDPIGUI = UltraModernDPIGUI

def main():
    """Ana fonksiyon"""
    try:
        app = UltraModernDPIGUI()
        app.run()
    except Exception as e:
        print(f"GUI başlatma hatası: {e}")
        messagebox.showerror("Hata", f"GUI başlatılamadı: {e}")

if __name__ == "__main__":
    main()
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NetLan Guardian")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Modern tema renkleri
        self.colors = {
            'primary': '#2C3E50',      # Koyu mavi
            'secondary': '#3498DB',     # Açık mavi
            'success': '#27AE60',       # Yeşil
            'danger': '#E74C3C',        # Kırmızı
            'warning': '#F39C12',       # Turuncu
            'dark': '#1A252F',          # Çok koyu mavi
            'light': '#ECF0F1',         # Açık gri
            'white': '#FFFFFF',
            'text_primary': '#2C3E50',
            'text_secondary': '#7F8C8D'
        }
        
        # Uygulama durumu
        self.bypass_active = False
        self.dpi_bypass = DPIBypass()
        self.config_manager = ConfigManager()
        
        self.setup_styles()
        self.create_main_layout()
        self.load_config()
        
    def setup_styles(self):
        """Modern stilleri ayarla"""
        self.root.configure(bg=self.colors['light'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ana buton stilleri
        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0,
                       focuscolor='none')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['secondary']),
                           ('pressed', self.colors['dark'])])
        
    def create_main_layout(self):
        """Ana layout'u oluştur"""
        # Ana frame
        main_frame = tk.Frame(self.root, bg=self.colors['light'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Başlık
        self.create_header(main_frame)
        
        # İçerik alanı
        content_frame = tk.Frame(main_frame, bg=self.colors['light'])
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Sol panel - Platform butonları
        self.create_platform_panel(content_frame)
        
        # Orta panel - Ana kontroller
        self.create_control_panel(content_frame)
        
        # Sağ panel - Durum ve log
        self.create_status_panel(content_frame)
        
    def create_header(self, parent):
        """Başlık bölümünü oluştur"""
        header_frame = tk.Frame(parent, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)
        
        # Logo ve başlık
        title_label = tk.Label(header_frame,
                              text="🌐 NetLan Guardian",
                              font=('Segoe UI', 24, 'bold'),
                              bg=self.colors['primary'],
                              fg=self.colors['white'])
        title_label.pack(side='left', padx=20, pady=20)
        
        # Sağ taraf frame (sürüm ve güncelleme butonu için)
        right_frame = tk.Frame(header_frame, bg=self.colors['primary'])
        right_frame.pack(side='right', padx=20, pady=10)
        
        # Güncelleme butonu
        update_btn = tk.Button(right_frame,
                              text="🔄 Güncelle",
                              font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['accent_primary'],
                              fg=self.colors['text_primary'],
                              activebackground=self.colors['accent_secondary'],
                              activeforeground=self.colors['text_primary'],
                              relief='flat',
                              padx=15,
                              pady=5,
                              cursor='hand2',
                              command=self.check_for_updates)
        update_btn.pack(side='top', pady=2)
        
        # Sürüm bilgisi
        version_label = tk.Label(right_frame,
                                text=f"v{self.current_version}",
                                font=('Segoe UI', 10),
                                bg=self.colors['primary'],
                                fg=self.colors['light'])
        version_label.pack(side='top', pady=2)
        
    def create_platform_panel(self, parent):
        """Platform butonları panelini oluştur"""
        platform_frame = tk.LabelFrame(parent,
                                      text="🚀 Hızlı Platform Erişimi",
                                      font=('Segoe UI', 12, 'bold'),
                                      bg=self.colors['light'],
                                      fg=self.colors['text_primary'],
                                      relief='solid',
                                      borderwidth=1)
        platform_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Platform butonları
        platforms = [
            ("🎮 Discord", "discord.com", "#5865F2"),
            ("🎲 Roblox", "roblox.com", "#00A2FF"),
            ("📝 Pastebin", "pastebin.com", "#02A9F1"),
            ("📺 YouTube", "youtube.com", "#FF0000"),
            ("🐦 Twitter/X", "twitter.com", "#1DA1F2"),
            ("📘 Facebook", "facebook.com", "#1877F2"),
            ("📷 Instagram", "instagram.com", "#E4405F"),
            ("🎬 Netflix", "netflix.com", "#E50914"),
            ("🎵 Spotify", "spotify.com", "#1ED760"),
            ("💻 GitHub", "github.com", "#181717")
        ]
        
        for i, (name, url, color) in enumerate(platforms):
            btn = tk.Button(platform_frame,
                           text=name,
                           font=('Segoe UI', 10, 'bold'),
                           bg=color,
                           fg='white',
                           activebackground=color,
                           activeforeground='white',
                           relief='flat',
                           cursor='hand2',
                           width=20,
                           command=lambda u=url: self.add_platform_site(u))
            btn.pack(pady=5, padx=10, fill='x')
            
            # Hover efekti
            def on_enter(e, button=btn, original_color=color):
                button.configure(bg=self.lighten_color(original_color))
                
            def on_leave(e, button=btn, original_color=color):
                button.configure(bg=original_color)
                
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            
    def lighten_color(self, color):
        """Rengi açar"""
        # Basit renk açma işlemi
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(min(255, int(c * 1.2)) for c in rgb)
        return f"#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}"
        
    def create_control_panel(self, parent):
        """Ana kontrol panelini oluştur"""
        control_frame = tk.LabelFrame(parent,
                                     text="⚙️ DPI Bypass Kontrolü",
                                     font=('Segoe UI', 12, 'bold'),
                                     bg=self.colors['light'],
                                     fg=self.colors['text_primary'],
                                     relief='solid',
                                     borderwidth=1)
        control_frame.pack(side='left', fill='both', expand=True, padx=10)
        
        # Durum göstergesi
        status_frame = tk.Frame(control_frame, bg=self.colors['light'])
        status_frame.pack(fill='x', pady=10)
        
        tk.Label(status_frame,
                text="Durum:",
                font=('Segoe UI', 12, 'bold'),
                bg=self.colors['light'],
                fg=self.colors['text_primary']).pack(side='left')
        
        self.status_indicator = tk.Label(status_frame,
                                       text="●",
                                       font=('Segoe UI', 20),
                                       bg=self.colors['light'],
                                       fg=self.colors['danger'])
        self.status_indicator.pack(side='left', padx=10)
        
        self.status_text = tk.Label(status_frame,
                                  text="Devre Dışı",
                                  font=('Segoe UI', 12, 'bold'),
                                  bg=self.colors['light'],
                                  fg=self.colors['danger'])
        self.status_text.pack(side='left')
        
        # Ana butonlar
        button_frame = tk.Frame(control_frame, bg=self.colors['light'])
        button_frame.pack(fill='x', pady=20)
        
        self.start_button = tk.Button(button_frame,
                                    text="🚀 DPI Bypass'ı Başlat",
                                    font=('Segoe UI', 12, 'bold'),
                                    bg=self.colors['success'],
                                    fg='white',
                                    activebackground=self.colors['success'],
                                    relief='flat',
                                    cursor='hand2',
                                    height=2,
                                    command=self.start_bypass)
        self.start_button.pack(side='left', fill='x', expand=True, padx=5)
        
        self.stop_button = tk.Button(button_frame,
                                   text="⏹️ Durdur",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg=self.colors['danger'],
                                   fg='white',
                                   activebackground=self.colors['danger'],
                                   relief='flat',
                                   cursor='hand2',
                                   height=2,
                                   state='disabled',
                                   command=self.stop_bypass)
        self.stop_button.pack(side='right', fill='x', expand=True, padx=5)
        
        # Site yönetimi
        site_frame = tk.LabelFrame(control_frame,
                                 text="🌐 Site Yönetimi",
                                 font=('Segoe UI', 11, 'bold'),
                                 bg=self.colors['light'],
                                 fg=self.colors['text_primary'])
        site_frame.pack(fill='both', expand=True, pady=10)
        
        # Site listesi
        list_frame = tk.Frame(site_frame, bg=self.colors['light'])
        list_frame.pack(fill='both', expand=True, pady=5)
        
        # Scrollbar ile listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.site_listbox = tk.Listbox(list_frame,
                                     yscrollcommand=scrollbar.set,
                                     font=('Segoe UI', 10),
                                     bg='white',
                                     selectbackground=self.colors['secondary'],
                                     relief='solid',
                                     borderwidth=1)
        self.site_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.site_listbox.yview)
        
        # Site ekleme/çıkarma butonları
        site_button_frame = tk.Frame(site_frame, bg=self.colors['light'])
        site_button_frame.pack(fill='x', pady=5)
        
        tk.Button(site_button_frame,
                 text="➕ Site Ekle",
                 font=('Segoe UI', 9),
                 bg=self.colors['secondary'],
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 command=self.add_site).pack(side='left', padx=2, fill='x', expand=True)
        
        tk.Button(site_button_frame,
                 text="➖ Site Çıkar",
                 font=('Segoe UI', 9),
                 bg=self.colors['warning'],
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 command=self.remove_site).pack(side='right', padx=2, fill='x', expand=True)
                 
    def create_status_panel(self, parent):
        """Durum ve log panelini oluştur"""
        status_frame = tk.LabelFrame(parent,
                                   text="📊 Durum & Loglar",
                                   font=('Segoe UI', 12, 'bold'),
                                   bg=self.colors['light'],
                                   fg=self.colors['text_primary'],
                                   relief='solid',
                                   borderwidth=1)
        status_frame.pack(side='right', fill='y', padx=(10, 0))
        
        # İstatistikler
        stats_frame = tk.Frame(status_frame, bg=self.colors['light'])
        stats_frame.pack(fill='x', pady=10)
        
        tk.Label(stats_frame,
                text="📈 İstatistikler",
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['light'],
                fg=self.colors['text_primary']).pack(anchor='w')
        
        self.stats_text = tk.Text(stats_frame,
                                height=8,
                                width=30,
                                font=('Segoe UI', 9),
                                bg='white',
                                relief='solid',
                                borderwidth=1,
                                state='disabled')
        self.stats_text.pack(fill='x', pady=5)
        
        # Log alanı
        tk.Label(status_frame,
                text="📝 Log Mesajları",
                font=('Segoe UI', 11, 'bold'),
                bg=self.colors['light'],
                fg=self.colors['text_primary']).pack(anchor='w', pady=(10, 0))
        
        log_frame = tk.Frame(status_frame, bg=self.colors['light'])
        log_frame.pack(fill='both', expand=True, pady=5)
        
        log_scrollbar = ttk.Scrollbar(log_frame)
        log_scrollbar.pack(side='right', fill='y')
        
        self.log_text = tk.Text(log_frame,
                              yscrollcommand=log_scrollbar.set,
                              font=('Consolas', 9),
                              bg='#1E1E1E',
                              fg='#00FF00',
                              relief='solid',
                              borderwidth=1,
                              state='disabled')
        self.log_text.pack(side='left', fill='both', expand=True)
        log_scrollbar.config(command=self.log_text.yview)
        
        # Alt butonlar
        bottom_frame = tk.Frame(status_frame, bg=self.colors['light'])
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(bottom_frame,
                 text="🗑️ Logları Temizle",
                 font=('Segoe UI', 9),
                 bg=self.colors['warning'],
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 command=self.clear_logs).pack(fill='x', pady=2)
        
        tk.Button(bottom_frame,
                 text="💾 Config Kaydet",
                 font=('Segoe UI', 9),
                 bg=self.colors['primary'],
                 fg='white',
                 relief='flat',
                 cursor='hand2',
                 command=self.save_config).pack(fill='x', pady=2)
        
    def add_platform_site(self, domain):
        """Platform sitesini bypass listesine ekle"""
        sites = self.config_manager.get_bypass_sites()
        if domain not in sites:
            sites.append(domain)
            self.config_manager.update_bypass_sites(sites)
            self.update_site_list()
            self.log(f"✅ {domain} bypass listesine eklendi")
            
            # Eğer bypass aktifse, yeniden başlat
            if self.bypass_active:
                self.log("♻️ Bypass yeniden başlatılıyor...")
                threading.Thread(target=self._restart_bypass, daemon=True).start()
        else:
            self.log(f"ℹ️ {domain} zaten listede mevcut")
            
    def _restart_bypass(self):
        """Bypass'ı yeniden başlat"""
        self.dpi_bypass.stop_bypass()
        time.sleep(2)
        self.dpi_bypass.start_bypass()
        
    def add_site(self):
        """Manuel site ekleme"""
        site = simpledialog.askstring("Site Ekle", "Site adresini girin (örn: example.com):")
        if site:
            site = site.strip().replace('https://', '').replace('http://', '').replace('www.', '')
            if '/' in site:
                site = site.split('/')[0]
            self.add_platform_site(site)
            
    def remove_site(self):
        """Site çıkarma"""
        selection = self.site_listbox.curselection()
        if selection:
            site = self.site_listbox.get(selection[0])
            sites = self.config_manager.get_bypass_sites()
            if site in sites:
                sites.remove(site)
                self.config_manager.update_bypass_sites(sites)
                self.update_site_list()
                self.log(f"❌ {site} bypass listesinden çıkarıldı")
                
                # Eğer bypass aktifse, yeniden başlat
                if self.bypass_active:
                    self.log("♻️ Bypass yeniden başlatılıyor...")
                    threading.Thread(target=self._restart_bypass, daemon=True).start()
                    
    def start_bypass(self):
        """DPI Bypass başlat"""
        if not self.bypass_active:
            self.log("🚀 DPI Bypass başlatılıyor...")
            threading.Thread(target=self._start_bypass_thread, daemon=True).start()
            
    def _start_bypass_thread(self):
        """Bypass başlatma thread'i"""
        try:
            self.dpi_bypass.start_bypass()
            self.bypass_active = True
            
            # UI güncelle
            self.root.after(0, self._update_ui_started)
            self.log("✅ DPI Bypass başarıyla başlatıldı!")
            
        except Exception as e:
            self.log(f"❌ Hata: {str(e)}")
            self.root.after(0, self._update_ui_error)
            
    def _update_ui_started(self):
        """UI'yi başlatılmış duruma güncelle"""
        self.status_indicator.configure(fg=self.colors['success'])
        self.status_text.configure(text="Aktif", fg=self.colors['success'])
        self.start_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        
        # Tray menüsünü güncelle
        self.update_tray_menu()
        
    def stop_bypass(self):
        """DPI Bypass durdur"""
        if self.bypass_active:
            self.log("⏹️ DPI Bypass durduruluyor...")
            threading.Thread(target=self._stop_bypass_thread, daemon=True).start()
            
    def _stop_bypass_thread(self):
        """Bypass durdurma thread'i"""
        try:
            self.dpi_bypass.stop_bypass()
            self.bypass_active = False
            
            # UI güncelle
            self.root.after(0, self._update_ui_stopped)
            self.log("✅ DPI Bypass durduruldu")
            
        except Exception as e:
            self.log(f"❌ Durdurma hatası: {str(e)}")
            
    def _update_ui_stopped(self):
        """UI'yi durdurulmuş duruma güncelle"""
        self.status_indicator.configure(fg=self.colors['danger'])
        self.status_text.configure(text="Devre Dışı", fg=self.colors['danger'])
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        
        # Tray menüsünü güncelle
        self.update_tray_menu()
        
    def _update_ui_error(self):
        """UI'yi hata durumuna güncelle"""
        self.status_indicator.configure(fg=self.colors['warning'])
        self.status_text.configure(text="Hata", fg=self.colors['warning'])
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        
    def update_site_list(self):
        """Site listesini güncelle"""
        self.site_listbox.delete(0, tk.END)
        sites = self.config_manager.get_bypass_sites()
        for site in sites:
            self.site_listbox.insert(tk.END, site)
            
    def load_config(self):
        """Konfigürasyonu yükle"""
        self.update_site_list()
        self.update_stats()
        
    def update_stats(self):
        """İstatistikleri güncelle"""
        sites = self.config_manager.get_bypass_sites()
        stats_text = f"Toplam Site: {len(sites)}\n"
        stats_text += f"Durum: {'Aktif' if self.bypass_active else 'Devre Dışı'}\n"
        stats_text += f"Çalışma Süresi: {self.get_uptime()}\n"
        
        self.stats_text.configure(state='normal')
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.configure(state='disabled')
        
        # Her 5 saniyede güncelle
        self.root.after(5000, self.update_stats)
        
    def get_uptime(self):
        """Çalışma süresini hesapla"""
        # Basit uptime hesabı
        return "00:00:00"  # Placeholder
        
    def log(self, message):
        """Log mesajı ekle"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
        
    def clear_logs(self):
        """Logları temizle"""
        self.log_text.configure(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.configure(state='disabled')
        
    def save_config(self):
        """Konfigürasyonu kaydet"""
        self.config_manager.save_config()
        self.log("💾 Konfigürasyon kaydedildi")
        messagebox.showinfo("Bilgi", "Konfigürasyon başarıyla kaydedildi!")
    
    def check_for_updates(self):
        """Güncelleme kontrolü yap"""
        def update_check_thread():
            try:
                self.log("🔍 Güncelleme kontrol ediliyor...")
                update_available, latest_version = self.update_manager.check_for_updates(show_progress=False)
                
                if update_available:
                    self.log(f"🎉 Yeni güncelleme bulundu: v{latest_version}")
                    
                    # Ana thread'de messagebox göster
                    self.root.after(0, lambda: self.show_update_dialog(latest_version))
                else:
                    self.log("✅ Program zaten güncel!")
                    self.root.after(0, lambda: messagebox.showinfo("Güncelleme", "Program zaten güncel!"))
                    
            except Exception as e:
                error_msg = f"❌ Güncelleme kontrolü başarısız: {str(e)}"
                self.log(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Hata", error_msg))
        
        # Arka planda kontrol et
        thread = threading.Thread(target=update_check_thread, daemon=True)
        thread.start()
    
    def show_update_dialog(self, latest_version):
        """Güncelleme dialog'unu göster"""
        response = messagebox.askyesno(
            "Güncelleme Mevcut",
            f"Yeni sürüm mevcut: v{latest_version}\n"
            f"Mevcut sürüm: v{self.current_version}\n\n"
            f"Şimdi güncellemek istiyor musunuz?",
            icon='question'
        )
        
        if response:
            self.download_and_install_update()
    
    def download_and_install_update(self):
        """Güncellemeyi indir ve yükle"""
        def download_thread():
            try:
                self.log("📥 Güncelleme indiriliyor...")
                
                # İndir
                update_file = self.update_manager.download_update()
                
                if update_file:
                    self.log("✅ İndirme tamamlandı!")
                    self.log("🔧 Güncelleme yükleniyor...")
                    
                    # Yükle
                    success = self.update_manager.install_update(update_file)
                    
                    if success:
                        self.log("🎉 Güncelleme başarıyla yüklendi!")
                        self.root.after(0, lambda: messagebox.showinfo(
                            "Başarılı", 
                            "Güncelleme başarıyla yüklendi!\nProgram yeniden başlatılacak."
                        ))
                    else:
                        self.log("❌ Güncelleme yüklenemedi!")
                        self.root.after(0, lambda: messagebox.showerror(
                            "Hata", 
                            "Güncelleme yüklenemedi!"
                        ))
                else:
                    self.log("❌ Güncelleme indirilemedi!")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Hata", 
                        "Güncelleme indirilemedi!"
                    ))
                    
            except Exception as e:
                error_msg = f"❌ Güncelleme hatası: {str(e)}"
                self.log(error_msg)
                self.root.after(0, lambda: messagebox.showerror("Hata", error_msg))
        
        # Arka planda indir ve yükle
        thread = threading.Thread(target=download_thread, daemon=True)
        thread.start()
        
    def on_closing(self):
        """Uygulama kapatılırken"""
        # Eğer tray'e küçültme aktifse, sadece tray'e gizle
        if hasattr(self, 'minimize_to_tray') and self.minimize_to_tray.get():
            if self.hide_to_tray():
                return  # Kapatma işlemini durdur
        
        # Normal kapatma işlemi
        if self.bypass_active:
            self.log("🔄 Uygulama kapatılıyor, bypass durduruluyor...")
            self.dpi_bypass.stop_bypass()
        
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.stop()
            
        self.root.destroy()
        
    def run(self):
        """Uygulamayı çalıştır"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # İlk log mesajı
        self.log("🎉 NetLan Guardian başlatıldı!")
        self.log("ℹ️ Soldan platform butonlarını kullanarak hızlı site ekleyebilirsiniz")
        
        self.root.mainloop()

def main():
    """Ana fonksiyon"""
    try:
        app = ModernDPIGUI()
        app.run()
    except Exception as e:
        print(f"GUI başlatma hatası: {e}")
        messagebox.showerror("Hata", f"GUI başlatılamadı: {e}")

if __name__ == "__main__":
    main()
