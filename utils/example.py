from dao import MembershipDao
from entities import Membership, Response
from utils import dollars_to_cents


def create_example_memberships(name: str, price: int, admin: bool) -> Response:
    new_individual_membership = Membership(
        name=name,
        description="individual subscription",
        price=dollars_to_cents(price),
        currency="USD",
        interval="month",
        interval_count=1,
        active_admin=admin,
        type_=["Admin"] if admin else ["Individual"]
    )
    return MembershipDao().create_membership(new_individual_membership)
