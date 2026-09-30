import logging
import time
from datetime import datetime
from typing import List, Dict, Tuple, Any

from jugaad_data.nse import NSELive

logger = logging.getLogger(__name__)

class NSEPreOpenClient:
    """Client wrapper for fetching pre-open market data from NSE using jugaad_data."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self._nse = NSELive()
    
    def _refresh_session(self) -> None:
        """Forces a new session by creating a new NSELive instance."""
        logger.info("Refreshing NSE session")
        self._nse = NSELive()

    def fetch_preopen_snapshot(self, category: str = 'FO') -> Tuple[List[Dict[str, Any]], datetime]:
        """
        Fetches the pre-open market snapshot for a given category.
        
        Args:
            category: The category of stocks (e.g., 'FO', 'NIFTY').
            
        Returns:
            A tuple containing a list of raw stock dictionaries and the fetch timestamp.
        """
        for attempt in range(self.max_retries):
            try:
                # Force fresh data cache clear by setting timeout to 0 temporarily
                self._nse.time_out = 0
                
                fetch_time = datetime.now()
                response = self._nse.pre_open_market(category)
                
                if not response:
                    logger.warning("Empty response from NSE API")
                    self._refresh_session()
                    time.sleep(2 ** attempt)
                    continue
                
                data = response.get('data', [])
                
                # Check for market closed or empty data
                if not data and response.get('msg') == "No Data Found":
                    logger.info("Market may be closed or no pre-open data found.")
                    return [], fetch_time
                    
                if not data:
                    logger.warning("Data field is empty, but no 'No Data Found' message. Refreshing session.")
                    self._refresh_session()
                    time.sleep(2 ** attempt)
                    continue
                    
                return data, fetch_time
                
            except Exception as e:
                logger.error(f"Error fetching pre-open snapshot (attempt {attempt + 1}): {e}", exc_info=True)
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("Max retries reached. Returning empty list.")
                    
        return [], datetime.now()
        
    def fetch_market_indices(self) -> Dict[str, Any]:
        """
        Fetches market indices like NIFTY 50 and all indices.
        
        Returns:
            A dictionary containing index data.
        """
        indices_data = {}
        try:
            self._nse.time_out = 0
            nifty = self._nse.live_index('NIFTY 50')
            if nifty:
                indices_data['NIFTY 50'] = nifty
                
            all_indices = self._nse.all_indices()
            if all_indices:
                indices_data['all'] = all_indices
                
        except Exception as e:
            logger.error(f"Error fetching market indices: {e}", exc_info=True)
            
        return indices_data

# Module-level convenience functions using a default client instance
_default_client = NSEPreOpenClient()

def fetch_preopen_snapshot(category: str = 'FO') -> Tuple[List[Dict[str, Any]], datetime]:
    """Fetches the pre-open market snapshot for a given category."""
    return _default_client.fetch_preopen_snapshot(category)

def fetch_market_indices() -> Dict[str, Any]:
    """Fetches market indices like NIFTY 50 and VIX."""
    return _default_client.fetch_market_indices()
