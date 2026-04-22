"""
GreenWing Analytics - Fleet Analyzer
Filo performans analizi ve veri yönetimi
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
from loguru import logger


class FleetAnalyzer:
    """
    Havayolu filosu için yakıt verimliliği ve emisyon analizi yapar.
    """
    
    def __init__(self):
        self.flights = []
        logger.info("FleetAnalyzer başlatıldı")
    
    def add_manual_flight(self, origin: str, destination: str, fuel_kg: float,
                          distance_nm: float, aircraft_type: str, 
                          cruise_altitude_ft: float = 35000):
        """Manuel uçuş verisi ekler"""
        
        flight = {
            'origin': origin,
            'destination': destination,
            'route': f"{origin}-{destination}",
            'fuel_kg': fuel_kg,
            'distance_nm': distance_nm,
            'aircraft_type': aircraft_type,
            'cruise_altitude_ft': cruise_altitude_ft,
            'co2_kg': fuel_kg * 3.16,
            'fuel_per_nm': fuel_kg / distance_nm if distance_nm > 0 else 0,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        self.flights.append(flight)
    
    def generate_fleet_summary(self) -> Dict:
        """Filo özet istatistiklerini üretir"""
        
        if not self.flights:
            self._create_demo_data()
        
        df = pd.DataFrame(self.flights)
        
        total_fuel_kg = df['fuel_kg'].sum()
        total_co2_kg = df['co2_kg'].sum()
        total_distance_nm = df['distance_nm'].sum()
        
        avg_fuel_per_nm = df['fuel_per_nm'].mean()
        efficiency_score = max(0, min(100, 100 - ((avg_fuel_per_nm - 8.5) / 8.5 * 100)))
        
        route_analysis = self._analyze_routes(df)
        benchmark = self._calculate_benchmark(avg_fuel_per_nm)
        savings = self._calculate_savings_potential(df, avg_fuel_per_nm)
        altitude_perf = self._analyze_altitude_performance(df)
        
        summary = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_flights_analyzed': len(self.flights),
            },
            'fleet_summary': {
                'total_fuel_tonnes': total_fuel_kg / 1000,
                'total_co2_tonnes': total_co2_kg / 1000,
                'total_distance_nm': total_distance_nm,
                'avg_fuel_per_flight_kg': df['fuel_kg'].mean(),
                'avg_fuel_per_nm': avg_fuel_per_nm,
                'fleet_efficiency_score': round(efficiency_score, 1),
                'unique_aircraft': df['aircraft_type'].nunique(),
                'unique_routes': df['route'].nunique()
            },
            'route_analysis': route_analysis,
            'benchmark': benchmark,
            'savings_potential': savings,
            'altitude_performance': altitude_perf
        }
        
        return summary
    
    def _create_demo_data(self):
        """Demo uçuş verileri oluşturur"""
        
        demo_flights = [
            ('IST', 'LHR', 12500, 1560, 'B738', 37000),
            ('IST', 'LHR', 12800, 1560, 'B738', 35000),
            ('LHR', 'IST', 11500, 1560, 'B738', 37000),
            ('IST', 'FRA', 8500, 1000, 'B738', 37000),
            ('IST', 'FRA', 8900, 1000, 'B738', 35000),
            ('FRA', 'IST', 8200, 1000, 'B738', 37000),
            ('IST', 'DXB', 42000, 1550, 'B77W', 39000),
            ('IST', 'ESB', 3200, 190, 'B738', 33000),
            ('IST', 'ESB', 3400, 190, 'B738', 31000),
            ('SAW', 'AMS', 4200, 1350, 'A320', 35000),
        ]
        
        for f in demo_flights:
            self.add_manual_flight(
                origin=f[0], destination=f[1],
                fuel_kg=f[2], distance_nm=f[3],
                aircraft_type=f[4], cruise_altitude_ft=f[5]
            )
    
    def _analyze_routes(self, df: pd.DataFrame) -> Dict:
        """Rota bazlı performans analizi"""
        
        route_stats = df.groupby('route').agg({
            'fuel_kg': ['mean', 'std', 'count'],
            'fuel_per_nm': 'mean',
            'co2_kg': 'sum'
        }).round(2)
        
        route_stats.columns = ['avg_fuel_kg', 'fuel_std', 'flights', 'fuel_per_nm', 'total_co2_kg']
        route_stats = route_stats.reset_index()
        
        rankings = route_stats.sort_values('fuel_per_nm', ascending=True).to_dict('records')
        
        return {
            'rankings': rankings[:10],
            'least_efficient_routes': rankings[-3:] if len(rankings) > 3 else rankings,
        }
    
    def _calculate_benchmark(self, fleet_avg_fuel_per_nm: float) -> Dict:
        """Sektör benchmark karşılaştırması"""
        
        industry_avg = 8.5
        industry_best = 7.2
        
        if fleet_avg_fuel_per_nm <= industry_avg * 0.95:
            rating = "Mükemmel"
        elif fleet_avg_fuel_per_nm <= industry_avg:
            rating = "İyi"
        elif fleet_avg_fuel_per_nm <= industry_avg * 1.1:
            rating = "Orta"
        else:
            rating = "İyileştirme Gerekli"
        
        return {
            'fleet_fuel_per_nm': round(fleet_avg_fuel_per_nm, 2),
            'industry_avg_fuel_per_nm': industry_avg,
            'industry_best_fuel_per_nm': industry_best,
            'gap_to_best_pct': round(((fleet_avg_fuel_per_nm - industry_best) / industry_best) * 100, 1),
            'rating': rating
        }
    
    def _calculate_savings_potential(self, df: pd.DataFrame, avg_fuel_per_nm: float) -> Dict:
        """Tasarruf potansiyeli"""
        
        industry_best = 7.2
        fuel_price_usd_per_tonne = 850
        
        total_distance = df['distance_nm'].sum()
        potential_saving_kg_per_nm = max(0, avg_fuel_per_nm - industry_best)
        potential_saving_kg = potential_saving_kg_per_nm * total_distance
        
        return {
            'estimated_fuel_saving_kg': round(potential_saving_kg, 0),
            'estimated_cost_saving_usd': round(potential_saving_kg / 1000 * fuel_price_usd_per_tonne, 0),
            'annualized_fuel_saving_tonnes': round(potential_saving_kg / 1000 * 2, 0),
            'annualized_cost_saving_usd': round(potential_saving_kg / 1000 * fuel_price_usd_per_tonne * 2, 0),
            'total_co2_saving_kg': round(potential_saving_kg * 3.16, 0)
        }
    
    def _analyze_altitude_performance(self, df: pd.DataFrame) -> Dict:
        """İrtifa performansı"""
        
        df['optimum_altitude_ft'] = df['distance_nm'].apply(
            lambda d: min(41000, 30000 + (d - 500) * 2 if d > 500 else 30000)
        )
        df['altitude_deviation_ft'] = abs(df['cruise_altitude_ft'] - df['optimum_altitude_ft'])
        df['sar_loss_pct'] = df['altitude_deviation_ft'] / 1000 * 1.5
        
        return {
            'avg_deviation_from_optimum_ft': round(df['altitude_deviation_ft'].mean(), 0),
            'avg_sar_loss_pct': round(df['sar_loss_pct'].mean(), 1),
            'flights_with_step_climb': int((df['cruise_altitude_ft'] > 35000).sum())
        }


if __name__ == "__main__":
    analyzer = FleetAnalyzer()
    summary = analyzer.generate_fleet_summary()
    print(f"✅ FleetAnalyzer çalışıyor! {summary['report_metadata']['total_flights_analyzed']} uçuş analiz edildi")