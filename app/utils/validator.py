from pydantic import BaseModel, Field, field_validator

class CropPredictionInput(BaseModel):
    nitrogen: float = Field(..., ge=0, le=200, description="Nitrogen content (0-200)")
    phosphorus: float = Field(..., ge=0, le=200, description="Phosphorus content (0-200)")
    potassium: float = Field(..., ge=0, le=200, description="Potassium content (0-200)")
    temperature: float = Field(..., ge=-10, le=60, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, description="Humidity percentage")
    ph: float = Field(..., ge=0, le=14, description="pH value (0-14)")
    rainfall: float = Field(..., ge=0, le=500, description="Rainfall in mm")
    
    @field_validator('humidity')
    @classmethod
    def validate_humidity(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Humidity must be between 0 and 100')
        return v