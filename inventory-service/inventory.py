from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base

class ImportBatch(Base):
    __tablename__ = "import_batches"

    id= Column(Integer, primary_key=True, index=True)
    processed_rows =Column(Integer)
    valid_rows = Column(Integer)
    invalid_rows = Column(Integer)

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    condition = Column(String)
    defects = Column(String)
    batch_id = Column(Integer, ForeignKey("import_batches.id"))

class ImportError(Base):
    __tablename__ = "import_errors"

    id = Column(Integer, primary_key=True, index=True)
    row_number = Column(Integer)
    message = Column(String)
    batch_id = Column(Integer, ForeignKey("import_batches.id"))