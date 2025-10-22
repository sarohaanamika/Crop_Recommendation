# API Documentation

## Endpoints

### POST /predict
Request body:
{
  "nitrogen": 90,
  "phosphorus": 42,
  ...
}

Response:
{
  "predicted_crop": "Rice",
  "confidence": 0.95,
  ...
}