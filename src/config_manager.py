#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration Manager
Site ve IP adreslerini yönetmek için konfigürasyon modülü
"""

import json
import yaml
import os
from typing import List, Dict, Any

class ConfigManager:
    def __init__(self, config_file='config/dpi_config.yaml'):
        self.config_file = config_file
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Konfigürasyon dosyasını yükle"""
        default_config = {
            'allowed_sites': [],
            'allowed_ips': [
                '8.8.8.8',
                '8.8.4.4',
                '1.1.1.1',
                '1.0.0.1',
                '208.67.222.222',
                '208.67.220.220',
                '9.9.9.9',
                '149.112.112.112'
            ],
            'blocked_sites': [],
            'techniques': {
                'fragment_packets': True,
                'modify_ttl': True,
                'fake_packets': True,
                'domain_fronting_proxy': False
            },
            'settings': {
                'auto_start': False,
                'log_level': 'INFO',
                'max_threads': 10,
                'request_timeout': 5,
                'dpi_tool': 'goodbyedpi',  # goodbyedpi veya zapret
                'country_code': 'TR',  # Varsayılan ülke kodu
                'minimize_to_tray': False,  # System tray desteği
                'show_notifications': True  # Bildirimler
            }
        }
        
        if not os.path.exists(self.config_file):
            # Konfigürasyon dizinini oluştur
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            self.save_config(default_config)
            return default_config
            
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    return yaml.safe_load(f) or default_config
                else:
                    return json.load(f) or default_config
        except Exception as e:
            print(f"Konfigürasyon yükleme hatası: {e}")
            return default_config
            
    def save_config(self, config=None):
        """Konfigürasyonu dosyaya kaydet"""
        if config is None:
            config = self.config
            
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                if self.config_file.endswith('.yaml') or self.config_file.endswith('.yml'):
                    yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Konfigürasyon kaydetme hatası: {e}")
            
    def get_allowed_sites(self) -> List[str]:
        """İzin verilen siteleri döndür"""
        return self.config.get('allowed_sites', [])
        
    def add_allowed_site(self, site: str) -> bool:
        """İzin verilen sitelere yeni site ekle"""
        if site not in self.config.get('allowed_sites', []):
            self.config.setdefault('allowed_sites', []).append(site)
            self.save_config()
            return True
        return False
        
    def remove_allowed_site(self, site: str) -> bool:
        """İzin verilen sitelerden site kaldır"""
        if site in self.config.get('allowed_sites', []):
            self.config['allowed_sites'].remove(site)
            self.save_config()
            return True
        return False
        
    def get_bypass_sites(self) -> List[str]:
        """Bypass edilecek siteleri döndür (allowed_sites ile aynı)"""
        return self.get_allowed_sites()
        
    def update_bypass_sites(self, sites: List[str]):
        """Bypass edilecek siteleri güncelle ve blacklist dosyasını oluştur"""
        self.config['allowed_sites'] = sites
        self.save_config()
        
        # Blacklist dosyasını güncelle
        self.create_blacklist_file(sites)
        
    def create_blacklist_file(self, sites: List[str]):
        """GoodbyeDPI için blacklist.txt dosyası oluştur"""
        from pathlib import Path
        
        # Blacklist dosyası yolu
        base_dir = Path(__file__).parent.parent
        external_dir = base_dir / "external"
        external_dir.mkdir(exist_ok=True)
        blacklist_path = external_dir / "blacklist.txt"
        
        try:
            with open(blacklist_path, 'w', encoding='utf-8') as f:
                f.write("# GoodbyeDPI Blacklist - DPI bypass uygulanacak siteler\n")
                f.write("# Bu listedeki sitelere bypass uygulanır, diğerleri normal erişim\n")
                f.write(f"# Toplam {len(sites)} site\n\n")
                
                if not sites:
                    f.write("# Liste boş - hiçbir siteye DPI bypass uygulanmayacak\n")
                else:
                    # Optimize edilmiş domain listesi oluştur
                    final_domains = set()
                    
                    for site in sites:
                        # Domain'i temizle
                        domain = site.strip()
                        if domain.startswith(('http://', 'https://')):
                            from urllib.parse import urlparse
                            parsed = urlparse(domain)
                            domain = parsed.hostname or domain
                        
                        # www. prefix'ini kaldır
                        if domain.startswith('www.'):
                            domain = domain[4:]
                        
                        if domain:  # Boş değilse ekle
                            final_domains.add(domain)
                            # www subdomain'i de ekle (çoğu site için gerekli)
                            final_domains.add(f"www.{domain}")
                            
                            # Belirli domainler için özel subdomain'ler
                            if 'discord' in domain:
                                final_domains.update([
                                    f"cdn.{domain}",
                                    f"gateway.{domain}",
                                    f"media.{domain}",
                                    f"images-ext-1.{domain}",
                                    f"images-ext-2.{domain}"
                                ])
                            elif 'youtube' in domain:
                                final_domains.update([
                                    f"www.{domain}",
                                    f"m.{domain}",
                                    f"music.{domain}",
                                    f"gaming.{domain}",
                                    f"tv.{domain}"
                                ])
                                # YouTube için googlevideo domain'leri
                                final_domains.update([
                                    "googlevideo.com",
                                    "www.googlevideo.com"
                                ])
                            elif 'github' in domain:
                                final_domains.update([
                                    f"api.{domain}",
                                    f"raw.githubusercontent.com",
                                    f"codeload.{domain}",
                                    f"assets-cdn.{domain}"
                                ])
                    
                    # Temiz domain'leri yaz
                    for domain in sorted(final_domains):
                        f.write(f"{domain}\n")
            
            print(f"📝 Blacklist dosyası güncellendi: {blacklist_path}")
            print(f"   → {len(sites)} site listeye eklendi")
            return str(blacklist_path)
            
        except Exception as e:
            print(f"❌ Blacklist dosyası oluşturma hatası: {e}")
            return None
    
    def get_blacklist_path(self) -> str:
        """Blacklist dosyasının yolunu döndür"""
        from pathlib import Path
        base_dir = Path(__file__).parent.parent
        external_dir = base_dir / "external"
        return str(external_dir / "blacklist.txt")
        
    def get_allowed_ips(self) -> List[str]:
        """İzin verilen IP adreslerini döndür"""
        return self.config.get('allowed_ips', [])
        
    def add_allowed_ip(self, ip: str) -> bool:
        """İzin verilen IP'lere yeni IP ekle"""
        if self.validate_ip(ip) and ip not in self.config.get('allowed_ips', []):
            self.config.setdefault('allowed_ips', []).append(ip)
            self.save_config()
            return True
        return False
        
    def remove_allowed_ip(self, ip: str) -> bool:
        """İzin verilen IP'lerden IP kaldır"""
        if ip in self.config.get('allowed_ips', []):
            self.config['allowed_ips'].remove(ip)
            self.save_config()
            return True
        return False
        
    def get_blocked_sites(self) -> List[str]:
        """Engellenmiş siteleri döndür"""
        return self.config.get('blocked_sites', [])
        
    def add_blocked_site(self, site: str) -> bool:
        """Engellenmiş sitelere yeni site ekle"""
        if site not in self.config.get('blocked_sites', []):
            self.config.setdefault('blocked_sites', []).append(site)
            self.save_config()
            return True
        return False
        
    def remove_blocked_site(self, site: str) -> bool:
        """Engellenmiş sitelerden site kaldır"""
        if site in self.config.get('blocked_sites', []):
            self.config['blocked_sites'].remove(site)
            self.save_config()
            return True
        return False
        
    def get_technique_status(self, technique: str) -> bool:
        """Belirli bir tekniğin durumunu döndür"""
        return self.config.get('techniques', {}).get(technique, False)
        
    def set_technique_status(self, technique: str, status: bool):
        """Teknik durumunu ayarla"""
        self.config.setdefault('techniques', {})[technique] = status
        self.save_config()
        
    def get_setting(self, setting: str, default=None):
        """Ayarları döndür"""
        return self.config.get('settings', {}).get(setting, default)
        
    def set_setting(self, setting: str, value):
        """Ayar değiştir"""
        self.config.setdefault('settings', {})[setting] = value
        self.save_config()
        
    def validate_ip(self, ip: str) -> bool:
        """IP adresinin geçerliliğini kontrol et"""
        import ipaddress
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
            
    def validate_domain(self, domain: str) -> bool:
        """Domain adının geçerliliğini kontrol et"""
        import re
        pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(pattern.match(domain))
        
    def export_config(self, filename: str):
        """Konfigürasyonu dışa aktar"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                else:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Dışa aktarma hatası: {e}")
            return False
            
    def import_config(self, filename: str):
        """Konfigürasyonu içe aktar"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    imported_config = yaml.safe_load(f)
                else:
                    imported_config = json.load(f)
                    
            if imported_config:
                self.config = imported_config
                self.save_config()
                return True
        except Exception as e:
            print(f"İçe aktarma hatası: {e}")
        return False
        
    def reset_config(self):
        """Konfigürasyonu varsayılana sıfırla"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.config = self.load_config()
        
    def get_all_config(self) -> Dict[str, Any]:
        """Tüm konfigürasyonu döndür"""
        return self.config.copy()
    
    def get_dpi_tool(self) -> str:
        """Seçili DPI aracını döndür"""
        return self.config.get('settings', {}).get('dpi_tool', 'goodbyedpi')
    
    def set_dpi_tool(self, tool: str):
        """DPI aracını ayarla (goodbyedpi veya zapret)"""
        if tool in ['goodbyedpi', 'zapret']:
            self.config.setdefault('settings', {})['dpi_tool'] = tool
            self.save_config()
            return True
        return False
    
    def get_country_code(self) -> str:
        """Seçili ülke kodunu döndür"""
        return self.config.get('settings', {}).get('country_code', 'TR')
    
    def set_country_code(self, country_code: str):
        """Ülke kodunu ayarla"""
        self.config.setdefault('settings', {})['country_code'] = country_code
        self.save_config()
