from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import date, datetime

# ===== CLIENT =====
class ClientBase(BaseModel):
    nom: str = Field(..., max_length=50)
    prenom: str = Field(..., max_length=50)
    cin: int = Field(..., gt=0, le=99999999, description="8 chiffres max")
    adresse: Optional[str] = None
    email: Optional[EmailStr] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id_client: str
    
    class Config:
        orm_mode = True

# ===== LIGNE TÉLÉPHONIQUE =====
class LigneTelephoniqueBase(BaseModel):
    debit_internet: Optional[str] = Field(None, max_length=20)
    etat: Optional[str] = Field(None, regex="^(actif|inactif)$")

class LigneTelephoniqueCreate(LigneTelephoniqueBase):
    id_client: str

class LigneTelephonique(LigneTelephoniqueBase):
    num_ligne: str
    id_client: str
    
    class Config:
        orm_mode = True

# ===== FACTURE =====
class FactureBase(BaseModel):
    date_emission: date
    montant: float = Field(..., gt=0)
    statut_paiement: str = Field(..., regex="^(payée|impayée)$")

class FactureCreate(FactureBase):
    num_ligne: str

class Facture(FactureBase):
    id_facture: str
    num_ligne: str
    
    class Config:
        orm_mode = True

# ===== RÉCLAMATION =====
class ReclamationBase(BaseModel):
    type_probleme: Optional[str] = Field(None, max_length=100)
    etat: Optional[str] = Field(None, regex="^(en cours|résolue)$")

class ReclamationCreate(ReclamationBase):
    num_ligne: str

class Reclamation(ReclamationBase):
    id_reclamation: str
    num_ligne: str
    date_reclamation: datetime
    
    class Config:
        orm_mode = True

# ===== HISTORIQUE DIALOGUE =====
class HistoriqueDialogueBase(BaseModel):
    message_utilisateur: str
    reponse_chatbot: str

class HistoriqueDialogueCreate(HistoriqueDialogueBase):
    id_reclamation: str

class HistoriqueDialogue(HistoriqueDialogueBase):
    id_dialogue: str
    id_reclamation: str
    timestamp: datetime
    
    class Config:
        orm_mode = True