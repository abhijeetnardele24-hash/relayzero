"""
RelayZero Synthetic Demonstration Scenarios.
Covers multilingual (DE, FR, IT, EN) and multi-source (Text, Document Transcript, Voice Transcript)
reports with calibrated factual conflicts and missing data.
"""

from typing import List
from datetime import datetime, timezone
from .schemas import (
    Incident,
    SourceReport,
    ModalityEnum,
    LanguageEnum,
    AppModeEnum,
)


def get_synthetic_presets(app_mode: AppModeEnum = AppModeEnum.FIXTURE) -> List[Incident]:
    now = datetime.now(timezone.utc).isoformat()

    # Preset 1: Alpine Tunnel Smoke Incident (Gotthard Corridor)
    tunnel_incident = Incident(
        incident_id="INC-2026-CH-01",
        title="Alpine Tunnel Smoke Incident — Gotthard Corridor",
        preset_id="alpine_tunnel_smoke",
        status="active",
        deployment_mode="air_gapped",
        app_mode=app_mode,
        created_at=now,
        updated_at=now,
        sources=[
            SourceReport(
                report_id="SRC-DE-01",
                incident_id="INC-2026-CH-01",
                modality=ModalityEnum.TEXT,
                language=LanguageEnum.DE,
                author_role="Polizei Uri / Einsatzleitzentrale",
                received_at="2026-10-12T14:08:00Z",
                source_channel="TETRA Radio / SMS Dispatch",
                reliability_tier="Verified Emergency Services",
                raw_content="EILMELDUNG: Starke Rauchentwicklung im Gotthard-Strassentunnel ca. 500m nach dem Nordportal Göschenen. Ereignis um 14:05 Uhr bemerkt. Dichter schwarzer Rauch behindert Sicht komplett. Tunnel in beiden Richtungen blockiert. Keine bestätigten Verletzten bis jetzt. Lüftung Nord aktiv.",
                metadata={"location_tag": "Nordportal Göschenen", "priority": "CRITICAL"},
            ),
            SourceReport(
                report_id="SRC-FR-02",
                incident_id="INC-2026-CH-01",
                modality=ModalityEnum.DOCUMENT_TRANSCRIPT,
                language=LanguageEnum.FR,
                author_role="Centre d'intervention Sud / Airolo (Scanned Form OCR Transcript)",
                received_at="2026-10-12T14:14:00Z",
                source_channel="Fax / Scanned Protocol Form OCR",
                reliability_tier="Field Inspection Unit",
                raw_content="FICHE D'INTERVENTION #442: Important dégagement de fumée signalé dans le secteur sud vers le portail d'Airolo. Environ 20 personnes réfugiées dans les niches de sécurité. Visibilité réduite à moins de 5 mètres. Nécessite activation immédiate de la ventilation de secours côté Tessin. Véhicule en cause non localisé.",
                metadata={"ocr_confidence": 0.94, "document_type": "Intervention Sheet"},
            ),
            SourceReport(
                report_id="SRC-IT-03",
                incident_id="INC-2026-CH-01",
                modality=ModalityEnum.VOICE_TRANSCRIPT,
                language=LanguageEnum.IT,
                author_role="Citizen / Trapped Driver (Audio Transcript)",
                received_at="2026-10-12T14:19:00Z",
                source_channel="Centrale 118 / Voice Emergency Call",
                reliability_tier="Direct Witness",
                raw_content="[TRASCRIZIONE VOCALE 118]: Pronto? C'è fumo denso ovunque, non si respira! Siamo chiusi nella nicchia di sicurezza 4. Con me ci sono altre persone, siamo in 12 persone nella nicchia 4, compreso un bambino. Abbiamo sentito un boato verso le 14:15, mandate soccorsi presto!",
                metadata={"audio_duration_sec": 34, "transcription_source": "Speech-to-text transcript"},
            ),
        ],
    )

    # Preset 2: Flood Shelter Capacity Incident (Rhône Valley)
    flood_incident = Incident(
        incident_id="INC-2026-CH-02",
        title="Rhône Flash Flood & Emergency Shelter Overflow — Sion",
        preset_id="flood_shelter_capacity",
        status="active",
        deployment_mode="air_gapped",
        app_mode=app_mode,
        created_at=now,
        updated_at=now,
        sources=[
            SourceReport(
                report_id="SRC-FR-01",
                incident_id="INC-2026-CH-02",
                modality=ModalityEnum.TEXT,
                language=LanguageEnum.FR,
                author_role="Sécurité Civile Valais",
                received_at="2026-10-12T09:30:00Z",
                source_channel="Cell Broadcast / Alert Message",
                reliability_tier="Cantonal Command",
                raw_content="ALERTE CRUE: Débordement soudain du Rhône suite aux précipitations torrentielles. Évacuation préventive ordonnée pour le secteur sous-gare de Sion. Ouverture immédiate du centre d'accueil d'urgence du Gymnase des Collines à Sion. Capacité théorique 150 lits.",
                metadata={"sector": "Sion Bas", "warning_level": "Level 4 Red"},
            ),
            SourceReport(
                report_id="SRC-DE-02",
                incident_id="INC-2026-CH-02",
                modality=ModalityEnum.DOCUMENT_TRANSCRIPT,
                language=LanguageEnum.DE,
                author_role="Zivilschutz Einsatzleiter (Scanned Status Transcript)",
                received_at="2026-10-12T10:15:00Z",
                source_channel="Field Dispatch Sheet Transcript",
                reliability_tier="Civil Protection Lead",
                raw_content="LAGEBERICHT NOTUNTERKUNFT: Gymnase des Collines komplett ausgelastet. Bereits 180 Personen eingetroffen (Kapazität 150 überschritten). Dringender Bedarf an 50 zusätzlichen Feldbetten und Eröffnung der Sekundärunterkunft Turnhalle Bramois. Trinkwasserversorgung stabil.",
                metadata={"capacity_status": "EXCEEDED"},
            ),
        ],
    )

    # Preset 3: Rail Power Failure Incident (Olten-Bern Mainline)
    rail_incident = Incident(
        incident_id="INC-2026-CH-03",
        title="Rail Traction Power Outage & Stranded InterCity — Olten-Bern",
        preset_id="rail_power_failure",
        status="active",
        deployment_mode="air_gapped",
        app_mode=app_mode,
        created_at=now,
        updated_at=now,
        sources=[
            SourceReport(
                report_id="SRC-DE-01",
                incident_id="INC-2026-CH-03",
                modality=ModalityEnum.TEXT,
                language=LanguageEnum.DE,
                author_role="SBB Betriebszentrale Mitte",
                received_at="2026-10-12T16:20:00Z",
                source_channel="Railway Operational Telegram",
                reliability_tier="Infrastructure Manager",
                raw_content="DRINGEND: Kompletter Fahrleitungs-Stromausfall auf der Neubaustrecke Mattstetten-Rothrist bei km 28. IC 817 mit Lokomotive Re 460 stromlos zum Stillstand gekommen. Klimaanlage ausgefallen. Ca. 450 Passagiere an Bord. Keine Entgleisung. Diesel-Hilfslok angefordert.",
                metadata={"train_number": "IC 817", "line": "NBS Olten-Bern"},
            ),
            SourceReport(
                report_id="SRC-FR-02",
                incident_id="INC-2026-CH-03",
                modality=ModalityEnum.VOICE_TRANSCRIPT,
                language=LanguageEnum.FR,
                author_role="Chef de Train / Conductor (Radio Transcript)",
                received_at="2026-10-12T16:32:00Z",
                source_channel="CFF Internal Radio",
                reliability_tier="On-board Crew",
                raw_content="[RADIO CONVOI]: Ici chef de train IC 817. Température qui monte rapidement dans les voitures. 450 voyageurs calmes mais inquiets. Besoin urgent de ravitaillement en eau et d'évacuation par rame de secours. Aucune blessure signalée.",
                metadata={"train_temperature": "Rising", "passengers_condition": "Calm"},
            ),
        ],
    )

    return [tunnel_incident, flood_incident, rail_incident]
