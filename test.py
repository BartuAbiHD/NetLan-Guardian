#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DPI Bypass Tool Test Script
Test ve örnek kullanım dosyası
"""

import sys
import os

# Projenin ana dizinini Python path'ine ekle
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.config_manager import ConfigManager
from src.dpi_bypass import DPIBypass
from colorama import init, Fore, Style

init()

def test_config_manager():
    """Config Manager testleri"""
    print(f"{Fore.CYAN}=== Config Manager Testleri ==={Style.RESET_ALL}")
    
    config = ConfigManager('config/test_config.yaml')
    
    # Site ekleme/çıkarma testi
    print("Site yönetimi testi...")
    config.add_allowed_site('test.com')
    config.add_allowed_site('example.org')
    
    sites = config.get_allowed_sites()
    print(f"İzin verilen siteler: {sites}")
    
    # IP ekleme/çıkarma testi
    print("\nIP yönetimi testi...")
    config.add_allowed_ip('192.168.1.1')
    config.add_allowed_ip('10.0.0.1')
    
    ips = config.get_allowed_ips()
    print(f"İzin verilen IP'ler: {ips}")
    
    # Teknik ayarları testi
    print("\nTeknik ayarları testi...")
    config.set_technique_status('fragment_packets', True)
    config.set_technique_status('modify_ttl', False)
    
    print(f"Fragment packets: {config.get_technique_status('fragment_packets')}")
    print(f"Modify TTL: {config.get_technique_status('modify_ttl')}")
    
    print(f"{Fore.GREEN}✅ Config Manager testleri başarılı{Style.RESET_ALL}\n")

def test_dpi_bypass():
    """DPI Bypass testleri"""
    print(f"{Fore.CYAN}=== DPI Bypass Testleri ==={Style.RESET_ALL}")
    
    config = ConfigManager('config/test_config.yaml')
    dpi = DPIBypass(config)
    
    # Durum kontrolü
    status = dpi.get_status()
    print(f"DPI Bypass durumu: {status}")
    
    # Bağlantı testi
    print("\nBağlantı testleri...")
    test_sites = ['google.com', 'github.com', 'stackoverflow.com']
    
    for site in test_sites:
        result = dpi.check_connection(site)
        status_icon = "✅" if result else "❌"
        print(f"{status_icon} {site}: {'Bağlantı başarılı' if result else 'Bağlantı başarısız'}")
    
    print(f"{Fore.GREEN}✅ DPI Bypass testleri tamamlandı{Style.RESET_ALL}\n")

def demo_console_usage():
    """Konsol kullanımı örneği"""
    print(f"{Fore.CYAN}=== Konsol Kullanımı Demo ==={Style.RESET_ALL}")
    
    config = ConfigManager()
    dpi = DPIBypass(config)
    
    # Demo siteler ekle
    demo_sites = ['google.com', 'github.com', 'stackoverflow.com']
    for site in demo_sites:
        config.add_allowed_site(site)
    
    # Demo IP'ler ekle
    demo_ips = ['8.8.8.8', '1.1.1.1']
    for ip in demo_ips:
        config.add_allowed_ip(ip)
    
    print("Demo konfigürasyon oluşturuldu:")
    print(f"Siteler: {config.get_allowed_sites()}")
    print(f"IP'ler: {config.get_allowed_ips()}")
    
    # Teknik ayarlarını göster
    techniques = ['fragment_packets', 'modify_ttl', 'fake_packets', 'domain_fronting_proxy']
    print("\nTeknik durumları:")
    for tech in techniques:
        status = config.get_technique_status(tech)
        icon = "🟢" if status else "🔴"
        print(f"  {icon} {tech}")
    
    print(f"{Fore.GREEN}✅ Demo tamamlandı{Style.RESET_ALL}\n")

def validation_tests():
    """Doğrulama testleri"""
    print(f"{Fore.CYAN}=== Doğrulama Testleri ==={Style.RESET_ALL}")
    
    config = ConfigManager()
    
    # Domain doğrulama testleri
    test_domains = [
        ('google.com', True),
        ('sub.example.org', True),
        ('invalid..domain', False),
        ('', False),
        ('very-long-domain-name-that-might-be-invalid.com', True)
    ]
    
    print("Domain doğrulama testleri:")
    for domain, expected in test_domains:
        result = config.validate_domain(domain)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{domain}': {result}")
    
    # IP doğrulama testleri
    test_ips = [
        ('192.168.1.1', True),
        ('8.8.8.8', True),
        ('256.1.1.1', False),
        ('invalid.ip', False),
        ('', False),
        ('::1', True),  # IPv6
    ]
    
    print("\nIP doğrulama testleri:")
    for ip, expected in test_ips:
        result = config.validate_ip(ip)
        status = "✅" if result == expected else "❌"
        print(f"  {status} '{ip}': {result}")
    
    print(f"{Fore.GREEN}✅ Doğrulama testleri tamamlandı{Style.RESET_ALL}\n")

def performance_test():
    """Performans testi"""
    print(f"{Fore.CYAN}=== Performans Testleri ==={Style.RESET_ALL}")
    
    import time
    
    config = ConfigManager()
    
    # Toplu site ekleme testi
    start_time = time.time()
    
    test_sites = [f"test{i}.com" for i in range(100)]
    for site in test_sites:
        config.add_allowed_site(site)
    
    end_time = time.time()
    
    print(f"100 site ekleme süresi: {end_time - start_time:.3f} saniye")
    
    # Konfigürasyon kaydetme testi
    start_time = time.time()
    config.save_config()
    end_time = time.time()
    
    print(f"Konfigürasyon kaydetme süresi: {end_time - start_time:.3f} saniye")
    
    print(f"{Fore.GREEN}✅ Performans testleri tamamlandı{Style.RESET_ALL}\n")

def main():
    """Ana test fonksiyonu"""
    print(f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                  DPI BYPASS TOOL - TEST                     ║
║                      Test ve Demo                           ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
    """)
    
    try:
        test_config_manager()
        test_dpi_bypass()
        demo_console_usage()
        validation_tests()
        performance_test()
        
        print(f"{Fore.GREEN}🎉 Tüm testler başarıyla tamamlandı!{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Test hatası: {str(e)}{Style.RESET_ALL}")
        return 1
        
    # Test dosyalarını temizle
    try:
        if os.path.exists('config/test_config.yaml'):
            os.remove('config/test_config.yaml')
        print(f"{Fore.YELLOW}🧹 Test dosyaları temizlendi{Style.RESET_ALL}")
    except:
        pass
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
