from fastapi import APIRouter, Depends
from rmediator.decorators.request_handler import Annotated
from rmediator.mediator import Mediator

from ed_optimization.application.common.responses.base_response import \
    BaseResponse
from ed_optimization.application.features.order.dtos.create_order_dto import \
    CreateOrderDto
from ed_optimization.application.features.order.requests.commands.process_order_command import \
    ProcessOrderCommand
from ed_optimization.common.logging_helpers import get_logger
from ed_optimization.webapi.common.helpers import (GenericResponse,
                                                   rest_endpoint)
from ed_optimization.webapi.dependency_setup import mediator

LOG = get_logger()
router = APIRouter(prefix="/orders", tags=["Order Feature"])


@router.post("", response_model=GenericResponse[None])
@rest_endpoint
async def create_order(
    model: CreateOrderDto,
    mediator: Annotated[Mediator, Depends(mediator)],
) -> BaseResponse[None]:
    return await mediator.send(ProcessOrderCommand(model=model))
