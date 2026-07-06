from fastapi import APIRouter

from app.brain.engineering_brain import EngineeringBrain
from app.brain.engineering_session import EngineeringSession

router = APIRouter()


@router.get("/")
async def root():
    return {
        "project": "GridMind AI",
        "status": "running",
        "identity": "Autonomous Electrical Power Systems Engineer",
    }


@router.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@router.post("/brain/test")
async def test_engineering_brain():
    session = EngineeringSession(
        title="Transformer differential relay trip investigation"
    )

    session.add_observation(
        {
            "asset": "Transformer T1",
            "voltage": "230/13.8 kV",
            "event": "Differential relay trip",
            "available_data": ["basic event description"],
            "missing_data": ["COMTRADE", "relay event report", "DGA", "inspection record"],
        }
    )

    brain = EngineeringBrain()
    completed_session = brain.run(session)

    return completed_session.to_dict()
