import logging
import math

class NamoNexusEngine:
    """
    NamoNexus Fusion Engine v4.0.0 (Bayesian Multimodal Fusion)
    ใช้ Golden Ratio (phi) เป็นค่าคงที่ในการถ่วงน้ำหนักสัญญาณประสาท
    """
    def __init__(self):
        self.phi = 1.618034
        self.fused_score = 0.5
        self.confidence = 0.0
        self.has_drift_alarm = False
        self.drift_threshold = 0.4
        self.logger = logging.getLogger(__name__)

    def update(self, score: float, confidence: float, modality: str):
        """รับค่าจาก Text/Voice/Face และคำนวณการหลอมรวม"""
        # น้ำหนักตาม modality (Face > Voice > Text)
        weight = {"face": self.phi**2, "voice": self.phi, "text": 1.0}.get(modality, 1.0)
        
        # Bayesian fusion approximation
        new_fused = (self.fused_score + (score * confidence * weight)) / (1 + weight)
        
        # Drift Detection
        if abs(new_fused - self.fused_score) > self.drift_threshold:
            self.has_drift_alarm = True
            self.logger.warning(f"[DRIFT ALARM]: Detected emotional deviation! Fused: {new_fused:.2f}")
        else:
            self.has_drift_alarm = False
            
        self.fused_score = new_fused
        self.confidence = confidence

    def explain(self) -> str:
        return f"Fusion Score: {self.fused_score:.2f} (Confidence: {self.confidence:.2f})"
