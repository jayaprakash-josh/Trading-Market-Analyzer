import re

with open('preopen_analyzer/main.py', 'r') as f:
    text = f.read()

match = re.search(r'    def _build_fno_candidates\(self, candidates_long\):.*?    def _sort_and_rank_fno\(self, fno_candidates\):', text, re.DOTALL)
if match:
    replacement = '''    def _build_fno_candidates(self, candidates_long):
        """Filter F&O stocks from long candidates, fetch OI data, and produce combined scores."""
        try:
            fno_symbols = self._get_fno_symbol_set()
            if not fno_symbols:
                logger.warning("Could not fetch F&O symbol list. Skipping F&O table.")
                return []

            fno_candidates = self._filter_fno_candidates(candidates_long, fno_symbols)
            if not fno_candidates:
                logger.info("No valid F&O candidates found in LONG pool.")
                return []

            self._apply_fno_scores(fno_candidates)
            self._sort_and_rank_fno(fno_candidates)

            logger.info(f"F&O OI-Confirmed: {len(fno_candidates[:10])} stocks ranked.")
            return fno_candidates[:10]

        except Exception as e:
            logger.error(f"F&O pipeline failed: {e}", exc_info=True)
            return []

    def _get_fno_symbol_set(self):
        """Fetch and return the set of F&O eligible symbols."""
        from preopen_analyzer.fno_client import get_fno_symbols
        symbols = get_fno_symbols()
        return set(symbols if symbols else set()

    def _filter_fno_candidates(self, candidates_long, fno_symbols):
        """Filter candidates to only include F&O stocks that passed hard filters."""
        return [c for c in candidates_long if not c.is_rejected and c.symbol in fno_symbols]

    def _apply_fno_scores(self, fno_candidates):
        """Apply F&O OI scoring to each candidate."""
        from preopen_analyzer.fno_client import fetch_fno_data_for_symbol
        for c in fno_candidates:
            futures_info, oc_data = fetch_fno_data_for_symbol(c.symbol)
            futures_data = {c.symbol: futures_info} if futures_info else {}
            
            fno_result = calculate_fno_score(c.symbol, c.latest_iep, c.prev_close, futures_data, oc_data)

            c.fno_buildup = fno_result['buildup_type']
            c.fno_pcr = fno_result['pcr']
            c.fno_oi_score = fno_result['fno_oi_score']
            c.fno_combined_score = calculate_combined_fno_score(c.opening_strength_score, c.fno_oi_score)

    def _sort_and_rank_fno(self, fno_candidates):'''
    new_text = text[:match.start()] + replacement + text[match.end()-41:]
    with open('preopen_analyzer/main.py', 'w') as f:
        f.write(new_text)
    print('main.py successfully updated.')
else:
    print('Failed to find match in main.py.')
