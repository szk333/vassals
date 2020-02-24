import factory

from users.models import User


class UserFactory(factory.DjangoModelFactory):
    username = factory.Sequence(lambda n: "User %03d" % n)

    class Meta:
        model = User
