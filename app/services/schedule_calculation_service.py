"""
Schedule Calculation Service for Uzhathunai v2.0.

Handles quantity calculations for schedule templates based on calculation_basis.
Supports per_acre, per_plant, and fixed calculations.
"""
from typing import Dict, Any, Optional
from decimal import Decimal
from app.core.logging import get_logger
from app.core.exceptions import ValidationError

logger = get_logger(__name__)


class ScheduleCalculationService:
    """Service for calculating task quantities from schedule templates."""
    
    def calculate_task_quantities(
        self,
        task_details_template: Dict[str, Any],
        template_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate actual quantities from template formulas.
        
        Args:
            task_details_template: Template with calculation formulas
            template_parameters: Parameters (area, plant_count, start_date)
        
        Returns:
            dict: Calculated task_details for schedule_task
        
        Validates: Requirements 6.8, 6.9, 6.10, 6.11
        """
        task_details = {}
        
        # Calculate input items
        if 'input_items' in task_details_template:
            task_details['input_items'] = self._calculate_input_items(
                task_details_template['input_items'],
                template_parameters
            )
        
        # Calculate labor
        if 'labor' in task_details_template:
            task_details['labor'] = self._calculate_labor(
                task_details_template['labor'],
                template_parameters
            )
        
        # Calculate machinery
        if 'machinery' in task_details_template:
            task_details['machinery'] = self._calculate_machinery(
                task_details_template['machinery'],
                template_parameters
            )
        
        # Calculate concentration
        if 'concentration' in task_details_template:
            task_details['concentration'] = self._calculate_concentration(
                task_details_template['concentration'],
                template_parameters
            )
            
        # Handle Flat Structure (Dosage + Input Item at root)
        if 'dosage_amount' in task_details_template and 'input_item_id' in task_details_template:
            amount = task_details_template.get('dosage_amount', 0)
            per = task_details_template.get('dosage_per', 'ACRE')
            calculated_qty = self._calculate_dosage_quantity(
                amount,
                per,
                template_parameters
            )
            
            result_item = {
                'input_item_id': task_details_template['input_item_id'],
                'quantity': calculated_qty,
                'quantity_unit_id': task_details_template.get('dosage_unit'),
                'dosage': {
                    'amount': amount,
                    'per': per,
                    'unit': task_details_template.get('dosage_unit')
                }
            }
            
            if 'application_method_id' in task_details_template:
                result_item['application_method_id'] = task_details_template['application_method_id']
                
            if 'input_items' not in task_details:
                task_details['input_items'] = [result_item]
            else:
                task_details['input_items'].append(result_item)
                
        logger.info(
            "Task quantities calculated",
            extra={
                "has_input_items": 'input_items' in task_details,
                "has_labor": 'labor' in task_details,
                "has_machinery": 'machinery' in task_details,
                "has_concentration": 'concentration' in task_details
            }
        )
        
        return task_details
    
    def _calculate_input_items(
        self,
        input_items_template: list,
        template_parameters: Dict[str, Any]
    ) -> list:
        """Calculate input item quantities."""
        calculated_items = []
        
        for item in input_items_template:
            # Handle new dosage structure
            if 'dosage' in item:
                dosage = item['dosage']
                calculated_qty = self._calculate_dosage_quantity(
                    dosage['amount'],
                    dosage.get('per'),
                    template_parameters
                )
                
                result_item = {
                    'input_item_id': item['input_item_id'],
                    'quantity': calculated_qty,
                    'quantity_unit_id': dosage.get('unit_id') or dosage.get('unit'), # Assuming unit field handles ID or Code. Schema probably expects ID.
                    'dosage': dosage # Persist dosage info for reference/display
                }
                
                # Copy other fields like application_method_id if present in item level
                if 'application_method_id' in item:
                    result_item['application_method_id'] = item['application_method_id']
                    
                calculated_items.append(result_item)
                
            else:
                # Handle old calculation_basis
                calculated_qty = self._calculate_quantity(
                    item['quantity'],
                    item['calculation_basis'],
                    template_parameters
                )
                
                calculated_items.append({
                    'input_item_id': item['input_item_id'],
                    'quantity': calculated_qty,
                    'quantity_unit_id': item['quantity_unit_id']
                })
        
        return calculated_items

    def _calculate_dosage_quantity(
        self,
        amount: float,
        per: str,
        template_parameters: Dict[str, Any]
    ) -> float:
        """
        Calculate quantity based on dosage.per value.
        
        Args:
            amount: Dosage amount
            per: Scaling factor ('ACRE', 'PLANT', 'LITER_WATER')
            template_parameters: Payload parameters
            
        Returns:
            float: Calculated quantity
        """
        if per == 'ACRE':
            # Map total_acres or area
            factor = template_parameters.get('total_acres') or template_parameters.get('area')
            if factor is None:
                 raise ValidationError(message="Missing 'total_acres' or 'area' for ACRE calculation", error_code="MISSING_SCALING_FACTOR")
            return float(amount) * float(factor)
            
        elif per == 'PLANT':
            # Map total_plants or plant_count
            factor = template_parameters.get('total_plants') or template_parameters.get('plant_count')
            if factor is None:
                raise ValidationError(message="Missing 'total_plants' or 'plant_count' for PLANT calculation", error_code="MISSING_SCALING_FACTOR")
            return float(amount) * float(factor)
            
        elif per == 'LITER_WATER':
            # Map water_liters
            factor = template_parameters.get('water_liters')
            if factor is None:
                raise ValidationError(message="Missing 'water_liters' for LITER_WATER calculation", error_code="MISSING_SCALING_FACTOR")
            return float(amount) * float(factor)
            
        elif per is None:
             # Fixed amount if per is not specified? Or error? Assuming fixed.
             return float(amount)
             
        else:
             raise ValidationError(message=f"Invalid dosage per: {per}", error_code="INVALID_DOSAGE_PER")

    def _calculate_labor(
        self,
        labor_template: Dict[str, Any],
        template_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate labor hours."""
        calculated_hours = self._calculate_quantity(
            labor_template['estimated_hours'],
            labor_template['calculation_basis'],
            template_parameters
        )
        
        labor_details = {
            'estimated_hours': calculated_hours
        }
        
        # Include worker_count if present
        if 'worker_count' in labor_template:
            labor_details['worker_count'] = labor_template['worker_count']
        
        return labor_details
    
    def _calculate_machinery(
        self,
        machinery_template: Dict[str, Any],
        template_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate machinery hours."""
        calculated_hours = self._calculate_quantity(
            machinery_template['estimated_hours'],
            machinery_template['calculation_basis'],
            template_parameters
        )
        
        return {
            'equipment_type': machinery_template['equipment_type'],
            'estimated_hours': calculated_hours
        }
    
    def _calculate_concentration(
        self,
        concentration_template: Dict[str, Any],
        template_parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate concentration with ingredients.
        
        Validates: Requirement 6.11
        """
        # Calculate total solution volume
        total_volume = self._calculate_quantity(
            concentration_template['solution_volume'],
            concentration_template['calculation_basis'],
            template_parameters
        )
        
        # Calculate ingredient quantities
        ingredients = []
        for ing in concentration_template['ingredients']:
            # Convert volume to liters for concentration calculation
            total_volume_liters = float(total_volume) / 1000.0
            
            # Calculate total quantity: concentration_per_liter * volume_in_liters
            total_qty = float(ing['concentration_per_liter']) * total_volume_liters
            
            ingredients.append({
                'input_item_id': ing['input_item_id'],
                'total_quantity': total_qty,
                'quantity_unit_id': ing['concentration_unit_id'],
                'concentration_per_liter': ing['concentration_per_liter']
            })
        
        return {
            'total_solution_volume': total_volume,
            'total_solution_volume_unit_id': concentration_template['solution_volume_unit_id'],
            'ingredients': ingredients
        }
    
    def _calculate_quantity(
        self,
        base_quantity: float,
        calculation_basis: str,
        template_parameters: Dict[str, Any]
    ) -> float:
        """
        Calculate quantity based on calculation_basis.
        
        Args:
            base_quantity: Base quantity from template
            calculation_basis: 'per_acre', 'per_plant', or 'fixed'
            template_parameters: Parameters with area and plant_count
        
        Returns:
            float: Calculated quantity
        
        Validates: Requirements 6.8, 6.9, 6.10
        """
        if calculation_basis == 'per_acre':
            # Requirement 6.8: Multiply by area
            area = template_parameters.get('area') or template_parameters.get('total_acres')
            if area is None:
                raise ValidationError(
                    message="Area/Total Acres required for per_acre calculation",
                    error_code="MISSING_AREA_PARAMETER",
                    details={"calculation_basis": calculation_basis}
                )
            return float(base_quantity) * float(area)
        
        elif calculation_basis == 'per_plant':
            # Requirement 6.9: Multiply by plant_count
            plant_count = template_parameters.get('plant_count') or template_parameters.get('total_plants')
            if plant_count is None:
                raise ValidationError(
                    message="Plant count/Total Plants required for per_plant calculation",
                    error_code="MISSING_PLANT_COUNT_PARAMETER",
                    details={"calculation_basis": calculation_basis}
                )
            return float(base_quantity) * float(plant_count)
        
        elif calculation_basis == 'fixed':
            # Requirement 6.10: Use quantity directly
            return float(base_quantity)
        
        else:
            raise ValidationError(
                message=f"Invalid calculation_basis: {calculation_basis}",
                error_code="INVALID_CALCULATION_BASIS",
                details={"calculation_basis": calculation_basis}
            )
    
    def validate_template_parameters(
        self,
        task_details_template: Dict[str, Any],
        template_parameters: Dict[str, Any]
    ) -> None:
        """
        Validate that template_parameters contains all required fields.
        
        Args:
            task_details_template: Template to check for required parameters
            template_parameters: Parameters to validate
        
        Raises:
            ValidationError: If required parameters are missing
        
        Validates: Requirement 6.14
        """
        required_params = set()
        
        # Check all calculation_basis fields in template
        self._collect_required_parameters(task_details_template, required_params)
        
        # Validate required parameters are present
        missing_params = []
        for param in required_params:
            if param not in template_parameters or template_parameters[param] is None:
                missing_params.append(param)
        
        if missing_params:
            raise ValidationError(
                message=f"Missing required template parameters: {', '.join(missing_params)}",
                error_code="INCOMPLETE_TEMPLATE_PARAMETERS",
                details={"missing_parameters": missing_params}
            )
        
        # Validate start_date is always present
        if 'start_date' not in template_parameters:
            raise ValidationError(
                message="start_date is required in template_parameters",
                error_code="MISSING_START_DATE",
                details={}
            )
    
    def _collect_required_parameters(
        self,
        template: Dict[str, Any],
        required_params: set
    ) -> None:
        """Collect required parameters based on calculation_basis in template."""
        # Check input items
        if 'input_items' in template:
            for item in template['input_items']:
                if 'dosage' in item:
                    # New dosage support
                    per = item['dosage'].get('per')
                    if per == 'ACRE':
                         required_params.add('total_acres') # or area
                    elif per == 'PLANT':
                         required_params.add('total_plants') # or plant_count
                    elif per == 'LITER_WATER':
                         required_params.add('water_liters')
                else:
                    # Old calculation_basis support
                    if item.get('calculation_basis') == 'per_acre':
                        required_params.add('area')
                        required_params.add('area_unit_id')
                    elif item.get('calculation_basis') == 'per_plant':
                        required_params.add('plant_count')
        
        # Check labor
        if 'labor' in template:
            if template['labor'].get('calculation_basis') == 'per_acre':
                required_params.add('area')
                required_params.add('area_unit_id')
            elif template['labor'].get('calculation_basis') == 'per_plant':
                required_params.add('plant_count')
        
        # Check machinery
        if 'machinery' in template:
            if template['machinery'].get('calculation_basis') == 'per_acre':
                required_params.add('area')
                required_params.add('area_unit_id')
            elif template['machinery'].get('calculation_basis') == 'per_plant':
                required_params.add('plant_count')
        
        # Check concentration
        if 'concentration' in template:
            if template['concentration'].get('calculation_basis') == 'per_acre':
                required_params.add('area')
                required_params.add('area_unit_id')
            elif template['concentration'].get('calculation_basis') == 'per_plant':
                required_params.add('plant_count')
