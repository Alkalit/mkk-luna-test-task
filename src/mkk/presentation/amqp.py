from faststream.rabbit import RabbitRouter
router = RabbitRouter()


@router.subscriber("testin")
@router.publisher("testout")
async def handle() -> str:
    return 'hello'
