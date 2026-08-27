from decimal import Decimal
from django.core.exceptions import ValidationError

from .models import FeedStockMovement


def record_stock_in(feed_inventory, user):
    FeedStockMovement.objects.create(
        feed_type=feed_inventory.feed_type,
        movement_type=FeedStockMovement.MovementType.IN,
        delta_kg=feed_inventory.quantity_kg,
        moved_by=user,
        feed_inventory=feed_inventory,
        notes=f"Inventory received: {feed_inventory.quantity_kg}kg",
    )


def consume_feed(feed_type, quantity_kg, user, feeding_log=None):
    available_stock = FeedStockMovement.available_stock(feed_type)
    if quantity_kg <= 0:
        raise ValidationError("Feed quantity must be greater than zero.")
    if available_stock < quantity_kg:
        raise ValidationError(
            f"Not enough feed stock for {feed_type.name}. "
            f"Available: {available_stock}kg, required: {quantity_kg}kg."
        )

    return FeedStockMovement.objects.create(
        feed_type=feed_type,
        movement_type=FeedStockMovement.MovementType.OUT,
        delta_kg=Decimal('0.00') - quantity_kg,
        moved_by=user,
        feeding_log=feeding_log,
        notes=f"Feed used{f' for batch {feeding_log.stock_batch.batch_code}' if feeding_log else ''}",
    )
