from pydantic import BaseModel, Field


class ChangeTeacherRequest(BaseModel):
    """Schéma pro POST /subjects/{id}/change-teacher"""
    new_teacher_id: int = Field(..., gt=0, description="ID nového učitele")

    class Config:
        from_attributes = True


class PredmetResponse(BaseModel):
    """Schéma pro vrácení předmětu v API."""
    id: int
    nazev: str
    id_tridy: int
    id_ucitele: int
    pocet_hodin: int

    class Config:
        from_attributes = True


class TeacherOption(BaseModel):
    """Schéma pro select dropdown s učiteli."""
    id: int
    prijmeni: str

    class Config:
        from_attributes = True