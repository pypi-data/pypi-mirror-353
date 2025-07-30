"""Definitions (constants)."""

JOINED = 'joined'
"""Indicates that the given attribute should be loaded
using joined eager loading (``sqlalchemy.orm.joinedload()``).
"""

SUBQUERY = 'subquery'
"""Indicates that the given attribute should be loaded
using subquery eager loading (``sqlalchemy.orm.subqueryload()``).
"""

SELECT_IN = 'selectin'
"""Indicates that the given attribute should be loaded
using SELECT IN eager loading (``sqlalchemy.orm.selectinload()``).
"""
