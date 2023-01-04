# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from config.model import BaseModel


class StructureTag(BaseModel):
    name = sa.Column(sa.String(250))
    description = sa.Column(sa.String(500), nullable=True)


class Structure(BaseModel):
    aiida_pk = sa.Column(sa.Integer, nullable=True)
    filepath = sa.Column(sa.String(500), nullable=True)
    cover_img = sa.Column(sa.String(500), nullable=True)
    attributes = sa.Column(sa.JSON, nullable=True)
    tags = relationship("StructureTag", back_populates="structures",
                        nullable=True)
