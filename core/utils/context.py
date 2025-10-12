"""
Script Python para a finalidade de 'context'.
"""

from contextvars import ContextVar

correlation_id_var = ContextVar('correlation_id', default=None)
