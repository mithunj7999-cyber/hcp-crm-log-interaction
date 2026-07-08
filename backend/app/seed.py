"""
Seed Script — Populates the database with sample HCPs, Materials, and Interactions.

Run:  python -m app.seed
"""

from datetime import date, time

from app.core.database import SessionLocal, engine, Base
from app.models.models import HCP, Material, Interaction, InteractionType, Sentiment, MaterialType


def seed():
    """Drop + recreate all tables, then insert sample data."""
    # Recreate tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # ── HCPs ────────────────────────────────────────────────────────
        hcps = [
            HCP(name="Dr. Sarah Chen",     specialty="Oncology",      institution="Metro Cancer Center",       email="s.chen@metrocc.com",       city="New York",      state="NY"),
            HCP(name="Dr. James Wilson",    specialty="Cardiology",    institution="HeartCare Clinic",          email="j.wilson@heartcare.com",   city="Chicago",       state="IL"),
            HCP(name="Dr. Priya Patel",     specialty="Endocrinology", institution="Diabetes & Endo Associates",email="p.patel@deassoc.com",      city="Houston",       state="TX"),
            HCP(name="Dr. Michael Torres",  specialty="Neurology",     institution="BrainHealth Institute",     email="m.torres@brainhealth.org", city="San Francisco", state="CA"),
            HCP(name="Dr. Emily Nakamura",  specialty="Pulmonology",   institution="Lung & Respiratory Center", email="e.nakamura@lungcenter.com",city="Seattle",       state="WA"),
            HCP(name="Dr. Robert Kim",      specialty="Rheumatology",  institution="Joint & Bone Specialists",  email="r.kim@jointnbone.com",     city="Boston",        state="MA"),
            HCP(name="Dr. Aisha Rahman",    specialty="Dermatology",   institution="SkinFirst Dermatology",     email="a.rahman@skinfirst.com",   city="Miami",         state="FL"),
            HCP(name="Dr. David Martinez",  specialty="Gastroenterology",institution="GI Health Partners",      email="d.martinez@gihealth.com",  city="Dallas",        state="TX"),
        ]
        db.add_all(hcps)
        db.flush()  # get IDs

        # ── Materials ───────────────────────────────────────────────────
        materials = [
            Material(name="OncoBoost Efficacy Brochure",   type=MaterialType.BROCHURE,      description="Phase III trial results for OncoBoost in NSCLC patients"),
            Material(name="CardioShield Clinical Data",    type=MaterialType.CLINICAL_DATA,  description="Long-term outcomes data for CardioShield in heart failure"),
            Material(name="GlucoBalance Patient Guide",    type=MaterialType.BROCHURE,      description="Patient-facing guide for GlucoBalance insulin therapy"),
            Material(name="NeuroCalm MOA Presentation",    type=MaterialType.PRESENTATION,   description="Mechanism of action slides for NeuroCalm migraine treatment"),
            Material(name="OncoBoost 50mg Sample",         type=MaterialType.SAMPLE,         description="14-day starter pack of OncoBoost 50mg"),
            Material(name="CardioShield 25mg Sample",      type=MaterialType.SAMPLE,         description="7-day trial supply of CardioShield 25mg"),
            Material(name="GlucoBalance Pen Demo Kit",     type=MaterialType.SAMPLE,         description="Demo insulin pen kit for patient training"),
            Material(name="ImmunoFlex Safety Profile",     type=MaterialType.CLINICAL_DATA,  description="Post-market surveillance data for ImmunoFlex"),
            Material(name="DermaClear Before/After Video", type=MaterialType.VIDEO,          description="Patient outcomes video for DermaClear psoriasis treatment"),
            Material(name="GastroEase Product Monograph",  type=MaterialType.BROCHURE,       description="Complete prescribing information for GastroEase"),
        ]
        db.add_all(materials)
        db.flush()

        # ── Sample Interactions ────────────────────────────────────────
        interactions = [
            Interaction(
                hcp_id=hcps[0].id,
                interaction_type=InteractionType.MEETING,
                date=date(2026, 7, 1),
                time=time(10, 30),
                attendees="Dr. Sarah Chen, John (Rep)",
                topics_discussed="OncoBoost Phase III results, patient selection criteria, dosing protocols",
                materials_shared="OncoBoost Efficacy Brochure",
                samples_distributed="OncoBoost 50mg Sample",
                sentiment=Sentiment.POSITIVE,
                outcomes="Dr. Chen expressed strong interest in prescribing OncoBoost for eligible NSCLC patients",
                follow_up_actions="Send full Phase III dataset, Schedule follow-up in 2 weeks",
            ),
            Interaction(
                hcp_id=hcps[1].id,
                interaction_type=InteractionType.CALL,
                date=date(2026, 7, 3),
                time=time(14, 0),
                attendees="Dr. James Wilson",
                topics_discussed="CardioShield long-term outcomes, comparison with existing treatments",
                materials_shared="CardioShield Clinical Data",
                sentiment=Sentiment.NEUTRAL,
                outcomes="Dr. Wilson wants to review the data before committing. Requested head-to-head comparison studies",
                follow_up_actions="Email comparison study summary, Follow up next week",
            ),
            Interaction(
                hcp_id=hcps[2].id,
                interaction_type=InteractionType.EMAIL,
                date=date(2026, 7, 5),
                attendees="Dr. Priya Patel",
                topics_discussed="GlucoBalance insulin pen ease of use, patient compliance data",
                materials_shared="GlucoBalance Patient Guide",
                samples_distributed="GlucoBalance Pen Demo Kit",
                sentiment=Sentiment.POSITIVE,
                outcomes="Dr. Patel agreed to trial GlucoBalance with 5 patients and provide feedback",
                follow_up_actions="Check in after 30 days on patient feedback",
            ),
        ]
        db.add_all(interactions)

        db.commit()
        print("✅  Database seeded successfully!")
        print(f"   • {len(hcps)} HCPs")
        print(f"   • {len(materials)} Materials")
        print(f"   • {len(interactions)} Interactions")

    except Exception as e:
        db.rollback()
        print(f"❌  Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
