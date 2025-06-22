from sqlalchemy import Column, Integer, String, Numeric, Date, TIMESTAMP, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database.base import Base

class Client(Base):
    __tablename__ = "client"
    
    id_client = Column(String(15), primary_key=True)
    nom = Column(String(50), nullable=False)
    prenom = Column(String(50), nullable=False)
    cin = Column(Integer, nullable=False)
    adresse = Column(Text)
    email = Column(String(100))
    
    lignes = relationship("LigneTelephonique", back_populates="client")

class LigneTelephonique(Base):
    __tablename__ = "lignetelephonique"
    
    num_ligne = Column(String(10), primary_key=True)
    id_client = Column(String(15), ForeignKey("client.id_client"))
    debit_internet = Column(String(20))
    etat = Column(String(10))
    
    client = relationship("Client", back_populates="lignes")
    factures = relationship("Facture", back_populates="ligne")
    reclamations = relationship("Reclamation", back_populates="ligne")

class Facture(Base):
    __tablename__ = "facture"
    
    id_facture = Column(String(15), primary_key=True)
    num_ligne = Column(String(10), ForeignKey("lignetelephonique.num_ligne"))
    date_emission = Column(Date, nullable=False)
    montant = Column(Numeric(10, 2))
    statut_paiement = Column(String(10))
    
    ligne = relationship("LigneTelephonique", back_populates="factures")

class Reclamation(Base):
    __tablename__ = "reclamation"
    
    id_reclamation = Column(String(15), primary_key=True)
    num_ligne = Column(String(10), ForeignKey("lignetelephonique.num_ligne"))
    date_reclamation = Column(TIMESTAMP)
    type_probleme = Column(String(100))
    etat = Column(String(20))
    
    ligne = relationship("LigneTelephonique", back_populates="reclamations")
    dialogues = relationship("HistoriqueDialogue", back_populates="reclamation")

class HistoriqueDialogue(Base):
    __tablename__ = "historiquedialogue"
    
    id_dialogue = Column(String(15), primary_key=True)
    id_reclamation = Column(String(15), ForeignKey("reclamation.id_reclamation"))
    message_utilisateur = Column(Text)
    reponse_chatbot = Column(Text)
    timestamp = Column(TIMESTAMP)
    
    reclamation = relationship("Reclamation", back_populates="dialogues")