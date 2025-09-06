#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetLan Guardian Updater
GitHub'dan otomatik güncelleme kontrolü ve indirme sistemi
"""

import os
import sys
import json
import zipfile
import shutil
import subprocess
import tempfile
import requests
from typing import Dict, Any, Optional, Tuple
from packaging import version
from colorama import Fore, Style
import threading
import time

class UpdateManager:
    def __init__(self, current_version: str = "1.0.0"):
        self.github_api_url = "https://api.github.com/repos/BartuAbiHD/NetLan-Guardian"
        self.github_repo_url = "https://github.com/BartuAbiHD/NetLan-Guardian"
        self.current_version = current_version
        self.update_available = False
        self.latest_version = None
        self.download_url = None
        self.release_notes = ""
        
    def check_for_updates(self, show_progress: bool = True) -> Tuple[bool, Optional[str]]:
        """GitHub'dan güncelleme kontrolü yapar"""
        try:
            if show_progress:
                print(f"{Fore.CYAN}Güncelleme kontrol ediliyor...{Style.RESET_ALL}")
                
            response = requests.get(f"{self.github_api_url}/releases/latest", timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            self.latest_version = release_data['tag_name'].lstrip('v')
            self.release_notes = release_data['body']
            
            # İndirme URL'sini bul (Windows exe veya zip dosyası)
            for asset in release_data['assets']:
                asset_name = asset['name'].lower()
                if 'windows' in asset_name or asset_name.endswith('.exe') or asset_name.endswith('.zip'):
                    self.download_url = asset['browser_download_url']
                    break
            
            # Versiyon karşılaştırması
            if version.parse(self.latest_version) > version.parse(self.current_version):
                self.update_available = True
                if show_progress:
                    print(f"{Fore.GREEN}✓ Yeni güncelleme bulundu: v{self.latest_version}{Style.RESET_ALL}")
                return True, self.latest_version
            else:
                if show_progress:
                    print(f"{Fore.GREEN}✓ Program güncel (v{self.current_version}){Style.RESET_ALL}")
                return False, self.current_version
                
        except requests.exceptions.RequestException as e:
            if show_progress:
                print(f"{Fore.RED}Güncelleme kontrolü başarısız: İnternet bağlantısı hatası{Style.RESET_ALL}")
            return False, None
        except Exception as e:
            if show_progress:
                print(f"{Fore.RED}Güncelleme kontrolü hatası: {str(e)}{Style.RESET_ALL}")
            return False, None
    
    def show_update_info(self) -> None:
        """Güncelleme bilgilerini gösterir"""
        if not self.update_available:
            return
            
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🎉 YENİ GÜNCELLEME MEVCUT!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Mevcut Sürüm: {Fore.WHITE}v{self.current_version}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Yeni Sürüm:   {Fore.WHITE}v{self.latest_version}{Style.RESET_ALL}")
        
        if self.release_notes:
            print(f"\n{Fore.YELLOW}Güncelleme Notları:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}{self.release_notes}{Style.RESET_ALL}")
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def download_update(self, download_path: Optional[str] = None) -> Optional[str]:
        """Güncellemeyi indirir"""
        if not self.download_url:
            print(f"{Fore.RED}İndirme URL'si bulunamadı!{Style.RESET_ALL}")
            return None
            
        try:
            if download_path is None:
                download_path = tempfile.mkdtemp()
            
            filename = os.path.basename(self.download_url)
            file_path = os.path.join(download_path, filename)
            
            print(f"{Fore.CYAN}Güncelleme indiriliyor: {filename}{Style.RESET_ALL}")
            
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r{Fore.YELLOW}İndirme İlerlemesi: {progress:.1f}%{Style.RESET_ALL}", end='')
            
            print(f"\n{Fore.GREEN}✓ İndirme tamamlandı: {file_path}{Style.RESET_ALL}")
            return file_path
            
        except Exception as e:
            print(f"\n{Fore.RED}İndirme hatası: {str(e)}{Style.RESET_ALL}")
            return None
    
    def install_update(self, update_file: str) -> bool:
        """Güncellemeyi yükler"""
        try:
            current_exe = sys.executable
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Mevcut programı yedekle
            backup_dir = os.path.join(current_dir, 'backup')
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            print(f"{Fore.CYAN}Mevcut program yedekleniyor...{Style.RESET_ALL}")
            
            # Eğer zip dosyasıysa
            if update_file.endswith('.zip'):
                with tempfile.TemporaryDirectory() as temp_dir:
                    # Zip'i çıkart
                    with zipfile.ZipFile(update_file, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                    
                    # Yeni dosyaları kopyala
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            src_file = os.path.join(root, file)
                            rel_path = os.path.relpath(src_file, temp_dir)
                            dest_file = os.path.join(current_dir, rel_path)
                            
                            # Dizini oluştur
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            
                            # Dosyayı kopyala
                            shutil.copy2(src_file, dest_file)
            
            # Eğer exe dosyasıysa
            elif update_file.endswith('.exe'):
                dest_exe = os.path.join(current_dir, 'NetLanGuardian.exe')
                shutil.copy2(update_file, dest_exe)
            
            print(f"{Fore.GREEN}✓ Güncelleme başarıyla yüklendi!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Program yeniden başlatılacak...{Style.RESET_ALL}")
            
            # Programı yeniden başlat
            time.sleep(2)
            
            if update_file.endswith('.exe'):
                subprocess.Popen([os.path.join(current_dir, 'NetLanGuardian.exe')])
            else:
                subprocess.Popen([sys.executable, os.path.join(current_dir, 'main.py')])
            
            sys.exit(0)
            
        except Exception as e:
            print(f"{Fore.RED}Güncelleme yükleme hatası: {str(e)}{Style.RESET_ALL}")
            return False
    
    def auto_update(self, force: bool = False) -> bool:
        """Otomatik güncelleme yapar"""
        try:
            # Güncelleme kontrol et
            update_available, latest_ver = self.check_for_updates(show_progress=True)
            
            if not update_available and not force:
                return False
            
            if update_available:
                self.show_update_info()
                
                # Kullanıcıya sor
                response = input(f"\n{Fore.YELLOW}Güncellemeyi şimdi yüklemek istiyor musunuz? (E/H): {Style.RESET_ALL}")
                
                if response.lower() in ['e', 'evet', 'y', 'yes']:
                    # İndir
                    update_file = self.download_update()
                    if update_file:
                        # Yükle
                        return self.install_update(update_file)
                else:
                    print(f"{Fore.YELLOW}Güncelleme iptal edildi.{Style.RESET_ALL}")
                    return False
            
            return True
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Güncelleme işlemi iptal edildi.{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}Otomatik güncelleme hatası: {str(e)}{Style.RESET_ALL}")
            return False
    
    def background_check(self, callback=None):
        """Arka planda güncelleme kontrolü yapar"""
        def check_updates():
            try:
                update_available, latest_ver = self.check_for_updates(show_progress=False)
                if callback:
                    callback(update_available, latest_ver)
            except:
                pass
        
        thread = threading.Thread(target=check_updates, daemon=True)
        thread.start()
        return thread

def get_current_version() -> str:
    """Mevcut program versiyonunu döndürür"""
    version_file = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
    if os.path.exists(version_file):
        with open(version_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return "1.0.0"

# Test fonksiyonu
if __name__ == "__main__":
    from colorama import init
    init()
    
    updater = UpdateManager(get_current_version())
    updater.auto_update()
