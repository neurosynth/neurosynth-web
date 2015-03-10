from nsweb.core import marshmallow as mm


class PeakSchema(mm.Schema):

    class Meta:

        fields = ('table', 'x', 'y', 'z')


class AnalysisSchema(mm.Schema):

    studies = mm.Nested('StudySchema', many=True, only='pmid')

    class Meta:

        fields = ('id', 'name', 'description', 'n_studies', 'n_activations',
                  'type', 'studies')


class StudySchema(mm.Schema):

    peaks = mm.Nested(PeakSchema, many=True)
    analyses = mm.Nested('AnalysisSchema', many=True, only='id')

    class Meta:

        fields = ('pmid', 'doi', 'title', 'authors', 'journal', 'year',
                  'peaks', 'analyses')
