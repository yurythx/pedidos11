"""
Throttling (Rate Limiting) customizado para API.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class BurstRateThrottle(UserRateThrottle):
    """
    Rate limit para operações rápidas (burst).
    
    Limite: 60 requests/minuto
    Uso: Operações normais de leitura/escrita
    """
    scope = 'burst'


class SustainedRateThrottle(UserRateThrottle):
    """
    Rate limit sustentado.
    
    Limite: 1000 requests/hora
    Uso: Proteção geral da API
    """
    scope = 'sustained'


class VendaRateThrottle(UserRateThrottle):
    """
    Rate limit específico para vendas.
    
    Limite: 100 requests/minuto
    Uso: Evitar criação excessiva de vendas
    """
    scope = 'vendas'


class RelatorioRateThrottle(UserRateThrottle):
    """
    Rate limit para relatórios pesados.
    
    Limite: 10 requests/minuto
    Uso: Queries pesadas de relatórios
    """
    scope = 'relatorios'


class AnonStrictRateThrottle(AnonRateThrottle):
    """
    Rate limit estrito para usuários não autenticados.
    
    Limite: 20 requests/hora
    Uso: Proteção contra abuso
    """
    scope = 'anon_strict'
