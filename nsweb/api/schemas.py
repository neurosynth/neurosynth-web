from nsweb.core import marshmallow as mm
from nsweb.initializers import settings
from flask import url_for
from os.path import join


class PeakSchema(mm.Schema):

    class Meta:

        fields = ('table', 'x', 'y', 'z')


class ImageSchema(mm.Schema):

    analysis = mm.Nested('AnalysisSchema', only='id')
    location = mm.Nested('LocationSchema', only='id')
    file = mm.Function(lambda obj: url_for('images.download', val=obj.id))

    class Meta:

        fields = ('id', 'label', 'description', 'stat', 'type', 'analysis',
                  'location', 'file')


class AnalysisSchema(mm.Schema):

    studies = mm.Nested('StudySchema', many=True, only='pmid')
    images = mm.Nested('ImageSchema', many=True, only='id')

    class Meta:

        fields = ('id', 'name', 'description', 'n_studies', 'n_activations',
                  'type', 'studies', 'images')


class StudySchema(mm.Schema):

    peaks = mm.Nested('PeakSchema', many=True)
    analyses = mm.Nested('AnalysisSchema', many=True, only='id')

    class Meta:

        fields = ('pmid', 'doi', 'title', 'authors', 'journal', 'year',
                  'peaks', 'analyses')


class LocationSchema(mm.Schema):

    studies = mm.Nested('StudySchema', many=True, only='pmid')
    images = mm.Nested('ImageSchema', many=True, only='id')

    class Meta:

        fields = ('x', 'y', 'z', 'studies', 'images')


class DecodingSchema(mm.Schema):

    def get_values(self, dec):
        data = open(join(settings.DECODING_RESULTS_DIR,
                         dec.uuid + '.txt')).read().splitlines()
        data = [x.split('\t') for x in data]
        return dict([(f, round(float(v), 3)) for (f, v) in data])

    image = mm.Nested('ImageSchema', allow_null=True)
    reference = mm.Function(lambda obj: obj.decoding_set.name)
    values = mm.Method('get_values')

    class Meta:

        fields = ('id', 'url', 'neurovault_id', 'uuid', 'comments', 'image',
                  'reference', 'values')


class GeneSchema(mm.Schema):

    images = mm.Nested('ImageSchema', many=True, only='id')

    class Meta:

        fields = ('symbol', 'name', 'synonyms', 'locus_type', 'images')
