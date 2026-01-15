
import pytest
from uuid import uuid4, UUID
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.user import User
from app.models.organization import Organization
from app.models.farm import Farm
from app.models.work_order import WorkOrder, WorkOrderScope
from app.models.enums import WorkOrderStatus, WorkOrderScopeType
from app.services.farm_service import FarmService
from app.core.exceptions import NotFoundError

class TestFSPAccess:
    """
    Verify FSP Access Logic in FarmService.
    """

    def test_fsp_access_granted_via_work_order(self):
        """
        Scenario: User is FSP. Farm is Client. Active Work Order Exists.
        Expected: Success.
        """
        mock_db = MagicMock(spec=Session)
        service = FarmService(mock_db)

        # IDs
        fsp_org_id = uuid4()
        client_org_id = uuid4()
        farm_id = uuid4()
        work_order_id = uuid4()

        # 1. Mock Farm (owned by Client)
        farm = Mock(spec=Farm)
        farm.id = farm_id
        farm.organization_id = client_org_id
        farm.is_active = True
        
        # 2. Mock Work Order (Active)
        work_order = Mock(spec=WorkOrder)
        work_order.id = work_order_id
        work_order.fsp_organization_id = fsp_org_id
        work_order.farming_organization_id = client_org_id
        work_order.status = WorkOrderStatus.ACCEPTED

        # 3. Mock Scope (Farm Scope)
        scope = Mock(spec=WorkOrderScope)
        scope.scope = WorkOrderScopeType.FARM
        scope.scope_id = farm_id

        # Setup Query Chains
        # We have multiple queries in get_farm_by_id:
        # A. Query Farm by ID
        # B. Query WorkOrder (if org mismatch)
        # C. Query Scope
        
        # We need careful side_effect setup or using filter logic mocking.
        # Since implementation uses chained .filter(), we mock the result of the chain.
        
        # Query A: Farm
        # service.db.query(Farm).options().filter().first() -> returns farm
        q_farm = mock_db.query.return_value
        q_options = q_farm.options.return_value
        q_filter_farm = q_options.filter.return_value
        q_filter_farm.first.return_value = farm

        # Query B: WorkOrder
        # This is where it gets tricky because Python mocks of clustered queries are hard.
        # The code calls: db.query(WorkOrder).filter(...).first()
        # We can distinguish by the Model passed to query() if we mock query() specifically.
        
        def query_side_effect(model_cls):
            if model_cls == Farm:
                # Return chain that yields 'farm'
                m = MagicMock()
                m.options.return_value.filter.return_value.first.return_value = farm
                return m
            elif model_cls == WorkOrder:
                # Return chain that yields 'work_order'
                m = MagicMock()
                m.filter.return_value.first.return_value = work_order
                return m
            elif model_cls == WorkOrderScope:
                # Return chain that yields 'scope'
                m = MagicMock()
                m.filter.return_value.filter.return_value.first.return_value = scope
                return m
            return MagicMock()

        mock_db.query.side_effect = query_side_effect
        
        # Call Service
        # We mock _to_response to avoid Pydantic validation issues on Mocks
        service._to_response = Mock(return_value={"id": farm_id, "name": "Success"})

        result = service.get_farm_by_id(farm_id, fsp_org_id)
        
        assert result["id"] == farm_id
        assert result["name"] == "Success"

    def test_fsp_access_denied_no_work_order(self):
        """
        Scenario: User is FSP. Farm is Client. NO Work Order.
        Expected: NotFoundError.
        """
        mock_db = MagicMock(spec=Session)
        service = FarmService(mock_db)

        fsp_org_id = uuid4()
        client_org_id = uuid4()
        farm_id = uuid4()

        farm = Mock(spec=Farm)
        farm.id = farm_id
        farm.organization_id = client_org_id
        farm.is_active = True

        def query_side_effect(model_cls):
            if model_cls == Farm:
                m = MagicMock()
                m.options.return_value.filter.return_value.first.return_value = farm
                return m
            elif model_cls == WorkOrder:
                m = MagicMock()
                m.filter.return_value.first.return_value = None # No Work Order
                return m
            return MagicMock()
        
        mock_db.query.side_effect = query_side_effect

        with pytest.raises(NotFoundError):
            service.get_farm_by_id(farm_id, fsp_org_id)

