from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Max

from .models import FeedStockMovement, FeedSack


def record_stock_in(feed_inventory, user):
    FeedStockMovement.objects.create(
        feed_type=feed_inventory.feed_type,
        movement_type=FeedStockMovement.MovementType.IN,
        delta_kg=feed_inventory.quantity_kg,
        moved_by=user,
        feed_inventory=feed_inventory,
        notes=f"Inventory received: {feed_inventory.quantity_kg}kg",
    )


def add_feed_sacks(feed_type, quantity, weight_per_sack, user=None, notes=''):
    """Add new physical sacks to a FeedType."""
    quantity = int(quantity)
    weight_per_sack = Decimal(str(weight_per_sack))
    if quantity <= 0 or weight_per_sack <= 0:
        return []

    max_num = feed_type.sacks.aggregate(m=Max('sack_number'))['m'] or 0
    created_sacks = []
    total_added_kg = Decimal('0.000')

    for i in range(quantity):
        sack_num = max_num + i + 1
        sack = FeedSack.objects.create(
            feed_type=feed_type,
            sack_number=sack_num,
            initial_weight_kg=weight_per_sack,
            current_weight_kg=weight_per_sack
        )
        created_sacks.append(sack)
        total_added_kg += weight_per_sack

    if not feed_type.kg_per_sack or feed_type.kg_per_sack <= 0:
        feed_type.kg_per_sack = weight_per_sack
    feed_type.quantity_sacks = Decimal(str(feed_type.sacks.filter(current_weight_kg__gt=0).count()))
    feed_type.save(update_fields=['kg_per_sack', 'quantity_sacks'])

    FeedStockMovement.objects.create(
        feed_type=feed_type,
        movement_type=FeedStockMovement.MovementType.IN,
        delta_kg=total_added_kg,
        moved_by=user,
        notes=notes or f"Added {quantity} sack(s) ({weight_per_sack}kg each)",
    )
    return created_sacks


def deduct_feed_from_sacks(feed_type, quantity_kg, user=None, notes='', feeding_log=None):
    """Deduct feed in FIFO order from physical FeedSack records."""
    quantity_kg = Decimal(str(quantity_kg))
    if quantity_kg <= Decimal('0'):
        return None

    active_sacks = list(feed_type.sacks.filter(current_weight_kg__gt=0).order_by('sack_number'))
    remaining_to_deduct = quantity_kg

    if active_sacks:
        for sack in active_sacks:
            if remaining_to_deduct <= Decimal('0'):
                break
            if sack.current_weight_kg >= remaining_to_deduct:
                sack.current_weight_kg -= remaining_to_deduct
                sack.save(update_fields=['current_weight_kg', 'updated_at'])
                remaining_to_deduct = Decimal('0')
                break
            else:
                remaining_to_deduct -= sack.current_weight_kg
                sack.current_weight_kg = Decimal('0.000')
                sack.save(update_fields=['current_weight_kg', 'updated_at'])

        feed_type.quantity_sacks = Decimal(str(feed_type.sacks.filter(current_weight_kg__gt=0).count()))
        feed_type.save(update_fields=['quantity_sacks'])
    else:
        # Fallback for feed types without explicit sack records
        if feed_type.kg_per_sack and feed_type.kg_per_sack > 0:
            curr_total_kg = (feed_type.quantity_sacks or Decimal('0')) * feed_type.kg_per_sack
            new_total_kg = max(Decimal('0.00'), curr_total_kg - quantity_kg)
            feed_type.quantity_sacks = new_total_kg / feed_type.kg_per_sack
            feed_type.save(update_fields=['quantity_sacks'])

    return FeedStockMovement.objects.create(
        feed_type=feed_type,
        movement_type=FeedStockMovement.MovementType.OUT,
        delta_kg=Decimal('0.00') - quantity_kg,
        moved_by=user,
        feeding_log=feeding_log,
        notes=notes or f"Feed used ({quantity_kg}kg)",
    )


def restore_feed_to_sacks(feed_type, quantity_kg, user=None, notes=''):
    """Restore feed quantity back to sacks in reverse order (LIFO)."""
    quantity_kg = Decimal(str(quantity_kg))
    if quantity_kg <= Decimal('0'):
        return

    sacks = list(feed_type.sacks.all().order_by('-sack_number'))
    remaining_to_restore = quantity_kg

    if sacks:
        for sack in sacks:
            if remaining_to_restore <= Decimal('0'):
                break
            deficit = sack.initial_weight_kg - sack.current_weight_kg
            if deficit > Decimal('0'):
                add_amt = min(deficit, remaining_to_restore)
                sack.current_weight_kg += add_amt
                sack.save(update_fields=['current_weight_kg', 'updated_at'])
                remaining_to_restore -= add_amt

        feed_type.quantity_sacks = Decimal(str(feed_type.sacks.filter(current_weight_kg__gt=0).count()))
        feed_type.save(update_fields=['quantity_sacks'])
    else:
        if feed_type.kg_per_sack and feed_type.kg_per_sack > 0:
            curr_kg = (feed_type.quantity_sacks or Decimal('0')) * feed_type.kg_per_sack
            feed_type.quantity_sacks = (curr_kg + quantity_kg) / feed_type.kg_per_sack
            feed_type.save(update_fields=['quantity_sacks'])


def consume_feed(feed_type, quantity_kg, user, feeding_log=None):
    """Consume feed using FIFO sack deduction."""
    quantity_kg = Decimal(str(quantity_kg))
    if quantity_kg <= 0:
        raise ValidationError("Feed quantity must be greater than zero.")

    total_avail = feed_type.total_kg
    if total_avail < quantity_kg:
        raise ValidationError(
            f"Not enough feed stock for {feed_type.name}. "
            f"Available: {total_avail}kg, required: {quantity_kg}kg."
        )

    notes = f"Feed used{f' for batch {feeding_log.stock_batch.batch_code}' if feeding_log else ''}"
    return deduct_feed_from_sacks(feed_type, quantity_kg, user=user, notes=notes, feeding_log=feeding_log)
