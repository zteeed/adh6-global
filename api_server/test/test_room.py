import logging
import json
import pytest
from adh.model.database import Database as db
from adh.model.models import Chambre
from CONFIGURATION import TEST_DATABASE as db_settings
from .resource import base_url, TEST_HEADERS


def assert_room_in_db(body):
    s = db.get_db().get_session()
    q = s.query(Chambre)
    q = q.filter(body["roomNumber"] == Chambre.numero)
    c = q.one()
    assert body["vlan"] == c.vlan.numero
    assert str(body["phone"]) == c.telephone
    assert body["description"] == c.description


def prep_db(session,
            sample_room1,
            sample_room2):
    session.add_all([
        sample_room1,
        sample_room2,
    ])
    session.commit()


@pytest.fixture
def api_client(sample_room1, sample_room2):
    from .context import app
    with app.app.test_client() as c:
        db.init_db(db_settings, testing=True)
        prep_db(db.get_db().get_session(),
                sample_room1, sample_room2)
        yield c


def test_room_to_dict(sample_room1):
    dict(sample_room1)


def test_room_filter_all_rooms(api_client):
    r = api_client.get(
        "{}/room/".format(base_url),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 2


def test_room_filter_all_rooms_limit_invalid(api_client):
    r = api_client.get(
        "{}/room/?limit={}".format(base_url, -1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_room_filter_all_rooms_limit(api_client):
    r = api_client.get(
        "{}/room/?limit={}".format(base_url, 1),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 1


def test_room_filter_by_term(api_client):
    r = api_client.get(
        "{}/room/?terms={}".format(base_url, "voisin"),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 1


def test_room_get_valid_room(api_client):
    r = api_client.get(
        "{}/room/{}".format(base_url, 5110),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 200
    response = json.loads(r.data.decode())
    assert len(response) == 4


def test_room_get_invalid_room(api_client):
    r = api_client.get(
        "{}/room/{}".format(base_url, 4900),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_put_new_room_invalid_vlan(api_client):
    room = {
        "roomNumber": 5111,
        "vlan": 45,
        "phone": 6842,
        "description": "Chambre 5111"
    }
    r = api_client.put(
        "{}/room/{}".format(base_url, 5111),
        data=json.dumps(room),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 400


def test_room_put_new_room(api_client):
    room = {
      "roomNumber": 5111,
      "vlan": 42,
      "phone": 6842,
      "description": "Chambre 5111"
    }
    r = api_client.put(
        "{}/room/{}".format(base_url, 5111),
        data=json.dumps(room),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 201
    assert_room_in_db(room)


def test_room_put_update_room(api_client):
    room = {
      "roomNumber": 5111,
      "vlan": 42,
      "phone": 6842,
      "description": "Chambre 5111"
    }
    r = api_client.put(
        "{}/room/{}".format(base_url, 5110),
        data=json.dumps(room),
        content_type='application/json',
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204
    assert_room_in_db(room)


def test_room_delete_existant_room(api_client):
    r = api_client.delete(
        "{}/room/{}".format(base_url, 5110),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 204

    s = db.get_db().get_session()
    q = s.query(Chambre)
    q = q.filter(Chambre.numero == 5110)
    assert q.count() == 0


def test_room_delete_non_existant_room(api_client):
    r = api_client.delete(
        "{}/room/{}".format(base_url, 4900),
        headers=TEST_HEADERS,
    )
    assert r.status_code == 404


def test_room_log_create_room(api_client, caplog):

    with caplog.at_level(logging.INFO):
        test_room_put_new_room(api_client)

    assert caplog.record_tuples[1] == (
        'root', 20,
        'TestingClient created the room 5111\n{"description": "Chambre 5111", '
        '"phone": 6842, "roomNumber": 5111, "vlan": 42}'
    )


def test_room_log_update_room(api_client, caplog):

    with caplog.at_level(logging.INFO):
        test_room_put_update_room(api_client)

    assert caplog.record_tuples[1] == (
        'root', 20,
        'TestingClient updated the room 5110\n{"description": "Chambre 5111", '
        '"phone": 6842, "roomNumber": 5111, "vlan": 42}'
    )


def test_room_log_delete_room(api_client, caplog):

    with caplog.at_level(logging.INFO):
        test_room_delete_existant_room(api_client)

    assert caplog.record_tuples[1] == (
        'root', 20,
        'TestingClient deleted the room 5110'
    )