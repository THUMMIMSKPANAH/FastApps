from fastapps import BaseWidget, ConfigDict
# from fastapps import auth_required, no_auth, optional_auth, UserContext
from pydantic import BaseModel
from typing import Dict, Any


class MyWidgetInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


# Optional: Add authentication
# @auth_required(scopes=["user"])
# @no_auth
# @optional_auth(scopes=["user"])
class MyWidgetTool(BaseWidget):
    identifier = "my_widget"
    title = "My Widget"
    input_schema = MyWidgetInput
    invoking = "Loading widget..."
    invoked = "Widget ready!"

    widget_csp = {
        "connect_domains": [],
        "resource_domains": []
    }

    async def execute(self, input_data: MyWidgetInput, context=None, user=None) -> Dict[str, Any]:
        return {
            "message": "Welcome to FastApps"
        }
