#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetLan Guardian
Python ile yazılmış gelişmiş DPI (Deep Packet Inspection) bypass aracı
GoodbyeDPI ve Zapret araçları için merkezi yönetim platformu
"""

import sys
import os
import threading
import time
import argparse
from colorama import init, Fore, Back, Style
from src.dpi_bypass import DPIBypass
from src.config_manager import ConfigManager
from src.ui.console_ui import ConsoleUI
from src.updater import UpdateManager, get_current_version

init()  # Colorama initialization for Windows

class DPIProgram:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.dpi_bypass = DPIBypass(self.config_manager)
        self.console_ui = ConsoleUI(self.config_manager, self.dpi_bypass)
        self.running = False
        
        # Güncelleme yöneticisini başlat
        self.current_version = get_current_version()
        self.update_manager = UpdateManager(self.current_version)
        
    def safe_input(self, prompt):
        """Güvenli input fonksiyonu EOF hatalarını yakalar"""
        try:
            if sys.stdin.isatty():
                return input(prompt).strip()
            else:
                print(f"{prompt}[AUTO - Exiting]")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.GREEN}Program sonlandırılıyor...{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"\nGiriş hatası: {e}")
            sys.exit(0)
        
    def show_banner(self):
        banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                    NetLan Guardian                          ║
║                   DPI Bypass Hub 2025                       ║
║            GoodbyeDPI & Zapret Management Platform          ║
║                      Version {self.current_version}                         ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
        """
        print(banner)
        
        # Arka planda güncelleme kontrolü yap
        self.update_manager.background_check(self._on_update_check)
        
    def _on_update_check(self, update_available, latest_version):
        """Güncelleme kontrolü callback fonksiyonu"""
        if update_available:
            print(f"\n{Fore.GREEN}🎉 Yeni güncelleme mevcut: v{latest_version}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Güncellemeleri kontrol etmek için menüden '4' seçeneğini kullanın.{Style.RESET_ALL}")
        
    def show_menu(self):
        menu = f"""
{Fore.YELLOW}[1]{Style.RESET_ALL} Konsol Modu (Console Mode)
{Fore.YELLOW}[2]{Style.RESET_ALL} GUI Modu (Graphical Interface)
{Fore.YELLOW}[3]{Style.RESET_ALL} Güncelleme Kontrol Et (Check for Updates)
{Fore.YELLOW}[4]{Style.RESET_ALL} Çıkış (Exit)
        """
        print(menu)
        
    def run(self, nogui=False):
        if nogui:
            # Konsol modu direkt açılır
            print(f"{Fore.CYAN}Konsol modu başlatılıyor...{Style.RESET_ALL}")
            self.console_ui.run()
            return
            
        # GUI modunu önce dene
        try:
            from src.ui.modern_gui import UltraModernDPIGUI
            modern_gui = UltraModernDPIGUI()
            modern_gui.run()
            return
        except ImportError as e:
            print(f"{Fore.RED}Ultra Modern GUI modülü yüklenemedi: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Konsol moduna geçiliyor...{Style.RESET_ALL}")
            self.console_ui.run()
            return
        except Exception as e:
            print(f"{Fore.RED}Ultra Modern GUI başlatma hatası: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Konsol moduna geçiliyor...{Style.RESET_ALL}")
            self.console_ui.run()
            return

    def run_interactive(self):
        """İnteraktif mod - kullanıcı menüden seçim yapar"""
        self.show_banner()
        
        while True:
            self.show_menu()
            try:
                choice = self.safe_input(f"{Fore.GREEN}Seçiminiz (Your choice): {Style.RESET_ALL}")
                
                if choice == "1":
                    self.console_ui.run()
                elif choice == "2":
                    try:
                        from src.ui.modern_gui import UltraModernDPIGUI
                        modern_gui = UltraModernDPIGUI()
                        modern_gui.run()
                    except ImportError as e:
                        print(f"{Fore.RED}Ultra Modern GUI modülü yüklenemedi: {e}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}Konsol modunu kullanın.{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}Ultra Modern GUI başlatma hatası: {e}{Style.RESET_ALL}")
                elif choice == "3":
                    # Güncelleme kontrol et ve yükle
                    print(f"{Fore.CYAN}Güncelleme kontrol ediliyor...{Style.RESET_ALL}")
                    try:
                        self.update_manager.auto_update(force=True)
                    except Exception as e:
                        print(f"{Fore.RED}Güncelleme hatası: {str(e)}{Style.RESET_ALL}")
                elif choice == "4":
                    print(f"{Fore.GREEN}Program sonlandırılıyor...{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED}Geçersiz seçim!{Style.RESET_ALL}")
                    
            except KeyboardInterrupt:
                print(f"\n{Fore.GREEN}Program sonlandırılıyor...{Style.RESET_ALL}")
                break
            except Exception as e:
                print(f"{Fore.RED}Hata: {str(e)}{Style.RESET_ALL}")

def main():
    # Komut satırı argümanlarını parse et
    parser = argparse.ArgumentParser(description='NetLan Guardian - DPI Bypass Hub')
    parser.add_argument('--nogui', action='store_true', 
                       help='Konsol modu kullan (GUI olmadan)')
    parser.add_argument('--interactive', action='store_true',
                       help='İnteraktif menü göster')
    parser.add_argument('--check-updates', action='store_true',
                       help='Başlangıçta güncellemeleri kontrol et')
    parser.add_argument('--auto-update', action='store_true',
                       help='Otomatik güncelleme yap (kullanıcı onayı ile)')
    args = parser.parse_args()
    
    if not os.path.exists('config'):
        os.makedirs('config')
    if not os.path.exists('logs'):
        os.makedirs('logs')
        
    program = DPIProgram()
    
    # Başlangıçta güncelleme kontrolü
    if args.check_updates or args.auto_update:
        try:
            print(f"{Fore.CYAN}Başlangıç güncelleme kontrolü...{Style.RESET_ALL}")
            if args.auto_update:
                program.update_manager.auto_update()
            else:
                update_available, latest_ver = program.update_manager.check_for_updates(show_progress=True)
                if update_available:
                    program.update_manager.show_update_info()
                    print(f"{Fore.YELLOW}Güncellemeyi yüklemek için --auto-update parametresini kullanın.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}Güncelleme kontrolü hatası: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Program normal şekilde başlatılıyor...{Style.RESET_ALL}")
    
    # Argümanlara göre çalıştırma modunu belirle
    if args.interactive:
        # İnteraktif menü göster
        program.run_interactive()
    elif args.nogui:
        # Konsol modu
        program.run(nogui=True)
    else:
        # Varsayılan: GUI modu dene, başarısız olursa konsol modu
        program.run(nogui=False)

if __name__ == "__main__":
    main()
