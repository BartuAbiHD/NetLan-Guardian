#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console User Interface
DPI Bypass programı için konsol arayüzü
"""

import os
import time
import sys
from colorama import Fore, Back, Style

class ConsoleUI:
    def __init__(self, config_manager, dpi_bypass):
        self.config = config_manager
        self.dpi = dpi_bypass
        self.running = False
        
    def safe_input(self, prompt):
        """Güvenli input fonksiyonu EOF hatalarını yakalar"""
        try:
            if sys.stdin.isatty():
                return input(prompt)
            else:
                # Eğer stdin terminal değilse, varsayılan değer döndür
                print(f"{prompt}[AUTO]")
                return ""
        except (EOFError, KeyboardInterrupt):
            print("\n\nProgram sonlandırılıyor...")
            sys.exit(0)
        except Exception as e:
            print(f"\nGiriş hatası: {e}")
            return ""
        
    def clear_screen(self):
        """Ekranı temizle"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def show_main_menu(self):
        """Ana menüyü göster"""
        self.clear_screen()
        
        # DPI araç durumu
        current_tool = self.config.get_dpi_tool()
        tool_names = {'goodbyedpi': 'GoodbyeDPI', 'zapret': 'Zapret'}
        tool_name = tool_names.get(current_tool, current_tool)
        
        # DPI bypass durumu
        status = "Aktif" if self.dpi.active else "Pasif"
        status_color = Fore.GREEN if self.dpi.active else Fore.RED
        
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║              DPI BYPASS KONSOL               ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}📊 Durum:{Style.RESET_ALL}
  • DPI Araç: {Fore.CYAN}{tool_name}{Style.RESET_ALL}
  • Bypass: {status_color}{status}{Style.RESET_ALL}

{Fore.GREEN}[1]{Style.RESET_ALL} DPI Bypass Başlat/Durdur
{Fore.GREEN}[2]{Style.RESET_ALL} Site Yönetimi
{Fore.GREEN}[3]{Style.RESET_ALL} IP Adresi Yönetimi  
{Fore.GREEN}[4]{Style.RESET_ALL} Teknik Ayarları
{Fore.GREEN}[5]{Style.RESET_ALL} DPI Araç Seçimi
{Fore.GREEN}[6]{Style.RESET_ALL} Konfigürasyon İşlemleri
{Fore.GREEN}[0]{Style.RESET_ALL} Ana Menüye Dön / Çıkış
{Fore.GREEN}[5]{Style.RESET_ALL} Durum Görüntüle
{Fore.GREEN}[6]{Style.RESET_ALL} Konfigürasyon
{Fore.GREEN}[7]{Style.RESET_ALL} Bağlantı Testi
{Fore.GREEN}[0]{Style.RESET_ALL} Ana Menüye Dön

{Fore.YELLOW}Durum:{Style.RESET_ALL} {'🟢 Aktif' if self.dpi.running else '🔴 Pasif'}
        """)
        
    def show_site_menu(self):
        """Site yönetimi menüsü"""
        self.clear_screen()
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║                SİTE YÖNETİMİ                 ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}💡 İzin Verilen Siteler = DPI Bypass uygulanacak siteler
   Bu listedeki sitelere erişim zorlaştırılmışsa bypass kullanılır{Style.RESET_ALL}

{Fore.GREEN}[1]{Style.RESET_ALL} İzin Verilen Siteleri Listele
{Fore.GREEN}[2]{Style.RESET_ALL} Yeni Site Ekle (Bypass için)
{Fore.GREEN}[3]{Style.RESET_ALL} Site Sil
{Fore.GREEN}[4]{Style.RESET_ALL} Engellenmiş Siteleri Görüntüle
{Fore.GREEN}[5]{Style.RESET_ALL} Engellenmiş Site Ekle/Sil
{Fore.GREEN}[0]{Style.RESET_ALL} Ana Menüye Dön
        """)
        
    def show_ip_menu(self):
        """IP yönetimi menüsü"""
        self.clear_screen()
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║               IP ADRESİ YÖNETİMİ             ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}[1]{Style.RESET_ALL} İzin Verilen IP'leri Listele
{Fore.GREEN}[2]{Style.RESET_ALL} Yeni IP Ekle
{Fore.GREEN}[3]{Style.RESET_ALL} IP Sil
{Fore.GREEN}[0]{Style.RESET_ALL} Ana Menüye Dön
        """)
        
    def show_technique_menu(self):
        """Teknik ayarları menüsü"""
        self.clear_screen()
        techniques = {
            'fragment_packets': 'Paket Parçalama',
            'modify_ttl': 'TTL Modifikasyonu',
            'fake_packets': 'Sahte Paket Gönderimi',
            'domain_fronting_proxy': 'Domain Fronting Proxy'
        }
        
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║               TEKNİK AYARLARI                ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        
        for i, (tech_key, tech_name) in enumerate(techniques.items(), 1):
            status = "🟢 Aktif" if self.config.get_technique_status(tech_key) else "🔴 Pasif"
            print(f"{Fore.GREEN}[{i}]{Style.RESET_ALL} {tech_name}: {status}")
            
        print(f"{Fore.GREEN}[0]{Style.RESET_ALL} Ana Menüye Dön")
        
    def handle_bypass_toggle(self):
        """DPI Bypass başlat/durdur"""
        if self.dpi.running:
            self.dpi.stop_bypass()
            print(f"\n{Fore.GREEN}✅ DPI Bypass durduruldu{Style.RESET_ALL}")
        else:
            if self.dpi.start_bypass():
                print(f"\n{Fore.GREEN}✅ DPI Bypass başlatıldı{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.RED}❌ DPI Bypass başlatılamadı{Style.RESET_ALL}")
        
        self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        
    def handle_site_management(self):
        """Site yönetimi işlemleri"""
        while True:
            self.show_site_menu()
            choice = self.safe_input(f"{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}")
            
            if choice == "1":
                self.list_allowed_sites()
            elif choice == "2":
                self.add_site()
            elif choice == "3":
                self.remove_site()
            elif choice == "4":
                self.list_blocked_sites()
            elif choice == "5":
                self.manage_blocked_sites()
            elif choice == "0":
                break
            else:
                print(f"{Fore.RED}Geçersiz seçim!{Style.RESET_ALL}")
                time.sleep(1)
                
    def list_allowed_sites(self):
        """İzin verilen siteleri listele"""
        sites = self.config.get_allowed_sites()
        print(f"\n{Fore.CYAN}İzin Verilen Siteler:{Style.RESET_ALL}")
        print("=" * 50)
        
        if sites:
            for i, site in enumerate(sites, 1):
                print(f"{Fore.GREEN}{i:2d}.{Style.RESET_ALL} {site}")
        else:
            print(f"{Fore.YELLOW}Hiç site eklenmemiş.{Style.RESET_ALL}")
            
        self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        
    def add_site(self):
        """Yeni site ekle (DPI bypass için)"""
        print(f"\n{Fore.CYAN}💡 Bu listeye eklenen siteler DPI bypass ile erişim sağlanacak sitelerdir.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Örneğin Türkiye'de engellenmiş siteleri buraya ekleyebilirsiniz.{Style.RESET_ALL}")
        
        site = self.safe_input(f"\n{Fore.GREEN}DPI bypass uygulanacak site adı: {Style.RESET_ALL}").strip()
        
        if not site:
            print(f"{Fore.RED}Site adı boş olamaz!{Style.RESET_ALL}")
            return
            
        if not self.config.validate_domain(site):
            print(f"{Fore.RED}Geçersiz domain formatı!{Style.RESET_ALL}")
            time.sleep(2)
            return
            
        if self.config.add_allowed_site(site):
            print(f"{Fore.GREEN}✅ '{site}' bypass listesine eklendi{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   → Bu siteye erişim sırasında DPI bypass uygulanacak{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ '{site}' zaten bypass listesinde{Style.RESET_ALL}")
            
        time.sleep(3)
        
    def remove_site(self):
        """Site sil"""
        sites = self.config.get_allowed_sites()
        
        if not sites:
            print(f"\n{Fore.YELLOW}Silinecek site bulunmuyor.{Style.RESET_ALL}")
            time.sleep(2)
            return
            
        print(f"\n{Fore.CYAN}Mevcut Siteler:{Style.RESET_ALL}")
        for i, site in enumerate(sites, 1):
            print(f"{Fore.GREEN}{i:2d}.{Style.RESET_ALL} {site}")
            
        try:
            choice = int(self.safe_input(f"\n{Fore.GREEN}Silinecek site numarası: {Style.RESET_ALL}"))
            
            if 1 <= choice <= len(sites):
                site = sites[choice - 1]
                if self.config.remove_allowed_site(site):
                    print(f"{Fore.GREEN}✅ '{site}' başarıyla silindi{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Site silinemedi{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Geçersiz numara!{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Lütfen geçerli bir numara girin!{Style.RESET_ALL}")
            
        time.sleep(2)
        
    def list_blocked_sites(self):
        """Engellenmiş siteleri listele"""
        sites = self.config.get_blocked_sites()
        print(f"\n{Fore.RED}Engellenmiş Siteler:{Style.RESET_ALL}")
        print("=" * 50)
        
        if sites:
            for i, site in enumerate(sites, 1):
                print(f"{Fore.RED}{i:2d}.{Style.RESET_ALL} {site}")
        else:
            print(f"{Fore.YELLOW}Hiç engellenmiş site yok.{Style.RESET_ALL}")
            
        self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        
    def manage_blocked_sites(self):
        """Engellenmiş site yönetimi"""
        print(f"\n{Fore.CYAN}[1]{Style.RESET_ALL} Engellenmiş site ekle")
        print(f"{Fore.CYAN}[2]{Style.RESET_ALL} Engellenmiş site sil")
        
        choice = self.safe_input(f"{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}")
        
        if choice == "1":
            site = self.safe_input(f"\n{Fore.RED}Engellenecek site adı: {Style.RESET_ALL}").strip()
            if site and self.config.validate_domain(site):
                if self.config.add_blocked_site(site):
                    print(f"{Fore.GREEN}✅ '{site}' engellenenler listesine eklendi{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ '{site}' zaten mevcut{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Geçersiz site adı!{Style.RESET_ALL}")
        elif choice == "2":
            # Engellenmiş site silme işlemi (benzer mantık)
            sites = self.config.get_blocked_sites()
            if sites:
                print(f"\n{Fore.RED}Engellenmiş Siteler:{Style.RESET_ALL}")
                for i, site in enumerate(sites, 1):
                    print(f"{Fore.RED}{i:2d}.{Style.RESET_ALL} {site}")
                try:
                    choice = int(self.safe_input(f"\n{Fore.GREEN}Silinecek site numarası: {Style.RESET_ALL}"))
                    if 1 <= choice <= len(sites):
                        site = sites[choice - 1]
                        if self.config.remove_blocked_site(site):
                            print(f"{Fore.GREEN}✅ '{site}' engellenenler listesinden silindi{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED}Geçersiz numara!{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}Silinecek site bulunmuyor.{Style.RESET_ALL}")
        
        time.sleep(2)
        
    def handle_ip_management(self):
        """IP yönetimi işlemleri"""
        while True:
            self.show_ip_menu()
            choice = self.safe_input(f"{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}")
            
            if choice == "1":
                self.list_allowed_ips()
            elif choice == "2":
                self.add_ip()
            elif choice == "3":
                self.remove_ip()
            elif choice == "0":
                break
            else:
                print(f"{Fore.RED}Geçersiz seçim!{Style.RESET_ALL}")
                time.sleep(1)
                
    def list_allowed_ips(self):
        """İzin verilen IP'leri listele"""
        ips = self.config.get_allowed_ips()
        print(f"\n{Fore.CYAN}İzin Verilen IP Adresleri:{Style.RESET_ALL}")
        print("=" * 50)
        
        if ips:
            for i, ip in enumerate(ips, 1):
                print(f"{Fore.GREEN}{i:2d}.{Style.RESET_ALL} {ip}")
        else:
            print(f"{Fore.YELLOW}Hiç IP adresi eklenmemiş.{Style.RESET_ALL}")
            
        self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        
    def add_ip(self):
        """Yeni IP ekle"""
        ip = self.safe_input(f"\n{Fore.GREEN}Eklenecek IP adresi: {Style.RESET_ALL}").strip()
        
        if not ip:
            print(f"{Fore.RED}IP adresi boş olamaz!{Style.RESET_ALL}")
            time.sleep(2)
            return
            
        if not self.config.validate_ip(ip):
            print(f"{Fore.RED}Geçersiz IP adresi formatı!{Style.RESET_ALL}")
            time.sleep(2)
            return
            
        if self.config.add_allowed_ip(ip):
            print(f"{Fore.GREEN}✅ '{ip}' başarıyla eklendi{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}⚠️ '{ip}' zaten mevcut{Style.RESET_ALL}")
            
        time.sleep(2)
        
    def remove_ip(self):
        """IP sil"""
        ips = self.config.get_allowed_ips()
        
        if not ips:
            print(f"\n{Fore.YELLOW}Silinecek IP bulunmuyor.{Style.RESET_ALL}")
            time.sleep(2)
            return
            
        print(f"\n{Fore.CYAN}Mevcut IP Adresleri:{Style.RESET_ALL}")
        for i, ip in enumerate(ips, 1):
            print(f"{Fore.GREEN}{i:2d}.{Style.RESET_ALL} {ip}")
            
        try:
            choice = int(self.safe_input(f"\n{Fore.GREEN}Silinecek IP numarası: {Style.RESET_ALL}"))
            
            if 1 <= choice <= len(ips):
                ip = ips[choice - 1]
                if self.config.remove_allowed_ip(ip):
                    print(f"{Fore.GREEN}✅ '{ip}' başarıyla silindi{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ IP silinemedi{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}Geçersiz numara!{Style.RESET_ALL}")
        except ValueError:
            print(f"{Fore.RED}Lütfen geçerli bir numara girin!{Style.RESET_ALL}")
            
        time.sleep(2)
        
    def handle_technique_settings(self):
        """Teknik ayarları yönetimi"""
        techniques = {
            'fragment_packets': 'Paket Parçalama',
            'modify_ttl': 'TTL Modifikasyonu', 
            'fake_packets': 'Sahte Paket Gönderimi',
            'domain_fronting_proxy': 'Domain Fronting Proxy'
        }
        
        while True:
            self.show_technique_menu()
            try:
                choice = int(self.safe_input(f"{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}"))
                
                if choice == 0:
                    break
                elif 1 <= choice <= len(techniques):
                    tech_key = list(techniques.keys())[choice - 1]
                    current_status = self.config.get_technique_status(tech_key)
                    new_status = not current_status
                    self.config.set_technique_status(tech_key, new_status)
                    
                    status_text = "aktif" if new_status else "pasif"
                    print(f"\n{Fore.GREEN}✅ {techniques[tech_key]} {status_text} olarak ayarlandı{Style.RESET_ALL}")
                    time.sleep(1)
                else:
                    print(f"{Fore.RED}Geçersiz seçim!{Style.RESET_ALL}")
                    time.sleep(1)
            except ValueError:
                print(f"{Fore.RED}Lütfen geçerli bir numara girin!{Style.RESET_ALL}")
                time.sleep(1)
                
    def show_status(self):
        """Durum görüntüle"""
        status = self.dpi.get_status()
        self.clear_screen()
        
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║                    DURUM                     ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}DPI Bypass:{Style.RESET_ALL} {'🟢 Çalışıyor' if status['running'] else '🔴 Durduruldu'}
{Fore.YELLOW}Aktif Thread:{Style.RESET_ALL} {status['active_threads']}

{Fore.CYAN}Aktif Teknikler:{Style.RESET_ALL}
""")
        
        for tech, enabled in status['techniques'].items():
            tech_names = {
                'fragment_packets': 'Paket Parçalama',
                'modify_ttl': 'TTL Modifikasyonu',
                'fake_packets': 'Sahte Paket Gönderimi',
                'domain_fronting_proxy': 'Domain Fronting Proxy'
            }
            icon = "🟢" if enabled else "🔴"
            print(f"  {icon} {tech_names.get(tech, tech)}")
            
        print(f"\n{Fore.CYAN}Konfigürasyon:{Style.RESET_ALL}")
        print(f"  📝 İzin verilen site sayısı: {len(self.config.get_allowed_sites())}")
        print(f"  🌐 İzin verilen IP sayısı: {len(self.config.get_allowed_ips())}")
        print(f"  🚫 Engellenmiş site sayısı: {len(self.config.get_blocked_sites())}")
        
        self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        
    def handle_configuration(self):
        """Konfigürasyon işlemleri"""
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║               KONFİGÜRASYON                  ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.GREEN}[1]{Style.RESET_ALL} Konfigürasyonu Dışa Aktar
{Fore.GREEN}[2]{Style.RESET_ALL} Konfigürasyonu İçe Aktar
{Fore.GREEN}[3]{Style.RESET_ALL} Konfigürasyonu Sıfırla
{Fore.GREEN}[0]{Style.RESET_ALL} Ana Menüye Dön
        """)
        
        choice = self.safe_input(f"{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}")
        
        if choice == "1":
            filename = self.safe_input(f"\n{Fore.GREEN}Dosya adı (config_backup.yaml): {Style.RESET_ALL}") or "config_backup.yaml"
            if self.config.export_config(filename):
                print(f"{Fore.GREEN}✅ Konfigürasyon '{filename}' dosyasına kaydedildi{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Konfigürasyon dışa aktarılamadı{Style.RESET_ALL}")
        elif choice == "2":
            filename = self.safe_input(f"\n{Fore.GREEN}İçe aktarılacak dosya adı: {Style.RESET_ALL}")
            if filename and os.path.exists(filename):
                if self.config.import_config(filename):
                    print(f"{Fore.GREEN}✅ Konfigürasyon '{filename}' dosyasından yüklendi{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}❌ Konfigürasyon içe aktarılamadı{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Dosya bulunamadı{Style.RESET_ALL}")
        elif choice == "3":
            confirm = self.safe_input(f"\n{Fore.RED}Tüm ayarlar silinecek! Emin misiniz? (y/N): {Style.RESET_ALL}")
            if confirm.lower() == 'y':
                self.config.reset_config()
                print(f"{Fore.GREEN}✅ Konfigürasyon sıfırlandı{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}İşlem iptal edildi{Style.RESET_ALL}")
                
        time.sleep(2)
        
    def test_connections(self):
        """Bağlantı testi"""
        self.clear_screen()
        print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║                BAĞLANTI TESTİ                ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}
        """)
        
        sites = self.config.get_allowed_sites()
        
        if not sites:
            print(f"{Fore.YELLOW}Test edilecek site bulunamadı.{Style.RESET_ALL}")
            self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
            return
            
        for site in sites:
            print(f"{Fore.YELLOW}Testing {site}...{Style.RESET_ALL}", end=" ")
            
            if self.dpi.check_connection(site):
                print(f"{Fore.GREEN}✅ Bağlantı başarılı{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Bağlantı başarısız{Style.RESET_ALL}")
                
        self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
        
    def run(self):
        """Ana UI döngüsü"""
        self.running = True
        
        while self.running:
            self.show_main_menu()
            choice = self.safe_input(f"{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}")
            
            try:
                if choice == "1":
                    self.handle_bypass_toggle()
                elif choice == "2":
                    self.handle_site_management()
                elif choice == "3":
                    self.handle_ip_management()
                elif choice == "4":
                    self.handle_technique_settings()
                elif choice == "5":
                    self.handle_dpi_tool_selection()
                elif choice == "6":
                    self.handle_configuration()
                elif choice == "0":
                    self.running = False
                    # DPI bypass çalışıyorsa durdur
                    if self.dpi.running:
                        print(f"{Fore.YELLOW}DPI Bypass durduruluyor...{Style.RESET_ALL}")
                        self.dpi.stop_bypass()
                    print(f"{Fore.GREEN}Konsol modu kapatılıyor...{Style.RESET_ALL}")
                    time.sleep(1)
                else:
                    print(f"{Fore.RED}Geçersiz seçim!{Style.RESET_ALL}")
                    time.sleep(1)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Çıkış yapılıyor...{Style.RESET_ALL}")
                self.running = False
                if self.dpi.running:
                    self.dpi.stop_bypass()
            except Exception as e:
                print(f"{Fore.RED}Hata: {str(e)}{Style.RESET_ALL}")
                self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
    
    def handle_dpi_tool_selection(self):
        """DPI araç seçimi menüsü"""
        while True:
            self.clear_screen()
            
            current_tool = self.config.get_dpi_tool()
            tools = self.dpi.get_available_tools()
            
            print(f"""
{Fore.CYAN}╔══════════════════════════════════════════════╗
║                DPI ARAÇ SEÇİMİ               ║
╚══════════════════════════════════════════════╝{Style.RESET_ALL}

{Fore.YELLOW}Mevcut Araçlar:{Style.RESET_ALL}
""")
            
            # GoodbyeDPI
            goodbyedpi_status = "✅ Aktif" if current_tool == 'goodbyedpi' else "⚪"
            goodbyedpi_available = "🟢 Mevcut" if tools['goodbyedpi']['available'] else "🔴 Yok"
            print(f"{Fore.GREEN}[1]{Style.RESET_ALL} GoodbyeDPI {goodbyedpi_status}")
            print(f"    📍 {tools['goodbyedpi']['description']}")
            print(f"    🔧 {goodbyedpi_available}")
            
            # Zapret
            zapret_status = "✅ Aktif" if current_tool == 'zapret' else "⚪"
            zapret_available = "🟢 Mevcut" if tools['zapret']['available'] else "🔴 Yok"
            print(f"\n{Fore.GREEN}[2]{Style.RESET_ALL} Zapret {zapret_status}")
            print(f"    📍 {tools['zapret']['description']}")
            print(f"    🔧 {zapret_available}")
            
            if not tools['zapret']['available']:
                print(f"    📦 Kurulum: https://github.com/bol-van/zapret-win-bundle")
                print(f"    📂 Hedef: external/zapret/ klasörü")
            
            print(f"\n{Fore.YELLOW}Seçenekler:{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[1]{Style.RESET_ALL} GoodbyeDPI Seç")
            print(f"{Fore.GREEN}[2]{Style.RESET_ALL} Zapret Seç")
            print(f"{Fore.GREEN}[3]{Style.RESET_ALL} Araç Durumlarını Göster")
            print(f"{Fore.GREEN}[0]{Style.RESET_ALL} Geri Dön")
            
            choice = self.safe_input(f"\n{Fore.GREEN}Seçiminiz: {Style.RESET_ALL}")
            
            if choice == "1":
                # GoodbyeDPI seç
                was_active = self.dpi.active
                if was_active:
                    print(f"{Fore.YELLOW}DPI Bypass durduruluyor...{Style.RESET_ALL}")
                    self.dpi.stop_bypass()
                
                self.config.set_dpi_tool('goodbyedpi')
                print(f"{Fore.GREEN}✅ GoodbyeDPI seçildi!{Style.RESET_ALL}")
                
                if was_active:
                    print(f"{Fore.YELLOW}DPI Bypass yeniden başlatılıyor...{Style.RESET_ALL}")
                    time.sleep(1)
                    self.dpi.start_bypass()
                
                time.sleep(2)
                
            elif choice == "2":
                # Zapret seç
                was_active = self.dpi.active
                if was_active:
                    print(f"{Fore.YELLOW}DPI Bypass durduruluyor...{Style.RESET_ALL}")
                    self.dpi.stop_bypass()
                
                self.config.set_dpi_tool('zapret')
                print(f"{Fore.GREEN}✅ Zapret seçildi!{Style.RESET_ALL}")
                
                # Zapret yoksa otomatik indirilecek bilgisi
                tools = self.dpi.get_available_tools()
                if not tools['zapret']['available']:
                    print(f"{Fore.CYAN}🔄 Zapret ilk kullanımda otomatik olarak indirilecek.{Style.RESET_ALL}")
                
                if was_active:
                    print(f"{Fore.YELLOW}DPI Bypass yeniden başlatılıyor...{Style.RESET_ALL}")
                    time.sleep(1)
                    self.dpi.start_bypass()
                
                time.sleep(2)
                
            elif choice == "3":
                # Araç durumlarını göster
                self.clear_screen()
                print(f"{Fore.CYAN}📊 DPI Araç Durumları{Style.RESET_ALL}\n")
                
                for tool_key, tool_data in tools.items():
                    print(f"{Fore.YELLOW}{tool_data['name']}:{Style.RESET_ALL}")
                    print(f"  • Mevcut: {'✅' if tool_data['available'] else '❌'}")
                    print(f"  • Çalışıyor: {'✅' if tool_data['running'] else '❌'}")
                    print(f"  • Sürüm: {tool_data['version']}")
                    print(f"  • Yol: {tool_data['path']}")
                    print(f"  • Açıklama: {tool_data['description']}\n")
                
                self.safe_input(f"\n{Fore.YELLOW}Devam etmek için Enter'a basın...{Style.RESET_ALL}")
                
            elif choice == "0":
                break
            else:
                print(f"{Fore.RED}Geçersiz seçim!{Style.RESET_ALL}")
                time.sleep(1)
