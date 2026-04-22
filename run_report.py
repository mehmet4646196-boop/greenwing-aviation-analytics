"""
GreenWing Analytics - Rapor Üretim Demo
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.analysis.fleet_analyzer import FleetAnalyzer
from src.reporting.report_generator import ReportGenerator

def main():
    print("\n" + "="*60)
    print("  GREENWING ANALYTICS - RAPOR ÜRETİM SİSTEMİ")
    print("="*60)
    
    print("\n📊 Adım 1: Fleet Analyzer başlatılıyor...")
    analyzer = FleetAnalyzer()
    fleet_summary = analyzer.generate_fleet_summary()
    
    print(f"   ✅ {fleet_summary['report_metadata']['total_flights_analyzed']} uçuş analiz edildi")
    
    print("\n📄 Adım 2: Profesyonel rapor üretiliyor...")
    generator = ReportGenerator()
    
    result = generator.generate_fleet_report(
        fleet_summary=fleet_summary,
        airline_name="Demo Airlines",
        reporting_period="Ocak - Haziran 2025"
    )
    
    print("\n" + "="*60)
    print("  ✅ RAPOR BAŞARIYLA ÜRETİLDİ!")
    print("="*60)
    print(f"\n📁 HTML Rapor: {result['html_path']}")
    
    # Raporu aç
    os.system(f"start {result['html_path']}")

if __name__ == "__main__":
    main()