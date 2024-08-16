
from ..db.pg_factory import PGFactory
from ..db.gpkg_factory import GPKGFactory


class ConfigDBsSupported():
    def __init__(self):
        self.id_default_db = None
        self._db_factories = dict()
        self._init_db_factories()

    def _init_db_factories(self):
        # PostgreSQL/PostGIS
        db_factory = PGFactory()
        self._db_factories[db_factory.get_id()] = db_factory
        self.id_default_db = db_factory.get_id()  # Make PostgreSQL the default DB engine

        # GeoPackage
        db_factory = GPKGFactory()
        self._db_factories[db_factory.get_id()] = db_factory

    def get_db_factories(self):
        return self._db_factories

    def get_db_factory(self, engine):
        return self._db_factories.get(engine, None)
