#! coding: utf-8
import six
import unicodecsv
import yaml

from django_datajsonar.models import Catalog, Dataset
from .strings import DATASET_STATUS, CATALOG_STATUS

CATALOG_HEADER = u'catalog_id'
DATASET_ID_HEADER = u'dataset_identifier'


class DatasetIndexableToggler(object):

    def __init__(self):
        self.logs = []
        self.catalogs = {}

    def process(self, federation_file):
        self.read_dataset_csv(federation_file)
        self.update_database()
        return self.logs

    def read_dataset_csv(self, federation_file):
        reader = unicodecsv.reader(federation_file)

        headers = six.next(reader)
        if CATALOG_HEADER not in headers or DATASET_ID_HEADER not in headers:
            raise ValueError

        catalog_idx = headers.index(CATALOG_HEADER)
        dataset_id_idx = headers.index(DATASET_ID_HEADER)

        # Struct con catalog identifiers como keys y listas de datasets como values
        for line in reader:
            catalog = line[catalog_idx]
            dataset_id = line[dataset_id_idx]
            if catalog not in self.catalogs:  # Inicializo
                self.catalogs[catalog] = []

            self.catalogs[catalog].append(dataset_id)

    def update_database(self):
        for catalog, datasets in self.catalogs.items():
            status = 'OK'
            try:
                dataset_models = Catalog.objects.get(identifier=catalog).dataset_set
            except Catalog.DoesNotExist:
                status = 'ERROR'
                self.logs.append(CATALOG_STATUS.format(catalog, status))
                continue

            for dataset in datasets:
                try:
                    dataset_model = dataset_models.get(identifier=dataset)
                    dataset_model.federable = True
                    dataset_model.save()
                except Dataset.DoesNotExist:
                    status = 'ERROR'

                self.logs.append(DATASET_STATUS.format(catalog, dataset, status))


def process_node_register_file_action(register_file):
    """Registra (crea objetos Node) los nodos marcados como federado en el registro"""
    from .tasks import process_node_register_file
    process_node_register_file.delay(register_file.id)


def confirm_delete(node, register_files):
    """Itera sobre todos los registros y solo borra el nodo si no está registrado
    como federado en ninguno de ellos"""
    found = False
    for register_file in register_files:
        indexing_file = register_file.indexing_file
        yml = indexing_file.read()
        nodes = yaml.load(yml)
        if node.catalog_id in nodes and nodes[node.catalog_id].get('federado'):
            found = True
            break

    if not found:
        node.delete()
