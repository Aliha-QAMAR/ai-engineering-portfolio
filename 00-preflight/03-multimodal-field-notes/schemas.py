from typing import List, Optional
from pydantic import BaseModel, Field

class FitCheckItem(BaseModel):
    category: str = Field(description="Clothing item category e.g., Top, Bottom, Footwear, Accessory")
    description: str = Field(description="Visual description of the item")
    color: str = Field(description="Dominant color")
    brand: Optional[str] = Field(default=None, description="Brand name if visible")

class FitCheckAnalysis(BaseModel):
    aesthetic_vibe: str = Field(description="Overall style aesthetic e.g., Y2K, Streetwear, Minimalist")
    color_palette: List[str] = Field(description="Main color scheme of the outfit")
    items: List[FitCheckItem] = Field(description="List of detected clothing items")
    styling_tips: List[str] = Field(description="Suggestions to elevate the fit")

class ActionItem(BaseModel):
    task: str = Field(description="Specific action required")
    owner: str = Field(description="Person assigned to the task or Unassigned")
    due_date: str = Field(description="Target completion date or TBD")

class VoiceNotesSummary(BaseModel):
    summary: str = Field(description="High level summary of the audio recording")
    decisions: List[str] = Field(description="Key decisions made")
    action_items: List[ActionItem] = Field(description="List of action items with owners and dates")
    open_questions: List[str] = Field(description="Unresolved questions or follow ups")