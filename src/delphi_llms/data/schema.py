from pydantic import BaseModel


class DatasetRow(BaseModel):
    item_id: str
