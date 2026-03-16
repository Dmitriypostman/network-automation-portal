from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.vlan_service import (
    load_inventory,
    get_device_by_name,
    add_vlan_to_device_trunk,
)

app = FastAPI(title="VLAN Trunk Automation Portal")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    inventory = load_inventory()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": inventory["devices"],
            "result": None,
        },
    )


@app.post("/add-vlan", response_class=HTMLResponse)
def add_vlan(
    request: Request,
    device_name: str = Form(...),
    interface_name: str = Form(...),
    vlan_id: int = Form(...),
):
    inventory = load_inventory()
    device = get_device_by_name(device_name)

    if not device:
        raise HTTPException(status_code=404, detail=f"Device '{device_name}' not found")

    if interface_name not in device.get("trunk_interfaces", []):
        raise HTTPException(
            status_code=400,
            detail=f"Interface '{interface_name}' is not listed as a trunk interface for device '{device_name}'"
        )

    ok, message = add_vlan_to_device_trunk(device, interface_name, vlan_id)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "devices": inventory["devices"],
            "result": {
                "success": ok,
                "message": message,
            },
        },
    )

#test