import sys
from as_models.manifest import Model
from as_models.ports import INPUT_PORT, DOCUMENT_PORT, DOCUMENT_COLLECTION_PORT, STREAM_COLLECTION_PORT, \
    GRID_COLLECTION_PORT, STREAM_PORT, GRID_PORT

import unittest

from as_models.runtime.r import _convert_ports
from as_models.testing import Context, mock


@unittest.skipIf(sys.version_info[:2] < (3, 5), 'as-models r support not tested for python < v3.5')
class ContextTests(unittest.TestCase):
    mock_as = mock.MockAnalysisServiceApi()

    def setUp(self):
        self.context = Context()
        self.context.configure_analysis_client(url=ContextTests.mock_as.base_url)

    @mock_as.activate
    def test_ports(self):
        model = Model({
            'id': 'test',
            'ports': [
                {'portName': 'a', 'type': DOCUMENT_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'b', 'type': DOCUMENT_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'c', 'type': STREAM_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'd', 'type': STREAM_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'e', 'type': GRID_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'f', 'type': GRID_PORT, 'direction': INPUT_PORT, 'required': False}
            ]
        })

        job_request = {
            'modelId': 'test',
            'ports': {
                # AS-API sends model requests that also include the 'direction' property.
                # as_models now uses the port direction from the manifest file
                # Make sure this is still supported for backward compatibility.
                'b': {'document': 'doc1', 'direction': 'input'},
                'd': {'streamId': 'stream1', 'direction': 'output'},
                'f': {'catalog': 'cat1.xml', 'dataset': 'data1.nc'}
            },
            'sensorCloudConfiguration': {
                "url": "https://52.64.57.4/api/sensor/v2",
                "apiKey": "714debe3bfc3464dc6364dbc5455f326"
            }
        }

        ports = _convert_ports(model.ports, job_request.get('ports', {}), self.context.analysis_client)

        doc1 = ports.rx2('b')
        stream1 = ports.rx2('d')
        grid1 = ports.rx2('f')

        self.assertEqual('\"doc1\"', doc1.rx2('document').r_repr())
        self.assertEqual('\"stream1\"', stream1.rx2('streamId').r_repr())
        self.assertEqual('\"cat1.xml\"', grid1.rx2('catalog').r_repr())
        self.assertEqual('\"data1.nc\"', grid1.rx2('dataset').r_repr())

    @mock_as.activate
    def test_collection_ports(self):
        model = Model({
            'id': 'test',
            'ports': [
                {'portName': 'a', 'type': DOCUMENT_COLLECTION_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'b', 'type': DOCUMENT_COLLECTION_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'c', 'type': STREAM_COLLECTION_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'd', 'type': STREAM_COLLECTION_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'e', 'type': GRID_COLLECTION_PORT, 'direction': INPUT_PORT, 'required': False},
                {'portName': 'f', 'type': GRID_COLLECTION_PORT, 'direction': INPUT_PORT, 'required': False}
            ]
        })
        job_request = {
            'modelId': 'test',
            'ports': {
                # AS-API sends model requests that also include the 'direction' property.
                # as_models now uses the port direction from the manifest file
                # Make sure this is still supported for backward compatibility.
                'a': {'ports': [{'document': 'doc1', 'direction': 'input'}, {'document': 'doc2', 'direction': 'input'}]},
                'b': {'ports': [{'streamId': 'stream1'}, {'streamId': 'stream2'}]},
                'c': {'ports': [{'catalog': 'cat1.xml', 'dataset': 'data1.nc'}, {'catalog': 'cat2.xml', 'dataset': 'data2.nc'}]}
            },
            'sensorCloudConfiguration': {
                "url": "https://52.64.57.4/api/sensor/v2",
                "apiKey": "714debe3bfc3464dc6364dbc5455f326"
            }
        }

        ports = _convert_ports(model.ports, job_request.get('ports', {}), self.context.analysis_client)

        doc1 = ports.rx2('a')[0]
        doc2 = ports.rx2('a')[1]
        print(doc1)

        # print (doc1)
        self.assertEqual('\"doc1\"', doc1.rx2('document').r_repr())
        self.assertEqual('0L', doc1.rx2('index').r_repr())
        self.assertEqual('\"doc2\"', str(doc2.rx2('document').r_repr()))
        self.assertEqual('1L', doc2.rx2('index').r_repr())

        stream1 = ports.rx2('b')[0]
        stream2 = ports.rx2('b')[1]

        self.assertEqual('\"stream1\"', stream1.rx2('streamId').r_repr())
        self.assertEqual('0L', stream1.rx2('index').r_repr())
        self.assertEqual('\"stream2\"', str(stream2.rx2('streamId').r_repr()))
        self.assertEqual('1L', stream2.rx2('index').r_repr())

        grid1 = ports.rx2('c')[0]
        grid2 = ports.rx2('c')[1]

        self.assertEqual('\"cat1.xml\"', grid1.rx2('catalog').r_repr())
        self.assertEqual('\"data1.nc\"', grid1.rx2('dataset').r_repr())
        self.assertEqual('0L', grid1.rx2('index').r_repr())
        self.assertEqual('\"cat2.xml\"', grid2.rx2('catalog').r_repr())
        self.assertEqual('\"data2.nc\"', grid2.rx2('dataset').r_repr())
        self.assertEqual('1L', grid2.rx2('index').r_repr())
