"""
Scheduler for Automatic Scraping
Handles periodic updates of product prices
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from database import Database
from scrapers import SercoPlusScraper, MemoryKingsScraper, PCImpactoScraper


class ScrapingScheduler:
    """Manages scheduled scraping tasks"""
    
    def __init__(self, db: Database):
        self.db = db
        self.is_running = False
        self.scheduler_thread = None
        
        # Initialize scrapers
        self.scrapers = {
            'SercoPlus': SercoPlusScraper(),
            'MemoryKings': MemoryKingsScraper(),
            'PCImpacto': PCImpactoScraper()
        }
    
    def add_scraping_task(self, store_name: str, url: str, category: str = '', 
                         frequency_hours: int = 24) -> bool:
        """
        Adds a new scraping task to the schedule
        
        Args:
            store_name: Name of the store
            url: URL to scrape
            category: Category name (optional)
            frequency_hours: How often to scrape (in hours)
            
        Returns:
            True if successful
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            next_run = datetime.now() + timedelta(hours=frequency_hours)
            
            cursor.execute("""
                INSERT INTO scraping_schedule 
                (store_name, url, category, frequency_hours, next_run, is_active)
                VALUES (?, ?, ?, ?, ?, 1)
            """, (store_name, url, category, frequency_hours, next_run.isoformat()))
            
            conn.commit()
            conn.close()
            
            print(f"✅ Tarea de scraping agregada: {store_name} - {category}")
            return True
            
        except Exception as e:
            print(f"❌ Error agregando tarea: {e}")
            conn.close()
            return False
    
    def get_pending_tasks(self) -> List[Dict]:
        """Gets all tasks that are ready to run"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            SELECT * FROM scraping_schedule 
            WHERE is_active = 1 
            AND (next_run IS NULL OR next_run <= ?)
            ORDER BY next_run
        """, (now,))
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks
    
    def update_task(self, task_id: int, last_run: datetime = None, 
                   next_run: datetime = None) -> bool:
        """Updates task timestamps"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            if last_run and next_run:
                cursor.execute("""
                    UPDATE scraping_schedule 
                    SET last_run = ?, next_run = ?
                    WHERE id = ?
                """, (last_run.isoformat(), next_run.isoformat(), task_id))
            elif last_run:
                cursor.execute("""
                    UPDATE scraping_schedule 
                    SET last_run = ?
                    WHERE id = ?
                """, (last_run.isoformat(), task_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating task: {e}")
            conn.close()
            return False
    
    def log_scraping_run(self, store_name: str, url: str, products_found: int,
                        products_saved: int, status: str, error_message: str = None,
                        duration: float = 0.0, started_at: datetime = None,
                        completed_at: datetime = None) -> bool:
        """Logs a scraping run"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO scraping_logs 
                (store_name, url, products_found, products_saved, status, 
                 error_message, duration_seconds, started_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                store_name, url, products_found, products_saved, status,
                error_message, duration, 
                started_at.isoformat() if started_at else None,
                completed_at.isoformat() if completed_at else None
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error logging scraping run: {e}")
            conn.close()
            return False
    
    def run_scraping_task(self, task: Dict) -> Dict:
        """
        Executes a single scraping task
        
        Args:
            task: Task dictionary from database
            
        Returns:
            Result dictionary with statistics
        """
        store_name = task['store_name']
        url = task['url']
        
        print(f"\n🚀 Iniciando scraping: {store_name} - {url}")
        
        started_at = datetime.now()
        result = {
            'products_found': 0,
            'products_saved': 0,
            'status': 'failed',
            'error_message': None
        }
        
        try:
            # Get appropriate scraper
            scraper = self.scrapers.get(store_name)
            
            if not scraper:
                raise ValueError(f"No scraper available for store: {store_name}")
            
            # Scrape the page
            products = scraper.scrape_category_page(url)
            
            if not products:
                result['status'] = 'no_products'
                result['error_message'] = 'No products found'
                return result
            
            result['products_found'] = len(products)
            
            # Save products to database
            saved_count = 0
            for product in products:
                if self.db.insert_product(product):
                    saved_count += 1
            
            result['products_saved'] = saved_count
            result['status'] = 'success'
            
            print(f"✅ Scraping completado: {saved_count}/{len(products)} productos guardados")
            
        except Exception as e:
            result['error_message'] = str(e)
            print(f"❌ Error durante scraping: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            completed_at = datetime.now()
            duration = (completed_at - started_at).total_seconds()
            
            # Log the run
            self.log_scraping_run(
                store_name=store_name,
                url=url,
                products_found=result['products_found'],
                products_saved=result['products_saved'],
                status=result['status'],
                error_message=result['error_message'],
                duration=duration,
                started_at=started_at,
                completed_at=completed_at
            )
            
            # Update task schedule
            frequency_hours = task.get('frequency_hours', 24)
            next_run = datetime.now() + timedelta(hours=frequency_hours)
            self.update_task(task['id'], last_run=completed_at, next_run=next_run)
        
        return result
    
    def check_and_run_tasks(self):
        """Checks for pending tasks and runs them"""
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            return
        
        print(f"\n📋 Encontradas {len(pending_tasks)} tareas pendientes")
        
        for task in pending_tasks:
            self.run_scraping_task(task)
            
            # Small delay between tasks to be respectful
            time.sleep(5)
    
    def start_scheduler(self):
        """Starts the scheduler in a background thread"""
        if self.is_running:
            print("⚠️ Scheduler ya está corriendo")
            return
        
        self.is_running = True
        
        # Schedule check every hour
        schedule.every(1).hours.do(self.check_and_run_tasks)
        
        # Also check immediately on start
        schedule.every(5).minutes.do(self.check_and_run_tasks)
        
        def run_scheduler():
            print("✅ Scheduler iniciado")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print("🕐 Scheduler corriendo en segundo plano")
    
    def stop_scheduler(self):
        """Stops the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        schedule.clear()
        print("⏹️ Scheduler detenido")
    
    def get_scraping_logs(self, limit: int = 50, store_name: str = None) -> List[Dict]:
        """Gets recent scraping logs"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if store_name:
            cursor.execute("""
                SELECT * FROM scraping_logs 
                WHERE store_name = ?
                ORDER BY started_at DESC 
                LIMIT ?
            """, (store_name, limit))
        else:
            cursor.execute("""
                SELECT * FROM scraping_logs 
                ORDER BY started_at DESC 
                LIMIT ?
            """, (limit,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    
    def get_schedule_status(self) -> Dict:
        """Gets overall scheduler status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total active tasks
        cursor.execute("""
            SELECT COUNT(*) as count FROM scraping_schedule WHERE is_active = 1
        """)
        total_tasks = cursor.fetchone()['count']
        
        # Pending tasks
        now = datetime.now().isoformat()
        cursor.execute("""
            SELECT COUNT(*) as count FROM scraping_schedule 
            WHERE is_active = 1 AND (next_run IS NULL OR next_run <= ?)
        """, (now,))
        pending_tasks = cursor.fetchone()['count']
        
        # Recent logs
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM scraping_logs 
            WHERE completed_at >= datetime('now', '-24 hours')
            GROUP BY status
        """)
        recent_runs = {row['status']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'is_running': self.is_running,
            'total_active_tasks': total_tasks,
            'pending_tasks': pending_tasks,
            'recent_runs_24h': recent_runs
        }


# Predefined store URLs for common categories
STORE_URLS = {
    'SercoPlus': {
        'procesadores_intel_1700': 'https://sercoplus.com/765-cpu-1700-12va-generacion',
        'procesadores_intel_1200': 'https://sercoplus.com/764-cpu-1200-11va-generacion',
        'procesadores_amd': 'https://sercoplus.com/758-cpu-am4-ryzen-serie-3000-4000-5000',
        'tarjetas_graficas': 'https://sercoplus.com/759-tarjetas-de-video'
    },
    'MemoryKings': {
        'procesadores_intel': 'https://memorykings.pe/productos/Procesadores',
        'tarjetas_graficas': 'https://memorykings.pe/productos/Graficos'
    },
    'PCImpacto': {
        'procesadores': 'https://www.impacto.com.pe/catalogo?categoria=procesadores',
        'tarjetas_graficas': 'https://www.impacto.com.pe/catalogo?categoria=tarjetas-graficas'
    }
}
