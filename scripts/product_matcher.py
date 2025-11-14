"""
Product Comparison and Matching System
Intelligently matches products across different stores
"""

import re
from typing import List, Dict, Tuple, Optional
from difflib import SequenceMatcher
from database import Database


class ProductMatcher:
    """Matches products across different stores for price comparison"""
    
    def __init__(self, db: Database):
        self.db = db
        
    def normalize_for_comparison(self, name: str) -> str:
        """
        Aggressively normalizes product name for comparison
        Removes brands, common words, and standardizes format
        """
        # Convert to uppercase
        name = name.upper()
        
        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove common prefixes
        prefixes = [
            'PROCESADOR', 'PROCESSOR', 'CPU',
            'TARJETA GRAFICA', 'TARJETA GRÁFICA', 'GPU',
            'MEMORIA', 'RAM',
            'DISCO', 'SSD', 'HDD',
            'PLACA', 'MOTHER', 'MOTHERBOARD'
        ]
        for prefix in prefixes:
            if name.startswith(prefix):
                name = name[len(prefix):].strip()
        
        # Remove brand names (they're stored separately)
        brands = [
            'INTEL', 'AMD', 'NVIDIA', 'ASUS', 'MSI', 'GIGABYTE', 'ASROCK',
            'CORSAIR', 'KINGSTON', 'SAMSUNG', 'WESTERN DIGITAL', 'WD',
            'SEAGATE', 'CRUCIAL', 'G.SKILL', 'HYPERX', 'RAZER',
            'LOGITECH', 'COOLER MASTER', 'NZXT', 'THERMALTAKE'
        ]
        for brand in brands:
            name = name.replace(brand, ' ')
        
        # Remove special characters and extra whitespace
        name = re.sub(r'[^\w\s]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def extract_model_number(self, name: str) -> Optional[str]:
        """
        Extracts the core model number from product name
        e.g., "Intel Core i7-12700F" -> "I7-12700F"
        """
        name = name.upper()
        
        # Intel patterns
        intel_match = re.search(r'(I[357][-\s]?\d{4,5}[A-Z]*)', name)
        if intel_match:
            return intel_match.group(1).replace(' ', '-')
        
        # AMD Ryzen patterns
        ryzen_match = re.search(r'(RYZEN\s*[357]\s*\d{4}[A-Z]*)', name)
        if ryzen_match:
            return ryzen_match.group(1).replace(' ', '')
        
        # NVIDIA GPU patterns
        nvidia_match = re.search(r'(RTX|GTX)\s*(\d{4}\s*TI|\d{4})', name)
        if nvidia_match:
            return (nvidia_match.group(1) + nvidia_match.group(2)).replace(' ', '')
        
        # AMD GPU patterns
        amd_gpu_match = re.search(r'(RX\s*\d{4}\s*XT|\RX\s*\d{4})', name)
        if amd_gpu_match:
            return amd_gpu_match.group(1).replace(' ', '')
        
        # Generic pattern: letters followed by numbers
        generic_match = re.search(r'([A-Z]{2,}[-\s]?\d{3,}[A-Z]*)', name)
        if generic_match:
            return generic_match.group(1).replace(' ', '-')
        
        return None
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculates similarity score between two product names
        Returns 0.0 to 1.0
        """
        # Normalize both names
        norm1 = self.normalize_for_comparison(name1)
        norm2 = self.normalize_for_comparison(name2)
        
        # Use SequenceMatcher for fuzzy matching
        similarity = SequenceMatcher(None, norm1, norm2).ratio()
        
        # Boost similarity if model numbers match
        model1 = self.extract_model_number(name1)
        model2 = self.extract_model_number(name2)
        
        if model1 and model2 and model1 == model2:
            similarity = max(similarity, 0.9)  # Boost to at least 0.9
        
        return similarity
    
    def find_matches(self, product: Dict, threshold: float = 0.75) -> List[Dict]:
        """
        Finds matching products from other stores
        
        Args:
            product: Product dictionary to match
            threshold: Minimum similarity score (0.0 to 1.0)
            
        Returns:
            List of matching products with similarity scores
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get products from other stores with same component type
        cursor.execute("""
            SELECT * FROM products 
            WHERE store != ? 
            AND component_type = ?
            AND is_active = 1
        """, (product['store'], product.get('component_type', '')))
        
        candidates = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        matches = []
        
        for candidate in candidates:
            # Calculate similarity
            similarity = self.calculate_similarity(product['name'], candidate['name'])
            
            # Check if brands match (if both have brand info)
            if product.get('brand') and candidate.get('brand'):
                if product['brand'].upper() != candidate['brand'].upper():
                    similarity *= 0.7  # Penalize if brands don't match
            
            # Check if SKUs match
            if product.get('sku') and candidate.get('sku'):
                if product['sku'].upper() == candidate['sku'].upper():
                    similarity = max(similarity, 0.95)  # Very high confidence
            
            if similarity >= threshold:
                matches.append({
                    'product': candidate,
                    'similarity': similarity,
                    'match_reason': self._get_match_reason(product, candidate, similarity)
                })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches
    
    def _get_match_reason(self, prod1: Dict, prod2: Dict, similarity: float) -> str:
        """Determines the reason for the match"""
        if prod1.get('sku') and prod2.get('sku'):
            if prod1['sku'].upper() == prod2['sku'].upper():
                return 'exact_sku_match'
        
        model1 = self.extract_model_number(prod1['name'])
        model2 = self.extract_model_number(prod2['name'])
        
        if model1 and model2 and model1 == model2:
            return 'model_number_match'
        
        if similarity >= 0.9:
            return 'high_name_similarity'
        elif similarity >= 0.75:
            return 'medium_name_similarity'
        else:
            return 'low_name_similarity'
    
    def compare_product_prices(self, product_name: str, component_type: str = None) -> Optional[Dict]:
        """
        Compares prices for a product across all stores
        
        Args:
            product_name: Product name to search for
            component_type: Optional component type filter
            
        Returns:
            Dict with comparison results or None if no matches
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Search for products matching the name
        search_term = f"%{product_name}%"
        
        if component_type:
            cursor.execute("""
                SELECT * FROM products 
                WHERE name LIKE ? AND component_type = ? AND is_active = 1
                ORDER BY price_usd ASC
            """, (search_term, component_type))
        else:
            cursor.execute("""
                SELECT * FROM products 
                WHERE name LIKE ? AND is_active = 1
                ORDER BY price_usd ASC
            """, (search_term,))
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        if not products:
            return None
        
        # Group by store
        by_store = {}
        for prod in products:
            store = prod['store']
            if store not in by_store:
                by_store[store] = []
            by_store[store].append(prod)
        
        # Find the best match from each store
        best_matches = []
        reference_product = products[0]  # Use first product as reference
        
        for store, store_products in by_store.items():
            # Find best matching product from this store
            best_match = None
            best_similarity = 0.0
            
            for prod in store_products:
                similarity = self.calculate_similarity(reference_product['name'], prod['name'])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = prod
            
            if best_match and best_similarity >= 0.6:  # Lower threshold for search results
                best_matches.append({
                    **best_match,
                    'match_confidence': best_similarity
                })
        
        if not best_matches:
            return None
        
        # Sort by price
        best_matches.sort(key=lambda x: x['price_usd'])
        
        lowest = best_matches[0]
        highest = best_matches[-1]
        
        return {
            'product_name': reference_product['name'],
            'total_stores': len(best_matches),
            'matches': best_matches,
            'lowest_price': {
                'store': lowest['store'],
                'price_usd': lowest['price_usd'],
                'price_local': lowest.get('price_local'),
                'url': lowest.get('source_url'),
                'stock': lowest.get('stock')
            },
            'highest_price': {
                'store': highest['store'],
                'price_usd': highest['price_usd'],
                'price_local': highest.get('price_local')
            },
            'price_difference_usd': highest['price_usd'] - lowest['price_usd'],
            'savings_percentage': round(
                ((highest['price_usd'] - lowest['price_usd']) / highest['price_usd']) * 100, 
                2
            ) if highest['price_usd'] > 0 else 0
        }
    
    def create_match_record(self, product_id_1: int, product_id_2: int, 
                           confidence: float, method: str) -> bool:
        """Creates a match record in the database"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO product_matches 
                (product_id_1, product_id_2, confidence, match_method)
                VALUES (?, ?, ?, ?)
            """, (product_id_1, product_id_2, confidence, method))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating match record: {e}")
            conn.close()
            return False
    
    def batch_match_products(self, component_type: str = None, threshold: float = 0.8):
        """
        Batch process to find and record matches across all products
        Useful for initial setup or periodic re-matching
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get all products
        if component_type:
            cursor.execute("""
                SELECT * FROM products 
                WHERE component_type = ? AND is_active = 1
                ORDER BY store, name
            """, (component_type,))
        else:
            cursor.execute("""
                SELECT * FROM products 
                WHERE is_active = 1
                ORDER BY component_type, store, name
            """)
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        matches_found = 0
        
        for i, product in enumerate(products):
            print(f"Matching product {i+1}/{len(products)}: {product['name'][:50]}...")
            
            matches = self.find_matches(product, threshold)
            
            for match in matches:
                matched_product = match['product']
                similarity = match['similarity']
                reason = match['match_reason']
                
                # Create match record
                if self.create_match_record(
                    product['id'], 
                    matched_product['id'],
                    similarity,
                    reason
                ):
                    matches_found += 1
                    print(f"  ✓ Matched with {matched_product['store']}: {matched_product['name'][:40]} ({similarity:.2f})")
        
        print(f"\n✅ Total matches created: {matches_found}")
        return matches_found
