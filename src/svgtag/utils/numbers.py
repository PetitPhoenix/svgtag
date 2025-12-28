"""Utilitaires de génération de nombres aléatoires pour tests"""
import random


def generate_random_numbers(n, length, repetition_prob=0.2, seed=None):
    """
    Génère n chaînes de chiffres aléatoires avec répétitions possibles.
    
    Args:
        n: Nombre de chaînes à générer
        length: Longueur de chaque chaîne (nombre de chiffres)
        repetition_prob: Probabilité d'avoir des répétitions (0.0 à 1.0)
        seed: Graine aléatoire pour reproductibilité
    
    Returns:
        Liste de n chaînes de chiffres
    
    Example:
        >>> generate_random_numbers(10, 10, repetition_prob=0.2, seed=42)
        ['8373615377', '6597306256', ...]
    """
    if seed is not None:
        random.seed(seed)
    
    chaines = []
    for _ in range(n):
        chaine = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        chaines.append(chaine)
    
    # Ajouter des répétitions
    if repetition_prob > 0:
        nb_repetitions = int(n * repetition_prob)
        for _ in range(nb_repetitions):
            idx = random.randint(0, n - 1)
            chaine_repetee = chaines[random.randint(0, n - 1)]
            chaines[idx] = chaine_repetee
    
    return chaines


def generate_test_set(difficulty='moyen', n=10, seed=None):
    """
    Génère un jeu de 10 chaînes pour test selon la difficulté.
    
    Args:
        difficulty: 'facile', 'moyen', 'difficile'
        n: Nombre de chaînes à renvoyer
        seed: Graine aléatoire pour reproductibilité
    
    Returns:
        Liste de n chaînes
    
    Example:
        >>> generate_narcosis_test_set('facile', seed=42)
        ['837361', '659730', ...]
    """
    config = {
        'facile': {'length': 6, 'repetition_prob': 0.3},
        'moyen': {'length': 10, 'repetition_prob': 0.2},
        'difficile': {'length': 12, 'repetition_prob': 0.1},
    }
    
    if difficulty not in config:
        raise ValueError(f"Difficulté '{difficulty}' inconnue. Choisir parmi: {list(config.keys())}")
    
    params = config[difficulty]
    return generate_random_numbers(
        n,
        length=params['length'],
        repetition_prob=params['repetition_prob'],
        seed=seed
    )