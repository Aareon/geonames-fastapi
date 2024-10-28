from typing import Optional
from pydantic import BaseModel, Field

class LocationResponse(BaseModel):
    name: str = Field(..., description="Name of the location")
    postal_code: Optional[str] = Field(None, description="Postal code")
    country: str = Field(..., description="Country code")
    state: Optional[str] = Field(None, description="State or primary administrative division")
    state_code: Optional[str] = Field(None, description="State code")
    province: Optional[str] = Field(None, description="Secondary administrative division")
    province_code: Optional[str] = Field(None, description="Province code")
    community: Optional[str] = Field(None, description="Tertiary administrative division")
    community_code: Optional[str] = Field(None, description="Community code")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    accuracy: Optional[int] = Field(None, description="Geographical accuracy level, if available")
    
class GeoLocationResponse(BaseModel):
    """Response model for detailed geolocation information."""
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State name")
    country_code: str = Field(..., description="Country code")
    state_code: str = Field(..., description="State code")
    province: Optional[str] = Field(None, description="Province name")
    province_code: Optional[str] = Field(None, description="Province code")

class DatabaseStats(BaseModel):
    """Response model for database statistics."""
    total_entries: int = Field(..., description="Total number of entries in the database")
    country_count: int = Field(..., description="Total number of countries in the database")

class ErrorResponse(BaseModel):
    """Response model for error messages."""
    detail: str = Field(..., description="Error message detail")