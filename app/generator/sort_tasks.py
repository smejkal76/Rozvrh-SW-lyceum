"""
    generator/sort_tasks.py

    Krok 5. Heuristické řazení úloh podle obtížnosti umístění v rozvrhu.

    Podstata se děje ve funkci difficulty().  Používají se váhy, které určují relativní důležitost jednotlivých faktorů:
    - Počet hodin (×100): delší bloky mají výrazně vyšší prioritu, protože omezují volné sloty.
    - Blokace zdrojů (×2): čím více blokovaných slotů má třída, učitel nebo učebna, tím obtížnější je plánování.
    - Učebna (×20): úlohy s pevně určenou učebnou dostávají vyšší váhu – mají menší flexibilitu.
    - Náhodná složka (+0–9): malá náhodnost, aby se zabránilo deterministickým shlukům.
    - Délka svazku (+50(L-1)):* vícehodinové bloky (např. dvouhodinovky) mají vyšší prioritu i jako celek.
"""

import random
_rng = random.Random()

def _safe_sum_row(row, H):
    """Bezpečně sečte True hodnoty v řádku, i když má kratší délku než H+1."""
    L = min(H, len(row) - 1)
    if L <= 0:
        return 0
    return sum(1 for h in range(1, L + 1) if row[h])

def blocked_share(cal, u):
    """Vrací součet blokovaných slotů pro třídu, učitele a učebnu."""
    H = cal.H
    tr = 0; te = 0; r = 0
    for d in range(cal.D):
        tr += _safe_sum_row(cal.busy_trida[(u.id_tridy, d)], H)
        te += _safe_sum_row(cal.busy_ucitel[(u.id_ucitele, d)], H)
        if u.id_ucebny:
            r += _safe_sum_row(cal.busy_ucebna[(u.id_ucebny, d)], H)
    return tr + te + r

def difficulty(cal, item):
    """Výpočet obtížnosti umístění jedné úlohy nebo sloučené úlohy."""
    def single(u):
        # Základní skóre: delší bloky mají větší váhu (×100)
        base = 100*(u.pocet_hodin-1)
        # Kolize zdrojů: počet blokovaných slotů (×2)
        base += 2 * blocked_share(cal, u)
        # Pevná učebna: penalizace flexibilnosti (×20)
        if u.id_ucebny:
            base += 20
        # Malá náhodnost (+0–9) pro rozbití shluků
        base += _rng.randint(0, 9)
        return base

    # Pro sloučené úlohy (dvě půlené hodiny) se sčítají obtížnosti obou částí
    if hasattr(item, 'parts'):
        L = item.pocet_hodin
        total = sum(single(u) for u in item.parts)
        # Délka svazku (×50 na každou další hodinu) zvýhodní delší bloky
        total += 50 * (L - 1)
        return total
    return single(item)

def sort_items(cal, items):
    """Vrátí úlohy seřazené podle obtížnosti (složitější první)."""
    return sorted(items, key=lambda it: difficulty(cal, it), reverse=True)