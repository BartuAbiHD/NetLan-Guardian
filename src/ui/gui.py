#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Graphical User Interface
DPI Bypass programı için grafik arayüzü
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

import threading
import time
from datetime import datetime

class DPIGUI:
    def __init__(self, config_manager, dpi_bypass):
        if not TKINTER_AVAILABLE:
            raise ImportError("Tkinter modülü bulunamadı")
            
        self.config = config_manager
        self.dpi = dpi_bypass
        self.root = None
        self.status_var = None
        self.log_text = None
        self.site_listbox = None
        self.ip_listbox = None
        self.running = False
        self.update_job = None  # Auto update job ID'si
        
    def create_main_window(self):
        """Ana pencereyi oluştur"""
        self.root = tk.Tk()
        self.root.title("DPI Bypass Tool - GUI Mode")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Ana stil ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        
        self.create_menu()
        self.create_tabs()
        self.update_status()
        
        # Otomatik durum güncelleme - güvenli şekilde
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.update_job = self.root.after(2000, self.auto_update)
        
    def create_menu(self):
        """Menü çubuğunu oluştur"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Dosya menüsü
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Dosya", menu=file_menu)
        file_menu.add_command(label="Konfigürasyonu Dışa Aktar", command=self.export_config)
        file_menu.add_command(label="Konfigürasyonu İçe Aktar", command=self.import_config)
        file_menu.add_separator()
        file_menu.add_command(label="Çıkış", command=self.on_closing)
        
        # Araçlar menüsü
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Araçlar", menu=tools_menu)
        tools_menu.add_command(label="Bağlantı Testi", command=self.test_connections)
        tools_menu.add_command(label="Logları Temizle", command=self.clear_logs)
        tools_menu.add_command(label="Konfigürasyonu Sıfırla", command=self.reset_config)
        
        # Yardım menüsü
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Yardım", menu=help_menu)
        help_menu.add_command(label="Hakkında", command=self.show_about)
        
    def create_tabs(self):
        """Sekmeleri oluştur"""
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Ana kontrol sekmesi
        self.create_main_tab(notebook)
        
        # Site yönetimi sekmesi
        self.create_sites_tab(notebook)
        
        # IP yönetimi sekmesi  
        self.create_ips_tab(notebook)
        
        # Teknik ayarları sekmesi
        self.create_techniques_tab(notebook)
        
        # Log sekmesi
        self.create_logs_tab(notebook)
        
    def create_main_tab(self, notebook):
        """Ana kontrol sekmesi"""
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Ana Kontrol")
        
        # Başlık
        title_label = ttk.Label(main_frame, text="DPI Bypass Tool", style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Durum çerçevesi
        status_frame = ttk.LabelFrame(main_frame, text="Durum", padding=10)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        self.status_var = tk.StringVar(value="🔴 Durduruldu")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Arial', 12))
        status_label.pack()
        
        # Kontrol butonları
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Başlat", command=self.toggle_bypass)
        self.start_button.pack(side='left', padx=10)
        
        refresh_button = ttk.Button(button_frame, text="Yenile", command=self.refresh_data)
        refresh_button.pack(side='left', padx=10)
        
        # İstatistikler çerçevesi
        stats_frame = ttk.LabelFrame(main_frame, text="İstatistikler", padding=10)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, wrap='word', state='disabled')
        self.stats_text.pack(fill='both', expand=True)
        
        scrollbar_stats = ttk.Scrollbar(stats_frame, orient="vertical", command=self.stats_text.yview)
        scrollbar_stats.pack(side='right', fill='y')
        self.stats_text.configure(yscrollcommand=scrollbar_stats.set)
        
    def create_sites_tab(self, notebook):
        """Site yönetimi sekmesi"""
        sites_frame = ttk.Frame(notebook)
        notebook.add(sites_frame, text="Site Yönetimi")
        
        # İzin verilen siteler
        allowed_frame = ttk.LabelFrame(sites_frame, text="İzin Verilen Siteler", padding=10)
        allowed_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Site listesi
        list_frame = ttk.Frame(allowed_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.site_listbox = tk.Listbox(list_frame)
        self.site_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar_sites = ttk.Scrollbar(list_frame, orient="vertical", command=self.site_listbox.yview)
        scrollbar_sites.pack(side='right', fill='y')
        self.site_listbox.configure(yscrollcommand=scrollbar_sites.set)
        
        # Site ekleme/çıkarma
        site_control_frame = ttk.Frame(allowed_frame)
        site_control_frame.pack(fill='x', pady=10)
        
        self.site_entry = ttk.Entry(site_control_frame)
        self.site_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Placeholder text için bind eventi
        self.site_entry.insert(0, "Site adı girin...")
        self.site_entry.bind('<FocusIn>', self.on_site_entry_focus_in)
        self.site_entry.bind('<FocusOut>', self.on_site_entry_focus_out)
        self.site_entry.config(foreground='grey')
        
        add_site_button = ttk.Button(site_control_frame, text="Ekle", command=self.add_site)
        add_site_button.pack(side='right', padx=(5, 0))
        
        remove_site_button = ttk.Button(site_control_frame, text="Sil", command=self.remove_site)
        remove_site_button.pack(side='right')
        
        # Engellenmiş siteler
        blocked_frame = ttk.LabelFrame(sites_frame, text="Engellenmiş Siteler", padding=10)
        blocked_frame.pack(fill='x', padx=20, pady=10)
        
        # Engellenmiş site listesi ve kaydırma çubuğu için frame
        blocked_list_frame = ttk.Frame(blocked_frame)
        blocked_list_frame.pack(fill='x')
        
        self.blocked_listbox = tk.Listbox(blocked_list_frame, height=5)
        self.blocked_listbox.pack(side='left', fill='x', expand=True)
        
        scrollbar_blocked = ttk.Scrollbar(blocked_list_frame, orient="vertical", command=self.blocked_listbox.yview)
        scrollbar_blocked.pack(side='right', fill='y')
        self.blocked_listbox.configure(yscrollcommand=scrollbar_blocked.set)
        
        # Engellenmiş site kontrolleri
        blocked_control_frame = ttk.Frame(blocked_frame)
        blocked_control_frame.pack(fill='x', pady=10)
        
        add_blocked_button = ttk.Button(blocked_control_frame, text="Engellenene Ekle", command=self.add_blocked_site)
        add_blocked_button.pack(side='left', padx=(0, 5))
        
        remove_blocked_button = ttk.Button(blocked_control_frame, text="Engellenenden Sil", command=self.remove_blocked_site)
        remove_blocked_button.pack(side='left')
        
    def create_ips_tab(self, notebook):
        """IP yönetimi sekmesi"""
        ips_frame = ttk.Frame(notebook)
        notebook.add(ips_frame, text="IP Yönetimi")
        
        # IP listesi
        ip_list_frame = ttk.LabelFrame(ips_frame, text="İzin Verilen IP Adresleri", padding=10)
        ip_list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        list_frame = ttk.Frame(ip_list_frame)
        list_frame.pack(fill='both', expand=True)
        
        self.ip_listbox = tk.Listbox(list_frame)
        self.ip_listbox.pack(side='left', fill='both', expand=True)
        
        scrollbar_ips = ttk.Scrollbar(list_frame, orient="vertical", command=self.ip_listbox.yview)
        scrollbar_ips.pack(side='right', fill='y')
        self.ip_listbox.configure(yscrollcommand=scrollbar_ips.set)
        
        # IP ekleme/çıkarma
        ip_control_frame = ttk.Frame(ip_list_frame)
        ip_control_frame.pack(fill='x', pady=10)
        
        self.ip_entry = ttk.Entry(ip_control_frame)
        self.ip_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        # Placeholder text için bind eventi
        self.ip_entry.insert(0, "IP adresi girin...")
        self.ip_entry.bind('<FocusIn>', self.on_ip_entry_focus_in)
        self.ip_entry.bind('<FocusOut>', self.on_ip_entry_focus_out)
        self.ip_entry.config(foreground='grey')
        
        add_ip_button = ttk.Button(ip_control_frame, text="Ekle", command=self.add_ip)
        add_ip_button.pack(side='right', padx=(5, 0))
        
        remove_ip_button = ttk.Button(ip_control_frame, text="Sil", command=self.remove_ip)
        remove_ip_button.pack(side='right')
        
    def create_techniques_tab(self, notebook):
        """Teknik ayarları sekmesi"""
        techniques_frame = ttk.Frame(notebook)
        notebook.add(techniques_frame, text="Teknik Ayarları")
        
        # Teknikler listesi
        self.technique_vars = {}
        techniques = {
            'fragment_packets': 'Paket Parçalama',
            'modify_ttl': 'TTL Modifikasyonu',
            'fake_packets': 'Sahte Paket Gönderimi',
            'domain_fronting_proxy': 'Domain Fronting Proxy'
        }
        
        techniques_list_frame = ttk.LabelFrame(techniques_frame, text="DPI Bypass Teknikleri", padding=20)
        techniques_list_frame.pack(fill='x', padx=20, pady=10)
        
        for tech_key, tech_name in techniques.items():
            var = tk.BooleanVar()
            self.technique_vars[tech_key] = var
            
            checkbox = ttk.Checkbutton(
                techniques_list_frame,
                text=tech_name,
                variable=var,
                command=lambda tk=tech_key: self.toggle_technique(tk)
            )
            checkbox.pack(anchor='w', pady=5)
            
        # Ayarlar
        settings_frame = ttk.LabelFrame(techniques_frame, text="Genel Ayarlar", padding=20)
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Thread sayısı
        thread_frame = ttk.Frame(settings_frame)
        thread_frame.pack(fill='x', pady=5)
        
        ttk.Label(thread_frame, text="Maksimum Thread Sayısı:").pack(side='left')
        
        self.thread_var = tk.IntVar(value=self.config.get_setting('max_threads', 10))
        thread_spin = ttk.Spinbox(
            thread_frame,
            from_=1,
            to=50,
            textvariable=self.thread_var,
            command=self.update_thread_setting,
            width=10
        )
        thread_spin.pack(side='right')
        
        # Timeout ayarı
        timeout_frame = ttk.Frame(settings_frame)
        timeout_frame.pack(fill='x', pady=5)
        
        ttk.Label(timeout_frame, text="İstek Timeout (saniye):").pack(side='left')
        
        self.timeout_var = tk.IntVar(value=self.config.get_setting('request_timeout', 5))
        timeout_spin = ttk.Spinbox(
            timeout_frame,
            from_=1,
            to=30,
            textvariable=self.timeout_var,
            command=self.update_timeout_setting,
            width=10
        )
        timeout_spin.pack(side='right')
        
    def create_logs_tab(self, notebook):
        """Log sekmesi"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Loglar")
        
        # Log görüntüleme alanı
        log_display_frame = ttk.LabelFrame(logs_frame, text="Sistem Logları", padding=10)
        log_display_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(
            log_display_frame,
            wrap='word',
            height=20,
            state='disabled',
            font=('Courier', 9)
        )
        self.log_text.pack(fill='both', expand=True)
        
        # Log kontrolleri
        log_control_frame = ttk.Frame(logs_frame)
        log_control_frame.pack(fill='x', padx=20, pady=10)
        
        clear_logs_button = ttk.Button(log_control_frame, text="Logları Temizle", command=self.clear_logs)
        clear_logs_button.pack(side='left')
        
        save_logs_button = ttk.Button(log_control_frame, text="Logları Kaydet", command=self.save_logs)
        save_logs_button.pack(side='left', padx=(10, 0))
        
        refresh_logs_button = ttk.Button(log_control_frame, text="Yenile", command=self.refresh_logs)
        refresh_logs_button.pack(side='right')
        
    def toggle_bypass(self):
        """DPI Bypass'ı başlat/durdur"""
        if self.dpi.running:
            threading.Thread(target=self._stop_bypass, daemon=True).start()
        else:
            threading.Thread(target=self._start_bypass, daemon=True).start()
            
    def _start_bypass(self):
        """DPI Bypass başlat (thread içinde)"""
        try:
            if self.dpi.start_bypass():
                self.log_message("✅ DPI Bypass başlatıldı")
                self.root.after(0, lambda: self.start_button.config(text="Durdur"))
            else:
                self.log_message("❌ DPI Bypass başlatılamadı")
        except Exception as e:
            self.log_message(f"❌ Başlatma hatası: {str(e)}")
            
    def _stop_bypass(self):
        """DPI Bypass durdur (thread içinde)"""
        try:
            self.dpi.stop_bypass()
            self.log_message("⏹️ DPI Bypass durduruldu")
            self.root.after(0, lambda: self.start_button.config(text="Başlat"))
        except Exception as e:
            self.log_message(f"❌ Durdurma hatası: {str(e)}")
            
    def add_site(self):
        """Site ekle"""
        site = self.site_entry.get().strip()
        
        # Placeholder text kontrolü
        if not site or site == "Site adı girin...":
            messagebox.showwarning("Uyarı", "Site adı boş olamaz!")
            return
            
        if not self.config.validate_domain(site):
            messagebox.showerror("Hata", "Geçersiz domain formatı!")
            return
            
        if self.config.add_allowed_site(site):
            self.site_entry.delete(0, tk.END)
            self.refresh_sites()
            self.log_message(f"✅ Site eklendi: {site}")
            messagebox.showinfo("Başarılı", f"'{site}' başarıyla eklendi!")
        else:
            messagebox.showwarning("Uyarı", f"'{site}' zaten mevcut!")
            
    def remove_site(self):
        """Seçili siteyi sil"""
        selection = self.site_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Silinecek site seçin!")
            return
            
        site = self.site_listbox.get(selection[0])
        if messagebox.askyesno("Onay", f"'{site}' sitesini silmek istediğinizden emin misiniz?"):
            if self.config.remove_allowed_site(site):
                self.refresh_sites()
                self.log_message(f"🗑️ Site silindi: {site}")
                messagebox.showinfo("Başarılı", f"'{site}' başarıyla silindi!")
                
    def add_ip(self):
        """IP ekle"""
        ip = self.ip_entry.get().strip()
        
        # Placeholder text kontrolü
        if not ip or ip == "IP adresi girin...":
            messagebox.showwarning("Uyarı", "IP adresi boş olamaz!")
            return
            
        if not self.config.validate_ip(ip):
            messagebox.showerror("Hata", "Geçersiz IP adresi formatı!")
            return
            
        if self.config.add_allowed_ip(ip):
            self.ip_entry.delete(0, tk.END)
            self.refresh_ips()
            self.log_message(f"✅ IP eklendi: {ip}")
            messagebox.showinfo("Başarılı", f"'{ip}' başarıyla eklendi!")
        else:
            messagebox.showwarning("Uyarı", f"'{ip}' zaten mevcut!")
            
    def remove_ip(self):
        """Seçili IP'yi sil"""
        selection = self.ip_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Silinecek IP seçin!")
            return
            
        ip = self.ip_listbox.get(selection[0])
        if messagebox.askyesno("Onay", f"'{ip}' IP adresini silmek istediğinizden emin misiniz?"):
            if self.config.remove_allowed_ip(ip):
                self.refresh_ips()
            self.log_message(f"🗑️ IP silindi: {ip}")
            messagebox.showinfo("Başarılı", f"'{ip}' başarıyla silindi!")
            
    def on_site_entry_focus_in(self, event):
        """Site entry focus aldığında placeholder'ı temizle"""
        if self.site_entry.get() == "Site adı girin...":
            self.site_entry.delete(0, tk.END)
            self.site_entry.config(foreground='black')
            
    def on_site_entry_focus_out(self, event):
        """Site entry focus kaybettiğinde placeholder'ı geri getir"""
        if self.site_entry.get() == "":
            self.site_entry.insert(0, "Site adı girin...")
            self.site_entry.config(foreground='grey')
            
    def on_ip_entry_focus_in(self, event):
        """IP entry focus aldığında placeholder'ı temizle"""
        if self.ip_entry.get() == "IP adresi girin...":
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.config(foreground='black')
            
    def on_ip_entry_focus_out(self, event):
        """IP entry focus kaybettiğinde placeholder'ı geri getir"""
        if self.ip_entry.get() == "":
            self.ip_entry.insert(0, "IP adresi girin...")
            self.ip_entry.config(foreground='grey')
            
    def add_blocked_site(self):
        """Engellenmiş sitelere ekle"""
        # Seçili siteyi alıp engellenenlere ekle
        selection = self.site_listbox.curselection()
        if selection:
            site = self.site_listbox.get(selection[0])
            if self.config.add_blocked_site(site):
                self.refresh_sites()
                self.log_message(f"🚫 Site engellenenlere eklendi: {site}")
                messagebox.showinfo("Başarılı", f"'{site}' engellenmiş sitelere eklendi!")
        else:
            # Manuel site adı girme
            site = tk.simpledialog.askstring("Site Engelle", "Engellenecek site adı:")
            if site and self.config.validate_domain(site):
                if self.config.add_blocked_site(site):
                    self.refresh_sites()
                    self.log_message(f"🚫 Site engellenenlere eklendi: {site}")
                    messagebox.showinfo("Başarılı", f"'{site}' engellenmiş sitelere eklendi!")
                else:
                    messagebox.showwarning("Uyarı", f"'{site}' zaten engellenmiş!")
            elif site:
                messagebox.showerror("Hata", "Geçersiz site adı!")
                
    def remove_blocked_site(self):
        """Engellenmiş sitelerden sil"""
        selection = self.blocked_listbox.curselection()
        if not selection:
            messagebox.showwarning("Uyarı", "Silinecek engellenmiş site seçin!")
            return
            
        site = self.blocked_listbox.get(selection[0])
        if messagebox.askyesno("Onay", f"'{site}' sitesini engellenmiş listeden çıkarmak istediğinizden emin misiniz?"):
            if self.config.remove_blocked_site(site):
                self.refresh_sites()
                self.log_message(f"✅ Site engellenmiş listeden çıkarıldı: {site}")
                messagebox.showinfo("Başarılı", f"'{site}' engellenmiş listeden çıkarıldı!")
                
    def toggle_technique(self, technique):
        """Tekniği aç/kapat"""
        status = self.technique_vars[technique].get()
        self.config.set_technique_status(technique, status)
        
        tech_names = {
            'fragment_packets': 'Paket Parçalama',
            'modify_ttl': 'TTL Modifikasyonu',
            'fake_packets': 'Sahte Paket Gönderimi',
            'domain_fronting_proxy': 'Domain Fronting Proxy'
        }
        
        status_text = "aktif" if status else "pasif"
        self.log_message(f"⚙️ {tech_names.get(technique, technique)} {status_text}")
        
    def update_thread_setting(self):
        """Thread sayısı ayarını güncelle"""
        self.config.set_setting('max_threads', self.thread_var.get())
        
    def update_timeout_setting(self):
        """Timeout ayarını güncelle"""
        self.config.set_setting('request_timeout', self.timeout_var.get())
        
    def refresh_data(self):
        """Tüm verileri yenile"""
        self.refresh_sites()
        self.refresh_ips()
        self.refresh_techniques()
        self.refresh_stats()
        self.refresh_logs()
        
    def refresh_sites(self):
        """Site listesini yenile"""
        self.site_listbox.delete(0, tk.END)
        for site in self.config.get_allowed_sites():
            self.site_listbox.insert(tk.END, site)
            
        self.blocked_listbox.delete(0, tk.END)
        for site in self.config.get_blocked_sites():
            self.blocked_listbox.insert(tk.END, site)
            
    def refresh_ips(self):
        """IP listesini yenile"""
        self.ip_listbox.delete(0, tk.END)
        for ip in self.config.get_allowed_ips():
            self.ip_listbox.insert(tk.END, ip)
            
    def refresh_techniques(self):
        """Teknik ayarlarını yenile"""
        for tech_key, var in self.technique_vars.items():
            var.set(self.config.get_technique_status(tech_key))
            
    def refresh_stats(self):
        """İstatistikleri yenile"""
        stats = self.dpi.get_status()
        
        self.stats_text.config(state='normal')
        self.stats_text.delete(1.0, tk.END)
        
        stats_text = f"""
DPI Bypass Durumu: {'🟢 Çalışıyor' if stats['running'] else '🔴 Durduruldu'}
Aktif Thread Sayısı: {stats['active_threads']}

Konfigürasyon:
  📝 İzin verilen site sayısı: {len(self.config.get_allowed_sites())}
  🌐 İzin verilen IP sayısı: {len(self.config.get_allowed_ips())}
  🚫 Engellenmiş site sayısı: {len(self.config.get_blocked_sites())}

Aktif Teknikler:
"""
        
        tech_names = {
            'fragment_packets': 'Paket Parçalama',
            'modify_ttl': 'TTL Modifikasyonu',
            'fake_packets': 'Sahte Paket Gönderimi',
            'domain_fronting_proxy': 'Domain Fronting Proxy'
        }
        
        for tech, enabled in stats['techniques'].items():
            icon = "🟢" if enabled else "🔴"
            stats_text += f"  {icon} {tech_names.get(tech, tech)}\n"
            
        self.stats_text.insert(tk.END, stats_text)
        self.stats_text.config(state='disabled')
        
    def refresh_logs(self):
        """Logları yenile"""
        try:
            with open('logs/dpi_bypass.log', 'r', encoding='utf-8') as f:
                logs = f.read()
                
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, logs)
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        except FileNotFoundError:
            self.log_message("Log dosyası bulunamadı")
        except Exception as e:
            self.log_message(f"Log okuma hatası: {e}")
            
    def log_message(self, message):
        """Log mesajı ekle"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if self.log_text:
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
            
    def clear_logs(self):
        """Logları temizle"""
        if messagebox.askyesno("Onay", "Tüm logları temizlemek istediğinizden emin misiniz?"):
            if self.log_text:
                self.log_text.config(state='normal')
                self.log_text.delete(1.0, tk.END)
                self.log_text.config(state='disabled')
            
            try:
                with open('logs/dpi_bypass.log', 'w', encoding='utf-8') as f:
                    f.write("")
                self.log_message("🧹 Loglar temizlendi")
            except Exception as e:
                messagebox.showerror("Hata", f"Log dosyası temizlenemedi: {e}")
                
    def save_logs(self):
        """Logları dosyaya kaydet"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".log",
            filetypes=[("Log dosyası", "*.log"), ("Metin dosyası", "*.txt"), ("Tüm dosyalar", "*.*")]
        )
        
        if filename:
            try:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Başarılı", f"Loglar '{filename}' dosyasına kaydedildi!")
            except Exception as e:
                messagebox.showerror("Hata", f"Log kaydetme hatası: {e}")
                
    def export_config(self):
        """Konfigürasyonu dışa aktar"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".yaml",
            filetypes=[("YAML dosyası", "*.yaml"), ("JSON dosyası", "*.json"), ("Tüm dosyalar", "*.*")]
        )
        
        if filename:
            if self.config.export_config(filename):
                messagebox.showinfo("Başarılı", f"Konfigürasyon '{filename}' dosyasına kaydedildi!")
                self.log_message(f"📤 Konfigürasyon dışa aktarıldı: {filename}")
            else:
                messagebox.showerror("Hata", "Konfigürasyon dışa aktarılamadı!")
                
    def import_config(self):
        """Konfigürasyonu içe aktar"""
        filename = filedialog.askopenfilename(
            filetypes=[("YAML dosyası", "*.yaml"), ("JSON dosyası", "*.json"), ("Tüm dosyalar", "*.*")]
        )
        
        if filename:
            if self.config.import_config(filename):
                self.refresh_data()
                messagebox.showinfo("Başarılı", f"Konfigürasyon '{filename}' dosyasından yüklendi!")
                self.log_message(f"📥 Konfigürasyon içe aktarıldı: {filename}")
            else:
                messagebox.showerror("Hata", "Konfigürasyon içe aktarılamadı!")
                
    def reset_config(self):
        """Konfigürasyonu sıfırla"""
        if messagebox.askyesno("Onay", "Tüm ayarları sıfırlamak istediğinizden emin misiniz?\nBu işlem geri alınamaz!"):
            self.config.reset_config()
            self.refresh_data()
            messagebox.showinfo("Başarılı", "Konfigürasyon varsayılan değerlere sıfırlandı!")
            self.log_message("🔄 Konfigürasyon sıfırlandı")
            
    def test_connections(self):
        """Bağlantı testi"""
        sites = self.config.get_allowed_sites()
        
        if not sites:
            messagebox.showwarning("Uyarı", "Test edilecek site bulunamadı!")
            return
            
        # Test sonuçlarını gösterecek pencere
        test_window = tk.Toplevel(self.root)
        test_window.title("Bağlantı Testi")
        test_window.geometry("500x400")
        
        result_text = scrolledtext.ScrolledText(test_window, wrap='word')
        result_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        def run_tests():
            try:
                test_window.after(0, lambda: result_text.insert(tk.END, "Bağlantı testleri başlatılıyor...\n\n"))
                
                for site in sites:
                    test_window.after(0, lambda s=site: result_text.insert(tk.END, f"Testing {s}... "))
                    test_window.after(0, lambda: result_text.update_idletasks())
                    
                    try:
                        success = self.dpi.check_connection(site)
                        if success:
                            test_window.after(0, lambda: result_text.insert(tk.END, "✅ Başarılı\n"))
                        else:
                            test_window.after(0, lambda: result_text.insert(tk.END, "❌ Başarısız\n"))
                    except Exception as e:
                        test_window.after(0, lambda: result_text.insert(tk.END, f"❌ Hata: {str(e)}\n"))
                        
                    test_window.after(0, lambda: result_text.see(tk.END))
                    test_window.after(0, lambda: result_text.update_idletasks())
                    
                test_window.after(0, lambda: result_text.insert(tk.END, "\nTest tamamlandı."))
                test_window.after(0, lambda: result_text.update_idletasks())
                
            except Exception as e:
                test_window.after(0, lambda: result_text.insert(tk.END, f"\nTest hatası: {str(e)}"))
            
        threading.Thread(target=run_tests, daemon=True).start()
        
    def show_about(self):
        """Hakkında penceresi"""
        about_text = """
DPI Bypass Tool v1.0

Python ile yazılmış DPI (Deep Packet Inspection) bypass aracı.
GoodbyeDPI ve Zapret benzeri işlevsellik sağlar.

Özellikler:
• Paket parçalama
• TTL modifikasyonu  
• Sahte paket gönderimi
• Domain fronting proxy
• Site ve IP yönetimi
• Grafik ve konsol arayüzü

Geliştirici: AI Assistant
"""
        messagebox.showinfo("Hakkında", about_text)
        
    def update_status(self):
        """Durum güncellemesi"""
        if self.dpi.running:
            self.status_var.set("🟢 Çalışıyor")
            self.start_button.config(text="Durdur")
        else:
            self.status_var.set("🔴 Durduruldu")
            self.start_button.config(text="Başlat")
            
    def auto_update(self):
        """Otomatik güncelleme döngüsü"""
        try:
            if self.running and self.root and self.root.winfo_exists():
                self.update_status()
                # Önceki job'u iptal et
                if self.update_job:
                    self.root.after_cancel(self.update_job)
                # Yeni job planla
                self.update_job = self.root.after(2000, self.auto_update)
        except tk.TclError:
            # Widget destroy edildiyse, update'i durdur
            self.running = False
            
    def on_closing(self):
        """Pencere kapatılırken"""
        # Update job'unu iptal et
        if self.update_job:
            self.root.after_cancel(self.update_job)
            
        if self.dpi.running:
            if messagebox.askyesno("Onay", "DPI Bypass hala çalışıyor. Kapatmak istediğinizden emin misiniz?"):
                self.dpi.stop_bypass()
                self.running = False
                self.root.destroy()
        else:
            self.running = False
            self.root.destroy()
            self.root.destroy()
            
    def on_site_entry_focus_in(self, event):
        """Site entry focus olunca placeholder'ı temizle"""
        if self.site_entry.get() == "Site adı girin...":
            self.site_entry.delete(0, tk.END)
            self.site_entry.config(foreground='black')
            
    def on_site_entry_focus_out(self, event):
        """Site entry focus kaybedince placeholder'ı geri koy"""
        if self.site_entry.get() == "":
            self.site_entry.insert(0, "Site adı girin...")
            self.site_entry.config(foreground='grey')
            
    def on_ip_entry_focus_in(self, event):
        """IP entry focus olunca placeholder'ı temizle"""
        if self.ip_entry.get() == "IP adresi girin...":
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.config(foreground='black')
            
    def on_ip_entry_focus_out(self, event):
        """IP entry focus kaybedince placeholder'ı geri koy"""
        if self.ip_entry.get() == "":
            self.ip_entry.insert(0, "IP adresi girin...")
            self.ip_entry.config(foreground='grey')
            
    def run(self):
        """GUI'yi çalıştır"""
        self.running = True
        self.create_main_window()
        self.refresh_data()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
