from __future__ import annotations

from pydantic import BaseModel, ConfigDict


def _spinalcase_rename(field_name: str) -> str:
    return field_name.replace("_", "-")


class KebabCaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=_spinalcase_rename, populate_by_name=True)
