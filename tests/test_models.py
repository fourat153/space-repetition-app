import pytest
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import Session

from app.models import Base, Card, Deck, Rating, ReviewLog, Tag, User, card_tags


@pytest.fixture
def session():
    engine = create_engine("sqlite://")

    @event.listens_for(engine, "connect")
    def _fk_on(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def user(session):
    u = User(email="ahmed@example.com", hashed_password="x")
    session.add(u)
    session.commit()
    return u


def test_new_card_defaults(session, user):
    deck = Deck(user=user, name="Spanish")
    card = Card(deck=deck, front="hola", back="hello")
    session.add(card)
    session.commit()

    assert card.ease_factor == 2.5
    assert card.interval_days == 0
    assert card.repetitions == 0
    assert card.is_new and not card.is_learned


def test_deleting_deck_removes_only_its_cards_and_history(session, user):
    spanish, capitals = Deck(user=user, name="Spanish"), Deck(user=user, name="Capitals")
    c1 = Card(deck=spanish, front="hola", back="hello")
    Card(deck=spanish, front="adios", back="bye")
    keep = Card(deck=capitals, front="France", back="Paris")
    c1.review_logs.append(ReviewLog(rating=Rating.GOOD, interval_days=1, ease_factor=2.5))
    session.add_all([spanish, capitals])
    session.commit()

    session.delete(spanish)
    session.commit()

    assert session.scalars(select(Card)).all() == [keep]
    assert session.scalar(select(func.count()).select_from(ReviewLog)) == 0


def test_tags_many_to_many_and_rename(session, user):
    verbs, exam = Tag(user=user, name="verbs"), Tag(user=user, name="exam-prep")
    deck = Deck(user=user, name="Spanish")
    c1 = Card(deck=deck, front="comer", back="to eat", tags=[verbs, exam])
    c2 = Card(deck=deck, front="beber", back="to drink", tags=[verbs])
    session.add_all([c1, c2])
    session.commit()

    verbs.name = "verbos"
    session.commit()
    assert {t.name for t in c2.tags} == {"verbos"}

    session.delete(exam)
    session.commit()
    assert [t.name for t in c1.tags] == ["verbos"]
    assert session.scalar(select(func.count()).select_from(Card)) == 2


def test_deleting_card_keeps_tag(session, user):
    tag = Tag(user=user, name="verbs")
    card = Card(deck=Deck(user=user, name="Spanish"), front="ir", back="to go", tags=[tag])
    session.add(card)
    session.commit()

    session.delete(card)
    session.commit()
    assert session.scalar(select(func.count()).select_from(card_tags)) == 0
    assert session.get(Tag, tag.id) is not None
