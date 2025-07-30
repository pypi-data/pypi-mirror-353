from typing import Any, Optional, ClassVar
from pydantic import Field
from .baseObj import BaseObj

class TranslationEntry(BaseObj):
    dbCollectionName: ClassVar[str] = "translations"

    id:             str               = Field(..., description="Stable and unique ID for the field in the object")
    object_id:      str               = Field(..., description="ID of the object being translated")
    locale:         str               = Field(..., description="Locale code, e.g. 'en-US', 'he-IL'")
    text:           str               = Field(..., description="Translated text")
    gender_variant: Optional[int]     = Field(None, description="1 (male), 2 (female), or None for neutral")

    def createFilter(self) -> dict[str, Any]:
        filter = {
            "object_id":      self.object_id,
            "locale":         self.locale,
            "id":             self.id,
            # For neutral translations, gender_variant is None
            "gender_variant": self.gender_variant
        }

        return filter
