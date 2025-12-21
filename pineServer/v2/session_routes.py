"""
Session Routes - Clean implementation using V2 architecture

These routes use the SessionService for clean, testable endpoint logic.
Import and include this router in main.py to use the refactored flow.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional

from models import (
    StartSessionRequest, StartSessionResponse,
    CompleteSessionRequest, CompleteSessionResponse,
    Exercise, ExerciseType, Operator
)
from v2.session_service import get_session_service
from v2.models import (
    ExerciseResult, Exercise as V2Exercise, TipoRespuesta
)
from roble_client import roble_client

router = APIRouter(prefix="/api", tags=["sessions"])


@router.post("/sessions/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """
    Start a new exercise session.
    
    Uses the V2 SessionService for clean orchestration of:
    1. User operation state lookup
    2. Batch type determination
    3. Exercise generation
    4. Session creation
    """
    try:
        print(f"[SessionRouter] Starting session for user: {request.user_ref}")
        
        service = get_session_service()
        
        # Use the service to start the session
        result = service.start_session(
            user_ref=request.user_ref,
            num_exercises=request.num_exercises,
            batch_type_override=request.batch_type
        )
        
        # Convert V2 exercises to legacy format for response
        legacy_exercises = _convert_to_legacy_exercises(result["exercises"])
        
        # Build user profile for response
        user_profile = {op.value: 1.0 for op in Operator}
        if result.get("is_miniboss"):
            user_profile['is_miniboss'] = 1.0
        
        return StartSessionResponse(
            session_id=result["session_id"],
            exercises=legacy_exercises,
            user_profile=user_profile
        )
        
    except Exception as e:
        print(f"[SessionRouter] Error in start_session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/complete", response_model=CompleteSessionResponse)
async def complete_session(session_id: str, request: CompleteSessionRequest):
    """
    Complete a session and save results.
    
    Uses the V2 SessionService for clean orchestration of:
    1. Result conversion and validation
    2. Performance evaluation
    3. Score calculation
    4. State persistence
    5. Gamification updates
    """
    try:
        print(f"[SessionRouter] Completing session: {session_id}")
        
        service = get_session_service()
        
        # Convert legacy exercise results to V2 format
        v2_results = _convert_to_v2_results(request.exercises)
        
        # Use the service to complete the session
        result = service.complete_session(
            session_id=session_id,
            exercise_results=v2_results
        )
        
        return CompleteSessionResponse(
            session_id=result["session_id"],
            total_exercises=result["total_exercises"],
            correct_answers=result["correct_answers"],
            score_earned=result["score_earned"],
            difficulty_adjustments=result["difficulty_adjustments"],
            gamification=result["gamification"],
            endless_info=result.get("endless_info")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"[SessionRouter] Error in complete_session: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def _convert_to_legacy_exercises(v2_exercises: List[V2Exercise]) -> List[Exercise]:
    """Convert V2 Exercise objects to legacy Exercise model format."""
    op_map = {
        "suma": Operator.ADD,
        "resta": Operator.SUBTRACT,
        "mult": Operator.MULTIPLY,
        "div": Operator.DIVIDE
    }
    
    legacy_exercises = []
    for ex in v2_exercises:
        ex_type = (
            ExerciseType.MULTIPLE_CHOICE 
            if ex.tipo_respuesta == TipoRespuesta.MULTIPLE_CHOICE 
            else ExerciseType.TEXT_INPUT
        )
        legacy_exercises.append(Exercise(
            exercise_type=ex_type,
            operator=op_map.get(ex.operacion, Operator.ADD),
            operand_1=ex.operand_1,
            operand_2=ex.operand_2,
            correct_answer=ex.respuesta_correcta,
            options=ex.opciones,
            difficulty_level=ex.dificultad
        ))
    return legacy_exercises


def _convert_to_v2_results(legacy_exercises) -> List[ExerciseResult]:
    """Convert legacy exercise results to V2 ExerciseResult format."""
    op_map_rev = {'+': 'suma', '-': 'resta', '*': 'mult', '/': 'div'}
    
    v2_results = []
    for ex in legacy_exercises:
        op_v2 = op_map_rev.get(ex.operator.value, 'suma')
        
        exercise_obj = V2Exercise(
            operand_1=ex.operand_1,
            operand_2=ex.operand_2,
            operacion=op_v2,
            respuesta_correcta=ex.correct_answer,
            dificultad=ex.difficulty_level,
            tipo_respuesta=(
                TipoRespuesta.MULTIPLE_CHOICE 
                if ex.exercise_type.value == "multiple_choice" 
                else TipoRespuesta.ABIERTA
            ),
            opciones=ex.options
        )
        
        v2_res = ExerciseResult(
            exercise=exercise_obj,
            respuesta_usuario=ex.user_answer if ex.user_answer is not None else 0,
            es_correcto=ex.is_correct,
            tiempo_segundos=ex.time_taken_ms / 1000.0
        )
        v2_results.append(v2_res)
    
    return v2_results
