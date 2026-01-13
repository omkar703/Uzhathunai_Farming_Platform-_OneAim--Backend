"""API v1 routes"""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    organizations,
    roles,
    members,
    invitations,
    fsp_services,
    work_orders,
    schedule_templates,
    schedules,
    task_actuals,
    queries,
    measurement_units,
    crop_data,
    input_items,
    finance_categories,
    tasks,
    reference_data,
    farms,
    plots,
    crops,
    crop_yields,
    crop_photos,
    notifications,
    video_zoom
)
from app.api.v1.farm_audit import option_sets, parameters, sections, templates, audits, reports
from app.api.v1.bff import farming_dashboard, fsp_dashboard
from app.api.v1 import admin

api_router = APIRouter()

# Include admin routes
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Include auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include organization routes
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])

# Include role routes
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])

# Include member routes
api_router.include_router(members.router, tags=["Members"])

# Include invitation routes
api_router.include_router(invitations.router, prefix="/invitations", tags=["Invitations"])

# Include FSP service routes
api_router.include_router(fsp_services.router, prefix="/fsp-services", tags=["FSP Services"])

# Include work order routes
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["Work Orders"])

# Include schedule template routes
api_router.include_router(schedule_templates.router, tags=["Schedule Templates"])

# Include schedule routes
api_router.include_router(schedules.router, tags=["Schedules"])

# Include task actual routes
api_router.include_router(task_actuals.router, tags=["Task Actuals"])
api_router.include_router(task_actuals.change_log_router, tags=["Schedule Change Log"])

# Include query routes
api_router.include_router(queries.router, tags=["Queries"])

# Include notification routes
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Include reference data routes
api_router.include_router(measurement_units.router, prefix="/measurement-units", tags=["Measurement Units"])
api_router.include_router(crop_data.router, prefix="/crop-data", tags=["Crop Data"])
api_router.include_router(input_items.router, prefix="/input-items", tags=["Input Items"])
api_router.include_router(finance_categories.router, prefix="/finance-categories", tags=["Finance Categories"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(reference_data.router, prefix="/reference-data", tags=["Reference Data"])

# Include farm management routes
api_router.include_router(farms.router, prefix="/farms", tags=["Farms"])
api_router.include_router(plots.router, prefix="/plots", tags=["Plots"])

# Include crop management routes
api_router.include_router(crops.router, prefix="/crops", tags=["Crops"])
api_router.include_router(crop_yields.router, prefix="/crop-yields", tags=["Crop Yields"])
api_router.include_router(crop_photos.router, prefix="/crop-photos", tags=["Crop Photos"])

# Include farm audit management routes
api_router.include_router(option_sets.router, prefix="/farm-audit/option-sets", tags=["Farm Audit - Option Sets"])
api_router.include_router(parameters.router, prefix="/farm-audit/parameters", tags=["Farm Audit - Parameters"])
api_router.include_router(sections.router, prefix="/farm-audit/sections", tags=["Farm Audit - Sections"])
api_router.include_router(templates.router, prefix="/farm-audit/templates", tags=["Farm Audit - Templates"])
api_router.include_router(audits.router, prefix="/farm-audit", tags=["Farm Audit - Audits"])
api_router.include_router(reports.router, prefix="/farm-audit", tags=["Farm Audit - Reports"])

# Include BFF (Backend For Frontend) routes
api_router.include_router(farming_dashboard.router, prefix="/bff", tags=["BFF - Dashboard"])
api_router.include_router(fsp_dashboard.router, prefix="/bff", tags=["BFF - Dashboard"])

# Include video session routes
api_router.include_router(video_zoom.router, prefix="/video", tags=["Video Consultations"])
